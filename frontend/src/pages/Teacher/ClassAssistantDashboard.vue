<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="班级教学助手"
      subtitle="点名、考勤、纪律与值日管理"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <select
            v-model="selectedClassroomId"
            @change="loadClassroomData"
            class="px-4 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white/80 backdrop-blur-sm transition-all"
          >
            <option v-if="classrooms.length === 0" value="">暂无班级</option>
            <option
              v-for="classroom in classrooms"
              :key="classroom.id"
              :value="classroom.id"
            >
              {{ classroom.name }}
            </option>
          </select>
          <button
            @click="handleRefresh"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-xl border border-gray-200 text-gray-700 bg-white/80 backdrop-blur-sm hover:bg-white hover:shadow-md transition-all"
            :disabled="loading"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            刷新
          </button>
          <button
            @click="handleBackToDashboard"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
            title="返回教师工作台"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            返回工作台
          </button>
        </div>
      </template>
    </DashboardHeader>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 加载状态 -->
      <div
        v-if="loading && !selectedClassroomId"
        class="flex items-center justify-center py-16 text-gray-500 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg"
      >
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600 mr-3"></div>
        <span class="text-sm font-medium">正在加载...</span>
      </div>

      <!-- 未选择班级 -->
      <div
        v-else-if="!selectedClassroomId"
        class="bg-white/80 backdrop-blur-sm border border-dashed border-gray-200 rounded-2xl p-12 text-center text-gray-500 shadow-lg"
      >
        请选择一个班级开始管理
      </div>

      <!-- 班级概览 -->
      <template v-else>
        <div class="space-y-8">
          <!-- 功能入口卡片 -->
          <section>
            <div class="overview-grid">
              <!-- 点名考勤 -->
              <router-link
                :to="`/teacher/class-assistant/${selectedClassroomId}/attendance`"
                class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              >
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-blue-500 to-cyan-600"></span>
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-blue-50/80 via-transparent to-transparent"></div>

                <div class="relative flex items-start justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-blue-600">点名考勤</p>
                    <h3 class="mt-1 text-lg font-bold text-gray-900">快速点名</h3>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-blue-500 to-cyan-600">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>

                <div class="relative mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-blue-700">{{ todayAttendanceCount }}</span>
                  <span class="text-sm text-gray-500">今日点名次数</span>
                </div>

                <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
                  开始新的点名，快速记录学生出勤情况
                </p>

                <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-4 py-2 rounded-xl transition-all">
                  开始点名
                  <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </router-link>

              <!-- 课堂表现 -->
              <router-link
                :to="`/teacher/class-assistant/${selectedClassroomId}/positive-behaviors`"
                class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              >
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-green-500 to-emerald-600"></span>
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-green-50/80 via-transparent to-transparent"></div>

                <div class="relative flex items-start justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-green-600">课堂表现</p>
                    <h3 class="mt-1 text-lg font-bold text-gray-900">正面激励</h3>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-green-500 to-emerald-600">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </div>
                </div>

                <div class="relative mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-green-700">{{ leaderboardTop3.length }}</span>
                  <span class="text-sm text-gray-500">本周积分 Top 3</span>
                </div>

                <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
                  记录学生的积极表现，正向激励学习
                </p>

                <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-green-600 hover:text-green-700 hover:bg-green-50 px-4 py-2 rounded-xl transition-all">
                  查看详情
                  <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </router-link>

              <!-- 纪律记录 -->
              <router-link
                :to="`/teacher/class-assistant/${selectedClassroomId}/discipline`"
                class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              >
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-amber-500 to-orange-600"></span>
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-amber-50/80 via-transparent to-transparent"></div>

                <div class="relative flex items-start justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-amber-600">纪律记录</p>
                    <h3 class="mt-1 text-lg font-bold text-gray-900">行为管理</h3>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-amber-500 to-orange-600">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>

                <div class="relative mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-amber-700">{{ thisWeekDisciplineCount }}</span>
                  <span class="text-sm text-gray-500">本周记录</span>
                </div>

                <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
                  记录课堂纪律事件，形成可回顾的数据
                </p>

                <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-amber-600 hover:text-amber-700 hover:bg-amber-50 px-4 py-2 rounded-xl transition-all">
                  查看记录
                  <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </router-link>

              <!-- 值日管理 -->
              <router-link
                :to="`/teacher/class-assistant/${selectedClassroomId}/duty`"
                class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              >
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-purple-500 to-pink-600"></span>
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-purple-50/80 via-transparent to-transparent"></div>

                <div class="relative flex items-start justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-purple-600">值日管理</p>
                    <h3 class="mt-1 text-lg font-bold text-gray-900">轮值安排</h3>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-purple-500 to-pink-600">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>

                <div class="relative mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-purple-700">{{ todayDutyCount }}</span>
                  <span class="text-sm text-gray-500">今日值日</span>
                </div>

                <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
                  设置值日规则，自动生成轮值表
                </p>

                <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-purple-600 hover:text-purple-700 hover:bg-purple-50 px-4 py-2 rounded-xl transition-all">
                  管理值日
                  <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </router-link>

              <!-- 成员管理 -->
              <router-link
                :to="`/teacher/class-assistant/${selectedClassroomId}/members`"
                class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              >
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-gray-500 to-slate-600"></span>
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-gray-50/80 via-transparent to-transparent"></div>

                <div class="relative flex items-start justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-600">成员管理</p>
                    <h3 class="mt-1 text-lg font-bold text-gray-900">班级成员</h3>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-gray-500 to-slate-600">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                </div>

                <div class="relative mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-gray-700">—</span>
                  <span class="text-sm text-gray-500">成员管理</span>
                </div>

                <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
                  添加、编辑和移除班级成员，管理角色和权限
                </p>

                <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-xl transition-all">
                  管理成员
                  <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </router-link>

              <!-- 数据统计 -->
              <router-link
                :to="`/teacher/class-assistant/${selectedClassroomId}/stats`"
                class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
              >
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-indigo-500 to-blue-600"></span>
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-indigo-50/80 via-transparent to-transparent"></div>

                <div class="relative flex items-start justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-indigo-600">数据统计</p>
                    <h3 class="mt-1 text-lg font-bold text-gray-900">综合分析</h3>
                  </div>
                  <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-indigo-500 to-blue-600">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>

                <div class="relative mt-4 flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-indigo-700">—</span>
                  <span class="text-sm text-gray-500">综合数据</span>
                </div>

                <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
                  查看出勤率、积分、纪律等综合统计
                </p>

                <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 px-4 py-2 rounded-xl transition-all">
                  查看统计
                  <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </router-link>
            </div>
          </section>

          <!-- 今日值日提醒 -->
          <section v-if="todayDutyList.length > 0">
            <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-bold text-gray-900">今日值日</h2>
                <router-link
                  :to="`/teacher/class-assistant/${selectedClassroomId}/duty`"
                  class="text-sm text-purple-600 hover:text-purple-700 font-medium"
                >
                  查看详情 →
                </router-link>
              </div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="duty in todayDutyList"
                  :key="duty.id"
                  class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700 border border-purple-200 text-sm"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ duty.assignee_name }}
                </span>
              </div>
            </div>
          </section>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type {
  ClassroomInfo,
  PositiveBehaviorLeaderboardEntry,
  DutyAssignment,
  StudentInfo,
} from '@/types/classroomAssistant'

