<template>
  <div v-if="showDisplay && count > 0" class="module-count-info">
    <span class="module-count-icon">📚</span>
    <span class="module-count-text">
      <span class="module-count-value">{{ count }}</span>
      <span class="module-count-label">{{ label }}</span>
    </span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  count?: number  // 模块数量
  label?: string  // 显示文本
  showDisplay?: boolean
}

withDefaults(defineProps<Props>(), {
  count: 0,
  label: '个模块',
  showDisplay: true
})
</script>

<style scoped>
.module-count-info {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: #eff6ff;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid #bfdbfe;
}

.module-count-icon {
  font-size: 1rem;
}

.module-count-text {
  display: flex;
  align-items: center;
  gap: 0.125rem;
}

.module-count-value {
  font-weight: 700;
  font-size: 1rem;
  color: #2563eb;
}

.module-count-label {
  color: #4b5563;
  font-size: 0.8125rem;
}
</style>
