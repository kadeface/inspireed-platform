<template>
  <div class="statistics-panel">
    <h3 class="panel-title">📊 实时统计</h3>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总学生数</div>
        <div class="stat-value">{{ statistics.totalStudents }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">已提交</div>
        <div class="stat-value text-green-600">{{ statistics.submittedCount }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">草稿中</div>
        <div class="stat-value text-yellow-600">{{ statistics.draftCount }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">未开始</div>
        <div class="stat-value text-gray-600">{{ statistics.notStartedCount }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">平均分</div>
        <div class="stat-value text-blue-600">
          {{ statistics.averageScore !== null ? statistics.averageScore.toFixed(1) : '-' }}
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">平均用时</div>
        <div class="stat-value text-purple-600">
          {{ formatTime(statistics.averageTimeSpent) }}
        </div>
      </div>
    </div>
    
    <!-- 进度条 -->
    <div class="progress-section">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
      <p class="progress-text">
        提交进度：{{ statistics.submittedCount }} / {{ statistics.totalStudents }} 
        ({{ progressPercent }}%)
      </p>
    </div>
    
    <!-- 连接状态指示和刷新按钮 -->
    <div class="connection-status-section">
      <div v-if="isConnected" class="connection-status connected">
        <span class="status-dot"></span>
        实时更新中
      </div>
      <div v-else-if="isConnecting" class="connection-status connecting">
        <span class="status-dot"></span>
        连接中...
      </div>
      <div v-else class="connection-status disconnected">
        <span class="status-dot"></span>
        未连接
      </div>
      
      <!-- 🆕 手动刷新按钮 -->
      <button 
        @click="loadStatisticsFromAPI" 
        class="refresh-btn"
        :disabled="refreshing"
        title="手动刷新统计数据"
      >
        <svg class="w-4 h-4" :class="{ 'animate-spin': refreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ refreshing ? '刷新中...' : '刷新' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRealtimeChannel } from '@/composables/useRealtimeChannel'
import type { WebSocketMessage } from '@/composables/useRealtimeChannel'
import { useUserStore } from '@/store/user'
import { authService } from '@/services/auth'

interface Props {
  cellId: number
  lessonId: number
  sessionId?: number
}

const props = defineProps<Props>()
const userStore = useUserStore()

const statistics = ref({
  totalStudents: 0,
  submittedCount: 0,
  draftCount: 0,
  notStartedCount: 0,
  averageScore: null as number | null,
  averageTimeSpent: 0,
})

const refreshing = ref(false)
let pollingInterval: ReturnType<typeof setInterval> | null = null

const progressPercent = computed(() => {
  if (statistics.value.totalStudents === 0) return 0
  return Math.round((statistics.value.submittedCount / statistics.value.totalStudents) * 100)
})

function formatTime(seconds: number): string {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟`
}

const channelDescriptor = computed(() => {
  if (props.sessionId) {
    return { scope: 'session' as const, id: props.sessionId }
  }
  return { scope: 'lesson' as const, id: props.lessonId }
})

const {
  isConnected,
  isConnecting,
  connect: connectRealtime,
  disconnect: disconnectRealtime,
  registerListener,
  unregisterAll,
  requestStatistics: requestStats,
} = useRealtimeChannel(channelDescriptor)

function handleStatisticsUpdate(message: WebSocketMessage) {
  if (message.data.cell_id !== props.cellId) return
  
  statistics.value = {
    totalStudents: message.data.total_students || 0,
    submittedCount: message.data.submitted_count || 0,
    draftCount: message.data.draft_count || 0,
    notStartedCount: message.data.not_started_count || 0,
    averageScore: message.data.average_score,
    averageTimeSpent: message.data.average_time_spent || 0,
  }
}

// 🆕 直接通过 API 加载统计数据（备用方案）
async function loadStatisticsFromAPI() {
  refreshing.value = true
  try {
    console.log('📊 通过 API 直接加载统计数据...', { cellId: props.cellId })
    const { activityService } = await import('../../services/activity')
    const stats = await activityService.getStatistics(props.cellId)
    
    // 转换 API 返回的格式到组件需要的格式（后端可能返回 snake_case 或 camelCase）
    const statsAny = stats as any
    const totalStudents = stats.totalStudents || statsAny.total_students || 0
    const submittedCount = stats.submittedCount || statsAny.submitted_count || 0
    const draftCount = stats.draftCount || statsAny.draft_count || 0
    
    statistics.value = {
      totalStudents,
      submittedCount,
      draftCount,
      notStartedCount: Math.max(0, totalStudents - submittedCount - draftCount),
      averageScore: stats.averageScore ?? statsAny.average_score ?? null,
      averageTimeSpent: stats.averageTimeSpent ?? statsAny.average_time_spent ?? 0,
    }
    
    console.log('✅ 统计数据已加载（API）:', statistics.value)
  } catch (error: any) {
    console.error('❌ 通过 API 加载统计数据失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      cellId: props.cellId,
    })
  } finally {
    refreshing.value = false
  }
}

onMounted(async () => {
  try {
    // 0. 首先通过 API 直接加载统计数据（确保有数据）
    await loadStatisticsFromAPI()
    
    // 1. 确保用户信息已加载
    if (!userStore.user && userStore.token) {
      console.log('📥 加载用户信息...')
      try {
        const user = await authService.getCurrentUser()
        userStore.setUser(user)
        console.log('✅ 用户信息已加载:', user)
      } catch (error) {
        console.error('❌ 加载用户信息失败:', error)
      }
    }
    
    // 2. 连接实时通道
    await connectRealtime()
    console.log('📡 连接完成，isConnected =', isConnected.value)
    
    registerListener('submission_statistics_updated', handleStatisticsUpdate)
    
    // 3. 等待一小段时间确保连接稳定，然后请求统计（用于实时更新）
    setTimeout(() => {
      console.log('📊 延迟请求统计，isConnected =', isConnected.value)
      if (isConnected.value) {
        requestStats(props.cellId, props.lessonId)
      } else {
        console.warn('⚠️ WebSocket 未连接，将使用 API 定期刷新')
        // 如果 WebSocket 未连接，定期通过 API 刷新
        pollingInterval = setInterval(() => {
          loadStatisticsFromAPI()
        }, 5000) // 每5秒刷新一次
      }
    }, 100)
  } catch (error) {
    console.error('❌ 连接实时通道失败:', error)
    // 如果 WebSocket 连接失败，使用 API 定期刷新
    pollingInterval = setInterval(() => {
      loadStatisticsFromAPI()
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
.statistics-panel {
  @apply bg-white rounded-lg border border-gray-200 p-6 shadow-sm;
}

.panel-title {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.stats-grid {
  @apply grid grid-cols-2 md:grid-cols-3 gap-4 mb-6;
}

.stat-card {
  @apply bg-gray-50 rounded-lg p-4 text-center transition-all hover:bg-gray-100;
}

.stat-label {
  @apply text-sm text-gray-600 mb-2;
}

.stat-value {
  @apply text-2xl font-bold;
}

.progress-section {
  @apply mt-4 mb-4;
}

.progress-bar {
  @apply w-full h-3 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-600 transition-all duration-300 ease-in-out;
}

.progress-text {
  @apply text-sm text-gray-600 mt-2 text-center;
}

.connection-status-section {
  @apply flex items-center justify-between mt-4 pt-4 border-t border-gray-200;
}

.connection-status {
  @apply flex items-center gap-2 text-sm;
}

.refresh-btn {
  @apply flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.connected {
  @apply text-green-600;
}

.connected .status-dot {
  @apply bg-green-600 animate-pulse;
}

.connecting {
  @apply text-yellow-600;
}

.connecting .status-dot {
  @apply bg-yellow-600 animate-pulse;
}

.disconnected {
  @apply text-gray-400;
}

.disconnected .status-dot {
  @apply bg-gray-400;
}
</style>

