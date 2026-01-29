<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部工具栏 -->
    <LessonEditorToolbar
      :lesson-title="lessonTitle"
      @update:lessonTitle="lessonTitle = $event"
      :save-status="saveStatus"
      :last-saved-at="lastSavedAt"
      :is-preview-mode="isPreviewMode"
      :compact-mode="compactMode"
      :can-enter-preview-mode="canEnterPreviewMode"
      :current-lesson="currentLesson"
      :is-saving="isSaving"
      :is-recently-unpublished="isRecentlyUnpublished"
      :exporting="exporting"
      :classroom-panel-data="classroomPanelData"
      :cells-count="cellsCount"
      :format-save-time="formatSaveTime"
      @back="handleBack"
      @manual-save="handleManualSave"
      @publish="handlePublish"
      @toggle-compact="compactMode = !compactMode"
      @toggle-preview="handleTogglePreviewMode"
      @fullscreen-preview="toggleFullscreenPreview"
      @show-ai-assistant="showLessonAssistant = true"
      @export-lesson="handleExportLesson"
    />

    <!-- 主内容区 -->
    <LessonEditorMainContent
      :is-loading="isLoading"
      :load-error="loadError"
      :current-lesson="currentLesson"
      :is-preview-mode="isPreviewMode"
      :is-fullscreen-preview="isFullscreenPreview"
      :compact-mode="compactMode"
      :toolbar-collapsed="toolbarCollapsed"
      :show-classroom-panel="showClassroomPanel"
      :show-reference-panel="showReferencePanel"
      :reference-resource="referenceResource"
      :cover-image-url="coverImageUrl"
      :cover-image-load-error="coverImageLoadError"
      :sections="sections"
      :active-section-index="activeSectionIndex"
      :editing-tab-id="editingTabId"
      :cell-list-ref="cellListRef"
      :tabs-container-ref="tabsContainerRef"
      @toggle-toolbar-collapsed="toolbarCollapsed = !toolbarCollapsed"
      @add-cell-to-end="(cellType) => {
        console.log('LessonEditor: 收到 add-cell-to-end 事件', { cellType })
        handleAddCellToEnd(cellType as CellType)
      }"
      @back="handleBack"
      @cover-image-error="coverImageLoadError = true"
      @cover-image-load="coverImageLoadError = false"
      @upload-cover-image="() => triggerCoverImageUpload()"
      @session-changed="handleSessionChanged"
      @close-reference-panel="showReferencePanel = false"
      @show-pdf-viewer="showPDFViewer = true"
      @update-notes="handleNotesUpdated"
      @set-active-section="activeSectionIndex = $event"
      @tab-dbl-click="handleTabDblClick"
      @tab-edit-done="editingTabId = null"
      @delete-section="handleSectionDelete"
      @add-section="handleAddSection"
      @update-section="({ index, payload }) => handleSectionUpdate(index, payload)"
      @add-cell-in-section="(data) => {
        console.log('LessonEditor: 收到 add-cell-in-section 事件', { data })
        if (!data || typeof data !== 'object') {
          console.error('LessonEditor: add-cell-in-section 数据格式错误', { data })
          return
        }
        handleAddCellInSection(data.sectionIndex, data.indexInSection, data.cellType)
      }"
      @cell-update="handleCellUpdate"
      @cell-delete="handleDeleteCell"
      @cell-move-up="handleMoveUp"
      @cell-move-down="handleMoveDown"
    />

    <!-- Toast 提示 -->
    <LessonEditorToast :toast="toast" @close="toast.show = false" />

    <LessonAiAssistantDrawer
      v-model="showLessonAssistant"
      :lesson-title="lessonTitle"
      :lesson-outline="lessonOutline"
      @insert="handleAiInsert"
    />

    <ClassroomSelectorModal
      v-model="showPublishModal"
      :classrooms="availableClassrooms"
      :initial-selected-ids="selectedClassroomIds"
      :loading="isLoadingClassrooms"
      :error="publishModalError"
      @confirm="handlePublishConfirm"
      @cancel="handlePublishCancel"
    />

    <!-- MVP: PDF 查看器 -->
    <PDFViewerModal v-model="showPDFViewer" :resource-id="referenceResource?.id || null" />

    <!-- 浮动教学助手按钮（仅在授课模式显示） -->
    <TeachingAssistantFAB
      :visible="isPreviewMode"
      :classroom-id="currentClassroomId"
      @open-drawer="handleOpenAssistantDrawer"
    />

    <!-- 教学助手抽屉 -->
    <TeachingAssistantDrawer v-model="showAssistantDrawer" :classroom-id="currentClassroomId" />

    <!-- 全屏预览模式 -->
    <LessonEditorFullscreen
      :is-fullscreen-preview="isFullscreenPreview"
      :lesson-title="lessonTitle"
      :slide-mode="slideMode"
      :slide-fullscreen="slideFullscreen"
      :compact-mode="compactMode"
      :display-cells="displayCells"
      :current-cell="currentCell"
      :current-slide-index="currentSlideIndex"
      :show-slide-controls="showSlideControls"
      :slide-container-ref="slideContainerRef"
      @exit-fullscreen="toggleFullscreenPreview"
      @toggle-slide-mode="slideMode = !slideMode"
      @toggle-slide-fullscreen="handleSlideFullscreenToggle"
      @previous-slide="goToPreviousSlide"
      @next-slide="goToNextSlide"
      @slide-mouse-move="handleSlideMouseMove"
      @slide-mouse-leave="handleSlideMouseLeave"
      @controls-mouse-enter="handleControlsMouseEnter"
      @controls-mouse-leave="handleControlsMouseLeave"
      @scroll-to-top="scrollToTop"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLessonStore } from '../../store/lesson'
