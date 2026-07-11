<template>
  <div class="pb-16">
    <!-- Loading State -->
    <div v-if="loading" class="min-h-screen overflow-x-hidden px-4 md:px-3 lg:px-5">
      <!-- Banner Skeleton -->
      <div class="h-[38vh] max-h-[340px] bg-white/[0.03] rounded-lg animate-pulse mb-8" />
      <!-- Content Skeletons -->
      <div class="space-y-8">
        <div v-for="i in 3" :key="i" class="space-y-4">
          <div class="flex items-center justify-between">
            <div class="h-6 bg-white/[0.03] rounded w-32 animate-pulse" />
            <div class="h-4 bg-white/[0.03] rounded w-20 animate-pulse" />
          </div>
          <div class="flex gap-4 overflow-hidden">
            <div
              v-for="j in 6"
              :key="j"
              class="flex-shrink-0 w-[140px] md:w-[160px] lg:w-[180px]"
            >
              <div class="aspect-[2/3] bg-white/[0.03] rounded-lg animate-pulse" />
              <div class="mt-2 h-4 bg-white/[0.03] rounded w-3/4 animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loaded Content -->
    <template v-else>
      <!-- Banner - 全宽显示，延伸到导航栏下方 -->
      <HomeBanner :banners="banners" extend-to-sidebar class="mb-8 -mt-14 md:-ml-44 lg:-ml-48" />

      <div class="px-4 md:px-3 lg:px-5">
        <div class="flex gap-6">
          <!-- 左侧主内容区 -->
          <div class="flex-1 space-y-10 min-w-0">

        <template v-if="activeCategory === 'home'">
          <template v-for="(block, index) in homeBlocks" :key="block.item_key">
            <HomeCarousel
              v-if="block.item_type === 'carousel'"
              :title="block.data_json.title"
              :subtitle="block.data_json.subtitle"
              :movies="block.data_json.items"
              :more-link="block.data_json.more_link"
              :limit="block.data_json.title === '新片速递' ? 6 : 12"
            />
            <HomeGrid
              v-else-if="block.item_type === 'grid'"
              :title="block.data_json.title"
              :subtitle="block.data_json.subtitle"
              :movies="block.data_json.items"
              :more-link="block.data_json.more_link"
            />
            <HomeRank
              v-else-if="block.item_type === 'rank'"
              :title="block.data_json.title"
              :subtitle="block.data_json.subtitle"
              :movies="block.data_json.items"
            />
          </template>
        </template>

        <!-- Category Specific Content -->
        <template v-else-if="activeCategory !== 'today'">
          <!-- 骨架屏 -->
          <div v-if="categoryLoading" class="space-y-10">
            <div v-for="section in 3" :key="section" class="space-y-4">
              <div class="h-6 bg-white/[0.03] rounded w-32 animate-pulse" />
              <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                <div v-for="i in 6" :key="i" class="space-y-2">
                  <div class="aspect-[2/3] bg-white/[0.03] rounded-lg animate-pulse" />
                  <div class="h-4 bg-white/[0.03] rounded w-3/4 animate-pulse" />
                </div>
              </div>
            </div>
          </div>

          <!-- 分类内容展示 -->
          <div v-else class="space-y-10">
            <!-- 最新更新 -->
            <section v-if="categoryMovies.newest.length > 0">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold">最新更新</h2>
                <NuxtLink
                  :to="currentCategory.link"
                  class="text-sm text-app-primary hover:underline flex items-center gap-1"
                >
                  <span>查看更多</span>
                  <el-icon><ArrowRight /></el-icon>
                </NuxtLink>
              </div>
              <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                <VideoCard
                  v-for="movie in categoryMovies.newest.slice(0, 12)"
                  :key="movie.id"
                  :movie="movie"
                />
              </div>
            </section>

            <!-- 推荐影片 -->
            <section v-if="categoryMovies.recommend.length > 0">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold">推荐影片</h2>
                <NuxtLink
                  :to="currentCategory.link"
                  class="text-sm text-app-primary hover:underline flex items-center gap-1"
                >
                  <span>查看更多</span>
                  <el-icon><ArrowRight /></el-icon>
                </NuxtLink>
              </div>
              <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                <VideoCard
                  v-for="movie in categoryMovies.recommend.slice(0, 12)"
                  :key="movie.id"
                  :movie="movie"
                />
              </div>
            </section>

            <!-- 高分影片 -->
            <section v-if="categoryMovies.topRated.length > 0">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold">高分影片</h2>
                <NuxtLink
                  :to="currentCategory.link"
                  class="text-sm text-app-primary hover:underline flex items-center gap-1"
                >
                  <span>查看更多</span>
                  <el-icon><ArrowRight /></el-icon>
                </NuxtLink>
              </div>
              <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                <VideoCard
                  v-for="movie in categoryMovies.topRated.slice(0, 12)"
                  :key="movie.id"
                  :movie="movie"
                />
              </div>
            </section>
          </div>
        </template>
          </div>

          <!-- 右侧侧边栏 -->
          <div v-if="activeCategory === 'home'" class="hidden xl:block w-80 flex-shrink-0">
            <!-- 热搜榜/热播榜 -->
            <div class="rounded-lg bg-white/[0.03] backdrop-blur-sm">
              <div class="p-4">
                <div class="flex items-center justify-between">
                  <!-- Tab 切换 -->
                  <div class="flex items-center gap-6">
                    <button
                      @click="activeRankTab = 'hot'"
                      class="relative text-sm font-medium transition-colors pb-1"
                      :class="activeRankTab === 'hot' ? 'text-white' : 'text-white/70 hover:text-white'"
                    >
                      热播榜
                      <span
                        v-if="activeRankTab === 'hot'"
                        class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-full"
                      />
                    </button>
                    <button
                      @click="activeRankTab = 'search'"
                      class="relative text-sm font-medium transition-colors pb-1"
                      :class="activeRankTab === 'search' ? 'text-white' : 'text-white/70 hover:text-white'"
                    >
                      热搜榜
                      <span
                        v-if="activeRankTab === 'search'"
                        class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-full"
                      />
                    </button>
                  </div>
                </div>
              </div>
              <div class="p-2">
                <div v-if="rankLoading" class="space-y-2 p-2">
                  <div v-for="i in 5" :key="i" class="flex gap-3">
                    <div class="w-5 h-5 bg-white/[0.03] rounded animate-pulse flex-shrink-0" />
                    <div class="w-14 h-20 bg-white/[0.03] rounded animate-pulse flex-shrink-0" />
                    <div class="flex-1 space-y-2 py-1">
                      <div class="h-4 bg-white/[0.03] rounded w-3/4 animate-pulse" />
                      <div class="h-3 bg-white/[0.03] rounded w-1/2 animate-pulse" />
                    </div>
                  </div>
                </div>
                <div v-else-if="currentRankMovies.length === 0" class="text-center py-8 text-white/70 text-sm">
                  暂无数据
                </div>
                <div v-else class="space-y-1">
                  <a
                    v-for="(movie, index) in currentRankMovies"
                    :key="movie.id"
                    :href="routes.stream(generateMovieSlug(movie.id, movie.title))"
                    target="_blank"
                    class="flex gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors group"
                  >
                    <!-- 排名序号 -->
                    <div class="flex-shrink-0 w-5 h-5 flex items-center justify-center rounded text-xs font-bold"
                      :class="{
                        'bg-amber-400 text-white': index === 0,
                        'bg-gray-400 text-white': index === 1,
                        'bg-orange-400 text-white': index === 2,
                        'bg-gray-700 text-white': index > 2
                      }"
                    >
                      {{ index + 1 }}
                    </div>
                    <div class="relative w-14 h-[72px] flex-shrink-0">
                      <img
                        :src="getBestCover(movie.covers, movie.cover) || '/placeholder.jpg'"
                        :alt="movie.title"
                        class="w-full h-full object-cover rounded-md"
                      />
                    </div>
                    <div class="flex-1 min-w-0 py-0.5">
                      <h4 class="text-sm font-medium text-white truncate group-hover:text-blue-400 transition-colors">
                        {{ movie.title }}
                      </h4>
                      <p class="text-xs text-white/70 mt-1">{{ movie.tags?.slice(0, 2).join(' ') }}</p>
                      <p class="text-xs text-white/50 mt-0.5">{{ movie.score ? movie.score + '分' : '' }}</p>
                    </div>
                  </a>
                </div>
              </div>
              <div class="p-3 text-center">
                <NuxtLink :to="routes.tiers()" class="text-sm text-blue-400 hover:text-blue-500">
                  查看更多
                </NuxtLink>
              </div>
            </div>

            <!-- 今日更新 -->
            <div class="mt-4 rounded-lg bg-white/[0.03] backdrop-blur-sm">
              <div class="p-4">
                <div class="flex items-center justify-between">
                  <h3 class="font-bold text-white flex items-center gap-2">
                    <el-icon class="text-blue-400"><Calendar /></el-icon>
                    今日更新
                  </h3>
                  <span class="text-xs text-white/70">{{ todaySidebarTotal }} 部</span>
                </div>
              </div>
              <div class="p-2">
                <div v-if="todaySidebarLoading" class="space-y-2 p-2">
                  <div v-for="i in 10" :key="i" class="flex gap-3">
                    <div class="w-14 h-20 bg-white/[0.03] rounded animate-pulse flex-shrink-0" />
                    <div class="flex-1 space-y-2 py-1">
                      <div class="h-4 bg-white/[0.03] rounded w-3/4 animate-pulse" />
                      <div class="h-3 bg-white/[0.03] rounded w-1/2 animate-pulse" />
                    </div>
                  </div>
                </div>
                <div v-else-if="todaySidebarMovies.length === 0" class="text-center py-8 text-white/70 text-sm">
                  今日暂无更新
                </div>
                <div v-else class="space-y-1">
                  <a
                    v-for="(movie, index) in todaySidebarMovies"
                    :key="movie.id"
                    :href="routes.stream(generateMovieSlug(movie.id, movie.title))"
                    target="_blank"
                    class="flex gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors group"
                  >
                    <div class="relative w-14 h-[72px] flex-shrink-0">
                      <img
                        :src="getBestCover(movie.covers, movie.cover) || '/placeholder.jpg'"
                        :alt="movie.title"
                        class="w-full h-full object-cover rounded-md"
                      />
                    </div>
                    <div class="flex-1 min-w-0 py-0.5">
                      <h4 class="text-sm font-medium text-white truncate group-hover:text-blue-400 transition-colors">
                        {{ movie.title }}
                      </h4>
                      <p class="text-xs text-white/70 mt-1">{{ movie.tags?.slice(0, 2).join(' ') }}</p>
                      <p class="text-xs text-white/50 mt-0.5">{{ formatUpdateTime(movie.update_time) }}</p>
                    </div>
                  </a>
                </div>
              </div>
              <div v-if="todaySidebarTotal > todaySidebarMovies.length" class="p-3 text-center">
                <NuxtLink to="/today" class="text-sm text-blue-400 hover:text-blue-500">
                  查看更多
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import {
  Film,
  Monitor,
  VideoCamera,
  MagicStick,
  Lightning,
  Calendar,
  ArrowRight
} from '@element-plus/icons-vue'
import type { HomeBlock, MovieItem } from '~/types'

