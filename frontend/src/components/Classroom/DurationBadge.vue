<template>
  <span
    class="duration-badge"
    :aria-label="`预计时长: ${minutes}分钟`"
  >
    ⏱️ {{ formattedDuration }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  minutes?: number
}

const props = withDefaults(defineProps<Props>(), {
  minutes: 5
})

const formattedDuration = computed(() => {
  if (props.minutes < 60) {
    return `${props.minutes}分钟`
  }
  const hours = Math.floor(props.minutes / 60)
  const remainingMinutes = props.minutes % 60
  return remainingMinutes > 0
    ? `${hours}小时${remainingMinutes}分`
    : `${hours}小时`
})
</script>

<style scoped>
.duration-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
  background: #F3F4F6;
  color: #6B7280;
}
</style>
