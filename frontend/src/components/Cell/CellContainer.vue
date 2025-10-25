<template>
  <div class="cell-wrapper" :data-cell-id="cell.id" :data-cell-index="props.index">
    <div class="cell-header" v-if="showHeader">
      <div class="flex items-center gap-2">
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
import { computed } from 'vue'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import TextCell from './TextCell.vue'
import CodeCell from './CodeCell.vue'
import ParamCell from './ParamCell.vue'
import SimCell from './SimCell.vue'
import QACell from './QACell.vue'
import ChartCell from './ChartCell.vue'
import ContestCell from './ContestCell.vue'
import VideoCell from './VideoCell.vue'

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

const cellComponent = computed(() => {
  const componentMap = {
    [CellType.TEXT]: TextCell,
    [CellType.CODE]: CodeCell,
    [CellType.PARAM]: ParamCell,
    [CellType.SIM]: SimCell,
    [CellType.QA]: QACell,
    [CellType.CHART]: ChartCell,
    [CellType.CONTEST]: ContestCell,
    [CellType.VIDEO]: VideoCell,
  }
  return componentMap[props.cell.type]
})

const cellTypeLabel = computed(() => {
  const labelMap = {
    [CellType.TEXT]: '文本',
    [CellType.CODE]: '代码',
    [CellType.PARAM]: '参数',
    [CellType.SIM]: '仿真',
    [CellType.QA]: '问答',
    [CellType.CHART]: '图表',
    [CellType.CONTEST]: '竞赛',
    [CellType.VIDEO]: '视频',
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
  @apply flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200;
}

.cell-type-badge {
  @apply inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded;
}

.cell-order {
  @apply text-sm text-gray-500;
}

.cell-actions {
  @apply flex gap-2;
}
</style>

