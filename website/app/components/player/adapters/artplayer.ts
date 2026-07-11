import type Artplayer from 'artplayer'
import type { PlayerInstance, PlayerConfig } from '../types'

export interface ArtPlayerOptions {
  hideDefaultControls?: boolean
}

export class ArtPlayerAdapter {
  private artplayer: Artplayer | null = null
  private eventHandlers: Map<string, Function[]> = new Map()
  private hlsInstance: any = null

  constructor(
    private container: HTMLElement,
    private config: PlayerConfig,
    private options?: ArtPlayerOptions
  ) {}

  async init(): Promise<PlayerInstance> {
    // SSR 安全检查
    if (process.server) {
      throw new Error('ArtPlayer can only be initialized on client side')
    }

    // 动态导入 ArtPlayer
    const ArtplayerModule = await import('artplayer')
    const Artplayer = ArtplayerModule.default

    // 确保容器高度为 100%
    this.container.style.height = '100%'
    this.container.style.width = '100%'

    this.artplayer = new Artplayer({
      container: this.container,
      url: this.config.src,
      poster: this.config.poster,
      title: this.config.title,
      autoplay: this.config.autoplay || false,
      preload: 'metadata',     // 预加载元数据，平衡性能和体验
      autoSize: false,         // 关闭自动尺寸，使用容器尺寸
      fit: 'contain',          // 保持比例填充
      autoMini: false,         // 关闭自动小窗
      mutex: true,             // 互斥播放，一个页面只有一个播放器出声
      playsInline: true,       // iOS 内联播放

      // 功能开关
      fullscreen: !this.options?.hideDefaultControls,
      fullscreenWeb: !this.options?.hideDefaultControls,
      pip: !this.options?.hideDefaultControls,
      setting: !this.options?.hideDefaultControls,
      playbackRate: !this.options?.hideDefaultControls,
      aspectRatio: true,  // 始终启用比例设置功能，即使隐藏默认控制器
      screenshot: false,       // 截图功能（可按需开启）
      airplay: !this.options?.hideDefaultControls,  // AirPlay 支持
      fastForward: true,       // 移动端长按快进

      // 外观
      theme: '#2563eb',
      lang: 'zh-cn',

      // 加载超时
      loadingTimeout: 10000,   // 10秒加载超时

      // 视频类型
      type: this.getVideoType(this.config.src),
      customType: {
        m3u8: this.playM3u8.bind(this)
      }
    })

    // ArtPlayer 初始化后，确保其内部容器也占满高度
    this.fixArtplayerHeight()

    // 如果使用自定义控制器，隐藏默认控制器
    if (this.options?.hideDefaultControls) {
      this.hideDefaultControls()
    }

    this.bindEvents()

    return {
      play: () => this.artplayer?.play(),
      pause: () => this.artplayer?.pause(),
      seek: (time: number) => {
        if (this.artplayer) {
          this.artplayer.currentTime = time
        }
      },
      destroy: () => this.destroy(),
      on: (event: string, callback: Function) => this.on(event, callback),
      off: (event: string, callback: Function) => this.off(event, callback),
      artplayer: this.artplayer
    }
  }

  private fixArtplayerHeight() {
    // ArtPlayer 会创建一个 .art-video-player 容器，需要确保它高度为 100%
    const artContainer = this.container.querySelector('.art-video-player') as HTMLElement
    if (artContainer) {
      artContainer.style.height = '100%'
      artContainer.style.width = '100%'
    }

    // 视频元素也需要占满
    const video = this.container.querySelector('video') as HTMLVideoElement
    if (video) {
      video.style.height = '100%'
      video.style.width = '100%'
    }
  }

  private hideDefaultControls() {
    if (!this.artplayer) return
    // 通过 ArtPlayer 的 template 访问控制器并隐藏
    const controls = (this.artplayer as any).template?.$controls as HTMLElement
    const bottom = (this.artplayer as any).template?.$bottom as HTMLElement
    if (controls) {
      controls.style.display = 'none'
    }
    if (bottom) {
      bottom.style.display = 'none'
    }
    // 同时隐藏进度条
    const progress = (this.artplayer as any).template?.$progress as HTMLElement
    if (progress) {
      progress.style.display = 'none'
    }
  }

  private getVideoType(url: string): string {
    if (url.includes('.m3u8')) return 'm3u8'
    if (url.includes('.mp4')) return 'mp4'
    return 'auto'
  }

