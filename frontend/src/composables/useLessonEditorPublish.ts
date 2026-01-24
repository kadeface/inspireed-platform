/**
 * 教案编辑器 - 发布：弹窗、选择班级、confirm/cancel
 */

import { ref, computed } from 'vue'
import { useLessonStore } from '../store/lesson'

export function useLessonEditorPublish(
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void
) {
  const lessonStore = useLessonStore()

  const showPublishModal = ref(false)
  const selectedClassroomIds = ref<number[]>([])
  const publishError = ref<string | null>(null)

  const publishModalError = computed(
    () => publishError.value || lessonStore.classroomsError || null
  )

  async function handlePublish() {
    publishError.value = null
    try {
      await lessonStore.loadAvailableClassrooms()
      const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
      const existing = (cur as any)?.classroom_ids ?? []
      selectedClassroomIds.value = [...existing]
      const list = lessonStore.availableClassrooms ?? []
      if (selectedClassroomIds.value.length === 0 && list.length === 1) {
        selectedClassroomIds.value = [list[0].id]
      }
      showPublishModal.value = true
    } catch (e: any) {
      showToast('error', e.message || '获取班级列表失败')
    }
  }

  async function handlePublishConfirm(classroomIds: number[]) {
    if (classroomIds.length === 0) {
      publishError.value = '请选择至少一个班级'
      return
    }
    publishError.value = null
    try {
      await lessonStore.publishCurrentLesson(classroomIds)
      selectedClassroomIds.value = [...classroomIds]
      showPublishModal.value = false
      showToast('success', '教案已发布')
    } catch (e: any) {
      publishError.value = e.message || '发布失败'
    }
  }

  function handlePublishCancel() {
    publishError.value = null
  }

  return {
    showPublishModal,
    selectedClassroomIds,
    publishError,
    publishModalError,
    handlePublish,
    handlePublishConfirm,
    handlePublishCancel,
  }
}
