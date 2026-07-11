<template>
  <div class="sticky top-14 z-30 bg-app-bg/95 backdrop-blur-sm -mx-1 sm:-mx-4 md:-mx-3 lg:-mx-5 px-1 sm:px-4 md:px-3 lg:px-5">
    <!-- Collapsed State -->
    <div v-if="!isExpanded" class="py-2 md:py-3">
      <div class="flex items-center justify-between">
        <!-- PC: Show filter tags | Mobile: Show "已筛选" only -->
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-500 hidden md:inline">已选筛选：</span>
          <span class="text-sm text-gray-500 md:hidden">已筛选</span>
          <div class="hidden md:flex items-center gap-2 flex-wrap">
            <span
              v-for="filter in activeFilters"
              :key="filter.key"
              class="px-2 py-0.5 bg-app-primary/10 text-app-primary text-xs rounded"
            >
              {{ filter.label }}: {{ filter.valueLabel }}
            </span>
            <span v-if="activeFilters.length === 0" class="text-sm text-gray-500">全部</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm font-medium" style="color: #B8860B;">共 {{ total }} 部</span>
          <button
            class="flex items-center gap-1 px-3 py-1.5 bg-black hover:bg-app-bg-tertiary text-gray-300 text-sm rounded-lg transition-colors"
            @click="isExpanded = true"
          >
            <el-icon :size="14"><Filter /></el-icon>
            <span>筛选</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Expanded State -->
    <div v-else class="py-3 md:py-4">
      <!-- Filter Groups & Sort -->
      <div class="space-y-2 md:space-y-3">
        <div
          v-for="filter in filters"
          :key="filter.key"
          class="flex items-start gap-4"
        >
          <span class="text-sm text-gray-500 whitespace-nowrap mt-1 w-12">{{ filter.label }}</span>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="option in filter.options"
              :key="option.value"
              class="px-3 py-1 text-sm rounded-full transition-colors"
              :class="modelValue[filter.key] === option.value
                ? 'bg-app-primary text-white'
                : 'bg-app-bg text-white hover:bg-app-bg-tertiary'"
              @click="updateFilter(filter.key, option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <!-- Sort -->
        <div class="flex items-start gap-4">
          <span class="text-sm text-gray-500 whitespace-nowrap mt-1 w-12">排序</span>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="option in sortOptions"
              :key="option.value"
              class="px-3 py-1 text-sm rounded-full transition-colors"
              :class="modelValue.sort === option.value
                ? 'bg-app-primary text-white'
                : 'text-white/70 hover:text-white'"
              @click="updateFilter('sort', option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Footer: Count & Close -->
      <div class="flex items-center justify-between mt-3 md:mt-4">
        <span class="text-sm font-medium" style="color: #B8860B;">共 {{ total }} 部</span>
        <button
          class="flex items-center gap-1 px-4 py-1.5 bg-black hover:bg-app-bg-tertiary text-gray-300 text-sm rounded-lg transition-colors"
          @click="isExpanded = false"
        >
          <el-icon :size="14"><ArrowUp /></el-icon>
          <span>收起</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowUp, Filter } from '@element-plus/icons-vue'
import type { FilterConfig, FilterOptions } from '~/types'

interface Props {
  filters: FilterConfig[]
  sortOptions: { value: string; label: string }[]
  modelValue: FilterOptions
  total: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: FilterOptions]
  change: [value: FilterOptions]
}>()

const updateFilter = (key: string, value: string) => {
  const newValue = { ...props.modelValue, [key]: value }
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

// 展开/收起状态
const isExpanded = ref(false)

// 当前生效的筛选条件
const activeFilters = computed(() => {
  const result: { key: string; label: string; valueLabel: string }[] = []
  props.filters.forEach(filter => {
    const currentValue = props.modelValue[filter.key]
    const option = filter.options.find(opt => opt.value === currentValue)
    if (option && currentValue !== 'all' && currentValue !== '') {
      result.push({
        key: filter.key,
        label: filter.label,
        valueLabel: option.label
      })
    }
  })

  // 添加排序方式到已选筛选
  const currentSort = props.modelValue.sort
  const sortOption = props.sortOptions.find(opt => opt.value === currentSort)
  if (sortOption) {
    result.push({
      key: 'sort',
      label: '排序',
      valueLabel: sortOption.label
    })
  }

  return result
})
</script>
