/**
 * 实时通道 Composable
 * 支持学生和教师的实时通知订阅
 */
import { ref, computed, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { useUserStore } from '../store/user'

export interface ChannelDescriptor {
  scope: 'session' | 'lesson'
  id: number
}

export interface WebSocketMessage {
  event_id: string
  version: number
  type: string
  timestamp: string
  channel: {
    scope: 'session' | 'lesson'
    id: number
  }
  delivery_mode: 'cast' | 'unicast'
  data: any
  ack_token?: string
}

export type MessageHandler = (message: WebSocketMessage) => void

export class RealtimeChannelManager {
  private ws: WebSocket | null = null
  private url: string = ''
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 3000
  private heartbeatInterval: number = 30000
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private isManualClose: boolean = false
  
  // 消息去重
  private processedMessages: Set<string> = new Set()
  private maxProcessedMessages: number = 100
  
  // 事件监听器
  private eventListeners: Map<string, Set<MessageHandler>> = new Map()
  
  // 连接参数（用于重连）
  private channelDescriptor: ChannelDescriptor | null = null
  private token: string = ''
  private isTeacher: boolean = false

  /**
   * 连接实时通道
   */
  connect(channel: ChannelDescriptor, token: string, isTeacher: boolean = false): Promise<void> {
    return new Promise((resolve, reject) => {
      // 保存连接参数以便重连
      this.channelDescriptor = channel
      this.token = token
      this.isTeacher = isTeacher
      
      // 构建 WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // 获取 API 基础 URL 并移除 /api/v1 后缀（如果存在）
      let apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      if (apiBase.endsWith('/api/v1')) {
        apiBase = apiBase.replace('/api/v1', '')
      }
      
      const wsBase = apiBase.replace('http://', '').replace('https://', '')
      
      // 根据角色和通道类型选择端点
      let endpoint = ''
      if (isTeacher) {
        // 教师端点
        if (channel.scope === 'session') {
          endpoint = `/api/v1/classroom-sessions/sessions/${channel.id}/ws/teacher`
        } else {
          endpoint = `/api/v1/classroom-sessions/lessons/${channel.id}/ws/teacher`
        }
      } else {
        // 学生端点（保持兼容）
        if (channel.scope === 'session') {
          endpoint = `/api/v1/classroom-sessions/sessions/${channel.id}/ws`
        } else {
          // 学生课后模式暂时没有独立端点，可以复用课堂端点或不连接
          console.warn('⚠️ 学生端课后模式暂不支持 WebSocket')
          reject(new Error('Student lesson WebSocket not supported yet'))
          return
        }
      }
      
      this.url = `${wsProtocol}//${wsBase}${endpoint}?token=${token}`
      
      console.log(`🔌 连接实时通道 [${isTeacher ? '教师' : '学生'}]:`, channel.scope, channel.id)
      console.log(`🔗 WebSocket URL: ${this.url.replace(/token=.+$/, 'token=***')}`)
      
      try {
        this.ws = new WebSocket(this.url)
        this.isManualClose = false
        
        // 连接成功
        this.ws.onopen = () => {
          console.log('✅ 实时通道连接成功')
          console.log('  - readyState:', this.ws?.readyState)
          console.log('  - isConnected:', this.isConnected)
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }
        
        // 接收消息
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('❌ 解析消息失败:', error)
          }
        }
        
        // 连接关闭
        this.ws.onclose = (event) => {
          console.log('🔌 实时通道连接关闭:', event.code, event.reason)
          this.stopHeartbeat()
          
          // 如果不是手动关闭，尝试重连
          if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect()
          }
        }
        
        // 连接错误
        this.ws.onerror = (error) => {
          console.error('❌ 实时通道错误:', error)
          console.error('❌ 连接 URL:', this.url.replace(/token=.+$/, 'token=***'))
          console.error('❌ isTeacher:', isTeacher)
          reject(error)
        }
        
      } catch (error) {
        console.error('❌ 实时通道连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.isManualClose = true
    this.stopHeartbeat()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    // 清理监听器
    this.eventListeners.clear()
    this.processedMessages.clear()
    
    console.log('🔌 实时通道已断开')
  }

  /**
   * 订阅特定类型的消息
   * @returns 取消订阅函数
   */
  subscribe(messageType: string, handler: MessageHandler): () => void {
    if (!this.eventListeners.has(messageType)) {
      this.eventListeners.set(messageType, new Set())
    }
    this.eventListeners.get(messageType)!.add(handler)
    
    // 返回取消订阅函数
    return () => {
      this.unsubscribe(messageType, handler)
    }
  }

  /**
   * 取消订阅
   */
  unsubscribe(messageType: string, handler: MessageHandler) {
    if (this.eventListeners.has(messageType)) {
      this.eventListeners.get(messageType)!.delete(handler)
    }
  }

  /**
   * 发送消息
   */
  send(message: any) {
    console.log('📤 准备发送消息:', message.type)
    console.log('  - ws 状态:', this.ws ? `readyState=${this.ws.readyState}` : 'null')
    console.log('  - WebSocket.OPEN =', WebSocket.OPEN)
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('✅ 发送消息')
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('⚠️ 实时通道未连接，无法发送消息')
      console.warn('  - this.ws:', this.ws)
      console.warn('  - readyState:', this.ws?.readyState)
      console.warn('  - URL:', this.url)
    }
  }

  /**
   * 请求统计信息
   */
  requestStatistics(cellId: number, lessonId: number) {
    this.send({
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
  private handleMessage(message: WebSocketMessage) {
    // 消息去重
    if (message.event_id && this.processedMessages.has(message.event_id)) {
      console.log('⚠️ 重复消息已忽略:', message.event_id)
      return
    }
    
    // 记录已处理的消息
    if (message.event_id) {
      this.processedMessages.add(message.event_id)
      
      // 限制集合大小
      if (this.processedMessages.size > this.maxProcessedMessages) {
        const firstItem = this.processedMessages.values().next().value
        this.processedMessages.delete(firstItem)
      }
    }
    
    console.log('📨 收到实时消息:', message.type, message.data)
    
    // 触发对应类型的监听器
    if (this.eventListeners.has(message.type)) {
      const callbacks = this.eventListeners.get(message.type)!
      callbacks.forEach(callback => {
        try {
          callback(message)
        } catch (error) {
          console.error('❌ 消息处理回调错误:', error)
        }
      })
    }
  }

  /**
   * 重连
   */
  private reconnect() {
    if (!this.channelDescriptor || !this.token) {
      console.error('❌ 缺少重连参数')
      return
    }
    
    this.reconnectAttempts++
    console.log(`🔄 尝试重连实时通道 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
    
    setTimeout(() => {
      this.connect(this.channelDescriptor!, this.token, this.isTeacher).catch(error => {
        console.error('❌ 重连失败:', error)
      })
    }, this.reconnectDelay)
  }

  /**
   * 开始心跳
   */
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({
        type: 'ping',
        timestamp: new Date().toISOString(),
      })
    }, this.heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 获取连接状态
   */
  get isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// 全局管理器映射（支持多个通道）
const channelManagers = new Map<string, RealtimeChannelManager>()

function getChannelKey(channel: ChannelDescriptor): string {
  return `${channel.scope}:${channel.id}`
}

/**
 * 使用实时通道 Composable
 */
export function useRealtimeChannel(
  channelRef: Ref<ChannelDescriptor> | ComputedRef<ChannelDescriptor>
) {
  const userStore = useUserStore()
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const error = ref<Error | null>(null)
  
  let manager: RealtimeChannelManager | null = null
  const offFns = new Map<string, () => void>()
  
  // 判断是否为教师
  const isTeacher = computed(() => userStore.user?.role === 'teacher')

  /**
   * 连接通道
   */
  async function connect() {
    if (isConnecting.value || isConnected.value) {
      return
    }
    
    const channel = channelRef.value
    const token = userStore.token
    
    console.log('🔍 WebSocket 连接调试信息:')
    console.log('  - userStore.user:', userStore.user)
    console.log('  - userStore.user?.role:', userStore.user?.role)
    console.log('  - isTeacher.value:', isTeacher.value)
    console.log('  - channel:', channel)
    
    if (!token) {
      error.value = new Error('未登录')
      return
    }
    
    isConnecting.value = true
    error.value = null
    
    try {
      const channelKey = getChannelKey(channel)
      
      // 复用或创建管理器
      if (!channelManagers.has(channelKey)) {
        channelManagers.set(channelKey, new RealtimeChannelManager())
      }
      
      manager = channelManagers.get(channelKey)!
      
      console.log('🔌 准备连接，isTeacher =', isTeacher.value)
      await manager.connect(channel, token, isTeacher.value)
      isConnected.value = manager.isConnected
      console.log('✅ 连接完成，isConnected =', isConnected.value)
    } catch (e) {
      error.value = e as Error
      console.error('❌ 连接实时通道失败:', e)
    } finally {
      isConnecting.value = false
    }
  }

  /**
   * 断开通道
   */
  function disconnect() {
    if (manager) {
      manager.disconnect()
      manager = null
    }
    
    // 清理所有订阅
    offFns.forEach(off => off())
    offFns.clear()
    
    isConnected.value = false
  }

  /**
   * 注册事件监听器
   */
  function registerListener(type: string, handler: MessageHandler) {
    if (!manager) {
      console.warn('⚠️ 管理器未初始化，请先连接')
      return
    }
    
    const off = manager.subscribe(type, handler)
    offFns.set(type, off)
  }

  /**
   * 取消所有监听器
   */
  function unregisterAll() {
    offFns.forEach(off => off())
    offFns.clear()
  }

  /**
   * 请求统计信息
   */
  function requestStatistics(cellId: number, lessonId: number) {
    if (manager) {
      console.log('📊 请求统计信息:', { cellId, lessonId, isConnected: isConnected.value })
      manager.requestStatistics(cellId, lessonId)
    } else {
      console.warn('⚠️ 管理器未初始化，无法请求统计信息')
    }
  }

  // 组件卸载时自动断开
  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    registerListener,
    unregisterAll,
    requestStatistics,
  }
}

