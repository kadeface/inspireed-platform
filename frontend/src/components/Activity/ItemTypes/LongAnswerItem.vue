<template>
  <div class="long-answer-item">
    <textarea
      :value="modelValue"
      class="answer-textarea"
      :rows="8"
      :placeholder="item.config.placeholder || '请在此输入答案'"
      :minlength="item.config.minLength"
      :maxlength="item.config.maxLength"
      :disabled="isSubmitted"
      @input="handleInput($event)"
    />
    <p v-if="item.config.maxLength" class="text-xs text-gray-500 mt-1">
      {{ (modelValue?.length || 0) }} / {{ item.config.maxLength }} 字
    </p>
    
    <ItemFeedback
      v-if="isSubmitted && answerData"
      :answer="answerData"
      :points="item.points"
    />
  </div>
</template>

<script setup lang="ts">
import type { LongAnswerItem } from '@/types/activity'
import ItemFeedback from './shared/ItemFeedback.vue'

interface Props {
  item: LongAnswerItem
  modelValue: string | undefined
  isSubmitted: boolean
  answerData?: {
    correct?: boolean
    score?: number
    [key: string]: any
  } | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [itemId: string]
}>()

function handleInput(event: Event) {
  const value = (event.target as HTMLTextAreaElement).value
  emit('update:modelValue', value)
  emit('change', props.item.id)
}
</script>

<style scoped>
.long-answer-item {
  @apply space-y-2;
}

.answer-textarea {
  @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.answer-textarea:disabled {
  @apply bg-gray-50 cursor-not-allowed;
}
</style>

