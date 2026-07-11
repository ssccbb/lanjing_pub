import type { FilterConfig, FilterOptions } from '~/types'

// ==================== 电影（侧重：类型）====================
const movieTypeOptions = [
  { value: 'all', label: '全部' },
  { value: '剧情', label: '剧情' },
  { value: '喜剧', label: '喜剧' },
  { value: '动作', label: '动作' },
  { value: '爱情', label: '爱情' },
  { value: '惊悚', label: '惊悚' },
  { value: '恐怖', label: '恐怖' },
  { value: '犯罪', label: '犯罪' },
  { value: '悬疑', label: '悬疑' },
  { value: '科幻', label: '科幻' },
  { value: '奇幻', label: '奇幻' },
  { value: '冒险', label: '冒险' },
  { value: '动画', label: '动画' },
  { value: '战争', label: '战争' },
  { value: '历史', label: '历史' },
  { value: '传记', label: '传记' },
  { value: '武侠', label: '武侠' },
  { value: '纪录片', label: '纪录片' },
  { value: '家庭', label: '家庭' },
  { value: '音乐', label: '音乐' },
  { value: '同性', label: '同性' }
]

// ==================== 电视剧（侧重：地区）====================
const tvTypeOptions = [
  { value: 'all', label: '全部' },
  { value: '剧情', label: '剧情' },
  { value: '爱情', label: '爱情' },
  { value: '喜剧', label: '喜剧' },
  { value: '悬疑', label: '悬疑' },
  { value: '犯罪', label: '犯罪' },
  { value: '古装', label: '古装' },
  { value: '科幻', label: '科幻' },
  { value: '奇幻', label: '奇幻' },
  { value: '惊悚', label: '惊悚' },
  { value: '动作', label: '动作' },
  { value: '家庭', label: '家庭' },
  { value: '历史', label: '历史' },
  { value: '战争', label: '战争' },
  { value: '武侠', label: '武侠' },
  { value: '恐怖', label: '恐怖' },
  { value: '同性', label: '同性' },
  { value: '传记', label: '传记' },
  { value: '冒险', label: '冒险' }
]

// ==================== 综艺（侧重：节目类型）====================
const varietyTypeOptions = [
  { value: 'all', label: '全部' },
  { value: '真人秀', label: '真人秀' },
  { value: '脱口秀', label: '脱口秀' },
  { value: '相声', label: '相声' },
  { value: '晚会', label: '晚会' },
  { value: '歌舞', label: '歌舞' },
  { value: '演唱会', label: '演唱会' },
  { value: '美食', label: '美食' },
  { value: '生活', label: '生活' },
  { value: '运动', label: '运动' },
  { value: '音乐', label: '音乐' },
  { value: '喜剧', label: '喜剧' },
  { value: '纪录片', label: '纪录片' },
  { value: '爱情', label: '爱情' },
  { value: '剧情', label: '剧情' },
  { value: '历史', label: '历史' },
  { value: '冒险', label: '冒险' },
  { value: '家庭', label: '家庭' }
]

// ==================== 动漫（侧重：题材）====================
const animationTypeOptions = [
  { value: 'all', label: '全部' },
  { value: '奇幻', label: '奇幻' },
  { value: '冒险', label: '冒险' },
  { value: '科幻', label: '科幻' },
  { value: '热血', label: '热血' },
  { value: '玄幻', label: '玄幻' },
  { value: '武侠', label: '武侠' },
  { value: '古装', label: '古装' },
  { value: '悬疑', label: '悬疑' },
  { value: '穿越', label: '穿越' },
  { value: '战斗', label: '战斗' },
  { value: '动作', label: '动作' },
  { value: '喜剧', label: '喜剧' },
  { value: '爱情', label: '爱情' },
  { value: '恐怖', label: '恐怖' },
  { value: '惊悚', label: '惊悚' },
  { value: '运动', label: '运动' },
  { value: '音乐', label: '音乐' },
  { value: '战争', label: '战争' },
  { value: '犯罪', label: '犯罪' },
  { value: '历史', label: '历史' },
  { value: '歌舞', label: '歌舞' },
  { value: '搞笑', label: '搞笑' },
  { value: '少女', label: '少女' },
  { value: '恋爱', label: '恋爱' },
  { value: '儿童', label: '儿童' },
  { value: '家庭', label: '家庭' },
  { value: '剧情', label: '剧情' }
]

