<template>
  <div
    class="player-controls absolute bottom-0 left-0 right-0 z-20 bg-gradient-to-t from-black/80 via-black/40 to-transparent px-2 sm:px-3 pb-1.5 sm:pb-2 pt-6 sm:pt-8 transition-opacity duration-300"
    :class="{ 'opacity-0': !visible && !isPaused, 'opacity-100': visible || isPaused }"
    @mouseenter="showControls"
    @mouseleave="hideControls"
  >
    <!-- 上层：进度条 -->
    <div class="flex items-center gap-1 sm:gap-1.5 mb-1.5 sm:mb-2">
      <!-- 当前时间 -->
      <span class="text-[10px] sm:text-xs text-white/90 min-w-[36px] sm:min-w-[45px] text-right tabular-nums" style="font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;">{{ formatTime(currentTime) }}</span>

      <!-- 进度条容器 - 增加可点击区域 -->
      <div
        ref="progressRef"
        class="flex-1 h-5 sm:h-4 flex items-center cursor-pointer relative group"
        @click="onProgressClick"
        @mousedown="onProgressDragStart"
        @mousemove="onProgressHover"
        @mouseenter="showTooltip = true"
        @mouseleave="showTooltip = false"
      >
        <!-- 进度条背景轨道 -->
        <div class="w-full h-2 sm:h-1.5 bg-white/30 rounded-full relative overflow-hidden">
          <!-- 缓冲进度 -->
          <div
            class="absolute left-0 top-0 h-full bg-white/40 rounded-full pointer-events-none transition-all duration-100"
            :style="{ width: `${bufferedPercent}%` }"
          />
          <!-- 播放进度 -->
          <div
            class="absolute left-0 top-0 h-full bg-app-primary rounded-full pointer-events-none transition-all duration-100"
            :style="{ width: `${progressPercent}%` }"
          />
        </div>
        <!-- 拖动点 - 位于轨道上方 -->
        <div
          class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
          :style="{ left: `${progressPercent}%`, transform: `translate(-50%, -50%)` }"
        />
        <!-- 时间提示框 -->
        <div
          v-if="showTooltip && duration > 0"
          class="absolute -top-6 sm:-top-5 px-1.5 py-0.5 bg-black/80 rounded text-[10px] text-white pointer-events-none transform -translate-x-1/2"
          :style="{ left: `${tooltipPosition}%` }"
        >
          {{ formatTime(tooltipTime) }}
        </div>
      </div>

      <!-- 总时长 -->
      <span class="text-[10px] sm:text-xs text-white/90 min-w-[36px] sm:min-w-[45px] text-right tabular-nums" style="font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;">{{ formatTime(duration) }}</span>
    </div>

    <!-- 下层：控制按钮 -->
    <div class="flex items-center justify-between">
      <!-- 左侧按钮组 -->
      <div class="flex items-center gap-0.5 sm:gap-1">
        <!-- 播放/暂停 -->
        <button
          class="p-1.5 rounded hover:bg-white/20 transition-colors text-white"
          :title="isPaused ? '播放' : '暂停'"
          @click="togglePlay"
        >
          <img
            :src="isPaused ? '/ic_play.png' : '/ic_pause.png'"
            class="w-4 h-4"
            :alt="isPaused ? '播放' : '暂停'"
          >
        </button>

        <!-- 静音 -->
        <button
          class="p-1.5 rounded hover:bg-white/20 transition-colors text-white"
          :title="isMuted ? '取消静音' : '静音'"
          @click="$emit('toggleMute')"
        >
          <img
            :src="isMuted ? '/ic_volumn_off.png' : '/ic_volumn_on.png'"
            class="w-4 h-4"
            :alt="isMuted ? '取消静音' : '静音'"
          >
        </button>

        <!-- 弹幕开关 -->
        <button
          v-if="showDanmaku"
          class="p-2 sm:p-1.5 rounded hover:bg-white/20 transition-colors"
          :title="danmakuEnabled ? '关闭弹幕' : '开启弹幕'"
          @click="$emit('toggleDanmaku')"
        >
          <img
            :src="danmakuEnabled ? '/ic_danmaku_on.png' : '/ic_danmaku_off.png'"
            class="w-5 h-5 sm:w-[18px] sm:h-[18px]"
            :class="{ 'opacity-100': danmakuEnabled, 'opacity-70': !danmakuEnabled }"
            alt="弹幕"
          >
        </button>

        <!-- 弹幕设置 - 仅PC端显示 -->
        <div v-if="showDanmaku" ref="danmakuSettingsRef" class="hidden sm:block relative">
          <button
            class="p-2 sm:p-1.5 rounded hover:bg-white/20 transition-colors"
            title="弹幕设置"
            @click="showDanmakuSettings = !showDanmakuSettings"
          >
            <img
              src="/ic_dnamaku_setting.png"
              class="w-5 h-5 sm:w-[18px] sm:h-[18px]"
              :class="{ 'opacity-100': showDanmakuSettings, 'opacity-70': !showDanmakuSettings }"
              alt="弹幕设置"
            >
          </button>

          <!-- PC端弹幕设置弹窗 -->
          <Transition name="fade-up">
            <div
              v-if="showDanmakuSettings"
              class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-black rounded-lg py-2 min-w-[200px] shadow-xl border border-white/10"
              @mouseenter="showControls"
              @click.stop
            >
              <!-- 弹窗标题 -->
              <div class="px-3 pb-2 border-b border-white/10">
                <span class="text-xs text-white/90 font-medium">弹幕设置</span>
              </div>

              <!-- 速度选择 -->
              <div class="px-3 py-2">
                <div class="text-[10px] text-white/50 mb-1.5">弹幕速度</div>
                <div class="flex gap-1">
                  <button
                    v-for="option in speedOptions"
                    :key="option.value"
                    class="flex-1 px-2 py-1 rounded text-[11px] transition-colors"
                    :class="danmakuSpeed === option.value ? 'bg-app-primary text-white' : 'bg-white/10 text-white/70 hover:bg-white/20'"
                    @click="$emit('updateDanmakuSpeed', option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>

              <!-- 透明度设置 -->
              <div class="px-3 py-2 border-t border-white/10">
                <div class="text-[10px] text-white/50 mb-1.5">不透明度 {{ Math.round(danmakuOpacity * 100) }}% (最低50%)</div>
                <input
                  type="range"
                  min="0.5"
                  max="1"
                  step="0.1"
                  :value="danmakuOpacity"
                  class="w-full h-1 bg-white/20 rounded-full appearance-none cursor-pointer accent-app-primary"
                  @input="$emit('updateDanmakuOpacity', Math.max(0.5, parseFloat(($event.target as HTMLInputElement).value)))"
                >
              </div>

              <!-- 默认发送类型 -->
              <div class="px-3 py-2 border-t border-white/10">
                <div class="text-[10px] text-white/50 mb-1.5">默认发送位置</div>
                <div class="flex gap-1">
                  <button
                    v-for="option in modeOptions"
                    :key="option.value"
                    class="flex-1 px-2 py-1 rounded text-[11px] transition-colors"
                    :class="defaultMode === option.value ? 'bg-app-primary text-white' : 'bg-white/10 text-white/70 hover:bg-white/20'"
                    @click="$emit('updateDefaultMode', option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>

              <!-- 屏蔽选项 -->
              <div class="px-3 py-2 border-t border-white/10">
                <div class="text-[10px] text-white/50 mb-1.5">屏蔽类型</div>
                <div class="flex gap-3">
                  <label class="flex items-center gap-1.5 text-[11px] text-white/80 cursor-pointer hover:text-white transition-colors">
                    <input
                      type="checkbox"
                      :checked="blockScroll"
                      class="w-3.5 h-3.5 rounded border-white/30 bg-transparent accent-app-primary cursor-pointer"
                      @change="$emit('updateBlockScroll', ($event.target as HTMLInputElement).checked)"
                    >
                    <span>滚动</span>
                  </label>
                  <label class="flex items-center gap-1.5 text-[11px] text-white/80 cursor-pointer hover:text-white transition-colors">
                    <input
                      type="checkbox"
                      :checked="blockTop"
                      class="w-3.5 h-3.5 rounded border-white/30 bg-transparent accent-app-primary cursor-pointer"
                      @change="$emit('updateBlockTop', ($event.target as HTMLInputElement).checked)"
                    >
                    <span>顶部</span>
                  </label>
                  <label class="flex items-center gap-1.5 text-[11px] text-white/80 cursor-pointer hover:text-white transition-colors">
                    <input
                      type="checkbox"
                      :checked="blockBottom"
                      class="w-3.5 h-3.5 rounded border-white/30 bg-transparent accent-app-primary cursor-pointer"
                      @change="$emit('updateBlockBottom', ($event.target as HTMLInputElement).checked)"
                    >
                    <span>底部</span>
                  </label>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 弹幕输入框 - 移动端隐藏 -->
        <div v-if="showDanmaku && danmakuEnabled" class="hidden sm:flex items-center gap-1 ml-0.5 sm:ml-1">
          <input
            v-model="danmakuInputText"
            type="text"
            maxlength="50"
            :placeholder="inputPlaceholder"
            :disabled="!isLoggedIn"
            class="w-32 sm:w-48 h-7 sm:h-6 px-2 sm:px-2.5 rounded-full bg-white/10 border border-white/20 focus:border-app-primary focus:outline-none text-xs text-white placeholder-white/40 disabled:opacity-50 transition-colors"
            @keydown.enter="sendDanmakuText"
          >
          <button
            class="w-7 h-7 sm:w-6 sm:h-6 flex items-center justify-center bg-app-primary hover:bg-app-primary-hover disabled:bg-white/20 disabled:cursor-not-allowed rounded-full text-white transition-colors"
            :disabled="!isLoggedIn || !danmakuInputText.trim()"
            @click="sendDanmakuText"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 sm:w-3 sm:h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 右侧按钮组 -->
      <div class="flex items-center gap-0.5 sm:gap-1">
        <!-- 显示设置 - 仅PC端显示 -->
        <div ref="displaySettingsRef" class="hidden sm:block relative">
          <button
            class="p-2 sm:p-1.5 rounded hover:bg-white/20 transition-colors text-white/70 hover:text-white"
            :class="{ 'text-blue-400 bg-white/10': showDisplaySettings }"
            title="显示设置"
            @click="showDisplaySettings = !showDisplaySettings"
          >
            <img
              src="/ic_setting.png"
              class="w-5 h-5 sm:w-[18px] sm:h-[18px] opacity-80"
              :class="{ 'opacity-100': showDisplaySettings }"
              alt="设置"
            >
          </button>

          <!-- PC端显示设置弹窗 -->
          <Transition name="fade-up-offset">
            <div
              v-if="showDisplaySettings"
              class="absolute bottom-full left-1/2 -translate-x-2/3 mb-2 bg-black rounded-lg py-2 min-w-[220px] shadow-xl border border-white/10"
              @mouseenter="showControls"
              @click.stop
            >
              <!-- 播放速度 -->
              <div class="px-3 py-2">
                <div class="text-[10px] text-white/50 mb-2">播放速度</div>
                <div class="flex gap-1.5">
                  <button
                    v-for="rate in playbackRates"
                    :key="rate"
                    class="flex-1 px-1 py-1 rounded text-[11px] transition-colors"
                    :class="currentPlaybackRate === rate ? 'bg-app-primary text-white' : 'bg-white/10 text-white/70 hover:bg-white/20'"
                    @click="setPlaybackRate(rate)"
                  >
                    {{ rate }}x
                  </button>
                </div>
              </div>

              <!-- 画面比例 -->
              <div class="px-3 py-2 border-t border-white/10">
                <div class="text-[10px] text-white/50 mb-2">画面比例</div>
                <div class="flex gap-1.5">
                  <button
                    v-for="ratio in aspectRatios"
                    :key="ratio"
                    class="flex-1 px-1 py-1 rounded text-[11px] transition-colors"
                    :class="currentAspectRatio === ratio ? 'bg-app-primary text-white' : 'bg-white/10 text-white/70 hover:bg-white/20'"
                    @click="setAspectRatio(ratio)"
                  >
                    {{ ratio === 'default' ? '默认' : ratio }}
                  </button>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- AirPlay -->
        <button
          v-if="supportsAirPlay"
          class="p-2 sm:p-1.5 rounded hover:bg-white/20 transition-colors text-white/70 hover:text-white"
          title="AirPlay"
          @click="toggleAirPlay"
        >
          <img
            src="/ic_airplay.png"
            class="w-5 h-5 sm:w-[18px] sm:h-[18px] opacity-80"
            alt="AirPlay"
          >
        </button>

        <!-- 画中画 -->
        <button
          v-if="supportsPiP"
          class="p-2 sm:p-1.5 rounded hover:bg-white/20 transition-colors text-white/70 hover:text-white"
          :class="{ 'text-blue-400': isPiPActive }"
          title="画中画"
          @click="togglePiP"
        >
          <img
            src="/ic_picture_on_picture.png"
            class="w-5 h-5 sm:w-[18px] sm:h-[18px]"
            :class="{ 'opacity-80': !isPiPActive, 'opacity-100': isPiPActive }"
            alt="画中画"
          >
        </button>

        <!-- 全屏 -->
        <button
          class="p-2 sm:p-1.5 rounded hover:bg-white/20 transition-colors text-white/70 hover:text-white"
          :class="{ 'text-blue-400': isFullscreen }"
          title="全屏"
          @click="toggleFullscreen"
        >
          <img
            :src="isFullscreen ? '/ic_fullscreen_exit.png' : '/ic_fullscreen.png'"
            class="w-5 h-5 sm:w-[18px] sm:h-[18px]"
            :class="{ 'opacity-80': !isFullscreen, 'opacity-100': isFullscreen }"
            alt="全屏"
          >
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onClickOutside } from '@vueuse/core'
import { getRandomReminderMessage } from '~/config/danmaku.config'

