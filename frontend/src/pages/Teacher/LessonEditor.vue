<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部工具栏 -->
    <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- 左侧：返回按钮 + 标题 -->
          <div class="flex items-center gap-4 flex-1">
            <button
              @click="handleBack"
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              title="返回"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <input
              v-model="lessonTitle"
              type="text"
              placeholder="教案标题"
              class="text-lg font-semibold text-gray-900 border-none outline-none bg-transparent flex-1 max-w-md focus:ring-2 focus:ring-blue-500 rounded px-2"
            />
          </div>

          <!-- 右侧：操作按钮 -->
          <div class="flex items-center gap-3">
            <!-- 保存状态指示器 -->
            <div class="flex items-center gap-2 text-sm">
              <span v-if="saveStatus === 'saving'" class="text-gray-500 flex items-center gap-1">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                保存中...
              </span>
              <span v-else-if="saveStatus === 'saved'" class="text-green-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                已保存
              </span>
              <span v-else-if="saveStatus === 'error'" class="text-red-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                保存失败
              </span>
              <span v-else-if="lastSavedAt" class="text-gray-500">
                {{ formatSaveTime(lastSavedAt) }}
              </span>
            </div>

            <!-- 教案状态提示 -->
            <div v-if="currentLesson?.status === 'published'" class="flex items-center gap-2 px-3 py-1.5 text-sm text-orange-600 bg-orange-50 rounded-md">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              已发布教案
            </div>

            <!-- 手动保存按钮 -->
            <button
              @click="handleManualSave"
              :disabled="saveStatus === 'saving'"
              :class="[
                'px-3 py-1.5 text-sm font-medium rounded-md disabled:opacity-50',
                currentLesson?.status === 'published' 
                  ? 'text-orange-700 bg-orange-100 border border-orange-300 hover:bg-orange-200' 
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ currentLesson?.status === 'published' ? '保存修改*' : '保存' }}
            </button>

            <!-- 发布按钮 -->
            <button
              v-if="currentLesson?.status === 'draft'"
              @click="handlePublish"
              :disabled="isSaving"
              class="px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              发布
            </button>

            <!-- 预览模式切换 -->
            <button
              @click="isPreviewMode = !isPreviewMode"
              :class="[
                'px-3 py-1.5 text-sm font-medium rounded-md',
                isPreviewMode
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
              ]"
            >
              {{ isPreviewMode ? '编辑模式' : '预览模式' }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 左侧：Cell 工具箱 -->
      <CellToolbar
        v-if="!isPreviewMode"
        :collapsed="toolbarCollapsed"
        @add-cell="handleAddCellToEnd"
        @toggle-collapsed="toolbarCollapsed = !toolbarCollapsed"
      />

      <!-- 中间：编辑区 -->
      <main class="flex-1 overflow-y-auto">
        <div class="max-w-4xl mx-auto py-6 px-4">
          <!-- 加载状态 -->
          <div v-if="isLoading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">加载教案中...</p>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="loadError" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <svg class="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">加载失败</h3>
            <p class="mt-2 text-sm text-gray-600">{{ loadError }}</p>
            <button
              @click="handleBack"
              class="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              返回教案列表
            </button>
          </div>

          <!-- Cell 列表 -->
          <div v-else-if="currentLesson" class="space-y-4">
            <!-- MVP: 参考资源面板 -->
            <ReferenceResourcePanel
              v-if="showReferencePanel && referenceResource && !isPreviewMode"
              :lesson-id="currentLesson.id"
              :resource="referenceResource"
              :notes="currentLesson.reference_notes"
              @close="showReferencePanel = false"
              @view-pdf="showPDFViewer = true"
              @notes-updated="handleNotesUpdated"
            />
            
            <!-- 空状态 -->
            <div
              v-if="cells.length === 0"
              class="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center"
            >
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 class="mt-4 text-lg font-medium text-gray-900">开始创建教案内容</h3>
              <p class="mt-2 text-sm text-gray-600">从左侧工具栏选择要添加的单元类型</p>
            </div>

            <!-- Cell 列表容器 -->
            <div ref="cellListRef" class="space-y-4">
              <template v-for="(cell, index) in cells" :key="cell.id">
                <!-- 顶部添加按钮（第一个 Cell 前） -->
                <AddCellMenu
                  v-if="index === 0 && !isPreviewMode"
                  :insert-index="0"
                  @add="handleAddCellAt"
                />

                <!-- Cell 容器 -->
                <CellContainer
                  :cell="cell"
                  :index="index"
                  :editable="!isPreviewMode"
                  :draggable="!isPreviewMode"
                  :show-move-buttons="!isPreviewMode"
                  @update="handleCellUpdate"
                  @delete="handleDeleteCell"
                  @move-up="handleMoveUp"
                  @move-down="handleMoveDown"
                />

                <!-- Cell 之间的添加按钮 -->
                <AddCellMenu
                  v-if="!isPreviewMode"
                  :insert-index="index + 1"
                  @add="handleAddCellAt"
                />
              </template>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Toast 提示 -->
    <Transition name="toast-slide">
      <div
        v-if="toast.show"
        class="fixed top-4 right-4 z-50 max-w-sm"
      >
        <div
          :class="[
            'rounded-lg shadow-xl p-4 border-l-4 transform transition-all duration-300',
            toast.type === 'success' 
              ? 'bg-green-50 border-green-400 border-l-green-500' 
              : 'bg-red-50 border-red-400 border-l-red-500',
          ]"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div
                :class="[
                  'rounded-full p-1',
                  toast.type === 'success' ? 'bg-green-100' : 'bg-red-100'
                ]"
              >
                <svg
                  v-if="toast.type === 'success'"
                  class="h-4 w-4 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <svg
                  v-else
                  class="h-4 w-4 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
            </div>
            <div class="ml-3 flex-1">
              <p
                :class="[
                  'text-sm font-semibold',
                  toast.type === 'success' ? 'text-green-800' : 'text-red-800',
                ]"
              >
                {{ toast.message }}
              </p>
            </div>
            <button
              @click="toast.show = false"
              class="ml-2 flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MVP: PDF 查看器 -->
    <PDFViewerModal
      v-model="showPDFViewer"
      :resource-id="referenceResource?.id || null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLessonStore } from '../../store/lesson'
