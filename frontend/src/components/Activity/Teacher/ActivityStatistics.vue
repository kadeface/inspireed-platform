<template>
  <div class="statistics-panel">
    <!-- 标题 -->
    <div class="panel-header">
      <h3 class="panel-title">📊 活动统计</h3>
      <button @click="refreshStatistics" class="btn-refresh" :disabled="loading">
        <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span v-if="!loading">刷新</span>
      </button>
    </div>

    <div v-if="loading && !statistics" class="loading-state">
      <div class="spinner"></div>
      <p>加载统计数据...</p>
    </div>

    <div v-else-if="statistics" class="statistics-content">
      <!-- 提交概况 -->
      <div class="stats-section">
        <h4 class="stats-title">📋 提交概况</h4>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.totalStudents }}</div>
            <div class="stat-label">总学生数</div>
          </div>
          <div class="stat-card stat-draft">
            <div class="stat-value">{{ statistics.draftCount }}</div>
            <div class="stat-label">草稿</div>
          </div>
          <div class="stat-card stat-submitted">
            <div class="stat-value">{{ statistics.submittedCount }}</div>
            <div class="stat-label">已提交</div>
          </div>
          <div class="stat-card stat-graded">
            <div class="stat-value">{{ statistics.gradedCount }}</div>
            <div class="stat-label">已评分</div>
          </div>
        </div>

        <!-- 提交率 -->
        <div class="progress-section">
          <div class="flex justify-between text-sm mb-2">
            <span>提交率</span>
            <span class="font-semibold">{{ submissionRate }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill bg-green-500" :style="{ width: `${submissionRate}%` }"></div>
          </div>
        </div>
      </div>

      <!-- 成绩统计 -->
      <div v-if="statistics.averageScore !== null" class="stats-section">
        <h4 class="stats-title">💯 成绩统计</h4>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.averageScore?.toFixed(1) || '-' }}</div>
            <div class="stat-label">平均分</div>
          </div>
          <div class="stat-card stat-success">
            <div class="stat-value">{{ statistics.highestScore?.toFixed(1) || '-' }}</div>
            <div class="stat-label">最高分</div>
          </div>
          <div class="stat-card stat-danger">
            <div class="stat-value">{{ statistics.lowestScore?.toFixed(1) || '-' }}</div>
            <div class="stat-label">最低分</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.medianScore?.toFixed(1) || '-' }}</div>
            <div class="stat-label">中位数</div>
          </div>
        </div>

        <!-- 成绩分布图（简化版） -->
        <div class="score-distribution">
          <h5 class="text-sm font-semibold mb-3">成绩分布</h5>
          <div class="distribution-bars">
            <div class="distribution-bar">
              <div class="bar-label">优秀(90-100)</div>
              <div class="bar-container">
                <div class="bar-fill bg-green-500" :style="{ width: `${getScoreDistribution('excellent')}%` }"></div>
              </div>
              <div class="bar-value">{{ getScoreCount('excellent') }}</div>
            </div>
            <div class="distribution-bar">
              <div class="bar-label">良好(80-89)</div>
              <div class="bar-container">
                <div class="bar-fill bg-blue-500" :style="{ width: `${getScoreDistribution('good')}%` }"></div>
              </div>
              <div class="bar-value">{{ getScoreCount('good') }}</div>
            </div>
            <div class="distribution-bar">
              <div class="bar-label">及格(60-79)</div>
              <div class="bar-container">
                <div class="bar-fill bg-yellow-500" :style="{ width: `${getScoreDistribution('pass')}%` }"></div>
              </div>
              <div class="bar-value">{{ getScoreCount('pass') }}</div>
            </div>
            <div class="distribution-bar">
              <div class="bar-label">不及格(&lt;60)</div>
              <div class="bar-container">
                <div class="bar-fill bg-red-500" :style="{ width: `${getScoreDistribution('fail')}%` }"></div>
              </div>
              <div class="bar-value">{{ getScoreCount('fail') }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 时间统计 -->
      <div v-if="statistics.averageTimeSpent" class="stats-section">
        <h4 class="stats-title">⏱️ 时间统计</h4>
        <div class="stat-card">
          <div class="stat-value">{{ formatTime(statistics.averageTimeSpent) }}</div>
          <div class="stat-label">平均用时</div>
        </div>
      </div>

      <!-- 互评统计 -->
      <div v-if="statistics.peerReviewCount > 0" class="stats-section">
        <h4 class="stats-title">🤝 互评统计</h4>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.peerReviewCount }}</div>
            <div class="stat-label">互评总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.avgPeerReviewScore?.toFixed(1) || '-' }}</div>
            <div class="stat-label">平均互评分</div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions-section">
        <button @click="viewSubmissions" class="btn-primary">
          📝 查看所有提交
        </button>
        <button @click="exportData" class="btn-secondary">
          📥 导出数据
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>暂无统计数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { ActivityStatistics } from '../../../types/activity'
import activityService from '../../../services/activity'

