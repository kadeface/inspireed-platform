<template>
  <div class="classroom-control-board">
    <div class="board-header">
      <h4 class="board-title">📺 导播台</h4>
      <div class="board-stats">
        <span class="stat-item">
          共 {{ cells.length }} 个模块
        </span>
        <span v-if="currentCellIndex >= 0" class="stat-item">
          当前: {{ currentCellIndex + 1 }}/{{ cells.length }}
        </span>
      </div>
    </div>

    <!-- 导播链条 -->
    <div class="control-chain-wrapper">
      <div class="control-chain" :class="{ 'chain-horizontal': layout === 'horizontal', 'chain-vertical': layout === 'vertical' }">
      <!-- 隐藏所有内容节点 -->
      <div 
        class="chain-node node-hidden"
        :class="{ 'node-active': !currentCellId }"
        @click="handleHideAll"
        :title="'隐藏所有内容'"
      >
        <div class="node-icon">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
        </div>
        <div class="node-label">隐藏</div>
        <div v-if="!currentCellId" class="node-indicator"></div>
      </div>

      <!-- 连接线 -->
      <div class="chain-connector"></div>

      <!-- 模块节点 -->
      <template v-for="(cell, index) in cells" :key="cell.id || index">
        <div 
          class="chain-node"
          :class="{
            'node-active': isActive(cell, index),
            [`node-type-${cell.type}`]: true,
            'node-completed': isCompleted(cell, index),
            'node-disabled': loading,
          }"
          :title="loading ? '切换中，请稍候...' : getNodeTooltip(cell, index)"
        >
          <!-- 复选框 -->
          <div class="node-checkbox" @click.stop="!loading && handleCheckboxClick(cell, index, $event)">
            <input 
              type="checkbox" 
              :checked="isActive(cell, index)"
              :disabled="loading"
              @change.stop="!loading && handleCheckboxChange(cell, index, $event)"
              @click.stop
              class="checkbox-input"
            />
          </div>
          
          <!-- 节点序号 -->
          <div class="node-number">{{ index + 1 }}</div>
          
          <!-- 模块类型标签 -->
          <div class="node-type-badge" :class="`badge-${cell.type}`">
            {{ getCellTypeEmoji(cell.type) }}
          </div>
          
          <!-- 节点图标 -->
          <div class="node-icon" :class="`icon-${cell.type}`" @click="!loading && handleNodeClick(cell, index)">
            <CellTypeIcon :type="cell.type" />
          </div>
          
          <!-- 节点标题 -->
          <div class="node-label" @click="!loading && handleNodeClick(cell, index)">
            <div class="node-title">{{ cell.title || getCellTypeLabel(cell.type) || `模块 ${index + 1}` }}</div>
            <div class="node-subtitle">{{ getCellTypeLabel(cell.type) }}</div>
          </div>
          
          <!-- 活动状态标记 -->
          <div v-if="cell.type === 'activity' && isActivityActive(cell, index)" class="node-activity-badge">
            🎯 进行中
          </div>
        </div>

        <!-- 连接线（最后一个节点后不显示） -->
        <div v-if="index < cells.length - 1" class="chain-connector"></div>
      </template>
      </div>
    </div>

    <!-- 当前模块详情 -->
    <div v-if="currentCell" class="current-module-detail">
      <div class="detail-header">
        <span class="detail-type-badge">{{ getCellTypeLabel(currentCell.type) }}</span>
        <span class="detail-title">{{ currentCell.title || currentCell.type }}</span>
      </div>
      <div class="detail-actions">
        <button 
          v-if="currentCell.type === 'activity' && !isActivityActive(currentCell, currentCellIndex)"
          @click="handleStartActivity"
          :disabled="loading"
          class="btn btn-sm btn-primary"
        >
          🎯 开始活动
        </button>
        <button 
          v-else-if="currentCell.type === 'activity' && isActivityActive(currentCell, currentCellIndex)"
          @click="handleEndActivity"
          :disabled="loading"
          class="btn btn-sm btn-secondary"
        >
          ✅ 结束活动
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import type { Cell } from '@/types/cell'
import { getCellId as getCellIdUtil, isUUID, toNumericId } from '../../utils/cellId'

// Cell类型图标组件
const CellTypeIcon = (props: { type: string }) => {
  const icons: Record<string, any> = {
    text: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 6h16M4 12h16M4 18h16' })
    ]),
    code: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' })
    ]),
    activity: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' })
    ]),
    video: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ]),
    flowchart: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' })
    ]),
    qa: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
    ]),
  }
  
  const IconComponent = icons[props.type] || icons.text
  return IconComponent()
}