import { lessonService } from '../../services/lesson'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import type { LessonRelatedMaterial } from '../../types/lesson'
import CellToolbar from '../../components/Lesson/CellToolbar.vue'
import CellContainer from '../../components/Cell/CellContainer.vue'
import AddCellMenu from '../../components/Lesson/AddCellMenu.vue'
import SectionContainer from '../../components/Lesson/SectionContainer.vue'
import { isContentWithSections } from '../../utils/lessonContent'
import ReferenceResourcePanel from '../../components/Resource/ReferenceResourcePanel.vue'
import PDFViewerModal from '../../components/Resource/PDFViewerModal.vue'
import ClassroomSelectorModal from '../../components/Lesson/ClassroomSelectorModal.vue'
import LessonAiAssistantDrawer from '@/components/Teacher/LessonAiAssistantDrawer.vue'
import TeacherClassroomControlPanel from '@/components/Classroom/TeacherControlPanel.vue'
import TeachingAssistantFAB from '@/components/Teacher/TeachingAssistantFAB.vue'
import TeachingAssistantDrawer from '@/components/Teacher/TeachingAssistantDrawer.vue'
import LessonEditorToast from '@/components/Lesson/LessonEditorToast.vue'
import LessonEditorToolbar from '@/components/Lesson/LessonEditorToolbar.vue'
import LessonEditorMainContent from '@/components/Lesson/LessonEditorMainContent.vue'
import LessonEditorFullscreen from '@/components/Lesson/LessonEditorFullscreen.vue'
import type { ToastData } from '@/components/Lesson/LessonEditorToast.vue'
import { useLessonEditorSections } from '@/composables/useLessonEditorSections'
import { useLessonEditorCells, getDefaultCell } from '@/composables/useLessonEditorCells'
import { useLessonEditorSave } from '@/composables/useLessonEditorSave'
import { useLessonEditorSession } from '@/composables/useLessonEditorSession'
import { useLessonEditorNav } from '@/composables/useLessonEditorNav'
import { useLessonEditorSlides } from '@/composables/useLessonEditorSlides'
import { useLessonEditorCover } from '@/composables/useLessonEditorCover'
import { useLessonEditorPublish } from '@/composables/useLessonEditorPublish'
import { useFullscreen } from '@/composables/useFullscreen'
import { summarizeCell, markdownToHtml } from '@/utils/lessonEditorHelpers'
import api from '../../services/api'
import courseExportService from '../../services/courseExport'
import { useToast } from '@/composables/useToast'
import { getServerBaseUrl } from '@/utils/url'
import { createLogger } from '../../utils/logger'

const logger = createLogger('LESSON_EDITOR')

const router = useRouter()
const route = useRoute()
const lessonStore = useLessonStore()

