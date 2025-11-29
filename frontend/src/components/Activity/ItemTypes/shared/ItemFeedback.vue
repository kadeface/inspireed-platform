<template>
  <div v-if="answer" class="feedback-info">
    <div v-if="answer.correct" class="feedback-correct">
      ✓ 回答正确！正确答案：{{ formatCorrectAnswer(answer.correctAnswer) }}
    </div>
    <div v-else class="feedback-wrong">
      ✗ 回答错误。正确答案：{{ formatCorrectAnswer(answer.correctAnswer) }}
    </div>
    <div v-if="showScore && answer.score !== undefined && points !== undefined" class="feedback-score">
      得分：{{ answer.score }} / {{ points }} 分
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  answer?: {
    correct?: boolean
    correctAnswer?: string | string[]
    score?: number
    [key: string]: any
  } | null
  points?: number
  showScore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  answer: null,
  points: undefined,
  showScore: true,
})

function formatCorrectAnswer(correctAnswer?: string | string[]): string {
  if (!correctAnswer) return ''
  
  if (Array.isArray(correctAnswer)) {
    return correctAnswer.join('、')
  }
  
  return String(correctAnswer)
}
</script>

<style scoped>
.feedback-info {
  @apply mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200;
}

.feedback-correct {
  @apply text-green-700 font-semibold mb-2;
}

.feedback-wrong {
  @apply text-red-700 font-semibold mb-2;
}

.feedback-score {
  @apply text-gray-600 text-sm mt-2;
}
</style>

