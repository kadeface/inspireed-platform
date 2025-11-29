/**
 * 活动提交管理 Composable
 * 统一处理保存和提交逻辑
 */

import { ref, computed } from 'vue'
import activityService from '../services/activity'
import { useOfflineActivity } from './useOfflineActivity'

interface UseActivitySubmissionOptions {
  cellId: number | string
  lessonId: number
  studentId: number
  answers: Record<string, any>
  startTime: Date
  submissionId: number | null
  onSubmissionUpdate?: (submission: any) => void
}

export function useActivitySubmission(options: UseActivitySubmissionOptions) {
  const {
    cellId,
    lessonId,
    studentId,
    answers,
    startTime,
    submissionId,
    onSubmissionUpdate,
  } = options
  
  const submitting = ref(false)
  
  // 初始化离线支持
  const actualCellId = cellId
  // 对于 UUID，使用哈希值作为存储 key；对于数字 ID，直接使用
  const cellIdForStorage: number = typeof actualCellId === 'string'
    ? parseInt(actualCellId.split('-')[0], 16) % 1000000
    : actualCellId
  
  const offlineActivity = cellIdForStorage > 0
    ? useOfflineActivity(cellIdForStorage, lessonId, studentId)
    : null
  
  /**
   * 保存单个答案（草稿）
   */
  async function saveAnswer(itemId: string) {
    console.log('💾 Auto-saving answer:', itemId, answers[itemId])
    
    try {
      // 使用离线支持自动保存
      await syncToServer(answers, 'draft')
    } catch (error) {
      // 保存失败会自动存到 IndexedDB
      console.log('📱 Saved offline')
    }
  }
  
  /**
   * 保存草稿
   */
  async function saveDraft(): Promise<void> {
    try {
      submitting.value = true
      await syncToServer(answers, 'draft')
      console.log('✅ Draft saved')
    } catch (error) {
      console.error('❌ Save draft failed:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }
  
  /**
   * 提交答案
   */
  async function submitActivity(): Promise<any> {
    const timeSpent = Math.floor((new Date().getTime() - startTime.getTime()) / 1000)
    
    try {
      submitting.value = true
      
      let submittedSubmission: any
      
      if (submissionId) {
        // 如果已有提交ID，调用正式提交API
        submittedSubmission = await activityService.submitActivity(submissionId, {
          responses: answers,
          timeSpent,
        })
      } else {
        // 先创建提交再提交
        const submission = await activityService.createSubmission({
          cellId: actualCellId as any, // 后端支持 number 或 string (UUID)
          lessonId,
          responses: answers,
          startedAt: startTime.toISOString(),
        })
        
        // 正式提交
        submittedSubmission = await activityService.submitActivity(submission.id, {
          responses: answers,
          timeSpent,
        })
      }
      
      if (onSubmissionUpdate) {
        onSubmissionUpdate(submittedSubmission)
      }
      
      return submittedSubmission
    } catch (error) {
      console.error('❌ Submit failed:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }
  
  /**
   * 同步到服务器（支持离线）
   */
  async function syncToServer(responses: Record<string, any>, status: string = 'draft'): Promise<any> {
    // 验证 cellId 是否有效
    if (!actualCellId || (typeof actualCellId === 'number' && actualCellId === 0)) {
      console.error('❌ Cannot sync: invalid cellId')
      return null
    }
    
    // 如果是 UUID 字符串，直接调用 API
    if (typeof actualCellId === 'string') {
      try {
        const submission = await activityService.createSubmission({
          cellId: actualCellId as any, // 后端支持 number 或 string (UUID)
          lessonId,
          responses,
          startedAt: startTime.toISOString(),
        })
        return submission
      } catch (error) {
        console.error('❌ UUID sync failed:', error)
        return null
      }
    }
    
    // 如果是数字 ID，使用离线支持
    if (!offlineActivity) {
      console.warn('⚠️ Offline activity not initialized yet, using direct API call')
      try {
        const submission = await activityService.createSubmission({
          cellId: actualCellId,
          lessonId,
          responses,
          startedAt: startTime.toISOString(),
        })
        return submission
      } catch (error) {
        console.error('❌ Direct API call failed:', error)
        return null
      }
    }
    
    return await offlineActivity.syncToServer(responses, status)
  }
  
  /**
   * 从 IndexedDB 加载
   */
  async function loadFromIndexedDB(): Promise<Record<string, any> | null> {
    if (!offlineActivity) return null
    return await offlineActivity.loadFromIndexedDB()
  }
  
  /**
   * 设置自动保存
   */
  function setupAutoSave(responses: Record<string, any>, interval: number = 30000) {
    if (!offlineActivity) {
      return () => {}
    }
    return offlineActivity.setupAutoSave(responses, interval)
  }
  
  /**
   * 获取在线状态
   */
  const isOnline = computed(() => offlineActivity?.isOnline.value ?? ref(navigator.onLine).value)
  const isSyncing = computed(() => offlineActivity?.isSyncing.value ?? ref(false).value)
  const hasUnsyncedChanges = computed(() => offlineActivity?.hasUnsyncedChanges.value ?? ref(false).value)
  
  return {
    // 状态
    submitting,
    isOnline,
    isSyncing,
    hasUnsyncedChanges,
    
    // 方法
    saveAnswer,
    saveDraft,
    submitActivity,
    syncToServer,
    loadFromIndexedDB,
    setupAutoSave,
  }
}

