<template>
  <div class="peer-review-task">
    <!-- 任务头部 -->
    <div class="task-header">
      <h3 class="task-title">🤝 互评任务</h3>
      <div class="task-status">
        <span class="text-sm text-gray-600">
          已完成 {{ completedCount }} / {{ totalCount }}
        </span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载互评任务...</p>
    </div>

    <!-- 任务列表 -->
    <div v-else-if="tasks.length > 0" class="tasks-list">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="task-card"
        :class="{ 'task-completed': task.status === 'completed' }"
      >
        <div class="task-card-header">
          <div class="flex items-center gap-2">
            <span class="task-number">#{{ task.id }}</span>
            <span :class="getStatusBadgeClass(task.status)">
              {{ getStatusLabel(task.status) }}
            </span>
          </div>
          <span v-if="task.completedAt" class="text-xs text-gray-500">
            完成于 {{ formatDateTime(task.completedAt) }}
          </span>
        </div>

        <div class="task-card-body">
          <p class="task-description">
            {{ isAnonymous ? '请评价以下作业' : `评价 ${task.studentName} 的作业` }}
          </p>

          <!-- 查看作业按钮 -->
          <button
            v-if="task.status === 'pending'"
            @click="startReview(task)"
            class="btn-start-review"
          >
            开始评价
          </button>

          <!-- 已完成的显示评分 -->
          <div v-else-if="task.status === 'completed' && task.score" class="completed-info">
            <span class="text-sm text-gray-600">您的评分:</span>
            <span class="font-semibold text-lg">{{ task.score }} / {{ task.maxScore }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="text-4xl mb-4">📭</div>
      <p class="text-gray-500">暂无互评任务</p>
    </div>

    <!-- 互评模态框 -->
    <PeerReviewModal
      v-if="reviewingTask"
      :task="reviewingTask"
      :activity="activity"
      @close="reviewingTask = null"
      @submitted="handleReviewSubmitted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { PeerReview } from '../../../types/activity'
import type { ActivityCellContent } from '../../../types/activity'
import activityService from '../../../services/activity'
import PeerReviewModal from './PeerReviewModal.vue'

interface Props {
  cellId: number
  activity: ActivityCellContent
  isAnonymous?: boolean
}

withDefaults(defineProps<Props>(), {
  isAnonymous: true,
})

const tasks = ref<PeerReview[]>([])
const loading = ref(false)
const reviewingTask = ref<PeerReview | null>(null)

const totalCount = computed(() => tasks.value.length)
const completedCount = computed(() => tasks.value.filter(t => t.status === 'completed').length)

// 获取状态标签
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: '待评价',
    in_progress: '评价中',
    completed: '已完成',
  }
  return labels[status] || status
}

// 获取状态徽章样式
function getStatusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    pending: 'status-badge status-pending',
    in_progress: 'status-badge status-progress',
    completed: 'status-badge status-completed',
  }
  return classes[status] || 'status-badge'
}

// 格式化时间
function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 开始评价
function startReview(task: PeerReview) {
  reviewingTask.value = task
}

// 评价提交完成
function handleReviewSubmitted() {
  reviewingTask.value = null
  loadTasks() // 重新加载任务列表
}

// 加载互评任务
async function loadTasks() {
  loading.value = true
  try {
    tasks.value = await activityService.getMyPeerReviewTasks()
  } catch (error) {
    console.error('Failed to load peer review tasks:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.peer-review-task {
  @apply space-y-6;
}

.task-header {
  @apply flex items-center justify-between mb-6;
}

.task-title {
  @apply text-2xl font-bold text-gray-900;
}

.task-status {
  @apply text-right;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-12;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-3;
}

.tasks-list {
  @apply space-y-4;
}

.task-card {
  @apply bg-white border-2 border-gray-200 rounded-lg p-5 transition-all hover:shadow-md;
}

.task-card.task-completed {
  @apply bg-green-50 border-green-300;
}

.task-card-header {
  @apply flex items-center justify-between mb-3 pb-3 border-b border-gray-100;
}

.task-number {
  @apply text-sm font-mono text-gray-500;
}

.status-badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;
}

.status-pending {
  @apply bg-yellow-100 text-yellow-800;
}

.status-progress {
  @apply bg-blue-100 text-blue-800;
}

.status-completed {
  @apply bg-green-100 text-green-800;
}

.task-card-body {
  @apply space-y-3;
}

.task-description {
  @apply text-gray-700;
}

.btn-start-review {
  @apply w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors;
}

.completed-info {
  @apply flex items-center justify-between p-3 bg-white rounded-lg border border-green-200;
}

.empty-state {
  @apply flex flex-col items-center justify-center py-16 text-center;
}

.assign-card {
  @apply space-y-6;
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
  @apply flex flex-col gap-1;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.stat-value {
  @apply text-xl font-bold text-gray-900;
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
  @apply text-xs text-gray-500 mt-1;
}

.checkbox-label {
  @apply flex items-center gap-2 cursor-pointer;
}

.checkbox-label input {
  @apply w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500;
}

.preview-section {
  @apply bg-blue-50 border border-blue-200 rounded-lg p-4;
}

.preview-title {
  @apply text-sm font-semibold text-gray-800 mb-2;
}

.preview-list {
  @apply list-disc list-inside space-y-1 text-sm text-gray-700;
}

.warning-banner {
  @apply px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-center;
}

.actions {
  @apply flex justify-end gap-3 pt-4;
}

.btn-primary {
  @apply px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors;
}
</style>

