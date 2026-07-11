// 分享功能组合函数
import { useSiteConfig } from '~/config/site'

export interface ShareOptions {
  title: string
  text?: string
  url: string
}

export const useShare = () => {
  const siteConfig = useSiteConfig()

  // 检测是否支持原生分享
  const isNativeShareSupported = (): boolean => {
    return typeof navigator !== 'undefined' && !!navigator.share
  }

  // 原生分享（移动端优先）
  const nativeShare = async (options: ShareOptions): Promise<boolean> => {
    if (!isNativeShareSupported()) return false

    try {
      await navigator.share(options)
      return true
    } catch (err) {
      // 用户取消或分享失败
      return false
    }
  }

  // 复制到剪贴板
  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch (err) {
      // 降级方案
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      const result = document.execCommand('copy')
      document.body.removeChild(textarea)
      return result
    }
  }

  // 分享到微博
  const shareToWeibo = (options: ShareOptions) => {
    const url = `${siteConfig.share.weibo}?url=${encodeURIComponent(options.url)}&title=${encodeURIComponent(options.text || options.title)}`
    window.open(url, '_blank', 'width=600,height=500,scrollbars=yes')
  }

  // 分享到QQ
  const shareToQQ = (options: ShareOptions) => {
    const url = `${siteConfig.share.qq}?url=${encodeURIComponent(options.url)}&title=${encodeURIComponent(options.title)}&summary=${encodeURIComponent(options.text || '')}`
    window.open(url, '_blank', 'width=600,height=500,scrollbars=yes')
  }

  // 生成分享链接
  const generateShareUrl = (path: string): string => {
    if (typeof window === 'undefined') return ''
    return `${window.location.origin}${path}`
  }

  return {
    isNativeShareSupported,
    nativeShare,
    copyToClipboard,
    shareToWeibo,
    shareToQQ,
    generateShareUrl
  }
}
