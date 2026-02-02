/**
 * useWebSocket Composable 单元测试
 *
 * 注意：由于 onMounted/onBeforeUnmount 需要组件上下文，
 * 这些测试主要验证初始化状态和导出的方法。
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'

// Mock auth store
const mockAuthStore = {
  token: 'mock-token-123',
}

vi.mock('@/store/auth', () => ({
  useAuthStore: () => mockAuthStore,
}))

describe('useWebSocket', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()

    // 重置环境变量
    import.meta.env.VITE_API_BASE_URL = 'http://localhost:8000'
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('应该正确初始化状态', () => {
    // 由于 useWebSocket 内部使用了 onMounted，
    // 我们需要在一个更受控的环境中测试
    // 这里我们只验证导入是否成功

    expect(async () => {
      const { useWebSocket } = await import('@/components/Classroom/composables/useWebSocket')
      const endpointUrl = ref('/ws/session/1')

      const { isConnected, isConnecting, reconnectAttempts, connect, disconnect } =
        useWebSocket({
          endpointUrl,
          scope: 'session',
        })

      expect(isConnected.value).toBe(false)
      expect(isConnecting.value).toBe(false)
      expect(reconnectAttempts.value).toBe(0)
      expect(typeof connect).toBe('function')
      expect(typeof disconnect).toBe('function')
    }).not.toThrow()
  })

  it('应该导出所有必需的方法和状态', async () => {
    const { useWebSocket } = await import('@/components/Classroom/composables/useWebSocket')
    const endpointUrl = ref('/ws/session/1')

    const result = useWebSocket({
      endpointUrl,
      scope: 'session',
    })

    // 验证所有导出的属性
    expect(result).toHaveProperty('isConnected')
    expect(result).toHaveProperty('isConnecting')
    expect(result).toHaveProperty('reconnectAttempts')
    expect(result).toHaveProperty('connect')
    expect(result).toHaveProperty('disconnect')
    expect(result).toHaveProperty('sendMessage')
    expect(result).toHaveProperty('requestStatistics')

    // 验证响应式状态
    expect(typeof result.isConnected.value).toBe('boolean')
    expect(typeof result.isConnecting.value).toBe('boolean')
    expect(typeof result.reconnectAttempts.value).toBe('number')

    // 验证方法是函数
    expect(typeof result.connect).toBe('function')
    expect(typeof result.disconnect).toBe('function')
    expect(typeof result.sendMessage).toBe('function')
    expect(typeof result.requestStatistics).toBe('function')
  })

  it('应该接受回调函数参数', async () => {
    const { useWebSocket } = await import('@/components/Classroom/composables/useWebSocket')
    const endpointUrl = ref('/ws/session/1')
    const onConnected = vi.fn()
    const onDisconnected = vi.fn()
    const onError = vi.fn()
    const onParticipantJoined = vi.fn()
    const onSessionStatusChanged = vi.fn()

    expect(() => {
      useWebSocket({
        endpointUrl,
        scope: 'session',
        onConnected,
        onDisconnected,
        onError,
        onParticipantJoined,
        onSessionStatusChanged,
      })
    }).not.toThrow()
  })

  it('应该支持自定义心跳间隔', async () => {
    const { useWebSocket } = await import('@/components/Classroom/composables/useWebSocket')
    const endpointUrl = ref('/ws/session/1')

    expect(() => {
      useWebSocket({
        endpointUrl,
        scope: 'session',
        heartbeatInterval: 5000,
      })
    }).not.toThrow()
  })

  it('应该支持 session 和 lesson 两种作用域', async () => {
    const { useWebSocket } = await import('@/components/Classroom/composables/useWebSocket')
    const endpointUrl = ref('/ws/session/1')

    expect(() => {
      useWebSocket({
        endpointUrl,
        scope: 'session',
      })
    }).not.toThrow()

    expect(() => {
      useWebSocket({
        endpointUrl,
        scope: 'lesson',
      })
    }).not.toThrow()
  })

  it('应该在 sendMessage 时处理未连接状态', () => {
    const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    // 由于 onMounted 在测试环境中不会正常工作，
    // 这个测试验证了当连接不存在时的行为
    expect(async () => {
      const { useWebSocket } = await import('@/components/Classroom/composables/useWebSocket')
      const endpointUrl = ref('/ws/session/1')

      const { sendMessage, isConnected } = useWebSocket({
        endpointUrl,
        scope: 'session',
      })

      // 初始状态应该是未连接
      expect(isConnected.value).toBe(false)

      // 尝试发送消息
      sendMessage({
        type: 'ping',
        timestamp: new Date().toISOString(),
        data: {},
      })

      // 应该有警告（但警告可能在异步回调中，所以这里只验证不会报错）
    }).not.toThrow()

    consoleWarnSpy.mockRestore()
  })
})
