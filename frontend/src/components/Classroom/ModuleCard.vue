<template>
  <div
    class="module-card"
    :class="cardClasses"
    :title="tooltip"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Checkbox for multi-select mode -->
    <div class="module-card-checkbox" @click.stop="handleCheckboxClick">
      <input
        :type="isMultiSelectMode ? 'checkbox' : 'radio'"
        :name="isMultiSelectMode ? `module-card-checkbox-${index}` : 'module-card-radio'"
        :checked="isActive"
        :disabled="loading"
        @change="handleCheckboxChange"
        @click.stop
        class="checkbox-input"
      />
    </div>

    <!-- Module number badge -->
    <div class="module-card-number">{{ index + 1 }}</div>

    <!-- Top metadata bar -->
    <div v-if="showLearningMeta" class="card-metadata">
      <DifficultyBadge :level="cell.difficulty" />
      <DurationBadge :minutes="cell.duration" />
    </div>

    <!-- Core content area -->
    <div class="card-content">
      <div class="card-icon" :class="`icon-${cell.type}`">
        <CellTypeIcon :type="cell.type" />
      </div>
      <div class="card-info">
        <h3 class="card-title">{{ cell.title || `模块 ${index + 1}` }}</h3>
        <p v-if="cell.preview" class="card-description">{{ cell.preview }}</p>
      </div>
    </div>

    <!-- Bottom status bar -->
    <div v-if="showLearningMeta" class="card-status">
      <ProgressRing
        :percentage="cell.progress || 0"
        :size="40"
        :color="typeColor"
      />
      <span class="status-text">{{ statusText }}</span>
    </div>

    <!-- Hover action buttons -->
    <div class="card-actions" v-show="showActions">
      <button
        class="action-btn action-btn-preview"
        @click.stop="handlePreview"
        :title="`预览 ${cell.title}`"
      >
        👁️
      </button>
      <button
        class="action-btn action-btn-edit"
        @click.stop="handleEdit"
        :title="`编辑 ${cell.title}`"
      >
        ✏️
      </button>
    </div>

    <!-- Activity badge for active modules -->
    <div v-if="cell.type === 'ACTIVITY' && isActivityActive" class="activity-badge">
      🎯
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Cell } from '../../types/cell'
import CellTypeIcon from './CellTypeIcon.vue'
import DifficultyBadge from './DifficultyBadge.vue'
import DurationBadge from './DurationBadge.vue'
import ProgressRing from './ProgressRing.vue'

interface Props {
  cell: Cell
  index: number
  isActive: boolean
  loading?: boolean
  isMultiSelectMode?: boolean
  isActivityActive?: boolean
  showLearningMeta?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  isMultiSelectMode: false,
  isActivityActive: false,
  showLearningMeta: true,
})

const emit = defineEmits<{
  'click': [cell: Cell, index: number]
  'checkbox-click': [cell: Cell, index: number, event: Event]
  'checkbox-change': [cell: Cell, index: number, event: Event]
  'preview': [cell: Cell, index: number]
  'edit': [cell: Cell, index: number]
}>()

const showActions = ref(false)

const cardClasses = computed(() => ({
  'module-card-active': props.isActive,
  'module-card-loading': props.loading,
  'module-card-disabled': props.loading,
  'module-card-compact': !props.showLearningMeta,
  [`module-card-type-${props.cell.type}`]: true
}))

const tooltip = computed(() => {
  const typeLabel = getTypeLabel(props.cell.type)
  const title = props.cell.title || `模块 ${props.index + 1}`
  const status = props.isActive ? ' (已选中)' : ''
  return `${props.index + 1}. ${title} - ${typeLabel}${status}`
})

const typeColor = computed(() => {
  const colors: Record<string, string> = {
    TEXT: '#F59E0B',
    VIDEO: '#3B82F6',
    CODE: '#10B981',
    ACTIVITY: '#A855F7',
    FLOWCHART: '#6366F1',
    CHART: '#6366F1',
    BROWSER: '#06B6D4',
    INTERACTIVE: '#A855F7',
    REFERENCE_MATERIAL: '#6B7280'
  }
  return colors[props.cell.type] || '#6B7280'
})

