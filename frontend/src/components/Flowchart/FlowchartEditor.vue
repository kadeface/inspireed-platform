<template>
  <div
    class="flowchart-editor h-full flex flex-col"
    style="min-height: 400px; height: 400px; width: 100%;"
  >
    <!-- 工具栏 -->
    <FlowchartToolbar
      :theme="content.style?.theme || 'light'"
      :layout-direction="content.style?.layoutDirection || 'TB'"
      @add-node="handleAddNode"
      @auto-layout="handleAutoLayout"
      @toggle-theme="handleToggleTheme"
      @change-layout="handleChangeLayout"
      @export-image="handleExportImage"
      @clear="handleClear"
    />

    <!-- 流程图画布 -->
    <div
      ref="vueFlowWrapper"
      class="flex-1 relative bg-gray-50"
      style="min-height: 400px; height: 400px; width: 100%;"
    >
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :class="{ 'dark': content.style?.theme === 'dark' }"
        :default-zoom="1"
        :min-zoom="0.2"
        :max-zoom="4"
        @connect="onConnect"
        @connect-start="handleInteractionStart"
        @connect-end="handleInteractionEnd"
        @node-drag-start="handleInteractionStart"
        @node-drag-stop="handleNodeDragStop"
        @move-start="handleInteractionStart"
        @move-end="handleInteractionEnd"
        @edge-update="onEdgeUpdate"
      >
        <!-- 背景网格 -->
        <Background
          :pattern-color="content.style?.theme === 'dark' ? '#555' : '#aaa'"
          :gap="16"
        />

        <!-- 控制按钮 -->
        <MiniMap v-if="showMinimap" />

        <!-- 自定义节点 -->
        <template #node-start="nodeProps">
          <StartNode v-bind="nodeProps" />
        </template>
        <template #node-process="nodeProps">
          <ProcessNode v-bind="nodeProps" />
        </template>
        <template #node-decision="nodeProps">
          <DecisionNode v-bind="nodeProps" />
        </template>
        <template #node-loop="nodeProps">
          <LoopNode v-bind="nodeProps" />
        </template>
        <template #node-end="nodeProps">
          <EndNode v-bind="nodeProps" />
        </template>
      </VueFlow>
      <FlowchartZoomControls position="top-right" />
    </div>

    <!-- 节点编辑对话框 -->
    <NodeEditDialog
      v-if="editingNode"
      :node="editingNode"
      @save="handleSaveNode"
      @close="editingNode = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, provide, nextTick, onBeforeUnmount } from 'vue'
import { VueFlow, useVueFlow, MarkerType } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import type { Node, Edge, Connection } from '@vue-flow/core'
import { v4 as uuidv4 } from 'uuid'
import dagre from 'dagre'

import FlowchartToolbar from './FlowchartToolbar.vue'
import FlowchartZoomControls from './FlowchartZoomControls.vue'
import StartNode from './nodes/StartNode.vue'
import ProcessNode from './nodes/ProcessNode.vue'
import DecisionNode from './nodes/DecisionNode.vue'
import LoopNode from './nodes/LoopNode.vue'
import EndNode from './nodes/EndNode.vue'
import NodeEditDialog from './NodeEditDialog.vue'
import type { FlowchartCellContent, FlowchartNode, FlowchartEdge } from '@/types/cell'

// 导入样式
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

interface Props {
  content: FlowchartCellContent
  showMinimap?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showMinimap: true,
})

const emit = defineEmits<{
  update: [content: FlowchartCellContent]
}>()

// Vue Flow 实例
const { fitView } = useVueFlow()

// 节点和边
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const editingNode = ref<FlowchartNode | null>(null)
const vueFlowWrapper = ref<HTMLElement | null>(null)
const isSyncingFromProps = ref(false)
const isInteracting = ref(false)

const EDITOR_INJECTION_KEY = 'flowchart-open-editor'

provide(EDITOR_INJECTION_KEY, openNodeEditor)

function notifyInteractionStart() {
  if (isInteracting.value) return
  isInteracting.value = true
  window.dispatchEvent(new CustomEvent('flowchart-interaction-start'))
}

function notifyInteractionEnd() {
  if (!isInteracting.value) return
  isInteracting.value = false
  window.dispatchEvent(new CustomEvent('flowchart-interaction-end'))
}

// 初始化数据
watch(
  () => props.content,
  (newContent) => {
    isSyncingFromProps.value = true
    // 转换 FlowchartNode 到 Vue Flow Node
    nodes.value = newContent.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: {
        label: node.label,
        ...node.data,
      },
    }))

    // 转换 FlowchartEdge 到 Vue Flow Edge
    edges.value = newContent.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      animated: false,
      markerEnd: MarkerType.ArrowClosed,
    }))

    nextTick(() => {
      if (newContent.nodes.length) {
        setTimeout(() => {
          fitView({ padding: 0.2, duration: 300 })
        }, 100)
      }
      isSyncingFromProps.value = false
    })
  },
  { immediate: true }
)

// 监听节点和边的变化，同步到 content
watch(
  [nodes, edges],
  () => {
    if (isSyncingFromProps.value) return
    emitUpdate()
  },
  { deep: true }
)

// 添加节点
function handleAddNode(type: 'start' | 'process' | 'decision' | 'loop' | 'end') {
  const nodeId = uuidv4()
  const labels = {
    start: '开始',
    process: '处理过程',
    decision: '判断条件',
    loop: '循环节点',
    end: '结束',
  }

  const newNode: Node = {
    id: nodeId,
    type,
    position: {
      x: Math.random() * 400 + 100,
      y: Math.random() * 300 + 100,
    },
    data: {
      label: labels[type],
    },
  }

  nodes.value = [...nodes.value, newNode]
}

