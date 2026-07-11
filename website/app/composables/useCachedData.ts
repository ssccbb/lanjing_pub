// 带缓存的数据获取
export const useCachedData = <T>(
  key: string,
  fetcher: () => Promise<T>,
  options: { expire?: number; server?: boolean; lazy?: boolean } = {}
) => {
  const { expire = 300, server = true, lazy = false } = options

  return useAsyncData(
    key,
    async () => {
      return await fetcher()
    },
    {
      server,
      lazy,
      default: () => null as T | null,
      // 客户端导航时从 payload 恢复
      getCachedData: (key) => {
        const nuxtApp = useNuxtApp()
        return nuxtApp.payload.data[key] as T | undefined
      }
    }
  )
}