  private async playM3u8(video: HTMLVideoElement, url: string, art: Artplayer) {
    try {
      const HlsModule = await import('hls.js')
      const Hls = HlsModule.default

      if (Hls.isSupported()) {
        // 保存 hls 实例用于后续清理
        this.hlsInstance = new Hls({
          // ===== 缓冲优化 =====
          maxBufferLength: 30,              // 最大缓冲 30 秒
          maxMaxBufferLength: 60,           // 绝对最大缓冲 60 秒
          maxBufferSize: 60 * 1000 * 1000,  // 最大缓冲 60MB
          maxBufferHole: 0.5,               // 最大缓冲空洞 0.5 秒

          // ===== 起始质量 =====
          startLevel: -1,                   // -1: 自动选择最佳质量

          // ===== 降级策略 =====
          capLevelToPlayerSize: true,       // 根据播放器尺寸限制质量
          capLevelOnFPSDrop: true,          // FPS 下降时降级

          // ===== 网络优化 =====
          fragLoadingTimeOut: 20000,        // 片段加载超时 20 秒
          manifestLoadingTimeOut: 10000,    // 清单加载超时 10 秒
          levelLoadingTimeOut: 10000,       // 级别加载超时 10 秒

          // ===== 重试策略 =====
          fragLoadingMaxRetry: 6,           // 片段重试 6 次
          manifestLoadingMaxRetry: 3,       // 清单重试 3 次
          levelLoadingMaxRetry: 3,          // 级别重试 3 次
          fragLoadingRetryDelay: 1000,      // 重试延迟 1 秒

          // ===== ABR 自适应码率 =====
          abrEwmaFastLive: 3.0,             // 快速估计权重
          abrEwmaSlowLive: 9.0,             // 慢速估计权重
          abrBandWidthFactor: 0.95,         // 带宽因子（留 5% 余量）
          abrBandWidthUpFactor: 0.7,        // 上行带宽因子

          // ===== 其他优化 =====
          enableWorker: true,               // 启用 Web Worker 解码
          enableSoftwareAES: true,          // 软件 AES 解密
          stretchShortVideoToFullWidth: false, // 不拉伸短视频
          maxFragLookUpTolerance: 0.25,     // 片段查找容差
          liveSyncDurationCount: 3,         // 直播同步时长
          liveMaxLatencyDurationCount: Infinity, // 直播最大延迟
          liveDurationInfinity: false,      // 直播时长无限
          forceKeyFrameOnDiscontinuity: true, // 不连续处强制关键帧
        })

        this.hlsInstance.loadSource(url)
        this.hlsInstance.attachMedia(video)

        // 首次加载完成
        this.hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
          art.emit('ready')
        })

        // 错误处理和自动恢复
        this.hlsInstance.on(Hls.Events.ERROR, (_, data) => {
          console.error('[HLS] 错误:', data)

          if (data.fatal) {
            switch(data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                console.error('[HLS] 网络错误，尝试恢复...')
                // 网络错误时尝试重新加载
                setTimeout(() => {
                  this.hlsInstance?.startLoad()
                }, 1000)
                break

              case Hls.ErrorTypes.MEDIA_ERROR:
                console.error('[HLS] 媒体错误，尝试恢复...')
                // 媒体错误时尝试恢复
                this.hlsInstance?.recoverMediaError()
                break

              default:
                // 不可恢复错误
                console.error('[HLS] 致命错误，无法恢复')
                art.emit('error', data)
                break
            }
          } else {
            // 非致命错误，只在特定情况下记录
            if (data.details !== 'internalException') {
              console.warn('[HLS] 非致命错误:', data.details || data.type)
            }
          }
        })

        // 缓冲事件（仅调试用途，不输出日志）
        this.hlsInstance.on(Hls.Events.BUFFER_STALLED, () => {
          // 缓冲卡顿
        })

        this.hlsInstance.on(Hls.Events.BUFFER_EMPTY, () => {
          // 缓冲为空
        })

      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari 原生支持 HLS
        video.src = url
        video.addEventListener('loadedmetadata', () => {
          art.emit('ready')
        })
      } else {
        art.emit('error', new Error('HLS is not supported in this browser'))
      }
    } catch (error) {
      console.error('[HLS] 初始化失败:', error)
      art.emit('error', error)
    }
  }

  private bindEvents() {
    if (!this.artplayer) return

    this.artplayer.on('video:play', () => this.emit('play'))
    this.artplayer.on('video:pause', () => this.emit('pause'))
    this.artplayer.on('video:ended', () => this.emit('ended'))
    this.artplayer.on('video:timeupdate', () => {
      this.emit('timeupdate', this.artplayer?.currentTime || 0)
    })
    this.artplayer.on('video:volumechange', () => {
      const video = this.artplayer?.template?.$video as HTMLVideoElement
      if (video) {
        this.emit('volumechange', {
          muted: video.muted,
          volume: video.volume
        })
      }
    })
    this.artplayer.on('ready', () => this.emit('ready'))
    this.artplayer.on('error', (error) => this.emit('error', error))

    // 小窗模式事件
    this.artplayer.on('mini', () => {
      // 小窗模式切换
    })
  }

  private emit(event: string, ...args: any[]) {
    const handlers = this.eventHandlers.get(event) || []
    handlers.forEach(handler => handler(...args))
  }

  on(event: string, handler: Function) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, [])
    }
    this.eventHandlers.get(event)!.push(handler)
  }

  off(event: string, handler: Function) {
    const handlers = this.eventHandlers.get(event) || []
    const index = handlers.indexOf(handler)
    if (index > -1) {
      handlers.splice(index, 1)
    }
  }

  destroy() {
    // 清理 hls.js 实例
    if (this.hlsInstance) {
      this.hlsInstance.destroy()
      this.hlsInstance = null
    }

    // 清理 ArtPlayer
    if (this.artplayer) {
      this.artplayer.destroy()
      this.artplayer = null
    }

    this.eventHandlers.clear()
  }
}
