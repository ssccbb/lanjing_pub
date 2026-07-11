<template>
  <div>
    <!-- 301重定向到新的cels路由 -->
    <p class="text-center py-20 text-gray-500">页面已迁移...</p>
  </div>
</template>

<script setup lang="ts">
/**
 * 旧版动漫列表页 - 301重定向到新版语义化路由
 */
onMounted(async () => {
  await navigateTo('/cels', { redirectCode: 301, replace: true })
})
</script>
