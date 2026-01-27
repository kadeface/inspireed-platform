<template>
  <div class="process-node">
    <Handle type="target" :position="Position.Top" />
    <div class="node-content">
      <div class="node-icon">📦</div>
      <div class="node-label" @dblclick="handleEdit">
        {{ data.label || '处理过程' }}
      </div>
    </div>
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { Handle, Position } from '@vue-flow/core'

interface Props {
  id: string
  data: {
    label: string
    [key: string]: any
  }
}

const props = defineProps<Props>()

const openEditor = inject<(id: string) => void>('flowchart-open-editor')

function handleEdit() {
  openEditor?.(props.id)
}
</script>

<style scoped>
.process-node {
  @apply relative px-6 py-4 bg-gradient-to-r from-blue-400 to-blue-500 
         rounded-lg border-2 border-blue-600 shadow-lg;
  min-width: 150px;
}

.node-content {
  @apply flex items-center justify-center gap-2;
}

.node-icon {
  @apply text-xl;
}

.node-label {
  @apply text-white font-medium text-sm cursor-pointer;
}

.node-label:hover {
  @apply underline;
}
</style>

