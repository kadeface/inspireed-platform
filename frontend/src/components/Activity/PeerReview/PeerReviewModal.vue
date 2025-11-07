<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <!-- 标题 -->
      <div class="modal-header">
        <h3 class="modal-title">🤝 互评作业</h3>
        <button @click="emit('close')" class="modal-close">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 主体内容 -->
      <div class="modal-body">
        <!-- 评价说明 -->
        <div class="instruction-banner">
          <p class="text-sm">
            请认真阅读同学的作业，根据评价标准给出客观公正的评价。
          </p>
        </div>

        <!-- 作业内容 -->
        <div class="submission-section">
          <h4 class="section-title">作业内容</h4>
          
          <!-- TODO: 显示提交的内容，需要从后端加载 -->
          <div class="submission-placeholder">
            <p class="text-gray-500">作业内容加载中...</p>
          </div>
        </div>

        <!-- 评价表单 -->
        <div class="review-form">
          <h4 class="section-title">您的评价</h4>

          <!-- 如果有评分标准（Rubric） -->
          <div v-if="hasRubric" class="rubric-section">
            <div
              v-for="item in rubricItems"
              :key="item.id"
              class="rubric-item"
            >
              <h5 class="rubric-criterion">{{ item.question }}</h5>
              <div class="rubric-levels">
                <label
                  v-for="level in item.config.levels"
                  :key="level.level"
                  class="level-option"
                >
                  <input
                    v-model="reviewData[item.id]"
                    type="radio"
                    :value="level.level"
                    :name="`rubric-${item.id}`"
                  />
                  <div class="level-content">
                    <div class="level-name">{{ level.name }}</div>
                    <div class="level-description">{{ level.description }}</div>
                    <div class="level-points">{{ level.points }} 分</div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- 简化评分（如果没有Rubric） -->
          <div v-else class="simple-grading">
            <div class="form-group">
              <label class="form-label">评分 (0-{{ maxScore }}分) *</label>
              <input
                v-model.number="simpleScore"
                type="number"
                :max="maxScore"
                min="0"
                step="0.5"
                class="score-input"
                placeholder="请输入分数"
              />
            </div>
          </div>

          <!-- 评价意见 -->
          <div class="form-group">
            <label class="form-label">评价意见</label>
            <textarea
              v-model="comment"
              class="comment-textarea"
              rows="4"
              placeholder="请写下您对这份作业的评价和建议...&#10;&#10;例如：&#10;- 优点：代码结构清晰，逻辑正确&#10;- 建议：可以添加更多注释"
            />
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="modal-footer">
        <button @click="emit('close')" class="btn-secondary">
          取消
        </button>
        <button @click="handleSubmitReview" class="btn-primary" :disabled="!canSubmit || submitting">
          {{ submitting ? '提交中...' : '提交评价' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { PeerReview, ActivityCellContent } from '../../../types/activity'
import activityService from '../../../services/activity'

interface Props {
  task: PeerReview
  activity: ActivityCellContent
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  submitted: []
}>()

const reviewData = ref<Record<string, any>>({})
const simpleScore = ref<number>(0)
const comment = ref('')
const submitting = ref(false)

// 检查是否有 Rubric 评分标准
const hasRubric = computed(() => {
  return props.activity.items.some(item => item.type === 'rubric-item')
})

// 获取 Rubric 项
const rubricItems = computed(() => {
  return props.activity.items.filter(item => item.type === 'rubric-item')
})

// 最大分数
const maxScore = computed(() => {
  return props.activity.grading.totalPoints || 100
})

// 是否可以提交
const canSubmit = computed(() => {
  if (hasRubric.value) {
    // 检查所有 Rubric 项是否都已评价
    return rubricItems.value.every(item => reviewData.value[item.id] !== undefined)
  } else {
    // 简化评分模式，需要输入分数
    return simpleScore.value > 0
  }
})

// 提交互评
async function handleSubmitReview() {
  if (!canSubmit.value) {
    alert('请完成所有评价项')
    return
  }

  try {
    submitting.value = true

    // 计算总分
    let totalScore = 0
    if (hasRubric.value) {
      // 根据 Rubric 计算分数
      rubricItems.value.forEach(item => {
        const level = reviewData.value[item.id]
        const levelConfig = item.config.levels.find(l => l.level === level)
        if (levelConfig) {
          totalScore += levelConfig.points
        }
      })
    } else {
      totalScore = simpleScore.value
    }

    // 提交互评
    await activityService.submitPeerReview(props.task.id, {
      submissionId: props.task.submissionId,
      reviewData: reviewData.value,
      score: totalScore,
      comment: comment.value,
    })

    alert('✅ 评价提交成功！感谢您的认真评价。')
    emit('submitted')
  } catch (error) {
    console.error('Submit peer review failed:', error)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // 加载已有的评价数据（如果是编辑）
  if (props.task.reviewData) {
    reviewData.value = props.task.reviewData
  }
  if (props.task.score) {
    simpleScore.value = props.task.score
  }
  if (props.task.comment) {
    comment.value = props.task.comment
  }
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

.instruction-banner {
  @apply px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg;
}

.section-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.submission-section {
  @apply bg-gray-50 rounded-lg p-4;
}

.submission-placeholder {
  @apply py-8 text-center;
}

.review-form {
  @apply space-y-6;
}

.rubric-section {
  @apply space-y-6;
}

.rubric-item {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.rubric-criterion {
  @apply text-base font-semibold text-gray-900 mb-4;
}

.rubric-levels {
  @apply space-y-2;
}

.level-option {
  @apply flex items-start gap-3 p-3 border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-all;
}

.level-option:has(input:checked) {
  @apply border-blue-500 bg-blue-50;
}

.level-content {
  @apply flex-1;
}

.level-name {
  @apply font-semibold text-gray-900 mb-1;
}

.level-description {
  @apply text-sm text-gray-600 mb-2;
}

.level-points {
  @apply text-sm font-semibold text-blue-600;
}

.simple-grading {
  @apply bg-gray-50 rounded-lg p-4;
}

.form-group {
  @apply space-y-2;
}

.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.score-input {
  @apply w-32 px-4 py-2 border border-gray-300 rounded-lg text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.comment-textarea {
  @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none;
}

.btn-primary {
  @apply px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors;
}
</style>

