<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="平台数据看板"
      subtitle="管理员专属 - 查看平台运行数据和统计信息"
      :user-name="userName"
      @logout="handleLogout"
    />

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="admin-dashboard">

    <!-- 快捷导航 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <router-link
        to="/admin/users"
        class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white hover:shadow-lg transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">用户管理</h3>
            <p class="text-sm text-blue-100">管理平台用户账号</p>
          </div>
          <div class="text-4xl">👥</div>
        </div>
      </router-link>

      <router-link
        to="/admin/organization"
        class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white hover:shadow-lg transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">组织架构</h3>
            <p class="text-sm text-green-100">管理区域和学校</p>
          </div>
          <div class="text-4xl">🏢</div>
        </div>
      </router-link>

      <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white opacity-50 cursor-not-allowed">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">系统设置</h3>
            <p class="text-sm text-purple-100">开发中...</p>
          </div>
          <div class="text-4xl">⚙️</div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-gray-500">加载中...</div>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboard" class="space-y-6">
      <!-- 用户统计 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center">
          <span class="text-2xl mr-2">👥</span>
          用户统计
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="stat-card">
            <div class="text-sm text-gray-600">总用户数</div>
            <div class="text-3xl font-bold text-blue-600">{{ dashboard.user_stats.total_users }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">管理员</div>
            <div class="text-2xl font-bold text-purple-600">{{ dashboard.user_stats.admin_count }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">教研员</div>
            <div class="text-2xl font-bold text-green-600">{{ dashboard.user_stats.researcher_count }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">教师</div>
            <div class="text-2xl font-bold text-orange-600">{{ dashboard.user_stats.teacher_count }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">学生</div>
            <div class="text-2xl font-bold text-indigo-600">{{ dashboard.user_stats.student_count }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">激活用户</div>
            <div class="text-2xl font-bold text-green-500">{{ dashboard.user_stats.active_users }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">未激活用户</div>
            <div class="text-2xl font-bold text-gray-500">{{ dashboard.user_stats.inactive_users }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">激活率</div>
            <div class="text-2xl font-bold text-blue-500">{{ activationRate }}%</div>
          </div>
        </div>
      </div>

      <!-- 内容统计 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center">
          <span class="text-2xl mr-2">📚</span>
          内容统计
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div class="stat-card">
            <div class="text-sm text-gray-600">课程总数</div>
            <div class="text-3xl font-bold text-purple-600">{{ dashboard.content_stats.total_courses }}</div>
            <div class="text-xs text-gray-500 mt-1">
              活跃: {{ dashboard.content_stats.active_courses }}
            </div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">教案总数</div>
            <div class="text-3xl font-bold text-blue-600">{{ dashboard.content_stats.total_lessons }}</div>
            <div class="text-xs text-gray-500 mt-1">
              已发布: {{ dashboard.content_stats.published_lessons }}
            </div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">资源总数</div>
            <div class="text-3xl font-bold text-green-600">{{ dashboard.content_stats.total_resources }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">草稿教案</div>
            <div class="text-2xl font-bold text-orange-600">{{ dashboard.content_stats.draft_lessons }}</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">课程激活率</div>
            <div class="text-2xl font-bold text-purple-500">{{ courseActivationRate }}%</div>
          </div>
          <div class="stat-card">
            <div class="text-sm text-gray-600">教案发布率</div>
            <div class="text-2xl font-bold text-blue-500">{{ lessonPublishRate }}%</div>
          </div>
        </div>
      </div>

      <!-- 活动统计 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center">
          <span class="text-2xl mr-2">📈</span>
          活动统计
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 用户增长 -->
          <div class="activity-section">
            <h3 class="text-lg font-medium mb-3 text-gray-700">用户增长</h3>
            <div class="space-y-2">
              <div class="flex justify-between items-center p-3 bg-blue-50 rounded">
                <span class="text-sm text-gray-600">今日新增</span>
                <span class="text-xl font-bold text-blue-600">{{ dashboard.activity_stats.users_created_today }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-green-50 rounded">
                <span class="text-sm text-gray-600">本周新增</span>
                <span class="text-xl font-bold text-green-600">{{ dashboard.activity_stats.users_created_this_week }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-purple-50 rounded">
                <span class="text-sm text-gray-600">本月新增</span>
                <span class="text-xl font-bold text-purple-600">{{ dashboard.activity_stats.users_created_this_month }}</span>
              </div>
            </div>
          </div>

          <!-- 教案创建 -->
          <div class="activity-section">
            <h3 class="text-lg font-medium mb-3 text-gray-700">教案创建</h3>
            <div class="space-y-2">
              <div class="flex justify-between items-center p-3 bg-orange-50 rounded">
                <span class="text-sm text-gray-600">今日创建</span>
                <span class="text-xl font-bold text-orange-600">{{ dashboard.activity_stats.lessons_created_today }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-indigo-50 rounded">
                <span class="text-sm text-gray-600">本周创建</span>
                <span class="text-xl font-bold text-indigo-600">{{ dashboard.activity_stats.lessons_created_this_week }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-pink-50 rounded">
                <span class="text-sm text-gray-600">本月创建</span>
                <span class="text-xl font-bold text-pink-600">{{ dashboard.activity_stats.lessons_created_this_month }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 更新时间 -->
      <div class="text-center text-sm text-gray-500">
        最后更新: {{ formatDate(dashboard.last_updated) }}
        <button 
          @click="refreshDashboard" 
          class="ml-3 text-blue-600 hover:text-blue-700"
        >
          🔄 刷新
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <div class="text-red-500">加载失败，请重试</div>
      <button 
        @click="loadDashboard" 
        class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        重新加载
      </button>
    </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import adminService, { type DashboardOverview } from '@/services/admin'
import { useToast } from '@/composables/useToast'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'

const router = useRouter()
const userStore = useUserStore()
const toast = useToast()
const loading = ref(true)
const dashboard = ref<DashboardOverview | null>(null)

// 用户名
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '管理员')

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

// 计算激活率
const activationRate = computed(() => {
  if (!dashboard.value || dashboard.value.user_stats.total_users === 0) return 0
  return Math.round((dashboard.value.user_stats.active_users / dashboard.value.user_stats.total_users) * 100)
})

// 计算课程激活率
const courseActivationRate = computed(() => {
  if (!dashboard.value || dashboard.value.content_stats.total_courses === 0) return 0
  return Math.round((dashboard.value.content_stats.active_courses / dashboard.value.content_stats.total_courses) * 100)
})

// 计算教案发布率
const lessonPublishRate = computed(() => {
  if (!dashboard.value || dashboard.value.content_stats.total_lessons === 0) return 0
  return Math.round((dashboard.value.content_stats.published_lessons / dashboard.value.content_stats.total_lessons) * 100)
})

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载数据看板
async function loadDashboard() {
  loading.value = true
  try {
    dashboard.value = await adminService.getDashboardOverview()
  } catch (error: any) {
    console.error('Failed to load dashboard:', error)
    toast.error(error.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
async function refreshDashboard() {
  toast.info('刷新中...')
  await loadDashboard()
  toast.success('数据已更新')
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.stat-card {
  @apply p-4 bg-gray-50 rounded-lg;
}

.activity-section {
  @apply border border-gray-200 rounded-lg p-4;
}
</style>

