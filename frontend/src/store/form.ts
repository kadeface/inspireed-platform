/**
 * Form Store - 互动表单状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createLogger } from '../utils/logger'
import { formService } from '../services/form'
import { useAuthStore } from './auth'
import type {
  FormCell,
  FormCellCreate,
  FormCellUpdate,
  FormResponse,
  FormResponseCreate,
  FormResults,
  FormWSMessage,
  Answer,
} from '../types/form'

const logger = createLogger('FormStore')

export const useFormStore = defineStore('form', () => {
  // 状态
  const currentForm = ref<FormCell | null>(null)
  const responses = ref<FormResponse[]>([])
  const results = ref<FormResults | null>(null)
  const isConnected = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isFormActive = ref(false)

  // WebSocket连接
  let ws: WebSocket | null = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5
  const reconnectDelay = 3000 // 3秒

  // 计算属性
  const totalResponses = computed(() => results.value?.total_responses || 0)
  const responseRate = computed(() => results.value?.response_rate || 0)

  /**
   * 获取表单详情
   */
  async function fetchForm(formCellId: number) {
    logger.debug('获取表单', formCellId)
    isLoading.value = true
    error.value = null

    try {
      currentForm.value = await formService.getForm(formCellId)
    } catch (err: any) {
      error.value = err.message || '获取表单失败'
      logger.error('获取表单失败', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建表单
   */
  async function createForm(data: FormCellCreate) {
    logger.debug('创建表单', data)
    isLoading.value = true
    error.value = null

    try {
      const form = await formService.createForm(data)
      currentForm.value = form
      return form
    } catch (err: any) {
      error.value = err.message || '创建表单失败'
      logger.error('创建表单失败', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新表单
   */
  async function updateForm(formCellId: number, data: FormCellUpdate) {
    logger.debug('更新表单', formCellId, data)
    isLoading.value = true
    error.value = null

    try {
      const form = await formService.updateForm(formCellId, data)
      currentForm.value = form
    } catch (err: any) {
      error.value = err.message || '更新表单失败'
      logger.error('更新表单失败', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除表单
   */
  async function deleteForm(formCellId: number) {
    logger.debug('删除表单', formCellId)
    isLoading.value = true
    error.value = null

    try {
      await formService.deleteForm(formCellId)
      currentForm.value = null
      results.value = null
      responses.value = []
    } catch (err: any) {
      error.value = err.message || '删除表单失败'
      logger.error('删除表单失败', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 提交答案
   */
  async function submitResponse(formCellId: number, answers: Answer[]) {
    logger.debug('提交答案', formCellId, answers)
    error.value = null

    try {
      const data: FormResponseCreate = { answers }
      const response = await formService.submitResponse(formCellId, data)
      responses.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '提交答案失败'
      logger.error('提交答案失败', err)
      throw err
    }
  }

  /**
   * 获取结果统计
   */
  async function fetchResults(formCellId: number) {
    logger.debug('获取结果', formCellId)
    error.value = null

    try {
      results.value = await formService.getResults(formCellId)
    } catch (err: any) {
      error.value = err.message || '获取结果失败'
      logger.error('获取结果失败', err)
      throw err
    }
  }

  /**
   * 连接WebSocket
   */
  function connectWebSocket(formCellId: number) {
    const authStore = useAuthStore()
    const token = authStore.token

    if (!token) {
      error.value = '未登录，无法连接WebSocket'
      logger.error('未登录')
      return
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
      logger.debug('WebSocket已连接')
      return
    }

    try {
      // 构建WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/forms/${formCellId}/ws?token=${token}`

      logger.debug('连接WebSocket', wsUrl)
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        logger.debug('WebSocket连接成功')
        isConnected.value = true
        reconnectAttempts = 0
      }

      ws.onmessage = (event) => {
        try {
          const message: FormWSMessage = JSON.parse(event.data)
          logger.debug('收到WebSocket消息', message.type)
          handleMessage(message)
        } catch (err) {
          logger.error('解析WebSocket消息失败', err)
        }
      }

      ws.onclose = (event) => {
        logger.debug('WebSocket连接关闭', event.code, event.reason)
        isConnected.value = false
        ws = null

        // 尝试重连
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++
          logger.debug(`尝试重连 (${reconnectAttempts}/${maxReconnectAttempts})`)
          setTimeout(() => {
            connectWebSocket(formCellId)
          }, reconnectDelay * reconnectAttempts)
        }
      }

      ws.onerror = (error) => {
        logger.error('WebSocket错误', error)
        error.value = 'WebSocket连接错误'
      }
    } catch (err) {
      logger.error('创建WebSocket失败', err)
      error.value = '创建WebSocket失败'
    }
  }

  /**
   * 断开WebSocket
   */
  function disconnectWebSocket() {
    logger.debug('断开WebSocket')
    reconnectAttempts = maxReconnectAttempts // 防止重连

    if (ws) {
      ws.close()
      ws = null
    }

    isConnected.value = false
  }

  /**
   * 处理WebSocket消息
   */
  function handleMessage(message: FormWSMessage) {
    switch (message.type) {
      case 'connection_established':
        logger.debug('连接已建立', message.is_active)
        isFormActive.value = message.is_active || false
        break

      case 'form_started':
        logger.debug('表单已开始')
        isFormActive.value = true
        break

      case 'form_stopped':
        logger.debug('表单已停止')
        isFormActive.value = false
        break

      case 'submit_success':
        logger.debug('提交成功')
        break

      case 'new_response':
        logger.debug('收到新答案', message.user_id)
        // 自动获取最新结果
        if (currentForm.value) {
          fetchResults(currentForm.value.id)
        }
        break

      case 'results_update':
        logger.debug('结果更新', message.total_responses)
        if (results.value && message.total_responses !== undefined) {
          results.value.total_responses = message.total_responses
        }
        break

      case 'error':
        logger.error('WebSocket错误', message.detail)
        error.value = message.detail || '发生错误'
        break

      default:
        logger.debug('未知消息类型', message)
    }
  }

  /**
   * 发送WebSocket消息
   */
  function sendWebSocketMessage(message: any) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    } else {
      logger.warn('WebSocket未连接，无法发送消息')
    }
  }

  /**
   * 开始投票（教师）
   */
  function startForm() {
    if (!currentForm.value) return

    sendWebSocketMessage({
      type: 'form_start',
    })

    isFormActive.value = true
  }

  /**
   * 停止投票（教师）
   */
  function stopForm() {
    if (!currentForm.value) return

    sendWebSocketMessage({
      type: 'form_stop',
    })

    isFormActive.value = false
  }

  /**
   * 重置状态
   */
  function reset() {
    currentForm.value = null
    responses.value = []
    results.value = null
    isConnected.value = false
    isFormActive.value = false
    error.value = null
    isLoading.value = false

    disconnectWebSocket()
  }

  return {
    // 状态
    currentForm,
    responses,
    results,
    isConnected,
    isLoading,
    error,
    isFormActive,

    // 计算属性
    totalResponses,
    responseRate,

    // 方法
    fetchForm,
    createForm,
    updateForm,
    deleteForm,
    submitResponse,
    fetchResults,
    connectWebSocket,
    disconnectWebSocket,
    startForm,
    stopForm,
    reset,
  }
})
