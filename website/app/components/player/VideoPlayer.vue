<template>
  <div
    ref="playerRef"
    class="relative w-full h-full bg-black will-change-transform"
    :class="{ 'hide-default-controls': customControls }"
  >
    <!-- Loading State -->
    <div
      v-if="loading"
      class="absolute inset-0 flex flex-col items-center justify-center bg-black/50 z-10 w-full h-full"
    >
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <!-- 加载提示 -->
      <p v-if="loadTime > 5" class="mt-4 text-gray-300 text-sm">
        正在加载资源...
      </p>
    </div>

    <!-- Timeout Warning -->
    <div
      v-if="loadTimeout"
      class="absolute inset-0 flex flex-col items-center justify-center bg-black/90 z-30 p-4 text-center w-full h-full"
    >
      <el-icon :size="40" class="mb-3 text-yellow-500"><Warning /></el-icon>
      <p class="text-white font-medium mb-1 text-base">视频加载时间过长</p>
      <p class="text-gray-400 text-xs mb-4 leading-relaxed">
        当前播放源响应较慢，或您的浏览器不支持该格式
      </p>
      <div class="flex flex-row gap-2 sm:gap-3 w-full sm:w-auto px-2 sm:px-0">
        <button
          class="flex-1 sm:flex-none px-3 py-1.5 bg-app-primary rounded-lg text-sm hover:bg-app-primary-hover whitespace-nowrap"
          @click="retry"
        >
          重新加载
        </button>
        <button
          v-if="hasMultipleSources"
          class="flex-1 sm:flex-none px-3 py-1.5 bg-gray-700 rounded-lg text-sm hover:bg-gray-600 whitespace-nowrap"
          @click="switchSource"
        >
          切换播放源
        </button>
      </div>
      <p class="mt-4 text-xs text-gray-500 leading-relaxed">
        提示：如问题持续，建议使用 Chrome 浏览器
      </p>
    </div>

    <!-- Error State -->
    <div
      v-if="error && !loadTimeout"
      class="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-20 p-4 w-full h-full"
    >
      <el-icon :size="40" class="mb-3 text-gray-500"><Warning /></el-icon>
      <p class="text-gray-400 text-base">视频加载失败</p>
      <p class="text-gray-500 text-xs mt-2 mb-4 text-center px-2 leading-relaxed">
        可能是播放源失效或浏览器不支持，建议切换播放源或使用 Chrome
      </p>
      <div class="flex flex-row gap-2 sm:gap-3 w-full sm:w-auto px-2 sm:px-0">
        <button
          class="flex-1 sm:flex-none px-3 py-1.5 bg-app-primary rounded-lg text-sm hover:bg-app-primary-hover"
          @click="retry"
        >
          重试
        </button>
        <button
          v-if="hasMultipleSources"
          class="flex-1 sm:flex-none px-3 py-1.5 bg-gray-700 rounded-lg text-sm hover:bg-gray-600"
          @click="switchSource"
        >
          换源
        </button>
      </div>
    </div>

    <!-- Player Container -->
    <div ref="artplayerRef" class="w-full h-full absolute inset-0" />
  </div>
</template>

<style scoped>
/* 确保 ArtPlayer 及其内部元素占满容器 */
:deep(.art-video-player) {
  width: 100% !important;
  height: 100% !important;
}

:deep(.art-video) {
  width: 100% !important;
  /* 不要设置 height: 100% !important，让 ArtPlayer 通过 aspectRatio 控制 */
  object-fit: contain;

  /* GPU 加速优化 */
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;

  /* 防止拖拽时出现选中文字 */
  user-select: none;
  -webkit-user-select: none;

  /* 硬件加速渲染 */
  -webkit-transform: translateZ(0);
  -webkit-backface-visibility: hidden;
}

/* 满屏比例 - 填满容器 */
:deep(.art-video.aspect-full) {
  object-fit: cover !important;
}

/* 播放器容器优化 */
:deep(.art-container) {
  /* 启用硬件加速 */
  transform: translate3d(0, 0, 0);
}

/* 控制栏优化 */
:deep(.art-controls),
:deep(.art-bottom) {
  /* 防止控制栏闪烁 */
  transform: translateZ(0);
}

/* 隐藏默认控制器当使用自定义控制器时 */
.hide-default-controls :deep(.art-controls),
.hide-default-controls :deep(.art-bottom) {
  display: none !important;
}

:deep(.art-layers) {
  z-index: 10 !important;
}

/* 缓冲提示优化 */
:deep(.art-loading) {
  will-change: opacity;
}

