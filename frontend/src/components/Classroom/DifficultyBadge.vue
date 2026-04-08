<template>
  <span
    class="difficulty-badge"
    :class="`difficulty-${level}`"
    :aria-label="`难度: ${levelLabel}`"
  >
    {{ levelIcon }} {{ levelLabel }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  level?: 'beginner' | 'intermediate' | 'advanced'
}

const props = withDefaults(defineProps<Props>(), {
  level: 'beginner'
})

const levelIcon = computed(() => {
  const icons = {
    beginner: '🟢',
    intermediate: '🟡',
    advanced: '🔴'
  }
  return icons[props.level]
})

const levelLabel = computed(() => {
  const labels = {
    beginner: '入门',
    intermediate: '中级',
    advanced: '高级'
  }
  return labels[props.level]
})
</script>

<style scoped>
.difficulty-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
}

.difficulty-beginner {
  background: #DCFCE7;
  color: #166534;
}

.difficulty-intermediate {
  background: #FEF9C3;
  color: #854D0E;
}

.difficulty-advanced {
  background: #FEE2E2;
  color: #991B1B;
}
</style>
