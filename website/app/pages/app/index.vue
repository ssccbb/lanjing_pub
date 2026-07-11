<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <!-- App Logo -->
      <div class="mx-auto mb-6">
        <span class="text-3xl font-bold text-blue-400">影视模版</span>
      </div>
      <p class="text-gray-500 mb-6">正在前往下载页面...</p>

      <!-- Loading -->
      <el-icon :size="32" class="text-app-primary is-loading"><Loading /></el-icon>

      <!-- Manual Link -->
      <p class="mt-6 text-sm text-gray-400">
        如果没有自动跳转，请
        <NuxtLink to="/download" class="text-app-primary hover:underline">点击这里</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'

usePageSeo('下载APP')

// 自动跳转
onMounted(() => {
  setTimeout(() => {
    navigateTo('/download')
  }, 1500)
})
</script>
