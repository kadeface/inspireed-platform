<template>
  <div class="flowchart-cell">
    <!-- 教师编辑模式 -->
    <div v-if="editable" class="flowchart-editor">
      <div class="editor-placeholder">
        <div class="placeholder-icon">📊</div>
        <h3 class="placeholder-title">流程图编辑器</h3>
        <p class="placeholder-text">
          流程图功能正在开发中...
        </p>
        <div class="feature-list">
          <div class="feature-item">✅ 支持多种节点类型（开始、过程、决策、结束）</div>
          <div class="feature-item">✅ 拖拽式可视化编辑</div>
          <div class="feature-item">✅ 自动布局</div>
          <div class="feature-item">✅ 导出为图片</div>
        </div>
        <p class="tech-note">
          推荐技术栈: Vue Flow 或 Mermaid.js
        </p>
      </div>
    </div>

    <!-- 学生查看模式 -->
    <div v-else class="flowchart-viewer">
      <div class="viewer-placeholder">
        <div class="placeholder-icon">📊</div>
        <h3 class="placeholder-title">流程图查看器</h3>
        <p class="placeholder-text">
          {{ cell.content.nodes.length }} 个节点, {{ cell.content.edges.length }} 个连线
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FlowchartCell } from '../../types/cell'

interface Props {
  cell: FlowchartCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: FlowchartCell]
}>()

// TODO: 实现流程图编辑和查看功能
// 推荐使用 @vue-flow/core 库
</script>

<style scoped>
.flowchart-cell {
  @apply min-h-[400px];
}

.flowchart-editor,
.flowchart-viewer {
  @apply w-full h-full;
}

.editor-placeholder,
.viewer-placeholder {
  @apply flex flex-col items-center justify-center py-16 px-8 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-dashed border-blue-300;
}

.placeholder-icon {
  @apply text-6xl mb-4;
}

.placeholder-title {
  @apply text-2xl font-bold text-gray-800 mb-2;
}

.placeholder-text {
  @apply text-gray-600 text-center mb-6;
}

.feature-list {
  @apply space-y-2 mb-6;
}

.feature-item {
  @apply text-sm text-gray-700 flex items-center gap-2;
}

.tech-note {
  @apply text-xs text-gray-500 bg-white px-4 py-2 rounded-full;
}
</style>

