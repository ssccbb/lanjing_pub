// 处理浏览器插件发出的 /SDK/* 请求，避免 Vue Router 警告
export default defineEventHandler((event) => {
  const url = getRequestURL(event)
  if (url.pathname.startsWith('/SDK/')) {
    // 返回空响应，阻止路由警告
    event.respondWith(new Response('', { status: 204 }))
  }
})
