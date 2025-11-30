<template>
  <div class="submission-list">
    <!-- 标题和过滤器 -->
    <div class="list-header">
      <h3 class="list-title">📝 学生提交列表</h3>
      <div class="filter-bar">
        <select v-model="statusFilter" class="filter-select" @change="loadSubmissions">
          <option value="">全部状态</option>
          <option value="not_started">未开始</option>
          <option value="draft">草稿</option>
          <option value="submitted">已提交</option>
          <option value="graded">已评分</option>
          <option value="returned">已退回</option>
        </select>
        <button @click="loadSubmissions" class="btn-refresh" :disabled="loading">
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 批量操作 -->
    <div v-if="selectedSubmissions.length > 0" class="bulk-actions">
      <span class="text-sm text-gray-600">已选择 {{ selectedSubmissions.length }} 项</span>
      <div class="flex gap-2">
        <button @click="handleBulkGrade" class="btn-sm btn-primary">
          批量评分
        </button>
        <button @click="handleBulkReturn" class="btn-sm btn-secondary">
          批量退回
        </button>
        <button @click="selectedSubmissions = []" class="btn-sm btn-secondary">
          取消选择
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && submissions.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载提交数据...</p>
    </div>

    <!-- 提交列表 -->
    <div v-else-if="submissions.length > 0" class="submissions-table">
      <table class="w-full">
        <thead>
          <tr>
            <th class="table-header">
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th class="table-header">学生</th>
            <th class="table-header">状态</th>
            <th class="table-header">分数</th>
            <th class="table-header">提交时间</th>
            <th class="table-header">用时</th>
            <th class="table-header">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="submission in submissions"
            :key="submission.id"
            class="table-row"
          >
            <td class="table-cell">
              <input
                type="checkbox"
                :value="submission.id"
                v-model="selectedSubmissions"
              />
            </td>
            <td class="table-cell">
              <div class="student-info">
                <div class="font-medium">{{ submission.studentName }}</div>
                <div class="text-xs text-gray-500">{{ submission.studentEmail }}</div>
              </div>
            </td>
            <td class="table-cell">
              <span :class="getStatusBadgeClass(submission.status)">
                {{ getStatusLabel(submission.status) }}
              </span>
              <span v-if="submission.isLate" class="late-badge">迟交</span>
            </td>
            <td class="table-cell">
              <div v-if="submission.score !== null" class="score-display">
                <span class="font-semibold">{{ submission.score }}</span>
                <span class="text-gray-500 text-sm">/ {{ submission.maxScore }}</span>
              </div>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="table-cell text-sm text-gray-600">
              {{ formatDateTime(submission.submittedAt) }}
            </td>
            <td class="table-cell text-sm text-gray-600">
              {{ submission.timeSpent ? formatTime(submission.timeSpent) : '-' }}
            </td>
            <td class="table-cell">
              <div class="flex gap-2">
                <button
                  v-if="submission.status !== 'not_started' && submission.id"
                  @click="viewSubmission(submission)"
                  class="btn-xs btn-view"
                  title="查看详情"
                >
                  查看
                </button>
                <button
                  v-if="submission.status === 'submitted' && submission.id"
                  @click="gradeSubmission(submission)"
                  class="btn-xs btn-grade"
                  title="评分"
                >
                  评分
                </button>
                <span v-if="submission.status === 'not_started'" class="text-xs text-gray-400">
                  暂无操作
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="text-4xl mb-4">📭</div>
      <p class="text-gray-500">暂无提交记录</p>
    </div>

    <!-- 评分模态框 -->
    <GradingModal
      v-if="gradingSubmission"
      :submission="gradingSubmission"
      :activity="activity"
      @close="gradingSubmission = null"
      @graded="handleGraded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { ActivitySubmission } from '../../../types/activity'
import type { ActivityCellContent } from '../../../types/activity'
import activityService from '../../../services/activity'
import GradingModal from './GradingModal.vue'
import { useRealtimeChannel } from '@/composables/useRealtimeChannel'
import type { WebSocketMessage } from '@/composables/useRealtimeChannel'

