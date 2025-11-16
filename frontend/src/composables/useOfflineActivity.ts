/**
 * 离线活动答题支持
 * 使用 IndexedDB 存储草稿和离线数据
 */

import { ref, watch } from 'vue'
import { openDB } from 'idb'
import activityService from '../services/activity'

// IndexedDB 数据库结构
interface SubmissionData {
  key: string
  cellId: number
  lessonId: number
  studentId: number
  submissionId?: number  // 服务器返回的提交ID
  responses: Record<string, any>
  status: string
  startedAt: string
  version: number
  lastModified: string
  synced: boolean
}

interface SyncQueueItem {
  action: 'create' | 'update' | 'submit'
  data: any
  timestamp: number
  retryCount: number
}

const DB_NAME = 'inspireed-activity'
const DB_VERSION = 1

let db: any = null

// 初始化数据库
async function initDB() {
  if (db) return db

  db = await openDB(DB_NAME, DB_VERSION, {
    upgrade(database) {
      // 创建提交表
      if (!database.objectStoreNames.contains('submissions')) {
        database.createObjectStore('submissions', { keyPath: 'key' })
      }
      // 创建同步队列表
      if (!database.objectStoreNames.contains('syncQueue')) {
        database.createObjectStore('syncQueue', { keyPath: 'timestamp' })
      }
    },
  })

  return db
}

/**
 * 离线活动 Composable
 */
