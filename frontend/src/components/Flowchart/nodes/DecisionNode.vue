<template>
  <div class="decision-node-wrapper">
    <Handle type="target" :position="Position.Top" />
    
    <div class="decision-node">
      <div class="node-content">
        <div class="node-icon">💎</div>
        <div class="node-label" @dblclick="handleEdit">
          {{ data.label || '判断条件' }}
        </div>
      </div>
    </div>
    
    <!-- 多个输出连接点 -->
    <Handle type="source" :position="Position.Bottom" :id="`${id}-bottom`" />
    <Handle type="source" :position="Position.Left" :id="`${id}-left`" />
    <Handle type="source" :position="Position.Right" :id="`${id}-right`" />
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
.decision-node-wrapper {
  @apply relative;
}

.decision-node {
  @apply relative px-8 py-6 bg-gradient-to-r from-yellow-400 to-yellow-500 
         border-2 border-yellow-600 shadow-lg;
  /* 菱形形状 */
  transform: rotate(45deg);
  min-width: 120px;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-content {
  /* 旋转回来让文字正常显示 */
  transform: rotate(-45deg);
  @apply flex flex-col items-center justify-center gap-1;
}

.node-icon {
  @apply text-xl;
}

.node-label {
  @apply text-white font-medium text-sm text-center cursor-pointer max-w-[100px];
  line-height: 1.2;
}

.node-label:hover {
  @apply underline;
}
</style>

