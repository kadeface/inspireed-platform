<template>
  <div class="true-false-item space-y-2">
    <label
      class="option-label"
      :class="{
        'option-correct': isSubmitted && isCorrectAnswer(true),
        'option-selected': modelValue === true,
        'option-wrong': isSubmitted && modelValue === true && !isCorrectAnswer(true)
      }"
    >
      <input
        type="radio"
        :value="true"
        :name="`item-${item.id}`"
        :checked="modelValue === true"
        :disabled="isSubmitted"
        @change="handleChange(true)"
      />
      <span>正确</span>
    </label>
    
    <label
      class="option-label"
      :class="{
        'option-correct': isSubmitted && isCorrectAnswer(false),
        'option-selected': modelValue === false,
        'option-wrong': isSubmitted && modelValue === false && !isCorrectAnswer(false)
      }"
    >
      <input
        type="radio"
        :value="false"
        :name="`item-${item.id}`"
        :checked="modelValue === false"
        :disabled="isSubmitted"
        @change="handleChange(false)"
      />
      <span>错误</span>
    </label>
    
    <ItemFeedback
      v-if="isSubmitted && answerData"
      :answer="answerData"
      :points="item.points"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TrueFalseItem } from '@/types/activity'
import ItemFeedback from './shared/ItemFeedback.vue'

interface Props {
  item: TrueFalseItem
  modelValue: boolean | undefined
  isSubmitted: boolean
  answerData?: {
    correct?: boolean
    correctAnswer?: string | boolean
    score?: number
    [key: string]: any
  } | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'change': [itemId: string]
}>()

function isCorrectAnswer(value: boolean): boolean {
  if (!props.answerData || props.answerData.correctAnswer === undefined) return false
  
  // 处理字符串格式的正确答案（"正确"/"错误"）
  if (typeof props.answerData.correctAnswer === 'string') {
    const correctValue = props.answerData.correctAnswer === '正确' || props.answerData.correctAnswer === 'True'
    return correctValue === value
  }
  
  // 处理布尔值格式
  return props.answerData.correctAnswer === value
}

function handleChange(value: boolean) {
  emit('update:modelValue', value)
  emit('change', props.item.id)
}
</script>

<style scoped>
.true-false-item {
  @apply space-y-2;
}

.option-label {
  @apply flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors;
}

.option-label input {
  @apply mt-1;
}

.option-label:has(input:disabled) {
  @apply opacity-75 cursor-not-allowed;
}

.option-correct {
  @apply bg-green-50 border-green-300;
}

.option-selected {
  @apply bg-blue-50 border-blue-300;
}

.option-wrong {
  @apply bg-red-50 border-red-300;
}
</style>

