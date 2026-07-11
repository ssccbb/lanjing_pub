/**
 * 影片筛选配置
 * 根据标签数据分析生成，每个分类有不同的侧重点
 * your_custom_filters_here
 */

export interface FilterOption {
  value: string
  label: string
}

export interface FilterConfig {
  key: string
  label: string
  options: FilterOption[]
  priority?: number // 排序优先级，数字小的排在前面
}

// ==================== 电影（侧重：类型）====================
export const movieFilters: FilterConfig[] = [
  {
    key: 'type',
    label: '类型',
    priority: 1,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'region',
    label: '地区',
    priority: 2,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'year',
    label: '年份',
    priority: 3,
    options: [
      { value: 'all', label: '全部' },
    ]
  }
]

// ==================== 电视剧（侧重：地区）====================
export const tvFilters: FilterConfig[] = [
  {
    key: 'region',
    label: '地区',
    priority: 1,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'type',
    label: '类型',
    priority: 2,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'year',
    label: '年份',
    priority: 3,
    options: [
      { value: 'all', label: '全部' },
    ]
  }
]

// ==================== 综艺（侧重：节目类型）====================
export const varietyFilters: FilterConfig[] = [
  {
    key: 'type',
    label: '节目类型',
    priority: 1,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'region',
    label: '地区',
    priority: 2,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'year',
    label: '年份',
    priority: 3,
    options: [
      { value: 'all', label: '全部' },
    ]
  }
]

// ==================== 动漫（侧重：题材）====================
export const animationFilters: FilterConfig[] = [
  {
    key: 'type',
    label: '题材',
    priority: 1,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'region',
    label: '地区',
    priority: 2,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'year',
    label: '年份',
    priority: 3,
    options: [
      { value: 'all', label: '全部' },
    ]
  }
]

// ==================== 短剧（侧重：内容标签）====================
export const shortsFilters: FilterConfig[] = [
  {
    key: 'type',
    label: '内容标签',
    priority: 1,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'region',
    label: '地区',
    priority: 2,
    options: [
      { value: 'all', label: '全部' },
    ]
  },
  {
    key: 'year',
    label: '年份',
    priority: 3,
    options: [
      { value: 'all', label: '全部' },
    ]
  }
]

// ==================== 排序选项 ====================
export const sortOptions = [
  { value: 'recommend', label: '推荐' },
  { value: 'new', label: '最新' },
  { value: 'score', label: '评分' }
]

// ==================== 获取默认筛选值 ====================
export const getDefaultFilters = () => ({
  type: 'all',
  region: 'all',
  year: 'all',
  sort: 'recommend'
})

// ==================== 根据分类获取筛选配置 ====================
export const getFiltersByCategory = (category: 'movie' | 'tv' | 'variety' | 'animation' | 'shorts') => {
  switch (category) {
    case 'movie':
      return movieFilters
    case 'tv':
      return tvFilters
    case 'variety':
      return varietyFilters
    case 'animation':
      return animationFilters
    case 'shorts':
      return shortsFilters
    default:
      return movieFilters
  }
}