// 支持 cellId 为数字或 UUID 字符串
export function useOfflineActivity(cellId: number | string, lessonId: number, studentId: number) {
  const isOnline = ref(navigator.onLine)
  const isSyncing = ref(false)
  const lastSyncTime = ref<Date | null>(null)
  const localResponses = ref<Record<string, any>>({})
  const hasUnsyncedChanges = ref(false)

  // 监听在线状态
  window.addEventListener('online', () => {
    isOnline.value = true
    syncWhenOnline()
  })

  window.addEventListener('offline', () => {
    isOnline.value = false
  })

  // 获取存储键
  function getStorageKey(): string {
    return `${cellId}-${studentId}`
  }

  // 清理数据，确保可序列化
  function sanitizeForStorage(data: any): any {
    if (data === null || data === undefined) {
      return data
    }
    
    if (typeof data === 'function') {
      return undefined  // 移除函数
    }
    
    if (data instanceof Date) {
      return data.toISOString()
    }
    
    if (Array.isArray(data)) {
      return data.map(item => sanitizeForStorage(item)).filter(item => item !== undefined)
    }
    
    if (typeof data === 'object') {
      const sanitized: any = {}
      for (const [key, value] of Object.entries(data)) {
        const cleaned = sanitizeForStorage(value)
        if (cleaned !== undefined) {
          sanitized[key] = cleaned
        }
      }
      return sanitized
    }
    
    return data
  }

  // 保存到 IndexedDB
  async function saveToIndexedDB(responses: Record<string, any>, status: string = 'draft', submissionId?: number) {
    try {
      const database = await initDB()
      const key = getStorageKey()
      
      // 获取现有数据以保留 submissionId
      const existing = await database.get('submissions', key).catch(() => null)

      // 清理 responses 数据，确保可序列化
      const sanitizedResponses = sanitizeForStorage(responses)

      const data = {
        key,
        cellId,
        lessonId,
        studentId,
        submissionId: submissionId || existing?.submissionId,
        responses: sanitizedResponses,
        status,
        startedAt: existing?.startedAt || new Date().toISOString(),
        version: Date.now(),
        lastModified: new Date().toISOString(),
        synced: false,
      }

      await database.put('submissions', data)
      hasUnsyncedChanges.value = true

      console.log('💾 Saved to IndexedDB:', key)
    } catch (error) {
      console.error('❌ Failed to save to IndexedDB:', error)
      throw error
    }
  }

  // 从 IndexedDB 加载
  async function loadFromIndexedDB(): Promise<Record<string, any> | null> {
    try {
      const database = await initDB()
      const key = getStorageKey()
      const data = await database.get('submissions', key)

      if (data) {
        console.log('📂 Loaded from IndexedDB:', key)
        localResponses.value = data.responses
        hasUnsyncedChanges.value = !data.synced
        return data.responses
      }

      return null
    } catch (error) {
      console.error('❌ Failed to load from IndexedDB:', error)
      return null
    }
  }

  // 清除缓存
  async function clearCache() {
    try {
      const database = await initDB()
      const key = getStorageKey()
      await database.delete('submissions', key)
      localResponses.value = {}
      hasUnsyncedChanges.value = false
      console.log('🗑️ Cleared cache:', key)
    } catch (error) {
      console.error('❌ Failed to clear cache:', error)
    }
  }

  // 同步到服务器
  async function syncToServer(responses: Record<string, any>, status: string = 'draft') {
    if (!isOnline.value) {
      console.log('📡 Offline, saving locally...')
      await saveToIndexedDB(responses, status)
      return null
    }

    try {
      isSyncing.value = true

      // 尝试同步到服务器
      const database = await initDB()
      const key = getStorageKey()
      const localData = await database.get('submissions', key).catch(() => null)

      let submission

      // 清理 responses 数据，确保是对象格式
      let sanitizedResponses: Record<string, any> = sanitizeForStorage(responses) || {}
      
      // 确保 responses 是对象而不是数组或其他类型
      if (!sanitizedResponses || typeof sanitizedResponses !== 'object' || Array.isArray(sanitizedResponses)) {
        console.warn('⚠️ Invalid responses format, using empty object')
        sanitizedResponses = {}
      }

      if (localData?.submissionId) {
        // 更新现有提交
        console.log('🔄 Updating existing submission:', localData.submissionId)
        submission = await activityService.updateSubmission(localData.submissionId, {
          responses: sanitizedResponses,
          status: status as any,
        })
      } else {
        // 创建新提交
        // 如果 cellId 是 0（表示 UUID），需要从调用方传递实际的 UUID
        // 这里我们假设 cellId 可能是数字或已经是正确的值
        console.log('🆕 Creating new submission:', { cellId, lessonId, responsesCount: Object.keys(sanitizedResponses).length })
        const startedAt = localData?.startedAt || new Date().toISOString()
        submission = await activityService.createSubmission({
          cellId,  // 后端现在支持数字或 UUID 字符串
          lessonId,
          responses: sanitizedResponses,
          startedAt,
        })
      }

      // 标记为已同步，保存 submissionId
      if (localData) {
        await database.put('submissions', {
          ...localData,
          submissionId: submission.id,
          responses: sanitizedResponses,
          status,
          synced: true,
          lastModified: new Date().toISOString(),
        })
      } else {
        // 如果没有本地数据，创建新的
        await saveToIndexedDB(sanitizedResponses, status, submission.id)
        const saved = await database.get('submissions', key)
        await database.put('submissions', {
          ...saved,
          synced: true,
        })
      }

      hasUnsyncedChanges.value = false
      lastSyncTime.value = new Date()

      console.log('✅ Synced to server')
      return submission
    } catch (error: any) {
      console.error('❌ Sync failed, saving locally:', error)
      // 记录详细的错误信息
      if (error.response) {
        console.error('Response status:', error.response.status)
        console.error('Response data:', error.response.data)
        console.error('Request data:', {
          cellId,
          lessonId,
          hasSubmissionId: !!localData?.submissionId,
          responsesKeys: Object.keys(responses || {}),
        })
      }
      await saveToIndexedDB(responses, status)
      throw error
    } finally {
      isSyncing.value = false
    }
  }

  // 当在线时自动同步
  async function syncWhenOnline() {
    if (!isOnline.value || !hasUnsyncedChanges.value) return

    console.log('🔄 Auto-syncing...')

    try {
      const database = await initDB()
      const key = getStorageKey()
      const localData = await database.get('submissions', key).catch(() => null)

      if (localData && !localData.synced) {
        await syncToServer(localData.responses, localData.status)
      }
    } catch (error) {
      console.error('❌ Auto-sync failed:', error)
    }
  }

  // 获取未同步的变更数量
  async function getUnsyncedCount(): Promise<number> {
    try {
      const database = await initDB()
      const allSubmissions = await database.getAll('submissions')
      return allSubmissions.filter((s) => !s.synced).length
    } catch (error) {
      console.error('❌ Failed to get unsynced count:', error)
      return 0
    }
  }

  // 自动保存功能
  function setupAutoSave(
    responses: Record<string, any>,
    interval: number = 30000 // 30秒
  ) {
    const autoSaveInterval = setInterval(async () => {
      if (Object.keys(responses).length > 0) {
        console.log('💾 Auto-saving...')
        await saveToIndexedDB(responses)
      }
    }, interval)

    // 返回清理函数
    return () => {
      clearInterval(autoSaveInterval)
    }
  }

  return {
    // 状态
    isOnline,
    isSyncing,
    lastSyncTime,
    hasUnsyncedChanges,
    localResponses,

    // 方法
    saveToIndexedDB,
    loadFromIndexedDB,
    clearCache,
    syncToServer,
    syncWhenOnline,
    getUnsyncedCount,
    setupAutoSave,
  }
}

