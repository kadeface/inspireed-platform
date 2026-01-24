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
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <router-link
        to="/admin/organization"
        class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white hover:shadow-lg transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">组织架构</h3>
            <p class="text-sm text-green-100">管理区域、学校、班级和人员</p>
          </div>
          <div class="text-4xl">🏢</div>
        </div>
      </router-link>

      <router-link
        to="/district-admin/exam-management"
        class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white hover:shadow-lg transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">考试管理</h3>
            <p class="text-sm text-purple-100">考试组织和成绩管理</p>
          </div>
          <div class="text-4xl">📊</div>
        </div>
      </router-link>

      <router-link
        to="/district-admin/value-added"
        class="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white hover:shadow-lg transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">增值评价</h3>
            <p class="text-sm text-orange-100">教学效果分析与评价报告</p>
          </div>
          <div class="text-4xl">📈</div>
        </div>
      </router-link>

      <router-link
        to="/admin/settings"
        class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white hover:shadow-lg transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold mb-2">系统设置</h3>
            <p class="text-sm text-blue-100">管理员和权限配置</p>
          </div>
          <div class="text-4xl">⚙️</div>
        </div>
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !dashboard" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <div class="text-gray-500">加载中...</div>
      <p class="text-sm text-gray-400 mt-2">如果加载时间过长，请检查网络连接或刷新页面</p>
    </div>
    
    <!-- Error State -->
    <div v-if="!loading && !dashboard" class="text-center py-12">
      <div class="text-red-500 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">数据加载失败</h3>
      <p class="text-gray-500 mb-4">无法加载数据看板信息，请检查：</p>
      <ul class="text-sm text-gray-500 text-left max-w-md mx-auto mb-4 space-y-1">
        <li>• 后端服务是否正常运行</li>
        <li>• 网络连接是否正常</li>
        <li>• 是否有权限访问数据</li>
      </ul>
      <button
        @click="loadDashboard"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        重试加载
      </button>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboard" class="space-y-6">
      <!-- 第一行：核心业务统计 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 考试统计 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold flex items-center">
              <span class="text-2xl mr-2">📊</span>
              考试统计
            </h2>
            <router-link to="/district-admin/exam-management" class="text-sm text-blue-600 hover:text-blue-700">
              查看详情 →
            </router-link>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="stat-card">
              <div class="text-sm text-gray-600">本学期考试</div>
              <div class="text-3xl font-bold text-purple-600">{{ examStats.totalExams }}</div>
              <div class="text-xs text-gray-500 mt-1">已完成</div>
            </div>
            <div class="stat-card">
              <div class="text-sm text-gray-600">参与学生</div>
              <div class="text-3xl font-bold text-blue-600">{{ examStats.totalStudents }}</div>
              <div class="text-xs text-gray-500 mt-1">人次</div>
            </div>
            <div class="stat-card">
              <div class="text-sm text-gray-600">成绩录入</div>
              <div class="text-3xl font-bold text-green-600">{{ examStats.completedRate }}%</div>
              <div class="text-xs text-gray-500 mt-1">完成率</div>
            </div>
            <div class="stat-card">
              <div class="text-sm text-gray-600">待处理</div>
              <div class="text-3xl font-bold text-orange-600">{{ examStats.pendingTasks }}</div>
              <div class="text-xs text-gray-500 mt-1">任务</div>
            </div>
          </div>
        </div>

        <!-- 增值评价统计 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold flex items-center">
              <span class="text-2xl mr-2">📈</span>
              增值评价
            </h2>
            <router-link to="/district-admin/value-added" class="text-sm text-orange-600 hover:text-orange-700">
              查看详情 →
            </router-link>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="stat-card">
              <div class="text-sm text-gray-600">评价报告</div>
              <div class="text-3xl font-bold text-orange-600">{{ valueAddedStats.totalReports }}</div>
              <div class="text-xs text-gray-500 mt-1">份报告</div>
            </div>
            <div class="stat-card">
              <div class="text-sm text-gray-600">平均进步</div>
              <div class="text-3xl font-bold text-green-600">+{{ valueAddedStats.avgProgress }}%</div>
              <div class="text-xs text-gray-500 mt-1">增值幅度</div>
            </div>
            <div class="stat-card">
              <div class="text-sm text-gray-600">进步学校</div>
              <div class="text-3xl font-bold text-blue-600">{{ valueAddedStats.improvedSchools }}</div>
              <div class="text-xs text-gray-500 mt-1">所学校</div>
            </div>
            <div class="stat-card">
              <div class="text-sm text-gray-600">优秀班级</div>
              <div class="text-3xl font-bold text-purple-600">{{ valueAddedStats.excellentClasses }}</div>
              <div class="text-xs text-gray-500 mt-1">个班级</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：优秀学生展示 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold flex items-center">
            <span class="text-2xl mr-2">🌟</span>
            优秀学生展示
            <span class="ml-3 text-sm font-normal text-gray-500">符合学校宣传的亮点数据</span>
          </h2>
          <el-tag type="success" size="large">本学期</el-tag>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 进步之星 -->
          <div class="achievement-card">
            <div class="card-header">
              <div class="icon-wrapper" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <span class="text-3xl">🚀</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-800">进步之星</h3>
                <p class="text-xs text-gray-500">进步幅度最大的学生</p>
              </div>
            </div>
            <div class="student-list">
              <div v-for="(student, index) in topImprovers" :key="student.id" class="student-item">
                <div class="rank-badge" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="student-info">
                  <div class="student-name">{{ student.name }}</div>
                  <div class="student-detail">{{ student.school }} · {{ student.class }}</div>
                </div>
                <div class="score-change" style="color: #67C23A;">
                  +{{ student.improvement }}%
                </div>
              </div>
            </div>
          </div>

          <!-- 成绩优异 -->
          <div class="achievement-card">
            <div class="card-header">
              <div class="icon-wrapper" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <span class="text-3xl">🏆</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-800">成绩优异</h3>
                <p class="text-xs text-gray-500">总分最高的学生</p>
              </div>
            </div>
            <div class="student-list">
              <div v-for="(student, index) in topStudents" :key="student.id" class="student-item">
                <div class="rank-badge" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="student-info">
                  <div class="student-name">{{ student.name }}</div>
                  <div class="student-detail">{{ student.school }} · {{ student.class }}</div>
                </div>
                <div class="total-score" style="color: #F56C6C;">
                  {{ student.score }}分
                </div>
              </div>
            </div>
          </div>

          <!-- 单科状元 -->
          <div class="achievement-card">
            <div class="card-header">
              <div class="icon-wrapper" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <span class="text-3xl">📚</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-800">单科状元</h3>
                <p class="text-xs text-gray-500">各学科最高分学生</p>
              </div>
            </div>
            <div class="subject-list">
              <div v-for="(item, index) in subjectToppers" :key="index" class="subject-item">
                <el-tag size="small" :type="getSubjectTagType(index)">{{ item.subject }}</el-tag>
                <div class="student-info">
                  <div class="student-name">{{ item.name }}</div>
                  <div class="student-detail">{{ item.school }}</div>
                </div>
                <div class="subject-score">{{ item.score }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 第三行：学校亮点 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center">
          <span class="text-2xl mr-2">🏫</span>
          学校亮点
          <span class="ml-3 text-sm font-normal text-gray-500">教学成果突出的学校</span>
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 最佳进步学校 -->
          <div class="school-highlight-card">
            <div class="highlight-icon" style="background: #ECF5FF;">
              <span class="text-4xl">📈</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mt-3 mb-2">最佳进步学校</h3>
            <div class="school-list">
              <div v-for="(school, index) in topImprovedSchools" :key="school.id" class="school-item">
                <div class="medal" :class="'medal-' + (index + 1)">{{ ['🥇', '🥈', '🥉'][index] }}</div>
                <div class="school-info">
                  <div class="school-name">{{ school.name }}</div>
                  <div class="school-improvement" style="color: #67C23A;">
                    平均进步 +{{ school.improvement }}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 教学质量优秀 -->
          <div class="school-highlight-card">
            <div class="highlight-icon" style="background: #FEF0F0;">
              <span class="text-4xl">⭐</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mt-3 mb-2">教学质量优秀</h3>
            <div class="school-list">
              <div v-for="(school, index) in topQualitySchools" :key="school.id" class="school-item">
                <div class="medal" :class="'medal-' + (index + 1)">{{ ['🥇', '🥈', '🥉'][index] }}</div>
                <div class="school-info">
                  <div class="school-name">{{ school.name }}</div>
                  <div class="school-score" style="color: #F56C6C;">
                    平均分 {{ school.avgScore }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 增值评价突出 -->
          <div class="school-highlight-card">
            <div class="highlight-icon" style="background: #FDF6EC;">
              <span class="text-4xl">🎯</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mt-3 mb-2">增值评价突出</h3>
            <div class="school-list">
              <div v-for="(school, index) in topValueAddedSchools" :key="school.id" class="school-item">
                <div class="medal" :class="'medal-' + (index + 1)">{{ ['🥇', '🥈', '🥉'][index] }}</div>
                <div class="school-info">
                  <div class="school-name">{{ school.name }}</div>
                  <div class="school-value" style="color: #E6A23C;">
                    增值指数 {{ school.valueIndex }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 第四行：基础数据统计（简化版） -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 用户统计（简化） -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-3 flex items-center">
            <span class="text-xl mr-2">👥</span>
            用户统计
          </h2>
          <div class="grid grid-cols-4 gap-3">
            <div class="mini-stat">
              <div class="text-xs text-gray-500">总用户</div>
              <div class="text-xl font-bold text-gray-800">{{ dashboard.user_stats.total_users }}</div>
            </div>
            <div class="mini-stat">
              <div class="text-xs text-gray-500">教师</div>
              <div class="text-xl font-bold text-blue-600">{{ dashboard.user_stats.teacher_count }}</div>
            </div>
            <div class="mini-stat">
              <div class="text-xs text-gray-500">学生</div>
              <div class="text-xl font-bold text-green-600">{{ dashboard.user_stats.student_count }}</div>
            </div>
            <div class="mini-stat">
              <div class="text-xs text-gray-500">激活率</div>
              <div class="text-xl font-bold text-purple-600">{{ activationRate }}%</div>
            </div>
          </div>
        </div>

        <!-- 内容统计（简化） -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-3 flex items-center">
            <span class="text-xl mr-2">📚</span>
            内容统计
          </h2>
          <div class="grid grid-cols-4 gap-3">
            <div class="mini-stat">
              <div class="text-xs text-gray-500">课程</div>
              <div class="text-xl font-bold text-gray-800">{{ dashboard.content_stats.total_courses }}</div>
            </div>
            <div class="mini-stat">
              <div class="text-xs text-gray-500">教案</div>
              <div class="text-xl font-bold text-blue-600">{{ dashboard.content_stats.total_lessons }}</div>
            </div>
            <div class="mini-stat">
              <div class="text-xs text-gray-500">资源</div>
              <div class="text-xl font-bold text-green-600">{{ dashboard.content_stats.total_resources }}</div>
            </div>
            <div class="mini-stat">
              <div class="text-xs text-gray-500">发布率</div>
              <div class="text-xl font-bold text-purple-600">{{ lessonPublishRate }}%</div>
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

// 考试统计数据（模拟数据，后续需要对接真实API）
const examStats = ref({
  totalExams: 12,
  totalStudents: 5420,
  completedRate: 85,
  pendingTasks: 3
})

// 增值评价统计数据（模拟数据，后续需要对接真实API）
const valueAddedStats = ref({
  totalReports: 24,
  avgProgress: 8.5,
  improvedSchools: 18,
  excellentClasses: 45
})

// 进步之星（模拟数据）
const topImprovers = ref([
  { id: 1, name: '张小明', school: '开平市第一中学', class: '高一(3)班', improvement: 15.2 },
  { id: 2, name: '李华', school: '开平市开侨中学', class: '高二(1)班', improvement: 12.8 },
  { id: 3, name: '王芳', school: '台山市华侨中学', class: '高三(2)班', improvement: 11.5 },
])

// 成绩优异（模拟数据）
const topStudents = ref([
  { id: 1, name: '陈思思', school: '开平市第一中学', class: '高三(1)班', score: 698 },
  { id: 2, name: '刘伟', school: '开平市开侨中学', class: '高三(2)班', score: 685 },
  { id: 3, name: '杨洋', school: '恩平市第一中学', class: '高三(3)班', score: 672 },
])

// 单科状元（模拟数据）
const subjectToppers = ref([
  { subject: '语文', name: '陈思思', school: '开平市第一中学', score: 138 },
  { subject: '数学', name: '刘伟', school: '开平市开侨中学', score: 145 },
  { subject: '英语', name: '杨洋', school: '恩平市第一中学', score: 142 },
  { subject: '物理', name: '赵强', school: '台山市华侨中学', score: 95 },
  { subject: '化学', name: '孙丽', school: '开平市第一中学', score: 98 },
])

// 最佳进步学校（模拟数据）
const topImprovedSchools = ref([
  { id: 1, name: '开平市第一中学', improvement: 12.5 },
  { id: 2, name: '台山市华侨中学', improvement: 10.8 },
  { id: 3, name: '恩平市第一中学', improvement: 9.6 },
])

// 教学质量优秀（模拟数据）
const topQualitySchools = ref([
  { id: 1, name: '开平市开侨中学', avgScore: 586 },
  { id: 2, name: '开平市第一中学', avgScore: 578 },
  { id: 3, name: '台山市华侨中学', avgScore: 572 },
])

// 增值评价突出（模拟数据）
const topValueAddedSchools = ref([
  { id: 1, name: '开平市第一中学', valueIndex: 1.25 },
  { id: 2, name: '台山市华侨中学', valueIndex: 1.18 },
  { id: 3, name: '恩平市第一中学', valueIndex: 1.12 },
])

// 获取学科标签类型
function getSubjectTagType(index: number): string {
  const types = ['primary', 'success', 'info', 'warning', 'danger']
  return types[index % types.length]
}

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
    // TODO: 后续需要加载考试和增值评价数据
    // await loadExamStats()
    // await loadValueAddedStats()
    // await loadTopStudents()
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

/* 优秀学生展示卡片样式 */
.achievement-card {
  @apply border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-white to-gray-50;
}

.card-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  transition: all 0.2s;
}

.student-item:hover {
  border-color: #3B82F6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  color: white;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%);
  color: white;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #CD7F32 0%, #B87333 100%);
  color: white;
}

.student-info {
  flex: 1;
}

.student-name {
  font-weight: 500;
  color: #1F2937;
  margin-bottom: 2px;
}

.student-detail {
  font-size: 12px;
  color: #6B7280;
}

.score-change,
.total-score {
  font-weight: 600;
  font-size: 16px;
}

.subject-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subject-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  transition: all 0.2s;
}

.subject-item:hover {
  border-color: #3B82F6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.subject-score {
  font-weight: 600;
  color: #3B82F6;
  margin-left: auto;
}

/* 学校亮点卡片样式 */
.school-highlight-card {
  @apply border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-white to-gray-50;
}

.highlight-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.school-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.school-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  transition: all 0.2s;
}

.school-item:hover {
  border-color: #10B981;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
}

.medal {
  font-size: 28px;
  flex-shrink: 0;
  width: 40px;
  text-align: center;
}

.school-info {
  flex: 1;
}

.school-name {
  font-weight: 500;
  color: #1F2937;
  margin-bottom: 4px;
}

.school-improvement,
.school-score,
.school-value {
  font-size: 13px;
  font-weight: 500;
}

/* 迷你统计卡片 */
.mini-stat {
  @apply p-3 bg-gray-50 rounded-lg text-center;
}

.mini-stat .text-xs {
  @apply text-gray-500;
}

.mini-stat .text-xl {
  @apply font-bold;
}
</style>