// ==================== 短剧（侧重：内容标签）====================
const shortsTypeOptions = [
  { value: 'all', label: '全部' },
  { value: '现代都市', label: '现代都市' },
  { value: '女频恋爱', label: '女频恋爱' },
  { value: '年代穿越', label: '年代穿越' },
  { value: '古装仙侠', label: '古装仙侠' },
  { value: '反转爽剧', label: '反转爽剧' },
  { value: '脑洞悬疑', label: '脑洞悬疑' },
  { value: '剧情', label: '剧情' },
  { value: '动作', label: '动作' },
  { value: '喜剧', label: '喜剧' }
]

// ==================== 地区选项 ====================
// 电影地区（全）
const movieRegionOptions = [
  { value: 'all', label: '全部' },
  { value: '中国大陆', label: '中国大陆' },
  { value: '美国', label: '美国' },
  { value: '中国香港', label: '中国香港' },
  { value: '日本', label: '日本' },
  { value: '韩国', label: '韩国' },
  { value: '英国', label: '英国' },
  { value: '中国台湾', label: '中国台湾' },
  { value: '法国', label: '法国' },
  { value: '德国', label: '德国' },
  { value: '印度', label: '印度' },
  { value: '加拿大', label: '加拿大' },
  { value: '泰国', label: '泰国' },
  { value: '意大利', label: '意大利' },
  { value: '西班牙', label: '西班牙' },
  { value: '澳大利亚', label: '澳大利亚' }
]

// 电视剧地区（侧重）
const tvRegionOptions = [
  { value: 'all', label: '全部' },
  { value: '中国大陆', label: '中国大陆' },
  { value: '日本', label: '日本' },
  { value: '韩国', label: '韩国' },
  { value: '中国香港', label: '中国香港' },
  { value: '中国台湾', label: '中国台湾' },
  { value: '泰国', label: '泰国' },
  { value: '美国', label: '美国' },
  { value: '英国', label: '英国' },
  { value: '法国', label: '法国' },
  { value: '德国', label: '德国' },
  { value: '加拿大', label: '加拿大' },
  { value: '西班牙', label: '西班牙' },
  { value: '意大利', label: '意大利' },
  { value: '印度', label: '印度' },
  { value: '澳大利亚', label: '澳大利亚' }
]

// 综艺地区
const varietyRegionOptions = [
  { value: 'all', label: '全部' },
  { value: '中国大陆', label: '中国大陆' },
  { value: '中国台湾', label: '中国台湾' },
  { value: '中国香港', label: '中国香港' },
  { value: '韩国', label: '韩国' },
  { value: '日本', label: '日本' },
  { value: '美国', label: '美国' },
  { value: '英国', label: '英国' }
]

// 动漫地区
const animationRegionOptions = [
  { value: 'all', label: '全部' },
  { value: '日本', label: '日本' },
  { value: '中国大陆', label: '中国大陆' },
  { value: '美国', label: '美国' },
  { value: '韩国', label: '韩国' },
  { value: '英国', label: '英国' },
  { value: '加拿大', label: '加拿大' },
  { value: '法国', label: '法国' },
  { value: '中国台湾', label: '中国台湾' },
  { value: '中国香港', label: '中国香港' }
]

// 短剧地区
const shortsRegionOptions = [
  { value: 'all', label: '全部' },
  { value: '中国大陆', label: '中国大陆' },
  { value: '韩国', label: '韩国' },
  { value: '美国', label: '美国' },
  { value: '中国台湾', label: '中国台湾' },
  { value: '中国香港', label: '中国香港' },
  { value: '日本', label: '日本' },
  { value: '法国', label: '法国' },
  { value: '泰国', label: '泰国' },
  { value: '印度', label: '印度' },
  { value: '英国', label: '英国' },
  { value: '澳大利亚', label: '澳大利亚' }
]

// ==================== 年份选项 ====================
const movieYearOptions = [
  { value: 'all', label: '全部' },
  { value: '2025', label: '2025' },
  { value: '2024', label: '2024' },
  { value: '2023', label: '2023' },
  { value: '2022', label: '2022' },
  { value: '2021', label: '2021' },
  { value: '2020', label: '2020' },
  { value: '2019', label: '2019' },
  { value: '2018', label: '2018' },
  { value: '2017', label: '2017' },
  { value: '2016', label: '2016' },
  { value: '2015', label: '2015' },
  { value: '2010s', label: '2010-2014' },
  { value: '2000s', label: '2000-2009' },
  { value: '1990s', label: '1990-1999' },
  { value: '1980s', label: '1980-1989' },
  { value: 'older', label: '更早' }
]

