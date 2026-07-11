// 播放记录管理 - 支持本地存储和云端存储（登录用户）
import { getAuthHeaders } from './useSignedFetch'

export interface PlayHistory {
  id: string
  title: string
  cover: string
  covers?: string[]  // 封面数组，用于 getBestCover
  episodeTitle?: string
  sourceName?: string
  timestamp: number
}

// 后端返回的观看记录格式
interface ApiWatchHistory {
  id: number
  movie_id: string
  episode_id: string
  timestamp: number
  covers: string[]
  title: string
  tags: string[]
  create_time: string
}

const HISTORY_KEY = 'app_play_history'
const MAX_HISTORY = 5

export const useHistory = () => {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  // 获取当前存储的 accesstoken
  const getAccessToken = (): string | null => {
    if (!process.client) return null
    const localToken = localStorage.getItem('accesstoken')
    if (localToken) return localToken
    return sessionStorage.getItem('accesstoken_session')
  }

  // 检查是否已登录
  const isLoggedIn = (): boolean => {
    return !!getAccessToken()
  }

  // 从API获取观看记录
  const getHistoryFromApi = async (): Promise<PlayHistory[]> => {
    const accesstoken = getAccessToken()
    if (!accesstoken) return []

    try {
      const response = await $fetch<{
        code: number
        data?: {
          list: ApiWatchHistory[]
          total: number
        }
      }>(`${baseUrl}/web/history/watch-history`, {
        method: 'GET',
        query: { accesstoken, page: 1, page_size: 20 },
        headers: getAuthHeaders()
      })

      if (response.code === 200 && response.data?.list) {
        return response.data.list.map(item => ({
          id: item.movie_id,
          title: item.title,
          cover: item.covers?.[0] || '',
          covers: item.covers || [],  // 保存 covers 数组供 getBestCover 使用
          timestamp: item.timestamp * 1000 // 转换为毫秒
        }))
      }
      return []
    } catch (error) {
      console.error('从API获取播放记录失败:', error)
      return []
    }
  }

  // 从localStorage获取观看记录
  const getHistoryFromLocal = (): PlayHistory[] => {
    if (process.server) return []
    try {
      const data = localStorage.getItem(HISTORY_KEY)
      return data ? JSON.parse(data) : []
    } catch {
      return []
    }
  }

  // 获取播放记录（根据登录状态自动选择来源）
  const getHistory = async (): Promise<PlayHistory[]> => {
    if (isLoggedIn()) {
      // 已登录，从API获取
      return await getHistoryFromApi()
    } else {
      // 未登录，从本地获取
      return getHistoryFromLocal()
    }
  }

  // 同步本地记录到云端（登录后调用）
  const syncLocalToCloud = async (): Promise<void> => {
    const accesstoken = getAccessToken()
    if (!accesstoken) return

    const localHistory = getHistoryFromLocal()
    if (localHistory.length === 0) return

    // 逐个将本地记录同步到云端
    // 调用 /web/content/movie/{movie_id}/count 接口
    for (const item of localHistory) {
      try {
        await $fetch(`${baseUrl}/web/movies/${item.id}/count`, {
          method: 'POST',
          headers: getAuthHeaders()
        })
      } catch (error) {
        console.debug('同步播放记录到云端失败:', error)
      }
    }
  }

  // 添加播放记录到本地
  const addHistoryToLocal = (item: Omit<PlayHistory, 'timestamp'>) => {
    if (process.server) return
    try {
      const history = getHistoryFromLocal()
      // 移除重复项
      const filtered = history.filter(h => h.id !== item.id)
      // 添加新记录到开头
      filtered.unshift({
        ...item,
        timestamp: Date.now()
      })
      // 只保留最近5条
      const limited = filtered.slice(0, MAX_HISTORY)
      localStorage.setItem(HISTORY_KEY, JSON.stringify(limited))
    } catch (error) {
      console.error('保存播放记录到本地失败:', error)
    }
  }

  // 添加播放记录到API
  // 调用 /web/content/movie/{movie_id}/count 接口，不传 recommend 参数表示观看+1
  const addHistoryToApi = async (item: Omit<PlayHistory, 'timestamp'>) => {
    const accesstoken = getAccessToken()
    if (!accesstoken) return

    try {
      await $fetch(`${baseUrl}/web/content/movie/${item.id}/count`, {
        method: 'POST',
        headers: getAuthHeaders()
      })
    } catch (error) {
      console.error('保存播放记录到API失败:', error)
    }
  }

  // 防抖记录：同一影片 5 秒内不重复记录
  const recentRecords = new Map<string, number>()
  const DEBOUNCE_TIME = 5000 // 5 秒

  // 添加播放记录（根据登录状态自动选择存储位置，带防抖）
  const addHistory = (item: Omit<PlayHistory, 'timestamp'>) => {
    const now = Date.now()
    const lastRecord = recentRecords.get(item.id)

    // 如果 5 秒内已记录过同一影片，则跳过
    if (lastRecord && now - lastRecord < DEBOUNCE_TIME) {
      return
    }

    // 更新记录时间
    recentRecords.set(item.id, now)

    // 清理过期的记录（避免内存泄漏）
    for (const [id, timestamp] of recentRecords.entries()) {
      if (now - timestamp > DEBOUNCE_TIME) {
        recentRecords.delete(id)
      }
    }

    if (isLoggedIn()) {
      // 已登录，记录到API
      addHistoryToApi(item)
    } else {
      // 未登录，记录到本地
      addHistoryToLocal(item)
    }
  }

  // 清空本地播放记录
  const clearLocalHistory = () => {
    if (process.server) return
    try {
      localStorage.removeItem(HISTORY_KEY)
    } catch (error) {
      console.error('清除本地播放记录失败:', error)
    }
  }

  // 清空API播放记录
  const clearApiHistory = async (): Promise<boolean> => {
    const accesstoken = getAccessToken()
    if (!accesstoken) return false

    try {
      const response = await $fetch<{
        code: number
      }>(`${baseUrl}/web/history/watch-history/all`, {
        method: 'DELETE',
        query: { accesstoken },
        headers: getAuthHeaders()
      })

      return response.code === 200
    } catch (error) {
      console.error('清除API播放记录失败:', error)
      return false
    }
  }

  // 清除播放记录（同时清除本地和云端，如果登录了）
  const clearHistory = async (): Promise<void> => {
    // 总是清空本地记录
    clearLocalHistory()

    // 如果已登录，同时清空云端记录
    if (isLoggedIn()) {
      await clearApiHistory()
    }
  }

  // 删除单条播放记录（根据movie_id）
  const removeHistoryItem = async (movieId: string): Promise<void> => {
    // 从本地删除
    if (process.server) return
    try {
      const history = getHistoryFromLocal()
      const filtered = history.filter(h => h.id !== movieId)
      localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered))
    } catch (error) {
      console.error('删除本地播放记录失败:', error)
    }

    // 如果已登录，同时从API删除
    if (isLoggedIn()) {
      const accesstoken = getAccessToken()
      if (!accesstoken) return

      try {
        await $fetch(`${baseUrl}/web/history/watch-history/${movieId}`, {
          method: 'DELETE',
          query: { accesstoken },
          headers: getAuthHeaders()
        })
      } catch (error) {
        console.error('删除API播放记录失败:', error)
      }
    }
  }

  return {
    getHistory,
    addHistory,
    clearHistory,
    removeHistoryItem,
    syncLocalToCloud,
    isLoggedIn
  }
}
