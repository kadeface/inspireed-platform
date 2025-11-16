<template>
  <div class="classroom-switcher">
    <div class="switcher-header">
      <h4 class="switcher-title">📺 导播台</h4>
      <div class="switcher-status">
        <span v-if="currentCellId" class="status-badge status-active">
          <span class="pulse-dot"></span>
          正在显示
        </span>
        <span v-else class="status-badge status-hidden">
          ⚠️ 已隐藏
        </span>
      </div>
    </div>

    <div class="switcher-content">
      <!-- 模块链条 -->
      <div class="cell-chain" ref="chainContainer">
        <!-- 隐藏按钮 -->
        <div 
          class="chain-node chain-node-hide"
          :class="{ 'active': !currentCellId }"
          @click="handleHideAll"
          :title="'隐藏所有内容'"
        >
          <div class="node-icon">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
          </div>
          <div class="node-label">隐藏</div>
        </div>

        <!-- 连接线 -->
        <div v-if="cells.length > 0" class="chain-connector"></div>

        <!-- 模块节点 -->
        <template v-for="(cell, index) in cells" :key="cell.id || index">
          <!-- 连接线 -->
          <div class="chain-connector" v-if="index > 0 || !currentCellId"></div>
          
          <!-- 节点 -->
          <div
            class="chain-node"
            :class="{
              'active': isActive(cell, index),
              'completed': isCompleted(cell, index),
              [`node-type-${cell.type}`]: true
            }"
            @click="handleNodeClick(cell, index)"
            :title="getNodeTooltip(cell, index)"
          >
            <!-- 节点图标 -->
            <div class="node-icon">
              <span class="text-2xl">{{ getCellIcon(cell.type) }}</span>
            </div>
            
            <!-- 节点内容 -->
            <div class="node-content">
              <div class="node-index">{{ index + 1 }}</div>
              <div class="node-title">{{ getNodeTitle(cell) }}</div>
              <div class="node-type">{{ getCellTypeLabel(cell.type) }}</div>
            </div>

            <!-- 活动状态指示 -->
            <div v-if="isActivityActive(cell, index)" class="node-activity-indicator">
              <span class="activity-pulse"></span>
            </div>

            <!-- 当前指示器 -->
            <div v-if="isActive(cell, index)" class="node-active-indicator">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </template>
      </div>

      <!-- 空状态 -->
      <div v-if="cells.length === 0" class="switcher-empty">
        <p class="text-gray-500 text-sm">暂无模块</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Cell } from '@/types/cell'
import { CellType } from '@/types/cell'

interface Props {
  cells: Cell[]
  currentCellId?: number | null
  currentActivityId?: number | null
  loading?: boolean
}

interface Emits {
  (e: 'switch', cell: Cell, index: number): void
  (e: 'hide'): void
}

const props = withDefaults(defineProps<Props>(), {
  currentCellId: null,
  currentActivityId: null,
  loading: false,
})

const emit = defineEmits<Emits>()

const chainContainer = ref<HTMLElement>()

// 判断节点是否激活
function isActive(cell: Cell, index: number): boolean {
  if (!props.currentCellId) return false
  const cellId = getCellId(cell)
  if (typeof cellId === 'number' && cellId === props.currentCellId) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === props.currentCellId) return true
  }
  return false
}

// 判断活动是否激活
function isActivityActive(cell: Cell, index: number): boolean {
  if (cell.type !== CellType.ACTIVITY) return false
  if (!props.currentActivityId || !props.currentCellId) return false
  return props.currentActivityId === props.currentCellId && isActive(cell, index)
}

// 判断节点是否已完成（未来功能）
function isCompleted(cell: Cell, index: number): boolean {
  // 可以基于学生完成情况来判断
  return false
}

// 获取Cell ID
function getCellId(cell: Cell): number | string | null {
  if (typeof cell.id === 'number') return cell.id
  if (typeof cell.id === 'string') {
    const numId = parseInt(cell.id)
    return isNaN(numId) ? cell.id : numId
  }
  return null
}

// 获取节点标题
function getNodeTitle(cell: Cell): string {
  if (cell.title && cell.title.trim()) {
    return cell.title.length > 12 ? cell.title.substring(0, 12) + '...' : cell.title
  }
  return getCellTypeLabel(cell.type)
}

// 获取节点提示
function getNodeTooltip(cell: Cell, index: number): string {
  const title = cell.title || getCellTypeLabel(cell.type)
  const type = getCellTypeLabel(cell.type)
  const status = isActive(cell, index) ? '（当前显示）' : ''
  return `${index + 1}. ${title} - ${type}${status}`
}

// 获取Cell类型标签
function getCellTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    [CellType.TEXT]: '文本',
    [CellType.CODE]: '代码',
    [CellType.VIDEO]: '视频',
    [CellType.ACTIVITY]: '活动',
    [CellType.FLOWCHART]: '流程图',
    [CellType.SIM]: '仿真',
    [CellType.CHART]: '图表',
    [CellType.CONTEST]: '竞赛',
    [CellType.PARAM]: '参数',
    [CellType.REFERENCE_MATERIAL]: '参考',
  }
  return labels[type] || type
}

