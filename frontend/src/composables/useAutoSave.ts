/**
 * 自动保存 Composable
 * 监听数据变化并自动保存，带防抖和状态管理
 */

import { ref, watch, type Ref } from 'vue'
import { useDebounceFn } from '@vueuse/core'

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export interface UseAutoSaveOptions {
  data: Ref<any>
  saveFn: () => Promise<void>
  delay?: number
  enabled?: Ref<boolean>
}

export interface UseAutoSaveReturn {
  saveStatus: Ref<SaveStatus>
  lastSavedAt: Ref<Date | null>
  errorMessage: Ref<string | null>
  manualSave: () => Promise<void>
}

/**
 * 自动保存 Hook
 * @param options 配置选项
 * @returns 保存状态和方法
 */
export function useAutoSave(options: UseAutoSaveOptions): UseAutoSaveReturn {
  const { data, saveFn, delay = 3000, enabled = ref(true) } = options

  const saveStatus = ref<SaveStatus>('idle')
  const lastSavedAt = ref<Date | null>(null)
  const errorMessage = ref<string | null>(null)

  // 执行保存
  async function performSave() {
    if (!enabled.value) return

    saveStatus.value = 'saving'
    errorMessage.value = null

    try {
      await saveFn()
      saveStatus.value = 'saved'
      lastSavedAt.value = new Date()

      // 2秒后重置为 idle
      setTimeout(() => {
        if (saveStatus.value === 'saved') {
          saveStatus.value = 'idle'
        }
      }, 2000)
    } catch (error: any) {
      saveStatus.value = 'error'
      errorMessage.value = error.message || '保存失败'
      console.error('Auto save error:', error)
    }
  }

  // 防抖保存
  const debouncedSave = useDebounceFn(performSave, delay)

  // 监听数据变化
  watch(
    data,
    () => {
      if (enabled.value && data.value) {
        debouncedSave()
      }
    },
    { deep: true }
  )

  // 手动保存
  async function manualSave() {
    await performSave()
  }

  return {
    saveStatus,
    lastSavedAt,
    errorMessage,
    manualSave,
  }
}

