/**
 * 教案编辑器 - 发布：直接发布，不选择班级（班级在上课时选择）
 */

import { useLessonStore } from '../store/lesson'

export function useLessonEditorPublish(
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void
) {
  const lessonStore = useLessonStore()

  async function handlePublish() {
    try {
      await lessonStore.publishCurrentLesson([])
      showToast('success', '教案已发布')
    } catch (e: any) {
      showToast('error', e.message || '发布失败')
    }
  }

  return {
    handlePublish,
  }
}
