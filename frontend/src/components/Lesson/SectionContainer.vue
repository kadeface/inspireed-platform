<template>
  <div class="section-container rounded-xl border border-gray-200 bg-white shadow-sm">
    <!-- 大环节标题栏 -->
    <div
      v-if="showHeader"
      class="section-header flex items-center gap-3 px-4 py-3 bg-gray-50 border-b border-gray-200 rounded-t-xl"
      :class="{ 'border-b-0': section.is_collapsed }"
    >
      <button
        v-if="editable"
        type="button"
        @click="toggleCollapsed"
        class="p-1 rounded text-gray-500 hover:bg-gray-200 transition-colors"
        :aria-label="section.is_collapsed ? '展开' : '折叠'"
      >
        <svg
          class="w-5 h-5 transition-transform"
          :class="{ '-rotate-90': section.is_collapsed }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
      <span
        v-if="!isEditingName"
        class="flex-1 font-semibold text-gray-800"
        @dblclick="startEditName"
      >
        {{ section.name }}
      </span>
      <input
        v-else
        ref="nameInputRef"
        v-model="editingName"
        type="text"
        class="flex-1 px-2 py-1 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        @blur="saveEditName"
        @keydown.enter="saveEditName"
        @keydown.escape="cancelEditName"
      />
      <span v-if="editable" class="text-sm text-gray-500"> {{ section.cells.length }} 个模块 </span>
      <!-- 自定义大环节：编辑名称、删除 -->
      <template v-if="editable && section.type === 'custom'">
        <button
          v-if="!isEditingName"
          type="button"
          @click="startEditName"
          class="p-1.5 rounded text-gray-400 hover:bg-gray-200 hover:text-gray-600"
          title="重命名"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
            />
          </svg>
        </button>
        <button
          type="button"
          @click="handleDelete"
          class="p-1.5 rounded text-gray-400 hover:bg-red-50 hover:text-red-600"
          title="删除大环节"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </template>
    </div>

    <!-- 大环节下的 Cells -->
    <div v-show="!section.is_collapsed" class="section-body px-2 pb-2">
      <div ref="cellListRef" :class="editable ? 'space-y-4' : 'space-y-2'">
        <template v-for="(cell, index) in section.cells" :key="cell.id">
          <div v-if="editable" class="add-cell-menu-container">
            <AddCellMenu
              :insert-index="index"
              @add="(t, i) => {
                console.log('SectionContainer: 发出 add-cell 事件', { sectionIndex, indexInSection: i, cellType: t })
                $emit('add-cell', sectionIndex, i, t)
              }"
            />
          </div>
          <CellContainer
            :cell="cell"
            :index="cellOffset + index"
            :editable="editable"
            :draggable="editable"
            :show-move-buttons="editable"
            :compact-mode="compactMode && editable"
            :lesson-id="lessonId"
            :interactive-viewer-mode="interactiveViewerMode"
            @update="(c) => $emit('cell-update', c)"
            @delete="(id) => $emit('cell-delete', id)"
            @move-up="(id) => $emit('cell-move-up', id)"
            @move-down="(id) => $emit('cell-move-down', id)"
          />
        </template>
        <!-- 末尾添加按钮 -->
        <div v-if="editable" class="add-cell-menu-container">
          <AddCellMenu
            :insert-index="section.cells.length"
            @add="(t, i) => {
              console.log('SectionContainer: 发出 add-cell 事件（末尾）', { sectionIndex, indexInSection: i, cellType: t })
              $emit('add-cell', sectionIndex, i, t)
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { SectionInContent } from '../../types/section'
import AddCellMenu from './AddCellMenu.vue'
import CellContainer from '../Cell/CellContainer.vue'
import type { InteractiveViewerRole } from '@/utils/interactiveView'

const props = withDefaults(
  defineProps<{
    section: SectionInContent
    sectionIndex: number
    /** 前面所有大环节的 cell 总数，用于 data-cell-index 以支持 scrollToNewCell */
    cellOffset?: number
    editable?: boolean
    compactMode?: boolean
    lessonId?: number
    showHeader?: boolean
    /** 交互式课件教师/学生视图（透传 CellContainer） */
    interactiveViewerMode?: InteractiveViewerRole
  }>(),
  { cellOffset: 0, editable: true, compactMode: false, showHeader: true }
)

const emit = defineEmits<{
  'update:section': [payload: Partial<SectionInContent>]
  'delete-section': []
  'add-cell': [sectionIndex: number, indexInSection: number, cellType: string]
  'cell-update': [cell: any]
  'cell-delete': [cellId: string]
  'cell-move-up': [cellId: string]
  'cell-move-down': [cellId: string]
}>()

const isEditingName = ref(false)
const editingName = ref('')
const nameInputRef = ref<HTMLInputElement | null>(null)

watch(
  () => props.section.name,
  (v) => {
    editingName.value = v
  },
  { immediate: true }
)

function toggleCollapsed() {
  emit('update:section', { is_collapsed: !props.section.is_collapsed })
}

function startEditName() {
  if (props.section.type !== 'custom') return
  editingName.value = props.section.name
  isEditingName.value = true
  nextTick(() => nameInputRef.value?.focus())
}

function saveEditName() {
  if (!isEditingName.value) return
  const v = editingName.value.trim()
  if (v && v !== props.section.name) {
    emit('update:section', { name: v })
  }
  isEditingName.value = false
}

function cancelEditName() {
  editingName.value = props.section.name
  isEditingName.value = false
}

function handleDelete() {
  if (props.section.type !== 'custom') return
  if (props.section.cells.length > 0) {
    if (
      !confirm(
        `「${props.section.name}」下还有 ${props.section.cells.length} 个模块，删除大环节后需先移动或删除这些模块。是否继续？`
      )
    ) {
      return
    }
  } else if (!confirm(`确定删除大环节「${props.section.name}」？`)) {
    return
  }
  emit('delete-section')
}
</script>