// 模板 refs
const cellListRef = ref<HTMLElement>()
const tabsContainerRef = ref<HTMLElement>()
const slideContainerRef = ref<HTMLElement>()
const teacherControlPanelRef = ref<InstanceType<typeof TeacherClassroomControlPanel> | null>(null)
// 本地状态
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const toolbarCollapsed = ref(false)
const isPreviewMode = ref(false)
const compactMode = ref(true)
const lessonTitle = ref('')
const isFlowInteractionActive = ref(false)
let flowInteractionResumeTimer: ReturnType<typeof setTimeout> | null = null
const referenceResource = ref<any>(null)
const showReferencePanel = ref(true)
const showPDFViewer = ref(false)
const showLessonAssistant = ref(false)
const showClassroomPanel = ref(false)
const showAssistantDrawer = ref(false)
// Toast
const toast = ref<ToastData>({ show: false, type: 'success', message: '' })
function showToast(type: 'success' | 'error' | 'warning', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => { toast.value.show = false }, 3000)
}
// Composables: Sections, Cells, Save, Session, Nav
const { sections, activeSectionIndex, editingTabId, editingTabNameRef, handleSectionUpdate, handleSectionDelete, handleAddSection: _handleAddSection, handleTabDblClick, initTabsSortable, destroySortable } = useLessonEditorSections(tabsContainerRef)
const handleAddSection = () => _handleAddSection(showToast)
function initSortable() { /* 大环节模式下由 SectionContainer 负责，cell 级 Sortable 已禁用 */ }
const { createReferenceMaterialCell, scrollToNewCell, handleAddCellToEnd, handleAddCellInSection, handleAddCellAt, insertReferenceMaterial, handleCellUpdate, handleDeleteCell, handleMoveUp, handleMoveDown } = useLessonEditorCells(sections, activeSectionIndex, cellListRef, showToast)
const { saveStatus, lastSavedAt, hasUnsavedChanges, isSavingOnUnmount, handleManualSave, handleBack, formatSaveTime, saveOnUnmount } = useLessonEditorSave(sections, lessonTitle, isPreviewMode, showToast)
const { currentSessionId, providedSessionRef, providedSessionId, handleSessionChanged } = useLessonEditorSession(teacherControlPanelRef, isPreviewMode, showClassroomPanel)
const { isFullscreenPreview, toggleFullscreenPreview, handleTogglePreviewMode, handleExportLesson, exporting } = useLessonEditorNav(isPreviewMode, showToast)

// 从 TeacherControlPanel 获取导播台数据
const classroomPanelData = computed(() => {
  if (!isPreviewMode.value || !teacherControlPanelRef.value) {
    return null
  }
  const panel = teacherControlPanelRef.value as any
  return {
    session: panel.session?.value,
    activeStudents: panel.activeStudents?.value || [],
    totalStudents: panel.totalStudents?.value || 0,
    displayDuration: panel.displayDuration?.value || 0,
    remainingTime: panel.remainingTime?.value || 0,
    formatDuration: panel.formatDuration,
    formatRemainingTime: panel.formatRemainingTime,
    handleToggleDisplayMode: panel.handleToggleDisplayMode,
    handlePause: panel.handlePause,
    handleEnd: panel.handleEnd,
  }
})

// cells, displayCells, Slides, Cover, Publish, currentLesson
const cells = computed(() => lessonStore.cells)

// 计算cells数量，用于toolbar显示
const cellsCount = computed(() => cells.value?.length || 0)

