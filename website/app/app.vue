<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import { useSiteConfig } from '~/config/site'

const siteConfig = useSiteConfig()

// 全局配置
useHead({
  title: `${siteConfig.brand.name} - ${siteConfig.brand.slogan}`,
  bodyAttrs: {
    class: 'bg-app-bg text-gray-100'
  },
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
    { name: 'description', content: `${siteConfig.brand.name} - ${siteConfig.brand.slogan}，海量高清影视资源在线观看` }
  ]
})
</script>

<style>
/* 全局样式 */
html {
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 图片懒加载占位 */
img[data-loading="true"] {
  background: linear-gradient(110deg, #000000 8%, #333333 18%, #000000 33%);
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}

@keyframes shimmer {
  to {
    background-position-x: -200%;
  }
}

/* 文字省略 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