interface Props {
  // 播放器状态
  isPaused: boolean
  isMuted: boolean
  volume: number
  currentTime: number
  duration: number
  buffered?: number

  // 全屏状态
  isFullscreen: boolean

  // 弹幕相关
  showDanmaku?: boolean
  danmakuEnabled?: boolean
  danmakuSpeed?: 'slow' | 'normal' | 'fast'
  danmakuOpacity?: number
  blockScroll?: boolean
  blockTop?: boolean
  blockBottom?: boolean
  defaultMode?: 'scroll' | 'top' | 'bottom'
  isLoggedIn?: boolean

  // 显示设置
  currentPlaybackRate?: number
  currentAspectRatio?: string
}

const props = withDefaults(defineProps<Props>(), {
  buffered: 0,
  isPaused: true,
  isMuted: false,
  volume: 1,
  currentTime: 0,
  duration: 0,
  isFullscreen: false,
  showDanmaku: false,
  danmakuEnabled: true,
  danmakuSpeed: 'normal',
  danmakuOpacity: 1,
  blockScroll: false,
  blockTop: false,
  blockBottom: false,
  defaultMode: 'scroll',
  isLoggedIn: false,
  currentPlaybackRate: 1,
  currentAspectRatio: 'default',
})

const emit = defineEmits<{
  play: []
  pause: []
  seek: [time: number]
  toggleMute: []
  toggleFullscreen: []
  toggleDanmaku: []
  updateDanmakuSpeed: [speed: 'slow' | 'normal' | 'fast']
  updateDanmakuOpacity: [opacity: number]
  updateBlockScroll: [blocked: boolean]
  updateBlockTop: [blocked: boolean]
  updateBlockBottom: [blocked: boolean]
  updateDefaultMode: [mode: 'scroll' | 'top' | 'bottom']
  sendDanmaku: [text: string, mode: 'scroll' | 'top' | 'bottom']
  updatePlaybackRate: [rate: number]
  updateAspectRatio: [ratio: string]
}>()

