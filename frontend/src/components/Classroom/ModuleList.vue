<template>
  <div class="module-list-container" data-testid="module-list-container">
    <!-- 导航控制栏（固定在顶部，始终可见） -->
    <div class="module-navigation-bar" v-if="cells.length > 0" data-testid="module-navigation-bar">
      <!-- 上一模块按钮 -->
      <button
        class="module-nav-btn module-nav-btn-prev"
        :class="{ 'module-nav-btn-disabled': !canGoPrev }"
        :disabled="!canGoPrev || loading"
        @click="handlePrevModule"
        data-testid="prev-module-button"
        :title="canGoPrev ? '上一模块' : '已经是第一个模块'"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>上一模块</span>
      </button>

      <!-- 当前模块：序号 + 标题（与下方预览联动时便于确认播出位置） -->
      <div
        class="module-nav-current"
        data-testid="module-navigation-current"
        :title="navCenterTitleFull"
      >
        <template v-if="currentModuleIndex < 0">
          <span class="module-nav-current-muted">未播出 / 已隐藏</span>
        </template>
        <template v-else>
          <span class="module-nav-current-index">{{ currentModuleIndex + 1 }} / {{ cells.length }}</span>
          <span class="module-nav-current-title">{{ navCenterTitleShort }}</span>
        </template>
      </div>

      <!-- 下一模块按钮 -->
      <button
        class="module-nav-btn module-nav-btn-next"
        :class="{ 'module-nav-btn-disabled': !canGoNext }"
        :disabled="!canGoNext || loading"
        @click="handleNextModule"
        data-testid="next-module-button"
        :title="canGoNext ? '下一模块' : '已经是最后一个模块'"
      >
        <span>下一模块</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <div class="module-list" ref="moduleListRef" v-if="cells.length > 0" data-testid="module-list">
      <!-- 课程模块列表 -->
      <ModuleCard
        v-for="(cell, index) in cells"
        :key="cell.id || index"
        :ref="el => setModuleItemRef(el, index)"
        :data-module-index="index"
        :data-testid="`cell-item-${index}`"
        :cell="cell"
        :index="index"
        :is-active="isModuleActive(cell, index)"
        :loading="loading"
        :is-multi-select-mode="isMultiSelectMode"
        :is-activity-active="isModuleActivityActive(cell, index)"
        :show-learning-meta="showLearningMeta"
        @click="handleModuleItemClick"
        @checkbox-click="handleModuleCheckboxClick"
        @checkbox-change="handleModuleCheckboxChange"
      />
    </div>
    <div v-else class="module-empty">
      <p>暂无课程模块</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { CellType, type Cell } from '../../types/cell'
import ModuleCard from './ModuleCard.vue'

// Cell类型图标组件
const CellTypeIcon = (props: { type: string }) => {
  const icons: Record<string, any> = {
    text: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M4 6h16M4 12h16M4 18h16' })
    ]),
    code: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' })
    ]),
    activity: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' })
    ]),
    video: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ]),
    flowchart: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' })
    ]),
    qa: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
    ]),
    browser: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9' })
    ]),
    interactive: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' })
    ]),
    reference_material: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', 'stroke-width': '2.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
    ]),
  }

  const IconComponent = icons[props.type] || icons.text
  return IconComponent()
}

interface Props {
  cells: Cell[]
  currentModuleIndex: number
  loading?: boolean
  isMultiSelectMode?: boolean
  displayCellOrders?: number[]
  sessionCurrentActivityId?: number | null
  showLearningMeta?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  isMultiSelectMode: false,
  displayCellOrders: () => [],
  sessionCurrentActivityId: null,
  // 授课导播台默认隐藏「难度/时长/进度状态」信息
  showLearningMeta: false,
})

const emit = defineEmits<{
  'item-click': [cell: Cell, index: number]
  'checkbox-click': [cell: Cell, index: number, event: Event]
  'checkbox-change': [cell: Cell, index: number, event: Event]
  'prev-module': []
  'next-module': []
}>()

// Refs
const moduleListRef = ref<HTMLElement | null>(null)
const moduleItemRefs = ref<Map<number, HTMLElement>>(new Map())

// 计算属性
const canGoPrev = computed(() => props.currentModuleIndex > 0)
const canGoNext = computed(() => props.cells.length > 0 && props.currentModuleIndex >= 0 && props.currentModuleIndex < props.cells.length - 1)


