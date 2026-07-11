import type { HomeBlock, MovieItem } from '~/types'
import { getAuthHeaders } from './useSignedFetch'

interface HomeData {
  banners: MovieItem[]
  recommends: MovieItem[]
  newest: MovieItem[]
  categories: {
    movies: MovieItem[]
    tv: MovieItem[]
    series: MovieItem[]
    cartoon: MovieItem[]
  }
}

export const useHome = () => {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  // 后端通用响应格式
  interface ApiResponse<T> {
    code: number
    data: T
    message?: string
  }

  // 获取首页数据
  const getHomeData = async (): Promise<HomeData> => {
    try {
      const response = await $fetch<ApiResponse<HomeData>>(`${baseUrl}/web/home`, {
        headers: getAuthHeaders()
      })
      return response.data || {
        banners: [],
        recommends: [],
        newest: [],
        categories: {
          movies: [],
          tv: [],
          series: [],
          cartoon: []
        }
      }
    } catch (error) {
      console.error('获取首页数据失败:', error)
      // 返回空数据作为fallback
      return {
        banners: [],
        recommends: [],
        newest: [],
        categories: {
          movies: [],
          tv: [],
          series: [],
          cartoon: []
        }
      }
    }
  }

  // 获取首页Banner数据
  const getHomeBanners = async (): Promise<MovieItem[]> => {
    const homeData = await getHomeData()
    return homeData.banners || []
  }

  // 获取今日更新列表
  const getTodayMovies = async (
    page: number = 1,
    pageSize: number = 30,
    categories?: number[]
  ): Promise<{ list: MovieItem[], total: number, page: number, pageSize: number }> => {
    try {
      const query: any = { page, page_size: pageSize }
      // 如果指定了分类，添加到查询参数
      if (categories && categories.length > 0) {
        query.categories = categories.join(',')
      }

      const response = await $fetch<ApiResponse<any>>(`${baseUrl}/web/home/today`, {
        query,
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

  // 获取首页区块数据（按设计文档格式）
  const getHomeBlocks = async (): Promise<HomeBlock[]> => {
    const homeData = await getHomeData()
    const blocks: HomeBlock[] = []

    // 最新上线
    if (homeData.newest?.length) {
      blocks.push({
        item_key: 'newest',
        item_type: 'carousel',
        data_json: {
          title: '新片速递',
          subtitle: '新鲜出炉的影视内容',
          items: homeData.newest,
          more_link: '/movies'
        },
        sort_order: 1
      })
    }

    // 电影推荐
    if (homeData.categories?.movies?.length) {
      blocks.push({
        item_key: 'movies',
        item_type: 'carousel',
        data_json: {
          title: '热门影片',
          subtitle: '当下最受欢迎的影片',
          items: homeData.categories.movies,
          more_link: '/movies'
        },
        sort_order: 2
      })
    }

    // 电视剧
    if (homeData.categories?.tv?.length) {
      blocks.push({
        item_key: 'tv',
        item_type: 'carousel',
        data_json: {
          title: '剧集精选',
          subtitle: '追番看剧不停歇',
          items: homeData.categories.tv,
          more_link: '/tv'
        },
        sort_order: 3
      })
    }

    // 综艺
    if (homeData.categories?.series?.length) {
      blocks.push({
        item_key: 'series',
        item_type: 'carousel',
        data_json: {
          title: '综艺大观',
          subtitle: '爆笑娱乐尽在其中',
          items: homeData.categories.series,
          more_link: '/variety'
        },
        sort_order: 4
      })
    }

    // 动漫
    if (homeData.categories?.cartoon?.length) {
      blocks.push({
        item_key: 'cartoon',
        item_type: 'carousel',
        data_json: {
          title: '二次元天地',
          subtitle: '精彩动画轮番上演',
          items: homeData.categories.cartoon,
          more_link: '/animation'
        },
        sort_order: 5
      })
    }

    return blocks
  }

  // 获取排行榜数据
  const getRankById = async (rankId: number): Promise<{ id: number, name: string, description: string, cover: string, movies: MovieItem[] } | null> => {
    try {
      const response = await $fetch<ApiResponse<any>>(`${baseUrl}/web/home/rank/${rankId}`, {
        headers: getAuthHeaders()
      })
      if (response?.data) {
        return response.data
      }
      return null
    } catch (error) {
      console.error('获取排行榜数据失败:', error)
      return null
    }
  }

  // 获取所有排行榜数据
  const getAllRanks = async (): Promise<{ id: number, name: string, description: string, cover: string, movies: MovieItem[] }[]> => {
    try {
      const response = await $fetch<ApiResponse<{ ranks: { id: number, name: string, description: string, cover: string, movies: MovieItem[] }[] }>>(`${baseUrl}/web/home/ranks/all`, {
        headers: getAuthHeaders()
      })
      if (response?.data?.ranks) {
        return response.data.ranks
      }
      return []
    } catch (error) {
      console.error('获取所有排行榜数据失败:', error)
      return []
    }
  }

  // 获取片单列表（分页）
  const getWatchlists = async (
    page: number = 1,
    pageSize: number = 6
  ): Promise<{
    list: { id: number, name: string, description: string, cover: string, movies: MovieItem[] }[],
    total: number,
    page: number,
    page_size: number,
    total_pages: number
  }> => {
    try {
      const response = await $fetch<ApiResponse<{
        list: { id: number, name: string, description: string, cover: string, movies: MovieItem[] }[],
        total: number,
        page: number,
        page_size: number,
        total_pages: number
      }>>(`${baseUrl}/web/home/watchlists/all`, {
        query: { page, page_size: pageSize },
        headers: getAuthHeaders()
      })
      if (response?.data) {
        return response.data
      }
      return { list: [], total: 0, page, page_size: pageSize, total_pages: 0 }
    } catch (error) {
      console.error('获取片单列表失败:', error)
      return { list: [], total: 0, page, page_size: pageSize, total_pages: 0 }
    }
  }

  return {
    getHomeData,
    getHomeBlocks,
    getHomeBanners,
    getTodayMovies,
    getRankById,
    getAllRanks,
    getWatchlists
  }
}
