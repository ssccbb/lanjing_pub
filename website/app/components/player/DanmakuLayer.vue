<template>
  <div
    ref="danmakuContainer"
    class="danmaku-layer absolute inset-0 pointer-events-none overflow-hidden z-10"
    :class="{ 'opacity-0': !visible }"
  >
    <!-- 弹幕轨道 -->
    <div
      v-for="track in trackCount"
      :key="track"
      class="danmaku-track absolute w-full h-8 flex items-center"
      :style="{ top: `${(track - 1) * trackHeight}px` }"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 弹幕层组件 - 完全独立于播放器
 * 性能优化：使用 CSS transform + will-change，单条弹幕使用 RAF 动画
 */

/** 弹幕项 - 与后端 API 格式一致 */
export interface DanmakuItem {
  id: string
  text: string
  time: number
  mode?: 'scroll' | 'top' | 'bottom'
  color?: string
  userId?: string
  userName?: string
  likes?: number
  createdAt?: number
}

interface Props {
  /** 弹幕数据列表 */
  items: DanmakuItem[]
  /** 是否显示弹幕 */
  visible?: boolean
  /** 播放进度（秒） */
  currentTime?: number
  /** 轨道数量 */
  trackCount?: number
  /** 轨道高度（像素） */
  trackHeight?: number
  /** 弹幕速度级别 */
  speedLevel?: 'slow' | 'normal' | 'fast'
  /** 透明度 */
  opacity?: number
  /** 屏蔽的弹幕类型 */
  blockedModes?: Array<'scroll' | 'top' | 'bottom'>
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  currentTime: 0,
  trackCount: 8,
  trackHeight: 36,
  speedLevel: 'normal',
  opacity: 1,
  blockedModes: () => [],
})

// 速度级别对应的像素/秒
const speedMap = {
  slow: 80,
  normal: 120,
  fast: 180,
}

// ==================== Refs ====================
const danmakuContainer = ref<HTMLElement>()
const danmakuElements = new Map<string, HTMLElement>()
const trackStates = ref<number[]>([])
const renderedIds = new Set<string>()

// ==================== 初始化 ====================
onMounted(() => {
  trackStates.value = new Array(props.trackCount).fill(0)
})

onUnmounted(() => {
  danmakuElements.forEach(el => el.remove())
  danmakuElements.clear()
  renderedIds.clear()
})

// ==================== 监听弹幕数据变化（处理ID变更和颜色更新）====================
watch(() => props.items, (newItems, oldItems) => {
  // 检查是否有ID变更（临时ID -> 真实ID）或颜色更新
  if (!oldItems || oldItems === newItems) return

  for (const newItem of newItems) {
    // 如果新ID不在 oldItems 中，且不是临时ID，可能是替换的
    const isNewId = !oldItems.some(old => old.id === newItem.id)

    if (isNewId && !newItem.id.startsWith('temp_')) {
      // 查找匹配的临时项（时间、文本相同）
      const tempItem = oldItems.find(old =>
        old.id.startsWith('temp_') &&
        old.time === newItem.time &&
        old.text === newItem.text
      )

      if (tempItem) {
        // ID 变更：更新 DOM 元素的颜色和引用
        const el = danmakuElements.get(tempItem.id)
        if (el) {
          // 更新颜色（后端返回的角色颜色）
          if (newItem.color && newItem.color !== tempItem.color) {
            el.style.color = newItem.color
          }
          // 更新 Map 中的引用
          danmakuElements.delete(tempItem.id)
          danmakuElements.set(newItem.id, el)
          // 更新 renderedIds
          renderedIds.delete(tempItem.id)
          renderedIds.add(newItem.id)
        }
      }
    }
  }
}, { deep: true })

// ==================== 监听设置变化 ====================
// 透明度变化 - 更新所有已渲染弹幕
watch(() => props.opacity, (newOpacity) => {
  danmakuElements.forEach(el => {
    el.style.opacity = String(newOpacity)
  })
})

// 屏蔽模式变化 - 移除被屏蔽类型的弹幕
watch(() => props.blockedModes, (newBlockedModes) => {
  if (!newBlockedModes || newBlockedModes.length === 0) return

  // 移除被屏蔽模式的弹幕
  for (const [id, el] of danmakuElements) {
    const item = props.items.find(i => i.id === id)
    if (item && newBlockedModes.includes(item.mode || 'scroll')) {
      el.remove()
      danmakuElements.delete(id)
      renderedIds.delete(id)
    }
  }
}, { deep: true })

// 速度变化 - 更新所有滚动弹幕的动画速度
watch(() => props.speedLevel, (newSpeed) => {
  const speed = speedMap[newSpeed]

  danmakuElements.forEach((el, id) => {
    const item = props.items.find(i => i.id === id)
    if (!item || item.mode !== 'scroll') return

    // 获取当前动画
    const animation = el.getAnimations()[0]
    if (animation) {
      // 重新计算动画时长
      const containerWidth = danmakuContainer.value?.clientWidth || 0
      const textWidth = el.offsetWidth
      const distance = containerWidth + textWidth
      const newDuration = distance / speed * 1000

      // 更新动画速度
      animation.effect?.updateTiming({ duration: newDuration })
    }
  })
})

