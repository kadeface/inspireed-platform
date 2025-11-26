<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="param-cell cell-container p-4" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
    <!-- 全屏按钮 -->
    <div v-if="!editable" class="cell-toolbar mb-3">
      <button
        class="cell-fullscreen-btn"
        :class="{ 'active': isFullscreen }"
        @click="toggleFullscreen"
        :title="isFullscreen ? '退出全屏 (Esc)' : '全屏查看'"
      >
        <svg v-if="!isFullscreen" class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <svg v-else class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span class="text-sm font-medium ml-1">{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
      </button>
    </div>
    
    <h3 class="text-lg font-semibold mb-3">{{ cell.title || '参数配置' }}</h3>
    <div class="param-form">
      <div v-for="(value, key) in cell.content.values" :key="key" class="param-item mb-3">
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ key }}</label>
        <input
          v-model="cell.content.values[key]"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :disabled="!editable"
          @change="handleUpdate"
        />
      </div>
    </div>
    <p class="text-sm text-gray-500 mt-4">JSON Schema驱动的表单功能开发中...</p>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable vue/no-mutating-props */
import { ref } from 'vue'
import type { ParamCell as ParamCellType } from '../../types/cell'
import { useFullscreen } from '@/composables/useFullscreen'

interface Props {
  cell: ParamCellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: ParamCellType]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

function handleUpdate() {
  emit('update', props.cell)
}
</script>

<style scoped>
/* 全屏按钮样式 */
.cell-toolbar {
  @apply flex justify-end;
}

.cell-fullscreen-btn {
  @apply flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors;
}

.cell-fullscreen-btn.active {
  @apply bg-red-50 hover:bg-red-100 text-red-700;
}

.cell-fullscreen-btn .icon {
  @apply w-4 h-4;
}

/* 全屏模式样式 */
.param-cell.fullscreen {
  @apply fixed inset-0 z-50 bg-white overflow-auto p-8;
}

.param-cell.fullscreen .param-form {
  @apply max-w-2xl mx-auto;
}
</style>

