<template>
  <div class="min-h-screen">
    <div class="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 2xl:px-12 py-4 md:py-8">
      <!-- 页面标题 -->
      <div class="mb-8 hidden md:block">
        <h1 class="text-2xl font-bold text-gray-100 flex items-center gap-2">
          <el-icon class="text-orange-500"><Trophy /></el-icon>
          排行榜
        </h1>
        <p class="text-gray-500 mt-1">实时更新热门影片排行</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
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
      <div v-else-if="ranks.length === 0" class="text-center py-20">
        <el-icon class="text-6xl text-gray-600 mb-4"><Trophy /></el-icon>
        <p class="text-gray-500">暂无排行榜数据</p>
      </div>

      <!-- 排行榜列表 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 items-start">
        <div
          v-for="rank in ranks"
          :key="rank.id"
          class="rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-white/[0.03] backdrop-blur-sm"
        >
          <!-- 榜单头部 -->
          <div class="p-4 bg-gradient-to-r from-orange-900/30 to-transparent">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-bold text-white flex items-center gap-2">
                <el-icon class="text-orange-500"><Trophy /></el-icon>
                {{ rank.name }}
              </h2>
              <span class="text-xs text-white/70">{{ rank.movies.length }}部</span>
            </div>
            <p v-if="rank.description" class="text-xs text-white/70 mt-1 truncate">
              {{ rank.description }}
            </p>
          </div>

          <!-- 榜单影片列表 -->
          <div class="p-3 space-y-2">
            <a
              v-for="(movie, index) in getDisplayedMovies(rank.id, rank.movies)"
              :key="movie.id"
              :href="routes.stream(generateMovieSlug(movie.id, movie.title))"
              target="_blank"
              class="flex gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors group"
            >
              <!-- 排名序号 -->
              <div
                class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded text-xs font-bold"
                :class="{
                  'bg-amber-400 text-white': index === 0,
                  'bg-gray-400 text-white': index === 1,
                  'bg-orange-400 text-white': index === 2,
                  'bg-gray-700 text-white': index > 2
                }"
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
                  <span v-if="movie.score" class="text-xs text-orange-400 font-medium">{{ movie.score }}分</span>
                  <span class="text-xs text-white/70">{{ movie.category === 1 ? '电影' : movie.category === 2 ? '电视剧' : movie.category === 3 ? '综艺' : movie.category === 4 ? '动漫' : '短剧' }}</span>
                </div>
                <p class="text-xs text-white/50 mt-0.5 truncate">{{ movie.tags?.slice(0, 2).join(' ') }}</p>
              </div>
            </a>
          </div>

          <!-- 展开/收起按钮 -->
          <div v-if="rank.movies.length > 5" class="px-3 pb-3">
            <button
              @click="toggleExpand(rank.id)"
              class="w-full py-2 text-sm text-white/70 hover:text-blue-400 hover:bg-white/10 rounded-lg transition-colors flex items-center justify-center gap-1"
            >
              <span>{{ isExpanded(rank.id) ? '收起' : `展开全部 ${rank.movies.length} 部` }}</span>
              <el-icon>
                <ArrowUp v-if="isExpanded(rank.id)" />
                <ArrowDown v-else />
              </el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Trophy, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

const { getAllRanks } = useHome()
const { getBestCover } = useImageProxy()

// 展开状态管理
const expandedRankIds = ref<Set<number>>(new Set())

// 使用 useAsyncData 加载排行榜数据
const { data: ranks, pending: loading, error } = useAsyncData(
  'tiers-all',
  async () => {
    const data = await getAllRanks()
    return data || []
  },
  {
    server: true,
    lazy: false,
    default: () => []
  }
)

// 获取展示的影片（根据展开状态）
const getDisplayedMovies = (rankId: number, movies: MovieItem[]) => {
  if (expandedRankIds.value.has(rankId)) {
    return movies
  }
  return movies.slice(0, 5)
}

// 切换展开/收起
const toggleExpand = (rankId: number) => {
  if (expandedRankIds.value.has(rankId)) {
    expandedRankIds.value.delete(rankId)
  } else {
    expandedRankIds.value.add(rankId)
  }
}

// 判断是否已展开
const isExpanded = (rankId: number) => {
  return expandedRankIds.value.has(rankId)
}

// SEO
usePageSeo('排行榜', '实时更新热门电影、电视剧、综艺、动漫排行榜')

// 记录登录用户页面访问
const { recordPageVisit } = useActivity()
onMounted(() => {
  recordPageVisit('/tiers')
  if (error.value) {
    console.error('排行榜加载错误:', error.value)
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
