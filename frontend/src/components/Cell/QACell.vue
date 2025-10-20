<template>
  <div class="qa-cell cell-container p-4">
    <h3 class="text-lg font-semibold mb-3">{{ cell.title || '问答互动' }}</h3>
    
    <div v-if="cell.content.question" class="question-area mb-4">
      <div class="text-sm font-medium text-gray-700 mb-2">问题:</div>
      <div class="bg-blue-50 p-3 rounded-lg">
        {{ cell.content.question }}
      </div>
    </div>

    <div v-if="cell.content.answer" class="answer-area mb-4">
      <div class="text-sm font-medium text-gray-700 mb-2">
        回答 {{ cell.content.isAIAnswer ? '(AI)' : '' }}:
      </div>
      <div class="bg-green-50 p-3 rounded-lg">
        {{ cell.content.answer }}
      </div>
    </div>

    <div v-if="editable && !cell.content.question" class="input-area">
      <textarea
        v-model="questionInput"
        placeholder="输入你的问题..."
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows="3"
      ></textarea>
      <button
        @click="submitQuestion"
        class="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        提交问题
      </button>
    </div>

    <p class="text-sm text-gray-500 mt-4">AI问答功能开发中...</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { QACell as QACellType } from '../../types/cell'

interface Props {
  cell: QACellType
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: QACellType]
}>()

const questionInput = ref('')

function submitQuestion() {
  if (questionInput.value.trim()) {
    props.cell.content.question = questionInput.value
    emit('update', props.cell)
    questionInput.value = ''
  }
}
</script>

