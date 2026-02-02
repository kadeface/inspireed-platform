/**
 * 计时器管理 Composable
 *
 * 管理课程时长的计时功能
 */

import { ref, watch, type Ref } from 'vue'

export interface UseDurationTimerOptions {
  /**
   * 获取会话状态
   * @returns 返回会话状态字符串
   */
  getSessionStatus: () => string | null | undefined

  /**
   * 课程总时长（秒）
   * @default 2400 (40分钟)
   */
  lessonDuration?: number

  /**
   * 计时器状态变化时的回调
   * @param isRunning - 计时器是否正在运行
   */
  onTimerStateChange?: (isRunning: boolean) => void
}

export function useDurationTimer(options: UseDurationTimerOptions) {
  const {
    getSessionStatus,
    lessonDuration = 40 * 60, // 默认40分钟
    onTimerStateChange,
  } = options

  // 当前课程时长（秒）
  const sessionDuration = ref(0)

  // 定时器引用
  const durationInterval = ref<ReturnType<typeof setInterval> | null>(null)

  /**
   * 启动计时器
   */
  function startDurationTimer() {
    if (durationInterval.value) return

    // 如果还没有开始计时（值为0或未定义），从0开始
    // 如果已经有值（比如暂停后继续），保持当前值继续计时
    if (sessionDuration.value === 0 || sessionDuration.value === null || sessionDuration.value === undefined) {
      sessionDuration.value = 0
    }

    // 每秒递增，直到达到课程时长
    durationInterval.value = window.setInterval(() => {
      sessionDuration.value = Math.min(sessionDuration.value + 1, lessonDuration)
    }, 1000)

    onTimerStateChange?.(true)
  }

  /**
   * 停止计时器
   */
  function stopDurationTimer() {
    if (durationInterval.value) {
      clearInterval(durationInterval.value)
      durationInterval.value = null
      onTimerStateChange?.(false)
    }
  }

  /**
   * 重置计时器
   */
  function resetDurationTimer() {
    stopDurationTimer()
    sessionDuration.value = 0
  }

  /**
   * 获取当前显示的时长（只在 active 状态显示实际时长）
   */
  function getDisplayDuration(): number {
    const status = getSessionStatus()
    if (status !== 'active' && status !== 'teaching') {
      return 0
    }
    return sessionDuration.value || 0
  }

  /**
   * 计算剩余时间
   */
  function getRemainingTime(): number {
    if (sessionDuration.value === null || sessionDuration.value === undefined) {
      return lessonDuration
    }
    const remaining = lessonDuration - sessionDuration.value
    return remaining > 0 ? remaining : 0
  }

  /**
   * 监听会话状态变化，自动启动/停止计时器
   */
  function watchSessionStatus(sessionStatus: Ref<string | null | undefined>) {
    watch(sessionStatus, (status, oldStatus) => {
      const normalizedStatus = status?.toLowerCase()
      const normalizedOldStatus = oldStatus?.toLowerCase()

      if (normalizedStatus === 'teaching' || normalizedStatus === 'active') {
        // 当状态变为 active 时，启动计时器
        if (!durationInterval.value) {
          // 只有在从 pending/preparing 状态变为 active（新开始）时，才重置为0
          // 如果是从 paused 恢复（继续），保持当前时长继续计时
          if (
            normalizedOldStatus === 'pending' ||
            normalizedOldStatus === 'preparing' ||
            sessionDuration.value === 0
          ) {
            sessionDuration.value = 0
          }
          startDurationTimer()
        }
      } else if (normalizedStatus === 'paused') {
        // 当状态变为 paused 时，停止计时器（但保持当前时长）
        stopDurationTimer()
      } else if (normalizedStatus === 'ended') {
        // 当状态变为 ended 时，停止计时器
        stopDurationTimer()
      } else {
        // 其他状态（如 pending, preparing），停止计时器
        stopDurationTimer()
      }
    }, { immediate: true })
  }

  return {
    // 状态
    sessionDuration,
    durationInterval,

    // 方法
    startDurationTimer,
    stopDurationTimer,
    resetDurationTimer,
    getDisplayDuration,
    getRemainingTime,
    watchSessionStatus,
  }
}
