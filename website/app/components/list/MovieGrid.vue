<template>
  <div>
    <!-- Grid -->
    <div
      v-if="movies.length > 0"
      class="grid gap-1 sm:gap-4"
      :class="{
        'grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7': size === 'normal',
        'grid-cols-4 sm:grid-cols-5 md:grid-cols-6': size === 'small'
      }"
    >
      <VideoCard
        v-for="movie in movies"
        :key="movie.id"
        :movie="movie"
      />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && !error" class="py-16 text-center">
      <el-icon :size="48" class="text-gray-400 mb-4"><Film /></el-icon>
      <p class="text-gray-500">暂无相关内容</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="py-16 text-center">
      <el-icon :size="48" class="text-red-400 mb-4"><Warning /></el-icon>
      <p class="text-gray-500 mb-4">加载失败，请稍后重试</p>
      <button
        class="px-4 py-2 bg-app-primary text-white rounded-lg text-sm hover:bg-app-primary-hover transition-colors"
        @click="$emit('retry')"
      >
        重新加载
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="py-8 text-center">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
    </div>

    <!-- Pagination -->
    <div v-if="showPagination && total > pageSize" class="flex justify-center mt-8">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @change="handlePageChange"
      />
    </div>

    <!-- Infinite Scroll Trigger -->
    <div v-if="infinite && hasMore" ref="loadMoreRef" class="py-4 text-center">
      <el-icon v-if="loadingMore" class="is-loading" :size="24"><Loading /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Film, Loading, Warning } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

interface Props {
  movies: MovieItem[]
  loading?: boolean
  loadingMore?: boolean
  error?: boolean
  total: number
  page?: number
  pageSize?: number
  size?: 'normal' | 'small'
  showPagination?: boolean
  infinite?: boolean
  hasMore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  loadingMore: false,
  error: false,
  page: 1,
  pageSize: 24,
  size: 'normal',
  showPagination: true,
  infinite: false,
  hasMore: false
})

const emit = defineEmits<{
  'update:page': [page: number]
  'load-more': []
  'retry': []
}>()

const currentPage = computed({
  get: () => props.page,
  set: (val) => emit('update:page', val)
})

const handlePageChange = (page: number) => {
  emit('update:page', page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Infinite scroll
const loadMoreRef = ref<HTMLElement>()

onMounted(() => {
  if (props.infinite && loadMoreRef.value) {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && props.hasMore && !props.loadingMore) {
        emit('load-more')
      }
    }, { rootMargin: '100px' })

    observer.observe(loadMoreRef.value)

    onUnmounted(() => observer.disconnect())
  }
})
</script>
