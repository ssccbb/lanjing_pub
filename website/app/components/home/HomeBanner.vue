<template>
  <div
    ref="bannerRef"
    class="relative overflow-hidden"
    :style="{ height: `${bannerHeight}px` }"
  >
    <!-- 背景层 -->
    <div class="absolute inset-0">
      <div
        v-for="(banner, index) in banners"
        :key="'bg-' + banner.id"
        class="absolute inset-0 transition-opacity duration-700 ease-in-out"
        :class="currentIndex === index ? 'opacity-100' : 'opacity-0'"
      >
        <div
          class="absolute inset-0 bg-cover bg-center"
          :style="{ backgroundImage: `url(${banner.extra?.horizontal_cover || ''})` }"
        />
        <!-- 底部渐变遮罩 -->
        <div class="absolute bottom-0 left-0 right-0 h-[50%] bg-gradient-to-t from-app-bg via-app-bg/70 to-transparent" />
      </div>
      <!-- 点击跳转层 -->
      <div
        class="absolute inset-0 cursor-pointer group"
        @click="goToDetail"
      >
        <!-- 鼠标聚焦遮罩 -->
        <div class="absolute inset-0 bg-transparent group-hover:bg-black/20 transition-colors duration-300" />
      </div>
    </div>

    <!-- 底部描述文字 + 缩略图列表 -->
    <div
      class="absolute bottom-4 right-4"
      :class="extendToSidebar ? 'left-6 md:left-52 lg:left-56' : 'left-6'"
    >
      <!-- oneshot_desc 描述文字 -->
      <div class="relative h-10 mb-4">
        <div
          v-for="(banner, index) in banners"
          :key="'desc-' + banner.id"
          class="absolute inset-0 transition-all duration-500 ease-in-out"
          :class="currentIndex === index ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'"
        >
          <p
            v-if="banner.oneshot_desc"
            class="text-white font-bold text-lg md:text-xl lg:text-2xl line-clamp-1 drop-shadow-lg tracking-wide"
          >
            {{ banner.oneshot_desc }}
          </p>
        </div>
      </div>

      <!-- 缩略图列表 -->
      <div ref="thumbListRef" class="flex items-end justify-start gap-4 overflow-x-auto pb-1 scrollbar-hide">
        <div
          v-for="(banner, index) in banners"
          :key="'thumb-' + banner.id"
          :ref="el => { if (el) thumbItemsRef[index] = el }"
          class="flex-shrink-0 cursor-pointer transition-all duration-300"
          :class="[
            currentIndex === index ? 'opacity-100 scale-105' : 'opacity-40 hover:opacity-70',
            containerWidth < 640 ? 'w-12' : '',
            containerWidth >= 640 && containerWidth < 1024 ? 'w-16' : '',
            containerWidth >= 1024 ? 'w-20' : ''
          ]"
          @click="goTo(index)"
        >
          <!-- 封面 -->
          <div class="rounded overflow-hidden shadow-md">
            <NuxtImg
              :src="getPosterUrl(banner)"
              :alt="banner.title"
              class="w-full aspect-[2/3] object-cover"
              format="webp"
              quality="90"
            />
          </div>
          <!-- 标题 -->
          <p
            class="mt-1 text-center text-white text-sm sm:text-xs md:text-sm line-clamp-1 drop-shadow-md"
            :class="currentIndex === index ? 'font-medium' : ''"
          >
            {{ banner.title }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MovieItem } from '~/types'
import { generateMovieSlug, routes } from '~/composables/useSlug'

interface Props {
  banners: MovieItem[]
  extendToSidebar?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  extendToSidebar: false
})

const router = useRouter()

const currentIndex = ref(0)

// 容器宽度响应式
const bannerRef = ref<HTMLElement>()
const containerWidth = ref(1024)

// 缩略图列表和 item refs
const thumbListRef = ref<HTMLElement>()
const thumbItemsRef = ref<HTMLElement[]>([])

// Banner高度
const bannerHeight = computed(() => {
  if (containerWidth.value < 640) return 350
  if (containerWidth.value < 1024) return 460
  if (containerWidth.value < 1280) return 600
  return 760
})

const updateWidth = () => {
  if (bannerRef.value) {
    containerWidth.value = bannerRef.value.clientWidth
  }
}

onMounted(() => {
  updateWidth()
  const resizeObserver = new ResizeObserver(() => {
    updateWidth()
  })
  if (bannerRef.value) {
    resizeObserver.observe(bannerRef.value)
  }
  onUnmounted(() => {
    resizeObserver.disconnect()
  })
})

const { getBestCover } = useImageProxy()

// 获取竖版封面
const getPosterUrl = (banner: MovieItem) => {
  return getBestCover(banner.covers || [], banner.cover || '')
}

let autoplayTimer: ReturnType<typeof setInterval> | null = null

const goTo = (index: number) => {
  currentIndex.value = index
  resetAutoplay()
  scrollToVisibleThumbnail(index)
}

// 跳转到影片播放页
const goToDetail = () => {
  const banner = props.banners[currentIndex.value]
  if (!banner?.id || !banner?.title) return
  const slug = generateMovieSlug(banner.id, banner.title)
  window.open(routes.stream(slug), '_blank')
}

// 自动滚动缩略图到可视区域
const scrollToVisibleThumbnail = (index: number) => {
  if (!thumbListRef.value || !thumbItemsRef.value[index]) return

  const listEl = thumbListRef.value
  const itemEl = thumbItemsRef.value[index]

  // 获取元素相对于容器的滚动位置
  const listRect = listEl.getBoundingClientRect()
  const itemRect = itemEl.getBoundingClientRect()

  // 计算 item 相对于 list 的偏移量
  const itemOffsetLeft = itemEl.offsetLeft
  const itemWidth = itemRect.width
  const listWidth = listRect.width

  // 检查 item 是否在可视区域内
  const isVisible = itemRect.left >= listRect.left && itemRect.right <= listRect.right

  if (!isVisible) {
    // 计算目标滚动位置：让 item 居中显示
    const scrollLeft = itemOffsetLeft - (listWidth / 2) + (itemWidth / 2)
    listEl.scrollTo({
      left: Math.max(0, scrollLeft),
      behavior: 'smooth'
    })
  }
}

// 监听 currentIndex 变化，自动滚动到可视区域
watch(currentIndex, (newIndex) => {
  scrollToVisibleThumbnail(newIndex)
})

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % props.banners.length
}

const resetAutoplay = () => {
  if (autoplayTimer) clearInterval(autoplayTimer)
  autoplayTimer = setInterval(next, 5000)
}

onMounted(() => {
  if (props.banners.length > 1) {
    resetAutoplay()
  }
})

onUnmounted(() => {
  if (autoplayTimer) clearInterval(autoplayTimer)
  // 清理 refs
  thumbItemsRef.value = []
})
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
