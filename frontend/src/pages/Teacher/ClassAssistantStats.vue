<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <DashboardHeader
      title="数据统计"
      subtitle="查看出勤率、积分、纪律等综合统计"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <input
            v-model="dateFrom"
            type="date"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <span class="text-gray-500">至</span>
          <input
            v-model="dateTo"
            type="date"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            @click="loadStats"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-blue-600 rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            查询
          </button>
          <button
            v-if="stats"
            @click="handlePrint"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            打印报表
          </button>
          <button
            @click="handleBack"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            返回
          </button>
        </div>
      </template>
    </DashboardHeader>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="text-center py-16 text-gray-500">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p>加载统计数据...</p>
      </div>

      <div v-else class="space-y-6 report-content">
        <!-- 报表标题（仅打印时显示） -->
        <div class="print-only report-header">
          <h1 class="report-title">班级数据统计报表</h1>
          <div class="report-meta">
            <p><strong>班级：</strong>{{ selectedClassroomName }}</p>
            <p><strong>统计时间：</strong>{{ dateFrom }} 至 {{ dateTo }}</p>
            <p><strong>生成时间：</strong>{{ new Date().toLocaleString('zh-CN') }}</p>
          </div>
        </div>
        <!-- 出勤统计 -->
        <div v-if="stats?.attendance" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">出勤统计</h2>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">{{ stats.attendance.totalSessions }}</p>
              <p class="text-sm text-gray-500">总点名次数</p>
            </div>
            <div 
              class="text-center cursor-pointer hover:bg-gray-50 rounded-lg p-2 transition-colors" 
              @click.stop="showDetail('present')"
              role="button"
              tabindex="0"
              @keydown.enter="showDetail('present')"
            >
              <p class="text-2xl font-bold text-green-600 pointer-events-none">{{ stats.attendance.presentCount }}</p>
              <p class="text-sm text-gray-500 pointer-events-none">出勤</p>
            </div>
            <div 
              class="text-center cursor-pointer hover:bg-gray-50 rounded-lg p-2 transition-colors" 
              @click.stop="showDetail('late')"
              role="button"
              tabindex="0"
              @keydown.enter="showDetail('late')"
            >
              <p class="text-2xl font-bold text-yellow-600 pointer-events-none">{{ stats.attendance.lateCount }}</p>
              <p class="text-sm text-gray-500 pointer-events-none">迟到</p>
            </div>
            <div 
              class="text-center cursor-pointer hover:bg-gray-50 rounded-lg p-2 transition-colors" 
              @click.stop="showDetail('leave')"
              role="button"
              tabindex="0"
              @keydown.enter="showDetail('leave')"
            >
              <p class="text-2xl font-bold text-blue-600 pointer-events-none">{{ stats.attendance.leaveCount }}</p>
              <p class="text-sm text-gray-500 pointer-events-none">请假</p>
            </div>
            <div 
              class="text-center cursor-pointer hover:bg-gray-50 rounded-lg p-2 transition-colors" 
              @click.stop="showDetail('absent')"
              role="button"
              tabindex="0"
              @keydown.enter="showDetail('absent')"
            >
              <p class="text-2xl font-bold text-red-600 pointer-events-none">{{ stats.attendance.absentCount }}</p>
              <p class="text-sm text-gray-500 pointer-events-none">缺勤</p>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">出勤率</span>
              <span class="text-xl font-bold text-green-600">
                {{ (stats.attendance.attendanceRate * 100).toFixed(1) }}%
              </span>
            </div>
            <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-green-600 h-2 rounded-full transition-all"
                :style="{ width: `${stats.attendance.attendanceRate * 100}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- 正面行为统计 -->
        <div v-if="stats?.positiveBehaviors" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">正面行为统计</h2>
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-green-600">{{ stats.positiveBehaviors.totalPoints }}</p>
              <p class="text-sm text-gray-500">总积分</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">{{ stats.positiveBehaviors.totalRecords }}</p>
              <p class="text-sm text-gray-500">记录数</p>
            </div>
            <div class="text-center">
              <p class="text-lg font-bold text-gray-700">
                {{ stats.positiveBehaviors.totalRecords > 0 
                  ? (stats.positiveBehaviors.totalPoints / stats.positiveBehaviors.totalRecords).toFixed(1) 
                  : 0 }}
              </p>
              <p class="text-sm text-gray-500">平均积分</p>
            </div>
          </div>
        </div>

        <!-- 纪律统计 -->
        <div v-if="stats?.discipline" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">纪律统计</h2>
          <div class="text-center">
            <p class="text-2xl font-bold text-amber-600">{{ stats.discipline.totalRecords }}</p>
            <p class="text-sm text-gray-500">总记录数</p>
          </div>
        </div>

        <!-- 值日统计 -->
        <div v-if="stats?.duty" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">值日统计</h2>
          <div class="grid grid-cols-4 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">{{ stats.duty.totalAssignments }}</p>
              <p class="text-sm text-gray-500">总任务数</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-green-600">{{ stats.duty.completedCount }}</p>
              <p class="text-sm text-gray-500">已完成</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-600">{{ stats.duty.pendingCount }}</p>
              <p class="text-sm text-gray-500">待完成</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-purple-600">
                {{ (stats.duty.completionRate * 100).toFixed(1) }}%
              </p>
              <p class="text-sm text-gray-500">完成率</p>
            </div>
          </div>
        </div>

        <!-- 无数据提示 -->
        <div v-if="!stats?.attendance && !stats?.positiveBehaviors && !stats?.discipline && !stats?.duty" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-12 text-center text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p>所选时间段内暂无统计数据</p>
        </div>
      </div>
    </main>

    <!-- 详情模态框 -->
    <div
      v-if="showDetailModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="showDetailModal = false"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-bold text-gray-900">
                {{ detailTitle }}
              </h2>
              <button
                @click="showDetailModal = false"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="p-6 max-h-[70vh] overflow-y-auto">
            <div v-if="loadingDetail" class="text-center py-8 text-gray-500">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
              加载中...
            </div>
            <div v-else-if="detailEntries.length === 0" class="text-center py-8 text-gray-500">
              暂无记录
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="entry in detailEntries"
                :key="entry.id"
                class="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all"
              >
                <div class="flex items-center gap-4 flex-1">
                  <div
                    class="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold"
                    :class="{
                      'bg-green-500': entry.status === 'present',
                      'bg-yellow-500': entry.status === 'late',
                      'bg-blue-500': entry.status === 'leave',
                      'bg-red-500': entry.status === 'absent',
                    }"
                  >
                    {{ getStudentName(entry.studentId)?.charAt(0) || '?' }}
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-gray-900">{{ getStudentName(entry.studentId) }}</p>
                    <p class="text-sm text-gray-500">
                      {{ getSessionDate(entry.sessionId) }}
                    </p>
                  </div>
                  <span
                    class="px-3 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': entry.status === 'present',
                      'bg-yellow-100 text-yellow-800': entry.status === 'late',
                      'bg-blue-100 text-blue-800': entry.status === 'leave',
                      'bg-red-100 text-red-800': entry.status === 'absent',
                    }"
                  >
                    {{ entry.status === 'present' ? '出勤' : entry.status === 'late' ? '迟到' : entry.status === 'leave' ? '请假' : '缺勤' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type { ClassroomStats, AttendanceEntry, StudentInfo, AttendanceStatus } from '@/types/classroomAssistant'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const classroomId = computed(() => Number(route.params.classroomId))

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const loading = ref(false)
const stats = ref<ClassroomStats | null>(null)
const selectedClassroomName = ref('')
const students = ref<StudentInfo[]>([])
const showDetailModal = ref(false)
const loadingDetail = ref(false)
const detailEntries = ref<AttendanceEntry[]>([])
const detailStatus = ref<AttendanceStatus | null>(null)
const sessionDates = ref<Map<number, string>>(new Map())

// 默认查询最近30天
const dateTo = ref(new Date().toISOString().split('T')[0])
const dateFrom = ref(
  new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
)

const detailTitle = computed(() => {
  const statusMap: Record<string, string> = {
    present: '出勤记录',
    late: '迟到记录',
    leave: '请假记录',
    absent: '缺勤记录',
  }
  return statusMap[detailStatus.value || ''] || '考勤记录'
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleBack = () => {
  router.push('/teacher/class-assistant')
}

const loadStats = async () => {
  try {
    loading.value = true
    const data = await classroomAssistantService.getClassroomStats(classroomId.value, {
      fromDate: dateFrom.value ? new Date(dateFrom.value).toISOString() : undefined,
      toDate: dateTo.value ? new Date(dateTo.value + 'T23:59:59').toISOString() : undefined,
    })
    stats.value = data
    
    // 加载班级名称和学生列表
    const classrooms = await classroomAssistantService.getMyClassrooms()
    const classroom = classrooms.find((c) => c.id === classroomId.value)
    selectedClassroomName.value = classroom?.name || `班级 ${classroomId.value}`
    
    // 加载学生列表
    students.value = await classroomAssistantService.getClassroomStudents(classroomId.value)
  } catch (error) {
    console.error('加载统计失败:', error)
    alert('加载统计数据失败，请重试')
  } finally {
    loading.value = false
  }
}

const showDetail = async (status: AttendanceStatus) => {
  console.log('showDetail called with status:', status)
  try {
    showDetailModal.value = true
    loadingDetail.value = true
    detailStatus.value = status
    
    const entries = await classroomAssistantService.getAttendanceEntriesByStatus(
      classroomId.value,
      status,
      dateFrom.value ? new Date(dateFrom.value).toISOString() : undefined,
      dateTo.value ? new Date(dateTo.value + 'T23:59:59').toISOString() : undefined
    )
    
    detailEntries.value = entries
    
    // 加载会话日期
    const sessionIds = [...new Set(entries.map(e => e.sessionId))]
    for (const sessionId of sessionIds) {
      try {
        const session = await classroomAssistantService.getAttendanceSession(sessionId)
        sessionDates.value.set(sessionId, new Date(session.startedAt).toLocaleString('zh-CN'))
      } catch (error) {
        console.error(`加载会话 ${sessionId} 失败:`, error)
      }
    }
  } catch (error) {
    console.error('加载详情失败:', error)
    alert('加载详情失败，请重试')
  } finally {
    loadingDetail.value = false
  }
}

const getStudentName = (studentId: number): string => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.fullName || student?.username || `学生${studentId}`
}

const getSessionDate = (sessionId: number): string => {
  return sessionDates.value.get(sessionId) || '未知时间'
}

const handlePrint = () => {
  window.print()
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
/* 打印样式 */
@media print {
  /* 隐藏不需要打印的元素 */
  .min-h-screen {
    background: white !important;
  }
  
  /* 隐藏头部和按钮 */
  :deep(.dashboard-header),
  button,
  input,
  .no-print {
    display: none !important;
  }
  
  /* 报表内容样式 */
  .report-content {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  
  /* 报表标题 */
  .report-header {
    display: block !important;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #000;
  }
  
  .report-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1rem;
    color: #000;
  }
  
  .report-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #666;
  }
  
  .report-meta p {
    margin: 0.25rem 0;
  }
  
  /* 统计卡片样式 */
  .bg-white\/80,
  .backdrop-blur-sm,
  .rounded-2xl,
  .border,
  .border-gray-200,
  .shadow-lg {
    background: white !important;
    border: 1px solid #ddd !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    page-break-inside: avoid;
    margin-bottom: 1rem;
    padding: 1rem;
  }
  
  /* 标题样式 */
  h2 {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 1rem;
    color: #000;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.5rem;
  }
  
  /* 数字样式 */
  .text-2xl {
    font-size: 20px !important;
  }
  
  .text-xl {
    font-size: 18px !important;
  }
  
  /* 颜色在打印时转为灰度 */
  .text-green-600,
  .text-yellow-600,
  .text-blue-600,
  .text-red-600,
  .text-amber-600,
  .text-purple-600 {
    color: #000 !important;
  }
  
  .bg-green-600,
  .bg-yellow-600,
  .bg-blue-600,
  .bg-red-600 {
    background: #ddd !important;
  }
  
  /* 进度条 */
  .bg-gray-200 {
    background: #ddd !important;
  }
  
  /* 网格布局 */
  .grid {
    display: grid !important;
  }
  
  /* 页眉页脚 */
  @page {
    margin: 2cm;
    size: A4;
  }
  
  /* 避免分页 */
  .space-y-6 > * {
    page-break-inside: avoid;
  }
}

/* 屏幕显示时隐藏报表标题 */
.print-only {
  display: none;
}

/* 打印时显示 */
@media print {
  .print-only {
    display: block !important;
  }
}
</style>
