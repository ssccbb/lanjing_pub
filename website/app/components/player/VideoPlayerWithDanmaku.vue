<template>
  <div
    ref="containerRef"
    class="video-player-with-danmaku relative w-full h-full overflow-hidden"
  >
    <!-- 原播放器 -->
    <VideoPlayer
      ref="playerRef"
      :src="src"
      :poster="poster"
      :title="title"
      :autoplay="autoplay"
      :custom-controls="true"
      @ready="onReady"
      @timeupdate="onTimeUpdate"
      @play="isPaused = false"
      @pause="isPaused = true"
      @ended="$emit('ended')"
      @switch-source="$emit('switchSource')"
    />

    <!-- 弹幕层 -->
    <DanmakuLayer
      ref="danmakuLayerRef"
      :items="filteredDanmakuItems"
      :visible="danmakuSettings.enabled && !isPaused"
      :current-time="currentTime"
      :speed-level="danmakuSettings.speed"
      :opacity="danmakuSettings.opacity"
      :blocked-modes="blockedModes"
      :track-height="isMobile ? 28 : 36"
    />

    <!-- 自定义控制器 -->
    <PlayerControls
      ref="controlsRef"
      :is-paused="isPaused"
      :is-muted="isMuted"
      :volume="volume"
      :current-time="currentTime"
      :duration="duration"
      :buffered="buffered"
      :is-fullscreen="isFullscreen"
      :show-danmaku="true"
      :danmaku-enabled="danmakuSettings.enabled"
      :danmaku-speed="danmakuSettings.speed"
      :danmaku-opacity="danmakuSettings.opacity"
      :block-scroll="danmakuSettings.blockScroll"
      :block-top="danmakuSettings.blockTop"
      :block-bottom="danmakuSettings.blockBottom"
      :default-mode="danmakuSettings.defaultMode"
      :is-logged-in="isLoggedIn"
      :current-playback-rate="currentPlaybackRate"
      :current-aspect-ratio="currentAspectRatio"
      @play="play"
      @pause="pause"
      @seek="seek"
      @toggle-mute="toggleMute"
      @toggle-fullscreen="toggleFullscreen"
      @toggle-danmaku="toggleDanmaku"
      @update-danmaku-speed="(s) => danmakuSettings.speed = s"
      @update-danmaku-opacity="(o) => danmakuSettings.opacity = o"
      @update-block-scroll="(b) => danmakuSettings.blockScroll = b"
      @update-block-top="(b) => danmakuSettings.blockTop = b"
      @update-block-bottom="(b) => danmakuSettings.blockBottom = b"
      @update-default-mode="(m) => danmakuSettings.defaultMode = m"
      @send-danmaku="sendDanmaku"
      @update-playback-rate="setPlaybackRate"
      @update-aspect-ratio="setAspectRatio"
    />
  </div>
</template>

<script setup lang="ts">
import type { DanmakuItem } from './DanmakuLayer.vue'
import VideoPlayer from './VideoPlayer.vue'
import PlayerControls from './PlayerControls.vue'
import { getRandomReminderMessage } from '~/config/danmaku.config'

interface Props {
  src?: string
  poster?: string
  title?: string
  autoplay?: boolean
  videoId: string | number
  isLoggedIn?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: false,
  isLoggedIn: false,
})

const emit = defineEmits<{
  ready: []
  ended: []
  login: []
  switchSource: []
}>()

// Refs
const containerRef = ref<HTMLElement>()
const playerRef = ref<InstanceType<typeof VideoPlayer>>()
const danmakuLayerRef = ref()

// 播放器状态
const currentTime = ref(0)
const isPaused = ref(true)
const isMuted = ref(false)
const volume = ref(1)
const duration = ref(0)
const buffered = ref(0)
const isFullscreen = ref(false)
const currentPlaybackRate = ref(1)
const currentAspectRatio = ref('default')

// 弹幕设置（带本地存储）
const STORAGE_KEY = 'app-danmaku-v11'

// 默认设置
const DEFAULT_SETTINGS = {
  enabled: true,
  speed: 'normal' as 'slow' | 'normal' | 'fast',
  opacity: 1,
  blockScroll: false,
  blockTop: false,
  blockBottom: false,
  defaultMode: 'scroll' as 'scroll' | 'top' | 'bottom',
}

