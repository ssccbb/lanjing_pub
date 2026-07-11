<template>
  <div class="px-4 md:px-6 lg:px-12 py-8">
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <a
        v-for="(banner, index) in displayBanners"
        :key="banner.id"
        :href="routes.stream(generateMovieSlug(banner.id, banner.title))"
        target="_blank"
        class="group relative aspect-[2/3] rounded-lg overflow-hidden"
        :class="index === 0 ? 'col-span-2 row-span-2 md:col-span-2 md:row-span-2' : ''"
      >
        <NuxtImg
          :src="getPosterUrl(banner)"
          :alt="banner.title"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          format="webp"
          quality="95"
        />
        <!-- 渐变遮罩 -->
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
        <!-- 播放按钮 (桌面端hover显示，不拦截移动端点击) -->
        <div class="hidden md:flex absolute inset-0 items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <div class="w-12 h-12 rounded-full bg-app-primary flex items-center justify-center">
            <el-icon :size="24"><VideoPlay /></el-icon>
          </div>
        </div>
        <!-- 标题 -->
        <div class="absolute bottom-0 left-0 right-0 p-3">
          <h3 class="font-medium truncate" :class="index === 0 ? 'text-lg' : 'text-sm'">
            {{ banner.title }}
          </h3>
          <p v-if="banner.score && banner.category !== 6" class="text-[#B8860B] text-sm font-bold">
            {{ banner.score.toFixed(1) }}
          </p>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { VideoPlay } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

interface Props {
  banners: MovieItem[]
}

const props = defineProps<Props>()
const { getBestCover } = useImageProxy()

const displayBanners = computed(() => props.banners.slice(0, 5))

const getPosterUrl = (banner: MovieItem) => {
  return getBestCover(banner.covers || [], banner.cover)
}
</script>