/* ===== 小窗模式优化（防止被浏览器工具栏盖住） ===== */
:deep(.art-mini) {
  /* 提高层级确保在最上层 */
  z-index: 9999 !important;

  /* 移动端底部留出浏览器工具栏空间 */
  bottom: 80px !important;
  right: 16px !important;

  /* 固定尺寸 */
  width: 180px !important;
  height: 101px !important;

  /* 阴影效果 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

/* PC 端小窗位置可以更靠下 */
@media (min-width: 1024px) {
  :deep(.art-mini) {
    bottom: 20px !important;
    right: 20px !important;
    width: 240px !important;
    height: 135px !important;
  }
}

/* iOS Safari 特殊处理 */
@supports (-webkit-touch-callout: none) {
  :deep(.art-mini) {
    /* iOS 底部安全区域 */
    bottom: calc(80px + env(safe-area-inset-bottom)) !important;
  }
}
</style>

<script setup lang="ts">
import { Loading, Warning } from '@element-plus/icons-vue'
import { usePlayer } from './composables/usePlayer'
import type { PlayerConfig } from './types'

// ==================== Props ====================
interface Props {
  src?: string
  poster?: string
  title?: string
  autoplay?: boolean
  customControls?: boolean  // 是否使用自定义控制器（禁用默认控制器）
  options?: {
    danmaku?: boolean
  }
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: false,
  customControls: false
})

// ==================== Emits ====================
const emit = defineEmits<{
  ended: []
  timeupdate: [time: number]
  ready: []
  error: [error: any]
  switchSource: []
  play: []      // 新增：播放事件
  pause: []     // 新增：暂停事件
}>()

// ==================== Refs ====================
const playerRef = ref<HTMLElement>()
const artplayerRef = ref<HTMLElement>()
const artplayerInstanceRef = ref<any>()  // ArtPlayer 原始实例
const loading = ref(true)
const error = ref(false)
const loadTimeout = ref(false)
const loadTime = ref(0)
const hasMultipleSources = ref(false)
const isUnmounted = ref(false)

// 播放器状态（供外部使用）
const isPaused = ref(true)
const isMuted = ref(false)
const volume = ref(1)
const currentTime = ref(0)
const duration = ref(0)
const buffered = ref(0)
const isFullscreen = ref(false)
const currentPlaybackRate = ref(1)
const currentAspectRatio = ref('default')

// 加载超时检测
let loadTimer: ReturnType<typeof setTimeout> | null = null
let timeCounter: ReturnType<typeof setInterval> | null = null

// 开始加载计时
const startLoadTimer = () => {
  stopLoadTimer()
  if (isUnmounted.value) return

  loadTime.value = 0
  loadTimeout.value = false

  timeCounter = setInterval(() => {
    if (!isUnmounted.value) {
      loadTime.value++
    }
  }, 1000)

  loadTimer = setTimeout(() => {
    if (!isUnmounted.value && loading.value) {
      loadTimeout.value = true
      stopLoadTimer()
    }
  }, 15000)
}

// 停止加载计时
const stopLoadTimer = () => {
  if (loadTimer) {
    clearTimeout(loadTimer)
    loadTimer = null
  }
  if (timeCounter) {
    clearInterval(timeCounter)
    timeCounter = null
  }
}

