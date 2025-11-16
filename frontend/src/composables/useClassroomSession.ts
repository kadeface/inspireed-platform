/**
 * 课堂会话 Composable（学生端）
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import classroomSessionService from '../services/classroomSession'
import type { ClassSession, StudentParticipation } from '../types/classroomSession'

export function useClassroomSession(lessonId: number) {
  const route = useRoute()
  const session = ref<ClassSession | null>(null)
  const participation = ref<StudentParticipation | null>(null)
  const currentCellId = ref<number | null>(null)
  const isInClassroomMode = computed(() => {
    return session.value?.status === 'active'
  })
  
  // 轮询定时器（用于定期获取会话状态）
  let pollingInterval: ReturnType<typeof setInterval> | null = null
  const POLLING_INTERVAL = 1000 // 每1秒轮询一次，减少延迟
  
  // WebSocket连接（未来实现）
  // const ws = ref<WebSocket | null>(null)
  
  /**
   * 查找并加入会话
   */
  async function findAndJoinSession() {
    try {
      // 获取该教案的所有活跃会话
      const sessions = await classroomSessionService.listSessions(lessonId, 'active')
      
      if (sessions.length > 0) {
        // 找到第一个活跃的会话
        const activeSession = sessions[0]
        
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
          // 如果已经加入过（403或其他错误），继续使用会话
          if (error.response?.status === 403) {
            console.log('ℹ️ 已经加入过会话，继续使用')
          } else {
            console.error('❌ 加入会话失败:', error)
          }
        }
        
        // 开始轮询会话状态（实时获取教师切换的内容）
        startPolling()
        
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
   * 离开会话
   */
  async function leaveSession() {
    stopPolling() // 停止轮询
    
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
   * 更新进度
   */
  async function updateProgress(completedCellIds: number[], currentCellId?: number) {
    if (!participation.value) return
    
    // 这里应该通过WebSocket或API更新进度
    // 暂时先不实现，后续可以通过WebSocket实时更新
    if (currentCellId) {
      currentCellId.value = currentCellId
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
   * 支持单选模式（displayCellId）和多选模式（display_cell_ids 数组）
   */
  const hasDisplayableContent = computed(() => {
    if (!isInClassroomMode.value) {
      return true  // 非课堂模式，显示所有内容
    }
    
    // 检查多选模式：如果有 display_cell_ids 数组且长度 > 0，有内容可显示
    const settings = session.value?.settings
    const displayCellIdsFromSession = settings?.display_cell_ids || 
                                     settings?.displayCellIds || []
    const multiSelectIds = Array.isArray(displayCellIdsFromSession) ? displayCellIdsFromSession : []
    
    if (multiSelectIds.length > 0) {
      return true  // 多选模式：有选中的模块
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
    displayCellId,
    shouldSyncDisplay,
    hasDisplayableContent,
    findAndJoinSession,
    leaveSession,
    updateProgress,
  }
}

