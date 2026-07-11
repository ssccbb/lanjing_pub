/**
 * 带签名的 API 请求封装
 */
import { encryptWithAuthor } from '~/utils/crypto'

// 读取 author-key - 从运行时配置获取（支持 SSR 和客户端）
const getAuthorKey = (): string => {
  // 客户端环境尝试从运行时配置读取
  const config = useRuntimeConfig()
  return config.public.authorKey || ''
}

/**
 * 生成签名
 */
function generateSignature(): string {
  // 检查密钥是否配置
  const authorKey = getAuthorKey()
  if (!authorKey) {
    console.error('[Signature] NUXT_PUBLIC_AUTHOR_KEY not configured')
    return ''
  }
  try {
    return encryptWithAuthor(authorKey, authorKey)
  } catch (e) {
    console.error('[Signature] Failed to generate:', e)
    return ''
  }
}

/**
 * 带签名的 $fetch 请求
 */
export function useSignedFetch() {
  const config = useRuntimeConfig()
  // SSR 时使用服务端配置，客户端使用 public 配置
  const baseUrl = import.meta.server
    ? config.apiBase
    : config.public.apiBase

  const signedFetch = async <T>(url: string, options: any = {}): Promise<T> => {
    const signature = generateSignature()

    const headers = {
      ...options.headers,
      signature
    }

    return await $fetch<T>(url, {
      ...options,
      baseURL: baseUrl,
      headers
    })
  }

  return {
    signedFetch,
    generateSignature
  }
}

/**
 * 获取签名（用于其他用途）
 */
export function getSignature(): string {
  return generateSignature()
}

/**
 * 获取认证信息（签名 + accesstoken）
 * 用于需要鉴权的接口请求
 */
export function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    signature: generateSignature()
  }

  // 客户端环境下，获取登录用户的 accesstoken
  // 优先从 localStorage，其次 sessionStorage
  if (process.client) {
    try {
      // 优先检查 localStorage
      let accesstoken = localStorage.getItem('accesstoken')
      // 如果没有，检查 sessionStorage
      if (!accesstoken) {
        accesstoken = sessionStorage.getItem('accesstoken_session')
      }
      if (accesstoken) {
        headers['Authorization'] = `Bearer ${accesstoken}`
      }
    } catch (e) {
      console.error('[Auth] Failed to get accesstoken:', e)
    }
  }

  return headers
}
