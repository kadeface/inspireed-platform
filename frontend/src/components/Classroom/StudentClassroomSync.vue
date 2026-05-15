<template>
  <div v-if="session && (session.status === 'teaching' || session.status === 'preparing')" class="student-classroom-sync">
    <!-- PENDING 状态：等待教师开始上课 -->
    <div v-if="session.status === 'preparing'" class="waiting-banner">
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
    
    <!-- ACTIVE 状态：同步状态提示 -->
    <div v-else-if="session.status === 'teaching' && isSyncing" class="sync-status-banner">
      <span class="sync-icon">🔄</span>
      <span>教师正在切换内容...</span>
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

// 解析UTC时间字符串（处理没有时区信息的情况）
function parseUTCTime(timeString: string): Date {
  let utcString = timeString.trim()
  
  // 检查是否已有时区信息
  const hasTimezone = utcString.endsWith('Z') || /[+-]\d{2}:?\d{2}$/.test(utcString)
  
  if (!hasTimezone) {
    // 如果没有时区信息，假设它是UTC时间并添加Z后缀
    if (utcString.includes(' ')) {
      // 空格格式转换为ISO格式：YYYY-MM-DD HH:MM:SS -> YYYY-MM-DDTHH:MM:SSZ
      utcString = utcString.replace(' ', 'T') + 'Z'
    } else if (utcString.includes('T')) {
      // 已经是ISO格式，只需添加Z
      utcString = utcString + 'Z'
    } else {
      // 其他格式，添加Z
      utcString = utcString + 'Z'
    }
  }
  
  return new Date(utcString)
}

// 计算当前已进行的时长（秒）
function calculateDuration(): number {
  if (!props.session?.actualStart) {
    return 0
  }
  
  try {
    const now = new Date()
    const start = parseUTCTime(props.session.actualStart)
    const diffMs = now.getTime() - start.getTime()
    
    // 如果时间差为负（未来时间），说明解析有误，返回0
    if (diffMs < 0) {
      console.warn('⚠️ 时间差为负，可能是时区解析问题:', {
        actualStart: props.session.actualStart,
        parsed: start.toISOString(),
        now: now.toISOString(),
        diffMs,
      })
      return 0
    }
    
    return Math.floor(diffMs / 1000)
  } catch (e) {
    console.error('❌ 解析actualStart时间失败:', props.session.actualStart, e)
    return 0
  }
}

function startDurationTimer() {
  if (durationInterval.value || !props.session?.actualStart) return
  
  // 计算初始时长
  sessionDuration.value = calculateDuration()
  
  // 设置定时器，每秒更新时长
  durationInterval.value = window.setInterval(() => {
    if (props.session?.actualStart) {
      const duration = calculateDuration()
      // 如果计算出的时长有效（>= 0），更新显示
      if (duration >= 0) {
        sessionDuration.value = duration
      } else {
        // 如果计算出负值，停止计时器
        console.error('❌ 计算出负时长，停止计时器')
        stopDurationTimer()
      }
    }
  }, 1000) as unknown as number
}

function stopDurationTimer() {
  if (durationInterval.value) {
    clearInterval(durationInterval.value)
    durationInterval.value = null
  }
}

watch(() => props.session?.status, (status) => {
  if (status === 'teaching' && props.session?.actualStart) {
    startDurationTimer()
  } else {
    stopDurationTimer()
  }
}, { immediate: true })

watch(() => props.session?.actualStart, (actualStart) => {
  if (actualStart && props.session?.status === 'teaching') {
    startDurationTimer()
  }
})

onMounted(() => {
  if (props.session?.status === 'teaching' && props.session?.actualStart) {
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
  @apply bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white rounded-2xl p-5 md:p-6 shadow-xl shadow-emerald-500/30;
}

.banner-content {
  @apply flex items-center gap-4;
}

.exit-button {
  @apply px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl transition-all flex items-center gap-2 font-medium text-sm shadow-lg hover:shadow-xl;
  @apply disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105;
}

.exit-button:hover:not(:disabled) {
  @apply bg-white/40;
}

.exit-loading {
  @apply text-sm;
}

.live-indicator {
  @apply w-3 h-3 bg-white rounded-full animate-pulse shadow-lg;
}

.banner-text {
  @apply flex-1;
}

.banner-title {
  @apply text-xl md:text-2xl font-bold mb-2;
}

.banner-subtitle {
  @apply text-sm md:text-base text-emerald-50 font-medium;
}

.teacher-name {
  @apply font-semibold;
}

.sync-status {
  @apply mt-4 pt-4 border-t border-emerald-300/50 flex items-center gap-2 text-sm text-emerald-50 font-medium;
}

.sync-status-banner {
  @apply bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white rounded-xl p-4 shadow-lg shadow-emerald-500/30 flex items-center gap-2 text-sm font-medium;
}

.sync-icon {
  @apply animate-spin text-lg;
}

.classroom-info {
  @apply flex items-center gap-6 text-sm bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-white/50;
}

.info-item {
  @apply flex items-center gap-2;
}

.info-label {
  @apply text-gray-600 font-medium;
}

.info-value {
  @apply font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent;
}

.waiting-banner {
  @apply bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white rounded-2xl p-5 md:p-6 shadow-xl shadow-emerald-500/30;
}

.waiting-indicator {
  @apply text-3xl animate-pulse;
}

.waiting-message {
  @apply mt-4 pt-4 border-t border-emerald-300/50 text-sm text-emerald-50 font-medium;
}
</style>

