/**
 * 课堂会话 Store
 *
 * 使用 Pinia 管理课堂会话的全局状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ClassSession,
  SessionStatistics,
  ActivityStatistics,
  StudentParticipation,
} from '../types/classroomSession'

/**
 * 会话状态枚举（标准化）
 */
type SessionStatus = 'preparing' | 'teaching' | 'ended'

export const useClassroomStore = defineStore('classroom', () => {
  // ==========================================================================
  // 状态
  // ==========================================================================

  // 当前课堂会话
  const session = ref<ClassSession | null>(null)

  // 学生参与列表
  const students = ref<StudentParticipation[]>([])

  // 会话统计
  const statistics = ref<SessionStatistics | null>(null)

  // 活动统计
  const activityStatistics = ref<ActivityStatistics | null>(null)

  // WebSocket 连接状态
  const isWebSocketConnected = ref(false)

  // 当前课程 ID
  const currentLessonId = ref<number | null>(null)

  // ==========================================================================
  // Getters (计算属性)
  // ==========================================================================

  /**
   * 标准化的会话状态
   */
  const normalizedSessionStatus = computed<SessionStatus | null>(() => {
    if (!session.value) return null

    const status = session.value.status?.toLowerCase()
    if (status === 'preparing' || status === 'pending') {
      return 'preparing'
    } else if (status === 'teaching' || status === 'active') {
      return 'teaching'
    } else if (status === 'ended') {
      return 'ended'
    }

    return null
  })

  /**
   * 会话是否已创建
   */
  const hasSession = computed(() => !!session.value)

  /**
   * 在线学生数量
   */
  const activeStudentCount = computed(() => {
    return students.value.filter(s => s.isActive).length
  })

  /**
   * 总学生数量
   */
  const totalStudentCount = computed(() => {
    return session.value?.totalStudents || students.value.length || 0
  })

  /**
   * 会话是否已结束
   */
  const isSessionEnded = computed(() => {
    return normalizedSessionStatus.value === 'ended'
  })

  /**
   * 会话是否正在授课
   */
  const isSessionTeaching = computed(() => {
    return normalizedSessionStatus.value === 'teaching'
  })

  /**
   * 会话是否正在准备
   */
  const isSessionPreparing = computed(() => {
    return normalizedSessionStatus.value === 'preparing'
  })

  /**
   * 当前显示的 Cell ID
   */
  const currentCellId = computed(() => {
    return session.value?.currentCellId || null
  })

  /**
   * 当前活动 ID
   */
  const currentActivityId = computed(() => {
    return session.value?.currentActivityId || null
  })

  /**
   * 显示的 Cell 顺序列表
   */
  const displayCellOrders = computed(() => {
    const settings = session.value?.settings as any
    if (settings?.display_cell_orders && Array.isArray(settings.display_cell_orders)) {
      return settings.display_cell_orders
    }
    return []
  })

  // ==========================================================================
  // 操作 (Actions)
  // ==========================================================================

  /**
   * 设置当前课程 ID
   */
  function setCurrentLessonId(lessonId: number) {
    currentLessonId.value = lessonId
  }

  /**
   * 设置会话
   */
  function setSession(newSession: ClassSession | null) {
    session.value = newSession

    // 如果会话有课程 ID，同步更新
    if (newSession?.lessonId) {
      currentLessonId.value = newSession.lessonId
    }
  }

  /**
   * 更新会话状态
   */
  function updateSessionStatus(status: string) {
    if (session.value) {
      session.value.status = status as any
    }
  }

  /**
   * 更新当前 Cell ID
   */
  function updateCurrentCellId(cellId: number | null) {
    if (session.value) {
      session.value.currentCellId = cellId
    }
  }

  /**
   * 更新显示的 Cell 顺序
   */
  function updateDisplayCellOrders(orders: number[]) {
    if (session.value) {
      const settings = (session.value.settings || {}) as any
      settings.display_cell_orders = orders
      session.value.settings = settings
    }
  }

  /**
   * 设置学生列表
   */
  function setStudents(newStudents: StudentParticipation[]) {
    students.value = newStudents

    // 同步更新会话中的学生数量
    if (session.value) {
      session.value.totalStudents = newStudents.length
      session.value.activeStudents = newStudents.filter(s => s.isActive).length
    }
  }

  /**
   * 添加学生
   */
  function addStudent(student: StudentParticipation) {
    // 检查是否已存在
    const exists = students.value.some(s => s.student_id === student.student_id)
    if (exists) {
      // 如果已存在，更新状态
      const index = students.value.findIndex(s => s.student_id === student.student_id)
      students.value[index] = student
    } else {
      // 不存在，添加
      students.value.push(student)
    }

    // 同步更新会话统计
    if (session.value) {
      session.value.totalStudents = students.value.length
      session.value.activeStudents = students.value.filter(s => s.isActive).length
    }
  }

  /**
   * 移除学生
   */
  function removeStudent(studentId: number) {
    const index = students.value.findIndex(s => s.studentId === studentId)
    if (index !== -1) {
      students.value.splice(index, 1)

      // 同步更新会话统计
      if (session.value) {
        session.value.totalStudents = students.value.length
        session.value.activeStudents = students.value.filter(s => s.isActive).length
      }
    }
  }

  /**
   * 更新学生在线状态
   */
  function updateStudentStatus(studentId: number, isOnline: boolean) {
    const student = students.value.find(s => s.studentId === studentId)
    if (student) {
      student.isActive = isOnline
      student.lastActiveAt = new Date().toISOString()

      // 同步更新会话统计
      if (session.value) {
        session.value.activeStudents = students.value.filter(s => s.isActive).length
      }
    }
  }

  /**
   * 设置会话统计
   */
  function setStatistics(newStatistics: SessionStatistics) {
    statistics.value = newStatistics
  }

  /**
   * 设置活动统计
   */
  function setActivityStatistics(newStats: ActivityStatistics) {
    activityStatistics.value = newStats
  }

  /**
   * 更新活动统计
   */
  function updateActivityStatistics(updates: Partial<ActivityStatistics>) {
    if (activityStatistics.value) {
      Object.assign(activityStatistics.value, updates)
    } else {
      activityStatistics.value = {
        totalStudents: 0,
        submittedCount: 0,
        itemStatistics: null,
        ...updates,
      }
    }
  }

  /**
   * 设置 WebSocket 连接状态
   */
  function setWebSocketConnected(connected: boolean) {
    isWebSocketConnected.value = connected
  }

  /**
   * 重置所有状态（清理）
   */
  function reset() {
    session.value = null
    students.value = []
    statistics.value = null
    activityStatistics.value = null
    isWebSocketConnected.value = false
    currentLessonId.value = null
  }

  /**
   * 会话结束后的清理
   */
  function cleanupSession() {
    // 标记所有学生为离线
    students.value.forEach(s => {
      s.isActive = false
      s.leftAt = new Date().toISOString()
    })

    // 更新会话状态
    if (session.value) {
      session.value.status = 'ended' as any
      session.value.activeStudents = 0
    }

    // 断开 WebSocket
    isWebSocketConnected.value = false
  }

  // ==========================================================================
  // 返回
  // ==========================================================================

  return {
    // 状态
    session,
    students,
    statistics,
    activityStatistics,
    isWebSocketConnected,
    currentLessonId,

    // Getters
    normalizedSessionStatus,
    hasSession,
    activeStudentCount,
    totalStudentCount,
    isSessionEnded,
    isSessionTeaching,
    isSessionPreparing,
    currentCellId,
    currentActivityId,
    displayCellOrders,

    // 操作
    setCurrentLessonId,
    setSession,
    updateSessionStatus,
    updateCurrentCellId,
    updateDisplayCellOrders,
    setStudents,
    addStudent,
    removeStudent,
    updateStudentStatus,
    setStatistics,
    setActivityStatistics,
    updateActivityStatistics,
    setWebSocketConnected,
    reset,
    cleanupSession,
  }
})
