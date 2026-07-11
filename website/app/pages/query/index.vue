<template>
  <div class="px-4 md:px-6 lg:px-10">
    <!-- Results -->
    <div>
      <!-- Loading -->
      <div v-if="loading" class="py-12 text-center">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p class="text-gray-500 mt-4">搜索中...</p>
      </div>

      <!-- Error -->
      <div v-else-if="searchError" class="py-16 text-center">
        <el-icon :size="48" class="text-red-400 mb-4"><Warning /></el-icon>
        <p class="text-gray-500 mb-2">{{ searchError }}</p>
        <button
          class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          @click="handleSearch"
        >
          重新搜索
        </button>
      </div>

      <!-- Results Grid -->
      <template v-else-if="hasSearched">
        <div class="mb-4">
          <p class="text-gray-500">
            "<span class="text-gray-100 font-medium">{{ searchedKeyword }}</span>" 的搜索结果
            <span v-if="total > 0" class="text-sm">（共 {{ total }} 条）</span>
          </p>
        </div>

        <!-- No Results -->
        <div v-if="results.length === 0" class="py-16 text-center">
          <el-icon :size="48" class="text-gray-500 mb-4"><Search /></el-icon>
          <p class="text-gray-500">未找到相关内容</p>
          <div class="mt-6">
            <p class="text-sm text-gray-500 mb-3">试试搜索</p>
            <div class="flex flex-wrap justify-center gap-2">
              <button
                v-for="tag in hotTags"
                :key="tag"
                class="px-3 py-1 bg-black rounded-full text-sm hover:bg-app-bg-tertiary transition-colors"
                @click="quickSearch(tag)"
              >
                {{ tag }}
              </button>
            </div>
          </div>
        </div>

        <!-- Results Grid -->
        <MovieGrid
          v-else
          v-model:page="page"
          :movies="results"
          :loading="loading"
          :total="total"
          :page-size="pageSize"
        />
      </template>

      <!-- Initial State -->
      <div v-else class="py-12">
        <div class="max-w-2xl mx-auto">
          <h2 class="text-lg font-bold mb-4">热门搜索</h2>
          <div class="flex flex-wrap gap-3">
            <button
              v-for="tag in hotTags"
              :key="tag"
              class="px-4 py-2 bg-black rounded-full hover:bg-app-bg-tertiary transition-colors"
              @click="quickSearch(tag)"
            >
              {{ tag }}
            </button>
          </div>

          <!-- Search History -->
          <div v-if="searchHistory.length" class="mt-8">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-bold">搜索历史</h2>
              <button
                class="text-sm text-gray-500 hover:text-gray-100"
                @click="clearHistory"
              >
                清空
              </button>
            </div>
            <div class="flex flex-wrap gap-3">
              <button
                v-for="tag in searchHistory"
                :key="tag"
                class="px-4 py-2 bg-black rounded-full hover:bg-app-bg-tertiary transition-colors"
                @click="quickSearch(tag)"
              >
                {{ tag }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Search, Loading, Warning } from '@element-plus/icons-vue'
import type { MovieItem } from '~/types'

const { searchMovies } = useMovies()
const { getSearchHistory, addSearchHistory, clearSearchHistory } = useSearchHistory()
const { recordSearchHistory, getHotSearchRecords } = useSearchRecord()

usePageSeo('搜索')

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const searchedKeyword = ref('')
const page = ref(1)
const pageSize = 24

// 从 URL 初始化搜索状态（服务端和客户端保持一致）
const initialQuery = route.query.q as string
const hasSearched = ref(!!initialQuery)
if (initialQuery) {
  keyword.value = initialQuery
  searchedKeyword.value = initialQuery
}

const searchHistory = computed(() => {
  if (process.server) return []
  return getSearchHistory().map(item => item.keyword)
})

// 热门搜索标签
const hotTags = ref<string[]>([])
const hotTagsLoading = ref(false)

// 加载热门搜索
const loadHotTags = async () => {
  hotTagsLoading.value = true
  try {
    const records = await getHotSearchRecords(10)
    hotTags.value = records.map(item => item.name)
  } catch (error) {
    console.error('加载热门搜索失败:', error)
    hotTags.value = []
  } finally {
    hotTagsLoading.value = false
  }
}

// 搜索结果缓存
const searchCache = ref<{
  keyword: string
  list: MovieItem[]
  total: number
} | null>(null)

// 搜索加载状态
const isSearching = ref(false)
const searchError = ref('')

// 加载搜索结果
const loadSearchResults = async () => {
  if (!searchedKeyword.value) return

  isSearching.value = true
  searchError.value = ''

  try {
    const result = await searchMovies(searchedKeyword.value, page.value, pageSize)

    searchCache.value = {
      keyword: searchedKeyword.value,
      list: result.list || [],
      total: result.total || 0
    }

    // 异步记录搜索历史（不阻塞主流程）
    if (result.list && result.list.length > 0) {
      const seriesTitles = [...new Set(
        result.list
          .map((movie: MovieItem) => movie.series_title)
          .filter((title: string | undefined) => title)
      )]
      recordSearchHistory(seriesTitles).catch(() => {
        // 忽略错误
      })
    }
  } catch (err: any) {
    console.error('搜索异常:', err)
    searchError.value = err?.message || '搜索失败'
    searchCache.value = {
      keyword: searchedKeyword.value,
      list: [],
      total: 0
    }
  } finally {
    isSearching.value = false
  }
}

const results = computed(() => searchCache.value?.list ?? [])
const total = computed(() => searchCache.value?.total ?? 0)
const loading = computed(() => isSearching.value)

const handleSearch = async () => {
  const q = keyword.value.trim()
  if (!q) return

  searchedKeyword.value = q
  hasSearched.value = true
  page.value = 1

  // Add to history
  if (!process.server) {
    addSearchHistory(q)
  }

  // Update URL
  router.push({ query: { q } })

  // 执行搜索
  await loadSearchResults()
}

const quickSearch = (tag: string) => {
  keyword.value = tag
  handleSearch()
}

const clearHistory = () => {
  if (!process.server) {
    clearSearchHistory()
  }
}

// 监听页码变化
watch(page, async () => {
  if (hasSearched.value && searchedKeyword.value) {
    await loadSearchResults()
  }
})

// Load from URL (client only)
onMounted(() => {
  // 加载热门搜索标签
  loadHotTags()

  // 如果已有搜索参数，执行搜索加载结果
  if (hasSearched.value && searchedKeyword.value) {
    loadSearchResults()
  }

  // 记录登录用户页面访问
  const { recordPageVisit } = useActivity()
  recordPageVisit('/query')
})

// 监听 URL 参数变化（在搜索页面内重新搜索）
watch(() => route.query.q, (newQ, oldQ) => {
  if (newQ && newQ !== oldQ) {
    const q = newQ as string
    keyword.value = q
    searchedKeyword.value = q
    hasSearched.value = true
    page.value = 1
    loadSearchResults()
  }
})
</script>
