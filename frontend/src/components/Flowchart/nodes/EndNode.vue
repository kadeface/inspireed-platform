<template>
  <div class="end-node">
    <Handle type="target" :position="Position.Top" />
    <div class="node-content">
      <div class="node-icon">🔴</div>
      <div class="node-label" @dblclick="handleEdit">
        {{ data.label || '结束' }}
      </div>
    </div>
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
.end-node {
  @apply relative px-6 py-3 bg-gradient-to-r from-red-400 to-red-500 
         rounded-full border-2 border-red-600 shadow-lg;
  min-width: 120px;
}

.node-content {
  @apply flex items-center justify-center gap-2;
}

.node-icon {
  @apply text-xl;
}

.node-label {
  @apply text-white font-semibold text-sm cursor-pointer;
}

.node-label:hover {
  @apply underline;
}
</style>