interface Props {
  cells: Cell[]
  currentCellId?: number | null
  currentCellIndex?: number | null  // 当前选中的 Cell 索引（-1 表示隐藏）
  currentActivityId?: number | null
  completedCellIds?: number[]
  displayCellIds?: number[]  // 多选模式下要显示的 Cell IDs（数据库 ID）
  dbCells?: Array<{ id: number; order: number; cell_type: string }>  // 数据库中的 Cell 记录（用于 ID 匹配）
  loading?: boolean
  layout?: 'horizontal' | 'vertical'
}

const props = withDefaults(defineProps<Props>(), {
  currentCellId: null,
  currentCellIndex: null,
  currentActivityId: null,
  completedCellIds: () => [],
  displayCellIds: () => [],
  dbCells: () => [],
  loading: false,
  layout: 'horizontal',
})

const emit = defineEmits<{
  navigateToCell: [cellId: number | string | null, cellOrder: number | null, action?: 'toggle' | 'add' | 'remove', multiSelect?: boolean]
  startActivity: [cellId: number]
  endActivity: []
}>()

// 计算属性
const currentCellIndex = computed(() => {
  if (!props.currentCellId) return -1
  
  return props.cells.findIndex((cell, index) => {
    const cellId = getCellId(cell)
    if (typeof cellId === 'number' && cellId === props.currentCellId) return true
    if (typeof cellId === 'string') {
      const numId = parseInt(cellId)
      if (!isNaN(numId) && numId === props.currentCellId) return true
    }
    return false
  })
})

const currentCell = computed(() => {
  if (currentCellIndex.value >= 0 && currentCellIndex.value < props.cells.length) {
    return props.cells[currentCellIndex.value]
  }
  return null
})

// 方法
// 使用工具函数获取 Cell ID（保留此函数名以兼容现有代码）
function getCellId(cell: Cell): number | string | null {
  return getCellIdUtil(cell)
}

function isActive(cell: Cell, index: number): boolean {
  // 多选模式：检查 displayCellIds
  if (props.displayCellIds && props.displayCellIds.length > 0) {
    const cellId = getCellId(cell)
    const numericId = toNumericId(cellId)
    
    // 1. 直接匹配数字 ID（如果 cell.id 是数字）
    if (numericId && props.displayCellIds.includes(numericId)) {
      return true
    }
    
    // 2. 通过 order 匹配：如果 cell.id 是 UUID，需要通过 order 查找对应的数据库 ID
    const cellOrder = cell.order !== undefined ? cell.order : index
    
    // 建立数据库 ID 到 order 的映射
    if (props.dbCells && props.dbCells.length > 0) {
      // 查找当前 Cell 的 order 对应的数据库 Cell ID
      const dbCell = props.dbCells.find(c => c.order === cellOrder)
      if (dbCell && dbCell.id && props.displayCellIds.includes(dbCell.id)) {
        return true
      }
      
      // 反向查找：如果 displayCellIds 中的某个数据库 ID 对应的 order 等于当前 Cell 的 order
      const idToOrderMap = new Map<number, number>()
      props.dbCells.forEach(dbCell => {
        if (dbCell.id && dbCell.order !== undefined) {
          idToOrderMap.set(dbCell.id, dbCell.order)
        }
      })
      
      // 检查是否有任何 displayCellIds 对应的 order 匹配当前 Cell 的 order
      for (const dbId of props.displayCellIds) {
        const mappedOrder = idToOrderMap.get(dbId)
        if (mappedOrder !== undefined && mappedOrder === cellOrder) {
          return true
        }
      }
    }
  }
  
  // 单选模式：优先使用索引匹配（最可靠，因为前端总是知道索引）
  if (props.currentCellIndex !== null && props.currentCellIndex !== undefined) {
    // -1 表示隐藏所有内容
    if (props.currentCellIndex === -1) return false
    // 索引匹配
    if (index === props.currentCellIndex) return true
  }
  
  // 如果没有索引，使用 cellId 匹配
  if (props.currentCellId) {
    const cellId = getCellId(cell)
    
    // 1. 直接匹配数字 ID
    if (typeof cellId === 'number' && cellId === props.currentCellId) return true
    
    // 2. 字符串 ID 转换为数字后匹配
    if (typeof cellId === 'string') {
      const numId = toNumericId(cellId)
      if (numId === props.currentCellId) return true
    }
    
    // 3. 通过 order 匹配（如果 cellId 是顺序索引）
    if (cell.order !== undefined) {
      if (cell.order === props.currentCellId || cell.order === Number(props.currentCellId)) {
        return true
      }
    }
    
    // 4. 通过索引匹配（如果 cellId 是顺序索引）
    if (index === props.currentCellId || index === Number(props.currentCellId)) {
      return true
    }
  }
  
  return false
}

