/**
 * 课堂会话 Composable（学生端）
 *
 * v2.0 更新：
 * - 移除 PAUSED 状态相关逻辑
 * - 使用状态映射工具处理大写/小写状态
 * - 简化状态比较逻辑
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import classroomSessionService from '../services/classroomSession'
import { websocketService, type WebSocketMessage } from '../services/websocket'
import { getAuthToken } from '../utils/auth'
import { useUserStore } from '../store/user'
import type { ClassSession, StudentParticipation } from '../types/classroomSession'
import { createLogger } from '../utils/logger'
import { normalizeSessionStatus, isSessionActive } from '../utils/sessionStatus'

const log = createLogger('ClassroomSession')

export function useClassroomSession(lessonId: number, onDisplayModeChanged?: (mode: 'fullscreen' | 'window') => void) {
  const route = useRoute()
  const session = ref<ClassSession | null>(null)
  const participation = ref<StudentParticipation | null>(null)
  const currentCellId = ref<number | null>(null)
  const isInClassroomMode = computed(() => {
    // v2.0: 在 PREPARING 和 TEACHING 状态下都认为是课堂模式
    if (!session.value?.status) return false
    return isSessionActive(session.value.status)
  })
  
  // 轮询定时器（用于定期获取会话状态）- 降级方案
  let pollingInterval: ReturnType<typeof setInterval> | null = null
  const POLLING_INTERVAL = 5000 // 降级时使用5秒轮询（减少负载）
  
  // WebSocket连接状态
  const isWebSocketConnected = ref<boolean>(false)
  const useWebSocket = ref<boolean>(true) // 默认启用 WebSocket
  
  /**
   * 查找并加入会话（带重试机制）
   */
  async function findAndJoinSession(retryCount: number = 0): Promise<ClassSession | null> {
    const MAX_RETRIES = 3
    const RETRY_DELAY = 2000 // 2秒
    
    try {
      log.debug(`[${retryCount + 1}/3] 查找会话 lessonId=${lessonId}`)

      // v2.0: 获取该教案的所有会话（包括 preparing 和 teaching 状态）
      // 先尝试查找 TEACHING 状态的会话
      let sessions = await classroomSessionService.listSessions(lessonId, 'TEACHING')
      log.debug(`找到 ${sessions.length} 个 TEACHING 会话`)

      // 如果没有 TEACHING 状态的会话，尝试查找 PREPARING 状态的会话
      if (sessions.length === 0) {
        const allSessions = await classroomSessionService.listSessions(lessonId)
        log.debug(`找到 ${allSessions.length} 个会话`)
        // v2.0: 使用状态映射工具比较，兼容大写和小写
        sessions = allSessions.filter(s => {
          const normalized = normalizeSessionStatus(s.status)
          return normalized === 'preparing' || normalized === 'teaching'
        })
        log.debug(`过滤后 ${sessions.length} 个可加入会话`)
      }

      if (sessions.length > 0) {
        // 按创建时间或ID排序，选择最新的会话（避免加入旧会话）
        const sortedSessions = sessions.sort((a, b) => {
          // 优先按 ID 降序排序（ID越大越新）
          if (a.id && b.id) {
            return b.id - a.id
          }
          // 其次按创建时间降序排序
          if (a.createdAt && b.createdAt) {
            return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
          }
          return 0
        })

        // v2.0: 找到最新的可加入会话（优先 TEACHING，其次 PREPARING）
        const activeSession = sortedSessions.find(s => {
          const normalized = normalizeSessionStatus(s.status)
          return normalized === 'teaching'
        }) || sortedSessions[0]

        log.debug('会话选择', { selectedSessionId: activeSession.id, status: activeSession.status })

        // v2.0: 检查会话状态（使用状态映射工具）
        const normalizedStatus = normalizeSessionStatus(activeSession.status)
        if (normalizedStatus === 'ended') {
          log.warn('会话已结束，无法加入')
          return null
        }
        
        // 🆕 获取完整的会话信息（包括 teacherName 和 lessonTitle）
        let fullSession: ClassSession | null = null
        try {
          fullSession = await classroomSessionService.getSession(activeSession.id)
        } catch (error) {
          log.warn('获取完整会话信息失败，使用列表', error)
        }
        
        // 使用完整会话信息或列表信息
        session.value = {
          ...(fullSession || activeSession),
          settings: (fullSession || activeSession).settings || {},
        }
        
        // 处理字段映射：后端可能返回 current_cell_id（snake_case）或 currentCellId（camelCase）
        const cellId = (session.value as any)?.current_cell_id ?? session.value?.currentCellId ?? null
        currentCellId.value = cellId
        
        log.debug('会话已加载', { sessionId: session.value?.id, status: session.value?.status })
        
        // 尝试加入会话（带重试）
        try {
          participation.value = await classroomSessionService.joinSession(session.value.id)
          log.debug('已加入会话', participation.value)
        } catch (error: any) {
          // 🆕 检查是否因为会话已结束而失败
          if (error.response?.status === 400 && error.response?.data?.detail?.includes('已结束')) {
            log.warn('会话已结束，无法加入')
            session.value = null
            return null
          }
          
          // 🆕 如果是权限错误（403），可能是班级不匹配，不重试
          if (error.response?.status === 403) {
            log.warn('无权加入该会话', error.response?.data?.detail)
            session.value = null
            return null
          }
          
          // 🆕 其他错误，如果还有重试次数，则重试
          if (retryCount < MAX_RETRIES) {
            log.warn(`加入会话失败，${RETRY_DELAY}ms后重试`, error)
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
            return findAndJoinSession(retryCount + 1)
          }
          
          // 重试次数用完，记录错误但不阻塞
          log.error('加入会话失败（已重试' + MAX_RETRIES + '次）', error)
        }
        
        // 尝试建立 WebSocket 连接（不阻塞，后台异步连接）
        if (useWebSocket.value && session.value) {
          // 🆕 添加一个短暂延迟，让页面资源加载完成后再建立 WebSocket 连接
          // 这可以避免首次连接时因资源竞争导致的超时问题
          setTimeout(() => {
            // 异步连接WebSocket，不阻塞页面加载
            connectWebSocket(session.value!.id).catch((error) => {
              log.warn('WebSocket 连接失败，降级轮询', error)
              startPolling()
            })
          }, 500)  // 延迟 500ms
        } else {
          // 不使用 WebSocket，直接使用轮询
          startPolling()
        }
        
        return session.value
      }
      
      // 如果没有找到会话，且还有重试次数，则重试
      if (retryCount < MAX_RETRIES) {
        log.debug(`未找到会话，${RETRY_DELAY}ms后重试`)
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
        return findAndJoinSession(retryCount + 1)
      }
      
      // 🆕 提供更清晰的日志说明
      log.debug('未找到可加入会话，学生可自主学习')
      return null
    } catch (error) {
      console.error('❌ 查找会话失败:', error)
      
      // 如果还有重试次数，则重试
      if (retryCount < MAX_RETRIES) {
        log.debug(`查找会话异常，${RETRY_DELAY}ms后重试`)
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
        return findAndJoinSession(retryCount + 1)
      }
      
      return null
    }
  }
  
  /**
   * 刷新会话状态（轮询时使用）
   */
  async function refreshSession() {
    if (!session.value) return
    
    try {
      const updatedSession = await classroomSessionService.getSession(session.value.id)
      if (updatedSession) {
        // 🆕 检查会话状态是否变为 ended
        const oldStatus = session.value.status
        const newStatus = updatedSession.status
        
        if (oldStatus !== 'ended' && newStatus === 'ended') {
          // 会话已结束
          // 更新会话状态
          session.value.status = 'ended'
          
          // 断开 WebSocket 连接
          disconnectWebSocket()
          
          // 停止轮询
          stopPolling()
          
          // 显示提示（仅对学生端显示，教师端不需要）
          const userStore = useUserStore()
          const isTeacher = userStore.user?.role === 'teacher'
          if (!isTeacher) {
            alert('课程已结束，感谢您的参与！')
          }
          
          // 不再继续更新，直接返回
          return
        }
        
        // 检查是否有实际变化（用于日志记录）
        const oldDisplayCellIds = JSON.stringify((session.value.settings as any)?.display_cell_ids || (session.value.settings as any)?.displayCellIds || [])
        const newDisplayCellIds = JSON.stringify((updatedSession.settings as any)?.display_cell_ids || (updatedSession.settings as any)?.displayCellIds || [])
        const hasDisplayCellIdsChanged = oldDisplayCellIds !== newDisplayCellIds
        
        const oldCurrentCellId = (session.value as any)?.current_cell_id ?? session.value?.currentCellId ?? null
        const newCurrentCellId = (updatedSession as any)?.current_cell_id ?? updatedSession.currentCellId ?? null
        const hasCurrentCellIdChanged = oldCurrentCellId !== newCurrentCellId
        
        // 提取 display_cell_ids，确保它是数组
        const rawSettings = updatedSession.settings || {}
        const displayCellIdsFromSettings = rawSettings.display_cell_ids || rawSettings.displayCellIds || []
        const displayCellIdsArray = Array.isArray(displayCellIdsFromSettings) ? displayCellIdsFromSettings : []
        
        // 总是使用响应式方式更新，确保 Vue 能够检测到变化
        // 创建新对象和新的 settings 对象确保响应式更新
        session.value = {
          ...updatedSession,
          settings: {
            ...rawSettings,
            display_cell_ids: displayCellIdsArray,  // 确保使用数组格式
            display_cell_orders: rawSettings.display_cell_orders,  // 🆕 保持 display_cell_orders
          }
        }
        
        // 更新 currentCellId
        const cellId = (updatedSession as any)?.current_cell_id ?? updatedSession.currentCellId ?? null
        currentCellId.value = cellId
        
        // 会话状态已更新
      }
    } catch (error) {
      console.error('❌ 刷新会话状态失败:', error)
      // 如果会话不存在或已结束，停止轮询
      if ((error as any).response?.status === 404) {
        stopPolling()
        session.value = null
        participation.value = null
      }
    }
  }
  
  /**
   * 开始轮询会话状态
   */
  function startPolling() {
    if (pollingInterval) return // 已经在轮询
    
    // 开始轮询会话状态
    pollingInterval = setInterval(() => {
      refreshSession()
    }, POLLING_INTERVAL)
  }
  
  /**
   * 停止轮询会话状态
   */
  function stopPolling() {
    if (pollingInterval) {
      // 停止轮询会话状态
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }
  
  /**
   * 连接 WebSocket
   * 先注册监听器再连接，避免连接后首条消息（如 connected/cell_changed）在监听器就绪前到达导致学生端不自动刷新。
   */
  async function connectWebSocket(sessionId: number) {
    try {
      const token = getAuthToken()
      if (!token) {
        console.error('❌ 未找到认证 Token')
        throw new Error('No auth token')
      }

      // 先注册监听器，再建立连接，确保不会错过连接后的首条消息
      setupWebSocketListeners()

      await websocketService.connect(sessionId, token)
      isWebSocketConnected.value = true
    } catch (error) {
      console.error('❌ WebSocket 连接失败:', error)
      isWebSocketConnected.value = false
      throw error
    }
  }
  
  /**
   * 设置 WebSocket 消息监听器
   */
  function setupWebSocketListeners() {
    // 1. 监听连接成功消息
    websocketService.on('connected', (message: WebSocketMessage) => {
      if (message.data.current_state && session.value) {
        // 🔧 修复：创建新对象以触发 Vue 响应式更新
        const newSession = { ...session.value }
        newSession.status = message.data.current_state.status
        newSession.settings = {
          ...session.value.settings,
          display_cell_orders: message.data.current_state.display_cell_orders,
          display_mode: message.data.current_state.display_mode || 'window',
        }
        
        // 🆕 保留或更新教师和课程信息（如果 WebSocket 消息中包含）
        if (message.data.current_state.teacher_name !== undefined) {
          newSession.teacherName = message.data.current_state.teacher_name
        }
        if (message.data.current_state.lesson_title !== undefined) {
          newSession.lessonTitle = message.data.current_state.lesson_title
        }
        if (message.data.current_state.classroom_name !== undefined) {
          newSession.classroomName = message.data.current_state.classroom_name
        }
        
        // 🔧 重新赋值整个 session 对象
        session.value = newSession
        currentCellId.value = message.data.current_state.current_cell_id
        
        // 如果初始状态包含display_mode，触发回调
        if (message.data.current_state.display_mode && onDisplayModeChanged) {
          onDisplayModeChanged(message.data.current_state.display_mode as 'fullscreen' | 'window')
        }
        
        // 初始状态已更新
      }
    })
    
    // 2. 监听内容切换消息（核心）
    websocketService.on('cell_changed', (message: WebSocketMessage) => {
      console.log('📨 学生端收到 cell_changed 消息:', message)

      if (session.value) {
        // 🆕 保存原始状态，确保 cell_changed 消息不会改变会话状态
        const originalStatus = session.value.status
        const originalDisplayOrders = session.value.settings?.display_cell_orders

        // 🔧 修复：创建新对象以触发 Vue 响应式更新
        const newSession = { ...session.value }

        // 🆕 显式保持会话状态不变
        newSession.status = originalStatus

        // 更新 display_cell_orders
        if (message.data.display_cell_orders !== undefined) {
          newSession.settings = {
            ...session.value.settings,
            display_cell_orders: message.data.display_cell_orders,
          }
          console.log('✅ display_cell_orders 已更新:', {
            from: originalDisplayOrders,
            to: message.data.display_cell_orders
          })
        }

        // 更新 current_cell_id
        if (message.data.current_cell_id !== undefined) {
          currentCellId.value = message.data.current_cell_id
        }

        session.value = newSession
        console.log('🔄 session 已更新:', {
          status: session.value.status,
          displayOrders: session.value.settings?.display_cell_orders
        })

        // 🆕 验证状态未被错误修改
        if (session.value.status !== originalStatus) {
          console.error('⚠️ 严重错误: cell_changed 消息导致会话状态变化!', {
            original: originalStatus,
            current: session.value.status
          })
        }
      }
    })
    
    // 🆕 监听显示模式变化
    websocketService.on('display_mode_changed', (message: WebSocketMessage) => {
      if (session.value && message.data.display_mode) {
        const newSession = { ...session.value }
        newSession.settings = {
          ...session.value.settings,
          display_mode: message.data.display_mode,
        }
        session.value = newSession
        
        // 触发显示模式变化事件（供组件监听）
        if (onDisplayModeChanged) {
          onDisplayModeChanged(message.data.display_mode)
        }
      }
    })
    
    // 3. 监听会话状态变化
    websocketService.on('session_status_changed', (message: WebSocketMessage) => {
      if (session.value && message.data.status) {
        const newSession = { ...session.value }
        newSession.status = message.data.status
        session.value = newSession
        
        // 如果会话结束，断开连接
        if (message.data.status === 'ended') {
          disconnectWebSocket()
        }
      }
    })
    
    // 🆕 监听会话结束（教师主动结束课程或异常退出）
    websocketService.on('session_ended', (message: WebSocketMessage) => {
      // 🆕 验证消息中的 session_id 是否匹配当前会话
      const messageSessionId = message.data?.session_id
      const currentSessionId = session.value?.id
      
      if (messageSessionId && currentSessionId && messageSessionId !== currentSessionId) {
        log.warn('忽略不匹配的 session_ended', { messageSessionId, currentSessionId })
        return  // 忽略不匹配的消息
      }
      
      if (session.value) {
        session.value.status = 'ended'
        
        // 断开 WebSocket
        disconnectWebSocket()
        
        // 显示提示（仅对学生端显示，教师端不需要）
        const userStore = useUserStore()
        const isTeacher = userStore.user?.role === 'teacher'
        if (!isTeacher) {
          // 根据结束原因显示不同的提示
          const reason = message.data?.reason
          let messageText = '课程已结束，感谢您的参与！'
          
          if (reason === 'teacher_disconnected') {
            messageText = '教师已断开连接，课程已自动结束。感谢您的参与！'
          } else if (message.data?.message) {
            messageText = message.data.message
          }
          
          alert(messageText)
        }
        
        // 可选：重定向到学生主页
        // router.push('/student')
      }
    })
    
    // 4. 监听活动开始
    websocketService.on('activity_started', (message: WebSocketMessage) => {
      // TODO: 触发活动界面显示
    })
    
    // 5. 监听活动结束
    websocketService.on('activity_ended', (message: WebSocketMessage) => {
      // TODO: 显示活动结果
    })
    
    // 6. 监听错误消息
    websocketService.on('error', (message: WebSocketMessage) => {
      console.error('Server error:', message.data)
      // TODO: 显示错误提示
    })
    
    // 7. 监听重连失败事件
    websocketService.on('reconnect_failed', (message: WebSocketMessage) => {
      log.warn('WebSocket 重连失败，降级轮询')
      isWebSocketConnected.value = false
      startPolling()
    })
    
    // 8. 监听连接关闭事件（服务器主动关闭）
    websocketService.on('connection_closed', (message: WebSocketMessage) => {
      log.warn('WebSocket 被服务器关闭', message.data)
      isWebSocketConnected.value = false
      
      // 🆕 更严格的判断：只有在确认是会话结束的情况下才修改状态
      const code = message.data?.code
      const reason = message.data?.reason || ''
      
      // 只有 code=1008 且原因明确包含"结束"相关词汇时，才认为会话结束
      if (code === 1008 && (reason.includes('ended') || reason.includes('结束') || reason.includes('已结束'))) {
        console.error('🛑 服务器确认会话已结束')
        if (session.value) {
          session.value.status = 'ended'
        }
        stopPolling()
      } else {
        startPolling()
      }
    })
  }
  
  /**
   * 断开 WebSocket 连接
   * 断开前清除所有监听器，避免重连或再次连接时重复注册导致重复处理消息。
   */
  function disconnectWebSocket() {
    websocketService.removeAllListeners()
    websocketService.disconnect()
    isWebSocketConnected.value = false
  }
  
  /**
   * 离开会话
   */
  async function leaveSession() {
    // 断开 WebSocket
    disconnectWebSocket()
    // 停止轮询
    stopPolling()
    
    if (session.value) {
      try {
        await classroomSessionService.leaveSession(session.value.id)
      } catch (error) {
        console.error('Failed to leave session:', error)
      }
    }
    session.value = null
    participation.value = null
  }
  
  /**
   * 更新进度（通过 WebSocket）
   */
  async function updateProgress(
    completedCellIds: number[], 
    currentCellIdParam?: number,
    progressPercentageParam?: number  // 🆕 可选的进度百分比参数
  ) {
    if (!participation.value || !session.value) return
    
    // 计算进度百分比（如果未提供参数，则基于 completedCellIds 计算）
    let progressPercentage: number
    if (progressPercentageParam !== undefined) {
      // 使用提供的进度百分比
      progressPercentage = progressPercentageParam
    } else {
      // 默认计算方式（向后兼容）
      const totalCells = session.value.settings?.display_cell_orders?.length || 
                        (completedCellIds.length > 0 ? completedCellIds.length : 10)
      progressPercentage = (completedCellIds.length / totalCells) * 100
    }
    
    // 如果 WebSocket 已连接，通过 WebSocket 发送进度更新
    if (isWebSocketConnected.value) {
      websocketService.send({
        type: 'update_progress',
        timestamp: new Date().toISOString(),
        data: {
          current_cell_id: currentCellIdParam || currentCellId.value,
          completed_cells: completedCellIds,
          progress_percentage: progressPercentage,
        },
      })
    }
    
    // 更新本地状态
    if (currentCellIdParam) {
      currentCellId.value = currentCellIdParam
    }
  }
  
  /**
   * 获取当前应该显示的Cell ID
   * 在课堂模式下，只有教师指定的Cell才显示
   */
  const displayCellId = computed(() => {
    if (isInClassroomMode.value) {
      // 课堂模式：严格遵循教师指定的Cell
      // 如果 currentCellId 为 null，则不显示任何Cell（等待教师切换）
      // 使用 current_cell_id（后端字段名）或 currentCellId（前端字段名）
      const cellId = (session.value as any)?.current_cell_id ?? session.value?.currentCellId ?? currentCellId.value ?? null
      return cellId
    }
    // 非课堂模式：返回null，显示所有Cell
    return null
  })
  
  /**
   * 是否应该限制显示
   * 课堂模式下默认严格同步，只显示教师指定的Cell
   */
  const shouldSyncDisplay = computed(() => {
    if (!isInClassroomMode.value) {
      return false
    }
    // 课堂模式下，如果 sync_mode 未设置或为 strict，则严格同步
    const syncMode = session.value?.settings?.sync_mode
    return syncMode === 'strict' || syncMode === undefined || syncMode === null
  })
  
  /**
   * 是否有可显示的内容
   * 在课堂模式下，如果教师还未切换到任何Cell，则没有内容可显示
   * 支持新方式（display_cell_orders）和旧方式（display_cell_ids）
   * v2.0: 在 PREPARING 状态下，学生不能看到内容（等待教师开始上课）
   */
  const hasDisplayableContent = computed(() => {
    if (!isInClassroomMode.value) {
      return true  // 非课堂模式，显示所有内容
    }

    // v2.0: PREPARING 状态下，学生不能看到内容
    const normalized = normalizeSessionStatus(session.value?.status || 'ended')
    if (normalized === 'preparing') {
      return false
    }

    const settings = session.value?.settings

    // 优先检查新方式：display_cell_orders
    const displayOrders = settings?.display_cell_orders
    if (displayOrders && Array.isArray(displayOrders)) {
      // v2.0: 移除PAUSED状态，只检查TEACHING状态
      const currentStatus = normalizeSessionStatus(session.value?.status || 'ended')
      // 在 TEACHING 状态下，即使display_cell_orders为空也认为"有内容可显示"
      // v2.0: 移除PAUSED状态，只在TEACHING状态下认为"有内容可显示"
      if (currentStatus === 'teaching') {
        return true  // TEACHING 状态下，认为"有内容可显示"（即使是空数组）
      }
      // 在其他状态下，空数组表示没有内容
      return displayOrders.length > 0
    }
    
    // 🔄 向后兼容：检查旧方式 display_cell_ids
    const displayCellIdsFromSession = settings?.display_cell_ids || 
                                     settings?.displayCellIds || []
    const multiSelectIds = Array.isArray(displayCellIdsFromSession) ? displayCellIdsFromSession : []
    
    if (multiSelectIds.length > 0) {
      return true  // 旧方式：有选中的模块
    }
    
    // 单选模式：检查 displayCellId
    return displayCellId.value !== null
  })
  
  // 初始化（不要在 composable 中自动调用，让调用方控制）
  // onMounted(async () => {
  //   // 尝试查找并加入会话
  //   await findAndJoinSession()
  // })
  
  onUnmounted(() => {
    // 断开 WebSocket
    disconnectWebSocket()
    // 停止轮询
    stopPolling()
    // 离开会话
    leaveSession()
  })
  
  return {
    session,
    participation,
    currentCellId,
    isInClassroomMode,
    isWebSocketConnected,
    displayCellId,
    shouldSyncDisplay,
    hasDisplayableContent,
    findAndJoinSession,
    leaveSession,
    updateProgress,
  }
}