const { getHomeBlocks, getHomeBanners, getTodayMovies: getHomeTodayMovies, getRankById } = useHome()
const { getMovieList } = useMovies()
const { getBestCover } = useImageProxy()

const activeCategory = ref('home')

// 热搜榜/热播榜相关
const activeRankTab = ref<'hot' | 'search'>('hot') // 默认显示热播榜
const rankLoading = ref(false)
const rankData = ref<{
  hot: MovieItem[]
  search: MovieItem[]
}>({
  hot: [],
  search: []
})

// 当前显示的排行榜影片
const currentRankMovies = computed(() => {
  return rankData.value[activeRankTab.value] || []
})

// 加载排行榜数据（热搜榜/热播榜）
const loadRankData = async () => {
  rankLoading.value = true
  try {
    // 并行加载两个榜单：热播榜(id=2)和热搜榜(id=1)
    const [hotResult, searchResult] = await Promise.all([
      getRankById(2), // 热播榜
      getRankById(1)  // 热搜榜
    ])
    if (hotResult?.movies) {
      rankData.value.hot = hotResult.movies
    }
    if (searchResult?.movies) {
      rankData.value.search = searchResult.movies
    }
  } catch (error) {
    console.error('加载排行榜数据失败:', error)
  } finally {
    rankLoading.value = false
  }
}
const categoryLoading = ref(false)
const categoryMovies = ref<{
  newest: MovieItem[]
  recommend: MovieItem[]
  topRated: MovieItem[]
}>({
  newest: [],
  recommend: [],
  topRated: []
})