function isCompleted(cell: Cell, index: number): boolean {
  const cellId = getCellId(cell)
  if (typeof cellId === 'number') {
    return props.completedCellIds.includes(cellId)
  }
  return false
}

function isActivityActive(cell: Cell, index: number): boolean {
  if (cell.type !== 'activity') return false
  if (!props.currentActivityId) return false
  
  const cellId = getCellId(cell)
  if (typeof cellId === 'number' && cellId === props.currentActivityId) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === props.currentActivityId) return true
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

function getCellTypeEmoji(type: string): string {
  const emojis: Record<string, string> = {
    text: '📄',
    code: '💻',
    activity: '📝',
    video: '📹',
    flowchart: '📊',
    qa: '❓',
  }
  return emojis[type] || '📦'
}


function getNodeTooltip(cell: Cell, index: number): string {
  const typeLabel = getCellTypeLabel(cell.type)
  const title = cell.title || `模块 ${index + 1}`
  const isActiveCell = isActive(cell, index)
  const status = isActiveCell ? ' (已选中)' : ''
  return `${index + 1}. ${title} - ${typeLabel}${status}`
}

// 事件处理
// 点击复选框
function handleCheckboxChange(cell: Cell, index: number, event: Event) {
  console.log('🔘 复选框 change 事件触发:', { index, cellId: cell.id, loading: props.loading })
  
  if (props.loading) {
    console.warn('⏸️ 切换中，请稍候...')
    return
  }
  
  const target = event.target as HTMLInputElement
  const isChecked = target.checked
  const isCurrentlyActive = isActive(cell, index)
  
  console.log('🔍 复选框状态检查:', {
    isChecked,
    isCurrentlyActive,
    displayCellIds: props.displayCellIds,
    displayCellIdsLength: props.displayCellIds?.length || 0,
  })
  
  // 如果状态没有变化，不需要操作
  if (isChecked === isCurrentlyActive) {
    console.log('⏭️ 状态未变化，跳过操作')
    return
  }
  
  // 确定操作类型：如果勾选则添加，否则移除
  const action: 'add' | 'remove' = isChecked ? 'add' : 'remove'
  
  console.log('☑️ 复选框状态变化:', {
    index,
    cellId: cell.id,
    isChecked,
    action,
    cellType: cell.type,
    cellOrder: cell.order,
  })
  
  const cellId = getCellId(cell)
  const cellOrder = cell.order !== undefined ? cell.order : index
  
  console.log('📤 准备发送导航事件:', {
    cellId,
    cellOrder,
    action,
    multiSelect: true,
    cellIdType: typeof cellId,
    isUUID: cellId && typeof cellId === 'string' ? isUUID(cellId) : false,
  })
  
  // 发送导航事件（多选模式）
  if (cellId && typeof cellId === 'string' && isUUID(cellId)) {
    console.log('✅ 使用 cellOrder (UUID):', cellOrder)
    emit('navigateToCell', null, cellOrder, action, true)
  } else {
    const numericId = toNumericId(cellId)
    if (numericId) {
      console.log('✅ 使用 numericId:', numericId)
      emit('navigateToCell', numericId, null, action, true)
    } else {
      console.log('✅ 使用 cellOrder (fallback):', cellOrder)
      emit('navigateToCell', null, cellOrder, action, true)
    }
  }
  
  console.log('✅ 导航事件已发送 (emit 调用完成)')
}

// 点击复选框区域（防止事件冒泡）
function handleCheckboxClick(cell: Cell, index: number, event: Event) {
  // 这个方法主要用于阻止事件冒泡，实际的改变由 handleCheckboxChange 处理
  event.stopPropagation()
  console.log('🖱️ 复选框区域被点击:', { index, cellId: cell.id })
}

