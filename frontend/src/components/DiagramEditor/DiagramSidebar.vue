<template>
  <div class="diagram-sidebar">
    <div class="sidebar-header">
      <h3 class="sidebar-title">节点库</h3>
    </div>

    <div class="sidebar-content">
      <!-- 流程图节点 -->
      <div v-if="mode === 'flowchart'" class="node-category">
        <h4 class="category-title">流程图节点</h4>
        <div class="node-list">
          <div
            v-for="node in flowchartNodes"
            :key="node.shape"
            class="node-item"
            @mousedown="handleMouseDown($event, node)"
          >
            <div class="node-preview" :style="getNodePreviewStyle(node)">
              {{ node.label }}
            </div>
            <span class="node-label">{{ node.label }}</span>
          </div>
        </div>
      </div>

      <!-- 思维导图节点 -->
      <div v-if="mode === 'mindmap'" class="node-category">
        <h4 class="category-title">思维导图节点</h4>
        <div class="node-list">
          <div
            v-for="node in mindmapNodes"
            :key="node.shape"
            class="node-item"
            @mousedown="handleMouseDown($event, node)"
          >
            <div class="node-preview" :style="getNodePreviewStyle(node)">
              {{ node.label }}
            </div>
            <span class="node-label">{{ node.label }}</span>
          </div>
        </div>
      </div>

      <!-- 使用提示 -->
      <div class="usage-tips">
        <div class="tip-item">
          <span class="tip-icon">💡</span>
          <span class="tip-text">拖拽节点到画布添加</span>
        </div>
        <div class="tip-item">
          <span class="tip-icon">⌨️</span>
          <span class="tip-text">双击节点编辑文本</span>
        </div>
        <div class="tip-item" v-if="mode === 'mindmap'">
          <span class="tip-icon">Tab</span>
          <span class="tip-text">添加子节点</span>
        </div>
        <div class="tip-item" v-if="mode === 'mindmap'">
          <span class="tip-icon">Enter</span>
          <span class="tip-text">添加兄弟节点</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DiagramMode } from '@/types/diagram'

interface NodeTemplate {
  shape: string
  label: string
  width: number
  height: number
  style: {
    stroke: string
    fill: string
    borderRadius?: string
  }
}

interface Props {
  mode: DiagramMode
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'drag-start': [node: NodeTemplate, event: MouseEvent]
}>()

const flowchartNodes: NodeTemplate[] = [
  {
    shape: 'flowchart-start',
    label: '开始',
    width: 100,
    height: 60,
    style: { stroke: '#10B981', fill: '#D1FAE5', borderRadius: '50%' },
  },
  {
    shape: 'flowchart-end',
    label: '结束',
    width: 100,
    height: 60,
    style: { stroke: '#EF4444', fill: '#FEE2E2', borderRadius: '50%' },
  },
  {
    shape: 'flowchart-process',
    label: '处理',
    width: 140,
    height: 60,
    style: { stroke: '#3B82F6', fill: '#DBEAFE', borderRadius: '8px' },
  },
  {
    shape: 'flowchart-decision',
    label: '判断',
    width: 140,
    height: 80,
    style: { stroke: '#F59E0B', fill: '#FEF3C7' },
  },
  {
    shape: 'flowchart-loop',
    label: '循环',
    width: 140,
    height: 60,
    style: { stroke: '#8B5CF6', fill: '#EDE9FE', borderRadius: '8px' },
  },
  {
    shape: 'flowchart-io',
    label: '输入/输出',
    width: 140,
    height: 60,
    style: { stroke: '#06B6D4', fill: '#CFFAFE' },
  },
  {
    shape: 'flowchart-document',
    label: '文档',
    width: 140,
    height: 60,
    style: { stroke: '#EC4899', fill: '#FCE7F3', borderRadius: '4px' },
  },
]

const mindmapNodes: NodeTemplate[] = [
  {
    shape: 'mindmap-central',
    label: '中心主题',
    width: 180,
    height: 60,
    style: { stroke: '#5F95FF', fill: '#EFF4FF', borderRadius: '30px' },
  },
  {
    shape: 'mindmap-main-branch',
    label: '一级分支',
    width: 140,
    height: 50,
    style: { stroke: '#10B981', fill: '#ECFDF5', borderRadius: '25px' },
  },
  {
    shape: 'mindmap-sub-branch',
    label: '二级分支',
    width: 120,
    height: 40,
    style: { stroke: '#F59E0B', fill: '#FEF3C7', borderRadius: '20px' },
  },
  {
    shape: 'mindmap-leaf',
    label: '叶子',
    width: 100,
    height: 35,
    style: { stroke: '#8B5CF6', fill: '#F5F3FF', borderRadius: '18px' },
  },
]

function handleMouseDown(event: MouseEvent, node: NodeTemplate) {
  // 使用 X6 Dnd 插件，传递节点和鼠标事件
  emit('drag-start', node, event)
}

function getNodePreviewStyle(node: NodeTemplate) {
  return {
    border: `2px solid ${node.style.stroke}`,
    backgroundColor: node.style.fill,
    borderRadius: node.style.borderRadius || '0',
    width: '60px',
    height: '40px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: '500',
    color: '#374151',
  }
}
</script>

<style scoped>
.diagram-sidebar {
  @apply w-64 bg-gray-50 border-r border-gray-200 flex flex-col;
}

.sidebar-header {
  @apply px-4 py-3 border-b border-gray-200 bg-white;
}

.sidebar-title {
  @apply text-base font-semibold text-gray-900;
}

.sidebar-content {
  @apply flex-1 overflow-y-auto p-4 space-y-6;
}

.node-category {
  @apply space-y-3;
}

.category-title {
  @apply text-sm font-semibold text-gray-700;
}

.node-list {
  @apply grid grid-cols-2 gap-3;
}

.node-item {
  @apply flex flex-col items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 cursor-move transition-all hover:shadow-md hover:border-blue-300;
}

.node-item:active {
  @apply opacity-50;
}

.node-preview {
  @apply select-none;
}

.node-label {
  @apply text-xs text-gray-600 text-center;
}

.usage-tips {
  @apply mt-6 p-3 bg-blue-50 rounded-lg border border-blue-100 space-y-2;
}

.tip-item {
  @apply flex items-center gap-2 text-xs text-gray-600;
}

.tip-icon {
  @apply text-sm;
}

.tip-text {
  @apply flex-1;
}
</style>

