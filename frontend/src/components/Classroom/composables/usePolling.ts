/**
 * 轮询管理 Composable
 *
 * 管理课堂会话的定时轮询，用于加载参与者、统计等信息
 */

import { ref, type Ref } from 'vue'

export interface UsePollingOptions {
  /**
   * 检查组件是否可见
   * @returns 如果组件不在DOM中，应返回false停止轮询
   */
  isComponentVisible?: () => boolean

  /**
   * 获取当前会话状态
   * @returns 返回 'pending' | 'preparing' | 'active' | 'teaching' | 'paused' | 'ended'
   */
  getSessionStatus: () => string | null

  /**
   * 检查会话是否存在
   * @returns 会话对象是否存在
   */
  hasSession: () => boolean

  /**
   * 加载参与者列表
   */
  loadParticipants: () => void | Promise<void>

  /**
   * 加载统计信息
   */
  loadStatistics?: () => void | Promise<void>

  /**
   * 加载活动统计
   */
  loadActivityStatistics?: () => void | Promise<void>

  /**
   * 当前是否为活动模块
   */
  isCurrentCellActivity?: () => boolean
}

export function usePolling(options: UsePollingOptions) {
  const {
    isComponentVisible,
    getSessionStatus,
    hasSession,
    loadParticipants,
    loadStatistics,
    loadActivityStatistics,
    isCurrentCellActivity,
  } = options

  // 存储所有轮询定时器
  const pollingIntervals = ref<Array<ReturnType<typeof setInterval>>>([])

  /**
   * 清理所有轮询定时器
   */
  function clearAllPollingIntervals() {
    pollingIntervals.value.forEach(interval => {
      clearInterval(interval)
    })
    pollingIntervals.value = []
  }

  /**
   * 启动轮询（只在会话存在且需要时启动）
   */
  function startPollingIfNeeded() {
    // 检查组件是否可见（如果组件被 v-if 隐藏，不应该启动轮询）
    if (isComponentVisible && !isComponentVisible()) {
      console.log('⏸️ startPollingIfNeeded: 组件不可见，跳过启动轮询')
      return
    }

    // 先清理旧的定时器
    clearAllPollingIntervals()

    // 检查会话是否存在
    if (!hasSession()) {
      return
    }

    // 根据会话状态启动不同的轮询
    const status = getSessionStatus()

    if (status === 'pending' || status === 'preparing') {
      // PENDING 状态：只轮询参与者列表（每3秒）
      const interval = setInterval(() => {
        // 检查组件是否还在 DOM 中
        if (isComponentVisible && !isComponentVisible()) {
          console.log('🛑 停止轮询：组件不在 DOM 中')
          clearAllPollingIntervals()
          return
        }

        // 检查会话是否还存在且状态正确
        const currentStatus = getSessionStatus()
        if (!hasSession() || currentStatus !== 'pending' && currentStatus !== 'preparing') {
          clearAllPollingIntervals()
          return
        }

        // 只在有会话时才加载
        loadParticipants()
      }, 3000)
      pollingIntervals.value.push(interval)

    } else if (status === 'active' || status === 'teaching' || status === 'paused') {
      // ACTIVE/PAUSED 状态：轮询参与者列表和统计（每5秒）
      const interval = setInterval(() => {
        // 检查组件是否还在 DOM 中
        if (isComponentVisible && !isComponentVisible()) {
          clearAllPollingIntervals()
          return
        }

        // 检查会话是否还存在且状态正确
        const checkStatus = getSessionStatus()
        if (!hasSession() || (checkStatus !== 'active' && checkStatus !== 'teaching' && checkStatus !== 'paused')) {
          clearAllPollingIntervals()
          return
        }

        // 只在有会话时才加载
        loadParticipants()
        loadStatistics?.()

        // 如果当前是活动模块，也刷新活动统计
        if (isCurrentCellActivity && isCurrentCellActivity()) {
          loadActivityStatistics?.()
        }
      }, 5000)
      pollingIntervals.value.push(interval)
    }

    // 其他状态不启动轮询
  }

  /**
   * 手动触发一次数据加载（不启动定时器）
   */
  function triggerLoadOnce() {
    if (!hasSession()) return

    loadParticipants()
    const status = getSessionStatus()
    if (status === 'active' || status === 'teaching' || status === 'paused') {
      loadStatistics?.()
      if (isCurrentCellActivity && isCurrentCellActivity()) {
        loadActivityStatistics?.()
      }
    }
  }

  return {
    // 状态
    pollingIntervals,

    // 方法
    startPollingIfNeeded,
    clearAllPollingIntervals,
    triggerLoadOnce,
  }
}
