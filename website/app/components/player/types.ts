// 播放器类型定义

export type PlayerType = 'artplayer' | 'native'

// 视频源
export interface VideoSource {
  url: string
  type?: string
  quality?: string
}

// 播放器配置
export interface PlayerConfig {
  type: PlayerType
  src: string
  poster?: string
  title?: string
  autoplay?: boolean
}

// 播放器实例接口
export interface PlayerInstance {
  play(): void
  pause(): void
  seek(time: number): void
  destroy(): void
  on(event: string, callback: Function): void
  off(event: string, callback: Function): void
}

// 播放器事件
export interface PlayerEvents {
  play: () => void
  pause: () => void
  ended: () => void
  timeupdate: (time: number) => void
  ready: () => void
  error: (error: any) => void
}
