/**
 * 教案编辑器 - 导航与视图：全屏预览、预览/编辑模式切换、导出
 */

import { ref, type Ref } from 'vue'
import { useLessonStore } from '../store/lesson'
import courseExportService from '../services/courseExport'

export function useLessonEditorNav(
  isPreviewMode: Ref<boolean>,
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void
) {
  const lessonStore = useLessonStore()
  const isFullscreenPreview = ref(false)
  const exporting = ref(false)

  function toggleFullscreenPreview() {
    isFullscreenPreview.value = !isFullscreenPreview.value
    if (isFullscreenPreview.value) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = ''
  }

  function handleTogglePreviewMode() {
    if (isPreviewMode.value) {
      isPreviewMode.value = false
      return
    }
    const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
    if (cur?.status !== 'published') {
      showToast('warning', '需要先发布教案才能进入授课模式')
      return
    }
    isPreviewMode.value = true
  }

  async function handleExportLesson() {
    const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
    if (!cur) {
      showToast('error', '教案不存在')
      return
    }
    exporting.value = true
    try {
      const blob = await courseExportService.exportLesson(cur.id)
      courseExportService.downloadFile(blob, `${cur.title}_导出.zip`)
      showToast('success', '教案导出成功')
    } catch (e: any) {
      console.error('导出教案失败:', e)
      showToast('error', e.response?.data?.detail || e.message || '导出教案失败')
    } finally {
      exporting.value = false
    }
  }

  return {
    isFullscreenPreview,
    toggleFullscreenPreview,
    handleTogglePreviewMode,
    handleExportLesson,
    exporting,
  }
}
