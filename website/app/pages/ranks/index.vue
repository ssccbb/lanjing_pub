<template>
  <div>
    <!-- 301重定向到新的tiers路由 -->
    <p class="text-center py-20 text-gray-500">页面已迁移...</p>
  </div>
</template>

<script setup lang="ts">
/**
 * 旧版排行榜页 - 301重定向到新版语义化路由
 */
onMounted(async () => {
  await navigateTo('/tiers', { redirectCode: 301, replace: true })
})
</script>