interface Props {
  cellId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  viewSubmissions: []
  export: []
}>()

const statistics = ref<ActivityStatistics | null>(null)
const loading = ref(false)

// 计算提交率
const submissionRate = computed(() => {
  if (!statistics.value || statistics.value.totalStudents === 0) return 0
  return Math.round(
    ((statistics.value.submittedCount + statistics.value.gradedCount) / statistics.value.totalStudents) * 100
  )
})

// 获取成绩分布（模拟数据，实际需要从后端获取详细数据）
function getScoreDistribution(level: 'excellent' | 'good' | 'pass' | 'fail'): number {
  // TODO: 从 itemStatistics 中获取实际分布数据
  const count = getScoreCount(level)
  const total = statistics.value?.gradedCount || 1
  return Math.round((count / total) * 100)
}

function getScoreCount(level: 'excellent' | 'good' | 'pass' | 'fail'): number {
  // TODO: 从 itemStatistics 中计算实际数量
  if (!statistics.value) return 0
  
  // 临时模拟数据
  const total = statistics.value.gradedCount
  if (level === 'excellent') return Math.floor(total * 0.3)
  if (level === 'good') return Math.floor(total * 0.4)
  if (level === 'pass') return Math.floor(total * 0.2)
  return Math.floor(total * 0.1)
}

// 格式化时间
function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}分${remainingSeconds}秒`
}

// 刷新统计数据
async function refreshStatistics() {
  loading.value = true
  try {
    statistics.value = await activityService.getStatistics(props.cellId)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

// 查看提交列表
function viewSubmissions() {
  emit('viewSubmissions')
}

// 导出数据
async function exportData() {
  try {
    const blob = await activityService.exportSubmissions(props.cellId, 'csv')
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `activity-${props.cellId}-submissions.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed:', error)
    alert('导出失败，请重试')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  refreshStatistics()
})
</script>

<style scoped>
.statistics-panel {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.panel-header {
  @apply flex items-center justify-between mb-6 pb-4 border-b border-gray-200;
}

.panel-title {
  @apply text-xl font-bold text-gray-900;
}

.btn-refresh {
  @apply flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-12;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin;
}

.statistics-content {
  @apply space-y-6;
}

.stats-section {
  @apply pb-6 border-b border-gray-100 last:border-b-0;
}

.stats-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.stats-grid {
  @apply grid grid-cols-2 md:grid-cols-4 gap-4;
}

.stat-card {
  @apply bg-gray-50 rounded-lg p-4 text-center border-2 border-gray-200;
}

.stat-card.stat-draft {
  @apply bg-gray-50 border-gray-300;
}

.stat-card.stat-submitted {
  @apply bg-blue-50 border-blue-300;
}

.stat-card.stat-graded {
  @apply bg-green-50 border-green-300;
}

.stat-card.stat-success {
  @apply bg-green-50 border-green-300;
}

.stat-card.stat-danger {
  @apply bg-red-50 border-red-300;
}

.stat-value {
  @apply text-3xl font-bold text-gray-900 mb-1;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.progress-section {
  @apply mt-4;
}

.progress-bar {
  @apply w-full h-4 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full transition-all duration-300;
}

.score-distribution {
  @apply mt-6 bg-gray-50 rounded-lg p-4;
}

.distribution-bars {
  @apply space-y-3;
}

.distribution-bar {
  @apply grid grid-cols-12 gap-2 items-center;
}

.bar-label {
  @apply col-span-3 text-sm text-gray-700;
}

.bar-container {
  @apply col-span-8 h-6 bg-gray-200 rounded-full overflow-hidden;
}

.bar-fill {
  @apply h-full transition-all duration-300;
}

.bar-value {
  @apply col-span-1 text-sm text-gray-700 text-right;
}

.actions-section {
  @apply flex gap-3 pt-4;
}

.btn-primary {
  @apply flex-1 px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors;
}

.btn-secondary {
  @apply flex-1 px-4 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors;
}

.empty-state {
  @apply text-center py-12 text-gray-500;
}
</style>

