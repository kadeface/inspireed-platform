<template>
  <div class="peer-review-assign">
    <div class="assign-card">
      <h3 class="card-title">🤝 分配互评任务</h3>
      
      <div class="info-banner">
        <p class="text-sm text-gray-700">
          互评可以让学生互相学习，提高评价能力。系统会自动分配评价任务。
        </p>
      </div>

      <!-- 提交统计 -->
      <div class="stats-section">
        <div class="stat-item">
          <span class="stat-label">已提交作业数</span>
          <span class="stat-value">{{ submittedCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">可分配互评</span>
          <span class="stat-value">{{ canAssignPeerReview ? '✅ 是' : '❌ 否' }}</span>
        </div>
      </div>

      <!-- 配置选项 -->
      <div class="config-section">
        <div class="form-group">
          <label class="form-label">
            每个学生需要评价的作品数量 *
          </label>
          <input
            v-model.number="reviewsPerStudent"
            type="number"
            min="1"
            max="5"
            class="form-input"
          />
          <p class="form-hint">
            建议 2-3 份，太多会增加学生负担
          </p>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input v-model="isAnonymous" type="checkbox" />
            <span>匿名互评（学生看不到评价者姓名）</span>
          </label>
        </div>
      </div>

      <!-- 分配预览 -->
      <div v-if="canAssignPeerReview" class="preview-section">
        <h4 class="preview-title">分配预览</h4>
        <ul class="preview-list">
          <li>将为 {{ submittedCount }} 名学生分配互评任务</li>
          <li>每人需评价 {{ reviewsPerStudent }} 份作业</li>
          <li>总计生成 {{ submittedCount * reviewsPerStudent }} 个互评任务</li>
          <li>{{ isAnonymous ? '匿名模式' : '实名模式' }}</li>
        </ul>
      </div>

      <!-- 警告 -->
      <div v-if="!canAssignPeerReview" class="warning-banner">
        ⚠️ 至少需要 {{ reviewsPerStudent + 1 }} 份提交才能进行互评
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <button @click="emit('close')" class="btn-secondary">
          取消
        </button>
        <button
          @click="handleAssign"
          class="btn-primary"
          :disabled="!canAssignPeerReview || assigning"
        >
          {{ assigning ? '分配中...' : '确认分配' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import activityService from '../../../services/activity'

interface Props {
  cellId: number
  lessonId: number
  submittedCount: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  assigned: [count: number]
}>()

const reviewsPerStudent = ref(2)
const isAnonymous = ref(true)
const assigning = ref(false)

const canAssignPeerReview = computed(() => {
  return props.submittedCount >= reviewsPerStudent.value + 1
})

async function handleAssign() {
  if (!canAssignPeerReview.value) return

  if (!confirm(`确定要分配互评任务吗？\n\n将为 ${props.submittedCount} 名学生各分配 ${reviewsPerStudent.value} 份作业进行互评。`)) {
    return
  }

  try {
    assigning.value = true
    const result = await activityService.assignPeerReviews({
      cellId: props.cellId,
      lessonId: props.lessonId,
      reviewsPerStudent: reviewsPerStudent.value,
      isAnonymous: isAnonymous.value,
    })
    
    alert(`✅ 互评任务分配成功！\n共分配了 ${result.assigned_count} 个互评任务。`)
    emit('assigned', result.assigned_count)
  } catch (error: any) {
    console.error('Assign peer review failed:', error)
    alert('分配失败：' + (error.response?.data?.detail || error.message))
  } finally {
    assigning.value = false
  }
}
</script>

<style scoped>
.peer-review-assign {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4;
}

.assign-card {
  @apply bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 space-y-6;
}

.card-title {
  @apply text-2xl font-bold text-gray-900;
}

.info-banner {
  @apply px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg;
}

.stats-section {
  @apply grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg;
}

.stat-item {
  @apply flex flex-col;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.config-section {
  @apply space-y-4;
}

.form-group {
  @apply space-y-2;
}

.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.form-input {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.form-hint {
  @apply text-xs text-gray-500;
}

.checkbox-label {
  @apply flex items-center gap-2 text-sm text-gray-700 cursor-pointer;
}

.checkbox-label input {
  @apply w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500;
}

.preview-section {
  @apply bg-green-50 border border-green-200 rounded-lg p-4;
}

.preview-title {
  @apply text-sm font-semibold text-gray-800 mb-2;
}

.preview-list {
  @apply list-disc list-inside space-y-1 text-sm text-gray-700;
}

.warning-banner {
  @apply px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800;
}

.actions {
  @apply flex justify-end gap-3;
}

.btn-primary {
  @apply px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors;
}
</style>