// 本地状态
const visible = ref(true)
const hideTimer = ref<ReturnType<typeof setTimeout> | null>(null)
const danmakuInputText = ref('')
const showDanmakuSettings = ref(false)
const showDisplaySettings = ref(false)
const isPiPActive = ref(false)
const supportsPiP = ref(false)
const supportsAirPlay = ref(false)

// 进度条 tooltip 状态
const showTooltip = ref(false)
const tooltipTime = ref(0)
const tooltipPosition = ref(0)

// Refs
const progressRef = ref<HTMLElement>()
const danmakuSettingsRef = ref<HTMLElement>()
const displaySettingsRef = ref<HTMLElement>()

// 弹幕输入框 placeholder（随机提示文案）
const inputPlaceholder = computed(() => {
  if (!props.isLoggedIn) {
    return '登录后发弹幕'
  }
  // 从提示文案中随机选择一条
  return getRandomReminderMessage()
})

// 选项
const speedOptions = [
  { label: '慢速', value: 'slow' as const },
  { label: '正常', value: 'normal' as const },
  { label: '快速', value: 'fast' as const },
]

const modeOptions = [
  { label: '滚动', value: 'scroll' as const },
  { label: '顶部', value: 'top' as const },
  { label: '底部', value: 'bottom' as const },
]

