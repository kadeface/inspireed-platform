<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <DashboardHeader
      title="点名考勤"
      :subtitle="selectedClassroom ? `班级：${selectedClassroom.name}` : '选择班级开始点名'"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <button
            @click="handleBackToDashboard"
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
      <!-- 历史记录按钮 -->
      <div class="mb-6 flex justify-end">
        <button
          @click="showHistory = true"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          查看历史记录
        </button>
      </div>

      <!-- 未开始点名 -->
      <div v-if="!currentSession" class="space-y-6">
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-8 text-center">
          <svg class="mx-auto h-16 w-16 text-blue-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">开始点名</h2>
          <p class="text-gray-600 mb-6">点击下方按钮开始新的点名，系统将自动为所有学生生成默认出勤记录</p>
          <button
            @click="startAttendance"
            :disabled="!selectedClassroom || starting"
            class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            开始点名
          </button>
        </div>
      </div>

      <!-- 点名进行中 -->
      <div v-else class="space-y-6">
        <!-- 会话信息 -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900">点名进行中</h2>
              <p class="text-sm text-gray-500 mt-1">
                开始时间：{{ new Date(currentSession.startedAt).toLocaleString() }}
              </p>
            </div>
            <div class="flex gap-3">
              <button
                @click="markAllPresent"
                :disabled="saving"
                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-xl hover:bg-blue-100 transition-all disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                一键全到
              </button>
              <button
                @click="completeAttendance"
                :disabled="saving"
                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                完成点名
              </button>
            </div>
          </div>
        </div>

        <!-- 学生列表 -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-bold text-gray-900">学生考勤状态</h3>
          </div>
          <div class="p-6">
            <div v-if="loadingStudents" class="text-center py-8 text-gray-500">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto mb-2"></div>
              加载学生列表...
            </div>
            <div v-else-if="attendanceEntries.length === 0" class="text-center py-8 text-gray-500">
              暂无学生
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="entry in attendanceEntries"
                :key="entry.id"
                class="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all"
                :class="{
                  'bg-green-50 border-green-200': entry.status === 'present',
                  'bg-yellow-50 border-yellow-200': entry.status === 'late',
                  'bg-blue-50 border-blue-200': entry.status === 'leave',
                  'bg-red-50 border-red-200': entry.status === 'absent',
                }"
              >
                <div class="flex items-center gap-3">
                  <div class="flex-shrink-0">
                    <div
                      class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                      :class="{
                        'bg-green-500': entry.status === 'present',
                        'bg-yellow-500': entry.status === 'late',
                        'bg-blue-500': entry.status === 'leave',
                        'bg-red-500': entry.status === 'absent',
                      }"
                    >
                      {{ getStudentName(entry.studentId)?.charAt(0) || '?' }}
                    </div>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ getStudentName(entry.studentId) }}</p>
                    <p class="text-xs text-gray-500">座号：{{ getStudentSeatNo(entry.studentId) || '-' }}</p>
                  </div>
                </div>
                <select
                  :value="entry.status"
                  @change="updateAttendanceStatus(entry.studentId, $event.target.value)"
                  :disabled="saving"
                  class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
                >
                  <option value="present">出勤</option>
                  <option value="late">迟到</option>
                  <option value="leave">请假</option>
                  <option value="absent">缺勤</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 历史记录模态框 -->
    <div
      v-if="showHistory"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="showHistory = false"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-bold text-gray-900">点名历史记录</h2>
              <button
                @click="showHistory = false"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="p-6 max-h-[70vh] overflow-y-auto">
            <div v-if="loadingHistory" class="text-center py-8 text-gray-500">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto mb-2"></div>
              加载中...
            </div>
            <div v-else-if="historySessions.length === 0" class="text-center py-8 text-gray-500">
              暂无历史记录
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="session in historySessions"
                :key="session.id"
                @click="viewHistorySession(session.id)"
                class="p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all cursor-pointer"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-gray-900">
                      {{ new Date(session.startedAt).toLocaleString('zh-CN') }}
                    </p>
                    <p v-if="session.endedAt" class="text-sm text-gray-500 mt-1">
                      结束时间：{{ new Date(session.endedAt).toLocaleString('zh-CN') }}
                    </p>
                    <p v-else class="text-sm text-amber-600 mt-1">未完成</p>
                  </div>
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史记录详情模态框 -->
    <div
      v-if="selectedHistorySession"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="selectedHistorySession = null"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl">
            <div class="flex items-center justify-between">
              <h2 class="text-2xl font-bold text-gray-900">点名详情</h2>
              <button
                @click="selectedHistorySession = null"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="p-6 max-h-[70vh] overflow-y-auto">
            <div v-if="loadingHistoryDetail" class="text-center py-8 text-gray-500">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto mb-2"></div>
              加载中...
            </div>
            <div v-else-if="historySessionDetail">
              <div class="mb-6">
                <p class="text-sm text-gray-500">开始时间</p>
                <p class="text-lg font-medium text-gray-900">
                  {{ new Date(historySessionDetail.startedAt).toLocaleString('zh-CN') }}
                </p>
                <p v-if="historySessionDetail.endedAt" class="text-sm text-gray-500 mt-2">结束时间</p>
                <p v-if="historySessionDetail.endedAt" class="text-lg font-medium text-gray-900">
                  {{ new Date(historySessionDetail.endedAt).toLocaleString('zh-CN') }}
                </p>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  v-for="entry in historySessionDetail.entries"
                  :key="entry.id"
                  class="flex items-center justify-between p-4 border border-gray-200 rounded-xl"
                  :class="{
                    'bg-green-50 border-green-200': entry.status === 'present',
                    'bg-yellow-50 border-yellow-200': entry.status === 'late',
                    'bg-blue-50 border-blue-200': entry.status === 'leave',
                    'bg-red-50 border-red-200': entry.status === 'absent',
                  }"
                >
                  <div class="flex items-center gap-3">
                    <div
                      class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                      :class="{
                        'bg-green-500': entry.status === 'present',
                        'bg-yellow-500': entry.status === 'late',
                        'bg-blue-500': entry.status === 'leave',
                        'bg-red-500': entry.status === 'absent',
                      }"
                    >
                      {{ getStudentName(entry.studentId)?.charAt(0) || '?' }}
                    </div>
                    <div>
                      <p class="font-medium text-gray-900">{{ getStudentName(entry.studentId) }}</p>
                      <p class="text-xs text-gray-500">座号：{{ getStudentSeatNo(entry.studentId) || '-' }}</p>
                    </div>
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
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type {
  ClassroomInfo,
  AttendanceSession,
  AttendanceEntry,
  AttendanceSessionWithEntries,
  StudentInfo,
  AttendanceStatus,
} from '@/types/classroomAssistant'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const classroomId = computed(() => Number(route.params.classroomId))

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const loading = ref(false)
const loadingStudents = ref(false)
const starting = ref(false)
const saving = ref(false)
const selectedClassroom = ref<ClassroomInfo | null>(null)
const students = ref<StudentInfo[]>([])
const currentSession = ref<AttendanceSession | null>(null)
const attendanceEntries = ref<AttendanceEntry[]>([])
const showHistory = ref(false)
const historySessions = ref<AttendanceSession[]>([])
const loadingHistory = ref(false)
const selectedHistorySession = ref<number | null>(null)
const historySessionDetail = ref<AttendanceSessionWithEntries | null>(null)
const loadingHistoryDetail = ref(false)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleBackToDashboard = () => {
  router.push('/teacher/class-assistant')
}

