/**
 * 密码验证工具函数
 */

// 允许的字符正则：大小写字母 + 数字 + 英文常用标点
const ALLOWED_CHARS_REGEX = /^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:',.<>?\/`~]+$/

// 英文常用标点集合
const PUNCTUATION_CHARS = '!@#$%^&*()_+-=[]{}|;\':",.<>?/`~'

/**
 * 校验密码字符是否合法（只包含允许的字符）
 * @param password 密码字符串
 * @returns true 表示只包含允许的字符
 */
export function validatePasswordChars(password: string): boolean {
  if (!password) return false
  return ALLOWED_CHARS_REGEX.test(password)
}

/**
 * 校验密码规则：必须大于8位且包含数字
 * @param password 密码字符串
 * @returns { valid: boolean, message: string }
 */
export function validatePasswordRule(password: string): { valid: boolean; message: string } {
  if (!password) {
    return { valid: false, message: '请输入密码' }
  }

  if (password.length <= 8) {
    return { valid: false, message: '密码长度必须大于8位' }
  }

  const hasNumber = /[0-9]/.test(password)
  if (!hasNumber) {
    return { valid: false, message: '密码必须包含数字' }
  }

  return { valid: true, message: '' }
}

/**
 * 计算密码强度
 * @param password 密码字符串
 * @returns 'weak' | 'medium' | 'strong'
 *
 * 规则：
 * - weak: 长度 ≤ 8 或 不包含数字
 * - medium: 长度 > 8 且 包含数字 且 (只有数字 或 只有字母)
 * - strong: 长度 > 8 且 包含数字 且 同时含大小写字母
 */
export function getPasswordStrength(password: string): 'weak' | 'medium' | 'strong' {
  if (!password) return 'weak'

  const hasNumber = /[0-9]/.test(password)
  const hasLowercase = /[a-z]/.test(password)
  const hasUppercase = /[A-Z]/.test(password)

  // 弱：长度 ≤ 8 或 不包含数字
  if (password.length <= 8 || !hasNumber) {
    return 'weak'
  }

  // 强：长度 > 8 且 包含数字 且 同时含大小写字母
  if (hasLowercase && hasUppercase) {
    return 'strong'
  }

  // 中：长度 > 8 且 包含数字 且 (只有数字 或 只有单一大小写字母)
  return 'medium'
}