const playbackRates = [0.5, 0.75, 1, 1.25, 1.5, 2]
const aspectRatios = ['default', '4:3', '16:9', 'full']

// 计算属性
const progressPercent = computed(() => {
  if (!props.duration || props.duration <= 0) return 0
  return (props.currentTime / props.duration) * 100
})

const bufferedPercent = computed(() => {
  if (!props.duration) return 0
  return (props.buffered / props.duration) * 100
})

// 方法 - 格式化时间为 MM:SS 或 HH:MM:SS
function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds) || seconds < 0) return '00:00'

  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  const minsStr = mins.toString().padStart(2, '0')
  const secsStr = secs.toString().padStart(2, '0')

  if (hours > 0) {
    return `${hours}:${minsStr}:${secsStr}`
  }
  return `${minsStr}:${secsStr}`
}

function togglePlay() {
  if (props.isPaused) {
    emit('play')
  } else {
    emit('pause')
  }
}

function onProgressClick(e: MouseEvent) {
  if (!progressRef.value || !props.duration || props.duration <= 0) return

  const rect = progressRef.value.getBoundingClientRect()
  const clickX = e.clientX - rect.left
  const percent = Math.max(0, Math.min(1, clickX / rect.width))
  const time = percent * props.duration

  emit('seek', time)
}

