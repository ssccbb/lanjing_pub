<template>
  <div class="min-h-screen">
    <div class="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 2xl:px-12 py-4 md:py-8">
      <!-- 页面标题 -->
      <div class="mb-8 hidden md:block">
        <h1 class="text-2xl font-bold text-gray-100 flex items-center gap-2">
          <el-icon class="text-blue-400"><Collection /></el-icon>
          片单广场
        </h1>
        <p class="text-gray-500 mt-1">精选影视片单，发现好内容</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && watchlists.length === 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
        <div v-for="i in 3" :key="i" class="bg-white/[0.03] rounded-lg shadow-sm p-4">
          <div class="h-6 bg-white/[0.03] rounded w-24 animate-pulse mb-4" />
          <div v-for="j in 5" :key="j" class="flex gap-3 mb-3">
            <div class="w-5 h-5 bg-white/[0.03] rounded animate-pulse flex-shrink-0" />
            <div class="w-12 h-16 bg-white/[0.03] rounded animate-pulse flex-shrink-0" />
            <div class="flex-1 space-y-2 py-1">
              <div class="h-4 bg-white/[0.03] rounded w-3/4 animate-pulse" />
              <div class="h-3 bg-white/[0.03] rounded w-1/2 animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="watchlists.length === 0" class="text-center py-20">
        <el-icon class="text-6xl text-gray-300 mb-4"><Collection /></el-icon>
        <p class="text-gray-500">暂无片单数据</p>
      </div>

      <!-- 片单列表 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 items-start">
        <div
          v-for="watchlist in watchlists"
          :key="watchlist.id"
          class="rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-white/[0.03] backdrop-blur-sm"
        >
          <!-- 片单头部 -->
          <div class="p-4 bg-gradient-to-r from-blue-900/30 to-transparent">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-bold text-white flex items-center gap-2">
                <el-icon class="text-blue-400"><Collection /></el-icon>
                {{ watchlist.name }}
              </h2>
              <span class="text-xs text-white/70">{{ watchlist.movies.length }}部</span>
            </div>
            <p v-if="watchlist.description" class="text-xs text-white/70 mt-1 truncate">
              {{ watchlist.description }}
            </p>
          </div>

          <!-- 片单影片列表 -->
          <div class="p-3 space-y-2">
            <a
              v-for="(movie, index) in getDisplayedMovies(watchlist.id, watchlist.movies)"
              :key="movie.id"
              :href="routes.stream(generateMovieSlug(movie.id, movie.title))"
              target="_blank"
              class="flex gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors group"
            >
              <!-- 序号 -->
              <div
                class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded text-xs font-bold bg-gray-700 text-white"
              >
                {{ index + 1 }}
              </div>

              <!-- 影片封面 -->
              <div class="relative w-12 h-16 flex-shrink-0 bg-gray-800 rounded">
                <img
                  :src="getBestCover(movie.covers, movie.cover) || '/placeholder.jpg'"
                  :alt="movie.title"
                  class="w-full h-full object-cover rounded"
                  loading="lazy"
                />
              </div>

              <!-- 影片信息 -->
              <div class="flex-1 min-w-0 py-0.5">
                <h3 class="text-sm font-medium text-white truncate group-hover:text-blue-400 transition-colors">
                  {{ movie.title }}
                </h3>
                <div class="flex items-center gap-2 mt-1">
                  <span v-if="movie.score" class="text-xs text-orange-500 font-medium">{{ movie.score }}分</span>
                  <span class="text-xs text-white/70">{{ movie.category === 1 ? '电影' : movie.category === 2 ? '电视剧' : movie.category === 3 ? '综艺' : movie.category === 4 ? '动漫' : '短剧' }}</span>
                </div>
                <p class="text-xs text-white/50 mt-0.5 truncate">{{ movie.tags?.slice(0, 2).join(' ') }}</p>
              </div>
            </a>
          </div>

          <!-- 展开/收起按钮 -->
          <div v-if="watchlist.movies.length > 5" class="px-3 pb-3">
            <button
              @click="toggleExpand(watchlist.id)"
              class="w-full py-2 text-sm text-white/70 hover:text-blue-400 hover:bg-white/10 rounded-lg transition-colors flex items-center justify-center gap-1"
            >
              <span>{{ isExpanded(watchlist.id) ? '收起' : `展开全部 ${watchlist.movies.length} 部` }}</span>
              <el-icon>
                <ArrowUp v-if="isExpanded(watchlist.id)" />
                <ArrowDown v-else />
              </el-icon>
            </button>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="watchlists.length > 0 && hasMore" class="mt-8 text-center">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="px-8 py-3 bg-app-bg-secondary rounded-lg text-white/70 hover:text-blue-400 hover:bg-app-bg-tertiary transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loadingMore" class="flex items-center gap-2">
            <el-icon class="animate-spin"><Loading /></el-icon>
            加载中...
          </span>
          <span v-else>加载更多</span>
        </button>
      </div>

      <!-- 没有更多数据提示 -->
      <div v-if="watchlists.length > 0 && !hasMore" class="mt-8 text-center text-gray-500 text-sm">
        已经到底啦~
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Collection, ArrowUp, ArrowDown, Loading } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

const { getWatchlists } = useHome()
const { getBestCover } = useImageProxy()

// 页面状态
const loadingMore = ref(false)
const currentPage = ref(1)
const pageSize = 6
const expandedWatchlistIds = ref<Set<number>>(new Set())

// 使用 useAsyncData 加载片单数据
const { data: watchlistData, pending: loading, error } = useAsyncData(
  'watchlists-page-1',
  async () => {
    // console.log('开始加载片单数据...')
    const data = await getWatchlists(1, pageSize)
    // console.log('片单数据加载成功:', data)
    return data
  },
  {
    server: true,
    lazy: false,
    default: () => ({ list: [], total: 0, page: 1, page_size: pageSize, total_pages: 0 })
  }
)

// 计算属性
const watchlists = computed(() => watchlistData.value?.list || [])
const totalPages = computed(() => watchlistData.value?.total_pages || 0)
const hasMore = computed(() => currentPage.value < totalPages.value)

// 获取展示的影片（根据展开状态）
const getDisplayedMovies = (watchlistId: number, movies: MovieItem[]) => {
  if (expandedWatchlistIds.value.has(watchlistId)) {
    return movies
  }
  return movies.slice(0, 5)
}

// 切换展开/收起
const toggleExpand = (watchlistId: number) => {
  if (expandedWatchlistIds.value.has(watchlistId)) {
    expandedWatchlistIds.value.delete(watchlistId)
  } else {
    expandedWatchlistIds.value.add(watchlistId)
  }
}

// 判断是否已展开
const isExpanded = (watchlistId: number) => {
  return expandedWatchlistIds.value.has(watchlistId)
}

// 加载更多（客户端追加数据）
const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return

  loadingMore.value = true
  currentPage.value++

  try {
    const data = await getWatchlists(currentPage.value, pageSize)
    if (data.list && data.list.length > 0) {
      watchlistData.value.list.push(...data.list)
    }
  } catch (err) {
    console.error('加载更多失败:', err)
  } finally {
    loadingMore.value = false
  }
}

// SEO
usePageSeo('片单广场', '精选各类影视片单，发现更多精彩内容')

const { recordPageVisit } = useActivity()
onMounted(() => {
  recordPageVisit('/watchlists')
  if (error.value) {
    console.error('片单加载错误:', error.value)
  }
})
</script>

<style scoped>
/* 隐藏滚动条 */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
