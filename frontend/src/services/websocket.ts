/**
 * WebSocket 服务
 */

import { getServerBaseUrl } from '../utils/url'
import { createLogger } from '../utils/logger'

const log = createLogger('WebSocket')

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
  /** 正在主动断开（含 CONNECTING 时断开），用于抑制 onerror 报错 */
  private isDisconnecting: boolean = false
  
  // 事件监听器
  private eventListeners: Map<string, Set<WebSocketEventCallback>> = new Map()
  
  /**
   * 连接 WebSocket
   */
  connect(sessionId: number, token: string, timeout: number = 20000): Promise<void> {
    return new Promise((resolve, reject) => {
      // 构建 WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // 使用统一的服务器基础URL获取函数
      const serverBaseUrl = getServerBaseUrl()
      const wsBase = serverBaseUrl.replace('http://', '').replace('https://', '')
      
      this.url = `${wsProtocol}//${wsBase}/api/v1/classroom-sessions/sessions/${sessionId}/ws?token=${token}`
      
      // 连接 WebSocket
      log.debug('连接', this.url.replace(/\?.*/, ''))
      
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
          log.debug('连接成功')
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
      
      // 超时：关闭连接并 reject；设 isDisconnecting 避免 onerror 再报一次
      timeoutId = setTimeout(() => {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
          log.warn(`连接超时 ${timeout}ms，请检查网络或后端`)
          this.isManualClose = true
          this.isDisconnecting = true
          this.ws.close()
          this.ws = null
          this.isDisconnecting = false
        }
        rejectOnce(new Error(`WebSocket连接超时（${timeout}ms），请检查网络或后端是否可访问`))
      }, timeout)
      
      try {
        this.ws = new WebSocket(this.url)
        this.isManualClose = false
        
        log.debug('创建 WebSocket，等待连接')
        
        // 连接成功
        this.ws.onopen = () => {
          log.debug('onopen')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolveOnce()
        }
        
        // 接收消息
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            if (message.type !== 'pong') {
              log.debug('消息', message.type)
            }
            if (message.type === 'connected') {
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
          
          log.debug('连接关闭', event.code, event.reason || '', this.isManualClose)
          
          // 🆕 code=1005 通常是客户端主动关闭（例如组件卸载）
          if (event.code === 1005) {
            log.debug('关闭 1005 客户端主动')
          }
          
          // 如果不是手动关闭，尝试重连
          if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
            // 检查关闭代码，某些代码不应该重连（如会话已结束）
            if (event.code === 1008) {
              // 1008: Policy Violation，通常是服务器主动关闭（如会话已结束）
              log.warn('服务器关闭', event.reason || '')
              this.handleMessage({
                type: 'connection_closed',
                timestamp: new Date().toISOString(),
                data: { code: event.code, reason: event.reason }
              })
            } else if (event.code === 1005 || event.code === 1006) {
              // 🆕 1005/1006: 异常断开，但不应该触发 connection_closed（避免误判为会话结束）
              log.debug('异常断开 1005/1006，尝试重连')
              this.reconnect(sessionId, token)
            } else {
              // 其他情况，尝试重连
              log.debug('关闭，尝试重连', event.code)
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
            log.debug('手动关闭，不重连')
          }
        }
        
        // 连接错误（若正在主动断开连接中，不报错、不 reject，避免「closed before established」刷屏）
        this.ws.onerror = (error) => {
          if (this.isDisconnecting) return
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
   * 若当前仍在 CONNECTING，关闭会导致浏览器报「closed before the connection is established」；
   * 已通过 isDisconnecting 在 onerror 中抑制重复报错。
   */
  disconnect() {
    log.debug('disconnect')
    this.isManualClose = true
    this.stopHeartbeat()
    
    if (this.ws) {
      const wasConnecting = this.ws.readyState === WebSocket.CONNECTING
      if (wasConnecting) this.isDisconnecting = true
      log.debug('关闭连接', wasConnecting ? '(连接尚未建立)' : '')
      this.ws.close()
      this.ws = null
      if (wasConnecting) this.isDisconnecting = false
    }
  }
  
  /**
   * 发送消息
   */
  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      log.warn('未连接，无法发送')
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
   * 移除所有事件监听（断开时调用，避免重连后重复注册）
   */
  removeAllListeners() {
    this.eventListeners.clear()
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
    log.debug('重连', this.reconnectAttempts, this.maxReconnectAttempts)
    
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

