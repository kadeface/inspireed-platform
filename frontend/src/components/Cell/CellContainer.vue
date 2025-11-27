<template>
  <div
    class="mb-4 rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
    :class="{ 'overflow-hidden': cell.type !== 'flowchart' }"
    :data-cell-id="cell.id"
    :data-cell-index="props.index"
  >
    <div class="flex">
      <aside
        :class="[
          'flex w-28 flex-shrink-0 flex-col items-center justify-center gap-2 border-r border-gray-200 px-3 py-6 text-white',
          stageStyles.bg
        ]"
      >
        <span :class="['text-xs tracking-[0.3em]', stageStyles.label]">环节</span>
        <span class="text-3xl font-semibold leading-none">{{ cell.order + 1 }}</span>
        <div class="w-full">
          <textarea
            v-if="editable"
            v-model="localStageLabel"
            @blur="handleStageLabelSave"
            @keyup.enter.prevent="handleStageLabelSave"
            rows="2"
            class="w-full resize-none rounded-md bg-white/15 px-2 py-1 text-center text-xs font-medium leading-snug text-white outline-none ring-0 placeholder:text-white/60 focus:bg-white/20 focus:text-white focus:ring-2 focus:ring-white/70"
            placeholder="输入环节名称"
          />
          <p
            v-else
            :class="['text-center text-xs font-medium leading-snug', stageStyles.label]"
          >
            {{ displayStageLabel }}
          </p>
        </div>
      </aside>

      <div class="flex-1 min-w-0">
        <div
          v-if="showHeader"
          class="flex items-center justify-between border-b border-gray-200 bg-gray-50 px-4 py-3"
        >
          <div class="flex flex-1 items-center gap-3 min-w-0">
            <!-- 拖拽手柄 -->
            <button
              v-if="draggable"
              class="drag-handle flex-shrink-0 cursor-grab active:cursor-grabbing p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-all duration-200"
              title="拖拽排序"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
              </svg>
            </button>
            <span class="inline-flex items-center rounded bg-blue-100 px-3 py-1 text-base font-semibold text-blue-800">
              {{ cellTypeLabel }}
            </span>

            <!-- 可编辑标题 -->
            <div class="flex-1 min-w-0" v-if="editable">
              <div class="cell-title-editor">
                <input
                  v-if="isEditingTitle"
                  v-model="localTitle"
                  @blur="saveTitle"
                  @keyup.enter="saveTitle"
                  @keyup.esc="cancelEditTitle"
                  @mousedown.stop
                  @click.stop
                  class="w-full rounded border border-blue-300 px-3 py-1 text-base font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="输入模块标题..."
                  ref="titleInputRef"
                />
                <div
                  v-else
                  @click.stop="startEditTitle"
                  @mousedown.stop
                  class="flex cursor-pointer items-center rounded px-3 py-1 text-base font-medium transition-colors hover:bg-gray-100 min-w-0"
                  :title="cell.title || '点击添加标题'"
                >
                  <span v-if="cell.title" class="text-gray-700 truncate">{{ cell.title }}</span>
                  <span v-else class="italic text-gray-400">点击添加标题</span>
                  <svg class="ml-1 h-4 w-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </div>
              </div>
            </div>
            <div v-else-if="cell.title" class="flex-1 font-medium text-gray-700 cell-drag-area min-w-0 truncate" :class="{ 'cursor-move': draggable }">
              {{ cell.title }}
            </div>
            <div v-else class="flex-1 cell-drag-area" :class="{ 'cursor-move': draggable }"></div>
          </div>

          <div class="flex gap-2 flex-shrink-0" v-if="editable">
            <!-- 上下移动按钮 -->
            <div v-if="showMoveButtons" class="mr-2 flex gap-1">
              <button
                @click="emit('move-up', String(cell.id))"
                class="rounded p-1 text-gray-500 hover:bg-blue-50 hover:text-blue-600"
                title="上移"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <button
                @click="emit('move-down', String(cell.id))"
                class="rounded p-1 text-gray-500 hover:bg-blue-50 hover:text-blue-600"
                title="下移"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>

            <button
              @click="emit('delete', String(cell.id))"
              class="rounded px-2 py-1 text-sm text-red-500 hover:bg-red-50 hover:text-red-700"
            >
              删除
            </button>
          </div>
        </div>

        <component
          :is="cellComponent"
          :cell="cell as any"
          :editable="editable"
          :compact-mode="compactMode"
          @update="handleUpdate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
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
import FlowchartCellX6 from './FlowchartCellX6.vue'
import BrowserCell from './BrowserCell.vue'
import ReferenceMaterialCell from '@/components/Cell/ReferenceMaterialCell.vue'
import { useFeatureFlag } from '@/composables/useFeatureFlag'

