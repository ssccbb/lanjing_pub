import { getAuthHeaders } from './useSignedFetch'

// 反馈/留言接口
export interface FeedbackData {
  content: string
  email?: string
  contact?: string
  feedback_type?: number  // 1=求片留言, 2=意见反馈, 3=问题报告
}

export const useFeedback = () => {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  // 提交反馈
  const submitFeedback = async (data: FeedbackData): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await $fetch<any>(`${baseUrl}/web/feedback/create`, {
        method: 'POST',
        body: {
          content: data.content,
          email: data.email || '',
          contact: data.contact || '',
          feedback_type: data.feedback_type || 1
        },
        headers: getAuthHeaders()
      })

      if (response?.code === 200) {
        return {
          success: true,
          message: response.data?.message || '提交成功'
        }
      }

      return {
        success: false,
        message: response?.message || '提交失败'
      }
    } catch (error: any) {
      console.error('提交反馈失败:', error)
      return {
        success: false,
        message: error?.data?.message || '网络错误，请稍后重试'
      }
    }
  }

  return {
    submitFeedback
  }
}