const statusText = computed(() => {
  const progress = props.cell.progress || 0
  if (progress === 100) return '已完成'
  if (progress > 0) return `进行中 ${progress}%`
  return '待开始'
})

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    TEXT: '文本',
    CODE: '代码',
    ACTIVITY: '活动',
    VIDEO: '视频',
    FLOWCHART: '流程图',
    CHART: '图表',
    QA: '问答',
    BROWSER: '浏览器',
    INTERACTIVE: '交互',
    REFERENCE_MATERIAL: '参考资料'
  }
  return labels[type] || type
}

function handleClick() {
  if (!props.loading) {
    emit('click', props.cell, props.index)
  }
}

function handleCheckboxClick(event: Event) {
  if (!props.loading) {
    emit('checkbox-click', props.cell, props.index, event)
  }
}

function handleCheckboxChange(event: Event) {
  if (!props.loading) {
    emit('checkbox-change', props.cell, props.index, event)
  }
}

function handleMouseEnter() {
  if (!props.loading) {
    showActions.value = true
  }
}

function handleMouseLeave() {
  showActions.value = false
}

function handlePreview() {
  emit('preview', props.cell, props.index)
}

function handleEdit() {
  emit('edit', props.cell, props.index)
}
</script>

<style scoped>
.module-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: white;
  border: 2px solid #E5E7EB;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease-out;
  min-height: 110px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 授课导播台紧凑模式（隐藏元信息时） */
.module-card-compact {
  min-height: 72px;
  padding: 8px 10px;
  gap: 6px;
}

.module-card:hover:not(.module-card-disabled) {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #D1D5DB;
}

.module-card-type-VIDEO:hover:not(.module-card-disabled) {
  border-color: #93C5FD;
}

.module-card-type-TEXT:hover:not(.module-card-disabled) {
  border-color: #FBBF24;
}

.module-card-type-ACTIVITY:hover:not(.module-card-disabled) {
  border-color: #D8B4FE;
}

.module-card-type-CODE:hover:not(.module-card-disabled) {
  border-color: #86EFAC;
}

.module-card-active {
  background: #3B82F6;
  border-color: #2563EB;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.module-card-type-TEXT.module-card-active {
  background: #F59E0B;
  border-color: #D97706;
}

.module-card-type-VIDEO.module-card-active {
  background: #3B82F6;
  border-color: #2563EB;
}

.module-card-type-ACTIVITY.module-card-active {
  background: #A855F7;
  border-color: #9333EA;
}

.module-card-type-CODE.module-card-active {
  background: #10B981;
  border-color: #059669;
}

.module-card-type-FLOWCHART.module-card-active {
  background: #6366F1;
  border-color: #4F46E5;
}

.module-card-type-CHART.module-card-active {
  background: #6366F1;
  border-color: #4F46E5;
}

.module-card-type-BROWSER.module-card-active {
  background: #06B6D4;
  border-color: #0891B2;
}

.module-card-type-INTERACTIVE.module-card-active {
  background: #A855F7;
  border-color: #9333EA;
}

.module-card-loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.module-card-disabled {
  cursor: not-allowed;
}

.module-card-checkbox {
  position: absolute;
  bottom: 8px;
  right: 8px;
  z-index: 10;
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  padding: 2px;
  transition: all 0.3s ease;
  min-width: 20px;
  min-height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}

.module-card-compact .module-card-checkbox {
  bottom: 6px;
  right: 6px;
}

.module-card-checkbox:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: #F9FAFB;
}

