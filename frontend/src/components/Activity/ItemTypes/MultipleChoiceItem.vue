<template>
  <div class="multiple-choice-item space-y-2">
    <label
      v-for="option in item.config.options"
      :key="option.id"
      class="option-label"
      :class="{
        'option-correct': isSubmitted && isCorrectOption(option.id),
        'option-selected': isSelected(option.id),
        'option-wrong': isSubmitted && isSelected(option.id) && !isCorrectOption(option.id)
      }"
    >
      <input
        :value="option.id"
        type="checkbox"
        :checked="isSelected(option.id)"
        :disabled="isSubmitted"
        @change="handleChange(option.id, $event)"
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
import type { MultipleChoiceItem } from '@/types/activity'
import ItemFeedback from './shared/ItemFeedback.vue'

interface Props {
  item: MultipleChoiceItem
  modelValue: string[] | undefined
  isSubmitted: boolean
  answerData?: {
    correct?: boolean
    correctAnswer?: string | string[]
    score?: number
    [key: string]: any
  } | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'change': [itemId: string]
}>()

function isSelected(optionId: string): boolean {
  return Array.isArray(props.modelValue) && props.modelValue.includes(optionId)
}

function isCorrectOption(optionId: string): boolean {
  if (!props.answerData || !props.answerData.correctAnswer) return false
  
  // 多选题的正确答案可能是逗号分隔的字符串或数组
  let correctAnswers: string[] = []
  
  if (Array.isArray(props.answerData.correctAnswer)) {
    correctAnswers = props.answerData.correctAnswer
  } else {
    correctAnswers = props.answerData.correctAnswer.split(',').map((s: string) => s.trim())
  }
  
  return correctAnswers.some((text: string) => {
    // 找到对应的选项
    const option = props.item.config.options.find((opt) => opt.id === optionId)
    return option && (text === option.text || text === option.id || text === optionId)
  })
}

function handleChange(optionId: string, event: Event) {
  const checked = (event.target as HTMLInputElement).checked
  const currentValue = Array.isArray(props.modelValue) ? [...props.modelValue] : []
  
  if (checked) {
    if (!currentValue.includes(optionId)) {
      currentValue.push(optionId)
    }
  } else {
    const index = currentValue.indexOf(optionId)
    if (index > -1) {
      currentValue.splice(index, 1)
    }
  }
  
  emit('update:modelValue', currentValue)
  emit('change', props.item.id)
}
</script>

<style scoped>
.multiple-choice-item {
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

