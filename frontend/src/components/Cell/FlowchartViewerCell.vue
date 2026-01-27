<template>
  <div class="flowchart-cell-view">
    <FlowchartViewer
      :content="cell.content"
      :show-minimap="cell.config?.showMinimap ?? true"
    />
  </div>
</template>

<script setup lang="ts">
import type { FlowchartCell } from '@/types/cell'
import FlowchartViewer from '@/components/Flowchart/FlowchartViewer.vue'

interface Props {
  cell: FlowchartCell
}

defineProps<Props>()
</script>

<style scoped>
.flowchart-cell-view {
  @apply bg-white rounded-lg shadow-sm overflow-hidden;
}
</style>