// ===== 首页数据获取（禁用SSR缓存，确保获取最新数据） =====
const { data: homeData, pending: loading, refresh } = await useAsyncData(
  'home-data-v2',  // 修改key强制刷新
  async () => {
    const [blocks, banners, todayResult] = await Promise.all([
      getHomeBlocks(),
      getHomeBanners(),
      getHomeTodayMovies(1, 10)
    ])
    return {
      blocks,
      banners,
      todayMovies: todayResult.list,
      todayTotal: todayResult.total
    }
  },
  {
    server: false,  // 禁用SSR，客户端获取确保数据最新
    lazy: false,
    default: () => ({
      blocks: [],
      banners: [],
      todayMovies: [],
      todayTotal: 0
    })
  }
)

// 页面挂载后强制刷新数据
onMounted(() => {
  refresh()
})

// 从预取数据解构
const homeBlocks = computed(() => homeData.value?.blocks ?? [])
const banners = computed(() => homeData.value?.banners ?? [])
const todaySidebarMovies = computed(() => homeData.value?.todayMovies ?? [])
const todaySidebarTotal = computed(() => homeData.value?.todayTotal ?? 0)
const todaySidebarLoading = ref(false)
const todaySidebarPageSize = 10

// 视频分类
const videoCategories = [
  { key: 'movies', label: '电影', icon: Film, link: '/reels' },
  { key: 'tv', label: '电视剧', icon: Monitor, link: '/tv' },
  { key: 'variety', label: '综艺', icon: VideoCamera, link: '/variety' },
  { key: 'animation', label: '动漫', icon: MagicStick, link: '/cels' },
  { key: 'shorts', label: '短剧', icon: Lightning, link: '/shorts' }
]