// ==================== Player Initialization ====================
const { player, initPlayer, destroyPlayer } = usePlayer({
  container: artplayerRef,
  config: computed(() => ({
    type: 'artplayer' as const,
    src: props.src || '',
    poster: props.poster,
    title: props.title,
    autoplay: props.autoplay
  })),
  playerOptions: computed(() => ({
    hideDefaultControls: props.customControls
  })),
  onReady: () => {
    if (isUnmounted.value) return
    loading.value = false
    loadTimeout.value = false
    stopLoadTimer()

    // 获取 ArtPlayer 原始实例用于比例设置
    const artplayerInstance = (player.value as any)?.artplayer
    if (artplayerInstance) {
      artplayerInstanceRef.value = artplayerInstance
    }

    // 直接监听 video 元素的事件
    const video = artplayerRef.value?.querySelector('video')
    if (video) {
      // 初始化默认比例类
      video.classList.add('aspect-default')
      // 初始化状态
      isPaused.value = video.paused
      isMuted.value = video.muted
      volume.value = video.volume
      duration.value = video.duration || 0
      currentTime.value = video.currentTime || 0
      if (video.buffered.length > 0) {
        buffered.value = video.buffered.end(video.buffered.length - 1)
      }

      // 如果元数据还没加载，监听 loadedmetadata
      if (!video.duration) {
        video.addEventListener('loadedmetadata', () => {
          duration.value = video.duration || 0
        }, { once: true })
      }

      // 监听 timeupdate 事件
      video.addEventListener('timeupdate', () => {
        currentTime.value = video.currentTime
        if (video.duration) {
          duration.value = video.duration
        }
        emit('timeupdate', video.currentTime)
      })

      // 监听 progress 事件（缓冲进度更新）
      video.addEventListener('progress', () => {
        if (video.buffered.length > 0) {
          // 获取当前播放时间附近的缓冲位置
          let bufferedEnd = 0
          for (let i = 0; i < video.buffered.length; i++) {
            if (video.buffered.start(i) <= video.currentTime && video.buffered.end(i) >= video.currentTime) {
              bufferedEnd = video.buffered.end(i)
              break
            }
          }
          // 如果没有找到当前位置的缓冲，取最后一个缓冲段
          if (!bufferedEnd && video.buffered.length > 0) {
            bufferedEnd = video.buffered.end(video.buffered.length - 1)
          }
          buffered.value = bufferedEnd
        }
      })

      // 监听播放状态变化
      video.addEventListener('play', () => {
        isPaused.value = false
        emit('play')
      })
      video.addEventListener('pause', () => {
        isPaused.value = true
        emit('pause')
      })

      // 监听音量变化
      video.addEventListener('volumechange', () => {
        isMuted.value = video.muted
        volume.value = video.volume
      })

      // 同时监听 durationchange 事件
      video.addEventListener('durationchange', () => {
        duration.value = video.duration || 0
      })
    }

    emit('ready')
  },
  onEnded: () => {
    if (!isUnmounted.value) emit('ended')
  },
  onError: (err: any) => {
    if (isUnmounted.value) return
    error.value = true
    loading.value = false
    loadTimeout.value = false
    stopLoadTimer()
    emit('error', err)
  }
})

// ==================== Watch src changes ====================
watch(() => props.src, (newSrc, oldSrc) => {
  if (newSrc && newSrc !== oldSrc) {
    loading.value = true
    error.value = false
    loadTimeout.value = false
    startLoadTimer()
    initPlayer()
  }
})

// ==================== Methods ====================
const retry = () => {
  error.value = false
  loadTimeout.value = false
  loading.value = true
  startLoadTimer()
  initPlayer()
}

const switchSource = () => {
  emit('switchSource')
}

