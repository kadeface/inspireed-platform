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
  connect(sessionId: number, token: string, timeout: number = 10000): Promise<void> {
    return new Promise((resolve, reject) => {
      // 构建 WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // 使用统一的服务器基础URL获取函数
      const serverBaseUrl = getServerBaseUrl()
      const wsBase = serverBaseUrl.replace('http://', '').replace('https://', '')
      
      this.url = `${wsProtocol}//${wsBase}/api/v1/classroom-sessions/sessions/${sessionId}/ws?token=${token}`
      
      // 连接 WebSocket
      console.log(`🔌 尝试连接 WebSocket: ${this.url}`)
      
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
          console.log('✅ WebSocket 连接成功（Promise resolved）')
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
      
      // 设置超时（增加到10秒）
      timeoutId = setTimeout(() => {
        if (this.ws) {
          console.warn(`⏰ WebSocket 连接超时（${timeout}ms），readyState=${this.ws.readyState}`)
          this.ws.close()
          this.ws = null
        }
        rejectOnce(new Error(`WebSocket连接超时（${timeout}ms）`))
      }, timeout)
      
      try {
        this.ws = new WebSocket(this.url)
        this.isManualClose = false
        
        console.log('🔌 WebSocket 对象已创建，等待连接...')
        
        // 连接成功
        this.ws.onopen = () => {
          console.log('🎉 WebSocket onopen 事件触发')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolveOnce()
        }
        
        // 接收消息
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            console.log(`📨 收到 WebSocket 消息: type=${message.type}`)
            
            // 🆕 如果收到 connected 消息，也认为连接成功
            if (message.type === 'connected') {
              console.log('📥 收到 connected 消息，确认连接成功')
              resolveOnce()
            }
            
            this.handleMessage(message)
          } catch (error) {
            console.error('❌ 解析消息失败:', error)
          }
        }
        
        // 连接关闭
        this.ws.onclose = (event) => {
          this.stopHeartbeat()
          
          console.log(`🔌 WebSocket 连接关闭: code=${event.code}, reason=${event.reason || '无原因'}, isManualClose=${this.isManualClose}`)
          
          // 🆕 code=1005 通常是客户端主动关闭（例如组件卸载）
          if (event.code === 1005) {
            console.log('ℹ️ WebSocket 关闭代码 1005（无状态接收），通常是客户端主动关闭或页面刷新')
          }
          
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
            } else if (event.code === 1005 || event.code === 1006) {
              // 🆕 1005/1006: 异常断开，但不应该触发 connection_closed（避免误判为会话结束）
              console.log('⚠️ WebSocket 异常断开（code=1005/1006），尝试重连而不触发 connection_closed')
              this.reconnect(sessionId, token)
            } else {
              // 其他情况，尝试重连
              console.log(`⚠️ WebSocket 关闭（code=${event.code}），尝试重连...`)
              this.reconnect(sessionId, token)
            }
          } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ WebSocket 重连次数已达上限')
            this.handleMessage({
              type: 'reconnect_failed',
              timestamp: new Date().toISOString(),
              data: { sessionId, attempts: this.reconnectAttempts }
            })
          } else if (this.isManualClose) {
            console.log('✅ WebSocket 手动关闭，不会重连')
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
    console.log('🔌 [主动断开] disconnect() 被调用, isManualClose 将设为 true')
    this.isManualClose = true
    this.stopHeartbeat()
    
    if (this.ws) {
      console.log('🔌 [主动断开] 正在关闭 WebSocket 连接...')
      this.ws.close()
      this.ws = null
      console.log('✅ [主动断开] WebSocket 已关闭')
    } else {
      console.log('ℹ️ [主动断开] WebSocket 已经是关闭状态，无需操作')
    }
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

