// ==================== 基础类型 ====================

export interface Movie {
  id: string                    // 后端返回字符串
  category: number
  title: string
  other_titles?: string[]       // 后端已解析为数组
  score: number
  covers?: string[]             // 后端已解析为数组
  cover_tag?: string
  contents?: string
  tags?: string[]               // 后端已解析为数组
  season?: number
  directors?: string[]          // 后端已解析为数组
  actors?: string[]             // 后端已解析为数组
  series_title?: string
  oneshot_desc?: string
  douban_id?: string
  imdb_id?: string
  publish_year?: string
  upload_time?: string
  update_time?: number
  search_keys?: string
  episodes?: string             // 原始JSON字符串
  episode_sources?: EpisodeSource[]  // 按播放源归类的剧集列表
  extra?: any
  recommend_num?: number
  link_douban?: string
  link_imdb?: string
}

// 单个剧集
export interface Episode {
  id: number
  movie_id: number
  title: string
  m3u8_link?: string
  link_type?: number
  duration?: number
  source_from?: string
  source_link?: string
  source_limit?: number  // 播放限制: 0=无限制, 1=需登录, 2=需付费
}

// 按播放源归类的剧集列表
export interface EpisodeSource {
  source_name: string      // source_from 字段值，如 "线路1", "腾讯视频" 等
  episodes: Episode[]      // 该播放源下的所有剧集
}

export interface HomeBlock {
  id?: number
  item_key: string
  item_type: 'banner' | 'carousel' | 'grid' | 'rank'
  data_json: HomeBlockData
  sort_order: number
}

export interface HomeBlockData {
  title: string
  subtitle?: string
  layout?: string
  items: MovieItem[]
  more_link?: string
}

export interface MovieItem {
  id: string                    // 后端返回字符串
  title: string
  covers?: string[]             // 后端返回covers数组
  cover?: string                // 兼容字段，取covers[0]
  cover_tag?: string            // 封面标签
  score?: number
  year?: string
  publish_year?: string         // 后端返回字段
  tags?: string[]
  episode_count?: number
  latest_episode?: string
  contents?: string             // 影片简介
  directors?: string[]          // 导演
  actors?: string[]             // 演员
  series_title?: string         // 系列标题
  oneshot_desc?: string         // 一句话描述
  extra?: {
    horizontal_cover?: string    // 横幅封面
    main_share_cover?: string
    watch_count?: number
    recommend_count?: number
  }
}

export interface Rank {
  id: number
  name: string
  description?: string
  cover?: string
  movies?: string
  rank_type?: number
}

// ==================== 筛选类型 ====================

export interface FilterOptions {
  type?: string
  year?: string
  region?: string
  status?: string
  sort: 'hot' | 'new' | 'score'
}

export interface FilterConfig {
  key: string
  label: string
  options: FilterOption[]
}

export interface FilterOption {
  value: string
  label: string
}

// ==================== 页面 Props ====================

export interface PageMeta {
  title: string
  description?: string
  keywords?: string
}

// ==================== 响应类型 ====================

export interface ApiResponse<T> {
  code: number
  data: T
  message?: string
}

export interface PaginatedData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
