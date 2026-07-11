/**
 * slug生成与解析工具
 * 将影片ID转换为语义化slug，增强URL可读性同时保持隐蔽性
 */

// 特殊字符映射表（用于增加混淆性）
const charMap: Record<string, string> = {
  '0': 'x', '1': 'y', '2': 'z', '3': 'a',
  '4': 'b', '5': 'c', '6': 'd', '7': 'e',
  '8': 'f', '9': 'g'
}

const reverseCharMap: Record<string, string> = {
  'x': '0', 'y': '1', 'z': '2', 'a': '3',
  'b': '4', 'c': '5', 'd': '6', 'e': '7',
  'f': '8', 'g': '9'
}

/**
 * 将ID编码为混淆字符串
 * 例如: "123" -> "yza"
 */
export const encodeId = (id: string | number): string => {
  return String(id).split('').map(c => charMap[c] || c).join('')
}

/**
 * 将混淆字符串解码为ID
 * 例如: "yza" -> "123"
 */
export const decodeId = (encoded: string): string => {
  return encoded.split('').map(c => reverseCharMap[c] || c).join('')
}

/**
 * 生成影片的语义化slug
 * 格式: {encodedId}-{title-slug}
 * 例如: "xyz-the-matrix-1999"
 */
export const generateMovieSlug = (id: string | number, title: string): string => {
  const encodedId = encodeId(id)
  const titleSlug = title
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // 移除非字母数字字符
    .replace(/\s+/g, '-')      // 空格替换为连字符
    .replace(/-+/g, '-')       // 多个连字符合并
    .substring(0, 50)          // 限制长度
  return `${encodedId}-${titleSlug}`
}

/**
 * 从slug中提取ID
 * 例如: "xyz-the-matrix-1999" -> "123"
 */
export const extractIdFromSlug = (slug: string): string => {
  const parts = slug.split('-')
  if (parts.length === 0) return ''
  return decodeId(parts[0])
}

/**
 * 路由路径生成器
 * 所有路径使用隐蔽的语义化词汇
 */
export const routes = {
  // 播放页 - stream: 流媒体
  stream: (slug: string, query?: { source?: number; episode?: number }) => {
    const params = new URLSearchParams()
    if (query?.source !== undefined) params.set('src', String(query.source))
    if (query?.episode !== undefined) params.set('ep', String(query.episode))
    const queryStr = params.toString()
    return `/stream/${slug}${queryStr ? '?' + queryStr : ''}`
  },

  // 电影列表 - reels: 胶片卷轴
  reels: () => '/reels',

  // 动漫列表 - cels: 动画胶片
  cels: () => '/cels',

  // 排行榜 - tiers: 层级
  tiers: () => '/tiers',

  // 下载页 - acquire: 获取
  acquire: () => '/acquire',

  // 反馈页 - echo: 回响
  echo: () => '/echo',

  // 搜索 - query: 查询
  query: (keyword?: string) => keyword ? `/query?q=${encodeURIComponent(keyword)}` : '/query',

  // 首页
  home: () => '/'
} as const

/**
 * 解析stream页面参数
 * 新参数名: src (source), ep (episode)
 */
export const parseStreamParams = (query: Record<string, unknown>) => {
  return {
    source: parseInt(query.src as string) || 0,
    episode: parseInt(query.ep as string) || 0
  }
}

/**
 * 构建stream页面查询参数（用于URL）
 */
export const buildStreamQuery = (source?: number, episode?: number): string => {
  const params = new URLSearchParams()
  if (source !== undefined) params.set('src', String(source))
  if (episode !== undefined) params.set('ep', String(episode))
  return params.toString()
}

/**
 * 获取播放页的完整slug和查询参数
 */
export const getStreamUrl = (
  movie: { id: string | number; title: string },
  options?: { source?: number; episode?: number }
): string => {
  const slug = generateMovieSlug(movie.id, movie.title)
  return routes.stream(slug, options)
}
