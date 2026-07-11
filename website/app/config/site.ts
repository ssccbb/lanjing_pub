// 站点配置文件
// 所有配置项从运行时配置读取，配置来源：website/.env 和 .env.shared

import type { RuntimeConfig } from 'nuxt/schema'

// 创建站点配置对象（从运行时配置获取值）
export function createSiteConfig(config: RuntimeConfig) {
  return {
    // 应用品牌
    brand: {
      name: config.public.appName,
      slogan: config.public.appSlogan,
      subSlogan: config.public.appSubSlogan,
    },

    // 协议页面
    policy: {
      agreement: config.public.policyAgreement,
      privacy: config.public.policyPrivacy,
    },

    // 联系方式
    contact: {
      email: config.public.contactEmail,
    },

    // 备案号
    icpNumber: config.public.icpNumber,

    // 第三方分享服务（固定URL）
    share: {
      weibo: 'https://service.weibo.com/share/share.php',
      qq: 'https://connect.qq.com/widget/shareqq/index.html',
    },
  }
}

// 便捷函数：获取站点配置
export function useSiteConfig() {
  const config = useRuntimeConfig()
  return createSiteConfig(config)
}