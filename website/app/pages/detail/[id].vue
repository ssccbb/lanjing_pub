<template>
  <div>
    <!-- 301重定向到播放页 -->
    <p class="text-center py-20 text-gray-500">页面已迁移...</p>
  </div>
</template>

<script setup lang="ts">
/**
 * 旧版详情页 - 301重定向到播放页
 * 保持SEO权重传递
 */
const route = useRoute()
const { getMovieDetail } = useMovies()

const id = route.params.id as string

// 获取影片信息以构建slug
onMounted(async () => {
  const movie = await getMovieDetail(id)
  if (movie) {
    const slug = generateMovieSlug(id, movie.title)
    // 301重定向到播放页
    await navigateTo(routes.stream(slug), { redirectCode: 301, replace: true })
  } else {
    // 影片不存在，跳转到首页
    await navigateTo('/', { replace: true })
  }
})
</script>
