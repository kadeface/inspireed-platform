/**
 * 教案编辑器 - 保存、返回前保存、卸载前保存、未保存标记、时间格式化
 */

import { ref, watch, nextTick, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import { renumberCellsGloballyInSections, sectionsToContent } from '../utils/lessonContent'
import type { SectionInContent } from '../types/section'
import { useLessonStore } from '../store/lesson'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export function useLessonEditorSave(
  sections: Ref<SectionInContent[]>,
  lessonTitle: Ref<string>,
  isPreviewMode: Ref<boolean>,
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void
) {
  const router = useRouter()
  const lessonStore = useLessonStore()

  const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const lastSavedAt = ref<Date | null>(null)
  const hasUnsavedChanges = ref(false)
  const isSavingOnUnmount = ref(false)

  function _currentLesson() {
    const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
    return cur
  }

  async function manualSave() {
    const cur = _currentLesson()
    if (!cur || isPreviewMode.value) return
    saveStatus.value = 'saving'
    try {
      (cur as any).title = lessonTitle.value
      renumberCellsGloballyInSections(sections.value)
      ;(cur as any).content = sectionsToContent(sections.value)
      await lessonStore.saveCurrentLesson()
      saveStatus.value = 'saved'
      lastSavedAt.value = new Date()
      setTimeout(() => {
        if (saveStatus.value === 'saved') saveStatus.value = 'idle'
      }, 2000)
    } catch (e: any) {
      saveStatus.value = 'error'
      console.error('保存失败:', e)
      throw e
    }
  }

  watch(
    [sections, lessonTitle],
    () => {
      if (_currentLesson() && !isPreviewMode.value && saveStatus.value !== 'saving') {
        hasUnsavedChanges.value = true
      }
    },
    { deep: true }
  )

  watch(saveStatus, (s) => {
    if (s === 'saved') hasUnsavedChanges.value = false
  })

  function formatSaveTime(date: Date) {
    const now = dayjs()
    const saveTime = dayjs(date)
    const d = now.diff(saveTime, 'minute')
    if (d < 1) return '刚刚保存'
    if (d < 60) return `${d}分钟前保存`
    return saveTime.format('HH:mm 保存')
  }

  async function handleManualSave() {
    if (isPreviewMode.value) {
      const ok = confirm(
        '当前处于授课模式（预览模式），无法保存教案。\n\n是否切换到编辑模式以保存更改？\n\n提示：切换到编辑模式后，您可以继续编辑和保存教案。'
      )
      if (!ok) return
      isPreviewMode.value = false
      await nextTick()
      try {
        const cur = _currentLesson()
        if (cur) (cur as any).title = lessonTitle.value
        await manualSave()
        showToast('success', '已切换到编辑模式并保存成功')
      } catch (e: any) {
        showToast('error', e.message || '保存失败')
      }
      return
    }
    try {
      const cur = _currentLesson()
      if (cur) (cur as any).title = lessonTitle.value
      await manualSave()
      showToast('success', '保存成功')
    } catch (e: any) {
      showToast('error', e.message || '保存失败')
    }
  }

  async function handleBack() {
    const cur = _currentLesson()
    if (!cur || isPreviewMode.value) {
      router.push('/teacher')
      return
    }
    if (!hasUnsavedChanges.value) {
      router.push('/teacher')
      return
    }
    isSavingOnUnmount.value = true
    try {
      (cur as any).title = lessonTitle.value
      renumberCellsGloballyInSections(sections.value)
      ;(cur as any).content = sectionsToContent(sections.value)
      await lessonStore.saveCurrentLesson()
      hasUnsavedChanges.value = false
      await new Promise((r) => setTimeout(r, 200))
    } catch (e) {
      console.error('返回前保存失败:', e)
    } finally {
      isSavingOnUnmount.value = false
    }
    router.push('/teacher')
  }

  async function saveOnUnmount() {
    if (isSavingOnUnmount.value) return
    const cur = _currentLesson()
    if (!cur || isPreviewMode.value) return
    if (!hasUnsavedChanges.value) return
    isSavingOnUnmount.value = true
    try {
      (cur as any).title = lessonTitle.value
      renumberCellsGloballyInSections(sections.value)
      ;(cur as any).content = sectionsToContent(sections.value)
      await lessonStore.saveCurrentLesson()
      hasUnsavedChanges.value = false
    } catch (e) {
      console.error('卸载前保存失败:', e)
    } finally {
      isSavingOnUnmount.value = false
    }
  }

  return {
    saveStatus,
    lastSavedAt,
    hasUnsavedChanges,
    isSavingOnUnmount,
    manualSave,
    handleManualSave,
    handleBack,
    formatSaveTime,
    saveOnUnmount,
  }
}