// 从 localStorage 读取设置
function loadSettings() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      const settings = { ...DEFAULT_SETTINGS, ...parsed }
      // 确保透明度不低于50%
      settings.opacity = Math.max(0.5, Math.min(1, settings.opacity))
      return settings
    }
  } catch {
    // 读取失败，使用默认值
  }
  return { ...DEFAULT_SETTINGS }
}

// 保存设置到 localStorage
function saveSettings(settings: typeof DEFAULT_SETTINGS) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch {
    // 保存失败，忽略
  }
}

// 响应式设置对象
const danmakuSettings = reactive(loadSettings())

// 监听设置变化并保存
watch(
  () => ({ ...danmakuSettings }),
  (newVal) => {
    saveSettings(newVal)
  },
  { deep: true }
)

// 被屏蔽的模式列表
const blockedModes = computed(() => {
  const modes: Array<'scroll' | 'top' | 'bottom'> = []
  if (danmakuSettings.blockScroll) modes.push('scroll')
  if (danmakuSettings.blockTop) modes.push('top')
  if (danmakuSettings.blockBottom) modes.push('bottom')
  return modes
})

// 弹幕管理
const danmakuManager = useDanmaku({ videoId: props.videoId, immediate: true })

// 弹幕提醒相关
const reminderShown = ref(false) // 当前剧集是否已显示过提醒

/**
 * 检查并显示弹幕提醒（每个剧集只触发一次）
 * 条件：弹幕开启 + 已登录 + 当前时间往后10秒内没有任何弹幕
 */
function checkAndShowReminder(currentTimeValue: number) {
  // 每个剧集只触发一次
  if (reminderShown.value) {
    return
  }

  // 检查基本条件
  if (!danmakuSettings.enabled) {
    return
  }
  if (!props.isLoggedIn) {
    return
  }

  // 检查当前时间往后10秒内是否有弹幕
  const windowEnd = currentTimeValue + 10
  const upcomingDanmaku = danmakuManager.items.value.filter(item => {
    const itemTime = item.time
    return itemTime > currentTimeValue && itemTime <= windowEnd
  })

  // 如果未来10秒内没有弹幕，显示提醒
  if (upcomingDanmaku.length === 0) {
    showLocalReminderDanmaku(currentTimeValue)
    reminderShown.value = true
  }
}

/**
 * 显示本地提醒弹幕（不走接口）
 */
