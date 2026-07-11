// 处理图片 URL
export const useImageProxy = () => {
  const getProxiedImageUrl = (url: string): string => {
    if (!url) return ''
    return url
  }

  // 从 covers 数组中获取最佳封面
  const getBestCover = (covers: string[] = [], fallbackCover: string = ''): string => {
    return covers.find(url => url) || fallbackCover || ''
  }

  return {
    getProxiedImageUrl,
    getBestCover
  }
}