const router = useRouter()
const userStore = useUserStore()

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const loading = ref(false)
const classrooms = ref<ClassroomInfo[]>([])
const selectedClassroomId = ref<number | null>(null)
const todayAttendanceCount = ref(0)
const leaderboardTop3 = ref<PositiveBehaviorLeaderboardEntry[]>([])
const thisWeekDisciplineCount = ref(0)
const todayDutyCount = ref(0)
const todayDutyList = ref<DutyAssignment[]>([])
const students = ref<StudentInfo[]>([])

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleBackToDashboard = () => {
  router.push('/teacher')
}

const loadClassrooms = async () => {
  try {
    loading.value = true
    classrooms.value = await classroomAssistantService.getMyClassrooms()
    if (classrooms.value.length > 0 && !selectedClassroomId.value) {
      selectedClassroomId.value = classrooms.value[0].id
      await loadClassroomData()
    }
  } catch (error) {
    console.error('加载班级列表失败:', error)
  } finally {
    loading.value = false
  }
}

const getStudentName = (studentId: number): string => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.fullName || student?.username || `学生${studentId}`
}

const loadClassroomData = async () => {
  if (!selectedClassroomId.value) return
  
  try {
    loading.value = true
    
    // 加载学生列表
    students.value = await classroomAssistantService.getClassroomStudents(selectedClassroomId.value)
    
    // 加载今日值日
    const dutyList = await classroomAssistantService.getTodayDuty(selectedClassroomId.value)
    todayDutyList.value = dutyList
    todayDutyCount.value = dutyList.length
    
    // 加载本周积分榜 Top 3
    const weekStart = new Date()
    weekStart.setDate(weekStart.getDate() - weekStart.getDay())
    weekStart.setHours(0, 0, 0, 0)
    
    const leaderboard = await classroomAssistantService.getPositiveBehaviorLeaderboard(
      selectedClassroomId.value,
      {
        fromDate: weekStart.toISOString(),
      }
    )
    leaderboardTop3.value = leaderboard.slice(0, 3)
    
    // TODO: 加载今日点名次数和本周纪律记录数
    // 这些需要后端API支持或在前端计算
  } catch (error) {
    console.error('加载班级数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  if (selectedClassroomId.value) {
    loadClassroomData()
  } else {
    loadClassrooms()
  }
}

onMounted(() => {
  loadClassrooms()
})
</script>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .overview-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
