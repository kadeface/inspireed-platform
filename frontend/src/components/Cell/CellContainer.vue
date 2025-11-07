<template>
  <div class="cell-wrapper" :data-cell-id="cell.id" :data-cell-index="props.index">
    <div class="cell-header" v-if="showHeader">
      <div class="flex items-center gap-3 flex-1">
        <!-- 拖拽手柄 -->
        <button
          v-if="draggable"
          class="drag-handle cursor-move p-1 text-gray-400 hover:text-gray-600"
          title="拖拽排序"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
          </svg>
        </button>
        <span class="cell-type-badge">{{ cellTypeLabel }}</span>
        <span class="cell-order">#{{ cell.order + 1 }}</span>
        
        <!-- 可编辑标题 -->
        <div class="flex-1" v-if="editable">
          <input
            v-if="isEditingTitle"
            v-model="localTitle"
            @blur="saveTitle"
            @keyup.enter="saveTitle"
            @keyup.esc="cancelEditTitle"
            class="cell-title-input"
            placeholder="输入模块标题..."
            ref="titleInputRef"
          />
          <div
            v-else
            @click="startEditTitle"
            class="cell-title-display"
            :title="cell.title || '点击添加标题'"
          >
            <span v-if="cell.title" class="text-gray-700">{{ cell.title }}</span>
            <span v-else class="text-gray-400 italic">点击添加标题</span>
            <svg class="w-4 h-4 ml-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </div>
        </div>
        <div v-else-if="cell.title" class="flex-1 text-gray-700 font-medium">
          {{ cell.title }}
        </div>
      </div>
      
      <div class="cell-actions" v-if="editable">
        <!-- 上下移动按钮 -->
        <div v-if="showMoveButtons" class="flex gap-1 mr-2">
          <button
            @click="emit('moveUp', cell.id)"
            class="p-1 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="上移"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
            </svg>
          </button>
          <button
            @click="emit('moveDown', cell.id)"
            class="p-1 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="下移"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
        
        <button
          @click="emit('delete', cell.id)"
          class="text-red-500 hover:text-red-700 text-sm px-2 py-1 rounded hover:bg-red-50"
        >
          删除
        </button>
      </div>
    </div>

    <component
      :is="cellComponent"
      :cell="cell as any"
      :editable="editable"
      @update="handleUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import TextCell from './TextCell.vue'
import CodeCell from './CodeCell.vue'
import ParamCell from './ParamCell.vue'
import SimCell from './SimCell.vue'
import ChartCell from './ChartCell.vue'
import ContestCell from './ContestCell.vue'
import VideoCell from './VideoCell.vue'
import ActivityCell from './ActivityCell.vue'
import FlowchartCell from './FlowchartCell.vue'

interface Props {
  cell: Cell
  editable?: boolean
  showHeader?: boolean
  draggable?: boolean
  showMoveButtons?: boolean
  index?: number
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  showHeader: true,
  draggable: false,
  showMoveButtons: false,
  index: 0,
})

const emit = defineEmits<{
  update: [cell: Cell]
  delete: [cellId: string]
  moveUp: [cellId: string]
  moveDown: [cellId: string]
}>()

// 标题编辑状态
const isEditingTitle = ref(false)
const localTitle = ref('')
const titleInputRef = ref<HTMLInputElement>()

// 开始编辑标题
function startEditTitle() {
  localTitle.value = props.cell.title || ''
  isEditingTitle.value = true
  nextTick(() => {
    titleInputRef.value?.focus()
  })
}

// 保存标题
function saveTitle() {
  isEditingTitle.value = false
  if (localTitle.value.trim() !== props.cell.title) {
    const updatedCell = {
      ...props.cell,
      title: localTitle.value.trim() || undefined,
    }
    emit('update', updatedCell)
  }
}

// 取消编辑
function cancelEditTitle() {
  isEditingTitle.value = false
  localTitle.value = ''
}

const cellComponent = computed(() => {
  const componentMap = {
    [CellType.TEXT]: TextCell,
    [CellType.CODE]: CodeCell,
    [CellType.PARAM]: ParamCell,
    [CellType.SIM]: SimCell,
    [CellType.CHART]: ChartCell,
    [CellType.CONTEST]: ContestCell,
    [CellType.VIDEO]: VideoCell,
    [CellType.ACTIVITY]: ActivityCell,
    [CellType.FLOWCHART]: FlowchartCell,
  }
  return componentMap[props.cell.type]
})

const cellTypeLabel = computed(() => {
  const labelMap = {
    [CellType.TEXT]: '文本',
    [CellType.CODE]: '代码',
    [CellType.PARAM]: '参数',
    [CellType.SIM]: '仿真',
    [CellType.CHART]: '图表',
    [CellType.CONTEST]: '竞赛',
    [CellType.VIDEO]: '视频',
    [CellType.ACTIVITY]: '活动',
    [CellType.FLOWCHART]: '流程图',
  }
  return labelMap[props.cell.type]
})

function handleUpdate(updatedCell: Cell) {
  emit('update', updatedCell)
}
</script>

<style scoped>
.cell-wrapper {
  @apply mb-4 border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow;
}

.cell-header {
  @apply flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200;
}

.cell-type-badge {
  @apply inline-flex items-center px-3 py-1 text-base font-semibold bg-blue-100 text-blue-800 rounded;
}

.cell-order {
  @apply text-base font-medium text-gray-600;
}

.cell-title-input {
  @apply w-full px-3 py-1 text-base font-medium text-gray-800 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white;
}

.cell-title-display {
  @apply cursor-pointer px-3 py-1 text-base font-medium rounded hover:bg-gray-100 transition-colors flex items-center;
}

.cell-actions {
  @apply flex gap-2;
}
</style>

