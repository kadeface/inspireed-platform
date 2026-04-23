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
        class="absolute right-0 top-0 flex h-full w-full max-w-2xl flex-col border-l border-slate-200/80 bg-white/96 backdrop-blur-sm shadow-[0_20px_48px_rgba(15,23,42,0.16)]"
      >
        <header class="relative overflow-hidden border-b border-slate-200 bg-gradient-to-b from-slate-50/95 to-slate-100/80 px-5 py-3 min-h-11">
          <div class="relative flex items-start justify-between gap-4">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
                教学助手
              </p>
              <h2 class="mt-1 text-xl font-bold text-slate-900">
                快速操作
              </h2>
              <p class="mt-1 text-sm text-slate-600">
                在授课过程中快速进行点名、考勤等操作
              </p>
            </div>
            <button
              type="button"
              class="h-[30px] w-[30px] rounded-lg border border-slate-200 bg-white p-1.5 text-slate-500 transition hover:border-slate-300 hover:bg-slate-50 hover:text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
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

        <main class="assistant-drawer-main">
          <!-- 功能标签页 -->
          <div class="mb-3">
            <div class="flex gap-1.5 border-b border-slate-200 pb-0.5">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                @click="activeTab = tab.key"
                :class="[
                  'relative -mb-px rounded-t-md px-3 h-9 inline-flex items-center text-sm font-medium transition-colors border-b-2',
                  activeTab === tab.key
                    ? 'text-slate-800 border-slate-500 bg-slate-100'
                    : 'text-slate-500 border-transparent hover:text-slate-700 hover:bg-slate-100/70'
                ]"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>

          <!-- 点名考勤 -->
          <div v-if="activeTab === 'attendance'" class="space-y-4">
            <!-- 未开始点名 -->
            <div v-if="!currentAttendanceSession" class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <svg class="mx-auto mb-3 h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="mb-2 text-lg font-semibold text-slate-900">快速点名</h3>
              <p class="mb-4 text-sm text-slate-600">一键开始点名，快速记录学生出勤情况</p>
              <button
                @click="startAttendance"
                :disabled="!classroomId || startingAttendance"
                class="inline-flex h-9 items-center gap-2 rounded-lg border border-slate-800 bg-slate-800 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
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
              <div class="rounded-xl border border-slate-200 bg-white p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-lg font-semibold text-slate-900">点名进行中</h3>
                    <p class="mt-1 text-sm text-slate-500">
                      {{ formatTime(currentAttendanceSession.startedAt) }}
                    </p>
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="markAllPresent"
                      :disabled="savingAttendance"
                      class="inline-flex h-9 items-center rounded-lg border border-slate-300 bg-slate-50 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-50"
                    >
                      一键全到
                    </button>
                    <button
                      @click="completeAttendance"
                      :disabled="savingAttendance"
                      class="inline-flex h-9 items-center rounded-lg border border-slate-800 bg-slate-800 px-3 text-sm font-medium text-white transition hover:bg-slate-900 disabled:opacity-50"
                    >
                      完成点名
                    </button>
                  </div>
                </div>
              </div>

              <!-- 学生列表（简化版） -->
              <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
                <div class="border-b border-slate-200 bg-slate-50 p-4">
                  <h4 class="text-sm font-semibold text-slate-900">学生考勤状态</h4>
                </div>
                <div class="p-4 max-h-[400px] overflow-y-auto">
                  <div v-if="loadingStudents" class="py-8 text-center text-slate-500">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-slate-600 mx-auto mb-2"></div>
                    <p class="text-sm">加载中...</p>
                  </div>
                  <div v-else-if="attendanceEntries.length === 0" class="py-8 text-center text-slate-500">
                    <p class="text-sm">暂无学生</p>
                  </div>
                  <div v-else class="grid grid-cols-2 gap-2">
                    <div
                      v-for="entry in attendanceEntries"
                      :key="entry.id"
                      class="flex items-center justify-between rounded-lg border border-slate-200 p-3 transition-all hover:bg-slate-50"
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
                          <p class="truncate text-sm font-medium text-slate-900">{{ getStudentName(entry.studentId) }}</p>
                        </div>
                      </div>
                      <select
                        :value="entry.status"
                        @change="updateAttendanceStatus(entry.studentId, ($event.target as HTMLSelectElement).value)"
                        :disabled="savingAttendance"
                        class="ml-2 flex-shrink-0 rounded border border-slate-300 bg-white px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-slate-400 disabled:opacity-50"
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
            <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <svg class="mx-auto mb-3 h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              <h3 class="mb-2 text-lg font-semibold text-slate-900">记录课堂表现</h3>
              <p class="mb-4 text-sm text-slate-600">快速记录学生的积极表现</p>
              <button
                @click="openFullPage('positive-behaviors')"
                class="inline-flex h-9 items-center gap-2 rounded-lg border border-slate-800 bg-slate-800 px-4 text-sm font-semibold text-white transition hover:bg-slate-900"
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
            <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <svg class="mx-auto mb-3 h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 class="mb-2 text-lg font-semibold text-slate-900">记录纪律</h3>
              <p class="mb-4 text-sm text-slate-600">快速记录课堂纪律事件</p>
              <button
                @click="openFullPage('discipline')"
                class="inline-flex h-9 items-center gap-2 rounded-lg border border-slate-800 bg-slate-800 px-4 text-sm font-semibold text-white transition hover:bg-slate-900"
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
            <div class="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <svg class="mx-auto mb-3 h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 class="mb-2 text-lg font-semibold text-slate-900">值日管理</h3>
              <p class="mb-4 text-sm text-slate-600">查看今日值日安排</p>
              <button
                @click="openFullPage('duty')"
                class="inline-flex h-9 items-center gap-2 rounded-lg border border-slate-800 bg-slate-800 px-4 text-sm font-semibold text-white transition hover:bg-slate-900"
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
    present: 'bg-white border-slate-200',
    late: 'bg-white border-slate-200',
    leave: 'bg-white border-slate-200',
    absent: 'bg-white border-slate-200',
  }
  return classes[status] || 'bg-white border-slate-200'
}

// 获取状态背景类
const getStatusBgClass = (status: string) => {
  const classes: Record<string, string> = {
    present: 'bg-slate-500',
    late: 'bg-slate-500',
    leave: 'bg-slate-500',
    absent: 'bg-slate-500',
  }
  return classes[status] || 'bg-slate-500'
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
.assistant-drawer-main {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px 18px;
  background: linear-gradient(180deg, #ffffff 0%, rgba(248, 250, 252, 0.55) 100%);
}

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