const tvYearOptions = [
  { value: 'all', label: '全部' },
  { value: '2025', label: '2025' },
  { value: '2024', label: '2024' },
  { value: '2023', label: '2023' },
  { value: '2022', label: '2022' },
  { value: '2021', label: '2021' },
  { value: '2020', label: '2020' },
  { value: '2019', label: '2019' },
  { value: '2018', label: '2018' },
  { value: '2017', label: '2017' },
  { value: '2016', label: '2016' },
  { value: '2015', label: '2015' },
  { value: '2010s', label: '2010-2014' },
  { value: '2000s', label: '2000-2009' },
  { value: '1990s', label: '1990-1999' },
  { value: '1980s', label: '1980-1989' },
  { value: 'older', label: '更早' }
]

const varietyYearOptions = [
  { value: 'all', label: '全部' },
  { value: '2025', label: '2025' },
  { value: '2024', label: '2024' },
  { value: '2023', label: '2023' },
  { value: '2022', label: '2022' },
  { value: '2021', label: '2021' },
  { value: '2020', label: '2020' },
  { value: '2019', label: '2019' },
  { value: '2018', label: '2018' },
  { value: '2017', label: '2017' },
  { value: '2016', label: '2016' },
  { value: '2015', label: '2015' },
  { value: 'older', label: '更早' }
]

const animationYearOptions = [
  { value: 'all', label: '全部' },
  { value: '2025', label: '2025' },
  { value: '2024', label: '2024' },
  { value: '2023', label: '2023' },
  { value: '2022', label: '2022' },
  { value: '2021', label: '2021' },
  { value: '2020', label: '2020' },
  { value: '2019', label: '2019' },
  { value: '2018', label: '2018' },
  { value: '2017', label: '2017' },
  { value: '2016', label: '2016' },
  { value: '2015', label: '2015' },
  { value: '2010s', label: '2010-2014' },
  { value: '2000s', label: '2000-2009' },
  { value: 'older', label: '更早' }
]

const shortsYearOptions = [
  { value: 'all', label: '全部' },
  { value: '2025', label: '2025' },
  { value: '2024', label: '2024' },
  { value: '2023', label: '2023' },
  { value: '2022', label: '2022' },
  { value: '2021', label: '2021' },
  { value: '2020', label: '2020' },
  { value: 'older', label: '更早' }
]

// ==================== 排序选项 ====================
const sortOptions = [
  { value: 'hot', label: '最热' },
  { value: 'new', label: '最新' },
  { value: 'score', label: '评分' }
]

// ==================== 状态选项 ====================
const statusOptions = [
  { value: 'all', label: '全部' },
  { value: 'ongoing', label: '连载中' },
  { value: 'completed', label: '已完结' }
]

export const useFilters = () => {
  /**
   * 获取电影筛选配置
   * 侧重：类型
   */
  const getMovieFilters = (): FilterConfig[] => [
    { key: 'type', label: '类型', options: movieTypeOptions },
    { key: 'region', label: '地区', options: movieRegionOptions },
    { key: 'year', label: '年份', options: movieYearOptions }
  ]

  /**
   * 获取电视剧筛选配置
   * 侧重：地区
   */
  const getTvFilters = (): FilterConfig[] => [
    { key: 'region', label: '地区', options: tvRegionOptions },
    { key: 'type', label: '类型', options: tvTypeOptions },
    { key: 'year', label: '年份', options: tvYearOptions }
  ]

  /**
   * 获取综艺筛选配置
   * 侧重：节目类型
   */
  const getVarietyFilters = (): FilterConfig[] => [
    { key: 'type', label: '节目类型', options: varietyTypeOptions },
    { key: 'region', label: '地区', options: varietyRegionOptions },
    { key: 'year', label: '年份', options: varietyYearOptions }
  ]

  /**
   * 获取动漫筛选配置
   * 侧重：题材
   */
  const getAnimationFilters = (): FilterConfig[] => [
    { key: 'type', label: '题材', options: animationTypeOptions },
    { key: 'region', label: '地区', options: animationRegionOptions },
    { key: 'year', label: '年份', options: animationYearOptions }
  ]

  /**
   * 获取短剧筛选配置
   * 侧重：内容标签
   */
  const getShortsFilters = (): FilterConfig[] => [
    { key: 'type', label: '内容标签', options: shortsTypeOptions },
    { key: 'region', label: '地区', options: shortsRegionOptions },
    { key: 'year', label: '年份', options: shortsYearOptions }
  ]

  /**
   * 获取默认筛选状态
   */
  const getDefaultFilters = (): FilterOptions => ({
    type: 'all',
    year: 'all',
    region: 'all',
    status: 'all',
    sort: 'new'
  })

  return {
    getMovieFilters,
    getTvFilters,
    getVarietyFilters,
    getAnimationFilters,
    getShortsFilters,
    getDefaultFilters,
    sortOptions,
    statusOptions
  }
}
