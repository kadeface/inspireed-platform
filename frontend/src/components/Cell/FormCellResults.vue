<template>
  <div class="form-cell-results">
    <div class="results-header">
      <h3 class="text-lg font-semibold text-gray-900">投票结果</h3>
      <div class="results-stats">
        <span class="stat-item">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          {{ totalResponses }} 人参与
        </span>
        <span class="stat-item">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          {{ responseRate.toFixed(1) }}% 响应率
        </span>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p class="text-gray-500 mt-3">加载结果中...</p>
    </div>

    <!-- 无数据 -->
    <div v-else-if="!results || results.option_stats.length === 0" class="empty-state">
      <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-500 mt-3">暂无投票结果</p>
    </div>

    <!-- 单选/多选结果 -->
    <div v-else-if="cellType !== 'ranking'" class="results-list">
      <div
        v-for="stat in sortedStats"
        :key="stat.option_id"
        class="result-item"
      >
        <div class="result-header">
          <span class="option-text">{{ stat.text }}</span>
          <span class="option-count">{{ stat.count }} 票 ({{ stat.percentage.toFixed(1) }}%)</span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${stat.percentage}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 排序题结果 -->
    <div v-else class="ranking-results">
      <table class="ranking-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>选项</th>
            <th>平均排名</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(stat, index) in sortedRankingStats"
            :key="stat.option_id"
          >
            <td>
              <span :class="['rank-badge', getRankClass(index)]">
                {{ index + 1 }}
              </span>
            </td>
            <td>{{ stat.text }}</td>
            <td>
              <span class="rank-score">
                {{ stat.average_rank?.toFixed(2) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 教师操作 -->
    <div v-if="isTeacher" class="teacher-actions">
      <button @click="handleExport" class="btn-export">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        导出结果
      </button>
      <button @click="handleRefresh" class="btn-refresh" :disabled="isRefreshing">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ isRefreshing ? '刷新中...' : '刷新' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFormStore } from '../../store/form'
import type { Cell } from '../../types/cell'
import type { OptionStats } from '../../types/form'

interface Props {
  cell: Cell
  isTeacher: boolean
}

const props = defineProps<Props>()

// Store
const formStore = useFormStore()

// 状态
const isLoading = ref(false)
const isRefreshing = ref(false)
const results = ref(formStore.results)

// 计算属性
const cellType = computed(() => props.cell.content?.cell_type || 'single_choice')
const totalResponses = computed(() => results.value?.total_responses || 0)
const responseRate = computed(() => results.value?.response_rate || 0)

const sortedStats = computed(() => {
  if (!results.value?.option_stats) return []
  return [...results.value.option_stats].sort((a, b) => (b.count || 0) - (a.count || 0))
})

const sortedRankingStats = computed(() => {
  if (!results.value?.option_stats) return []
  return [...results.value.option_stats].sort((a, b) =>
    (a.average_rank || 0) - (b.average_rank || 0)
  )
})

// 方法
function getRankClass(index: number): string {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return 'rank-normal'
}

async function handleRefresh() {
  isRefreshing.value = true
  try {
    await formStore.fetchResults(props.cell.id)
    results.value = formStore.results
  } catch (error) {
    console.error('刷新结果失败:', error)
  } finally {
    isRefreshing.value = false
  }
}

function handleExport() {
  // TODO: 实现导出功能
  console.log('导出结果', results.value)
  alert('导出功能开发中...')
}

// 生命周期
onMounted(async () => {
  isLoading.value = true
  try {
    await formStore.fetchResults(props.cell.id)
    results.value = formStore.results
  } catch (error) {
    console.error('加载结果失败:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.form-cell-results {
  @apply space-y-4;
}

.results-header {
  @apply flex justify-between items-center;
}

.results-stats {
  @apply flex gap-3;
}

.stat-item {
  @apply inline-flex items-center text-sm text-gray-600;
}

/* 加载状态 */
.loading-state {
  @apply flex flex-col items-center justify-center h-48;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin;
}

/* 空状态 */
.empty-state {
  @apply flex flex-col items-center justify-center h-48;
}

/* 结果列表 */
.results-list {
  @apply space-y-3;
}

.result-item {
  @apply space-y-2;
}

.result-header {
  @apply flex justify-between items-center;
}

.option-text {
  @apply font-medium text-gray-900;
}

.option-count {
  @apply text-sm text-gray-600;
}

.progress-bar {
  @apply w-full h-3 bg-gray-100 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-500 rounded-full transition-all duration-500;
}

/* 排序结果 */
.ranking-results {
  @apply mt-4;
}

.ranking-table {
  @apply w-full;
}

.ranking-table thead {
  @apply bg-gray-50;
}

.ranking-table th {
  @apply px-4 py-2 text-left text-sm font-medium text-gray-700;
}

.ranking-table td {
  @apply px-4 py-3 text-sm text-gray-900 border-t border-gray-200;
}

.rank-badge {
  @apply inline-flex items-center justify-center w-6 h-6 text-xs font-bold rounded-full;
}

.rank-gold {
  @apply bg-yellow-100 text-yellow-700;
}

.rank-silver {
  @apply bg-gray-100 text-gray-700;
}

.rank-bronze {
  @apply bg-orange-100 text-orange-700;
}

.rank-normal {
  @apply bg-blue-100 text-blue-700;
}

.rank-score {
  @apply font-mono font-medium;
}

/* 教师操作 */
.teacher-actions {
  @apply flex gap-2 pt-4 border-t border-gray-200;
}

.btn-export,
.btn-refresh {
  @apply inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
