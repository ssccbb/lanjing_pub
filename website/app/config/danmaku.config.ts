/**
 * 弹幕相关配置
 */

// 弹幕提醒文案 - 当当前时间段内没有弹幕时随机显示
export const DANMAKU_REMINDER_MESSAGES = [
  'your_danmaku_reminder_message_here',
]

// 获取随机弹幕提醒文案
export function getRandomReminderMessage(): string {
  const index = Math.floor(Math.random() * DANMAKU_REMINDER_MESSAGES.length)
  return DANMAKU_REMINDER_MESSAGES[index]
}
