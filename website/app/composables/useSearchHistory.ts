// 搜索历史管理 - 使用 localStorage
export interface SearchHistoryItem {
  keyword: string
  timestamp: number
}

const SEARCH_HISTORY_KEY = 'app_search_history'
const MAX_HISTORY = 10

export const useSearchHistory = () => {
  // 获取搜索历史
  const getSearchHistory = (): SearchHistoryItem[] => {
    if (process.server) return []
    try {
      const data = localStorage.getItem(SEARCH_HISTORY_KEY)
      return data ? JSON.parse(data) : []
    } catch {
      return []
    }
  }

  // 添加搜索历史
  const addSearchHistory = (keyword: string) => {
    if (process.server) return
    try {
      const trimmed = keyword.trim()
      if (!trimmed) return

      const history = getSearchHistory()
      // 移除重复项
      const filtered = history.filter(h => h.keyword !== trimmed)
      // 添加新记录到开头
      filtered.unshift({
        keyword: trimmed,
        timestamp: Date.now()
      })
      // 只保留最近10条
      const limited = filtered.slice(0, MAX_HISTORY)
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(limited))
    } catch (error) {
      console.error('保存搜索历史失败:', error)
    }
  }

  // 删除单条搜索历史
  const removeSearchHistory = (keyword: string) => {
    if (process.server) return
    try {
      const history = getSearchHistory()
      const filtered = history.filter(h => h.keyword !== keyword)
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(filtered))
    } catch (error) {
      console.error('删除搜索历史失败:', error)
    }
  }

  // 清除搜索历史
  const clearSearchHistory = () => {
    if (process.server) return
    try {
      localStorage.removeItem(SEARCH_HISTORY_KEY)
    } catch (error) {
      console.error('清除搜索历史失败:', error)
    }
  }

  return {
    getSearchHistory,
    addSearchHistory,
    removeSearchHistory,
    clearSearchHistory
  }
}
