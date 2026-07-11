<template>
  <div class="relative">
    <!-- 播放记录按钮 -->
    <button
      ref="buttonRef"
      class="flex items-center gap-2 text-sm transition-colors"
      :class="variant === 'light' ? 'text-white/70 hover:text-white' : 'text-white/70 hover:text-white'"
      @click="toggleDropdown"
    >
      <el-icon :size="18"><Clock /></el-icon>
      <span class="hidden sm:inline">历史</span>
    </button>

    <!-- 下拉弹窗 - 客户端渲染避免 Safari SSR 问题 -->
    <Teleport v-if="isClient" to="body">
      <Transition name="fade">
        <div
          v-if="showDropdown"
          ref="dropdownRef"
          class="fixed z-50 rounded-lg shadow-lg py-2 w-72 max-w-[calc(100vw-32px)] dropdown-transparent"
          :style="dropdownStyle"
        >
          <div class="px-3 py-2 flex items-center justify-between">
            <span class="font-medium text-sm text-gray-200">最近播放</span>
            <button
              v-if="history.length > 0"
              class="text-xs text-gray-500 hover:text-red-400 transition-colors"
              @click="clearAll"
            >
              清空
            </button>
          </div>

          <div v-if="loading" class="px-3 py-8 text-center text-gray-500 text-sm">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span class="ml-1">加载中...</span>
          </div>

          <div v-else-if="history.length > 0" class="max-h-[60vh] overflow-y-auto">
            <a
              v-for="item in history"
              :key="item.id"
              :href="routes.stream(generateMovieSlug(item.id, item.title), { source: 0, episode: 0 })"
              target="_blank"
              class="flex items-center gap-2.5 px-3 py-2 hover:bg-white/10 transition-colors"
              @click="showDropdown = false"
            >
              <img
                :src="getHistoryCover(item)"
                :alt="item.title"
                class="w-8 h-11 object-cover rounded flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-200 truncate">{{ item.title }}</p>
                <p class="text-xs text-gray-500 truncate mt-0.5">{{ formatRelativeTime(item.timestamp) }}</p>
              </div>
            </a>
          </div>

          <div v-else class="px-3 py-8 text-center text-gray-500 text-sm">
            暂无播放记录
          </div>
        </div>
      </Transition>

      <!-- 遮罩层 -->
      <div
        v-if="showDropdown"
        class="fixed inset-0 z-40"
        @click="showDropdown = false"
      />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { Clock, Loading } from '@element-plus/icons-vue'
import { onClickOutside } from '@vueuse/core'
import type { PlayHistory } from '~/composables/useHistory'

// 客户端标识（用于模板）
const isClient = import.meta.client

interface Props {
  variant?: 'default' | 'light'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const { getHistory, clearHistory } = useHistory()
const { getBestCover } = useImageProxy()

const showDropdown = ref(false)
const rawHistory = ref<PlayHistory[]>([])
const loading = ref(false)
const dropdownPos = ref({ top: 0, left: 0 })

// 处理封面URL - 使用与分类列表相同的 getBestCover 方法
const getHistoryCover = (item: PlayHistory): string => {
  // 使用 getBestCover 优先获取非豆瓣图片，如果没有则使用 cover 作为 fallback
  return getBestCover(item.covers || [], item.cover) || '/placeholder.jpg'
}

// 格式化相对时间（如：5分钟前、2小时前、3天前）
const formatRelativeTime = (timestamp: number): string => {
  const now = Date.now()
  const diff = now - timestamp

  // 时间间隔（毫秒）
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day
  const year = 365 * day

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    const minutes = Math.floor(diff / minute)
    return `${minutes}分钟前`
  } else if (diff < day) {
    const hours = Math.floor(diff / hour)
    return `${hours}小时前`
  } else if (diff < week) {
    const days = Math.floor(diff / day)
    return `${days}天前`
  } else if (diff < month) {
    const weeks = Math.floor(diff / week)
    return `${weeks}周前`
  } else if (diff < year) {
    const months = Math.floor(diff / month)
    return `${months}个月前`
  } else {
    const years = Math.floor(diff / year)
    return `${years}年前`
  }
}

// 过滤掉不完整的记录（可能由于之前的bug导致），并按时间戳降序排序（最近的在前）
const history = computed(() => {
  return rawHistory.value
    .filter(item => item.id && item.title)
    .sort((a, b) => b.timestamp - a.timestamp)
})
const buttonRef = ref<HTMLElement>()
const dropdownRef = ref<HTMLElement>()

const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 640 // sm breakpoint
})

const dropdownStyle = computed(() => {
  return {
    top: `${dropdownPos.value.top}px`,
    left: `${dropdownPos.value.left}px`
  }
})

// 计算弹窗位置
const calculatePosition = () => {
  if (!buttonRef.value || !process.client) return

  const rect = buttonRef.value.getBoundingClientRect()
  const dropdownWidth = 288 // w-72 = 18rem = 288px
  const windowWidth = window.innerWidth

  // 始终在按钮下方显示
  const top = rect.bottom + 8

  // 按钮中线和弹窗中线对齐
  const buttonCenter = rect.left + rect.width / 2
  let left = buttonCenter - dropdownWidth / 2

  // 确保不超出左右边界
  left = Math.max(16, Math.min(left, windowWidth - dropdownWidth - 16))

  dropdownPos.value = { top, left }
}

const loadHistory = async () => {
  loading.value = true
  try {
    rawHistory.value = await getHistory()
  } catch (error) {
    console.error('加载播放记录失败:', error)
    rawHistory.value = []
  } finally {
    loading.value = false
  }
}

const toggleDropdown = () => {
  if (!showDropdown.value) {
    // 打开时计算位置并刷新数据
    if (process.client) {
      calculatePosition()
      loadHistory()
    }
  }
  showDropdown.value = !showDropdown.value
}

const clearAll = async () => {
  await clearHistory()
  rawHistory.value = []
}

// 点击外部关闭
onClickOutside(dropdownRef, () => {
  showDropdown.value = false
})

// 窗口大小变化时重新计算位置或关闭弹窗
onMounted(() => {
  const handleResize = () => {
    if (showDropdown.value) {
      // 窗口变化时重新计算位置
      calculatePosition()
    }
  }
  window.addEventListener('resize', handleResize)
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
