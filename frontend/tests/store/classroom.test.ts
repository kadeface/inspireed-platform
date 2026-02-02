/**
 * Classroom Store 单元测试
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useClassroomStore } from '@/store/classroom'
import type {
  ClassSession,
  StudentParticipation,
  SessionStatistics,
  ActivityStatistics,
} from '@/types/classroomSession'

describe('Classroom Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该正确初始化状态', () => {
    const store = useClassroomStore()

    expect(store.session).toBeNull()
    expect(store.students).toEqual([])
    expect(store.statistics).toBeNull()
    expect(store.activityStatistics).toBeNull()
    expect(store.isWebSocketConnected).toBe(false)
    expect(store.currentLessonId).toBeNull()
  })

  it('应该正确计算 normalizedSessionStatus', () => {
    const store = useClassroomStore()

    // 无会话
    expect(store.normalizedSessionStatus).toBeNull()

    // preparing 状态
    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'preparing',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })
    expect(store.normalizedSessionStatus).toBe('preparing')

    // PENDING 状态（应转换为 preparing）
    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'pending' as any,
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })
    expect(store.normalizedSessionStatus).toBe('preparing')

    // teaching 状态
    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })
    expect(store.normalizedSessionStatus).toBe('teaching')

    // ACTIVE 状态（应转换为 teaching）
    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'active' as any,
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })
    expect(store.normalizedSessionStatus).toBe('teaching')

    // ended 状态
    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'ended',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })
    expect(store.normalizedSessionStatus).toBe('ended')
  })

  it('应该正确计算 hasSession', () => {
    const store = useClassroomStore()

    expect(store.hasSession).toBe(false)

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'preparing',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    expect(store.hasSession).toBe(true)

    store.setSession(null)
    expect(store.hasSession).toBe(false)
  })

  it('应该正确计算 activeStudentCount', () => {
    const store = useClassroomStore()

    store.setStudents([
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
      { id: 2, sessionId: 1, studentId: 2, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
      { id: 3, sessionId: 1, studentId: 3, joinedAt: '', lastActiveAt: '', isActive: false, progressPercentage: 0 },
    ])

    expect(store.activeStudentCount).toBe(2)
  })

  it('应该正确计算 totalStudentCount', () => {
    const store = useClassroomStore()

    // 无学生时，从 session.totalStudents 获取
    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'preparing',
      totalStudents: 30,
      activeStudents: 10,
      createdAt: '',
      updatedAt: '',
    })
    expect(store.totalStudentCount).toBe(30)

    // 有学生时，从 students 数组获取
    store.setStudents([
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
      { id: 2, sessionId: 1, studentId: 2, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
    ])
    expect(store.totalStudentCount).toBe(2)
  })

  it('应该正确计算会话状态', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'preparing',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    expect(store.isSessionPreparing).toBe(true)
    expect(store.isSessionTeaching).toBe(false)
    expect(store.isSessionEnded).toBe(false)

    store.updateSessionStatus('teaching')
    expect(store.isSessionPreparing).toBe(false)
    expect(store.isSessionTeaching).toBe(true)
    expect(store.isSessionEnded).toBe(false)

    store.updateSessionStatus('ended')
    expect(store.isSessionPreparing).toBe(false)
    expect(store.isSessionTeaching).toBe(false)
    expect(store.isSessionEnded).toBe(true)
  })

  it('应该正确计算 currentCellId 和 currentActivityId', () => {
    const store = useClassroomStore()

    expect(store.currentCellId).toBeNull()
    expect(store.currentActivityId).toBeNull()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      currentCellId: 5,
      currentActivityId: 10,
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    expect(store.currentCellId).toBe(5)
    expect(store.currentActivityId).toBe(10)
  })

  it('应该正确计算 displayCellOrders', () => {
    const store = useClassroomStore()

    expect(store.displayCellOrders).toEqual([])

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      settings: { display_cell_orders: [0, 1, 2] },
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    expect(store.displayCellOrders).toEqual([0, 1, 2])
  })

  it('应该正确设置会话', () => {
    const store = useClassroomStore()
    const session: ClassSession = {
      id: 1,
      lessonId: 10,
      classroomId: 1,
      teacherId: 1,
      status: 'preparing',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    }

    store.setSession(session)

    expect(store.session).toEqual(session)
    expect(store.currentLessonId).toBe(10)
  })

  it('应该正确更新会话状态', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'preparing',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    store.updateSessionStatus('teaching')
    expect(store.session?.status).toBe('teaching')

    store.updateSessionStatus('ended')
    expect(store.session?.status).toBe('ended')
  })

  it('应该正确更新当前 Cell ID', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    store.updateCurrentCellId(5)
    expect(store.currentCellId).toBe(5)

    store.updateCurrentCellId(null)
    expect(store.currentCellId).toBeNull()
  })

  it('应该正确更新 displayCellOrders', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      settings: {},
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    store.updateDisplayCellOrders([0, 1, 2])
    expect(store.displayCellOrders).toEqual([0, 1, 2])
  })

  it('应该正确设置学生列表', () => {
    const store = useClassroomStore()
    const students: StudentParticipation[] = [
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 50 },
      { id: 2, sessionId: 1, studentId: 2, joinedAt: '', lastActiveAt: '', isActive: false, progressPercentage: 30 },
    ]

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    store.setStudents(students)

    expect(store.students).toEqual(students)
    expect(store.session?.totalStudents).toBe(2)
    expect(store.session?.activeStudents).toBe(1)
  })

  it('应该正确添加学生', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    const student: StudentParticipation = {
      id: 1,
      sessionId: 1,
      studentId: 1,
      joinedAt: '',
      lastActiveAt: '',
      isActive: true,
      progressPercentage: 0,
    }

    store.addStudent(student)

    expect(store.students).toHaveLength(1)
    expect(store.students[0]).toEqual(student)
    expect(store.session?.totalStudents).toBe(1)
    expect(store.session?.activeStudents).toBe(1)

    // 添加已存在的学生应该更新而不是重复添加
    const updatedStudent = { ...student, isActive: false, progressPercentage: 50 }
    store.addStudent(updatedStudent)

    expect(store.students).toHaveLength(1)
    expect(store.students[0]).toEqual(updatedStudent)
  })

  it('应该正确移除学生', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    const students: StudentParticipation[] = [
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
      { id: 2, sessionId: 1, studentId: 2, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
    ]

    store.setStudents(students)

    store.removeStudent(1)

    expect(store.students).toHaveLength(1)
    expect(store.students[0].studentId).toBe(2)
    expect(store.session?.totalStudents).toBe(1)
  })

  it('应该正确更新学生状态', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    const students: StudentParticipation[] = [
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
    ]

    store.setStudents(students)

    store.updateStudentStatus(1, false)

    expect(store.students[0].isActive).toBe(false)
    expect(store.session?.activeStudents).toBe(0)
  })

  it('应该正确设置统计信息', () => {
    const store = useClassroomStore()
    const statistics: SessionStatistics = {
      totalStudents: 30,
      activeStudents: 15,
      completedStudents: 5,
      averageProgress: 60,
      studentsByProgress: {
        '0-25%': 5,
        '25-50%': 10,
        '50-75%': 8,
        '75-100%': 2,
        '100%': 5,
      },
    }

    store.setStatistics(statistics)

    expect(store.statistics).toEqual(statistics)
  })

  it('应该正确设置活动统计', () => {
    const store = useClassroomStore()
    const stats: ActivityStatistics = {
      totalStudents: 30,
      submittedCount: 15,
      itemStatistics: null,
    }

    store.setActivityStatistics(stats)

    expect(store.activityStatistics).toEqual(stats)
  })

  it('应该正确更新活动统计', () => {
    const store = useClassroomStore()

    store.setActivityStatistics({
      totalStudents: 30,
      submittedCount: 10,
      itemStatistics: null,
    })

    store.updateActivityStatistics({ submittedCount: 20 })

    expect(store.activityStatistics?.submittedCount).toBe(20)
    expect(store.activityStatistics?.totalStudents).toBe(30) // 保持不变
  })

  it('应该正确设置 WebSocket 连接状态', () => {
    const store = useClassroomStore()

    expect(store.isWebSocketConnected).toBe(false)

    store.setWebSocketConnected(true)
    expect(store.isWebSocketConnected).toBe(true)

    store.setWebSocketConnected(false)
    expect(store.isWebSocketConnected).toBe(false)
  })

  it('应该正确设置当前课程 ID', () => {
    const store = useClassroomStore()

    store.setCurrentLessonId(10)

    expect(store.currentLessonId).toBe(10)
  })

  it('应该正确重置所有状态', () => {
    const store = useClassroomStore()

    // 设置各种状态
    store.setSession({
      id: 1,
      lessonId: 10,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 30,
      activeStudents: 15,
      createdAt: '',
      updatedAt: '',
    })

    store.setStudents([
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
    ])

    store.setStatistics({
      totalStudents: 30,
      activeStudents: 15,
      completedStudents: 5,
      averageProgress: 60,
      studentsByProgress: { '0-25%': 5, '25-50%': 10, '50-75%': 8, '75-100%': 2, '100%': 5 },
    })

    store.setActivityStatistics({ totalStudents: 30, submittedCount: 15, itemStatistics: null })
    store.setWebSocketConnected(true)
    store.setCurrentLessonId(10)

    // 重置
    store.reset()

    expect(store.session).toBeNull()
    expect(store.students).toEqual([])
    expect(store.statistics).toBeNull()
    expect(store.activityStatistics).toBeNull()
    expect(store.isWebSocketConnected).toBe(false)
    expect(store.currentLessonId).toBeNull()
  })

  it('应该正确清理会话', () => {
    const store = useClassroomStore()

    store.setSession({
      id: 1,
      lessonId: 1,
      classroomId: 1,
      teacherId: 1,
      status: 'teaching',
      totalStudents: 0,
      activeStudents: 0,
      createdAt: '',
      updatedAt: '',
    })

    store.setStudents([
      { id: 1, sessionId: 1, studentId: 1, joinedAt: '', lastActiveAt: '', isActive: true, progressPercentage: 0 },
    ])

    store.setWebSocketConnected(true)

    store.cleanupSession()

    // 所有学生应被标记为离线
    expect(store.students.every(s => !s.isActive)).toBe(true)
    expect(store.students.every(s => !!s.leftAt)).toBe(true)

    // 会话状态应结束
    expect(store.session?.status).toBe('ended')
    expect(store.session?.activeStudents).toBe(0)

    // WebSocket 应断开
    expect(store.isWebSocketConnected).toBe(false)
  })
})