// 连接节点
function onConnect(connection: Connection) {
  const edgeId = uuidv4()
  const edge: Edge = {
    id: edgeId,
    source: connection.source!,
    target: connection.target!,
    type: 'smoothstep',
    animated: false,
    markerEnd: MarkerType.ArrowClosed,
  }
  edges.value = [...edges.value, edge]
}

// 节点拖动停止
function onNodeDragStop() {
  emitUpdate()
}

function handleInteractionStart() {
  notifyInteractionStart()
}

function handleInteractionEnd() {
  notifyInteractionEnd()
}

function handleNodeDragStop() {
  onNodeDragStop()
  notifyInteractionEnd()
}

// 边更新
function onEdgeUpdate({ edge, connection }: { edge: Edge; connection: Connection }) {
  const index = edges.value.findIndex((e) => e.id === edge.id)
  if (index !== -1) {
    const updated = {
      ...edge,
      source: connection.source!,
      target: connection.target!,
    }
    const nextEdges = [...edges.value]
    nextEdges[index] = updated
    edges.value = nextEdges
  }
}

// 自动布局
function handleAutoLayout() {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  
  const direction = props.content.style?.layoutDirection || 'TB'
 
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 80,
    ranksep: 80,
  })

  // 添加节点到 dagre
  nodes.value.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 50 })
  })

  // 添加边到 dagre
  edges.value.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  // 计算布局
  dagre.layout(dagreGraph)

  // 更新节点位置
  nodes.value = nodes.value.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    if (!nodeWithPosition) {
      return node
    }

    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 75,
        y: nodeWithPosition.y - 25,
      },
    }
  })

  // 延迟适应视图
  setTimeout(() => {
    fitView({ padding: 0.2, duration: 300 })
  }, 50)
}

// 切换主题
function handleToggleTheme() {
  const newTheme = props.content.style?.theme === 'dark' ? 'light' : 'dark'
  emitUpdate({
    style: {
      ...props.content.style,
      theme: newTheme,
    },
  })
}

// 改变布局方向
function handleChangeLayout(direction: 'TB' | 'LR' | 'BT' | 'RL') {
  emitUpdate({
    style: {
      ...props.content.style,
      layoutDirection: direction,
    },
  })
  // 自动重新布局
  setTimeout(() => handleAutoLayout(), 100)
}

// 导出图片
async function handleExportImage() {
  // 使用 html2canvas 导出
  const { default: html2canvas } = await import('html2canvas')
  const vueFlowEl = vueFlowWrapper.value?.querySelector('.vue-flow') as HTMLElement | null
  
  if (vueFlowEl) {
    const canvas = await html2canvas(vueFlowEl, {
      backgroundColor: props.content.style?.theme === 'dark' ? '#1a1a1a' : '#ffffff',
    })
    
    // 下载图片
    const link = document.createElement('a')
    link.download = 'flowchart.png'
    link.href = canvas.toDataURL()
    link.click()
  }
}

// 清空画布
function handleClear() {
  if (confirm('确定要清空整个流程图吗？')) {
    nodes.value = []
    edges.value = []
  }
}

// 保存节点编辑
function handleSaveNode(updatedNode: FlowchartNode) {
  const index = nodes.value.findIndex((n) => n.id === updatedNode.id)
  if (index !== -1) {
    const updated = {
      ...nodes.value[index],
      data: {
        label: updatedNode.label,
        ...updatedNode.data,
      },
    }
    const nextNodes = [...nodes.value]
    nextNodes[index] = updated
    nodes.value = nextNodes
  }
  editingNode.value = null
}

function openNodeEditor(nodeId: string) {
  const node = nodes.value.find((n) => n.id === nodeId)
  if (!node) return

  editingNode.value = {
    id: node.id,
    type: (node.type as FlowchartNode['type']) || 'process',
    label: node.data?.label || '',
    position: { ...node.position },
    data: {
      ...node.data,
    },
  }
}

// 触发更新事件
function emitUpdate(partial?: Partial<FlowchartCellContent>) {
  const flowchartNodes: FlowchartNode[] = nodes.value.map((node) => ({
    id: node.id,
    type: node.type as any,
    label: node.data.label,
    position: node.position,
    data: node.data,
  }))

  const flowchartEdges: FlowchartEdge[] = edges.value.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label as string | undefined,
  }))

  const style = {
    ...(props.content.style ?? {}),
    ...(partial?.style ?? {}),
  }

  const payload: FlowchartCellContent = {
    nodes: flowchartNodes,
    edges: flowchartEdges,
    style,
  }

  if (partial) {
    Object.assign(payload, partial)
    if (partial.style) {
      payload.style = style
    }
  }

  emit('update', payload)
}

// 导出 fitView 供外部调用
defineExpose({
  fitView,
  autoLayout: handleAutoLayout,
})

onBeforeUnmount(() => {
  notifyInteractionEnd()
})
</script>

<style scoped>
.flowchart-editor {
  @apply w-full bg-white rounded-lg shadow-sm overflow-hidden;
}

:deep(.vue-flow) {
  @apply w-full h-full;
}

:deep(.vue-flow.dark) {
  @apply bg-gray-900;
}

:deep(.vue-flow__edge-path) {
  stroke: #b1b1b7;
  stroke-width: 2;
}

:deep(.vue-flow.dark .vue-flow__edge-path) {
  stroke: #555;
}

:deep(.vue-flow__edge-label) {
  @apply text-xs bg-white px-2 py-1 rounded shadow-sm;
}

:deep(.vue-flow.dark .vue-flow__edge-label) {
  @apply bg-gray-800 text-gray-200;
}
</style>

