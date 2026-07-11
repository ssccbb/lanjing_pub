<template>
  <a
    :href="routes.stream(generateMovieSlug(movie.id, movie.title))"
    target="_blank"
    class="group/video relative block"
  >
    <!-- Cover Image -->
    <div class="relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800">
      <!-- Default placeholder background (always visible) -->
      <div class="absolute inset-0 flex items-center justify-center bg-gray-800">
        <img
          src="/ic_default_picture.png"
          alt=""
          class="w-16 h-16 object-contain opacity-30"
        />
      </div>
      <img
        :src="coverUrl"
        :alt="movie.title"
        class="absolute inset-0 w-full h-full object-cover md:transition-transform md:duration-300 md:group-hover/video:scale-105"
        loading="lazy"
        referrerpolicy="origin-when-cross-origin"
      />

      <!-- Score Badge (隐藏短剧评分) -->
      <div
        v-if="movie.score && movie.score > 0 && movie.category !== 6"
        class="absolute top-1.5 right-1.5 px-1 py-0 rounded text-[10px] font-bold bg-[#FFD700]/80 text-[#8B4513]"
      >
        {{ movie.score.toFixed(1) }}
      </div>

      <!-- Hover Overlay (Desktop only) -->
      <div class="hidden md:group-hover/video:flex absolute inset-0 bg-black/50 opacity-0 md:group-hover/video:opacity-100 transition-opacity items-center justify-center pointer-events-none">
        <div class="w-12 h-12 rounded-full bg-app-primary flex items-center justify-center">
          <el-icon :size="28"><CaretRight /></el-icon>
        </div>
      </div>

      <!-- Episode Count (for series) -->
      <div
        v-if="movie.episode_count"
        class="absolute bottom-2 left-2 px-1.5 py-0.5 bg-black/60 rounded text-xs text-white"
      >
        {{ movie.episode_count }}集
      </div>

      <!-- Cover Tag -->
      <div
        v-if="movie.cover_tag"
        class="absolute bottom-2 right-2 text-xs text-white font-medium drop-shadow-md"
      >
        {{ movie.cover_tag }}
      </div>

      <!-- Latest Episode -->
      <div
        v-if="movie.latest_episode"
        class="absolute bottom-0 left-0 right-0 px-2 py-1 bg-gradient-to-t from-black/70 to-transparent text-xs text-white truncate"
      >
        {{ movie.latest_episode }}
      </div>
    </div>

    <!-- Title -->
    <h3 class="mt-1.5 text-sm font-medium truncate text-gray-100 md:group-hover/video:text-app-primary-light transition-colors">
      {{ movie.title }}
    </h3>

    <!-- Meta -->
    <p v-if="movie.year || movie.tags" class="mt-0 text-xs text-gray-400 truncate">
      {{ metaText }}
    </p>
  </a>
</template>

<script setup lang="ts">
import { CaretRight } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

interface Props {
  movie: MovieItem
}

const props = defineProps<Props>()
const { getBestCover } = useImageProxy()

// 封面URL - 优先使用豆瓣图片（通过代理加载）
const coverUrl = computed(() => {
  return getBestCover(props.movie.covers || [], props.movie.cover)
})

// 元信息文本
const metaText = computed(() => {
  const parts = []
  // 后端返回publish_year，前端类型定义有year/publish_year
  const year = props.movie.year || props.movie.publish_year
  if (year) parts.push(year)
  if (props.movie.tags?.length) {
    // 去重，并过滤掉与年份重复的标签
    const uniqueTags = [...new Set(props.movie.tags)]
    const filteredTags = year
      ? uniqueTags.filter(tag => tag !== year && tag !== year.toString())
      : uniqueTags
    parts.push(filteredTags.slice(0, 3).join(' '))
  }
  return parts.join(' · ')
})

</script>