interface Props {
  cellId: number
  activity: ActivityCellContent
  sessionId?: number
  lessonId?: number
}

const props = defineProps<Props>()

const submissions = ref<any[]>([])
const loading = ref(false)
const statusFilter = ref('')
const selectedSubmissions = ref<number[]>([])
const gradingSubmission = ref<any | null>(null)

// 全选状态
const allSelected = computed(() => {
  return submissions.value.length > 0 && selectedSubmissions.value.length === submissions.value.length
})

// 切换全选
function toggleSelectAll() {
  if (allSelected.value) {
    selectedSubmissions.value = []
  } else {
    selectedSubmissions.value = submissions.value.map(s => s.id)
  }
}

// 获取状态标签
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    not_started: '未开始',
    draft: '草稿',
    submitted: '已提交',
    graded: '已评分',
    returned: '已退回',
  }
  return labels[status] || status
}

// 获取状态徽章样式
function getStatusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    not_started: 'status-badge status-not-started',
    draft: 'status-badge status-draft',
    submitted: 'status-badge status-submitted',
    graded: 'status-badge status-graded',
    returned: 'status-badge status-returned',
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

function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟`
}

// 加载提交列表
async function loadSubmissions() {
  loading.value = true
  try {
    console.log('📥 加载提交列表...', {
      cellId: props.cellId,
      statusFilter: statusFilter.value,
    })
    
    const data = await activityService.getCellSubmissions(
      props.cellId,
      statusFilter.value || undefined,
      props.sessionId,
      props.lessonId
    )
    
    console.log('✅ 提交列表加载成功:', {
      count: data.length,
      submissions: data.map(s => ({
        id: s.id,
        studentName: s.studentName || s.student_name,
        status: s.status,
        score: s.score,
      })),
    })
    
    submissions.value = data
  } catch (error: any) {
    console.error('❌ 加载提交列表失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      cellId: props.cellId,
    })
    submissions.value = []
  } finally {
    loading.value = false
  }
}

// 查看提交详情
function viewSubmission(submission: any) {
  gradingSubmission.value = submission
}

// 评分
function gradeSubmission(submission: any) {
  gradingSubmission.value = submission
}

// 评分完成
function handleGraded() {
  gradingSubmission.value = null
  loadSubmissions() // 重新加载列表
}

// 批量评分
async function handleBulkGrade() {
  const score = prompt('请输入统一分数：')
  if (!score) return

  const scoreNum = parseFloat(score)
  if (isNaN(scoreNum)) {
    alert('请输入有效的分数')
    return
  }

  try {
    await activityService.bulkGrade(selectedSubmissions.value, scoreNum)
    alert('批量评分成功')
    selectedSubmissions.value = []
    loadSubmissions()
  } catch (error) {
    console.error('Bulk grade failed:', error)
    alert('批量评分失败')
  }
}

// 批量退回
async function handleBulkReturn() {
  const feedback = prompt('请输入退回原因：')
  if (!feedback) return

  try {
    await activityService.bulkReturn(selectedSubmissions.value, feedback)
    alert('批量退回成功')
    selectedSubmissions.value = []
    loadSubmissions()
  } catch (error) {
    console.error('Bulk return failed:', error)
    alert('批量退回失败')
  }
}

// WebSocket 实时更新
const channelDescriptor = computed(() => {
  if (props.sessionId) {
    return { scope: 'session' as const, id: props.sessionId }
  }
  return { scope: 'lesson' as const, id: props.lessonId! }
})

const {
  isConnected,
  connect: connectRealtime,
  disconnect: disconnectRealtime,
  registerListener,
  unregisterAll,
} = useRealtimeChannel(channelDescriptor)

// 监听新提交通知
function handleNewSubmission(message: WebSocketMessage) {
  const messageCellId = message.data.cell_id
  const propsCellId = props.cellId
  
  // 支持数字和字符串比较
  if (String(messageCellId) !== String(propsCellId)) {
    return
  }
  
  console.log('📬 收到新提交通知，刷新列表...', {
    submissionId: message.data.submission_id,
    messageCellId,
    propsCellId,
    studentId: message.data.student_id,
  })
  
  // 自动刷新列表
  loadSubmissions()
}

// 监听统计更新通知（也会触发列表刷新）
function handleStatisticsUpdate(message: WebSocketMessage) {
  const messageCellId = message.data.cell_id
  const propsCellId = props.cellId
  
  // 支持数字和字符串比较
  if (String(messageCellId) !== String(propsCellId)) {
    return
  }
  
  console.log('📊 收到统计更新通知，刷新列表...', {
    messageCellId,
    propsCellId,
  })
  
  // 自动刷新列表
  loadSubmissions()
}

let pollingInterval: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  // 初始加载
  await loadSubmissions()
  
  // 连接 WebSocket（如果有 sessionId）
  if (props.sessionId) {
    try {
      await connectRealtime()
      registerListener('new_submission', handleNewSubmission)
      registerListener('submission_statistics_updated', handleStatisticsUpdate)
      console.log('✅ SubmissionList: WebSocket 连接成功，将使用实时推送')
      
      // 即使 WebSocket 连接成功，也启动轮询作为备用（每10秒）
      pollingInterval = setInterval(() => {
        loadSubmissions()
      }, 10000)
    } catch (error) {
      console.warn('⚠️ SubmissionList: WebSocket 连接失败，降级到轮询模式', error)
      // WebSocket 失败时，定期刷新（每5秒）
      pollingInterval = setInterval(() => {
        loadSubmissions()
      }, 5000)
    }
  } else {
    // 没有 sessionId 时，也启动轮询（每5秒）
    console.log('⚠️ SubmissionList: 没有 sessionId，使用轮询模式')
    pollingInterval = setInterval(() => {
      loadSubmissions()
    }, 5000)
  }
})

onUnmounted(() => {
  unregisterAll()
  disconnectRealtime()
  // 清理轮询定时器
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
})
</script>

<style scoped>
.submission-list {
  @apply bg-white rounded-lg border border-gray-200;
}

.list-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.list-title {
  @apply text-xl font-bold text-gray-900;
}

.filter-bar {
  @apply flex items-center gap-3;
}

.filter-select {
  @apply px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.btn-refresh {
  @apply flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50;
}

.bulk-actions {
  @apply flex items-center justify-between px-6 py-3 bg-blue-50 border-b border-blue-200;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-12;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-3;
}

.submissions-table {
  @apply overflow-x-auto;
}

.table-header {
  @apply px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider bg-gray-50 border-b border-gray-200;
}

.table-row {
  @apply hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0;
}

.table-cell {
  @apply px-4 py-4 whitespace-nowrap;
}

.student-info {
  @apply min-w-[150px];
}

.status-badge {
  @apply inline-flex items-center px-2 py-1 text-xs font-medium rounded-full;
}

.status-draft {
  @apply bg-gray-100 text-gray-700;
}

.status-submitted {
  @apply bg-blue-100 text-blue-800;
}

.status-graded {
  @apply bg-green-100 text-green-800;
}

.status-returned {
  @apply bg-yellow-100 text-yellow-800;
}

.status-not-started {
  @apply bg-gray-100 text-gray-600;
}

.late-badge {
  @apply ml-2 inline-flex items-center px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full;
}

.score-display {
  @apply flex items-baseline gap-1;
}

.btn-xs {
  @apply px-3 py-1 text-xs rounded-lg transition-colors;
}

.btn-view {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.btn-grade {
  @apply bg-blue-100 text-blue-700 hover:bg-blue-200;
}

.btn-sm {
  @apply px-3 py-1 text-sm rounded-lg transition-colors;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.empty-state {
  @apply flex flex-col items-center justify-center py-16 text-center;
}
</style>