const currentCategory = computed(() => {
  return videoCategories.find(c => c.key === activeCategory.value) || videoCategories[0]
})

// 刷新右侧边栏今日更新（手动刷新时用）
const refreshTodaySidebar = async () => {
  todaySidebarLoading.value = true
  try {
    const result = await getHomeTodayMovies(1, todaySidebarPageSize)
    // 更新缓存数据
    if (homeData.value) {
      homeData.value.todayMovies = result.list
      homeData.value.todayTotal = result.total
    }
  } catch (error) {
    console.error('刷新侧边栏今日更新失败:', error)
  } finally {
    todaySidebarLoading.value = false
  }
}

// 格式化更新时间
const formatUpdateTime = (timestamp: number): string => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 加载分类数据
watch(activeCategory, async (newVal) => {
  if (newVal === 'home') return

  categoryLoading.value = true
  try {
    const [newestRes, recommendRes, topRatedRes] = await Promise.all([
      getMovieList(newVal, { sort: 'new' }, 1, 12),
      getMovieList(newVal, { sort: 'hot' }, 1, 12),
      getMovieList(newVal, { sort: 'score' }, 1, 12)
    ])

    categoryMovies.value = {
      newest: newestRes.list,
      recommend: recommendRes.list,
      topRated: topRatedRes.list
    }
  } finally {
    categoryLoading.value = false
  }
}, { immediate: true })

// SEO
usePageSeo('', '提供最新电影、电视剧、综艺、动漫等高清在线观看')

// 记录登录用户页面访问
const { recordPageVisit } = useActivity()
onMounted(() => {
  recordPageVisit('/')
  // 加载热搜榜/热播榜数据
  loadRankData()
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