// Performance: Check if virtualization is needed for large lists
const shouldVirtualize = computed(() => props.cells.length > 20)
const navCenterTitleShort = computed(() => {
  if (props.currentModuleIndex < 0 || !props.cells.length) return ''
  const cell = props.cells[props.currentModuleIndex]
  if (!cell) return ''
  const raw = (cell.title && String(cell.title).trim()) || getCellTypeLabel(cell.type) || `模块 ${props.currentModuleIndex + 1}`
  return raw.length > 36 ? `${raw.slice(0, 34)}…` : raw
})

const navCenterTitleFull = computed(() => {
  if (props.currentModuleIndex < 0 || !props.cells.length) return '当前未向学生播出内容'
  const cell = props.cells[props.currentModuleIndex]
  if (!cell) return ''
  return (cell.title && String(cell.title).trim()) || getCellTypeLabel(cell.type) || `模块 ${props.currentModuleIndex + 1}`
})

// 方法
function setModuleItemRef(el: any, index: number) {
  if (el) {
    const element = (el as any).$el || el
    if (element instanceof HTMLElement) {
      moduleItemRefs.value.set(index, element)
    }
  } else {
    moduleItemRefs.value.delete(index)
  }
}

function isModuleActive(cell: Cell, index: number): boolean {
  // 多选模式：使用 displayCellOrders
  if (props.displayCellOrders && props.displayCellOrders.length > 0) {
    const cellOrder = cell.order !== undefined ? cell.order : index
    return props.displayCellOrders.includes(cellOrder)
  }

  // 单选模式：使用 currentModuleIndex
  return props.currentModuleIndex === index
}

function isModuleActivityActive(cell: Cell, index: number): boolean {
  const t = cell.type as string
  if (t !== CellType.ACTIVITY && t.toLowerCase() !== 'activity') return false
  if (!props.sessionCurrentActivityId) return false

  const cellId = cell.id
  if (typeof cellId === 'number' && cellId === props.sessionCurrentActivityId) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === props.sessionCurrentActivityId) return true
  }
  return false
}

function getCellTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text: '文本',
    code: '代码',
    activity: '活动',
    video: '视频',
    flowchart: '流程图',
    qa: '问答',
  }
  return labels[type] || type
}

function getModuleTooltip(cell: Cell, index: number): string {
  const typeLabel = getCellTypeLabel(cell.type)
  const title = cell.title || `模块 ${index + 1}`
  const isActiveCell = isModuleActive(cell, index)
  const status = isActiveCell ? ' (已选中)' : ''
  return `${index + 1}. ${title} - ${typeLabel}${status}`
}

function handleItemClick(cell: Cell, index: number) {
  emit('item-click', cell, index)
}

function handleCheckboxClick(cell: Cell, index: number, event: Event) {
  emit('checkbox-click', cell, index, event)
}

function handleCheckboxChange(cell: Cell, index: number, event: Event) {
  emit('checkbox-change', cell, index, event)
}

function handlePrevModule() {
  emit('prev-module')
}

function handleNextModule() {
  emit('next-module')
}

function handleModuleItemClick(cell: Cell, index: number) {
  handleItemClick(cell, index)
}

function handleModuleCheckboxClick(cell: Cell, index: number, event: Event) {
  handleCheckboxClick(cell, index, event)
}

function handleModuleCheckboxChange(cell: Cell, index: number, event: Event) {
  handleCheckboxChange(cell, index, event)
}
</script>

<style scoped>
.module-list-container {
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: auto;
  max-height: none;
  overflow: visible;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  flex: 1 1 100%;
  min-width: 0;
}

