<template>
  <section>
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-xl font-bold">{{ title }}</h2>
        <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
      </div>
      <NuxtLink
        v-if="moreLink"
        :to="moreLink"
        class="text-sm text-app-primary hover:underline flex items-center gap-1"
      >
        <span>查看完整榜单</span>
        <el-icon><ArrowRight /></el-icon>
      </NuxtLink>
    </div>

    <!-- Top 3 -->
    <div class="grid grid-cols-3 gap-4 mb-6">
      <div
        v-for="(movie, index) in topThree"
        :key="movie.id"
        class="relative"
      >
        <VideoCard :movie="movie" />
        <!-- Rank Badge -->
        <div
          class="absolute -top-2 -left-2 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm"
          :class="rankClass(index)"
        >
          {{ index + 1 }}
        </div>
      </div>
    </div>

    <!-- Rest List -->
    <div class="space-y-2">
      <a
        v-for="(movie, index) in restList"
        :key="movie.id"
        :href="routes.stream(generateMovieSlug(movie.id, movie.title))"
        target="_blank"
        class="flex items-center gap-4 p-3 rounded-lg hover:bg-black transition-colors group"
      >
        <!-- Rank Number -->
        <span
          class="w-6 text-center font-bold"
          :class="index < 3 ? 'text-app-primary' : 'text-gray-500'"
        >
          {{ index + 4 }}
        </span>

        <!-- Cover -->
        <div class="w-16 h-24 flex-shrink-0 rounded overflow-hidden bg-app-bg-tertiary">
          <NuxtImg
            :src="getCoverUrl(movie)"
            :alt="movie.title"
            class="w-full h-full object-cover"
            format="webp"
            quality="85"
          />
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <h3 class="font-medium truncate group-hover:text-app-primary transition-colors">
            {{ movie.title }}
          </h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ (movie.year || movie.publish_year) }} · {{ movie.tags?.slice(0, 2).join(' ') }}
          </p>
        </div>

        <!-- Score (短剧不展示) -->
        <div
          v-if="movie.score && movie.category !== 6"
          class="text-lg font-bold text-[#B8860B]"
        >
          {{ movie.score.toFixed(1) }}
        </div>
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

interface Props {
  title: string
  subtitle?: string
  movies: MovieItem[]
  moreLink?: string
}

const props = defineProps<Props>()
const { getBestCover } = useImageProxy()

const topThree = computed(() => props.movies.slice(0, 3))
const restList = computed(() => props.movies.slice(3, 10))

// 获取封面URL - 使用代理
const getCoverUrl = (movie: MovieItem) => {
  return getBestCover(movie.covers || [], movie.cover)
}

const rankClass = (index: number) => {
  const classes = [
    'bg-app-primary text-white',     // 1st
    'bg-[#f5c518] text-black',     // 2nd
    'bg-black text-white'       // 3rd
  ]
  return classes[index]
}
</script>