.checkbox-input {
  width: 14px;
  height: 14px;
  cursor: pointer;
  border: 2px solid #9CA3AF;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

input[type="radio"].checkbox-input {
  border-radius: 9999px;
}

input[type="checkbox"].checkbox-input {
  border-radius: 4px;
}

.module-card-number {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  background: white;
  border: 2px solid #D1D5DB;
  color: #374151;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 2;
  transition: all 0.3s ease;
}

.module-card-type-VIDEO .module-card-number {
  border-color: #60A5FA;
  color: #2563EB;
}

.module-card-type-ACTIVITY .module-card-number {
  border-color: #C084FC;
  color: #9333EA;
}

.module-card-type-CODE .module-card-number {
  border-color: #4ADE80;
  color: #16A34A;
}

.module-card-type-FLOWCHART .module-card-number {
  border-color: #818CF8;
  color: #4F46E5;
}

.module-card-type-CHART .module-card-number {
  border-color: #818CF8;
  color: #4F46E5;
}

.module-card-type-TEXT .module-card-number {
  border-color: #FBBF24;
  color: #D97706;
}

.module-card-type-BROWSER .module-card-number {
  border-color: #22D3EE;
  color: #0891B2;
}

.module-card-type-INTERACTIVE .module-card-number {
  border-color: #C084FC;
  color: #9333EA;
}

.module-card-active .module-card-number {
  background: white;
  transform: scale(1.1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.card-metadata {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  margin-bottom: 4px;
}

.card-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
  min-height: 0;
}

.module-card-compact .card-content {
  align-items: center;
  gap: 6px;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border: 2px solid;
  border-radius: 6px;
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.module-card-compact .card-icon {
  width: 26px;
  height: 26px;
}

.card-icon.icon-TEXT {
  border-color: #FCD34D;
  color: #B45309;
}

.card-icon.icon-CODE {
  border-color: #86EFAC;
  color: #15803D;
}

.card-icon.icon-ACTIVITY {
  border-color: #D8B4FE;
  color: #7E22CE;
}

.card-icon.icon-VIDEO {
  border-color: #93C5FD;
  color: #1D4ED8;
}

.card-icon.icon-FLOWCHART {
  border-color: #A5B4FC;
  color: #4338CA;
}

.card-icon.icon-CHART {
  border-color: #A5B4FC;
  color: #4338CA;
}

.card-icon.icon-BROWSER {
  border-color: #67E8F9;
  color: #0891B2;
}

.card-icon.icon-INTERACTIVE {
  border-color: #C084FC;
  color: #7E22CE;
}

.card-icon.icon-REFERENCE_MATERIAL {
  border-color: #CBD5E1;
  color: #475569;
}

.module-card-active .card-icon {
  background: white;
  transform: scale(1.1);
  border-color: transparent;
}

.card-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 2px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
  transition: color 0.3s ease;
}

.module-card-compact .card-title {
  font-size: 12px;
  margin: 0;
  line-height: 1.25;
}

.card-description {
  font-size: 11px;
  font-weight: 500;
  color: #6B7280;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.module-card-compact .card-description {
  display: none;
}

.module-card-active .card-title,
.module-card-active .card-description {
  color: white;
}

.card-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  margin-top: auto;
}

.module-card-active .card-status {
  background: rgba(255, 255, 255, 0.2);
}

.status-text {
  font-size: 11px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.module-card-active .status-text {
  color: white;
}

.card-actions {
  position: absolute;
  bottom: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s ease 0.1s;
}

.module-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn-preview {
  background: white;
  border: 1px solid #D1D5DB;
}

.action-btn-preview:hover {
  background: #F3F4F6;
  transform: scale(1.1);
}

.action-btn-edit {
  background: #3B82F6;
  color: white;
}

.action-btn-edit:hover {
  background: #2563EB;
  transform: scale(1.1);
}

.activity-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 3px 6px;
  background: #A855F7;
  color: white;
  border-radius: 9999px;
  font-size: 9px;
  font-weight: 600;
  white-space: nowrap;
  animation: pulse-badge 2s infinite;
  z-index: 5;
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

/* Responsive design */
@media (max-width: 768px) {
  .module-card {
    padding: 10px;
    min-height: 100px;
  }

  .card-title {
    font-size: 13px;
  }

  .card-description {
    font-size: 10px;
  }

  .card-actions {
    opacity: 1;
    right: 6px;
    bottom: 6px;
  }

  .module-card-number {
    width: 24px;
    height: 24px;
    font-size: 10px;
  }
}
</style>
