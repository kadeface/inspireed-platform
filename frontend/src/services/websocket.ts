/**
 * WebSocket 服务
 */

import { getServerBaseUrl } from '../utils/url'

export interface WebSocketMessage {
  type: string
  timestamp: string
  data: any
}

export type WebSocketEventCallback = (message: WebSocketMessage) => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private url: string = ''
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 3000 // 3秒
  private heartbeatInterval: number = 30000 // 30秒
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private isManualClose: boolean = false
  
  // 事件监听器
  private eventListeners: Map<string, Set<WebSocketEventCallback>> = new Map()
  
  /**
   * 连接 WebSocket
   */
  connect(sessionId: number, token: string, timeout: number = 5000): Promise<void> {
    return new Promise((resolve, reject) => {
      // 构建 WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // 使用统一的服务器基础URL获取函数
      const serverBaseUrl = getServerBaseUrl()
      const wsBase = serverBaseUrl.replace('http://', '').replace('https://', '')
      
      this.url = `${wsProtocol}//${wsBase}/api/v1/classroom-sessions/sessions/${sessionId}/ws?token=${token}`
      
      // 连接 WebSocket
      
      // 设置连接超时
      let timeoutId: ReturnType<typeof setTimeout> | null = null
      let isResolved = false
      
      const cleanup = () => {
        if (timeoutId) {
          clearTimeout(timeoutId)
          timeoutId = null
        }
      }
      
      const resolveOnce = () => {
        if (!isResolved) {
          isResolved = true
          cleanup()
          resolve()
        }
      }
      
      const rejectOnce = (error: any) => {
        if (!isResolved) {
          isResolved = true
          cleanup()
          reject(error)
        }
      }
      
      // 设置超时
      timeoutId = setTimeout(() => {
        if (this.ws) {
          this.ws.close()
          this.ws = null
        }
        rejectOnce(new Error(`WebSocket连接超时（${timeout}ms）`))
      }, timeout)
      
      try {
        this.ws = new WebSocket(this.url)
        this.isManualClose = false
        
        // 连接成功
        this.ws.onopen = () => {
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolveOnce()
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
          this.stopHeartbeat()
          
          console.log(`🔌 WebSocket 连接关闭: code=${event.code}, reason=${event.reason || '无原因'}`)
          
          // 如果不是手动关闭，尝试重连
          if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
            // 检查关闭代码，某些代码不应该重连（如会话已结束）
            if (event.code === 1008) {
              // 1008: Policy Violation，通常是服务器主动关闭（如会话已结束）
              console.warn('⚠️ 服务器主动关闭连接，可能原因:', event.reason || '会话已结束或权限不足')
              this.handleMessage({
                type: 'connection_closed',
                timestamp: new Date().toISOString(),
                data: { code: event.code, reason: event.reason }
              })
            } else {
              // 其他情况，尝试重连
              this.reconnect(sessionId, token)
            }
          } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ WebSocket 重连次数已达上限')
            this.handleMessage({
              type: 'reconnect_failed',
              timestamp: new Date().toISOString(),
              data: { sessionId, attempts: this.reconnectAttempts }
            })
          }
        }
        
        // 连接错误
        this.ws.onerror = (error) => {
          console.error('❌ WebSocket 错误:', error)
          rejectOnce(error)
        }
        
      } catch (error) {
        console.error('❌ WebSocket 连接失败:', error)
        rejectOnce(error)
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
    
    // WebSocket 已断开
  }
  
  /**
   * 发送消息
   */
  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }
  
  /**
   * 监听特定类型的消息
   */
  on(messageType: string, callback: WebSocketEventCallback) {
    if (!this.eventListeners.has(messageType)) {
      this.eventListeners.set(messageType, new Set())
    }
    this.eventListeners.get(messageType)!.add(callback)
  }
  
  /**
   * 移除事件监听
   */
  off(messageType: string, callback: WebSocketEventCallback) {
    if (this.eventListeners.has(messageType)) {
      this.eventListeners.get(messageType)!.delete(callback)
    }
  }
  
  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage) {
    // 收到消息
    
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
    
    // 触发通用监听器（'*'）
    if (this.eventListeners.has('*')) {
      const callbacks = this.eventListeners.get('*')!
      callbacks.forEach(callback => {
        try {
          callback(message)
        } catch (error) {
          console.error('❌ 通用消息处理回调错误:', error)
        }
      })
    }
  }
  
  /**
   * 重连
   */
  private reconnect(sessionId: number, token: string) {
    this.reconnectAttempts++
    console.log(`🔄 尝试重连 WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
    
    // 使用指数退避策略，但最大延迟不超过30秒
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)
    
    setTimeout(() => {
      this.connect(sessionId, token).catch(error => {
        console.error(`❌ 重连失败 (${this.reconnectAttempts}/${this.maxReconnectAttempts}):`, error)
        
        // 如果重连次数未达到上限，继续重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnect(sessionId, token)
        } else {
          console.error('❌ WebSocket 重连次数已达上限，停止重连')
          // 触发重连失败事件，让调用方知道需要降级到轮询
          this.handleMessage({
            type: 'reconnect_failed',
            timestamp: new Date().toISOString(),
            data: { sessionId, attempts: this.reconnectAttempts }
          })
        }
      })
    }, delay)
  }
  
  /**
   * 开始心跳
   */
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({
        type: 'ping',
        timestamp: new Date().toISOString(),
        data: {},
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

// 单例
export const websocketService = new WebSocketService()

