<template>
  <div class="flowchart-cell">
    <!-- 教师编辑模式 -->
    <div v-if="editable" class="flowchart-editor-wrapper">
      <FlowchartEditor
        :content="cell.content"
        :show-minimap="cell.config?.showMinimap ?? true"
        @update="handleUpdate"
      />
    </div>

    <!-- 学生查看模式 -->
    <div v-else class="flowchart-viewer-wrapper">
      <FlowchartViewer
        :content="cell.content"
        :show-minimap="cell.config?.showMinimap ?? true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import FlowchartEditor from '../Flowchart/FlowchartEditor.vue'
import FlowchartViewer from '../Flowchart/FlowchartViewer.vue'
import type { FlowchartCell, FlowchartCellContent } from '../../types/cell'

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

function handleUpdate(newContent: FlowchartCellContent) {
  emit('update', {
    ...props.cell,
    content: newContent,
  })
}
</script>

<style scoped>
.flowchart-cell {
  @apply min-h-[500px];
}

.flowchart-editor-wrapper,
.flowchart-viewer-wrapper {
  @apply w-full h-full;
  min-height: 500px;
}
</style>

