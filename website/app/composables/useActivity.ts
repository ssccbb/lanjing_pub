import { getAuthHeaders } from './useSignedFetch'

export const useActivity = () => {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  /**
   * 记录页面访问
   * 只在用户已登录时调用
   */
  const recordPageVisit = async (path: string): Promise<void> => {
    // 只在客户端执行
    if (process.server) return

    // 检查是否有登录 token（优先 localStorage，其次 sessionStorage）
    let accesstoken = localStorage.getItem('accesstoken')
    if (!accesstoken) {
      accesstoken = sessionStorage.getItem('accesstoken_session')
    }
    if (!accesstoken) return

    try {
      await $fetch(`${baseUrl}/web/history/visit`, {
        method: 'POST',
        body: { path },
        headers: {
          ...getAuthHeaders(),
          'Authorization': `Bearer ${accesstoken}`
        }
      })
    } catch (error) {
      // 静默失败，不影响用户体验
      console.debug('记录页面访问失败:', error)
    }
  }

  return {
    recordPageVisit
  }
}
