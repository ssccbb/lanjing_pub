import type { H3Event } from 'h3'

// 允许的图片域名白名单
const ALLOWED_IMAGE_DOMAINS = [
  'img.xhscdn.com',
  'img.scpo.cn',
  'i0.hdslb.com',
  'i1.hdslb.com',
  'i2.hdslb.com',
  'p1.meituan.net',
  'p0.meituan.net',
  'img.meituan.net',
  'pic.rmb.bdstatic.com',
  'img.woobest.cn',
]

// 检查 URL 是否在白名单中
function isAllowedImageUrl(url: string): boolean {
  try {
    const urlObj = new URL(url)
    return ALLOWED_IMAGE_DOMAINS.some(domain =>
      urlObj.hostname === domain || urlObj.hostname.endsWith('.' + domain)
    )
  } catch {
    return false
  }
}

export default defineEventHandler(async (event: H3Event) => {
  const query = getQuery(event)
  const url = query.url as string

  if (!url) {
    throw createError({
      statusCode: 400,
      statusMessage: 'URL is required'
    })
  }

  // 检查 URL 是否在白名单中（防止 SSRF）
  if (!isAllowedImageUrl(url)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Domain not allowed'
    })
  }

  try {
    // Fetch the image
    const response = await $fetch.raw(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      },
      responseType: 'arrayBuffer'
    })

    // Get content type from response
    const contentType = response.headers.get('content-type') || 'image/jpeg'

    // Set response headers
    setResponseHeader(event, 'Content-Type', contentType)
    setResponseHeader(event, 'Cache-Control', 'public, max-age=86400')

    // Return the image data
    return response._data
  } catch (error) {
    console.error('Image proxy error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch image'
    })
  }
})