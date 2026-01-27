<template>
  <div class="zoom-controls" :class="positionClass">
    <button
      class="zoom-button"
      type="button"
      title="缩小"
      @click="handleZoomOut"
    >
      <span class="symbol">−</span>
    </button>
    <button
      class="zoom-button"
      type="button"
      title="放大"
      @click="handleZoomIn"
    >
      <span class="symbol">＋</span>
    </button>
    <button
      v-if="showFitView"
      class="zoom-button"
      type="button"
      title="适应视图"
      @click="handleFitView"
    >
      <svg class="icon" viewBox="0 0 20 20" fill="currentColor">
        <path
          fill-rule="evenodd"
          d="M4.5 3a1.5 1.5 0 00-1.5 1.5V7a1 1 0 102 0V5.5H7a1 1 0 100-2H4.5zm11 0H13a1 1 0 100 2h2.5V7a1 1 0 102 0V4.5A1.5 1.5 0 0015.5 3zm-11 14H7a1 1 0 100-2H4.5V13a1 1 0 10-2 0v2.5A1.5 1.5 0 004.5 17zm11 0a1.5 1.5 0 001.5-1.5V13a1 1 0 10-2 0v1.5H13a1 1 0 100 2h2.5z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useVueFlow } from '@vue-flow/core'

interface Props {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  showFitView?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  position: 'bottom-left',
  showFitView: true,
})

const { zoomIn, zoomOut, fitView } = useVueFlow()

const positionClass = computed(() => {
  switch (props.position) {
    case 'top-left':
      return 'top-left'
    case 'top-right':
      return 'top-right'
    case 'bottom-right':
      return 'bottom-right'
    default:
      return 'bottom-left'
  }
})

function handleZoomIn() {
  zoomIn({ duration: 120 })
}

function handleZoomOut() {
  zoomOut({ duration: 120 })
}

function handleFitView() {
  fitView({ padding: 0.2, duration: 200 })
}
</script>

<style scoped>
.zoom-controls {
  @apply absolute z-20 flex items-center gap-2;
}

.zoom-controls.bottom-left {
  @apply left-4 bottom-4;
}

.zoom-controls.bottom-right {
  @apply right-4 bottom-4;
}

.zoom-controls.top-left {
  @apply left-4 top-4;
}

.zoom-controls.top-right {
  @apply right-4 top-4;
}

.zoom-button {
  @apply w-10 h-10 flex items-center justify-center rounded-full bg-white shadow-md text-gray-600 border border-gray-200 hover:bg-blue-50 hover:text-blue-600 transition-colors;
}

.zoom-button:focus {
  @apply outline-none ring-2 ring-blue-200;
}

.symbol {
  @apply text-xl leading-none font-semibold;
}

.icon {
  @apply w-4 h-4;
}
</style>


