<template>
  <div class="single-choice-item space-y-2">
    <label
      v-for="option in item.config.options"
      :key="option.id"
      class="option-label"
      :class="{
        'option-correct': isSubmitted && isCorrectOption(option.id),
        'option-selected': modelValue === option.id,
        'option-wrong': isSubmitted && modelValue === option.id && !isCorrect
      }"
    >
      <input
        :value="option.id"
        type="radio"
        :name="`item-${item.id}`"
        :checked="modelValue === option.id"
        :disabled="isSubmitted"
        @change="handleChange(option.id)"
      />
      <span>{{ option.text }}</span>
      <span v-if="isSubmitted && isCorrectOption(option.id)" class="correct-badge">
        ✓ 正确答案
      </span>
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
import type { SingleChoiceItem } from '@/types/activity'
import ItemFeedback from './shared/ItemFeedback.vue'

interface Props {
  item: SingleChoiceItem
  modelValue: string | undefined
  isSubmitted: boolean
  answerData?: {
    correct?: boolean
    correctAnswer?: string
    correctAnswerId?: string
    score?: number
    [key: string]: any
  } | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [itemId: string]
}>()

const isCorrect = computed(() => props.answerData?.correct ?? false)

function isCorrectOption(optionId: string): boolean {
  if (!props.answerData || typeof props.answerData !== 'object') return false
  
  // 优先使用 correctAnswerId（如果存在）
  if (props.answerData.correctAnswerId) {
    return String(props.answerData.correctAnswerId) === String(optionId)
  }
  
  // 否则比较选项文本或ID
  if (props.answerData.correctAnswer) {
    const option = props.item.config.options.find((opt) => opt.id === optionId)
    if (!option) return false
    return (
      props.answerData.correctAnswer === option.text ||
      props.answerData.correctAnswer === option.id
    )
  }
  
  return false
}

function handleChange(optionId: string) {
  emit('update:modelValue', optionId)
  emit('change', props.item.id)
}
</script>

<style scoped>
.single-choice-item {
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

.correct-badge {
  @apply ml-auto px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded;
}
</style>

