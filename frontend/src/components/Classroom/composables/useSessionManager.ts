/**
 * 会话状态管理 Composable
 *
 * 管理课堂会话的创建、开始、暂停、继续、结束等操作
 */

import { ref, computed, type Ref } from 'vue'
import classroomSessionService from '@/services/classroomSession'
import type { LessonClassroom } from '@/types/lesson'
import { useLessonStore } from '@/store/lesson'

export interface UseSessionManagerOptions {
  lessonId: number
  onSessionCreated?: (session: any) => void
  onSessionStarted?: (session: any) => void
  onSessionEnded?: () => void
  onError?: (error: any) => void
}

export function useSessionManager(options: UseSessionManagerOptions) {
  const { lessonId, onSessionCreated, onSessionStarted, onSessionEnded, onError } = options

  // 状态
  const session = ref<any>(null)
  const loading = ref(false)
  const showClassroomSelectModal = ref(false)
  const selectedClassroomId = ref<number | null>(null)
  const classroomSelectError = ref<string | null>(null)

  const lessonStore = useLessonStore()
  const availableClassrooms = computed<LessonClassroom[]>(() => lessonStore.availableClassrooms || [])
  const loadingClassrooms = computed(() => lessonStore.isLoadingClassrooms)

  // 统一状态值处理：将后端返回的大写状态转换为小写
  const normalizedSessionStatus = computed(() => {
    if (!session.value || !session.value.status) return null
    const status = session.value.status
    // 统一转换为小写
    return typeof status === 'string' ? status.toLowerCase() : status
  })

  // 计算属性
  const statusTitle = computed(() => {
    if (!session.value) return '未创建会话'
    const status = normalizedSessionStatus.value
    const statusMap: Record<string, string> = {
      pending: '准备中',
      preparing: '准备中',
      active: '上课中',
      teaching: '上课中',
      ended: '已结束',
    }
    return statusMap[status || ''] || '未知状态'
  })

  const statusClass = computed(() => {
    if (!session.value) return 'status-pending'
    const status = normalizedSessionStatus.value || 'pending'
    return `status-${status}`
  })

  // 计算当前显示模式
  const currentDisplayMode = computed(() => {
    if (!session.value?.settings) return 'window'
    const settings = session.value.settings as any
    return settings.display_mode || 'window'
  })

  // 创建课堂会话
  async function handleCreateSession() {
    // 先加载可用班级列表
    try {
      await lessonStore.loadAvailableClassrooms()

      // 如果只有一个班级，直接使用；否则显示选择弹窗
      if (availableClassrooms.value.length === 1) {
        selectedClassroomId.value = availableClassrooms.value[0].id
        await createSessionWithClassroom(availableClassrooms.value[0].id)
      } else if (availableClassrooms.value.length === 0) {
        alert('当前没有可用的班级，请联系管理员配置班级信息。')
      } else {
        // 显示班级选择弹窗
        showClassroomSelectModal.value = true
        classroomSelectError.value = null
      }
    } catch (error: any) {
      console.error('加载班级列表失败:', error)
      alert('加载班级列表失败：' + (error.message || '未知错误'))
    }
  }

  // 确认选择班级并创建会话
  async function handleClassroomSelectConfirm() {
    if (!selectedClassroomId.value) {
      classroomSelectError.value = '请选择一个班级'
      return
    }

    classroomSelectError.value = null
    showClassroomSelectModal.value = false

    await createSessionWithClassroom(selectedClassroomId.value)

    // 重置选择
    selectedClassroomId.value = null
  }

  // 取消班级选择
  function handleClassroomSelectCancel() {
    showClassroomSelectModal.value = false
    selectedClassroomId.value = null
    classroomSelectError.value = null
  }

  // 使用指定班级创建会话
  async function createSessionWithClassroom(classroomId: number, retryCount: number = 0) {
    const MAX_RETRIES = 2 // 最多重试2次
    loading.value = true
    try {
      // 创建会话（状态为 PENDING）
      const newSession = await classroomSessionService.createSession(lessonId, {
        classroom_id: classroomId,
      })

      // 检查响应
      if (!newSession || !newSession.id) {
        console.error('Invalid session response:', newSession)
        throw new Error('创建会话失败：服务器返回的数据格式不正确')
      }

      // 保持 PENDING 状态，不立即开始
      session.value = newSession

      // 调用回调
      onSessionCreated?.(newSession)
    } catch (createError: any) {
      // 如果创建失败，检查是否是因为已有活跃会话
      const errorDetail = createError.response?.data?.detail || createError.message || ''

      // 检查错误消息中是否包含"已有活跃的课堂会话"
      const hasActiveSessionError = errorDetail.includes('已有活跃的课堂会话') ||
                                    errorDetail.includes('已有活跃会话')

      if (hasActiveSessionError && (createError.response?.status === 400 || createError.message)) {
        // 从错误信息中提取会话ID
        const sessionIdMatch = errorDetail.match(/\(ID\s*[：:]\s*(\d+)\)/) ||
                               errorDetail.match(/（ID\s*[：:]\s*(\d+)）/) ||
                               errorDetail.match(/ID\s*[：:]\s*(\d+)/)

        if (!sessionIdMatch) {
          console.error('❌ 无法从错误信息中提取会话ID。错误信息:', errorDetail)
          throw createError
        }

        const existingSessionId = parseInt(sessionIdMatch[1])

        // 直接加载现有会话，并提示用户
        try {
          const existingSession = await classroomSessionService.getSession(existingSessionId)
          if (existingSession) {
            // 检查会话状态，如果是 ENDED 状态，重新创建新会话
            if (existingSession.status === 'ended' || existingSession.status === 'ENDED') {
              console.log('ℹ️ 检测到的会话已经是 ENDED 状态，重新创建新会话')

              // 如果重试次数未超过限制，重新调用创建会话
              if (retryCount < MAX_RETRIES) {
                console.log(`🔄 重试创建会话 (${retryCount + 1}/${MAX_RETRIES})...`)
                loading.value = false
                await new Promise(resolve => setTimeout(resolve, 500))
                return await createSessionWithClassroom(classroomId, retryCount + 1)
              } else {
                console.error('❌ 重试次数已达上限，无法创建新会话')
                alert('检测到已结束的会话，但多次重试后仍无法创建新会话。请刷新页面后重试。')
                throw new Error('重试次数已达上限')
              }
            } else {
              // 会话是活跃状态，加载它并提示用户
              session.value = existingSession

              const sessionStatusText = {
                pending: '待开始',
                preparing: '待开始',
                active: '进行中',
                teaching: '进行中',
                paused: '已暂停',
                ended: '已结束',
              }[existingSession.status] || existingSession.status

              alert(
                `📢 检测到已有活跃的课堂会话（ID: ${existingSessionId}，状态：${sessionStatusText}）\n\n` +
                `已自动加载现有会话。如需创建新会话，请先点击"结束"按钮结束当前会话。`
              )
              onSessionCreated?.(existingSession)
              return
            }
          }
        } catch (loadError: any) {
          console.error('加载现有会话失败:', loadError)
          if (loadError.response?.status === 404) {
            console.log('ℹ️ 会话不存在（可能已删除），尝试重新创建新会话')

            if (retryCount < MAX_RETRIES) {
              console.log(`🔄 会话不存在，重试创建会话 (${retryCount + 1}/${MAX_RETRIES})...`)
              loading.value = false
              await new Promise(resolve => setTimeout(resolve, 500))
              return await createSessionWithClassroom(classroomId, retryCount + 1)
            } else {
              console.error('❌ 重试次数已达上限')
              alert('会话不存在，但多次重试后仍无法创建新会话。请刷新页面后重试。')
              throw loadError
            }
          } else {
            const loadErrorDetail = loadError.response?.data?.detail || loadError.message || '加载会话失败'
            alert(`检测到已有活跃会话，但无法加载：${loadErrorDetail}\n\n会话ID: ${existingSessionId}\n\n请刷新页面后重试。`)
            throw loadError
          }
        }
      } else {
        // 其他错误，显示错误信息
        console.error('Failed to create session:', createError)
        let errorMessage = createError.message || createError.response?.data?.detail || '创建课堂失败'

        if (errorMessage.includes('无权限')) {
          errorMessage = '无法访问该会话。请确保您是该会话的创建者。'
        } else if (errorMessage.includes('不存在')) {
          errorMessage = '会话不存在，请刷新页面重试。'
        } else if (errorMessage.includes('已有活跃的课堂会话')) {
          errorMessage = '检测到已有活跃会话，但无法自动加载。请刷新页面重试。'
        }

        alert(errorMessage)
        onError?.(createError)
      }
    } finally {
      loading.value = false
    }
  }

  // 开始上课（将 PENDING 状态变为 ACTIVE）
  async function handleBeginClass() {
    const status = normalizedSessionStatus.value
    if (!session.value || (status !== 'pending' && status !== 'preparing')) return

    loading.value = true
    try {
      session.value = await classroomSessionService.startSession(session.value.id)

      // 检查开始会话的响应
      if (!session.value) {
        throw new Error('开始会话失败：服务器返回的数据格式不正确')
      }

      onSessionStarted?.(session.value)
    } catch (error: any) {
      console.error('Failed to start session:', error)
      const errorMessage = error.message || error.response?.data?.detail || '开始上课失败'
      alert(errorMessage)
      onError?.(error)
    } finally {
      loading.value = false
    }
  }

  // 取消课堂（删除 PENDING 状态的会话）
  async function handleCancelSession(activeStudentsCount: number = 0) {
    const status = normalizedSessionStatus.value
    if (!session.value || (status !== 'pending' && status !== 'preparing')) return

    // 根据是否有学生进入，显示不同的提示
    const hasStudents = activeStudentsCount > 0
    const confirmMessage = hasStudents
      ? '确定要取消课堂吗？当前已有学生进入，这将结束当前会话。'
      : '确定要取消课堂吗？这将删除当前会话。'

    if (!confirm(confirmMessage)) return

    loading.value = true
    try {
      // 如果没有学生进入，直接清除本地会话状态
      if (!hasStudents) {
        session.value = null
        return
      }

      // 如果有学生进入，调用 endSession API 来结束会话
      session.value = await classroomSessionService.endSession(session.value.id)
    } catch (error: any) {
      console.error('Failed to cancel session:', error)
      // 如果 API 调用失败，但如果没有学生，仍然清除本地状态
      if (!hasStudents) {
        session.value = null
      } else {
        alert('取消课堂失败：' + (error.message || error.response?.data?.detail || '未知错误'))
        onError?.(error)
      }
    } finally {
      loading.value = false
    }
  }

  // 结束会话
  async function handleEnd() {
    if (!session.value) return
    if (!confirm('确定要结束课程吗？')) return

    loading.value = true
    const sessionId = session.value.id

    try {
      // 调用 API 结束会话
      await classroomSessionService.endSession(sessionId)

      // 结束会话后，清除本地状态
      session.value = null

      onSessionEnded?.()
      alert('课程已成功结束，现在可以创建新课堂了')
    } catch (error: any) {
      console.error('❌ 结束会话失败:', error)
      const errorMessage = error.response?.data?.detail || error.message || '结束课程失败'

      let userMessage = '结束课程失败：' + errorMessage
      if (error.response?.status === 403) {
        userMessage = '结束课程失败：您没有权限结束此会话'
      } else if (error.response?.status === 404) {
        userMessage = '结束课程失败：会话不存在（可能已被删除）'
      } else if (error.response?.status === 500) {
        userMessage = '结束课程失败：服务器内部错误，请稍后重试或联系管理员'
      }

      alert(userMessage)
      onError?.(error)

      // 即使 API 调用失败，也尝试清除本地状态
      if (error.response?.status === 404 || errorMessage.includes('不存在')) {
        console.log('⚠️ 会话可能已经不存在，清除本地状态')
        session.value = null
        onSessionEnded?.()
      }
    } finally {
      loading.value = false
    }
  }

  // 开始活动
  async function handleStartActivity(currentCellId: number | null) {
    if (!session.value || !currentCellId) {
      alert('无法开始活动：当前没有显示任何Cell')
      return
    }

    loading.value = true
    try {
      session.value = await classroomSessionService.startActivity(session.value.id, {
        cellId: currentCellId,
      })
    } catch (error: any) {
      console.error('Failed to start activity:', error)
      const errorMessage = error.response?.data?.detail || error.message || '开始活动失败'
      alert(errorMessage)
      onError?.(error)
    } finally {
      loading.value = false
    }
  }

  // 结束活动
  async function handleEndActivity() {
    if (!session.value) return

    loading.value = true
    try {
      session.value = await classroomSessionService.endActivity(session.value.id)
    } catch (error: any) {
      console.error('Failed to end activity:', error)
      alert('结束活动失败')
      onError?.(error)
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    session,
    loading,
    showClassroomSelectModal,
    selectedClassroomId,
    classroomSelectError,
    availableClassrooms,
    loadingClassrooms,
    normalizedSessionStatus,
    statusTitle,
    statusClass,
    currentDisplayMode,

    // 方法
    handleCreateSession,
    handleClassroomSelectConfirm,
    handleClassroomSelectCancel,
    handleBeginClass,
    handleCancelSession,
    handleEnd,
    handleStartActivity,
    handleEndActivity,
  }
}
