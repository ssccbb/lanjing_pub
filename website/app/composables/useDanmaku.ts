import type { DanmakuItem } from '~/components/player/DanmakuLayer.vue'
import { getAuthHeaders } from './useSignedFetch'

export interface UseDanmakuOptions {
  videoId: string | number
  immediate?: boolean
}

// 统一API响应格式
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 弹幕列表响应数据
interface DanmakuListData {
  items: DanmakuItem[]
  pagination: {
    hasMore: boolean
    nextCursor?: string
    total?: number
  }
}

// 发送弹幕响应数据
interface SendDanmakuData {
  id: string
  timestamp: number
  color?: string  // 后端根据角色返回的颜色
}

// 点赞弹幕响应数据
interface LikeDanmakuData {
  likes: number
  isLiked: boolean
}

/**
 * 弹幕数据管理 Composable
 * 对接后端 API 格式（统一使用 Response 包装格式）
 */
export function useDanmaku(options: UseDanmakuOptions) {
  const { videoId, immediate = true } = options
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  const items = ref<DanmakuItem[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const enabled = ref(true)

  // 获取当前存储的 accesstoken
  const getAccessToken = (): string | null => {
    if (!process.client) return null
    const localToken = localStorage.getItem('accesstoken')
    if (localToken) return localToken
    return sessionStorage.getItem('accesstoken_session')
  }

  /**
   * 从服务器加载弹幕列表
   * 公开接口，不需要签名和登录
   */
  async function loadDanmaku(startTime?: number, endTime?: number) {
    if (!videoId) return

    loading.value = true
    error.value = null

    try {
      // 调用后端 API
      const query = new URLSearchParams()
      if (startTime !== undefined) query.append('startTime', String(startTime))
      if (endTime !== undefined) query.append('endTime', String(endTime))

      const response = await $fetch<ApiResponse<DanmakuListData>>(
        `${baseUrl}/pub/danmaku/${videoId}?${query}`
      )

      if (response.code === 200 && response.data) {
        items.value = response.data.items || []
      } else {
        console.error('[Danmaku] 加载失败:', response.message)
        items.value = []
      }
    } catch (err) {
      error.value = err as Error
      console.error('[Danmaku] 加载失败:', err)
      items.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 发送弹幕
   * 需要签名和用户登录
   * @param isPlaying 是否正在播放，如果为true则立即在本地显示弹幕
   */
  async function sendDanmaku(
    text: string,
    time: number,
    color?: string,
    mode: DanmakuItem['mode'] = 'scroll',
    isPlaying: boolean = false
  ) {
    if (!text.trim()) return

    // 检查是否已登录
    const accesstoken = getAccessToken()
    if (!accesstoken) {
      throw new Error('请先登录后再发送弹幕')
    }

    // 生成临时ID用于实时显示
    const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // 创建弹幕项
    const newItem: DanmakuItem = {
      id: tempId,
      text: text.trim(),
      time,
      mode,
      color,
    }

    // 如果正在播放，立即添加到列表显示（实时效果）
    if (isPlaying) {
      items.value.push(newItem)
    }

    try {
      const response = await $fetch<ApiResponse<SendDanmakuData>>(
        `${baseUrl}/web/danmaku/${videoId}`,
        {
          method: 'POST',
          body: {
            text: text.trim(),
            time,
            mode,
            color,
            clientType: 'web',
          },
          headers: getAuthHeaders()
        }
      )

      if (response.code === 200 && response.data) {
        // 使用后端返回的颜色（根据用户角色确定）
        const finalColor = response.data.color || color

        // 更新为服务器返回的真实ID和颜色
        const index = items.value.findIndex(i => i.id === tempId)
        if (index !== -1) {
          items.value[index] = {
            ...newItem,
            id: response.data.id,
            color: finalColor
          }
        } else if (!isPlaying) {
          // 如果没有实时显示，现在添加到列表
          items.value.push({
            ...newItem,
            id: response.data.id,
            color: finalColor
          })
        }
        return { ...newItem, id: response.data.id, color: finalColor }
      }

      // 发送失败，移除临时弹幕（如果已显示）
      if (isPlaying) {
        items.value = items.value.filter(i => i.id !== tempId)
      }
      throw new Error(response.message || '发送失败')
    } catch (err: any) {
      // 发送失败，移除临时弹幕（如果已显示）
      if (isPlaying) {
        items.value = items.value.filter(i => i.id !== tempId)
      }
      console.error('[Danmaku] 发送失败:', err)
      throw new Error(err?.data?.message || err.message || '发送失败')
    }
  }

  /**
   * 点赞弹幕
   * 需要签名和用户登录
   */
  async function likeDanmaku(danmakuId: string) {
    // 检查是否已登录
    const accesstoken = getAccessToken()
    if (!accesstoken) {
      throw new Error('请先登录后再点赞')
    }

    try {
      const response = await $fetch<ApiResponse<LikeDanmakuData>>(
        `${baseUrl}/web/danmaku/${danmakuId}/like`,
        {
          method: 'POST',
          headers: getAuthHeaders()
        }
      )

      if (response.code === 200 && response.data) {
        const item = items.value.find(i => i.id === danmakuId)
        if (item) {
          item.likes = response.data.likes
        }
        return response.data
      }

      throw new Error(response.message || '点赞失败')
    } catch (err: any) {
      console.error('[Danmaku] 点赞失败:', err)
      throw new Error(err?.data?.message || err.message || '点赞失败')
    }
  }

  function toggleDanmaku() {
    enabled.value = !enabled.value
  }

  function clearDanmaku() {
    items.value = []
  }

  if (immediate) {
    onMounted(() => loadDanmaku())
  }

  return {
    items,
    loading,
    error,
    enabled,
    loadDanmaku,
    sendDanmaku,
    likeDanmaku,
    toggleDanmaku,
    clearDanmaku,
  }
}

export type UseDanmakuReturn = ReturnType<typeof useDanmaku>
