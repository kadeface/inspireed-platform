/**
 * 课堂会话 Composable（学生端）
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import classroomSessionService from '../services/classroomSession'
import { websocketService, type WebSocketMessage } from '../services/websocket'
import { getAuthToken } from '../utils/auth'
import type { ClassSession, StudentParticipation } from '../types/classroomSession'

export function useClassroomSession(lessonId: number) {
  const route = useRoute()
  const session = ref<ClassSession | null>(null)
  const participation = ref<StudentParticipation | null>(null)
  const currentCellId = ref<number | null>(null)
  const isInClassroomMode = computed(() => {
    // 在 pending 和 active 状态下都认为是课堂模式
    return session.value?.status === 'active' || session.value?.status === 'pending'
  })
  
  // 轮询定时器（用于定期获取会话状态）- 降级方案
  let pollingInterval: ReturnType<typeof setInterval> | null = null
  const POLLING_INTERVAL = 5000 // 降级时使用5秒轮询（减少负载）
  
  // WebSocket连接状态
  const isWebSocketConnected = ref<boolean>(false)
  const useWebSocket = ref<boolean>(true) // 默认启用 WebSocket
  
  /**
   * 查找并加入会话
   */
  async function findAndJoinSession() {
    try {
      // 🆕 获取该教案的所有会话（包括 pending 和 active 状态）
      // 先尝试查找 active 状态的会话
      let sessions = await classroomSessionService.listSessions(lessonId, 'active')
      
      // 如果没有 active 状态的会话，尝试查找 pending 状态的会话
      if (sessions.length === 0) {
        const allSessions = await classroomSessionService.listSessions(lessonId)
        sessions = allSessions.filter(s => s.status === 'pending' || s.status === 'active')
      }
      
      if (sessions.length > 0) {
        // 找到第一个可加入的会话（优先 active，其次 pending）
        const activeSession = sessions.find(s => s.status === 'active') || sessions[0]
        
        // 🆕 检查会话状态
        if (activeSession.status === 'ended') {
          console.log('⏹️ 会话已结束，无法加入')
          alert('该课程已结束，无法加入')
          return
        }
        
        // 🆕 如果是 pending 状态，提示学生等待
        if (activeSession.status === 'pending') {
          console.log('⏳ 会话处于等待状态，等待教师开始上课')
        }
        
        // 确保 settings 被正确设置
        if (!activeSession.settings) {
          activeSession.settings = {}
        }
        
        session.value = activeSession
        
        // 处理字段映射：后端可能返回 current_cell_id（snake_case）或 currentCellId（camelCase）
        const cellId = (activeSession as any).current_cell_id ?? activeSession.currentCellId ?? null
        currentCellId.value = cellId
        
        // 读取 display_cell_ids（多选模式）
        const displayCellIdsFromSession = (activeSession.settings as any)?.display_cell_ids || 
                                         (activeSession.settings as any)?.displayCellIds || []
        
        console.log('🎓 找到活跃会话:', {
          sessionId: activeSession.id,
          status: activeSession.status,
          currentCellId: cellId,
          settings: activeSession.settings,
          displayCellIds: displayCellIdsFromSession,
          displayCellIdsLength: Array.isArray(displayCellIdsFromSession) ? displayCellIdsFromSession.length : 0,
        })
        
        // 尝试加入会话
        try {
          participation.value = await classroomSessionService.joinSession(activeSession.id)
          console.log('✅ 成功加入会话:', participation.value)
        } catch (error: any) {
          // 🆕 检查是否因为会话已结束而失败
          if (error.response?.status === 400 && error.response?.data?.detail?.includes('已结束')) {
            console.log('⏹️ 会话已结束')
            alert('该课程已结束，无法加入')
            session.value = null
            return
          }
          
          // 如果已经加入过（403或其他错误），继续使用会话
          if (error.response?.status === 403) {
            console.log('ℹ️ 已经加入过会话，继续使用')
          } else {
            console.error('❌ 加入会话失败:', error)
          }
        }
        
        // 尝试建立 WebSocket 连接
        if (useWebSocket.value) {
          try {
            await connectWebSocket(activeSession.id)
          } catch (error) {
            console.warn('⚠️ WebSocket 连接失败，降级到轮询模式')
            startPolling()
          }
        } else {
          // 不使用 WebSocket，直接使用轮询
          startPolling()
        }
        
        return activeSession
      } else {
        console.log('ℹ️ 未找到活跃会话')
      }
      
      return null
    } catch (error) {
      console.error('Failed to find session:', error)
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
          }
        }
        
        // 更新 currentCellId
        const cellId = (updatedSession as any)?.current_cell_id ?? updatedSession.currentCellId ?? null
        currentCellId.value = cellId
        
        // 只在有实际变化时记录日志，但如果有 displayCellIds 则总是记录
        if (hasDisplayCellIdsChanged || hasCurrentCellIdChanged || session.value.status !== updatedSession.status || displayCellIdsArray.length > 0) {
          console.log('🔄 会话状态已更新:', {
            sessionId: updatedSession.id,
            status: updatedSession.status,
            currentCellId: cellId,
            settings: rawSettings,
            settingsKeys: Object.keys(rawSettings),
            displayCellIds: displayCellIdsArray,
            displayCellIdsLength: displayCellIdsArray.length,
            displayCellIdsType: typeof displayCellIdsArray,
            isArray: Array.isArray(displayCellIdsArray),
            rawDisplayCellIds: displayCellIdsFromSettings,
            hasDisplayCellIdsChanged,
            hasCurrentCellIdChanged,
          })
        }
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
    
    console.log('🔄 开始轮询会话状态（每1秒）')
    pollingInterval = setInterval(() => {
      refreshSession()
    }, POLLING_INTERVAL)
  }
  
  /**
   * 停止轮询会话状态
   */
  function stopPolling() {
    if (pollingInterval) {
      console.log('⏹️ 停止轮询会话状态')
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }
  
  /**
   * 连接 WebSocket
   */
  async function connectWebSocket(sessionId: number) {
    try {
      // 获取认证 Token
      const token = getAuthToken()
      if (!token) {
        console.error('❌ 未找到认证 Token')
        throw new Error('No auth token')
      }
      
      // 连接 WebSocket
      await websocketService.connect(sessionId, token)
      isWebSocketConnected.value = true
      
      // 监听消息
      setupWebSocketListeners()
      
      console.log('✅ WebSocket 连接已建立')
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
      console.log('🎉 WebSocket 已连接，接收初始状态:', message.data)
      
      // 更新会话状态
      if (message.data.current_state && session.value) {
        // 🔧 修复：创建新对象以触发 Vue 响应式更新
        const newSession = { ...session.value }
        newSession.status = message.data.current_state.status
        newSession.settings = {
          ...session.value.settings,
          display_cell_orders: message.data.current_state.display_cell_orders,
        }
        
        // 🔧 重新赋值整个 session 对象
        session.value = newSession
        currentCellId.value = message.data.current_state.current_cell_id
        
        console.log('🔧 初始状态已更新:', {
          status: newSession.status,
          displayCellOrders: newSession.settings?.display_cell_orders,
          currentCellId: message.data.current_state.current_cell_id,
        })
      }
    })
    
    // 2. 监听内容切换消息（核心）
    websocketService.on('cell_changed', (message: WebSocketMessage) => {
      console.log('🔄 收到内容切换消息:', message.data)
      
      if (session.value) {
        // 🔧 修复：创建新对象以触发 Vue 响应式更新
        const newSession = { ...session.value }
        
        // 更新 display_cell_orders
        if (message.data.display_cell_orders !== undefined) {
          newSession.settings = {
            ...session.value.settings,
            display_cell_orders: message.data.display_cell_orders,
          }
        }
        
        // 更新 current_cell_id
        if (message.data.current_cell_id !== undefined) {
          currentCellId.value = message.data.current_cell_id
        }
        
        // 🔧 重新赋值整个 session 对象，确保响应式触发
        session.value = newSession
        
        console.log('✅ 内容已同步:', {
          displayCellOrders: session.value.settings?.display_cell_orders,
          currentCellId: currentCellId.value,
        })
      }
    })
    
    // 3. 监听会话状态变化
    websocketService.on('session_status_changed', (message: WebSocketMessage) => {
      console.log('📊 会话状态变化:', message.data)
      
      if (session.value) {
        session.value.status = message.data.status
        
        // 如果会话结束，断开连接
        if (message.data.status === 'ended') {
          console.log('⏹️ 会话已结束')
          disconnectWebSocket()
        }
      }
    })
    
    // 🆕 监听会话结束（教师主动结束课程）
    websocketService.on('session_ended', (message: WebSocketMessage) => {
      console.log('⏹️ 教师已结束课程:', message.data)
      
      if (session.value) {
        session.value.status = 'ended'
        
        // 断开 WebSocket
        disconnectWebSocket()
        
        // 显示提示
        alert('教师已结束课程，感谢您的参与！')
        
        // 可选：重定向到学生主页
        // router.push('/student')
      }
    })
    
    // 4. 监听活动开始
    websocketService.on('activity_started', (message: WebSocketMessage) => {
      console.log('🎯 活动开始:', message.data)
      // TODO: 触发活动界面显示
    })
    
    // 5. 监听活动结束
    websocketService.on('activity_ended', (message: WebSocketMessage) => {
      console.log('✅ 活动结束:', message.data)
      // TODO: 显示活动结果
    })
    
    // 6. 监听错误消息
    websocketService.on('error', (message: WebSocketMessage) => {
      console.error('❌ 服务器错误:', message.data)
      // TODO: 显示错误提示
    })
  }
  
  /**
   * 断开 WebSocket 连接
   */
  function disconnectWebSocket() {
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
   * 在 PENDING 状态下，学生不能看到内容（等待教师开始上课）
   */
  const hasDisplayableContent = computed(() => {
    if (!isInClassroomMode.value) {
      return true  // 非课堂模式，显示所有内容
    }
    
    // 🆕 PENDING 状态下，学生不能看到内容
    if (session.value?.status === 'pending') {
      return false
    }
    
    const settings = session.value?.settings
    
    // 🆕 优先检查新方式：display_cell_orders
    const displayOrders = settings?.display_cell_orders
    if (displayOrders && Array.isArray(displayOrders) && displayOrders.length > 0) {
      return true  // 新方式：有选中的模块
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