interface Props {
  cell: Cell
  editable?: boolean
  showHeader?: boolean
  draggable?: boolean
  showMoveButtons?: boolean
  index?: number
  compactMode?: boolean // 紧凑模式：限制长内容的高度
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  showHeader: true,
  draggable: false,
  showMoveButtons: false,
  index: 0,
  compactMode: false,
})

const emit = defineEmits<{
  update: [cell: Cell]
  delete: [cellId: string]
  'move-up': [cellId: string]
  'move-down': [cellId: string]
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

// 特性开关
const { isEnabled } = useFeatureFlag()
const useX6Editor = isEnabled('use-x6-editor')

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
    // 使用特性开关选择流程图编辑器
    [CellType.FLOWCHART]: useX6Editor ? FlowchartCellX6 : FlowchartCell,
    [CellType.BROWSER]: BrowserCell,
    [CellType.REFERENCE_MATERIAL]: ReferenceMaterialCell,
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
    [CellType.BROWSER]: '浏览器',
    [CellType.REFERENCE_MATERIAL]: '参考素材',
  }
  return labelMap[props.cell.type]
})

const localStageLabel = ref(props.cell.stage_label ?? '')

watch(
  () => props.cell.stage_label,
  (value) => {
    localStageLabel.value = value ?? ''
  }
)

const displayStageLabel = computed(() => {
  if (props.cell.stage_label && props.cell.stage_label.trim()) {
    return props.cell.stage_label
  }
  if (props.cell.title && props.cell.title.trim()) {
    return props.cell.title
  }
  return cellTypeLabel.value
})

const stageStyles = computed(() => {
  const map = {
    [CellType.TEXT]: { bg: 'bg-violet-500', label: 'text-violet-100' },
    [CellType.CODE]: { bg: 'bg-blue-500', label: 'text-blue-100' },
    [CellType.PARAM]: { bg: 'bg-teal-500', label: 'text-teal-100' },
    [CellType.SIM]: { bg: 'bg-emerald-500', label: 'text-emerald-100' },
    [CellType.CHART]: { bg: 'bg-amber-500', label: 'text-amber-100' },
    [CellType.CONTEST]: { bg: 'bg-rose-500', label: 'text-rose-100' },
    [CellType.VIDEO]: { bg: 'bg-pink-500', label: 'text-pink-100' },
    [CellType.ACTIVITY]: { bg: 'bg-orange-500', label: 'text-orange-100' },
    [CellType.FLOWCHART]: { bg: 'bg-indigo-500', label: 'text-indigo-100' },
    [CellType.BROWSER]: { bg: 'bg-cyan-500', label: 'text-cyan-100' },
    [CellType.REFERENCE_MATERIAL]: { bg: 'bg-slate-500', label: 'text-slate-100' },
  }
  return map[props.cell.type] || { bg: 'bg-blue-500', label: 'text-blue-100' }
})

function handleUpdate(updatedCell: Cell) {
  emit('update', updatedCell)
}

function handleStageLabelSave() {
  const trimmed = localStageLabel.value.trim()
  const newValue = trimmed.length > 0 ? trimmed : undefined

  if (newValue !== props.cell.stage_label) {
    const updatedCell: Cell = {
      ...props.cell,
      stage_label: newValue,
    }
    emit('update', updatedCell)
  }
  localStageLabel.value = newValue ?? ''
}

function resetStageLabel() {
  localStageLabel.value = props.cell.stage_label ?? ''
}
</script>

