<template>
  <div>
    <!-- 301重定向到新的stream路由 -->
    <p class="text-center py-20 text-gray-500">页面已迁移...</p>
  </div>
</template>

<script setup lang="ts">
/**
 * 旧版播放页 - 301重定向到新版语义化路由
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
    // 保留原有查询参数（播放源和集数）
    const source = route.query.source as string
    const episode = route.query.episode as string
    const query: { src?: string; ep?: string } = {}
    if (source) query.src = source
    if (episode) query.ep = episode

    const queryStr = new URLSearchParams(query).toString()
    const targetUrl = `/stream/${slug}${queryStr ? '?' + queryStr : ''}`

    // 301重定向到新的stream路由
    await navigateTo(targetUrl, { redirectCode: 301, replace: true })
  } else {
    await navigateTo('/', { replace: true })
  }
})
</script>