const loadClassroom = async () => {
  try {
    const classrooms = await classroomAssistantService.getMyClassrooms()
    selectedClassroom.value = classrooms.find((c) => c.id === classroomId.value) || null
  } catch (error) {
    console.error('加载班级信息失败:', error)
  }
}

const loadStudents = async () => {
  try {
    loadingStudents.value = true
    const data = await classroomAssistantService.getClassroomStudents(classroomId.value)
    students.value = data
  } catch (error) {
    console.error('加载学生列表失败:', error)
  } finally {
    loadingStudents.value = false
  }
}

const getStudentName = (studentId: number): string => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.full_name || student?.username || `学生${studentId}`
}

const getStudentSeatNo = (studentId: number): number | null => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.seat_no || null
}

const checkCurrentSession = async () => {
  try {
    const session = await classroomAssistantService.getCurrentAttendanceSession(classroomId.value)
    if (session) {
      currentSession.value = session
      attendanceEntries.value = session.entries || []
    }
  } catch (error) {
    console.error('检查当前会话失败:', error)
  }
}

const startAttendance = async () => {
  try {
    starting.value = true
    const session = await classroomAssistantService.createAttendanceSession(classroomId.value, {
      windowSeconds: 60,
    })
    currentSession.value = session
    await loadAttendanceSession(session.id)
  } catch (error: any) {
    console.error('开始点名失败:', error)
    // 检查是否是未完成会话的错误
    const errorDetail = error.response?.data?.detail || error.message || ''
    if (errorDetail.includes('未完成的点名会话')) {
      // 尝试加载未完成的会话
      await checkCurrentSession()
      if (currentSession.value) {
        alert('检测到未完成的点名会话，已自动加载。您可以继续编辑或完成该会话。')
        return
      }
    }
    // 提取详细的错误信息
    let errorMessage = '开始点名失败，请重试'
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    alert(errorMessage)
  } finally {
    starting.value = false
  }
}

