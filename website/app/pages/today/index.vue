<template>
  <div class="px-4 md:px-6 lg:px-10 py-6 pb-16">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold flex items-center gap-2">
        <el-icon class="text-blue-400"><Calendar /></el-icon>
        今日更新
      </h1>
      <p class="text-gray-500 mt-2">共 {{ total }} 部影片更新</p>
    </div>

    <!-- 分类筛选 -->
    <div class="mb-6">
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-sm text-white/70 mr-2">分类筛选：</span>
        <button
          @click="selectCategory(null)"
          class="px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
          :class="selectedCategory === null
            ? 'bg-app-primary text-white'
            : 'text-white/70 hover:text-white'"
        >
          全部
        </button>
        <button
          v-for="cat in categoryOptions"
          :key="cat.value"
          @click="selectCategory(cat.value)"
          class="px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
          :class="selectedCategory === cat.value
            ? 'bg-app-primary text-white'
            : 'text-white/70 hover:text-white'"
        >
          {{ cat.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-8">
      <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
        <div v-for="i in 12" :key="i" class="space-y-2">
          <div class="aspect-[2/3] bg-white/[0.03] rounded-lg animate-pulse" />
          <div class="h-4 bg-white/[0.03] rounded w-3/4 animate-pulse" />
        </div>
      </div>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- 影片网格 -->
      <div v-if="movies.length > 0" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
        <VideoCard
          v-for="movie in movies"
          :key="movie.id"
          :movie="movie"
        />
      </div>

      <!-- 空状态 -->
      <div v-else class="flex flex-col items-center justify-center py-20">
        <el-icon :size="64" class="text-gray-500 mb-4"><Calendar /></el-icon>
        <p class="text-gray-500">今日暂无更新</p>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="flex justify-center pt-8">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @change="loadData"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Calendar } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

const { getTodayMovies } = useHome()

// SEO
usePageSeo('今日更新', '查看今日最新更新的电影、电视剧、综艺、动漫等影视资源')

// 分类选项
const categoryOptions = [
  { value: 1, label: '电影' },
  { value: 2, label: '电视剧' },
  { value: 3, label: '综艺' },
  { value: 4, label: '动漫' },
  { value: 6, label: '短剧' }
]

// State
const page = ref(1)
const pageSize = 30
const selectedCategory = ref<number | null>(null) // 默认选中全部

// SSR 预取数据
const { data: listData, pending: loading, refresh } = await useAsyncData(
  'today-movies',
  () => getTodayMovies(
    page.value,
    pageSize,
    selectedCategory.value !== null ? [selectedCategory.value] : undefined
  ),
  {
    server: true,
    lazy: false,
    default: () => ({ list: [], total: 0, page: 1, pageSize: 30 }),
    watch: [page, selectedCategory]
  }
)

const movies = computed(() => listData.value?.list ?? [])
const total = computed(() => listData.value?.total ?? 0)

// 选择分类（单选）
const selectCategory = (categoryId: number | null) => {
  selectedCategory.value = categoryId
  // 重置页码
  page.value = 1
  refresh()
}
</script>