function onProgressDragStart(e: MouseEvent) {
  e.preventDefault()
  e.stopPropagation()

  // 立即执行一次点击跳转
  onProgressClick(e)

  const handleMouseMove = (e: MouseEvent) => {
    onProgressClick(e)
  }

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function onProgressHover(e: MouseEvent) {
  if (!progressRef.value || !props.duration || props.duration <= 0) return

  const rect = progressRef.value.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const percent = Math.max(0, Math.min(1, mouseX / rect.width))

  tooltipTime.value = percent * props.duration
  tooltipPosition.value = percent * 100
}

function showControls() {
  visible.value = true
  if (hideTimer.value) {
    clearTimeout(hideTimer.value)
    hideTimer.value = null
  }
}

function hideControls() {
  if (hideTimer.value) {
    clearTimeout(hideTimer.value)
  }
  hideTimer.value = setTimeout(() => {
    if (!props.isPaused) {
      visible.value = false
      // 隐藏控制栏时同时关闭设置弹窗
      showDanmakuSettings.value = false
      showDisplaySettings.value = false
    }
  }, 2000)
}

function sendDanmakuText() {
  const text = danmakuInputText.value.trim()
  if (text) {
    emit('sendDanmaku', text, props.defaultMode)
    danmakuInputText.value = ''
  }
}

function toggleFullscreen() {
  emit('toggleFullscreen')
}

function setPlaybackRate(rate: number) {
  emit('updatePlaybackRate', rate)
}

function setAspectRatio(ratio: string) {
  emit('updateAspectRatio', ratio)
}

async function togglePiP() {
  const video = document.querySelector('video')
  if (!video) return

  try {
    if (document.pictureInPictureElement) {
      await document.exitPictureInPicture()
      isPiPActive.value = false
    } else {
      await video.requestPictureInPicture()
      isPiPActive.value = true
    }
  } catch (err) {
    console.error('PiP error:', err)
  }
}

function toggleAirPlay() {
  const video = document.querySelector('video') as any
  if (video && video.webkitShowPlaybackTargetPicker) {
    video.webkitShowPlaybackTargetPicker()
  }
}

// 监听弹幕开关变化，显示提示
let lastDanmakuEnabled = props.danmakuEnabled
watch(() => props.danmakuEnabled, (newVal) => {
  if (newVal !== lastDanmakuEnabled) {
    lastDanmakuEnabled = newVal
    if (process.client) {
      if (newVal) {
        ElMessage.success('弹幕已开启')
      } else {
        ElMessage.info('弹幕已关闭')
      }
    }
  }
})

// 点击外部关闭弹窗
onClickOutside(danmakuSettingsRef, () => {
  showDanmakuSettings.value = false
})

onClickOutside(displaySettingsRef, () => {
  showDisplaySettings.value = false
})

// 生命周期
onMounted(() => {
  // 检查功能支持
  supportsPiP.value = document.pictureInPictureEnabled ?? false

  // AirPlay 检测：延迟检测并使用 MutationObserver 监听 video 元素
  const checkAirPlay = () => {
    const video = document.querySelector('video') as any
    // iOS Safari: webkitShowPlaybackTargetPicker
    // macOS Safari: airplay 属性
    const hasAirPlay = !!(video && (
      video.webkitShowPlaybackTargetPicker ||
      ('airplay' in video && typeof video.airplay !== 'undefined')
    ))
    supportsAirPlay.value = hasAirPlay
  }

  // 延迟检测，等待 ArtPlayer 初始化
  setTimeout(checkAirPlay, 500)
  setTimeout(checkAirPlay, 1500)

  // 监听 video 元素的变化
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === 'childList') {
        const video = document.querySelector('video') as any
        if (video && !supportsAirPlay.value) {
          checkAirPlay()
        }
      }
    }
  })
  observer.observe(document.body, { childList: true, subtree: true })

  // 清理 observer
  onUnmounted(() => {
    observer.disconnect()
  })

  // 监听 PiP 变化
  document.addEventListener('enterpictureinpicture', () => {
    isPiPActive.value = true
  })
  document.addEventListener('leavepictureinpicture', () => {
    isPiPActive.value = false
  })
})
</script>

<style scoped>
/* PC端弹窗动画 - 从底部滑入（居中） */
@media (min-width: 640px) {
  .fade-up-enter-active,
  .fade-up-leave-active {
    transition: all 0.2s ease;
  }

  .fade-up-enter-from,
  .fade-up-leave-to {
    opacity: 0;
    transform: translateX(-50%) translateY(8px);
  }

  /* PC端弹窗动画 - 从底部滑入（2/3处对齐） */
  .fade-up-offset-enter-active,
  .fade-up-offset-leave-active {
    transition: all 0.2s ease;
  }

  .fade-up-offset-enter-from,
  .fade-up-offset-leave-to {
    opacity: 0;
    transform: translateX(-66.67%) translateY(8px);
  }
}

/* 移动端居中弹窗动画 - 缩放淡入 */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.2s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 滑块样式 */
input[type="range"] {
  -webkit-appearance: none;
  background: transparent;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-app-primary);
  cursor: pointer;
  margin-top: -3.5px;
}

input[type="range"]::-webkit-slider-runnable-track {
  width: 100%;
  height: 3px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

input[type="range"]:focus::-webkit-slider-runnable-track {
  background: rgba(255, 255, 255, 0.3);
}
</style>
