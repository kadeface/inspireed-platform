/**
 * 格式化工具函数
 *
 * 用于格式化时间、时长等数据
 */

/**
 * 格式化时长（秒转分钟）
 * @param seconds - 秒数
 * @returns 格式化后的时长字符串，如 "15分钟"
 */
export function formatDuration(seconds: number): string {
  if (seconds <= 0) return '0分钟'
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟`
}

/**
 * 格式化剩余时间（秒转 MM:SS 格式）
 * @param seconds - 秒数
 * @returns 格式化后的时间字符串，如 "25:30"
 */
export function formatRemainingTime(seconds: number): string {
  if (seconds <= 0) return '0:00'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

/**
 * 格式化课程时长（秒转小时和分钟）
 * @param seconds - 秒数
 * @returns 格式化后的时长字符串，如 "1小时30分钟" 或 "45分钟"
 */
export function formatLessonDuration(seconds: number): string {
  if (seconds <= 0) return '0分钟'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
  }
  return `${minutes}分钟`
}

/**
 * 格式化时间戳为可读时间
 * @param timestamp - 时间戳（秒或毫秒）
 * @returns 格式化后的时间字符串，如 "14:30" 或 "2024-01-01 14:30"
 */
export function formatTimestamp(timestamp: number, includeDate: boolean = false): string {
  const date = new Date(timestamp < 10000000000 ? timestamp * 1000 : timestamp)

  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')

  if (includeDate) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  }

  return `${hours}:${minutes}`
}

/**
 * 格式化百分比
 * @param value - 数值（0-1或0-100）
 * @param isDecimal - 是否为小数形式（0-1）
 * @returns 格式化后的百分比字符串，如 "75%"
 */
export function formatPercentage(value: number, isDecimal: boolean = true): string {
  const percentage = isDecimal ? value * 100 : value
  return `${Math.round(percentage)}%`
}

/**
 * 格式化数字为千分位格式
 * @param num - 数字
 * @returns 格式化后的字符串，如 "1,234"
 */
export function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化文件大小
 * @param bytes - 字节数
 * @returns 格式化后的文件大小，如 "1.5 MB" 或 "500 KB"
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

/**
 * 截断文本并添加省略号
 * @param text - 原始文本
 * @param maxLength - 最大长度
 * @returns 截断后的文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