import { useAutoSave } from '../../composables/useAutoSave'
import { v4 as uuidv4 } from 'uuid'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import Sortable from 'sortablejs'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import CellToolbar from '../../components/Lesson/CellToolbar.vue'
import CellContainer from '../../components/Cell/CellContainer.vue'
import AddCellMenu from '../../components/Lesson/AddCellMenu.vue'
import ReferenceResourcePanel from '../../components/Resource/ReferenceResourcePanel.vue'
import PDFViewerModal from '../../components/Resource/PDFViewerModal.vue'

// 配置 dayjs
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const router = useRouter()
const route = useRoute()
const lessonStore = useLessonStore()

// 本地状态
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const toolbarCollapsed = ref(false)
const isPreviewMode = ref(false)
const cellListRef = ref<HTMLElement>()
const lessonTitle = ref('')

// MVP: 参考资源相关状态
const referenceResource = ref<any>(null)
const showReferencePanel = ref(true)
const showPDFViewer = ref(false)

// Toast 提示
const toast = ref({
  show: false,
  type: 'success' as 'success' | 'error',
  message: '',
})

// 计算属性
const currentLesson = computed(() => lessonStore.currentLesson)
const cells = computed(() => lessonStore.cells)
const isSaving = computed(() => lessonStore.isSaving)

