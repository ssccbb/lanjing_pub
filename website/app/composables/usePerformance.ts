/**
 * 性能监控 Composable
 * 用于手动追踪特定操作的耗时
 */

interface Timer {
  name: string
  startTime: number
  endTime?: number
  duration?: number
}

interface PerformanceReport {
  name: string
  startTime: number
  endTime: number
  duration: number
  children: PerformanceReport[]
}

export const usePerformance = () => {
  const activeTimers = new Map<string, Timer>()
  const completedTimers: Timer[] = []

  // 开始计时
  const start = (name: string): string => {
    const id = `${name}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    activeTimers.set(id, {
      name,
      startTime: performance.now()
    })
    return id
  }

  // 结束计时
  const end = (id: string): number | null => {
    const timer = activeTimers.get(id)
    if (!timer) {
      return null
    }

    timer.endTime = performance.now()
    timer.duration = timer.endTime - timer.startTime

    activeTimers.delete(id)
    completedTimers.push(timer)

    return timer.duration
  }

  // 格式化时长
  const formatDuration = (ms: number): string => {
    if (ms < 1) return '<1ms'
    if (ms < 1000) return `${ms.toFixed(2)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  // 测量异步函数执行时间
  const measure = async <T>(name: string, fn: () => Promise<T>): Promise<T> => {
    const id = start(name)
    try {
      const result = await fn()
      end(id)
      return result
    } catch (error) {
      end(id)
      throw error
    }
  }

  // 获取所有已完成的计时器
  const getCompletedTimers = (): Timer[] => [...completedTimers]

  // 清除所有计时器
  const clear = () => {
    activeTimers.clear()
    completedTimers.length = 0
  }

  // 获取页面性能指标（Web Vitals）
  const getWebVitals = (): Record<string, number | undefined> => {
    if (typeof window === 'undefined') return {}

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    const paint = performance.getEntriesByType('paint')

    return {
      // DNS解析时间
      dns: navigation?.domainLookupEnd - navigation?.domainLookupStart,
      // TCP连接时间
      tcp: navigation?.connectEnd - navigation?.connectStart,
      // 首字节时间 (TTFB)
      ttfb: navigation?.responseStart - navigation?.startTime,
      // DOM解析时间
      domParse: navigation?.domContentLoadedEventEnd - navigation?.responseEnd,
      // 首屏渲染时间 (FCP)
      fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime,
      // 页面完全加载时间
      load: navigation?.loadEventEnd - navigation?.startTime
    }
  }

  return {
    start,
    end,
    measure,
    formatDuration,
    getCompletedTimers,
    clear,
    getWebVitals
  }
}
