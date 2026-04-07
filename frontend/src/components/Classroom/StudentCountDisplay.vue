<template>
  <div v-if="showDisplay" class="student-count-info" data-testid="student-count">
    <span class="student-count-icon" aria-hidden="true"></span>
    <span class="student-count-text">
      <span class="student-count-value" data-testid="student-count-value">{{ activeCount }}</span>
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
  gap: 0.35rem;
  padding: 0.4rem 0.8rem;
  background: linear-gradient(180deg, #f7fdf9 0%, #eefcf3 100%);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  border: 1px solid #b6eec8;
  box-shadow: 0 2px 8px rgba(22, 163, 74, 0.08);
}

.student-count-icon {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 999px;
  background: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.16);
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
