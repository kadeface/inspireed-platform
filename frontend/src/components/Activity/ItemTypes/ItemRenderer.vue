<template>
  <component
    :is="componentName"
    v-if="componentName"
    :item="item"
    :model-value="modelValue"
    :is-submitted="isSubmitted"
    :answer-data="answerData"
    @update:model-value="$emit('update:modelValue', $event)"
    @change="$emit('change', $event)"
  />
  <div v-else class="placeholder">
    <p class="text-gray-500">此题型的答题界面正在开发中...</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ActivityItem } from '@/types/activity'
import SingleChoiceItem from './SingleChoiceItem.vue'
import MultipleChoiceItem from './MultipleChoiceItem.vue'
import TrueFalseItem from './TrueFalseItem.vue'
import ShortAnswerItem from './ShortAnswerItem.vue'
import LongAnswerItem from './LongAnswerItem.vue'
import ScaleItem from './ScaleItem.vue'

interface Props {
  item: ActivityItem
  modelValue: any
  isSubmitted: boolean
  answerData?: any
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
  'change': [itemId: string]
}>()

const componentMap: Record<string, any> = {
  'single-choice': SingleChoiceItem,
  'multiple-choice': MultipleChoiceItem,
  'true-false': TrueFalseItem,
  'short-answer': ShortAnswerItem,
  'long-answer': LongAnswerItem,
  'scale': ScaleItem,
  // 以下题型待实现
  // 'file-upload': FileUploadItem,
  // 'code-submission': CodeSubmissionItem,
  // 'rubric-item': RubricItem,
}

const componentName = computed(() => {
  return componentMap[props.item.type] || null
})
</script>

<style scoped>
.placeholder {
  @apply py-8 text-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300;
}
</style>

