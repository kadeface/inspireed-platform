<template>
  <div class="loop-node">
    <Handle type="target" :position="Position.Top" />
    <div class="node-content">
      <div class="node-icon">🔁</div>
      <div class="node-label" @dblclick="handleEdit">
        {{ data.label || '循环节点' }}
      </div>
    </div>
    <Handle type="source" id="loop-continue" :position="Position.Bottom" />
    <Handle type="source" id="loop-exit" :position="Position.Right" />
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
.loop-node {
  @apply relative px-6 py-4 bg-gradient-to-r from-purple-400 to-purple-500
         rounded-lg border-2 border-purple-600 shadow-lg;
  min-width: 160px;
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