/* 导航控制栏 */
.module-navigation-bar {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.module-nav-current {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 0.5rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.module-nav-current-index {
  font-size: 0.75rem;
  font-weight: 600;
  color: #4b5563;
  line-height: 1.2;
}

.module-nav-current-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #111827;
  line-height: 1.25;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.module-nav-current-muted {
  font-size: 0.8125rem;
  color: #6b7280;
  text-align: center;
}

.module-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
  color: #1d4ed8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 0 0 auto;
  min-width: 7rem;
}

.module-nav-btn:hover:not(:disabled) {
  background: #dbeafe;
  border-color: #93c5fd;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.module-nav-btn:active:not(:disabled) {
  transform: translateY(0);
}

.module-nav-btn:disabled,
.module-nav-btn.module-nav-btn-disabled {
  background: #f3f4f6;
  border-color: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.module-nav-btn:disabled:hover,
.module-nav-btn.module-nav-btn-disabled:hover {
  transform: none;
  box-shadow: none;
}

.module-nav-btn svg {
  flex-shrink: 0;
}

/* 模块列表 */
.module-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding-bottom: 12px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  max-height: calc(76px * 2 + 12px);
  overflow-y: auto;
  overflow-x: hidden;
}

.module-list::-webkit-scrollbar {
  width: 6px;
}

.module-list::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb {
  background: #9ca3af;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

.module-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  padding-right: 36px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 52px;
  height: auto;
  width: 100%;
  min-width: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.module-item:hover:not(.module-item-disabled) {
  border-color: #d1d5db;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.module-item-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 不同类型模块的颜色主题 */
.module-item-type-video {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.module-item-type-video:hover:not(.module-item-disabled) {
  border-color: #93c5fd;
  background: #dbeafe;
}

.module-item-type-text {
  border-color: #fcd34d;
  background: #fffbeb;
  border-width: 2px;
}

.module-item-type-text:hover:not(.module-item-disabled) {
  border-color: #fbbf24;
  background: #fef3c7;
}

.module-item-type-browser {
  border-color: #a5f3fc;
  background: #cffafe;
  border-width: 2px;
}

.module-item-type-browser:hover:not(.module-item-disabled) {
  border-color: #67e8f9;
  background: #a5f3fc;
}

.module-item-type-activity {
  border-color: #e9d5ff;
  background: #faf5ff;
}

.module-item-type-activity:hover:not(.module-item-disabled) {
  border-color: #d8b4fe;
  background: #f3e8ff;
}

.module-item-type-code {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.module-item-type-code:hover:not(.module-item-disabled) {
  border-color: #86efac;
  background: #dcfce7;
}

.module-item-type-flowchart {
  border-color: #c7d2fe;
  background: #eef2ff;
}

.module-item-type-flowchart:hover:not(.module-item-disabled) {
  border-color: #a5b4fc;
  background: #e0e7ff;
}

.module-item-type-qa {
  border-color: #fde047;
  background: #fefce8;
}

.module-item-type-qa:hover:not(.module-item-disabled) {
  border-color: #facc15;
  background: #fef9c3;
}

/* 激活状态 */
.module-item-active {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px) scale(1.02);
  z-index: 10;
}

.module-item-type-video.module-item-active {
  background: #3b82f6;
  border-color: #2563eb;
}

.module-item-type-text.module-item-active {
  background: #f59e0b;
  border-color: #d97706;
}

.module-item-type-browser.module-item-active {
  background: #06b6d4;
  border-color: #0891b2;
}

.module-item-type-activity.module-item-active {
  background: #a855f7;
  border-color: #9333ea;
}

.module-item-type-code.module-item-active {
  background: #22c55e;
  border-color: #16a34a;
}

.module-item-type-flowchart.module-item-active {
  background: #6366f1;
  border-color: #4f46e5;
}

.module-item-type-qa.module-item-active {
  background: #eab308;
  border-color: #ca8a04;
}

/* 激活状态下的 hover 效果 */
.module-item-type-video.module-item-active:hover:not(.module-item-disabled) {
  background: #2563eb;
  border-color: #1d4ed8;
}

.module-item-type-text.module-item-active:hover:not(.module-item-disabled) {
  background: #d97706;
  border-color: #b45309;
}

.module-item-type-browser.module-item-active:hover:not(.module-item-disabled) {
  background: #0891b2;
  border-color: #0e7490;
}

.module-item-type-activity.module-item-active:hover:not(.module-item-disabled) {
  background: #9333ea;
  border-color: #7e22ce;
}

.module-item-type-code.module-item-active:hover:not(.module-item-disabled) {
  background: #16a34a;
  border-color: #15803d;
}

.module-item-type-flowchart.module-item-active:hover:not(.module-item-disabled) {
  background: #4f46e5;
  border-color: #4338ca;
}

.module-item-type-qa.module-item-active:hover:not(.module-item-disabled) {
  background: #ca8a04;
  border-color: #a16207;
}

/* 单选框/复选框样式 */
.module-item-checkbox {
  position: absolute;
  bottom: 6px;
  right: 6px;
  z-index: 10;
  background: white;
  border-radius: 0.25rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  padding: 2px;
  transition: all 0.3s ease;
  min-width: 24px;
  min-height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}

.module-item-checkbox:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  background: #f9fafb;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  border: 2px solid #9ca3af;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

input[type="radio"].checkbox-input {
  border-radius: 9999px;
}

input[type="checkbox"].checkbox-input {
  border-radius: 0.25rem;
}

.module-item-type-video .checkbox-input:checked {
  accent-color: #3b82f6;
}

.module-item-type-activity .checkbox-input:checked {
  accent-color: #a855f7;
}

.module-item-type-code .checkbox-input:checked {
  accent-color: #22c55e;
}

.module-item-type-flowchart .checkbox-input:checked {
  accent-color: #6366f1;
}

.module-item-type-qa .checkbox-input:checked {
  accent-color: #eab308;
}

.module-item-type-text .checkbox-input:checked {
  accent-color: #f59e0b;
}

.module-item-type-browser .checkbox-input:checked {
  accent-color: #06b6d4;
}

.checkbox-input:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* 模块序号 */
.module-item-number {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 24px;
  height: 24px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  background: white;
  border: 2px solid #d1d5db;
  color: #374151;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  z-index: 2;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.module-item-type-video .module-item-number {
  border-color: #60a5fa;
  color: #2563eb;
}

.module-item-type-activity .module-item-number {
  border-color: #c084fc;
  color: #9333ea;
}

.module-item-type-code .module-item-number {
  border-color: #4ade80;
  color: #16a34a;
}

.module-item-type-flowchart .module-item-number {
  border-color: #818cf8;
  color: #4f46e5;
}

.module-item-type-qa .module-item-number {
  border-color: #facc15;
  color: #ca8a04;
}

.module-item-type-text .module-item-number {
  border-color: #fbbf24;
  color: #d97706;
}

.module-item-type-browser .module-item-number {
  border-color: #22d3ee;
  color: #0891b2;
}

.module-item-active .module-item-number {
  background: white;
  transform: scale(1.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 模块图标 */
.module-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border: 2px solid;
  border-radius: 0.25rem;
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.module-item-icon.icon-text {
  border-color: #fcd34d;
}

.module-item-icon.icon-code {
  border-color: #86efac;
}

.module-item-icon.icon-activity {
  border-color: #d8b4fe;
}

.module-item-icon.icon-video {
  border-color: #93c5fd;
}

.module-item-icon.icon-flowchart {
  border-color: #a5b4fc;
}

.module-item-icon.icon-qa {
  border-color: #fde047;
}

.module-item-icon.icon-browser {
  border-color: #67e8f9;
}

.module-item-icon.icon-interactive {
  border-color: #c084fc;
}

.module-item-icon.icon-reference_material {
  border-color: #cbd5e1;
}

.module-item-active .module-item-icon {
  background: white;
  transform: scale(1.1);
  border-color: transparent;
}

.icon-text {
  color: #b45309;
}

.icon-browser {
  color: #0891b2;
}

.icon-video {
  color: #1d4ed8;
}

.icon-activity {
  color: #7e22ce;
}

.icon-code {
  color: #15803d;
}

.icon-flowchart {
  color: #4338ca;
}

.icon-qa {
  color: #a16207;
}

.icon-interactive {
  color: #7e22ce;
}

.icon-reference_material {
  color: #475569;
}

.module-item-active .module-item-icon {
  color: white;
}

/* 模块内容 */
.module-item-content {
  flex: 1;
  min-width: 0;
  padding-right: 4px;
  overflow: hidden;
}

.module-item-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.3s ease;
  max-width: 100%;
  line-height: 1.3;
}

.module-item-subtitle {
  display: none;
  font-size: 11px;
  color: #6b7280;
  transition: all 0.3s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  line-height: 1.2;
}

.module-item-active .module-item-title,
.module-item-active .module-item-subtitle {
  color: white;
  font-weight: 600;
}

/* 活动标记 */
.module-item-activity-badge {
  position: absolute;
  bottom: 6px;
  right: 6px;
  padding: 2px 6px;
  background: #a855f7;
  color: white;
  border-radius: 9999px;
  font-size: 9px;
  font-weight: 600;
  white-space: nowrap;
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

/* 空状态 */
.module-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .module-navigation-bar {
    gap: 10px;
    margin-bottom: 10px;
    padding-bottom: 10px;
  }

  .module-nav-btn {
    padding: 6px 12px;
    font-size: 12px;
    gap: 4px;
  }

  .module-nav-btn svg {
    width: 14px;
    height: 14px;
  }

  .module-list {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
    max-height: calc(100px * 2 + 10px);
  }

  .module-item {
    padding: 6px 8px;
    padding-right: 32px;
    min-height: 48px;
    gap: 5px;
  }

  .module-item-icon {
    width: 24px;
    height: 24px;
  }

  .module-item-title {
    font-size: 12px;
  }
}
</style>
