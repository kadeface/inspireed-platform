<template>
  <div v-if="showDisplay && count > 0" class="module-count-info" data-testid="module-count">
    <span class="module-count-icon">📚</span>
    <span class="module-count-text">
      <span class="module-count-value" data-testid="module-count-value">{{ count }}</span>
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
  gap: 0.375rem;
  height: 36px;
  padding: 0 0.75rem;
  background: #ffffff;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
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
  font-weight: 600;
  font-size: 0.875rem;
  color: #0f172a;
}

.module-count-label {
  color: #334155;
  font-size: 0.875rem;
}
</style>
