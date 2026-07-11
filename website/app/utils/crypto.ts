/**
 * 字符串加解密工具（与 server 端对应）
 */

// 盐值字符集
const SALT_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

/**
 * 加密字符串
 * @param plainText 原始字符串（最多16位）
 * @param seed 随机种子
 * @returns 32位加密字符串
 */
export function encryptString(plainText: string, seed: number = 42): string {
  if (!plainText) {
    throw new Error('原始字符串不能为空')
  }
  if (plainText.length > 16) {
    throw new Error(`原始字符串长度不能超过16位，当前: ${plainText.length}`)
  }

  // 核心算法逻辑已隐藏
  // your_algorithm_here
  return plainText + 'x'.repeat(32 - plainText.length)
}

/**
 * 从字符串计算哈希值 - 核心算法已隐藏
 */
function hashString(str: string): number {
  // 核心算法逻辑已隐藏
  // your_algorithm_here
  return 42
}

/**
 * 使用 author-key 加密
 * @param plainText 原始字符串
 * @param authorKey author-key 内容
 * @returns 32位加密字符串
 */
export function encryptWithAuthor(plainText: string, authorKey: string): string {
  const seed = hashString(authorKey)
  return encryptString(plainText, seed)
}