const filteredCells = computed(() => {
  if (!cells.value?.length) return []
  if (!isPreviewMode.value) return cells.value
  const session = providedSessionRef.value
  if (session?.settings?.display_cell_orders) {
    const orders = session.settings.display_cell_orders
    if (orders.length === 0) return []
    return cells.value.filter((c, i) => orders.includes(c.order !== undefined ? c.order : i))
  }
  return cells.value
})
const displayCells = computed(() => (isPreviewMode.value ? filteredCells.value : cells.value))
const { slideMode, currentSlideIndex, slideFullscreen, showSlideControls, currentCell, isSlideNativeFullscreen, toggleSlideFullscreen, goToPreviousSlide, goToNextSlide, goToSlide, scrollToTop, handleSlideMouseMove, handleSlideMouseLeave, handleControlsMouseEnter, handleControlsMouseLeave, resetControlsTimer, clearControlsTimer, handleSlideKeydown } = useLessonEditorSlides(slideContainerRef, displayCells, isFullscreenPreview)
const { coverImageInput, isUploadingCoverImage, showCoverImagePreview, coverImagePreviewUrl, coverImagePreviewFile, coverImagePreview, imageQuality, maxImageWidth, maxImageHeight, coverImageLoadError, coverImageUrl, triggerCoverImageUpload, handleCoverImageSelect, cancelCoverImageEdit, processAndUploadCoverImage } = useLessonEditorCover(showToast)
const { showPublishModal, selectedClassroomIds, publishError, publishModalError, handlePublish, handlePublishConfirm, handlePublishCancel } = useLessonEditorPublish(showToast)
const currentLesson = computed(() => lessonStore.currentLesson)

provide('classroomSession', providedSessionRef)
provide('classroomSessionId', providedSessionId)
provide(
  'currentLessonId',
  computed(() => currentLesson.value?.id)
)

// 判断是否可以进入授课模式（只有已发布的教案才能进入授课模式）
const canEnterPreviewMode = computed(() => {
  return currentLesson.value?.status === 'published'
})

// 获取当前班级ID（用于教学助手）
const currentClassroomId = computed(() => {
  // 优先从 lesson 的 classroom_ids 中获取第一个
  if (currentLesson.value?.classroom_ids && currentLesson.value.classroom_ids.length > 0) {
    return currentLesson.value.classroom_ids[0]
  }
  // 如果 session 中有 classroom_id，也可以使用
  // 这里暂时返回 null，后续可以根据实际需求扩展
  return null
})

// 处理打开教学助手抽屉
function handleOpenAssistantDrawer(type: 'attendance' | 'behavior' | 'discipline' | 'duty') {
  showAssistantDrawer.value = true
}

// 调试：输出课堂控制按钮的显示条件
watch([isPreviewMode, () => currentLesson.value?.status], ([preview, status]) => {
  if (preview) {
    logger.debug("课堂控制按钮显示条件:", {
      isPreviewMode: preview,
      lessonStatus: status,
      shouldShow: preview && status === 'published'
    })
  }
}, { immediate: true })

const isSaving = computed(() => lessonStore.isSaving)
const availableClassrooms = computed(() => lessonStore.availableClassrooms)
const isLoadingClassrooms = computed(() => lessonStore.isLoadingClassrooms)
const classroomsError = computed(() => lessonStore.classroomsError)

const lessonOutline = computed(() => {
  const list = cells.value || []
  if (list.length === 0) return ''
  const items = list
    .slice(0, 6)
    .map((cell, index) => summarizeCell(cell as Cell, index))
    .filter((item): item is string => Boolean(item))
  return items.join('\n')
})

// 标记是否最近从未发布状态切换的
const isRecentlyUnpublished = ref(false)


// 处理课堂控制按钮点击
function handleClassroomButtonClick() {
  if (!isPreviewMode.value) {
    // 如果不在预览模式，自动切换到预览模式并打开课堂控制面板
    isPreviewMode.value = true
    showClassroomPanel.value = true
    showToast('success', '已进入预览模式，课堂控制面板已打开')
    return
  }
  showClassroomPanel.value = !showClassroomPanel.value
}

// 切换幻灯片全屏（使用浏览器原生全屏API）
async function handleSlideFullscreenToggle() {
  try {
    await toggleSlideFullscreen()
  } catch (error) {
    console.error('切换幻灯片全屏失败:', error)
  }
}

// 监听预览模式变化
watch(isPreviewMode, (newValue) => {
  if (newValue) {
    destroySortable()
    // 进入授课模式时，自动打开课堂控制面板
    if (currentLesson.value?.status === 'published') {
      showClassroomPanel.value = true
    }
  } else {
    nextTick(() => {
      setTimeout(initSortable, 100)
      setTimeout(initTabsSortable, 100)
    })
  }
})