// 自动保存
const { saveStatus, lastSavedAt, manualSave } = useAutoSave({
  data: computed(() => lessonStore.currentLesson),
  saveFn: async () => {
    if (currentLesson.value) {
      // 更新标题
      currentLesson.value.title = lessonTitle.value
      await lessonStore.saveCurrentLesson()
    }
  },
  delay: 3000,
  enabled: computed(() => !isPreviewMode.value && !!currentLesson.value),
})

// 格式化保存时间
function formatSaveTime(date: Date) {
  const now = dayjs()
  const saveTime = dayjs(date)
  const diffInMinutes = now.diff(saveTime, 'minute')
  
  if (diffInMinutes < 1) {
    return '刚刚保存'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前保存`
  } else {
    return saveTime.format('HH:mm 保存')
  }
}

// 生成默认 Cell 内容
function getDefaultCell(cellType: CellType, order: number): Cell {
  const baseCell = {
    id: uuidv4(),
    type: cellType,
    order,
    editable: true,
  }

  switch (cellType) {
    case CellType.TEXT:
      return {
        ...baseCell,
        type: CellType.TEXT,
        content: {
          html: '<p>在此输入文本内容...</p>',
        },
      } as Cell

    case CellType.CODE:
      return {
        ...baseCell,
        type: CellType.CODE,
        content: {
          code: '# 在此编写代码\nprint("Hello, World!")',
          language: 'python' as const,
        },
        config: {
          environment: 'jupyterlite' as const,
        },
      } as Cell

    case CellType.PARAM:
      return {
        ...baseCell,
        type: CellType.PARAM,
        content: {
          schema: {},
          values: {},
        },
      } as Cell

    case CellType.SIM:
      return {
        ...baseCell,
        type: CellType.SIM,
        content: {
          type: 'threejs' as const,
          config: {},
        },
      } as Cell

    case CellType.CHART:
      return {
        ...baseCell,
        type: CellType.CHART,
        content: {
          chartType: 'bar' as const,
          data: {},
          options: {},
        },
      } as Cell

    case CellType.CONTEST:
      return {
        ...baseCell,
        type: CellType.CONTEST,
        content: {
          title: '竞赛任务',
          description: '在此输入竞赛说明...',
          rules: {},
        },
      } as Cell

    case CellType.VIDEO:
      return {
        ...baseCell,
        type: CellType.VIDEO,
        content: {
          videoUrl: '',
          title: '',
          description: '',
        },
        config: {
          autoplay: false,
          controls: true,
          loop: false,
          muted: false,
        },
      } as Cell

    default:
      throw new Error(`Unknown cell type: ${cellType}`)
  }
}

// 添加 Cell 到末尾
function handleAddCellToEnd(cellType: CellType) {
  const newCell = getDefaultCell(cellType, cells.value.length)
  lessonStore.addCell(newCell)
  showToast('success', `已添加${getCellTypeName(cellType)}`)
}

// 在指定位置添加 Cell
function handleAddCellAt(cellType: CellType, index: number) {
  const newCell = getDefaultCell(cellType, index)
  
  // 插入 Cell
  if (currentLesson.value) {
    currentLesson.value.content.splice(index, 0, newCell)
    
    // 更新后续 Cell 的 order
    currentLesson.value.content.forEach((cell, idx) => {
      cell.order = idx
    })
  }
  
  showToast('success', `已添加${getCellTypeName(cellType)}`)
  
  // 滚动到新添加的单元
  nextTick(() => {
    scrollToNewCell(index)
  })
}

// 更新 Cell
function handleCellUpdate(updatedCell: Cell) {
  lessonStore.updateCell(updatedCell.id, updatedCell)
}

// 删除 Cell
function handleDeleteCell(cellId: string) {
  if (confirm('确定要删除这个单元吗？')) {
    lessonStore.deleteCell(cellId)
    showToast('success', '单元已删除')
  }
}

// 上移 Cell
function handleMoveUp(cellId: string) {
  const index = cells.value.findIndex((c) => c.id === cellId)
  if (index > 0) {
    lessonStore.reorderCells(index, index - 1)
  }
}

// 下移 Cell
function handleMoveDown(cellId: string) {
  const index = cells.value.findIndex((c) => c.id === cellId)
  if (index < cells.value.length - 1) {
    lessonStore.reorderCells(index, index + 1)
  }
}

// 手动保存
async function handleManualSave() {
  try {
    await manualSave()
    showToast('success', '保存成功')
  } catch (error: any) {
    showToast('error', error.message || '保存失败')
  }
}

// 发布教案
async function handlePublish() {
  try {
    await lessonStore.publishCurrentLesson()
    showToast('success', '教案已发布')
  } catch (error: any) {
    showToast('error', error.message || '发布失败')
  }
}

// 返回
function handleBack() {
  router.push('/teacher')
}

// 显示 Toast
function showToast(type: 'success' | 'error', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 滚动到新添加的单元
function scrollToNewCell(index: number) {
  if (!cellListRef.value) return
  
  const cellElements = cellListRef.value.querySelectorAll('[data-cell-index]')
  const targetElement = cellElements[index]
  
  if (targetElement) {
    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    })
    
    // 添加高亮效果
    targetElement.classList.add('ring-2', 'ring-blue-400', 'ring-opacity-75')
    setTimeout(() => {
      targetElement.classList.remove('ring-2', 'ring-blue-400', 'ring-opacity-75')
    }, 2000)
  }
}

// 获取 Cell 类型名称
function getCellTypeName(cellType: CellType): string {
  const nameMap = {
    [CellType.TEXT]: '文本单元',
    [CellType.CODE]: '代码单元',
    [CellType.PARAM]: '参数单元',
    [CellType.SIM]: '仿真单元',
    [CellType.CHART]: '图表单元',
    [CellType.CONTEST]: '竞赛单元',
    [CellType.VIDEO]: '视频单元',
  }
  return nameMap[cellType]
}

// 初始化拖拽排序
let sortableInstance: Sortable | null = null

function initSortable() {
  if (cellListRef.value && !isPreviewMode.value) {
    sortableInstance = Sortable.create(cellListRef.value, {
      animation: 150,
      handle: '.drag-handle',
      ghostClass: 'opacity-50',
      onEnd: (evt) => {
        if (evt.oldIndex !== undefined && evt.newIndex !== undefined) {
          lessonStore.reorderCells(evt.oldIndex, evt.newIndex)
        }
      },
    })
  }
}

function destroySortable() {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
}

// 监听预览模式变化
watch(isPreviewMode, (newValue) => {
  if (newValue) {
    destroySortable()
  } else {
    setTimeout(initSortable, 100)
  }
})

// 监听标题变化
watch(() => currentLesson.value?.title, (newTitle) => {
  if (newTitle !== undefined) {
    lessonTitle.value = newTitle
  }
})

// MVP: 处理参考笔记更新
function handleNotesUpdated(notes: string) {
  if (currentLesson.value) {
    currentLesson.value.reference_notes = notes
  }
}

// 页面加载
onMounted(async () => {
  const lessonId = Number(route.params.id)
  
  if (!lessonId || isNaN(lessonId)) {
    loadError.value = '无效的教案 ID'
    isLoading.value = false
    return
  }

  try {
    await lessonStore.loadLesson(lessonId)
    lessonTitle.value = currentLesson.value?.title || ''
    
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
  } catch (error: any) {
    loadError.value = error.message || '加载教案失败'
  } finally {
    isLoading.value = false
  }
})

// 组件卸载
onUnmounted(() => {
  destroySortable()
})
</script>

<style scoped>
.toast-slide-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-slide-leave-active {
  transition: all 0.3s ease-in;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

/* 添加脉冲动画效果 */
@keyframes pulse-success {
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}

.toast-slide-enter-active .rounded-lg {
  animation: pulse-success 0.6s ease-out;
}
</style>
