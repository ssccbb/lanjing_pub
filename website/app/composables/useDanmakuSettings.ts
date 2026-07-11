/**
 * 弹幕设置管理 - 支持本地存储持久化
 */
import { useStorage } from '@vueuse/core'

export interface DanmakuSettings {
  enabled: boolean
  speed: 'slow' | 'normal' | 'fast'
  opacity: number
  blockScroll: boolean
  blockTop: boolean
  blockBottom: boolean
}

const DEFAULT_SETTINGS: DanmakuSettings = {
  enabled: true,
  speed: 'fast',
  opacity: 1,
  blockScroll: false,
  blockTop: false,
  blockBottom: false,
}

const STORAGE_KEY = 'app-danmaku-v6'

export function useDanmakuSettings() {
  // 使用 useStorage 直接存储对象
  const settings = useStorage<DanmakuSettings>(STORAGE_KEY, DEFAULT_SETTINGS, localStorage)

  // 计算被屏蔽的模式列表
  const blockedModes = computed(() => {
    const modes: Array<'scroll' | 'top' | 'bottom'> = []
    if (settings.value.blockScroll) modes.push('scroll')
    if (settings.value.blockTop) modes.push('top')
    if (settings.value.blockBottom) modes.push('bottom')
    return modes
  })

  // 重置为默认设置
  function resetSettings() {
    settings.value = { ...DEFAULT_SETTINGS }
  }

  // 切换弹幕显示
  function toggleEnabled() {
    settings.value.enabled = !settings.value.enabled
  }

  // 设置速度
  function setSpeed(s: DanmakuSettings['speed']) {
    settings.value.speed = s
  }

  // 设置透明度
  function setOpacity(o: number) {
    settings.value.opacity = Math.max(0.1, Math.min(1, o))
  }

  // 切换屏蔽模式
  function toggleBlockMode(mode: 'scroll' | 'top' | 'bottom') {
    const key = mode === 'scroll' ? 'blockScroll' : mode === 'top' ? 'blockTop' : 'blockBottom'
    settings.value[key] = !settings.value[key]
  }

  return {
    // 直接暴露 settings 对象的各个属性
    enabled: computed({
      get: () => settings.value.enabled ?? DEFAULT_SETTINGS.enabled,
      set: (v) => settings.value.enabled = v
    }),
    speed: computed({
      get: () => settings.value.speed ?? DEFAULT_SETTINGS.speed,
      set: (v) => settings.value.speed = v
    }),
    opacity: computed({
      get: () => settings.value.opacity ?? DEFAULT_SETTINGS.opacity,
      set: (v) => settings.value.opacity = v
    }),
    blockScroll: computed({
      get: () => settings.value.blockScroll ?? DEFAULT_SETTINGS.blockScroll,
      set: (v) => settings.value.blockScroll = v
    }),
    blockTop: computed({
      get: () => settings.value.blockTop ?? DEFAULT_SETTINGS.blockTop,
      set: (v) => settings.value.blockTop = v
    }),
    blockBottom: computed({
      get: () => settings.value.blockBottom ?? DEFAULT_SETTINGS.blockBottom,
      set: (v) => settings.value.blockBottom = v
    }),
    blockedModes,
    resetSettings,
    toggleEnabled,
    setSpeed,
    setOpacity,
    toggleBlockMode,
  }
}
