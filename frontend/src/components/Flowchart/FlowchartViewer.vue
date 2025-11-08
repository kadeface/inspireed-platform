<template>
  <div
    class="flowchart-viewer h-full"
    style="min-height: 400px; height: 400px; width: 100%;"
  >
    <div
      class="relative bg-gray-50 h-full"
      style="min-height: 400px; height: 400px; width: 100%;"
    >
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :class="{ 'dark': content.style?.theme === 'dark' }"
        :default-zoom="1"
        :min-zoom="0.2"
        :max-zoom="4"
        :nodes-draggable="false"
        :nodes-connectable="false"
        :elements-selectable="false"
      >
        <!-- 背景网格 -->
        <Background
          :pattern-color="content.style?.theme === 'dark' ? '#555' : '#aaa'"
          :gap="16"
        />

        <!-- 控制按钮（只读模式） -->
        <MiniMap v-if="showMinimap" />

        <!-- 自定义节点（只读） -->
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

      <!-- 只读提示 -->
      <div class="absolute top-4 left-4 bg-blue-100 text-blue-800 px-4 py-2 rounded-lg shadow-sm text-sm">
        📖 查看模式（不可编辑）
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VueFlow, useVueFlow, MarkerType } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import type { Node, Edge } from '@vue-flow/core'

import FlowchartZoomControls from './FlowchartZoomControls.vue'
import StartNode from './nodes/StartNode.vue'
import ProcessNode from './nodes/ProcessNode.vue'
import DecisionNode from './nodes/DecisionNode.vue'
import LoopNode from './nodes/LoopNode.vue'
import EndNode from './nodes/EndNode.vue'
import type { FlowchartCellContent } from '@/types/cell'

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

const { fitView } = useVueFlow()

const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])

// 初始化数据
watch(
  () => props.content,
  (newContent) => {
    nodes.value = newContent.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: {
        label: node.label,
        ...node.data,
      },
    }))

    edges.value = newContent.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      animated: false,
      markerEnd: MarkerType.ArrowClosed,
    }))

    // 自动适应视图
    setTimeout(() => {
      fitView({ padding: 0.2, duration: 300 })
    }, 100)
  },
  { immediate: true }
)

defineExpose({
  fitView,
})
</script>

<style scoped>
.flowchart-viewer {
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

