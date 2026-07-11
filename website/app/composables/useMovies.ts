import type { Movie, MovieItem, FilterOptions, PaginatedData } from '~/types'
import { getAuthHeaders } from './useSignedFetch'

// 分类映射（前端分类 -> 后端category_id）
const categoryMap: Record<string, number> = {
  'movie': 1,      // 电影
  'tv': 2,         // 电视剧
  'variety': 3,    // 综艺（series）
  'animation': 4,  // 动漫（cartoon）
  'shorts': 6      // 短剧
}

// 排序方式映射
const sortMap: Record<string, string> = {
  'hot': 'recommend_num',    // 最热
  'new': 'update_time',      // 最新
  'score': 'score'           // 评分
}

export const useMovies = () => {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  // 获取影片列表
  const getMovieList = async (
    category: string,
    filters: FilterOptions,
    page: number = 1,
    pageSize: number = 24
  ): Promise<PaginatedData<MovieItem>> => {
    try {
      const categoryId = categoryMap[category] || 1
      const orderBy = sortMap[filters.sort] || 'id'

      // 构建查询参数，包含筛选条件
      const query: any = {
        page,
        page_size: pageSize,
        order_by: orderBy
      }

      // 添加筛选参数（如果不是 'all'）
      if (filters.type && filters.type !== 'all') {
        query.type = filters.type
      }
      if (filters.year && filters.year !== 'all') {
        query.year = filters.year
      }
      if (filters.region && filters.region !== 'all') {
        query.region = filters.region
      }
      if (filters.status && filters.status !== 'all') {
        query.status = filters.status
      }

      const response = await $fetch<any>(`${baseUrl}/web/home/list/${categoryId}`, {
        query,
        headers: getAuthHeaders()
      })

      // 后端返回格式: { code, data: { list, total, page, page_size }, message }
      if (response?.data) {
        return {
          list: response.data.list || [],
          total: response.data.total || 0,
          page: response.data.page || page,
          pageSize: response.data.page_size || pageSize
        }
      }

      return { list: [], total: 0, page, pageSize }
    } catch (error) {
      console.error('获取影片列表失败:', error)
      return { list: [], total: 0, page, pageSize }
    }
  }

  // 获取今日更新
  const getTodayMovies = async (
    page: number = 1,
    pageSize: number = 30
  ): Promise<PaginatedData<MovieItem>> => {
    try {
      // 获取今天的时间戳范围
      const now = new Date()
      const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000
      const todayEnd = todayStart + 86400

      // 调用后端API获取今日更新
      const response = await $fetch<any>(`${baseUrl}/web/movies/today`, {
        query: {
          page,
          page_size: pageSize,
          start_time: todayStart,
          end_time: todayEnd
        },
        headers: getAuthHeaders()
      })

      if (response?.data) {
        return {
          list: response.data.list || [],
          total: response.data.total || 0,
          page: response.data.page || page,
          pageSize: response.data.page_size || pageSize
        }
      }

      return { list: [], total: 0, page, pageSize }
    } catch (error) {
      console.error('获取今日更新失败:', error)
      return { list: [], total: 0, page, pageSize }
    }
  }

  // 获取影片详情
  const getMovieDetail = async (id: string): Promise<Movie | null> => {
    try {
      const response = await $fetch<any>(`${baseUrl}/web/home/detail/${id}`, {
        headers: getAuthHeaders()
      })
      return response?.data || null
    } catch (error) {
      console.error('获取影片详情失败:', error)
      return null
    }
  }

  // 获取影片剧集
  const getMovieEpisodes = async (id: string) => {
    try {
      const response = await $fetch<any>(`${baseUrl}/web/movies/${id}/episodes`, {
        headers: getAuthHeaders()
      })
      return response?.data?.episode_sources || []
    } catch (error) {
      console.error('获取影片剧集失败:', error)
      return []
    }
  }

  // 获取相关推荐
  const getRelatedMovies = async (id: string): Promise<MovieItem[]> => {
    try {
      const response = await $fetch<any>(`${baseUrl}/web/movies/${id}/related`, {
        headers: getAuthHeaders()
      })
      return response?.data || []
    } catch (error) {
      console.error('获取相关推荐失败:', error)
      return []
    }
  }

  // 搜索影片
  const searchMovies = async (
    keyword: string,
    page: number = 1,
    pageSize: number = 24
  ): Promise<PaginatedData<MovieItem>> => {
    try {
      const response = await $fetch<any>(`${baseUrl}/web/search`, {
        query: {
          q: keyword,
          page,
          page_size: pageSize
        },
        headers: getAuthHeaders()
      })

      if (response?.data) {
        return {
          list: response.data.list || [],
          total: response.data.total || 0,
          page: response.data.page || page,
          pageSize: response.data.page_size || pageSize
        }
      }

      return { list: [], total: 0, page, pageSize }
    } catch (error) {
      console.error('搜索影片失败:', error)
      return { list: [], total: 0, page, pageSize }
    }
  }

  // 获取热门搜索词
  const getHotKeywords = async (): Promise<string[]> => {
    try {
      const response = await $fetch<any>(`${baseUrl}/web/search/hot`, {
        headers: getAuthHeaders()
      })
      return response?.data || []
    } catch (error) {
      console.error('获取热门搜索词失败:', error)
      return []
    }
  }

  // 更新观看数（静默调用，不阻塞用户）
  const updateWatchCount = async (id: string): Promise<void> => {
    try {
      await $fetch(`${baseUrl}/web/movies/${id}/count`, {
        method: 'POST',
        headers: getAuthHeaders()
      })
    } catch (error) {
      // 静默失败，不影响用户体验
      console.error('更新观看数失败:', error)
    }
  }

  // 更新推荐/不推荐数
  const updateRecommendCount = async (id: string, recommend: boolean): Promise<boolean> => {
    try {
      await $fetch(`${baseUrl}/web/content/movie/${id}/count`, {
        method: 'POST',
        query: { recommend },
        headers: getAuthHeaders()
      })
      return true
    } catch (error) {
      console.error('更新推荐数失败:', error)
      return false
    }
  }

  return {
    getMovieList,
    getMovieDetail,
    getMovieEpisodes,
    getRelatedMovies,
    searchMovies,
    getHotKeywords,
    getTodayMovies,
    updateWatchCount,
    updateRecommendCount
  }
}
