<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <DashboardHeader
      title="值日管理"
      subtitle="设置值日规则，自动生成轮值表"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <button
            @click="showRuleModal = true"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            创建规则
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
      <!-- 今日值日 -->
      <div class="mb-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-6">
        <h2 class="text-lg font-bold text-gray-900 mb-4">今日值日</h2>
        <div v-if="loadingToday" class="text-center py-4 text-gray-500">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto"></div>
        </div>
        <div v-else-if="todayDuty.length === 0" class="text-center py-4 text-gray-500">
          今日无值日安排
        </div>
        <div v-else class="flex flex-wrap gap-2">
          <span
            v-for="duty in todayDuty"
            :key="duty.id"
            class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm"
            :class="{
              'bg-green-50 text-green-700 border-green-200': duty.status === 'completed',
              'bg-gray-50 text-gray-700 border-gray-200': duty.status === 'pending',
            }"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            {{ getStudentName(duty.assigneeUserId) }}
            <button
              v-if="duty.status === 'pending'"
              @click="markDutyComplete(duty.id)"
              class="ml-2 text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-all"
            >
              标记完成
            </button>
          </span>
        </div>
      </div>

      <!-- 值日规则和生成 -->
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-bold text-gray-900">值日规则</h2>
        </div>
        <div class="p-6">
          <div v-if="loading" class="text-center py-8 text-gray-500">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-2"></div>
            加载中...
          </div>
          <div v-else class="space-y-4">
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
              <div>
                <p class="font-medium text-gray-900">生成值日任务</p>
                <p class="text-sm text-gray-500 mt-1">按当前规则生成未来的值日安排</p>
              </div>
              <div class="flex gap-2">
                <input
                  v-model.number="generateDays"
                  type="number"
                  min="1"
                  max="365"
                  placeholder="天数"
                  class="w-20 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  @click="generateAssignments"
                  :disabled="generating"
                  class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {{ generating ? '生成中...' : '生成任务' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 创建规则模态框 -->
    <div
      v-if="showRuleModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="showRuleModal = false"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50"></div>
        <div class="relative w-full max-w-md bg-white rounded-2xl shadow-2xl p-6">
          <h3 class="text-xl font-bold text-gray-900 mb-4">创建值日规则</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">轮换类型</label>
              <select
                v-model="newRule.rotationType"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="daily">按日轮换</option>
                <option value="weekly">按周轮换</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
              <input
                v-model="newRule.startDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">参与学生</label>
              <div class="max-h-40 overflow-y-auto border border-gray-300 rounded-lg p-2">
                <label
                  v-for="student in students"
                  :key="student.id"
                  class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="student.id"
                    v-model="newRule.memberUserIds"
                    class="rounded"
                  />
                  <span>{{ student.fullName || student.username }}</span>
                </label>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">每组人数</label>
              <input
                v-model.number="newRule.groupSize"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div class="flex gap-3 pt-4">
              <button
                @click="showRuleModal = false"
                class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all"
              >
                取消
              </button>
              <button
                @click="submitRule"
                :disabled="!newRule.rotationType || !newRule.startDate || newRule.memberUserIds.length === 0 || saving"
                class="flex-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
              >
                {{ saving ? '提交中...' : '提交' }}
              </button>
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
import type { StudentInfo, DutyAssignment, DutyRuleCreate, DutyRotationType } from '@/types/classroomAssistant'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const classroomId = computed(() => Number(route.params.classroomId))

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const loading = ref(false)
const loadingToday = ref(false)
const saving = ref(false)
const generating = ref(false)
const showRuleModal = ref(false)
const generateDays = ref(7)
const students = ref<StudentInfo[]>([])
const todayDuty = ref<DutyAssignment[]>([])
const newRule = ref<DutyRuleCreate>({
  rotationType: 'daily' as DutyRotationType,
  startDate: new Date().toISOString().split('T')[0],
  memberUserIds: [],
  groupSize: 1,
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleBack = () => {
  router.push('/teacher/class-assistant')
}

const loadData = async () => {
  await Promise.all([loadStudents(), loadTodayDuty()])
}

const loadStudents = async () => {
  try {
    const data = await classroomAssistantService.getClassroomStudents(classroomId.value)
    students.value = data
  } catch (error) {
    console.error('加载学生列表失败:', error)
  }
}

const loadTodayDuty = async () => {
  try {
    loadingToday.value = true
    const data = await classroomAssistantService.getTodayDuty(classroomId.value)
    todayDuty.value = data
  } catch (error) {
    console.error('加载今日值日失败:', error)
  } finally {
    loadingToday.value = false
  }
}

const getStudentName = (studentId: number): string => {
  const student = students.value.find((s) => s.id === studentId)
  return student?.fullName || student?.username || `学生${studentId}`
}

const submitRule = async () => {
  if (!newRule.value.rotationType || !newRule.value.startDate || newRule.value.memberUserIds.length === 0) return

  try {
    saving.value = true
    await classroomAssistantService.createDutyRule(classroomId.value, {
      ...newRule.value,
      startDate: new Date(newRule.value.startDate).toISOString(),
    })
    showRuleModal.value = false
    newRule.value = {
      rotationType: 'daily' as DutyRotationType,
      startDate: new Date().toISOString().split('T')[0],
      memberUserIds: [],
      groupSize: 1,
    }
  } catch (error) {
    console.error('创建规则失败:', error)
    alert('创建失败，请重试')
  } finally {
    saving.value = false
  }
}

const generateAssignments = async () => {
  try {
    generating.value = true
    await classroomAssistantService.generateDutyAssignments(classroomId.value, {
      days: generateDays.value,
      weeks: 0,
    })
    alert(`已生成 ${generateDays.value} 天的值日任务`)
    await loadTodayDuty()
  } catch (error) {
    console.error('生成任务失败:', error)
    alert('生成失败，请重试')
  } finally {
    generating.value = false
  }
}

const markDutyComplete = async (assignmentId: number) => {
  try {
    await classroomAssistantService.updateDutyAssignment(assignmentId, {
      status: 'completed',
    })
    await loadTodayDuty()
  } catch (error) {
    console.error('标记完成失败:', error)
    alert('操作失败，请重试')
  }
}

onMounted(() => {
  loadData()
})
</script>