// 监听 cells 变化，重新初始化拖拽（当 cells 数量变化时）
watch(
  () => cells.value.length,
  () => {
    if (!isPreviewMode.value && cellListRef.value) {
      nextTick(() => {
        destroySortable()
        setTimeout(initSortable, 100)
        setTimeout(initTabsSortable, 100)
      })
    }
  }
)

// 监听全屏预览模式，添加键盘快捷键
watch(isFullscreenPreview, (newValue) => {
  if (newValue) {
    // 添加键盘事件监听
    document.addEventListener('keydown', handleFullscreenKeydown)
  } else {
    // 移除键盘事件监听
    document.removeEventListener('keydown', handleFullscreenKeydown)
  }
})

// 监听幻灯片模式切换，重置索引
watch(slideMode, (newValue) => {
  if (newValue && isFullscreenPreview.value) {
    // 切换到幻灯片模式时，重置到第一页
    currentSlideIndex.value = 0
    // 退出全屏模式
    slideFullscreen.value = false
  }
})

// 监听原生全屏状态变化，同步到slideFullscreen
watch(isSlideNativeFullscreen, (newValue) => {
  slideFullscreen.value = newValue
  if (newValue) {
    // 进入全屏时，显示控制按钮
    showSlideControls.value = true
    resetControlsTimer()
  } else {
    // 退出全屏时，清除定时器
    clearControlsTimer()
  }
})

// 监听全屏模式切换，重置控制按钮显示状态
watch(slideFullscreen, (newValue) => {
  if (newValue) {
    // 进入全屏时，显示控制按钮
    showSlideControls.value = true
    resetControlsTimer()
  } else {
    // 退出全屏时，清除定时器
    clearControlsTimer()
  }
})

// 监听cells变化，确保索引有效（useLessonEditorSlides 内部也有类似逻辑）
watch(
  () => cells.value.length,
  (newLength) => {
    if (slideMode.value && currentSlideIndex.value >= newLength) {
      currentSlideIndex.value = Math.max(0, newLength - 1)
    }
  }
)

// 处理全屏预览的键盘事件
function handleFullscreenKeydown(event: KeyboardEvent) {
  if (handleSlideKeydown(event)) return
  if (event.key === 'Escape' && isFullscreenPreview.value) toggleFullscreenPreview()
}

function handleFlowInteractionStartEvent() {
  if (flowInteractionResumeTimer) {
    clearTimeout(flowInteractionResumeTimer)
    flowInteractionResumeTimer = null
  }
  isFlowInteractionActive.value = true
}

function handleFlowInteractionEndEvent() {
  if (flowInteractionResumeTimer) {
    clearTimeout(flowInteractionResumeTimer)
  }
  flowInteractionResumeTimer = setTimeout(() => {
    isFlowInteractionActive.value = false
    flowInteractionResumeTimer = null
  }, 500)
}

// 监听标题变化
watch(
  () => currentLesson.value?.title,
  (newTitle) => {
    if (newTitle !== undefined) {
      lessonTitle.value = newTitle
    }
  }
)

// MVP: 处理参考笔记更新
function handleNotesUpdated(notes: string) {
  if (currentLesson.value) {
    currentLesson.value.reference_notes = notes
  }
}

function handleAiInsert(content: string) {
  if (!currentLesson.value) return
  const html = markdownToHtml(content)
  if (!html) {
    showToast('error', 'AI 返回内容为空，插入失败')
    return
  }
  const teaching = sections.value.find((s) => s.order === 1)
  if (!teaching) return
  if (!teaching.cells) teaching.cells = []
  const idx = teaching.cells.length
  const newCell = getDefaultCell(CellType.TEXT, idx)
  ;(newCell.content as any).html = html
  teaching.cells.push(newCell)
  showToast('success', 'AI 建议已插入到教案末尾')
  const globalIndex = sections.value.reduce((a, s) => a + (s.cells?.length || 0), 0) - 1
  nextTick(() => scrollToNewCell(globalIndex))
}

