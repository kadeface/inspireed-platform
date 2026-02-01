<template>
  <div v-if="showDisplay" class="student-count-info">
    <span class="student-count-icon">👥</span>
    <span class="student-count-text">
      <span class="student-count-value">{{ activeCount }}</span>
      <span v-if="totalCount > 0" class="student-count-total">/{{ totalCount }}</span>
      <span class="student-count-label">{{ label }}</span>
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  activeCount?: number  // 已进入的学生数
  totalCount?: number  // 总学生数
  label?: string  // 显示文本
  showDisplay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  activeCount: 0,
  totalCount: 0,
  label: '人已进入',
  showDisplay: true
})
</script>

<style scoped>
.student-count-info {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: #f0fdf4;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #bbf7d0;
}

.student-count-icon {
  font-size: 1rem;
}

.student-count-text {
  display: flex;
  align-items: center;
  gap: 0.125rem;
}

.student-count-value {
  font-weight: 700;
  font-size: 1rem;
  color: #16a34a;
}

.student-count-total {
  color: #6b7280;
  font-size: 0.875rem;
}

.student-count-label {
  color: #4b5563;
  font-size: 0.8125rem;
}
</style>