const loadAttendanceSession = async (sessionId: number) => {
  try {
    loading.value = true
    const data = await classroomAssistantService.getAttendanceSession(sessionId)
    currentSession.value = data
    attendanceEntries.value = data.entries || []
  } catch (error) {
    console.error('加载点名会话失败:', error)
  } finally {
    loading.value = false
  }
}

const updateAttendanceStatus = async (studentId: number, status: string) => {
  if (!currentSession.value) return

  try {
    saving.value = true
    await classroomAssistantService.updateAttendanceEntry(currentSession.value.id, studentId, {
      status: status as AttendanceStatus,
    })
    
    // 更新本地状态
    const entry = attendanceEntries.value.find((e) => e.studentId === studentId)
    if (entry) {
      entry.status = status as AttendanceStatus
    }
  } catch (error) {
    console.error('更新考勤状态失败:', error)
    alert('更新失败，请重试')
  } finally {
    saving.value = false
  }
}

const markAllPresent = async () => {
  if (!currentSession.value) return

  try {
    saving.value = true
    await classroomAssistantService.markAllPresent(currentSession.value.id)
    
    // 更新本地状态
    attendanceEntries.value.forEach((entry) => {
      entry.status = 'present'
    })
  } catch (error) {
    console.error('一键全到失败:', error)
    alert('操作失败，请重试')
  } finally {
    saving.value = false
  }
}

const completeAttendance = async () => {
  if (!currentSession.value) return

  try {
    saving.value = true
    await classroomAssistantService.completeAttendanceSession(currentSession.value.id)
    currentSession.value = null
    attendanceEntries.value = []
    alert('点名已完成')
  } catch (error) {
    console.error('完成点名失败:', error)
    alert('完成失败，请重试')
  } finally {
    saving.value = false
  }
}

const loadHistory = async () => {
  try {
    loadingHistory.value = true
    historySessions.value = await classroomAssistantService.listAttendanceSessions(classroomId.value, false, 50)
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

const viewHistorySession = async (sessionId: number) => {
  try {
    loadingHistoryDetail.value = true
    selectedHistorySession.value = sessionId
    historySessionDetail.value = await classroomAssistantService.getAttendanceSession(sessionId)
  } catch (error) {
    console.error('加载历史记录详情失败:', error)
    alert('加载失败，请重试')
  } finally {
    loadingHistoryDetail.value = false
  }
}

// 监听历史记录模态框显示
watch(showHistory, (newVal) => {
  if (newVal) {
    loadHistory()
  }
})

onMounted(async () => {
  await loadClassroom()
  await loadStudents()
  // 检查是否有未完成的考勤会话
  await checkCurrentSession()
})
</script>
