<template>
  <div class="progress-ring" :style="{ width: size + 'px', height: size + 'px' }">
    <svg
      :width="size"
      :height="size"
      :viewBox="`0 0 ${size} ${size}`"
      class="progress-ring-svg"
    >
      <!-- Background circle -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="transparent"
        :stroke="backgroundColor"
        :stroke-width="strokeWidth"
      />
      <!-- Progress circle -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="transparent"
        :stroke="color"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
        :stroke-linecap="'round'"
        class="progress-ring-circle"
        transform="rotate(-90)"
        :transform-origin="`${size / 2} ${size / 2}`"
      />
    </svg>
    <div class="progress-ring-text">{{ percentage }}%</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  percentage?: number
  size?: number
  strokeWidth?: number
  color?: string
  backgroundColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  percentage: 0,
  size: 40,
  strokeWidth: 3,
  color: '#10B981',
  backgroundColor: '#E5E7EB'
})

const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashoffset = computed(() => {
  const progress = Math.min(100, Math.max(0, props.percentage))
  return circumference.value - (progress / 100) * circumference.value
})
</script>

<style scoped>
.progress-ring {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.progress-ring-svg {
  transform: rotate(0deg);
}

.progress-ring-circle {
  transition: stroke-dashoffset 0.35s ease-out;
}

.progress-ring-text {
  position: absolute;
  font-size: 10px;
  font-weight: 700;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