// ==================== 监听播放进度 ====================
watch(() => props.currentTime, (time) => {
  if (!props.visible) return
  renderDanmakuAtTime(time)
})

// ==================== 监听弹幕数据变化 ====================
watch(() => props.items, () => {
  if (!props.visible) return
  // 当弹幕数据变化时（如本地推入新弹幕），重新渲染
  renderDanmakuAtTime(props.currentTime)
}, { deep: true })

// ==================== 弹幕渲染 ====================
function renderDanmakuAtTime(currentTime: number) {
  const timeWindow = 3
  const itemsToShow = props.items.filter(item => {
    const mode = item.mode || 'scroll'
    // 过滤被屏蔽的类型
    if (props.blockedModes.includes(mode)) return false
    return item.time >= currentTime - 0.5 &&
           item.time <= currentTime + timeWindow &&
           !renderedIds.has(item.id)
  })

  itemsToShow.sort((a, b) => a.time - b.time)

  for (const item of itemsToShow) {
    if (!renderedIds.has(item.id)) {
      createDanmakuElement(item, currentTime)
      renderedIds.add(item.id)
    }
  }

  cleanupOldDanmaku(currentTime)
}

function createDanmakuElement(item: DanmakuItem, currentTime: number) {
  if (!danmakuContainer.value) return

  const el = document.createElement('div')
  const mode = item.mode || 'scroll'

  el.className = 'danmaku-item absolute whitespace-nowrap font-medium will-change-transform'
  el.textContent = item.text
  el.style.color = item.color || '#ffffff'
  // 字体大小通过 CSS 类响应式控制
  el.style.opacity = String(props.opacity)
  el.style.textShadow = '0 1px 2px rgba(0,0,0,0.5)'
  el.style.transform = 'translateZ(0)'

  if (mode === 'scroll') {
    const trackIndex = getAvailableTrack(item.time)
    el.style.top = `${trackIndex * props.trackHeight}px`
    el.style.left = '100%'

    danmakuContainer.value.appendChild(el)
    danmakuElements.set(item.id, el)

    const containerWidth = danmakuContainer.value.clientWidth
    const textWidth = el.offsetWidth
    const distance = containerWidth + textWidth
    const speed = speedMap[props.speedLevel]
    const duration = distance / speed * 1000
    const delay = Math.max(0, (item.time - currentTime) * 1000)

    const animation = el.animate([
      { transform: `translateX(0)` },
      { transform: `translateX(-${distance}px)` }
    ], {
      duration,
      delay,
      easing: 'linear',
      fill: 'forwards'
    })

    animation.onfinish = () => {
      el.remove()
      danmakuElements.delete(item.id)
    }

    trackStates.value[trackIndex] = item.time + (duration / 1000)

  } else if (mode === 'top' || mode === 'bottom') {
    setupFixedDanmaku(el, item, currentTime, mode === 'top')
  }
}

function setupFixedDanmaku(el: HTMLElement, item: DanmakuItem, currentTime: number, isTop: boolean) {
  if (!danmakuContainer.value) return

  el.style.left = '50%'
  el.style.transform = 'translateX(-50%)'
  el.style[isTop ? 'top' : 'bottom'] = isTop ? '20px' : '60px'

  danmakuContainer.value.appendChild(el)
  danmakuElements.set(item.id, el)

  const delay = Math.max(0, (item.time - currentTime) * 1000)

  setTimeout(() => {
    el.style.transition = 'opacity 0.3s'
    el.style.opacity = '1'

    setTimeout(() => {
      el.style.opacity = '0'
      setTimeout(() => {
        el.remove()
        danmakuElements.delete(item.id)
      }, 300)
    }, 3000)
  }, delay)
}

function getAvailableTrack(currentTime: number): number {
  for (let i = 0; i < props.trackCount; i++) {
    if (trackStates.value[i] < currentTime) {
      return i
    }
  }
  return Math.floor(Math.random() * props.trackCount)
}

function cleanupOldDanmaku(currentTime: number) {
  const expireTime = currentTime - 10

  for (const [id, el] of danmakuElements) {
    const item = props.items.find(i => i.id === id)
    if (item && item.time < expireTime) {
      el.remove()
      danmakuElements.delete(id)
    }
  }
}

// ==================== 暴露方法 ====================
defineExpose({
  clear() {
    danmakuElements.forEach(el => el.remove())
    danmakuElements.clear()
    renderedIds.clear()
    trackStates.value = new Array(props.trackCount).fill(0)
  }
})
</script>

<style scoped>
.danmaku-layer {
  transition: opacity 0.3s ease;
}

.danmaku-item {
  user-select: none;
  -webkit-user-select: none;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.4;
  font-size: 16px;
}

@media (min-width: 640px) {
  .danmaku-item {
    font-size: 20px;
  }
}
</style>
