<template>
  <div class="relative h-[50vh] md:h-[60vh] lg:h-[70vh]">
    <!-- 背景：使用低质量图片并模糊处理 -->
    <div class="absolute inset-0">
      <TransitionGroup name="fade">
        <div
          v-for="(banner, index) in banners"
          v-show="currentIndex === index"
          :key="banner.id"
          class="absolute inset-0"
        >
          <!-- 低质量背景图 + 高斯模糊遮丑 -->
          <div
            class="absolute inset-0 bg-cover bg-center blur-xl scale-110"
            :style="{ backgroundImage: `url(${getBlurUrl(banner)})` }"
          />
          <!-- 浅色遮罩 -->
          <div class="absolute inset-0 bg-gradient-to-b from-white/70 via-white/50 to-white/70" />
        </div>
      </TransitionGroup>
    </div>

    <!-- 内容：居中展示清晰封面 -->
    <div class="relative h-full flex flex-col items-center justify-center px-4">
      <TransitionGroup name="scale">
        <div
          v-show="currentIndex === activeIndex"
          :key="activeIndex"
          class="flex flex-col items-center text-center"
        >
          <!-- 清晰封面 -->
          <div class="w-40 md:w-48 lg:w-56 rounded-lg overflow-hidden shadow-2xl mb-6">
            <NuxtImg
              :src="getPosterUrl(activeBanner)"
              :alt="activeBanner.title"
              class="w-full aspect-[2/3] object-cover"
              format="webp"
              quality="95"
            />
          </div>

          <!-- 标题 -->
          <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold mb-2">
            {{ activeBanner.title }}
          </h2>

          <!-- 元信息 -->
          <p v-if="activeBanner.tags?.length" class="text-sm text-gray-500 mb-4">
            {{ activeBanner.tags.slice(0, 3).join(' · ') }}
          </p>

          <!-- 按钮 -->
          <div class="flex gap-3">
            <a
              :href="routes.stream(generateMovieSlug(activeBanner.id, activeBanner.title))"
              target="_blank"
              class="flex items-center gap-2 px-6 py-3 bg-app-primary text-white rounded-lg font-medium hover:bg-app-primary-hover transition-colors"
            >
              <el-icon><VideoPlay /></el-icon>
              <span>立即播放</span>
            </a>
          </div>
        </div>
      </TransitionGroup>

      <!-- 指示器 -->
      <div v-if="banners.length > 1" class="absolute bottom-8 flex gap-2">
        <button
          v-for="(_, index) in banners"
          :key="index"
          class="w-2 h-2 rounded-full transition-all"
          :class="currentIndex === index ? 'bg-app-primary w-6' : 'bg-gray-300'"
          @click="goTo(index)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { VideoPlay, InfoFilled } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

interface Props {
  banners: MovieItem[]
}

const props = defineProps<Props>()
const { getBestCover } = useImageProxy()

const currentIndex = ref(0)
const activeIndex = computed(() => currentIndex.value)
const activeBanner = computed(() => props.banners[currentIndex.value] || {})

// 获取竖版封面（通过代理）
const getPosterUrl = (banner: MovieItem) => {
  return getBestCover(banner.covers || [], banner.cover)
}

// 获取用于模糊背景的图片（通过代理）
const getBlurUrl = (banner: MovieItem) => {
  return getBestCover(banner.covers || [], banner.cover)
}

let autoplayTimer: ReturnType<typeof setInterval> | null = null

const goTo = (index: number) => {
  currentIndex.value = index
  resetAutoplay()
}

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
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.8s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.4s ease;
}

.scale-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.scale-leave-to {
  opacity: 0;
  transform: scale(1.05);
}
</style>
