<template>
  <div>
    <!-- 301重定向到新的echo路由 -->
    <p class="text-center py-20 text-gray-500">页面已迁移...</p>
  </div>
</template>

<script setup lang="ts">
/**
 * 旧版反馈页 - 301重定向到新版语义化路由
 */
onMounted(async () => {
  await navigateTo('/echo', { redirectCode: 301, replace: true })
})
</script>
