<template>
  <Transition name="drawer">
    <div v-if="modelValue" class="fixed inset-0 z-[100]">
      <!-- 遮罩层 -->
      <div
        class="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px]"
        @click="handleClose"
      ></div>

      <!-- 抽屉内容 -->
      <aside
        class="absolute right-0 top-0 flex h-full w-full max-w-2xl flex-col bg-white/95 backdrop-blur-sm shadow-2xl"
      >
        <header class="relative overflow-hidden border-b border-gray-200 bg-white/80 backdrop-blur-sm px-6 py-5">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-indigo-500 to-purple-600"></span>
          <div class="relative flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-indigo-600">
                教学助手
              </p>
              <h2 class="mt-1 text-xl font-bold text-gray-900">
                快速操作
              </h2>
              <p class="mt-1 text-sm text-gray-600">
                在授课过程中快速进行点名、考勤等操作
              </p>
            </div>
            <button
              type="button"
              class="rounded-xl p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              @click="handleClose"
            >
              <span class="sr-only">关闭</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fill-rule="evenodd"
                  d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10l-4.95-4.95A1 1 0 115.05 3.636L10 8.586z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>
        </header>

        <main class="flex-1 overflow-y-auto px-6 py-5">
          <!-- 功能标签页 -->
          <div class="mb-6">
            <div class="flex gap-2 border-b border-gray-200">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                @click="activeTab = tab.key"
                :class="[
                  'px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px',
                  activeTab === tab.key
                    ? 'text-indigo-600 border-indigo-600'
                    : 'text-gray-500 border-transparent hover:text-gray-700'
                ]"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>

          <!-- 点名考勤 -->
          <div v-if="activeTab === 'attendance'" class="space-y-4">
            <!-- 未开始点名 -->
            <div v-if="!currentAttendanceSession" class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-200 p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-blue-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">快速点名</h3>
              <p class="text-sm text-gray-600 mb-4">一键开始点名，快速记录学生出勤情况</p>
              <button
                @click="startAttendance"
                :disabled="!classroomId || startingAttendance"
                class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="!startingAttendance" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ startingAttendance ? '开始中...' : '开始点名' }}
              </button>
            </div>

            <!-- 点名进行中 -->
            <div v-else class="space-y-4">
              <!-- 会话信息 -->
              <div class="bg-white rounded-xl border border-gray-200 p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">点名进行中</h3>
                    <p class="text-sm text-gray-500 mt-1">
                      {{ formatTime(currentAttendanceSession.startedAt) }}
                    </p>
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="markAllPresent"
                      :disabled="savingAttendance"
                      class="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-all disabled:opacity-50"
                    >
                      一键全到
                    </button>
                    <button
                      @click="completeAttendance"
                      :disabled="savingAttendance"
                      class="px-3 py-1.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-600 rounded-lg shadow hover:shadow-md transition-all disabled:opacity-50"
                    >
                      完成点名
                    </button>
                  </div>
                </div>
              </div>

              <!-- 学生列表（简化版） -->
              <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div class="p-4 border-b border-gray-200 bg-gray-50">
                  <h4 class="text-sm font-semibold text-gray-900">学生考勤状态</h4>
                </div>
                <div class="p-4 max-h-[400px] overflow-y-auto">
                  <div v-if="loadingStudents" class="text-center py-8 text-gray-500">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto mb-2"></div>
                    <p class="text-sm">加载中...</p>
                  </div>
                  <div v-else-if="attendanceEntries.length === 0" class="text-center py-8 text-gray-500">
                    <p class="text-sm">暂无学生</p>
                  </div>
                  <div v-else class="grid grid-cols-2 gap-2">
                    <div
                      v-for="entry in attendanceEntries"
                      :key="entry.id"
                      class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:shadow-sm transition-all"
                      :class="getStatusClass(entry.status)"
                    >
                      <div class="flex items-center gap-2 flex-1 min-w-0">
                        <div
                          class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0"
                          :class="getStatusBgClass(entry.status)"
                        >
                          {{ getStudentInitial(entry.studentId) }}
                        </div>
                        <div class="min-w-0 flex-1">
                          <p class="text-sm font-medium text-gray-900 truncate">{{ getStudentName(entry.studentId) }}</p>
                        </div>
                      </div>
                      <select
                        :value="entry.status"
                        @change="updateAttendanceStatus(entry.studentId, ($event.target as HTMLSelectElement).value)"
                        :disabled="savingAttendance"
                        class="ml-2 px-2 py-1 text-xs border border-gray-300 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 flex-shrink-0"
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
          </div>

          <!-- 课堂表现 -->
          <div v-if="activeTab === 'behavior'" class="space-y-4">
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200 p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-green-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">记录课堂表现</h3>
              <p class="text-sm text-gray-600 mb-4">快速记录学生的积极表现</p>
              <button
                @click="openFullPage('positive-behaviors')"
                class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                进入完整功能
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 纪律记录 -->
          <div v-if="activeTab === 'discipline'" class="space-y-4">
            <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-amber-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">记录纪律</h3>
              <p class="text-sm text-gray-600 mb-4">快速记录课堂纪律事件</p>
              <button
                @click="openFullPage('discipline')"
                class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                进入完整功能
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 值日管理 -->
          <div v-if="activeTab === 'duty'" class="space-y-4">
            <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-purple-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">值日管理</h3>
              <p class="text-sm text-gray-600 mb-4">查看今日值日安排</p>
              <button
                @click="openFullPage('duty')"
                class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                进入完整功能
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </main>
      </aside>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type {
  AttendanceSessionWithEntries,
  AttendanceEntry,
  StudentInfo,
} from '@/types/classroomAssistant'

