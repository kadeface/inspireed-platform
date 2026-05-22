/**
 * WebSocket 管理 Composable
 *
 * 管理课堂会话的 WebSocket 连接，替代 HTTP 轮询
 */

import { ref, watch, onMounted, onBeforeUnmount, type Ref } from 'vue'
import { useUserStore } from '@/store/user'
import { createLogger } from '@/utils/logger'

const log = createLogger('ClassroomWebSocket')

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

  /** MathLab 竞赛相关 WebSocket 事件 */
  onMathlabContest?: (type: string, data: Record<string, unknown>) => void

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
    onMathlabContest,
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
   * 构建完整的 WebSocket URL（含 JWT，后端教师端 ws/teacher 需要 token 校验）
   */
  function buildWebSocketUrl(): string {
    let apiBase = import.meta.env.VITE_API_BASE_URL || ''
    if (!apiBase) {
      apiBase = import.meta.env.DEV ? 'http://localhost:8000' : `${window.location.origin}/api/v1`
    } else if (!import.meta.env.DEV && /(^|\/\/)[^/?#]*:8000(?:\/|$|\?|#)/.test(apiBase)) {
      apiBase = `${window.location.origin}/api/v1`
    }
    const wsProtocol = apiBase.startsWith('https') ? 'wss:' : 'ws:'
    const wsHost = apiBase.replace(/^https?:\/\//, '').replace(/\/api\/v1\/?$/, '')
    const token = getToken()
    const base = `${wsProtocol}//${wsHost}${endpointUrl.value}`
    return token ? `${base}?token=${encodeURIComponent(token)}` : base
  }

  /**
   * 获取 JWT Token（与 useRealtimeChannel / API 一致：userStore + localStorage）
   */
  function getToken(): string {
    const userStore = useUserStore()
    return userStore.token || localStorage.getItem('access_token') || ''
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
      log.warn('WebSocket 未连接，无法发送消息', message)
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
      const raw = JSON.parse(event.data)
      if (!raw || typeof raw !== 'object') {
        log.warn('收到无效 WebSocket 消息（非对象）', raw)
        return
      }
      const message = raw as Partial<WebSocketMessage>
      const type = message.type
      const data = message.data
      if (!type || typeof type !== 'string') {
        log.warn('收到无效 WebSocket 消息（缺少 type）', message)
        return
      }

      // 心跳等不刷屏，其他消息用 debug 级别
      if (type !== 'pong') {
        log.debug('收到 WebSocket 消息', type, data)
      }

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

        case 'mathlab_contest_started':
        case 'mathlab_contest_task_changed':
        case 'mathlab_contest_submission':
        case 'mathlab_contest_ended':
          onMathlabContest?.(type, data)
          break

        case 'pong':
          // 心跳响应，无需处理
          break

        default:
          log.warn('未知 WebSocket 消息类型', type)
      }
    } catch (error) {
      console.error('❌ 解析 WebSocket 消息失败:', error)
    }
  }

  /**
   * 连接 WebSocket
   */
  function connect() {
    // 无有效 endpoint 时不连接（例如 session 尚未创建）
    if (!endpointUrl.value || !endpointUrl.value.startsWith('/')) {
      return
    }

    if (ws.value?.readyState === WebSocket.OPEN) {
      log.debug('WebSocket 已连接，跳过')
      return
    }

    if (isConnecting.value) {
      log.debug('WebSocket 正在连接中，跳过')
      return
    }

    isConnecting.value = true

    try {
      const wsUrl = buildWebSocketUrl()
      const logUrl = wsUrl.includes('?') ? wsUrl.split('?')[0] : wsUrl
      log.debug('连接 WebSocket', logUrl)

      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = (event) => {
        log.debug('WebSocket 已连接')
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
        log.debug('WebSocket 已关闭', event.code, event.reason)
        isConnected.value = false
        isConnecting.value = false

        // 停止心跳
        stopHeartbeat()

        onDisconnected?.(event)

        // 如果不是手动关闭，尝试重连
        if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts) {
          reconnectAttempts.value++
          log.debug(`${reconnectDelay / 1000}秒后尝试重连`, reconnectAttempts.value, maxReconnectAttempts)

          setTimeout(() => {
            if (!isConnected.value) {
              connect()
            }
          }, reconnectDelay)
        } else if (reconnectAttempts.value >= maxReconnectAttempts) {
          // 达到最大重连次数，停止重连
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
   * 监听 endpointUrl 变化：当 session 创建后 endpoint 有效时自动连接
   */
  watch(
    endpointUrl,
    (url) => {
      if (url && url.startsWith('/') && !isConnected.value && !isConnecting.value) {
        setTimeout(() => connect(), 100)
      }
    },
    { immediate: true }
  )

  onMounted(() => {
    // 挂载时若 endpoint 已有效则连接
    if (endpointUrl.value && endpointUrl.value.startsWith('/')) {
      setTimeout(() => connect(), 100)
    }
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
