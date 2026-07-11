<template>
  <div>
    <!-- 301重定向到新的query路由 -->
    <p class="text-center py-20 text-gray-500">页面已迁移...</p>
  </div>
</template>

<script setup lang="ts">
/**
 * 旧版搜索页 - 301重定向到新版语义化路由
 */
const route = useRoute()

onMounted(async () => {
  const query = route.query.q ? `?q=${encodeURIComponent(route.query.q as string)}` : ''
  await navigateTo(`/query${query}`, { redirectCode: 301, replace: true })
})
</script>