// 页面加载
onMounted(async () => {
  // 添加页面卸载和可见性变化监听
  window.addEventListener('beforeunload', handleBeforeUnload)
  document.addEventListener('visibilitychange', handleVisibilityChange)

  window.addEventListener('flowchart-interaction-start', handleFlowInteractionStartEvent)
  window.addEventListener('flowchart-interaction-end', handleFlowInteractionEndEvent)

  const lessonId = Number(route.params.id)

  if (!lessonId || isNaN(lessonId)) {
    loadError.value = '无效的教案 ID'
    isLoading.value = false
    return
  }

  try {
    // 检查是否存在已发布教案的状态标记
    const wasPublished = sessionStorage.getItem(`lesson_${lessonId}_was_published`)

    await lessonStore.loadLesson(lessonId)
    lessonTitle.value = currentLesson.value?.title || ''

    const consumeQueue =
      typeof lessonStore.consumeReferenceQueue === 'function'
        ? lessonStore.consumeReferenceQueue
        : () => {
            const pending = lessonStore.pendingReferenceMaterials
            const items = Array.isArray((pending as any)?.value) ? [...(pending as any).value] : []
            if ((pending as any)?.value) {
              (pending as any).value = []
            }
            return items as LessonRelatedMaterial[]
          }

    const pendingMaterials = consumeQueue()
    if (pendingMaterials.length > 0 && currentLesson.value) {
      const insertedIndices: number[] = []
      let skippedCount = 0

      pendingMaterials.forEach((material) => {
        if (!material.is_accessible) {
          skippedCount += 1
          return
        }
        const index = insertReferenceMaterial(material)
        if (index !== null) {
          insertedIndices.push(index)
        }
      })

      const c = currentLesson.value.content
      if (Array.isArray(c)) {
        c.forEach((cell, idx) => {
          cell.order = idx
        })
      } else if (isContentWithSections(c)) {
        let i = 0
        for (const sec of c.sections || []) {
          for (const cell of sec.cells || []) {
            cell.order = i++
          }
        }
      }

      if (insertedIndices.length > 0) {
        await nextTick()
        scrollToNewCell(insertedIndices[0])
      }

      if (insertedIndices.length > 0 || skippedCount > 0) {
        const parts: string[] = []
        if (insertedIndices.length > 0) {
          parts.push(`已插入 ${insertedIndices.length} 个参考素材`)
        }
        if (skippedCount > 0) {
          parts.push(`${skippedCount} 个素材因权限限制未能插入`)
        }
        showToast(insertedIndices.length > 0 ? 'success' : 'error', parts.join('，'))
      }
    }

    // 如果这个教案刚刚从未发布状态切换，显示提示
    if (wasPublished && currentLesson.value?.status === 'draft') {
      isRecentlyUnpublished.value = true
      sessionStorage.removeItem(`lesson_${lessonId}_was_published`)
      // 5秒后隐藏提示
      setTimeout(() => {
        isRecentlyUnpublished.value = false
      }, 5000)
    }

    // MVP: 加载参考资源
    if (currentLesson.value?.reference_resource_id) {
      try {
        const { lessonService } = await import('../../services/lesson')
        referenceResource.value = await lessonService.getReferenceResource(lessonId)
      } catch (error) {
        console.error('Failed to load reference resource:', error)
      }
    }

    // 初始化拖拽
    setTimeout(initSortable, 100)
    setTimeout(initTabsSortable, 100)
  } catch (error: any) {
    loadError.value = error.message || '加载教案失败'
  } finally {
    isLoading.value = false
  }
})

// 页面卸载前提示用户
const handleBeforeUnload = (event: BeforeUnloadEvent) => {
  if (hasUnsavedChanges.value && currentLesson.value && !isPreviewMode.value) {
    // 提示用户有未保存的更改
    // 注意：现代浏览器会忽略自定义消息，只显示默认提示
    event.preventDefault()
    event.returnValue = ''
    return event.returnValue
  }
}

// 页面可见性变化时（切换标签页、最小化窗口等）
// 已删除自动保存，避免并发保存导致数据覆盖
// 用户需要手动点击保存按钮
const handleVisibilityChange = async () => {
  // 不再自动保存，避免并发保存导致数据覆盖
  // 用户需要手动点击保存按钮
}

