<template>
  <section>
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <div>
        <h2 class="text-xl font-bold">{{ title }}</h2>
        <p v-if="subtitle" class="text-sm text-gray-400 mt-1">{{ subtitle }}</p>
      </div>
      <NuxtLink
        v-if="moreLink"
        :to="moreLink"
        class="text-sm text-app-primary hover:underline flex items-center gap-1"
      >
        <span>查看更多</span>
        <el-icon><ArrowRight /></el-icon>
      </NuxtLink>
    </div>

    <!-- Grid -->
    <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
      <VideoCard
        v-for="movie in displayMovies"
        :key="movie.id"
        :movie="movie"
      />
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
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  limit: 12
})

const displayMovies = computed(() => {
  return props.movies.slice(0, props.limit)
})
</script>
