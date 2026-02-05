<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="平台数据看板"
      subtitle="管理员专属 - 查看平台运行数据和统计信息"
      :user-name="userName"
      :role-name="roleName"
      @logout="handleLogout"
    />

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="admin-dashboard">
        <!-- 快捷导航 -->
        <DashboardQuickNav />

        <!-- Loading State (Skeleton) -->
        <div v-if="loading" class="space-y-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <el-skeleton class="bg-white p-6 rounded-lg" :rows="4" animated />
            <el-skeleton class="bg-white p-6 rounded-lg" :rows="4" animated />
          </div>
          <el-skeleton class="bg-white p-6 rounded-lg" :rows="6" animated />
          <el-skeleton class="bg-white p-6 rounded-lg" :rows="4" animated />
        </div>

        <!-- Error State -->
        <div v-else-if="!dashboard" class="text-center py-12">
          <div class="text-red-500 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">数据加载失败</h3>
          <p class="text-gray-500 mb-4">无法加载数据看板信息，请检查网络连接或权限。</p>
          <el-button type="primary" @click="loadDashboard">重试加载</el-button>
        </div>

        <!-- Dashboard Content -->
        <div v-else class="space-y-6">
          <!-- 第一行：核心业务统计 -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ExamStatPanel :stats="examStats" />
            <ValueAddedStatPanel :stats="valueAddedStats" />
          </div>

          <!-- 第二行：优秀学生展示 -->
          <StudentShowcase
            :top-improvers="topImprovers"
            :top-students="topStudents"
            :subject-toppers="subjectToppers"
          />

          <!-- 第三行：学校亮点 -->
          <SchoolHighlightPanel
            :top-improved-schools="topImprovedSchools"
            :top-quality-schools="topQualitySchools"
            :top-value-added-schools="topValueAddedSchools"
          />

          <!-- 第四行：基础数据统计 -->
          <PlatformBaseStats
            :user-stats="dashboard.user_stats"
            :content-stats="dashboard.content_stats"
            :activation-rate="activationRate"
            :lesson-publish-rate="lessonPublishRate"
          />

          <!-- 更新时间 -->
          <div
            class="text-center text-sm text-gray-500 mt-8 flex items-center justify-center gap-2"
          >
            最后更新: {{ formatDate(dashboard.last_updated) }}
            <el-button link type="primary" @click="refreshDashboard" :loading="refreshing">
              <template #icon
                ><el-icon><Refresh /></el-icon
              ></template>
              刷新
            </el-button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import adminService, {
  type DashboardOverview,
  type ExamStats,
  type ValueAddedStats,
  type StudentImprover,
  type TopStudent,
  type SubjectTopper,
  type SchoolImproved,
  type SchoolQuality,
  type SchoolValueAdded,
} from '@/services/admin'
import { useToast } from '@/composables/useToast'
import { useUserStore } from '@/store/user'
import { getRoleDisplayName } from '@/types/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

// Import new components
import DashboardQuickNav from '@/components/Admin/Dashboard/DashboardQuickNav.vue'
import ExamStatPanel from '@/components/Admin/Dashboard/ExamStatPanel.vue'
import ValueAddedStatPanel from '@/components/Admin/Dashboard/ValueAddedStatPanel.vue'
import StudentShowcase from '@/components/Admin/Dashboard/StudentShowcase.vue'
import SchoolHighlightPanel from '@/components/Admin/Dashboard/SchoolHighlightPanel.vue'
import PlatformBaseStats from '@/components/Admin/Dashboard/PlatformBaseStats.vue'

const router = useRouter()
const userStore = useUserStore()
const toast = useToast()
const loading = ref(true)
const refreshing = ref(false)
const dashboard = ref<DashboardOverview | null>(null)

// 用户名
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '管理员')
// 角色显示名
const roleName = computed(() => getRoleDisplayName(userStore.user?.role))

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

// 计算激活率
const activationRate = computed(() => {
  if (!dashboard.value || dashboard.value.user_stats.total_users === 0) return 0
  return Math.round(
    (dashboard.value.user_stats.active_users / dashboard.value.user_stats.total_users) * 100
  )
})

// 计算教案发布率
const lessonPublishRate = computed(() => {
  if (!dashboard.value || dashboard.value.content_stats.total_lessons === 0) return 0
  return Math.round(
    (dashboard.value.content_stats.published_lessons /
      dashboard.value.content_stats.total_lessons) *
      100
  )
})

// 统计数据 State
const examStats = ref<ExamStats>({
  totalExams: 0,
  totalStudents: 0,
  completedRate: 0,
  pendingTasks: 0,
})

const valueAddedStats = ref<ValueAddedStats>({
  totalReports: 0,
  avgProgress: 0,
  improvedSchools: 0,
  excellentClasses: 0,
})

// 优秀学生 State
const topImprovers = ref<StudentImprover[]>([])
const topStudents = ref<TopStudent[]>([])
const subjectToppers = ref<SubjectTopper[]>([])

// 学校亮点 State
const topImprovedSchools = ref<SchoolImproved[]>([])
const topQualitySchools = ref<SchoolQuality[]>([])
const topValueAddedSchools = ref<SchoolValueAdded[]>([])

// 格式化日期
function formatDate(dateString: string): string {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 加载数据看板
async function loadDashboard() {
  loading.value = true
  try {
    // 并行请求所有数据
    const [overviewData, examData, valueAddedData, studentData, schoolData] = await Promise.all([
      adminService.getDashboardOverview(),
      adminService.getExamStats(),
      adminService.getValueAddedStats(),
      adminService.getStudentAchievements(),
      adminService.getSchoolHighlights(),
    ])

    // 赋值
    dashboard.value = overviewData
    examStats.value = examData
    valueAddedStats.value = valueAddedData

    // 学生数据
    topImprovers.value = studentData.topImprovers
    topStudents.value = studentData.topStudents
    subjectToppers.value = studentData.subjectToppers

    // 学校数据
    topImprovedSchools.value = schoolData.topImprovedSchools
    topQualitySchools.value = schoolData.topQualitySchools
    topValueAddedSchools.value = schoolData.topValueAddedSchools
  } catch (error: any) {
    console.error('Failed to load dashboard:', error)
    toast.error(error.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
async function refreshDashboard() {
  refreshing.value = true
  await loadDashboard()
  refreshing.value = false
  toast.success('数据已更新')
}

onMounted(() => {
  loadDashboard()
})
</script>