function showLocalReminderDanmaku(time: number) {
  const message = getRandomReminderMessage()
  const reminderItem: DanmakuItem = {
    id: `reminder_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    text: message,
    time: time,
    mode: 'scroll',
    color: '#FFD700', // 金色提醒
  }

  // 添加到弹幕列表（本地显示，不走接口）
  danmakuManager.items.value.push(reminderItem)
}

// 移动端检测
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 640
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 过滤后的弹幕列表
const filteredDanmakuItems = computed(() => {
  return danmakuManager.items.value.filter(item => {
    const mode = item.mode || 'scroll'
    return !blockedModes.value.includes(mode)
  })
})

// 动画帧同步ID
let rafId: number | null = null

// 事件处理
function onReady() {
  // 立即同步一次完整状态（包括 duration）
  const player = playerRef.value as any
  if (player) {
    duration.value = player.duration?.value ?? player.duration ?? 0
  }
  // 开始同步状态
  startStateSync()
  emit('ready')
}

function startStateSync() {
  if (rafId) cancelAnimationFrame(rafId)
  const syncLoop = () => {
    syncPlayerState()
    rafId = requestAnimationFrame(syncLoop)
  }
  rafId = requestAnimationFrame(syncLoop)
}

function stopStateSync() {
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
}

function syncPlayerState() {
  if (!playerRef.value) return

  // 从 VideoPlayer 同步所有状态
  const player = playerRef.value as any
  isPaused.value = player.isPaused?.value ?? player.isPaused ?? true
  isMuted.value = player.isMuted?.value ?? player.isMuted ?? false
  volume.value = player.volume?.value ?? player.volume ?? 1
  // duration 可能在元数据加载后才更新，需要持续同步
  const playerDuration = player.duration?.value ?? player.duration ?? 0
  if (playerDuration > 0) {
    duration.value = playerDuration
  }
  buffered.value = player.buffered?.value ?? player.buffered ?? 0
  currentPlaybackRate.value = player.currentPlaybackRate?.value ?? player.currentPlaybackRate ?? 1
  currentAspectRatio.value = player.currentAspectRatio?.value ?? player.currentAspectRatio ?? 'default'
  // 同步全屏状态（网页全屏由父组件控制，不同步）
  isFullscreen.value = player.isFullscreen?.value ?? player.isFullscreen ?? false
}

function onTimeUpdate(time: number) {
  currentTime.value = time
  // 同时从 playerRef 同步其他状态
  const player = playerRef.value as any
  if (player) {
    isPaused.value = player.isPaused?.value ?? player.isPaused ?? true
    isMuted.value = player.isMuted?.value ?? player.isMuted ?? false
    volume.value = player.volume?.value ?? player.volume ?? 1
    duration.value = player.duration?.value ?? player.duration ?? 0
    buffered.value = player.buffered?.value ?? player.buffered ?? 0
    isFullscreen.value = player.isFullscreen?.value ?? player.isFullscreen ?? false
    currentPlaybackRate.value = player.currentPlaybackRate?.value ?? player.currentPlaybackRate ?? 1
    currentAspectRatio.value = player.currentAspectRatio?.value ?? player.currentAspectRatio ?? 'default'
    // 网页全屏由父组件控制，不同步
  }
}

// 控制方法
function play() {
  playerRef.value?.play()
}

function pause() {
  playerRef.value?.pause()
}

function seek(time: number) {
  // 立即更新本地状态，让进度条立即响应
  currentTime.value = time
  playerRef.value?.seek(time)
}

function toggleMute() {
  playerRef.value?.toggleMute()
}

function toggleFullscreen() {
  playerRef.value?.toggleFullscreen()
}

function setPlaybackRate(rate: number) {
  playerRef.value?.setPlaybackRate(rate)
}

function setAspectRatio(ratio: string) {
  playerRef.value?.setAspectRatio(ratio)
}

function toggleDanmaku() {
  danmakuSettings.enabled = !danmakuSettings.enabled
}

async function sendDanmaku(text: string, mode?: 'scroll' | 'top' | 'bottom') {
  if (!props.isLoggedIn) {
    emit('login')
    return
  }

  try {
    // 使用传入的 mode 或设置的默认 mode
    const danmakuMode = mode || danmakuSettings.defaultMode
    // 如果正在播放，则实时显示弹幕
    await danmakuManager.sendDanmaku(text, currentTime.value, '#ffffff', danmakuMode, !isPaused.value)
  } catch (err) {
    console.error('发送弹幕失败:', err)
  }
}

// 监听视频ID变化，重置提醒状态
watch(() => props.videoId, () => {
  reminderShown.value = false
})

// 弹幕提醒触发逻辑
function triggerReminderCheck() {
  // 立即捕获当前时间，避免延迟期间时间变化
  const checkTime = currentTime.value
  // 延迟2秒检查（给播放器一点缓冲时间）
  setTimeout(() => {
    checkAndShowReminder(checkTime)
  }, 2000)
}

// 调试用的立即触发函数
function forceTriggerReminder() {
  reminderShown.value = false
  checkAndShowReminder(currentTime.value)
}

// 监听弹幕加载完成，触发一次提醒检查（每个剧集只触发一次）
watch(() => danmakuManager.loading.value, (loading, oldLoading) => {
  // 从 true/undefined 变为 false 表示加载完成
  if (oldLoading !== false && loading === false) {
    triggerReminderCheck()
  }
})

// 监听全屏变化
onMounted(() => {
  // 如果弹幕已经加载完成，触发提醒检查
  if (!danmakuManager.loading.value && !reminderShown.value) {
    triggerReminderCheck()
  }

  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })
})

// 组件卸载时清理
onUnmounted(() => {
  stopStateSync()
})

defineExpose({
  play,
  pause,
  seek,
  toggleDanmaku,
  clearDanmaku: danmakuManager.clearDanmaku,
  setHasMultipleSources: (value: boolean) => playerRef.value?.setHasMultipleSources?.(value),
  // 调试函数
  forceTriggerReminder,
})
</script>

<style scoped>
.video-player-with-danmaku :deep(.danmaku-layer) {
  pointer-events: none;
}
</style>