// 点击节点（非复选框区域）
function handleNodeClick(cell: Cell, index: number) {
  if (props.loading) {
    console.warn('⏸️ 切换中，请稍候...')
    return
  }
  
  const isCurrentlyActive = isActive(cell, index)
  
  // 🆕 对于活动模块，如果已经选中，使用 'add' 保持选中状态（用于显示统计信息）
  // 如果未选中，使用 'add' 选中它
  // 对于其他模块，使用 'toggle' 切换状态
  let action: 'toggle' | 'add' = 'toggle'
  if (cell.type === 'activity') {
    // 活动模块：始终使用 'add'，确保选中状态，以便显示统计信息
    action = 'add'
  } else {
    // 其他模块：使用 'toggle' 切换状态
    action = 'toggle'
  }
  
  console.log('🎯 导播台点击模块:', {
    index,
    cellId: cell.id,
    cellType: cell.type,
    cellTitle: cell.title,
    isCurrentlyActive,
    action,
  })
  
  const cellId = getCellId(cell)
  const cellOrder = cell.order !== undefined ? cell.order : index
  
  console.log('📤 发送导航事件:', { cellId, cellOrder, action, multiSelect: true })
  
  // 使用工具函数判断：如果是 UUID 或无效 ID，使用 cellOrder；否则使用数字 ID
  if (cellId && typeof cellId === 'string' && isUUID(cellId)) {
    // 是 UUID，使用 cellOrder
    emit('navigateToCell', null, cellOrder, action, true)
  } else {
    // 尝试转换为数字 ID
    const numericId = toNumericId(cellId)
    if (numericId) {
      // 有有效的数字 ID，使用 ID
      emit('navigateToCell', numericId, null, action, true)
    } else {
      // 无效 ID，使用 cellOrder
      emit('navigateToCell', null, cellOrder, action, true)
    }
  }
}

function handleHideAll() {
  emit('navigateToCell', 0, null)
}

function handleStartActivity() {
  if (!currentCell.value) return
  const cellId = getCellId(currentCell.value)
  if (typeof cellId === 'number' && cellId > 0) {
    emit('startActivity', cellId)
  }
}

function handleEndActivity() {
  emit('endActivity')
}
</script>

<style scoped>
.classroom-control-board {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.board-header {
  @apply flex items-center justify-between mb-6 pb-4 border-b border-gray-200;
}

.board-title {
  @apply text-lg font-semibold text-gray-900;
}

.board-stats {
  @apply flex items-center gap-4 text-sm text-gray-600;
}

.stat-item {
  @apply px-2 py-1 bg-gray-100 rounded;
}

/* 链条包装器 - 添加渐变阴影提示可滚动 */
.control-chain-wrapper {
  position: relative;
  width: 100%;
}

.control-chain-wrapper::before,
.control-chain-wrapper::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 12px; /* 减去滚动条高度 */
  width: 60px;
  pointer-events: none;
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s;
}

.control-chain-wrapper::before {
  left: 0;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), transparent);
}

.control-chain-wrapper::after {
  right: 0;
  background: linear-gradient(to left, rgba(255, 255, 255, 0.95), transparent);
}

.control-chain-wrapper:hover::before,
.control-chain-wrapper:hover::after {
  opacity: 1;
}

/* 链条容器 */
.control-chain {
  @apply flex items-center;
  overflow-x: auto;
  padding: 1rem 0;
  scroll-behavior: smooth;
  /* 确保滚动条可见 */
  scrollbar-width: thin;
  scrollbar-color: #9ca3af #e5e7eb;
}

/* 自定义滚动条样式（Webkit 浏览器） */
.control-chain::-webkit-scrollbar {
  height: 12px;
}

.control-chain::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 6px;
  margin: 0 1rem;
}

.control-chain::-webkit-scrollbar-thumb {
  background: #9ca3af;
  border-radius: 6px;
  border: 2px solid #f3f4f6;
}

.control-chain::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

.chain-horizontal {
  @apply flex-row;
  flex-wrap: nowrap; /* 防止换行 */
}

.chain-vertical {
  @apply flex-col;
}

