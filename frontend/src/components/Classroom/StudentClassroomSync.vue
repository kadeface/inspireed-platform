<template>
  <div v-if="session && (session.status === 'active' || session.status === 'pending')" class="student-classroom-sync">
    <!-- PENDING 状态：等待教师开始上课 -->
    <div v-if="session.status === 'pending'" class="waiting-banner">
      <div class="banner-content">
        <span class="waiting-indicator">⏳</span>
        <div class="banner-text">
          <div class="banner-title">等待教师开始上课</div>
          <div class="banner-subtitle">
            {{ session.lessonTitle || '课程' }} · 
            <span class="teacher-name">授课教师：{{ session.teacherName }}</span>
          </div>
        </div>
      </div>
      <div class="waiting-message">
        <p>已成功加入课堂，请等待教师开始上课...</p>
      </div>
    </div>
    
    <!-- ACTIVE 状态：正在上课 -->
    <div v-else-if="session.status === 'active'" class="classroom-banner">
      <div class="banner-content">
        <span class="live-indicator"></span>
        <div class="banner-text">
          <div class="banner-title">🎓 正在上课</div>
          <div class="banner-subtitle">
            {{ session.lessonTitle || '课程' }} · 
            <span class="teacher-name">授课教师：{{ session.teacherName }}</span>
          </div>
        </div>
        <button
          @click="handleExitClassroom"
          class="exit-button"
          :disabled="isExiting"
          title="退出上课"
        >
          <svg v-if="!isExiting" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span v-else class="exit-loading">退出中...</span>
        </button>
      </div>
      
      <!-- 同步状态 -->
      <div v-if="isSyncing" class="sync-status">
        <span class="sync-icon">🔄</span>
        <span>教师正在切换内容...</span>
      </div>
    </div>

    <!-- 课堂信息 -->
    <div v-if="session.status === 'active'" class="classroom-info">
      <div class="info-item">
        <span class="info-label">在线学生</span>
        <span class="info-value">{{ session.activeStudents }} / {{ session.totalStudents }}</span>
      </div>
      <div v-if="sessionDuration" class="info-item">
        <span class="info-label">已进行</span>
        <span class="info-value">{{ formatDuration(sessionDuration) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import type { ClassSession } from '../../types/classroomSession'

interface Props {
  lessonId: number
  session?: ClassSession | null
  onLeaveSession?: () => Promise<void>
}

const props = defineProps<Props>()

const isSyncing = ref(false)
const sessionDuration = ref(0)
const durationInterval = ref<number | null>(null)
const isExiting = ref(false)

// 处理退出上课
async function handleExitClassroom() {
  if (!props.session || isExiting.value || !props.onLeaveSession) return
  
  if (!confirm('确定要退出上课吗？退出后您将无法继续接收教师的实时同步内容。')) {
    return
  }
  
  isExiting.value = true
  try {
    await props.onLeaveSession()
    // 退出成功后，session 会被清空，组件会自动隐藏
    console.log('✅ 已成功退出上课')
  } catch (error: any) {
    console.error('❌ 退出上课失败:', error)
    alert('退出上课失败，请稍后重试')
  } finally {
    isExiting.value = false
  }
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function startDurationTimer() {
  if (durationInterval.value || !props.session?.actualStart) return
  
  durationInterval.value = setInterval(() => {
    if (props.session?.actualStart) {
      const now = new Date()
      const start = new Date(props.session.actualStart)
      sessionDuration.value = Math.floor((now.getTime() - start.getTime()) / 1000)
    }
  }, 1000)
}

function stopDurationTimer() {
  if (durationInterval.value) {
    clearInterval(durationInterval.value)
    durationInterval.value = null
  }
}

watch(() => props.session?.status, (status) => {
  if (status === 'active' && props.session?.actualStart) {
    startDurationTimer()
  } else {
    stopDurationTimer()
  }
}, { immediate: true })

watch(() => props.session?.actualStart, (actualStart) => {
  if (actualStart && props.session?.status === 'active') {
    startDurationTimer()
  }
})

onMounted(() => {
  if (props.session?.status === 'active' && props.session?.actualStart) {
    startDurationTimer()
  }
})

onUnmounted(() => {
  stopDurationTimer()
})
</script>

<style scoped>
.student-classroom-sync {
  @apply mb-4 space-y-3;
}

.classroom-banner {
  @apply bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-4 shadow-lg;
}

.banner-content {
  @apply flex items-center gap-3;
}

.exit-button {
  @apply px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors flex items-center gap-2 font-medium text-sm;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
}

.exit-button:hover:not(:disabled) {
  @apply bg-white/40;
}

.exit-loading {
  @apply text-sm;
}

.live-indicator {
  @apply w-3 h-3 bg-red-500 rounded-full animate-pulse;
}

.banner-text {
  @apply flex-1;
}

.banner-title {
  @apply text-lg font-bold mb-1;
}

.banner-subtitle {
  @apply text-sm text-blue-100;
}

.teacher-name {
  @apply font-medium;
}

.sync-status {
  @apply mt-3 pt-3 border-t border-blue-400 flex items-center gap-2 text-sm text-blue-100;
}

.sync-icon {
  @apply animate-spin;
}

.classroom-info {
  @apply flex items-center gap-6 text-sm text-gray-600 bg-gray-50 rounded-lg p-3;
}

.info-item {
  @apply flex items-center gap-2;
}

.info-label {
  @apply text-gray-600;
}

.info-value {
  @apply font-semibold text-gray-900;
}

.waiting-banner {
  @apply bg-gradient-to-r from-yellow-400 to-yellow-500 text-white rounded-lg p-4 shadow-lg;
}

.waiting-indicator {
  @apply text-2xl;
}

.waiting-message {
  @apply mt-3 pt-3 border-t border-yellow-300 text-sm text-yellow-50;
}
</style>

