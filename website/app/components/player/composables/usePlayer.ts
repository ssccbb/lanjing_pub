import { toValue } from 'vue'
import { ArtPlayerAdapter, type ArtPlayerOptions } from '../adapters/artplayer'
import type { PlayerConfig, PlayerInstance } from '../types'

export interface UsePlayerOptions {
  container: Ref<HTMLElement | undefined>
  config: Ref<PlayerConfig>
  playerOptions?: ArtPlayerOptions
  onReady?: () => void
  onEnded?: () => void
  onError?: (error: any) => void
}

export function usePlayer(options: UsePlayerOptions) {
  const player = ref<PlayerInstance | null>(null)
  const adapter = ref<ArtPlayerAdapter | null>(null)
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  const initPlayer = async () => {
    if (!options.container.value) return
    if (!options.config.value.src) return

    // 销毁旧的
    destroyPlayer()

    isLoading.value = true
    error.value = null

    try {
      adapter.value = new ArtPlayerAdapter(
        options.container.value,
        options.config.value,
        toValue(options.playerOptions)
      )
      player.value = await adapter.value.init()

      // 绑定事件
      if (options.onReady) adapter.value.on('ready', options.onReady)
      if (options.onEnded) adapter.value.on('ended', options.onEnded)
      if (options.onError) adapter.value.on('error', options.onError)

      isLoading.value = false
    } catch (err) {
      error.value = err instanceof Error ? err : new Error(String(err))
      isLoading.value = false
      options.onError?.(err)
    }
  }

  const destroyPlayer = () => {
    adapter.value?.destroy()
    adapter.value = null
    player.value = null
  }

  return {
    player,
    isLoading,
    error,
    initPlayer,
    destroyPlayer
  }
}
