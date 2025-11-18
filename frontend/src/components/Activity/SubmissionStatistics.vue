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
    
    <!-- 连接状态指示 -->
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

onMounted(async () => {
  try {
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
    
    // 3. 等待一小段时间确保连接稳定，然后请求统计
    setTimeout(() => {
      console.log('📊 延迟请求统计，isConnected =', isConnected.value)
      requestStats(props.cellId, props.lessonId)
    }, 100)
  } catch (error) {
    console.error('❌ 连接实时通道失败:', error)
  }
})

onUnmounted(() => {
  unregisterAll()
  disconnectRealtime()
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

.connection-status {
  @apply flex items-center justify-center gap-2 text-sm mt-4 pt-4 border-t border-gray-200;
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

