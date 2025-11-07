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
export function useOfflineActivity(cellId: number, lessonId: number, studentId: number) {
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

  // 保存到 IndexedDB
  async function saveToIndexedDB(responses: Record<string, any>, status: string = 'draft') {
    try {
      const database = await initDB()
      const key = getStorageKey()

      const data = {
        key,
        cellId,
        lessonId,
        studentId,
        responses,
        status,
        startedAt: new Date().toISOString(),
        version: Date.now(),
        lastModified: new Date().toISOString(),
        synced: false,
      }

      await database.put('submissions', data)
      hasUnsyncedChanges.value = true

      console.log('💾 Saved to IndexedDB:', key)
    } catch (error) {
      console.error('❌ Failed to save to IndexedDB:', error)
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
      const localData = await database.get('submissions', key)

      let submission

      if (localData && localData.version) {
        // 更新现有提交
        submission = await activityService.updateSubmission(cellId, {
          responses,
          status: status as any,
        })
      } else {
        // 创建新提交
        submission = await activityService.createSubmission({
          cellId,
          lessonId,
          responses,
          startedAt: new Date().toISOString(),
        })
      }

      // 标记为已同步
      if (localData) {
        await database.put('submissions', {
          ...localData,
          responses,
          status,
          synced: true,
          lastModified: new Date().toISOString(),
        })
      }

      hasUnsyncedChanges.value = false
      lastSyncTime.value = new Date()

      console.log('✅ Synced to server')
      return submission
    } catch (error) {
      console.error('❌ Sync failed, saving locally:', error)
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
      const localData = await database.get('submissions', key)

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