// 获取Cell图标（返回emoji字符串）
function getCellIcon(type: string): string {
  const icons: Record<string, string> = {
    [CellType.TEXT]: '📝',
    [CellType.CODE]: '💻',
    [CellType.VIDEO]: '🎥',
    [CellType.ACTIVITY]: '✅',
    [CellType.FLOWCHART]: '📊',
    [CellType.SIM]: '🎮',
    [CellType.CHART]: '📈',
    [CellType.CONTEST]: '🏆',
    [CellType.PARAM]: '⚙️',
    [CellType.REFERENCE_MATERIAL]: '📚',
  }
  return icons[type] || '📄'
}

// 处理节点点击
function handleNodeClick(cell: Cell, index: number) {
  if (props.loading) return
  emit('switch', cell, index)
}

// 处理隐藏所有
function handleHideAll() {
  if (props.loading) return
  emit('hide')
}
</script>

<style scoped>
.classroom-switcher {
  @apply bg-white rounded-lg border border-gray-200 p-4;
}

.switcher-header {
  @apply flex items-center justify-between mb-4;
}

.switcher-title {
  @apply text-lg font-semibold text-gray-800;
}

.switcher-status {
  @apply flex items-center gap-2;
}

.status-badge {
  @apply px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1.5;
}

.status-badge.status-active {
  @apply bg-green-100 text-green-700;
}

.status-badge.status-hidden {
  @apply bg-orange-100 text-orange-700;
}

.pulse-dot {
  @apply w-2 h-2 rounded-full bg-green-500;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

.switcher-content {
  @apply overflow-x-auto;
}

.cell-chain {
  @apply flex items-center gap-2 min-w-max;
  padding: 1rem 0;
}

.chain-node {
  @apply relative flex flex-col items-center justify-center 
         bg-white border-2 border-gray-300 rounded-lg 
         cursor-pointer transition-all duration-200
         hover:border-blue-400 hover:shadow-md
         min-w-[100px] p-3;
}

.chain-node:hover {
  @apply transform scale-105;
}

.chain-node.active {
  @apply border-blue-500 bg-blue-50 shadow-lg;
  transform: scale(1.05);
}

.chain-node.completed {
  @apply border-green-300 bg-green-50;
}

.chain-node-hide {
  @apply border-dashed border-gray-400;
  min-width: 80px;
}

.chain-node-hide.active {
  @apply border-orange-500 bg-orange-50;
}

.node-icon {
  @apply mb-2 flex items-center justify-center;
}

.node-content {
  @apply text-center;
}

.node-index {
  @apply text-xs font-bold text-gray-500 mb-1;
}

.chain-node.active .node-index {
  @apply text-blue-600;
}

.node-title {
  @apply text-sm font-medium text-gray-800 mb-1;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chain-node.active .node-title {
  @apply text-blue-700 font-semibold;
}

.node-type {
  @apply text-xs text-gray-500;
}

.chain-node.active .node-type {
  @apply text-blue-600;
}

.node-active-indicator {
  @apply absolute -top-2 -right-2 bg-blue-500 text-white rounded-full p-1;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

.node-activity-indicator {
  @apply absolute -top-1 -right-1;
}

.activity-pulse {
  @apply block w-3 h-3 bg-orange-500 rounded-full;
  animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  50%, 100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

.chain-connector {
  @apply flex-shrink-0 w-8 h-0.5 bg-gray-300 relative;
}

.chain-connector::after {
  content: '';
  @apply absolute right-0 top-1/2 transform -translate-y-1/2;
  width: 0;
  height: 0;
  border-left: 8px solid rgb(209, 213, 219);
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
}

.chain-node.active + .chain-connector,
.chain-connector + .chain-node.active {
  @apply bg-blue-400;
}

.chain-node.active + .chain-connector::after {
  border-left-color: rgb(96, 165, 250);
}

/* 不同类型节点的颜色 */
.chain-node.node-type-text {
  @apply border-violet-300;
}

.chain-node.node-type-text.active {
  @apply border-violet-500 bg-violet-50;
}

.chain-node.node-type-code {
  @apply border-blue-300;
}

.chain-node.node-type-code.active {
  @apply border-blue-500 bg-blue-50;
}

.chain-node.node-type-video {
  @apply border-pink-300;
}

.chain-node.node-type-video.active {
  @apply border-pink-500 bg-pink-50;
}

.chain-node.node-type-activity {
  @apply border-orange-300;
}

.chain-node.node-type-activity.active {
  @apply border-orange-500 bg-orange-50;
}

.chain-node.node-type-flowchart {
  @apply border-indigo-300;
}

.chain-node.node-type-flowchart.active {
  @apply border-indigo-500 bg-indigo-50;
}

.chain-node.node-type-sim {
  @apply border-emerald-300;
}

.chain-node.node-type-sim.active {
  @apply border-emerald-500 bg-emerald-50;
}

.switcher-empty {
  @apply text-center py-8 text-gray-400;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chain-node {
    min-width: 80px;
    padding: 0.75rem;
  }
  
  .node-title {
    max-width: 70px;
    font-size: 0.75rem;
  }
}
</style>

