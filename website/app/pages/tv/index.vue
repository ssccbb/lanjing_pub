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
const { getTvFilters, getDefaultFilters, sortOptions } = useFilters()

// SEO
usePageSeo('电视剧', '热门电视剧在线观看，国产剧、韩剧、美剧、日剧应有尽有')

// State
const page = ref(1)
const pageSize = 24
const filterConfigs = getTvFilters()
const filters = ref<FilterOptions>(getDefaultFilters())

// 数据加载
const { data: listData, pending: loading, error, refresh } = useAsyncData(
  () => `tv-${filters.value.sort}-${filters.value.type}-${filters.value.year}-${filters.value.region}-${page.value}`,
  () => getMovieList('tv', filters.value, page.value, pageSize),
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