/* 连接线 */
.chain-connector {
  @apply flex-shrink-0;
  width: 3rem;
  height: 3px;
  background: linear-gradient(to right, #d1d5db, #9ca3af, #d1d5db);
  margin: 0 0.75rem;
  position: relative;
  border-radius: 2px;
}

.chain-connector::before {
  content: '';
  @apply absolute right-0 top-1/2 transform -translate-y-1/2;
  width: 0;
  height: 0;
  border-left: 6px solid #9ca3af;
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
}

.chain-vertical .chain-connector {
  width: 3px;
  height: 3rem;
  background: linear-gradient(to bottom, #d1d5db, #9ca3af, #d1d5db);
  margin: 0.75rem 0;
}

.chain-vertical .chain-connector::before {
  @apply left-1/2 bottom-0 transform -translate-x-1/2;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 6px solid #9ca3af;
  border-bottom: none;
}

/* 节点 */
.chain-node {
  @apply flex flex-col items-center justify-center relative;
  @apply min-w-[140px] w-[140px] p-4 rounded-xl;
  @apply bg-white border-2 border-gray-200;
  @apply cursor-pointer transition-all duration-300;
  @apply hover:shadow-lg hover:border-gray-300;
  flex-shrink: 0;
  user-select: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chain-node:hover {
  transform: translateY(-2px);
}

.chain-node:active {
  transform: translateY(0) scale(0.98);
}

.chain-node:disabled {
  @apply cursor-not-allowed opacity-50;
}

.node-hidden {
  @apply bg-orange-50 border-orange-200;
}

.node-hidden:hover {
  @apply bg-orange-100 border-orange-300 shadow-lg;
}

/* 不同类型模块的颜色主题 */
.node-type-video {
  @apply border-blue-200 bg-blue-50;
}

.node-type-video:hover {
  @apply border-blue-300 bg-blue-100;
}

.node-type-text {
  @apply border-gray-200 bg-gray-50;
}

.node-type-text:hover {
  @apply border-gray-300 bg-gray-100;
}

.node-type-activity {
  @apply border-purple-200 bg-purple-50;
}

.node-type-activity:hover {
  @apply border-purple-300 bg-purple-100;
}

.node-type-code {
  @apply border-green-200 bg-green-50;
}

.node-type-code:hover {
  @apply border-green-300 bg-green-100;
}

.node-type-flowchart {
  @apply border-indigo-200 bg-indigo-50;
}

.node-type-flowchart:hover {
  @apply border-indigo-300 bg-indigo-100;
}

.node-type-qa {
  @apply border-yellow-200 bg-yellow-50;
}

.node-type-qa:hover {
  @apply border-yellow-300 bg-yellow-100;
}

/* 激活状态 */
.node-active {
  @apply shadow-xl;
  @apply ring-4 ring-offset-2;
  transform: translateY(-4px) scale(1.02);
  z-index: 10;
}

.node-type-video.node-active {
  @apply bg-blue-500 border-blue-600 ring-blue-300;
}

.node-type-text.node-active {
  @apply bg-gray-600 border-gray-700 ring-gray-300;
}

.node-type-activity.node-active {
  @apply bg-purple-500 border-purple-600 ring-purple-300;
}

.node-type-code.node-active {
  @apply bg-green-500 border-green-600 ring-green-300;
}

.node-type-flowchart.node-active {
  @apply bg-indigo-500 border-indigo-600 ring-indigo-300;
}

.node-type-qa.node-active {
  @apply bg-yellow-500 border-yellow-600 ring-yellow-300;
}

.node-active .node-number {
  @apply bg-white scale-110;
}

.node-active .node-title,
.node-active .node-subtitle {
  @apply text-white font-semibold;
}

.node-active .node-icon {
  @apply text-white scale-110;
}

.node-completed {
  @apply opacity-75;
}

.node-completed::after {
  content: '✓';
  @apply absolute top-1 right-1 w-4 h-4 bg-green-500 text-white rounded-full;
  @apply flex items-center justify-center text-xs font-bold;
}

.node-disabled {
  @apply opacity-50 cursor-wait;
  pointer-events: none;
}

.node-disabled:hover {
  @apply bg-gray-50 border-gray-200;
  transform: none;
}

/* 复选框 */
.node-checkbox {
  @apply absolute top-2 right-2 z-10;
  @apply bg-white rounded-md shadow-sm p-0.5;
  transition: all 0.3s ease;
}

.node-checkbox:hover {
  @apply shadow-md scale-110;
}

.checkbox-input {
  @apply w-5 h-5 cursor-pointer;
  @apply border-2 border-gray-300 rounded;
  @apply focus:ring-2 focus:ring-blue-500 focus:ring-offset-1;
  transition: all 0.2s ease;
}

.node-type-video .checkbox-input:checked {
  accent-color: #3b82f6;
}

.node-type-activity .checkbox-input:checked {
  accent-color: #a855f7;
}

.node-type-code .checkbox-input:checked {
  accent-color: #22c55e;
}

.node-type-flowchart .checkbox-input:checked {
  accent-color: #6366f1;
}

.node-type-qa .checkbox-input:checked {
  accent-color: #eab308;
}

.checkbox-input:disabled {
  @apply cursor-not-allowed opacity-50;
}

/* 节点内容 */
.node-number {
  @apply absolute -top-3 -left-3 w-7 h-7 rounded-full;
  @apply flex items-center justify-center text-xs font-bold;
  @apply bg-white border-2 border-gray-300 text-gray-700;
  @apply shadow-md;
  z-index: 2;
  transition: all 0.3s ease;
}

.node-type-video .node-number {
  @apply border-blue-400 text-blue-600;
}

.node-type-activity .node-number {
  @apply border-purple-400 text-purple-600;
}

.node-type-code .node-number {
  @apply border-green-400 text-green-600;
}

.node-type-flowchart .node-number {
  @apply border-indigo-400 text-indigo-600;
}

.node-type-qa .node-number {
  @apply border-yellow-400 text-yellow-600;
}

.node-active .node-number {
  @apply bg-white shadow-lg;
}

/* 类型标签 */
.node-type-badge {
  @apply absolute -top-2 -right-2 w-8 h-8 rounded-full;
  @apply flex items-center justify-center text-lg;
  @apply bg-white border-2 shadow-md;
  z-index: 2;
  transition: all 0.3s ease;
}

.badge-video {
  @apply border-blue-300;
}

.badge-activity {
  @apply border-purple-300;
}

.badge-code {
  @apply border-green-300;
}

.badge-flowchart {
  @apply border-indigo-300;
}

.badge-qa {
  @apply border-yellow-300;
}

.badge-text {
  @apply border-gray-300;
}

.node-active .node-type-badge {
  @apply scale-110;
}

.node-icon {
  @apply w-12 h-12 flex items-center justify-center;
  @apply text-gray-600 mb-2;
  transition: all 0.3s ease;
}

.icon-video {
  @apply text-blue-600;
}

.icon-activity {
  @apply text-purple-600;
}

.icon-code {
  @apply text-green-600;
}

.icon-flowchart {
  @apply text-indigo-600;
}

.icon-qa {
  @apply text-yellow-600;
}

.node-label {
  @apply w-full text-center;
}

.node-title {
  @apply text-sm font-semibold text-gray-800 mb-1;
  @apply line-clamp-2;
  transition: all 0.3s ease;
}

.node-subtitle {
  @apply text-xs text-gray-500;
  transition: all 0.3s ease;
}

/* 活动标记 */
.node-activity-badge {
  @apply absolute -bottom-2 left-1/2 transform -translate-x-1/2;
  @apply px-2 py-0.5 rounded-full text-xs font-medium;
  @apply bg-purple-500 text-white shadow-md;
  white-space: nowrap;
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0%, 100% {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translateX(-50%) scale(1.05);
  }
}

/* 当前模块详情 */
.current-module-detail {
  @apply mt-6 pt-4 border-t border-gray-200;
}

.detail-header {
  @apply flex items-center gap-3 mb-3;
}

.detail-type-badge {
  @apply px-2 py-1 text-xs font-medium rounded;
  @apply bg-blue-100 text-blue-700;
}

.detail-title {
  @apply text-sm font-semibold text-gray-900;
}

.detail-actions {
  @apply flex gap-2;
}

/* 响应式 */
@media (max-width: 1024px) {
  .chain-node {
    @apply min-w-[120px] w-[120px] p-3;
  }
  
  .node-title {
    @apply text-xs;
  }
  
  .node-icon {
    @apply w-10 h-10;
  }
}

@media (max-width: 768px) {
  .control-chain {
    @apply overflow-x-auto pb-4;
    -webkit-overflow-scrolling: touch;
  }
  
  .chain-node {
    @apply min-w-[100px] w-[100px] p-2.5;
  }
  
  .node-title {
    @apply text-[11px];
  }
  
  .node-subtitle {
    @apply text-[9px];
  }
  
  .node-icon {
    @apply w-8 h-8;
  }
  
  .node-number {
    @apply w-6 h-6 text-[10px];
  }
  
  .node-type-badge {
    @apply w-7 h-7 text-base;
  }
  
  .chain-connector {
    width: 2rem;
    margin: 0 0.5rem;
  }
}

@media (max-width: 480px) {
  .chain-node {
    @apply min-w-[85px] w-[85px] p-2;
  }
  
  .node-title {
    @apply text-[10px];
  }
  
  .node-subtitle {
    @apply hidden;
  }
  
  .chain-connector {
    width: 1.5rem;
    margin: 0 0.25rem;
  }
}
</style>

