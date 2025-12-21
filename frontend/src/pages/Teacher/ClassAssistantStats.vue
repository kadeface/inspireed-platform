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

      <div v-else class="space-y-6">
        <!-- 出勤统计 -->
        <div v-if="stats?.attendance" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">出勤统计</h2>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">{{ stats.attendance.totalSessions }}</p>
              <p class="text-sm text-gray-500">总点名次数</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-green-600">{{ stats.attendance.presentCount }}</p>
              <p class="text-sm text-gray-500">出勤</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-yellow-600">{{ stats.attendance.lateCount }}</p>
              <p class="text-sm text-gray-500">迟到</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-blue-600">{{ stats.attendance.leaveCount }}</p>
              <p class="text-sm text-gray-500">请假</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-red-600">{{ stats.attendance.absentCount }}</p>
              <p class="text-sm text-gray-500">缺勤</p>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type { ClassroomStats } from '@/types/classroomAssistant'

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

// 默认查询最近30天
const dateTo = ref(new Date().toISOString().split('T')[0])
const dateFrom = ref(
  new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
)

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
  } catch (error) {
    console.error('加载统计失败:', error)
    alert('加载统计数据失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>
