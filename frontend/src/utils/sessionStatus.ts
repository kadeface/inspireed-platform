/**
 * 课堂会话状态工具
 *
 * v2.0 状态枚举统一：
 * - 后端返回：大写（PREPARING, TEACHING, ENDED）
 * - 前端使用：小写（'preparing', 'teaching', 'ended'）
 */

/**
 * 标准化会话状态（大写 → 小写）
 */
export function normalizeSessionStatus(status: string): 'preparing' | 'teaching' | 'ended' {
  const upperStatus = status.toUpperCase()

  switch (upperStatus) {
    case 'PREPARING':
    case 'PENDING': // 兼容旧状态
      return 'preparing'
    case 'TEACHING':
    case 'ACTIVE': // 兼容旧状态
      return 'teaching'
    case 'ENDED':
      return 'ended'
    default:
      console.warn(`未知的会话状态: ${status}，默认返回 'ended'`)
      return 'ended'
  }
}

/**
 * 转换会话状态为后端格式（小写 → 大写）
 */
export function formatSessionStatusForAPI(status: 'preparing' | 'teaching' | 'ended'): string {
  return status.toUpperCase()
}

/**
 * 检查会话是否处于活跃状态（PREPARING 或 TEACHING）
 */
export function isSessionActive(status: string): boolean {
  const normalized = normalizeSessionStatus(status)
  return normalized === 'preparing' || normalized === 'teaching'
}

/**
 * 获取会话状态的显示文本
 */
export function getSessionStatusText(status: string): string {
  const normalized = normalizeSessionStatus(status)

  switch (normalized) {
    case 'preparing':
      return '准备中'
    case 'teaching':
      return '上课中'
    case 'ended':
      return '已结束'
    default:
      return '未知'
  }
}

/**
 * 状态常量（用于类型安全）
 */
export const SESSION_STATUS = {
  PREPARING: 'preparing' as const,
  TEACHING: 'teaching' as const,
  ENDED: 'ended' as const,
} as const

export type SessionStatus = typeof SESSION_STATUS[keyof typeof SESSION_STATUS]
