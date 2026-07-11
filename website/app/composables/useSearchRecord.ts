/**
 * 搜索记录上报
 * 用于异步上报搜索结果到服务端，不阻塞用户操作
 */

export const useSearchRecord = () => {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  /**
   * 记录搜索历史
   * @param seriesTitles 影片名称列表 ["影片名1", "影片名2"]
   * @returns Promise
   */
  const recordSearchHistory = async (seriesTitles: string[]): Promise<void> => {
    if (!seriesTitles || seriesTitles.length === 0) return

    try {
      await $fetch(`${baseUrl}/web/search/record`, {
        method: 'POST',
        body: seriesTitles,
        headers: getAuthHeaders()
      })
    } catch (error) {
      // 静默失败，不影响用户体验
      console.debug('[Search Record] 上报失败:', error)
    }
  }

  /**
   * 获取热门搜索记录（从搜索统计表）
   * @param limit 数量限制
   * @returns 热门搜索列表
   */
  const getHotSearchRecords = async (limit: number = 10): Promise<SearchMovie[]> => {
    try {
      const response = await $fetch(`${baseUrl}/web/search/hot-records`, {
        query: { limit },
        headers: getAuthHeaders()
      })

      if (response?.code === 200 && response.data?.list) {
        return response.data.list.map((item: any) => ({
          id: String(item.id),
          name: item.series_title
        }))
      }
      return []
    } catch (error) {
      console.error('[Search Record] 获取热门搜索失败:', error)
      return []
    }
  }

  return {
    recordSearchHistory,
    getHotSearchRecords
  }
}
