<template>
  <div class="scale-item">
    <div class="scale-labels">
      <span>{{ item.config.minLabel || '最小值' }}</span>
      <span>{{ item.config.maxLabel || '最大值' }}</span>
    </div>
    <div class="scale-options">
      <label
        v-for="value in scaleRange"
        :key="value"
        class="scale-option"
      >
        <input
          type="radio"
          :value="value"
          :name="`item-${item.id}`"
          :checked="modelValue === value"
          :disabled="isSubmitted"
          @change="handleChange(value)"
        />
        <span>{{ value }}</span>
      </label>
    </div>
    
    <ItemFeedback
      v-if="isSubmitted && answerData"
      :answer="answerData"
      :points="item.points"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ScaleItem } from '@/types/activity'
import ItemFeedback from './shared/ItemFeedback.vue'

interface Props {
  item: ScaleItem
  modelValue: number | undefined
  isSubmitted: boolean
  answerData?: {
    correct?: boolean
    score?: number
    [key: string]: any
  } | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'change': [itemId: string]
}>()

const scaleRange = computed(() => {
  const min = props.item.config.min ?? 1
  const max = props.item.config.max ?? 5
  const step = props.item.config.step ?? 1
  const range: number[] = []
  for (let i = min; i <= max; i += step) {
    range.push(i)
  }
  return range
})

function handleChange(value: number) {
  emit('update:modelValue', value)
  emit('change', props.item.id)
}
</script>

<style scoped>
.scale-item {
  @apply space-y-3;
}

.scale-labels {
  @apply flex justify-between text-sm text-gray-600;
}

.scale-options {
  @apply flex justify-between gap-2;
}

.scale-option {
  @apply flex flex-col items-center gap-1 cursor-pointer;
}

.scale-option input {
  @apply w-5 h-5;
}

.scale-option:has(input:disabled) {
  @apply opacity-75 cursor-not-allowed;
}
</style>

