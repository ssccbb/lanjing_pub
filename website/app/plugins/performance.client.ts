/**
 * 性能监控插件
 * 记录页面切换的各个阶段耗时
 */

interface PerformanceMetrics {
  route: string
  navigationStart: number
  fetchStart: number
  fetchEnd: number
  renderStart: number
  renderEnd: number
  totalTime: number
  fetchTime: number
  renderTime: number
}

// 存储当前页面的性能数据
let currentMetrics: Partial<PerformanceMetrics> = {}

export default defineNuxtPlugin((nuxtApp) => {
  // 只在客户端执行
  if (process.server) return

  // 页面开始加载
  nuxtApp.hook('page:start', () => {
    currentMetrics = {
      navigationStart: performance.now()
    }
  })

  // 页面挂载前（数据已获取）
  nuxtApp.hook('page:mount', () => {
    if (currentMetrics.navigationStart) {
      currentMetrics.fetchEnd = performance.now()
      currentMetrics.fetchTime = currentMetrics.fetchEnd - currentMetrics.navigationStart
      currentMetrics.renderStart = currentMetrics.fetchEnd
    }
  })

  // 页面完成挂载
  nuxtApp.hook('page:finish', () => {
    if (currentMetrics.navigationStart) {
      const now = performance.now()
      const route = useRoute().path

      const metrics: PerformanceMetrics = {
        route,
        navigationStart: currentMetrics.navigationStart,
        fetchStart: currentMetrics.navigationStart,
        fetchEnd: currentMetrics.fetchEnd || now,
        renderStart: currentMetrics.renderStart || now,
        renderEnd: now,
        totalTime: now - currentMetrics.navigationStart,
        fetchTime: currentMetrics.fetchTime || 0,
        renderTime: now - (currentMetrics.renderStart || now)
      }

      // 存储到全局状态供调试使用
      const perfHistory = useState<PerformanceMetrics[]>('performance-history', () => [])
      perfHistory.value.unshift(metrics)
      // 只保留最近20条
      if (perfHistory.value.length > 20) {
        perfHistory.value = perfHistory.value.slice(0, 20)
      }
    }
  })
})
