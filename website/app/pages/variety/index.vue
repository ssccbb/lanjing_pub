<template>
  <div class="px-1 sm:px-4 md:px-3 lg:px-5 pb-16">
    <!-- Filter Bar -->
    <FilterBar
      v-model="filters"
      :filters="filterConfigs"
      :sort-options="sortOptions"
      :total="total"
      @change="handleFilterChange"
    />

    <!-- Movie Grid -->
    <div>
      <MovieGrid
        v-model:page="page"
        :movies="movies"
        :loading="loading"
        :error="error"
        :total="total"
        :page-size="pageSize"
        @retry="refresh"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MovieItem, FilterOptions } from '~/types'

const { getMovieList } = useMovies()
const { getVarietyFilters, getDefaultFilters, sortOptions } = useFilters()

// SEO
usePageSeo('综艺', '热门综艺节目在线观看，真人秀、脱口秀、选秀节目等')

// State
const page = ref(1)
const pageSize = 24
const filterConfigs = getVarietyFilters()
const filters = ref<FilterOptions>(getDefaultFilters())

// 数据加载
const { data: listData, pending: loading, error, refresh } = useAsyncData(
  () => `variety-${filters.value.sort}-${filters.value.type}-${filters.value.year}-${filters.value.region}-${page.value}`,
  () => getMovieList('variety', filters.value, page.value, pageSize),
  {
    server: true,
    lazy: false,
    default: () => ({ list: [], total: 0, page: 1, pageSize: 24 }),
    watch: [page, filters]
  }
)

const movies = computed(() => listData.value?.list ?? [])
const total = computed(() => listData.value?.total ?? 0)

const handleFilterChange = () => {
  page.value = 1
  refresh()
}
</script>
