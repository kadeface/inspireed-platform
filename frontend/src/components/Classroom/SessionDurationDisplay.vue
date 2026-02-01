<template>
  <div
    v-if="showDisplay"
    class="duration-info"
    :class="{
      'duration-warning': isWarning,
      'duration-danger': isDanger
    }"
  >
    <span class="duration-icon">⏱️</span>
    <span class="duration-text">
      <span
        class="duration-value"
        :class="{
          'text-blue-600': !isWarning && !isDanger,
          'text-orange-600': isWarning && !isDanger,
          'text-red-600': isDanger
        }"
      >
        {{ formattedDuration }}
      </span>
      <span v-if="showRemaining" class="duration-remaining">
        剩余: {{ formattedRemaining }}
      </span>
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status?: string
  duration?: number  // 当前时长（秒）
  remaining?: number  // 剩余时长（秒）
  showDisplay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  status: 'ended',
  duration: 0,
  remaining: 0,
  showDisplay: true
})

// 计算是否显示剩余时间（只在active/teaching状态显示）
const showRemaining = computed(() => {
  const normalizedStatus = props.status.toLowerCase()
  return normalizedStatus === 'active' || normalizedStatus === 'teaching'
})

// 计算是否处于警告状态（剩余时间 < 10分钟）
const isWarning = computed(() => {
  return props.remaining < 600 && props.remaining >= 300
})

// 计算是否处于危险状态（剩余时间 < 5分钟）
const isDanger = computed(() => {
  return props.remaining < 300
})

// 格式化时长显示
const formattedDuration = computed(() => {
  const minutes = Math.floor(props.duration / 60)
  const seconds = props.duration % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

// 格式化剩余时间
const formattedRemaining = computed(() => {
  const minutes = Math.floor(props.remaining / 60)
  const seconds = props.remaining % 60
  return `${minutes}分${seconds}秒`
})
</script>

<style scoped>
.duration-info {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: #f9fafb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.duration-icon {
  font-size: 1rem;
}

.duration-text {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.duration-value {
  font-weight: 600;
  font-family: monospace;
  font-size: 0.9375rem;
}

.duration-remaining {
  color: #6b7280;
  font-size: 0.8125rem;
}

.duration-warning {
  background: #fef3c7;
  border: 1px solid #fbbf24;
}

.duration-danger {
  background: #fef2f2;
  border: 1px solid #f87171;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}
</style>