// 检测是否为移动设备
const isMobile = () => {
  const userAgent = navigator.userAgent.toLowerCase()
  const isIOS = /ipad|iphone|ipod/.test(userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isAndroid = /android/.test(userAgent)
  return isIOS || isAndroid || ('ontouchstart' in window && window.innerWidth < 1024)
}

// 全屏控制
const toggleFullscreen = async () => {
  const video = artplayerRef.value?.querySelector('video') as HTMLVideoElement & {
    webkitEnterFullscreen?: () => void
    webkitExitFullscreen?: () => void
    webkitDisplayingFullscreen?: boolean
    enterFullscreen?: () => void
    mozRequestFullScreen?: () => Promise<void>
    msRequestFullscreen?: () => void
  }
  if (!video) {
    console.error('[Fullscreen] video element not found')
    return
  }

  try {
    const mobile = isMobile()

    // 检查当前全屏状态
    const isCurrentlyFullscreen = !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement ||
      video.webkitDisplayingFullscreen
    )

    if (isCurrentlyFullscreen) {
      // 退出全屏
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if ((document as any).webkitExitFullscreen) {
        await (document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        await (document as any).mozCancelFullScreen()
      } else if ((document as any).msExitFullscreen) {
        await (document as any).msExitFullscreen()
      }
      if (video.webkitExitFullscreen) {
        video.webkitExitFullscreen()
      }
      isFullscreen.value = false

      // 解锁屏幕方向
      if ((screen as any).orientation && (screen as any).orientation.unlock) {
        (screen as any).orientation.unlock()
      }
    } else {
      // 进入全屏

      // 移动端优先使用 video 元素的全屏（体验更好）
      if (mobile && video.webkitEnterFullscreen) {
        video.webkitEnterFullscreen()
        isFullscreen.value = true
        return
      }

      // 尝试各种全屏 API（video 元素优先）
      const enterFullscreen = async () => {
        // 标准 API
        if (video.requestFullscreen) {
          await video.requestFullscreen()
          return
        }
        // webkit (Safari, Chrome, Edge)
        if ((video as any).webkitRequestFullscreen) {
          await (video as any).webkitRequestFullscreen()
          return
        }
        // Firefox
        if (video.mozRequestFullScreen) {
          await video.mozRequestFullScreen()
          return
        }
        // IE/Edge
        if (video.msRequestFullscreen) {
          video.msRequestFullscreen()
          return
        }
        // 回退到容器
        if (playerRef.value?.requestFullscreen) {
          await playerRef.value.requestFullscreen()
          return
        }
        throw new Error('No fullscreen API available')
      }

      await enterFullscreen()
      isFullscreen.value = true

      // 移动端尝试锁定横屏（提升观看体验）
      if (mobile && (screen as any).orientation && (screen as any).orientation.lock) {
        try {
          await (screen as any).orientation.lock('landscape')
        } catch {
          // 锁定方向失败，忽略
        }
      }
    }
  } catch {
    // 全屏操作失败，忽略
  }
}

const toggleMute = () => {
  const video = artplayerRef.value?.querySelector('video')
  if (video) {
    video.muted = !video.muted
    // 手动更新状态，因为 ArtPlayer 可能不会触发 volumechange 事件
    isMuted.value = video.muted
    volume.value = video.volume
  }
}

const setVolume = (vol: number) => {
  const video = artplayerRef.value?.querySelector('video')
  if (video) {
    video.volume = Math.max(0, Math.min(1, vol))
    // 手动更新状态
    volume.value = video.volume
  }
}

const setPlaybackRate = (rate: number) => {
  const video = artplayerRef.value?.querySelector('video')
  if (video) {
    video.playbackRate = rate
    currentPlaybackRate.value = rate
  }
}

const setAspectRatio = (ratio: string) => {
  const art = artplayerInstanceRef.value
  const video = artplayerRef.value?.querySelector('video')

  // 清除 aspect-full 类
  if (video) {
    video.classList.remove('aspect-full')
  }

  if (art) {
    // ArtPlayer 内置支持的比例格式
    if (ratio === 'default') {
      art.aspectRatio = 'default'
    } else if (ratio === '4:3') {
      art.aspectRatio = '4:3'
    } else if (ratio === '16:9') {
      art.aspectRatio = '16:9'
    } else if (ratio === 'full') {
      // full: 设置为 default 比例 + cover 模式
      art.aspectRatio = 'default'
      if (video) {
        video.classList.add('aspect-full')
      }
    }
    currentAspectRatio.value = ratio
  }
}

// ==================== Keyboard Shortcuts ====================
if (process.client) {
  onKeyStroke(' ', (e) => {
    if (e.target === document.body) {
      e.preventDefault()
      const video = artplayerRef.value?.querySelector('video')
      if (video) {
        if (video.paused) {
          video.play()
        } else {
          video.pause()
        }
      }
    }
  })

  onKeyStroke('f', (e) => {
    if (e.target === document.body) {
      e.preventDefault()
      toggleFullscreen()
    }
  })

  // 监听全屏变化（所有浏览器前缀）
  const handleFullscreenChange = () => {
    const video = artplayerRef.value?.querySelector('video') as any
    const isFull = !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement ||
      (video && video.webkitDisplayingFullscreen)
    )
    isFullscreen.value = isFull
  }

  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)

  // 清理函数
  onUnmounted(() => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
    document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  })
}

// ==================== Lifecycle ====================
onMounted(() => {
  isUnmounted.value = false
  if (props.src) {
    startLoadTimer()
    initPlayer()
  }
})

onUnmounted(() => {
  isUnmounted.value = true
  stopLoadTimer()
  destroyPlayer()
})

// ==================== Expose Methods ====================
defineExpose({
  play: () => {
    const video = artplayerRef.value?.querySelector('video')
    video?.play()
  },
  pause: () => {
    const video = artplayerRef.value?.querySelector('video')
    video?.pause()
  },
  seek: (time: number) => {
    const video = artplayerRef.value?.querySelector('video')
    if (video) {
      // 立即更新本地状态，让 UI 立即响应
      currentTime.value = time
      // 设置视频当前时间
      video.currentTime = time
      // 如果视频处于暂停状态，HLS 可能需要手动触发时间更新
      if (video.paused) {
        // 对于 HLS 视频，暂停时 seek 可能需要等待关键帧
        // 手动触发 timeupdate 事件同步
        setTimeout(() => {
          currentTime.value = video.currentTime
        }, 50)
      }
    }
  },
  toggleFullscreen,
  toggleMute,
  setVolume,
  setPlaybackRate,
  setAspectRatio,
  setHasMultipleSources: (value: boolean) => {
    hasMultipleSources.value = value
  },
  // 暴露状态和 ref（保持响应式）
  isPaused,
  isMuted,
  volume,
  currentTime,
  duration,
  buffered,
  isFullscreen,
  currentPlaybackRate,
  currentAspectRatio,
})
</script>
