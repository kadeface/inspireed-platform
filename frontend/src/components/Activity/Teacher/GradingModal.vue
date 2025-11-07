<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <!-- 标题 -->
      <div class="modal-header">
        <h3 class="modal-title">评分 - {{ submission.studentName }}</h3>
        <button @click="emit('close')" class="modal-close">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 学生答案 -->
      <div class="modal-body">
        <!-- 提交信息 -->
        <div class="info-section">
          <div class="info-row">
            <span class="info-label">提交时间:</span>
            <span>{{ formatDateTime(submission.submittedAt) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">用时:</span>
            <span>{{ submission.timeSpent ? formatTime(submission.timeSpent) : '-' }}</span>
          </div>
          <div v-if="submission.isLate" class="info-row">
            <span class="late-warning">⚠️ 迟交</span>
          </div>
        </div>

        <!-- 题目和答案 -->
        <div class="answers-section">
          <h4 class="section-title">学生答案</h4>
          <div
            v-for="(item, index) in activity.items"
            :key="item.id"
            class="answer-item"
          >
            <div class="answer-header">
              <span class="answer-number">{{ index + 1 }}.</span>
              <span class="font-medium">{{ item.question }}</span>
              <span v-if="item.points" class="points-badge">{{ item.points }}分</span>
            </div>

            <!-- 学生答案 -->
            <div class="answer-content">
              <div v-if="submission.responses[item.id]" class="student-answer">
                <!-- 选择题答案 -->
                <div v-if="item.type === 'single-choice' || item.type === 'multiple-choice'">
                  <p class="answer-label">学生答案:</p>
                  <p class="answer-text">{{ getChoiceAnswerText(item, submission.responses[item.id]) }}</p>
                  <p v-if="submission.responses[item.id].correct !== undefined" class="mt-2">
                    <span v-if="submission.responses[item.id].correct" class="text-green-600 font-semibold">✓ 正确</span>
                    <span v-else class="text-red-600 font-semibold">✗ 错误</span>
                  </p>
                </div>

                <!-- 文本答案 -->
                <div v-else-if="item.type === 'short-answer' || item.type === 'long-answer'">
                  <p class="answer-label">学生答案:</p>
                  <div class="answer-text-box">{{ submission.responses[item.id].text || submission.responses[item.id] }}</div>
                </div>

                <!-- 量表答案 -->
                <div v-else-if="item.type === 'scale'">
                  <p class="answer-label">评分:</p>
                  <p class="answer-text">{{ submission.responses[item.id].value || submission.responses[item.id] }} 分</p>
                </div>

                <!-- 其他类型 -->
                <div v-else>
                  <p class="answer-label">答案:</p>
                  <pre class="answer-text-box">{{ JSON.stringify(submission.responses[item.id], null, 2) }}</pre>
                </div>

                <!-- 单题评分 -->
                <div v-if="item.points" class="item-grading">
                  <label class="grading-label">得分:</label>
                  <input
                    v-model.number="itemScores[item.id]"
                    type="number"
                    :max="item.points"
                    min="0"
                    step="0.5"
                    class="grading-input"
                    :placeholder="`满分 ${item.points}`"
                  />
                </div>
              </div>
              <div v-else class="no-answer">
                未作答
              </div>
            </div>
          </div>
        </div>

        <!-- 总体评分 -->
        <div class="grading-section">
          <h4 class="section-title">总体评分</h4>
          
          <div class="form-group">
            <label class="form-label">总分 *</label>
            <div class="score-input-group">
              <input
                v-model.number="totalScore"
                type="number"
                :max="activity.grading.totalPoints"
                min="0"
                step="0.5"
                class="score-input"
                placeholder="输入总分"
              />
              <span class="score-max">/ {{ activity.grading.totalPoints }}</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">教师反馈</label>
            <textarea
              v-model="feedback"
              class="feedback-textarea"
              rows="4"
              placeholder="请输入对学生作业的评价和建议..."
            />
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="modal-footer">
        <button @click="emit('close')" class="btn-secondary">
          取消
        </button>
        <button @click="handleSaveGrade" class="btn-primary" :disabled="!totalScore">
          保存评分
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { ActivityCellContent, ActivityItem } from '../../../types/activity'
import activityService from '../../../services/activity'

interface Props {
  submission: any
  activity: ActivityCellContent
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  graded: []
}>()

const totalScore = ref<number>(props.submission.score || 0)
const feedback = ref(props.submission.teacherFeedback || '')
const itemScores = ref<Record<string, number>>({})

// 获取选择题答案文本
function getChoiceAnswerText(item: ActivityItem, answer: any): string {
  if (item.type === 'single-choice') {
    const option = item.config.options.find(opt => opt.id === answer.answer || opt.id === answer)
    return option?.text || answer
  } else if (item.type === 'multiple-choice') {
    const answers = answer.answer || answer
    const selectedOptions = item.config.options.filter(opt => answers.includes(opt.id))
    return selectedOptions.map(opt => opt.text).join(', ')
  }
  return ''
}

// 格式化时间
function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}分${secs}秒`
}

// 保存评分
async function handleSaveGrade() {
  if (!totalScore.value) {
    alert('请输入总分')
    return
  }

  try {
    await activityService.gradeSubmission(props.submission.id, {
      score: totalScore.value,
      teacherFeedback: feedback.value,
      itemScores: itemScores.value,
    })
    alert('评分成功')
    emit('graded')
  } catch (error) {
    console.error('Grade failed:', error)
    alert('评分失败，请重试')
  }
}

// 初始化分项分数
onMounted(() => {
  props.activity.items.forEach(item => {
    if (item.points && props.submission.responses[item.id]?.score !== undefined) {
      itemScores.value[item.id] = props.submission.responses[item.id].score
    }
  })
})
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col;
}

.modal-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.modal-title {
  @apply text-xl font-bold text-gray-900;
}

.modal-close {
  @apply text-gray-400 hover:text-gray-600 transition-colors;
}

.modal-body {
  @apply p-6 overflow-y-auto flex-1 space-y-6;
}

.modal-footer {
  @apply flex items-center justify-end gap-3 p-6 border-t border-gray-200;
}

.info-section {
  @apply bg-gray-50 rounded-lg p-4 space-y-2;
}

.info-row {
  @apply flex items-center gap-2 text-sm;
}

.info-label {
  @apply font-medium text-gray-700;
}

.late-warning {
  @apply text-red-600 font-semibold;
}

.section-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.answers-section {
  @apply space-y-4;
}

.answer-item {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.answer-header {
  @apply flex items-center gap-2 mb-3 pb-2 border-b border-gray-100;
}

.answer-number {
  @apply text-lg font-bold text-gray-900;
}

.points-badge {
  @apply ml-auto px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded;
}

.answer-content {
  @apply space-y-3;
}

.student-answer {
  @apply space-y-2;
}

.answer-label {
  @apply text-sm font-medium text-gray-700;
}

.answer-text {
  @apply text-gray-900;
}

.answer-text-box {
  @apply p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 whitespace-pre-wrap;
}

.no-answer {
  @apply text-gray-400 italic;
}

.item-grading {
  @apply flex items-center gap-3 mt-3 pt-3 border-t border-gray-100;
}

.grading-label {
  @apply text-sm font-medium text-gray-700;
}

.grading-input {
  @apply w-24 px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.grading-section {
  @apply bg-blue-50 border border-blue-200 rounded-lg p-4;
}

.form-group {
  @apply mb-4;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 mb-2;
}

.score-input-group {
  @apply flex items-center gap-2;
}

.score-input {
  @apply w-32 px-4 py-2 border border-gray-300 rounded-lg text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.score-max {
  @apply text-lg font-medium text-gray-600;
}

.feedback-textarea {
  @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none;
}

.btn-primary {
  @apply px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors;
}
</style>

