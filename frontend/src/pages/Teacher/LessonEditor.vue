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
            <div v-if="isRecentlyUnpublished" class="flex items-center gap-2 px-3 py-1.5 text-sm text-amber-600 bg-amber-50 rounded-md">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              已从已发布状态切换为草稿
            </div>

            <!-- 手动保存按钮 -->
            <button
              @click="handleManualSave"
              :disabled="saveStatus === 'saving'"
              class="px-3 py-1.5 text-sm font-medium rounded-md disabled:opacity-50 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50"
            >
              保存
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

            <!-- 全屏预览按钮 -->
            <button
              @click="toggleFullscreenPreview"
              class="px-3 py-1.5 text-sm font-medium rounded-md bg-purple-600 text-white hover:bg-purple-700 flex items-center gap-2"
              title="全屏预览"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              全屏预览
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

    <!-- 全屏预览模式 -->
    <Teleport to="body">
      <Transition name="fullscreen-fade">
        <div
          v-if="isFullscreenPreview"
          class="fixed inset-0 z-50 bg-gray-50 overflow-hidden"
        >
          <!-- 全屏预览顶部栏 -->
          <header class="bg-white shadow-sm sticky top-0 z-10">
            <div class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div>
                    <h1 class="text-xl font-bold text-gray-900">{{ lessonTitle }}</h1>
                    <p class="text-sm text-gray-500 mt-1">沉浸式预览</p>
                  </div>
                </div>
                <div class="flex items-center gap-4">
                  <!-- 退出全屏按钮 -->
                  <button
                    @click="toggleFullscreenPreview"
                    class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    退出预览
                  </button>
                </div>
              </div>
            </div>
          </header>

          <!-- 全屏预览内容 -->
          <div class="h-[calc(100vh-73px)] overflow-y-auto">
            <div class="max-w-5xl mx-auto px-6 py-8">
              <!-- Cell 列表 -->
              <div v-if="cells.length > 0" class="space-y-6">
                <CellContainer
                  v-for="(cell, index) in cells"
                  :key="cell.id"
                  :cell="cell"
                  :index="index"
                  :editable="false"
                  :draggable="false"
                  :show-move-buttons="false"
                />
              </div>

              <!-- 空状态 -->
              <div v-else class="text-center py-12">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="mt-4 text-lg text-gray-600">该教案暂无内容</p>
              </div>
            </div>
          </div>

          <!-- 浮动操作按钮 -->
          <div class="fixed bottom-8 right-8 flex flex-col gap-3">
            <!-- 返回顶部 -->
            <button
              @click="scrollToTop"
              class="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
              title="返回顶部"
            >
              <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
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
const isFullscreenPreview = ref(false)
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

// 标记是否最近从未发布状态切换的
const isRecentlyUnpublished = ref(false)

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
          type: 'phet' as const,
          config: {
            width: 800,
            height: 600,
            autoplay: false,
            locale: 'zh_CN'
          },
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

// 切换全屏预览
function toggleFullscreenPreview() {
  isFullscreenPreview.value = !isFullscreenPreview.value
  
  // 进入全屏时，禁止body滚动
  if (isFullscreenPreview.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

// 滚动到顶部
function scrollToTop() {
  const container = document.querySelector('.fixed.inset-0 .overflow-y-auto')
  if (container) {
    container.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
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

// 处理全屏预览的键盘事件
function handleFullscreenKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    toggleFullscreenPreview()
  }
}

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
    // 检查是否存在已发布教案的状态标记
    const wasPublished = sessionStorage.getItem(`lesson_${lessonId}_was_published`)
    
    await lessonStore.loadLesson(lessonId)
    lessonTitle.value = currentLesson.value?.title || ''
    
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
  } catch (error: any) {
    loadError.value = error.message || '加载教案失败'
  } finally {
    isLoading.value = false
  }
})

// 组件卸载
onUnmounted(() => {
  destroySortable()
  // 确保恢复body滚动
  document.body.style.overflow = ''
  // 移除键盘事件监听
  document.removeEventListener('keydown', handleFullscreenKeydown)
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
</style>
