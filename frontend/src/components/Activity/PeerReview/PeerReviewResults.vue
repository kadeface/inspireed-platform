<template>
  <div class="peer-review-results">
    <!-- 标题 -->
    <div class="results-header">
      <h3 class="results-title">📊 互评结果</h3>
      <button @click="loadReviews" class="btn-refresh" :disabled="loading">
        <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && reviews.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载互评结果...</p>
    </div>

    <!-- 互评统计 -->
    <div v-else-if="reviews.length > 0" class="results-content">
      <!-- 总体统计 -->
      <div class="summary-section">
        <div class="stat-card">
          <div class="stat-value">{{ reviews.length }}</div>
          <div class="stat-label">收到评价</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ averageScore.toFixed(1) }}</div>
          <div class="stat-label">平均分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ highestScore.toFixed(1) }}</div>
          <div class="stat-label">最高分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ lowestScore.toFixed(1) }}</div>
          <div class="stat-label">最低分</div>
        </div>
      </div>

      <!-- 详细评价列表 -->
      <div class="reviews-list">
        <h4 class="list-title">详细评价</h4>
        <div
          v-for="(review, index) in reviews"
          :key="review.id"
          class="review-card"
        >
          <div class="review-header">
            <div class="flex items-center gap-2">
              <span class="review-number">#{{ index + 1 }}</span>
              <span class="reviewer-name">
                {{ review.isAnonymous ? '匿名评价者' : review.reviewerName }}
              </span>
            </div>
            <div class="review-score">
              {{ review.score }} / {{ review.maxScore }}
            </div>
          </div>

          <!-- Rubric 评价详情 -->
          <div v-if="review.reviewData && Object.keys(review.reviewData).length > 0" class="review-details">
            <div
              v-for="(value, key) in review.reviewData"
              :key="key"
              class="detail-item"
            >
              <span class="detail-label">{{ key }}:</span>
              <span class="detail-value">{{ value }}</span>
            </div>
          </div>

          <!-- 评价意见 -->
          <div v-if="review.comment" class="review-comment">
            <p class="comment-label">评价意见:</p>
            <p class="comment-text">{{ review.comment }}</p>
          </div>

          <div class="review-footer">
            <span class="text-xs text-gray-500">
              {{ formatDateTime(review.completedAt) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="text-4xl mb-4">📭</div>
      <p class="text-gray-500">暂无互评结果</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { PeerReview } from '../../../types/activity'
import activityService from '../../../services/activity'

interface Props {
  submissionId: number
}

const props = defineProps<Props>()

const reviews = ref<PeerReview[]>([])
const loading = ref(false)

// 计算平均分
const averageScore = computed(() => {
  if (reviews.value.length === 0) return 0
  const total = reviews.value.reduce((sum, r) => sum + (r.score || 0), 0)
  return total / reviews.value.length
})

// 最高分
const highestScore = computed(() => {
  if (reviews.value.length === 0) return 0
  return Math.max(...reviews.value.map(r => r.score || 0))
})

// 最低分
const lowestScore = computed(() => {
  if (reviews.value.length === 0) return 0
  return Math.min(...reviews.value.map(r => r.score || 0))
})

// 格式化时间
function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载互评结果
async function loadReviews() {
  loading.value = true
  try {
    reviews.value = await activityService.getSubmissionPeerReviews(props.submissionId)
  } catch (error) {
    console.error('Failed to load peer reviews:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.peer-review-results {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.results-header {
  @apply flex items-center justify-between mb-6 pb-4 border-b border-gray-200;
}

.results-title {
  @apply text-xl font-bold text-gray-900;
}

.btn-refresh {
  @apply flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-12;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-3;
}

.results-content {
  @apply space-y-6;
}

.summary-section {
  @apply grid grid-cols-2 md:grid-cols-4 gap-4;
}

.stat-card {
  @apply bg-blue-50 border border-blue-200 rounded-lg p-4 text-center;
}

.stat-value {
  @apply text-3xl font-bold text-gray-900 mb-1;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.list-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.reviews-list {
  @apply space-y-4;
}

.review-card {
  @apply bg-white border border-gray-200 rounded-lg p-5 space-y-4;
}

.review-header {
  @apply flex items-center justify-between pb-3 border-b border-gray-100;
}

.review-number {
  @apply text-sm font-mono text-gray-500;
}

.reviewer-name {
  @apply text-base font-medium text-gray-900;
}

.review-score {
  @apply text-lg font-bold text-blue-600;
}

.review-details {
  @apply space-y-2 p-3 bg-gray-50 rounded-lg;
}

.detail-item {
  @apply flex items-center gap-2 text-sm;
}

.detail-label {
  @apply font-medium text-gray-700;
}

.detail-value {
  @apply text-gray-900;
}

.review-comment {
  @apply space-y-2;
}

.comment-label {
  @apply text-sm font-medium text-gray-700;
}

.comment-text {
  @apply p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 whitespace-pre-wrap;
}

.review-footer {
  @apply pt-3 border-t border-gray-100;
}

.empty-state {
  @apply flex flex-col items-center justify-center py-16 text-center;
}
</style>

