// SEO 相关的 composable
// 统一处理页面标题和描述，自动添加品牌名称

import { useSiteConfig } from '~/config/site'

/**
 * 设置页面 SEO 信息
 * @param title 页面标题（不含品牌名称）
 * @param description 页面描述（可选，会自动添加品牌信息）
 */
export function usePageSeo(title: string, description?: string) {
  const siteConfig = useSiteConfig()
  const brandName = siteConfig.brand.name
  const slogan = siteConfig.brand.slogan

  const fullTitle = title ? `${title} - ${brandName}` : `${brandName} - ${slogan}`
  const fullDescription = description
    ? `${brandName} - ${description}`
    : `${brandName} - ${slogan}，海量高清影视资源在线观看`

  useHead({
    title: fullTitle,
    meta: description ? [{ name: 'description', content: fullDescription }] : []
  })
}

/**
 * 获取品牌名称
 */
export function useBrandName() {
  const siteConfig = useSiteConfig()
  return siteConfig.brand.name
}

/**
 * 获取品牌标语
 */
export function useBrandSlogan() {
  const siteConfig = useSiteConfig()
  return siteConfig.brand.slogan
}

/**
 * 获取品牌副标语
 */
export function useBrandSubSlogan() {
  const siteConfig = useSiteConfig()
  return siteConfig.brand.subSlogan
}