// 组件卸载
onUnmounted(async () => {
  await saveOnUnmount()

  // 移除事件监听
  window.removeEventListener('beforeunload', handleBeforeUnload)
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  destroySortable()
  // 确保恢复body滚动
  document.body.style.overflow = ''
  // 移除键盘事件监听
  document.removeEventListener('keydown', handleFullscreenKeydown)
  window.removeEventListener('flowchart-interaction-start', handleFlowInteractionStartEvent)
  window.removeEventListener('flowchart-interaction-end', handleFlowInteractionEndEvent)
  if (flowInteractionResumeTimer) {
    clearTimeout(flowInteractionResumeTimer)
    flowInteractionResumeTimer = null
  }
  // 清除控制按钮定时器
  clearControlsTimer()
})
</script>

<style scoped>
/* 全屏预览动画 */
.fullscreen-fade-enter-active,
.fullscreen-fade-leave-active {
  transition: all 0.3s ease;
}

.fullscreen-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fullscreen-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 幻灯片切换动画 */
.slide-fade-enter-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.slide-fade-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
  position: absolute;
  width: 100%;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 触摸优化 */
.touch-manipulation {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

/* 幻灯片全屏模式 */
.slide-fullscreen-mode {
  @apply bg-gray-900;
}

.slide-fullscreen-mode .flex {
  height: 100%;
}

/* 全屏模式下隐藏 CellContainer 的边框和背景，添加白色背景 */
.slide-fullscreen-mode :deep(.cell-container) {
  @apply border-0 shadow-lg bg-white rounded-lg;
  max-height: none;
  max-width: 95vw;
  margin: auto;
  overflow: visible;
}

.slide-fullscreen-mode :deep(.cell-container > div) {
  @apply bg-white;
}

/* 确保文本内容可以滚动 */
.slide-fullscreen-mode :deep(.cell-container .text-cell-view),
.slide-fullscreen-mode :deep(.cell-container .text-cell-editor),
.slide-fullscreen-mode :deep(.cell-container .prose) {
  max-height: none;
  overflow: visible;
}

/* 全屏模式下优化内容显示 */
.slide-fullscreen-mode :deep(.cell-container .prose) {
  @apply max-w-none;
}

.slide-fullscreen-mode :deep(.cell-container img) {
  @apply max-h-[70vh] mx-auto;
}

/* 浏览器原生全屏模式下的样式 */
:fullscreen .slide-fullscreen-mode,
:-webkit-full-screen .slide-fullscreen-mode,
:-moz-full-screen .slide-fullscreen-mode,
:-ms-fullscreen .slide-fullscreen-mode {
  @apply bg-gray-900;
}

/* 只对幻灯片内容区域应用全屏样式，不影响按钮容器 */
:fullscreen .slide-fullscreen-mode > .flex.justify-center,
:-webkit-full-screen .slide-fullscreen-mode > .flex.justify-center,
:-moz-full-screen .slide-fullscreen-mode > .flex.justify-center,
:-ms-fullscreen .slide-fullscreen-mode > .flex.justify-center {
  min-height: 100vh;
  width: 100vw;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 确保按钮容器不受全屏样式影响，并确保在最上层 */
:fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8,
:-webkit-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8,
:-moz-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8,
:-ms-fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8 {
  height: auto !important;
  width: auto !important;
  flex-shrink: 0;
  z-index: 9999 !important;
  pointer-events: auto !important;
}

/* 确保按钮本身可以点击 */
:fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8 button,
:-webkit-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8 button,
:-moz-full-screen .slide-fullscreen-mode .fixed.bottom-8.right-8 button,
:-ms-fullscreen .slide-fullscreen-mode .fixed.bottom-8.right-8 button {
  pointer-events: auto !important;
  position: relative;
  z-index: 10000;
}

/* 控制按钮淡入淡出动画 */
.controls-fade-enter-active,
.controls-fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.controls-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.controls-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 滚动条样式优化 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 拖拽相关样式 */
.sortable-ghost {
  opacity: 0.5;
  background: #eff6ff;
  border: 2px dashed #3b82f6;
}

.sortable-chosen {
  transform: scale(1.02);
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.sortable-drag {
  opacity: 0.75;
}

/* 拖拽手柄悬停效果 */
.drag-handle:hover {
  transform: scale(1.1);
}

/* 可拖拽区域样式 */
.cell-drag-area {
  user-select: none;
  -webkit-user-select: none;
}

.cell-drag-area:hover {
  background-color: rgba(59, 130, 246, 0.05);
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

/* 隐藏滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