const props = defineProps<{
  modelValue: boolean
  classroomId?: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()

type TabKey = 'attendance' | 'behavior' | 'discipline' | 'duty'
const activeTab = ref<TabKey>('attendance')
const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'attendance', label: '点名考勤' },
  { key: 'behavior', label: '课堂表现' },
  { key: 'discipline', label: '纪律记录' },
  { key: 'duty', label: '值日管理' },
]

// 点名相关状态
const currentAttendanceSession = ref<AttendanceSessionWithEntries | null>(null)
const attendanceEntries = ref<AttendanceEntry[]>([])
const students = ref<StudentInfo[]>([])
const startingAttendance = ref(false)
const savingAttendance = ref(false)
const loadingStudents = ref(false)

const handleClose = () => {
  emit('update:modelValue', false)
}

// 格式化时间
const formatTime = (date: string | Date) => {
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 获取学生姓名
const getStudentName = (studentId: number): string => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.fullName || student?.username || `学生${studentId}`
}

// 获取学生首字母
const getStudentInitial = (studentId: number): string => {
  const name = getStudentName(studentId)
  return name.charAt(0) || '?'
}

// 获取状态样式类
const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    present: 'bg-green-50 border-green-200',
    late: 'bg-yellow-50 border-yellow-200',
    leave: 'bg-blue-50 border-blue-200',
    absent: 'bg-red-50 border-red-200',
  }
  return classes[status] || 'bg-gray-50 border-gray-200'
}

// 获取状态背景类
const getStatusBgClass = (status: string) => {
  const classes: Record<string, string> = {
    present: 'bg-green-500',
    late: 'bg-yellow-500',
    leave: 'bg-blue-500',
    absent: 'bg-red-500',
  }
  return classes[status] || 'bg-gray-500'
}

// 加载学生列表
const loadStudents = async () => {
  if (!props.classroomId) return
  try {
    loadingStudents.value = true
    students.value = await classroomAssistantService.getClassroomStudents(props.classroomId)
  } catch (error) {
    console.error('加载学生列表失败:', error)
  } finally {
    loadingStudents.value = false
  }
}

// 检查当前点名会话
const checkCurrentSession = async () => {
  if (!props.classroomId) return
  try {
    const session = await classroomAssistantService.getCurrentAttendanceSession(props.classroomId)
    if (session) {
      currentAttendanceSession.value = session
      attendanceEntries.value = session.entries || []
    } else {
      currentAttendanceSession.value = null
      attendanceEntries.value = []
    }
  } catch (error) {
    console.error('检查当前会话失败:', error)
  }
}

// 开始点名
const startAttendance = async () => {
  if (!props.classroomId) return
  try {
    startingAttendance.value = true
    await loadStudents()
    const session = await classroomAssistantService.createAttendanceSession(props.classroomId, {})
    // 创建后需要获取完整的会话信息（包含entries）
    const fullSession = await classroomAssistantService.getCurrentAttendanceSession(props.classroomId)
    if (fullSession) {
      currentAttendanceSession.value = fullSession
      attendanceEntries.value = fullSession.entries || []
    }
  } catch (error: any) {
    console.error('开始点名失败:', error)
    alert(error.response?.data?.detail || '开始点名失败，请重试')
  } finally {
    startingAttendance.value = false
  }
}

// 一键全到
const markAllPresent = async () => {
  if (!currentAttendanceSession.value) return
  try {
    savingAttendance.value = true
    await classroomAssistantService.markAllPresent(currentAttendanceSession.value.id)
    await checkCurrentSession()
  } catch (error: any) {
    console.error('一键全到失败:', error)
    alert(error.response?.data?.detail || '操作失败，请重试')
  } finally {
    savingAttendance.value = false
  }
}

// 更新考勤状态
const updateAttendanceStatus = async (studentId: number, status: string) => {
  if (!currentAttendanceSession.value) return
  try {
    savingAttendance.value = true
    await classroomAssistantService.updateAttendanceEntry(
      currentAttendanceSession.value.id,
      studentId,
      { status: status as any }
    )
    await checkCurrentSession()
  } catch (error: any) {
    console.error('更新考勤状态失败:', error)
    alert(error.response?.data?.detail || '更新失败，请重试')
  } finally {
    savingAttendance.value = false
  }
}

// 完成点名
const completeAttendance = async () => {
  if (!currentAttendanceSession.value) return
  try {
    savingAttendance.value = true
    await classroomAssistantService.completeAttendanceSession(currentAttendanceSession.value.id)
    currentAttendanceSession.value = null
    attendanceEntries.value = []
    handleClose()
  } catch (error: any) {
    console.error('完成点名失败:', error)
    alert(error.response?.data?.detail || '完成点名失败，请重试')
  } finally {
    savingAttendance.value = false
  }
}

// 打开完整功能页面
const openFullPage = (type: string) => {
  if (!props.classroomId) {
    router.push('/teacher/class-assistant')
    return
  }
  const routes: Record<string, string> = {
    'positive-behaviors': `/teacher/class-assistant/${props.classroomId}/positive-behaviors`,
    'discipline': `/teacher/class-assistant/${props.classroomId}/discipline`,
    'duty': `/teacher/class-assistant/${props.classroomId}/duty`,
  }
  router.push(routes[type] || '/teacher/class-assistant')
  handleClose()
}

// 监听抽屉打开，加载数据
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.classroomId) {
    loadStudents()
    checkCurrentSession()
  }
})

// 监听班级ID变化
watch(() => props.classroomId, (newId) => {
  if (newId && props.modelValue) {
    loadStudents()
    checkCurrentSession()
  }
})
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active aside,
.drawer-leave-active aside {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from aside,
.drawer-leave-to aside {
  transform: translateX(100%);
}
</style>

