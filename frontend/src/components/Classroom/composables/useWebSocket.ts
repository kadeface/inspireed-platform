/**
 * WebSocket 管理 Composable
 *
 * 管理课堂会话的 WebSocket 连接，替代 HTTP 轮询
 */

import { ref, onMounted, onBeforeUnmount, type Ref } from 'vue'
import { useAuthStore } from '@/store/auth'

export interface WebSocketMessage {
  type: string
  timestamp: string
  data: Record<string, any>
}

export interface UseWebSocketOptions {
  /**
   * 连接端点 URL（包含 session_id 或 lesson_id）
   */
  endpointUrl: Ref<string>

  /**
   * WebSocket 连接类型（session 或 lesson）
   */
  scope: 'session' | 'lesson'

  /**
   * 连接建立回调
   */
  onConnected?: (event: Event) => void

  /**
   * 连接关闭回调
   */
  onDisconnected?: (event: CloseEvent) => void

  /**
   * 连接错误回调
   */
  onError?: (event: Event) => void

  /**
   * 消息接收回调（参与者加入）
   */
  onParticipantJoined?: (data: any) => void

  /**
   * 消息接收回调（会话状态变化）
   */
  onSessionStatusChanged?: (data: any) => void

  /**
   * 消息接收回调（内容切换）
   */
  onCellChanged?: (data: any) => void

  /**
   * 消息接收回调（会话结束）
   */
  onSessionEnded?: (data: any) => void

  /**
   * 消息接收回调（活动统计更新）
   */
  onSubmissionStatisticsUpdated?: (data: any) => void

  /**
   * 心跳间隔（毫秒），默认 30000（30秒）
   */
  heartbeatInterval?: number
}

export function useWebSocket(options: UseWebSocketOptions) {
  const {
    endpointUrl,
    scope,
    onConnected,
    onDisconnected,
    onError,
    onParticipantJoined,
    onSessionStatusChanged,
    onCellChanged,
    onSessionEnded,
    onSubmissionStatisticsUpdated,
    heartbeatInterval = 30000,
  } = options

  // WebSocket 连接实例
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)

  // 心跳定时器
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  // 重连尝试次数
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = 3000 // 3秒后重连

  /**
   * 构建完整的 WebSocket URL
   */
  function buildWebSocketUrl(): string {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const wsProtocol = apiBase.startsWith('https') ? 'wss:' : 'ws:'
    const wsHost = apiBase.replace(/^https?:\/\//, '')

    return `${wsProtocol}//${wsHost}${endpointUrl.value}`
  }

  /**
   * 获取 JWT Token
   */
  function getToken(): string {
    const authStore = useAuthStore()
    return authStore.token || ''
  }

  /**
   * 启动心跳
   */
  function startHeartbeat() {
    stopHeartbeat()

    heartbeatTimer = setInterval(() => {
      if (isConnected.value && ws.value) {
        sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString(),
          data: {},
        })
      }
    }, heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  /**
   * 发送消息
   */
  function sendMessage(message: WebSocketMessage) {
    if (ws.value && isConnected.value) {
      ws.value.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket 未连接，无法发送消息:', message)
    }
  }

  /**
   * 请求统计信息（教师端）
   */
  function requestStatistics(cellId: number | string, lessonId: number) {
    sendMessage({
      type: 'request_statistics',
      timestamp: new Date().toISOString(),
      data: {
        cell_id: cellId,
        lesson_id: lessonId,
      },
    })
  }

  /**
   * 处理接收到的消息
   */
  function handleMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)
      const { type, data } = message

      console.log('📨 收到 WebSocket 消息:', type, data)

      switch (type) {
        case 'teacher_connected':
        case 'connected':
          isConnected.value = true
          isConnecting.value = false
          reconnectAttempts.value = 0
          onConnected?.(event)
          break

        case 'participant_joined':
          onParticipantJoined?.(data)
          break

        case 'session_status_changed':
          onSessionStatusChanged?.(data)
          break

        case 'cell_changed':
          onCellChanged?.(data)
          break

        case 'session_ended':
          onSessionEnded?.(data)
          break

        case 'submission_statistics_updated':
          onSubmissionStatisticsUpdated?.(data)
          break

        case 'pong':
          // 心跳响应，无需处理
          break

        default:
          console.log('⚠️ 未知 WebSocket 消息类型:', type)
      }
    } catch (error) {
      console.error('❌ 解析 WebSocket 消息失败:', error)
    }
  }

  /**
   * 连接 WebSocket
   */
  function connect() {
    if (ws.value?.readyState === WebSocket.OPEN) {
      console.log('WebSocket 已连接，跳过')
      return
    }

    if (isConnecting.value) {
      console.log('WebSocket 正在连接中，跳过')
      return
    }

    isConnecting.value = true

    try {
      const token = getToken()
      const url = buildWebSocketUrl()
      const wsUrl = token ? `${url}?token=${token}` : url

      console.log('🔌 连接 WebSocket:', wsUrl)

      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = (event) => {
        console.log('✅ WebSocket 已连接')
        isConnected.value = true
        isConnecting.value = false
        reconnectAttempts.value = 0

        // 启动心跳
        startHeartbeat()

        onConnected?.(event)
      }

      ws.value.onmessage = handleMessage

      ws.value.onerror = (event) => {
        console.error('❌ WebSocket 错误:', event)
        isConnecting.value = false
        onError?.(event)
      }

      ws.value.onclose = (event) => {
        console.log('🔌 WebSocket 已关闭:', event.code, event.reason)
        isConnected.value = false
        isConnecting.value = false

        // 停止心跳
        stopHeartbeat()

        onDisconnected?.(event)

        // 如果不是手动关闭，尝试重连
        if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts) {
          reconnectAttempts.value++
          console.log(`🔄 ${reconnectDelay / 1000}秒后尝试重连 (${reconnectAttempts.value}/${maxReconnectAttempts})...`)

          setTimeout(() => {
            if (!isConnected.value) {
              connect()
            }
          }, reconnectDelay)
        } else if (reconnectAttempts.value >= maxReconnectAttempts) {
          console.error('❌ 达到最大重连次数，停止重连')
        }
      }
    } catch (error) {
      console.error('❌ 创建 WebSocket 连接失败:', error)
      isConnecting.value = false
    }
  }

  /**
   * 断开连接
   */
  function disconnect() {
    reconnectAttempts.value = maxReconnectAttempts // 阻止自动重连

    if (ws.value) {
      ws.value.close(1000, 'Manual disconnect')
      ws.value = null
    }

    isConnected.value = false
    isConnecting.value = false

    // 停止心跳
    stopHeartbeat()
  }

  /**
   * 组件挂载时自动连接
   */
  onMounted(() => {
    // 延迟连接，确保组件已完全渲染
    setTimeout(() => {
      connect()
    }, 100)
  })

  /**
   * 组件卸载前断开连接
   */
  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    // 状态
    isConnected,
    isConnecting,
    reconnectAttempts,

    // 方法
    connect,
    disconnect,
    sendMessage,
    requestStatistics,
  }
}
