/**
 * useSessionManager Composable 单元测试
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useSessionManager } from '@/components/Classroom/composables/useSessionManager'
import classroomSessionService from '@/services/classroomSession'

// Mock classroomSessionService
vi.mock('@/services/classroomSession', () => ({
  default: {
    createSession: vi.fn(),
    getSession: vi.fn(),
    startSession: vi.fn(),
    endSession: vi.fn(),
    pauseSession: vi.fn(),
    resumeSession: vi.fn(),
    updateDisplayMode: vi.fn(),
    startActivity: vi.fn(),
    endActivity: vi.fn(),
  },
}))

// Mock lesson store
const mockLessonStore = {
  availableClassrooms: [],
  isLoadingClassrooms: false,
  loadAvailableClassrooms: vi.fn(),
}

vi.mock('@/store/lesson', () => ({
  useLessonStore: () => mockLessonStore,
}))

describe('useSessionManager', () => {
  beforeEach(() => {
    // 创建 Pinia 实例
    setActivePinia(createPinia())

    // Mock alert 和 confirm
    global.alert = vi.fn()
    global.confirm = vi.fn(() => true)

    // 重置所有 mocks
    vi.clearAllMocks()

    // 重置 lesson store
    mockLessonStore.availableClassrooms = []
    mockLessonStore.isLoadingClassrooms = false
    mockLessonStore.loadAvailableClassrooms.mockResolvedValue(undefined)
  })

  it('应该正确初始化状态', () => {
    const onSessionCreated = vi.fn()
    const onSessionStarted = vi.fn()
    const onSessionEnded = vi.fn()
    const onError = vi.fn()

    const { session, loading, showClassroomSelectModal, selectedClassroomId, classroomSelectError } =
      useSessionManager({
        lessonId: 1,
        onSessionCreated,
        onSessionStarted,
        onSessionEnded,
        onError,
      })

    expect(session.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(showClassroomSelectModal.value).toBe(false)
    expect(selectedClassroomId.value).toBeNull()
    expect(classroomSelectError.value).toBeNull()
  })

  it('应该正确计算 normalizedSessionStatus', () => {
    const { session, normalizedSessionStatus } = useSessionManager({ lessonId: 1 })

    expect(normalizedSessionStatus.value).toBeNull()

    session.value = { id: 1, status: 'PENDING' }
    expect(normalizedSessionStatus.value).toBe('pending')

    session.value = { id: 1, status: 'ACTIVE' }
    expect(normalizedSessionStatus.value).toBe('active')

    session.value = { id: 1, status: 'preparing' }
    expect(normalizedSessionStatus.value).toBe('preparing')

    session.value = { id: 1, status: 'TEACHING' }
    expect(normalizedSessionStatus.value).toBe('teaching')
  })

  it('应该正确计算 statusTitle', () => {
    const { session, statusTitle } = useSessionManager({ lessonId: 1 })

    expect(statusTitle.value).toBe('未创建会话')

    session.value = { id: 1, status: 'pending' }
    expect(statusTitle.value).toBe('准备中')

    session.value = { id: 1, status: 'active' }
    expect(statusTitle.value).toBe('上课中')

    session.value = { id: 1, status: 'teaching' }
    expect(statusTitle.value).toBe('上课中')

    session.value = { id: 1, status: 'ended' }
    expect(statusTitle.value).toBe('已结束')
  })

  it('应该正确计算 statusClass', () => {
    const { session, statusClass } = useSessionManager({ lessonId: 1 })

    expect(statusClass.value).toBe('status-pending')

    session.value = { id: 1, status: 'active' }
    expect(statusClass.value).toBe('status-active')

    session.value = { id: 1, status: 'teaching' }
    expect(statusClass.value).toBe('status-teaching')

    session.value = { id: 1, status: 'ended' }
    expect(statusClass.value).toBe('status-ended')
  })

  it('应该正确计算 currentDisplayMode', () => {
    const { session, currentDisplayMode } = useSessionManager({ lessonId: 1 })

    expect(currentDisplayMode.value).toBe('window')

    session.value = { id: 1, settings: { display_mode: 'fullscreen' } }
    expect(currentDisplayMode.value).toBe('fullscreen')

    session.value = { id: 1, settings: { display_mode: 'window' } }
    expect(currentDisplayMode.value).toBe('window')
  })

  it('应该在只有一个班级时自动创建会话', async () => {
    mockLessonStore.availableClassrooms = [{ id: 1, name: '班级1' }]
    const mockSession = { id: 1, status: 'pending', lesson_id: 1, classroom_id: 1 }
    ;(classroomSessionService.createSession as any).mockResolvedValue(mockSession)

    const onSessionCreated = vi.fn()
    const { handleCreateSession, session } = useSessionManager({ lessonId: 1, onSessionCreated })

    await handleCreateSession()

    expect(classroomSessionService.createSession).toHaveBeenCalledWith(1, { classroom_id: 1 })
    expect(session.value).toEqual(mockSession)
    expect(onSessionCreated).toHaveBeenCalledWith(mockSession)
  })

  it('应该在有多个班级时显示选择弹窗', async () => {
    mockLessonStore.availableClassrooms = [
      { id: 1, name: '班级1' },
      { id: 2, name: '班级2' },
    ]

    const { handleCreateSession, showClassroomSelectModal } = useSessionManager({ lessonId: 1 })

    await handleCreateSession()

    expect(showClassroomSelectModal.value).toBe(true)
  })

  it('应该在没有可用班级时显示提示', async () => {
    mockLessonStore.availableClassrooms = []

    const { handleCreateSession } = useSessionManager({ lessonId: 1 })

    await handleCreateSession()

    expect(global.alert).toHaveBeenCalledWith('当前没有可用的班级，请联系管理员配置班级信息。')
  })

  it('应该确认选择班级并创建会话', async () => {
    mockLessonStore.availableClassrooms = [{ id: 1, name: '班级1' }]
    const mockSession = { id: 1, status: 'pending', lesson_id: 1, classroom_id: 1 }
    ;(classroomSessionService.createSession as any).mockResolvedValue(mockSession)

    const { handleClassroomSelectConfirm, session, showClassroomSelectModal, selectedClassroomId } =
      useSessionManager({
        lessonId: 1,
      })

    showClassroomSelectModal.value = true
    selectedClassroomId.value = 1

    await handleClassroomSelectConfirm()

    expect(session.value).toEqual(mockSession)
    expect(showClassroomSelectModal.value).toBe(false)
  })

  it('应该取消班级选择', () => {
    const { handleClassroomSelectCancel, showClassroomSelectModal, selectedClassroomId } =
      useSessionManager({ lessonId: 1 })

    showClassroomSelectModal.value = true
    selectedClassroomId.value = 1

    handleClassroomSelectCancel()

    expect(showClassroomSelectModal.value).toBe(false)
    expect(selectedClassroomId.value).toBeNull()
  })

  it('应该开始上课', async () => {
    const pendingSession = { id: 1, status: 'pending' }
    const activeSession = { id: 1, status: 'active' }
    ;(classroomSessionService.startSession as any).mockResolvedValue(activeSession)

    const onSessionStarted = vi.fn()
    const { handleBeginClass, session } = useSessionManager({ lessonId: 1, onSessionStarted })

    session.value = pendingSession

    await handleBeginClass()

    expect(classroomSessionService.startSession).toHaveBeenCalledWith(1)
    expect(session.value).toEqual(activeSession)
    expect(onSessionStarted).toHaveBeenCalledWith(activeSession)
  })

  it('应该取消会话（无学生）', async () => {
    const pendingSession = { id: 1, status: 'pending' }
    const onSessionEnded = vi.fn()

    const { handleCancelSession, session } = useSessionManager({ lessonId: 1, onSessionEnded })

    session.value = pendingSession

    await handleCancelSession(0)

    expect(session.value).toBeNull()
  })

  it('应该暂停会话', async () => {
    const activeSession = { id: 1, status: 'active' }
    const pausedSession = { id: 1, status: 'paused' }
    ;(classroomSessionService.pauseSession as any).mockResolvedValue(pausedSession)

    const { handlePause, session } = useSessionManager({ lessonId: 1 })

    session.value = activeSession

    await handlePause()

    expect(classroomSessionService.pauseSession).toHaveBeenCalledWith(1)
    expect(session.value).toEqual(pausedSession)
  })

  it('应该继续会话', async () => {
    const pausedSession = { id: 1, status: 'paused' }
    const activeSession = { id: 1, status: 'active' }
    ;(classroomSessionService.resumeSession as any).mockResolvedValue(activeSession)

    const { handleResume, session } = useSessionManager({ lessonId: 1 })

    session.value = pausedSession

    await handleResume()

    expect(classroomSessionService.resumeSession).toHaveBeenCalledWith(1)
    expect(session.value).toEqual(activeSession)
  })

  it('应该结束会话', async () => {
    const activeSession = { id: 1, status: 'active' }
    const endedSession = { id: 1, status: 'ended', endedAt: '2024-01-01T00:00:00Z' }
    ;(classroomSessionService.endSession as any).mockResolvedValue(endedSession)

    const onSessionEnded = vi.fn()
    const { handleEnd, session } = useSessionManager({ lessonId: 1, onSessionEnded })

    session.value = activeSession

    await handleEnd()

    expect(classroomSessionService.endSession).toHaveBeenCalledWith(1)
    expect(session.value).toBeNull()
    expect(onSessionEnded).toHaveBeenCalled()
  })

  it('应该切换显示模式', async () => {
    const sessionWithWindow = { id: 1, status: 'active', settings: { display_mode: 'window' } }
    const sessionWithFullscreen = { id: 1, status: 'active', settings: { display_mode: 'fullscreen' } }
    ;(classroomSessionService.updateDisplayMode as any).mockResolvedValue(sessionWithFullscreen)

    const { handleToggleDisplayMode, session } = useSessionManager({ lessonId: 1 })

    session.value = sessionWithWindow

    await handleToggleDisplayMode()

    expect(classroomSessionService.updateDisplayMode).toHaveBeenCalledWith(1, 'fullscreen')
    expect(session.value).toEqual(sessionWithFullscreen)
  })

  it('应该开始活动', async () => {
    const activeSession = { id: 1, status: 'active' }
    const sessionWithActivity = { id: 1, status: 'active', current_activity_id: 10 }
    ;(classroomSessionService.startActivity as any).mockResolvedValue(sessionWithActivity)

    const { handleStartActivity, session } = useSessionManager({ lessonId: 1 })

    session.value = activeSession

    await handleStartActivity(5)

    expect(classroomSessionService.startActivity).toHaveBeenCalledWith(1, { cellId: 5 })
    expect(session.value).toEqual(sessionWithActivity)
  })

  it('应该结束活动', async () => {
    const sessionWithActivity = { id: 1, status: 'active', current_activity_id: 10 }
    const sessionWithoutActivity = { id: 1, status: 'active', current_activity_id: null }
    ;(classroomSessionService.endActivity as any).mockResolvedValue(sessionWithoutActivity)

    const { handleEndActivity, session } = useSessionManager({ lessonId: 1 })

    session.value = sessionWithActivity

    await handleEndActivity()

    expect(classroomSessionService.endActivity).toHaveBeenCalledWith(1)
    expect(session.value).toEqual(sessionWithoutActivity)
  })

  it('应该在创建会话失败时调用 onError', async () => {
    mockLessonStore.availableClassrooms = [{ id: 1, name: '班级1' }]
    const error = new Error('创建失败')
    ;(classroomSessionService.createSession as any).mockRejectedValue(error)

    const onError = vi.fn()
    const { handleCreateSession } = useSessionManager({ lessonId: 1, onError })

    await handleCreateSession()

    expect(onError).toHaveBeenCalledWith(error)
  })

  it('应该在未选择班级时显示错误', async () => {
    const { handleClassroomSelectConfirm, classroomSelectError } = useSessionManager({ lessonId: 1 })

    await handleClassroomSelectConfirm()

    expect(classroomSelectError.value).toBe('请选择一个班级')
  })

  it('应该在会话不存在时无法开始上课', async () => {
    const onSessionStarted = vi.fn()
    const { handleBeginClass } = useSessionManager({ lessonId: 1, onSessionStarted })

    await handleBeginClass()

    expect(classroomSessionService.startSession).not.toHaveBeenCalled()
    expect(onSessionStarted).not.toHaveBeenCalled()
  })

  it('应该在会话状态不是 pending/preparing 时无法开始上课', async () => {
    const activeSession = { id: 1, status: 'active' }
    const onSessionStarted = vi.fn()
    const { handleBeginClass, session } = useSessionManager({ lessonId: 1, onSessionStarted })

    session.value = activeSession

    await handleBeginClass()

    expect(classroomSessionService.startSession).not.toHaveBeenCalled()
    expect(onSessionStarted).not.toHaveBeenCalled()
  })
})
