<template>
  <div class="value-added-evaluation">
    <!-- 页面头部 -->
    <div class="page-header flex items-center gap-4 mb-8">
      <div class="flex items-center gap-4">
        <el-button @click="router.back()" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">增值评价</h1>
          <p class="text-gray-600 mt-2">教学效果分析与评价报告</p>
        </div>
      </div>
      <div class="current-semester">
        <el-tag v-if="currentSemester" type="success" size="large">
          {{ currentSemester.name }}
        </el-tag>
        <el-tag v-else type="info" size="large">未设置当前学期</el-tag>
      </div>
    </div>

    <!-- 快捷功能区 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
      <!-- 评价报告 -->
      <el-card shadow="hover" class="function-card" @click="navigateToEvaluationReport">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#409EFF"><Document /></el-icon>
          </div>
          <div class="card-info">
            <h3>评价报告</h3>
            <p class="description">查看学校和班级的增值评价报告，分析教学效果</p>
            <div class="stats">
              <el-tag size="small" type="info">{{ stats.totalReports }} 份报告</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 质量监测报告 -->
      <el-card shadow="hover" class="function-card" @click="navigateToMonitoringReports">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#17a2b8"><Document /></el-icon>
          </div>
          <div class="card-info">
            <h3>质量监测报告</h3>
            <p class="description">导入并查看小学/初中质量监测统计表，支持按学年查询</p>
            <div class="stats">
              <el-tag size="small" type="info">导入 Excel</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 学期表现 -->
      <el-card shadow="hover" class="function-card" @click="navigateToSemesterPerformance">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#67C23A"><TrendCharts /></el-icon>
          </div>
          <div class="card-info">
            <h3>学期表现</h3>
            <p class="description">分析学校和班级在不同学期的表现趋势</p>
            <div class="stats">
              <el-tag size="small" type="info">{{ stats.totalSemesters }} 个学期</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 学校对比 -->
      <el-card shadow="hover" class="function-card" @click="navigateToSchoolComparison">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#E6A23C"><School /></el-icon>
          </div>
          <div class="card-info">
            <h3>学校对比</h3>
            <p class="description">对比不同学校的教学效果和进步幅度</p>
            <div class="stats">
              <el-tag size="small" type="info">{{ stats.totalSchools }} 所学校</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 班级对比 -->
      <el-card shadow="hover" class="function-card" @click="navigateToClassComparison">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#F56C6C"><UserFilled /></el-icon>
          </div>
          <div class="card-info">
            <h3>班级对比</h3>
            <p class="description">对比不同班级的学习表现和进步情况</p>
            <div class="stats">
              <el-tag size="small" type="info">{{ stats.totalClasses }} 个班级</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 学科分析 -->
      <el-card shadow="hover" class="function-card" @click="navigateToSubjectAnalysis">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#909399"><Reading /></el-icon>
          </div>
          <div class="card-info">
            <h3>学科分析</h3>
            <p class="description">分析各学科的教学效果和学生表现</p>
            <div class="stats">
              <el-tag size="small" type="info">{{ stats.totalSubjects }} 个学科</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>

      <!-- 进步幅度 -->
      <el-card shadow="hover" class="function-card" @click="navigateToProgressAnalysis">
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="48" color="#409EFF"><DataAnalysis /></el-icon>
          </div>
          <div class="card-info">
            <h3>进步幅度</h3>
            <p class="description">深入分析学生、班级和学校的进步幅度</p>
            <div class="stats">
              <el-tag size="small" type="success">增值分析</el-tag>
            </div>
          </div>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>
    </div>

    <!-- 数据概览 -->
    <el-card shadow="never">
      <template #header>
        <div class="section-header">
          <h3>📊 数据概览</h3>
          <el-button size="small" @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-row :gutter="20" v-loading="loading">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #ecf5ff">
              <el-icon :size="32" color="#409EFF"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalReports }}</div>
              <div class="stat-label">评价报告</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f0f9ff">
              <el-icon :size="32" color="#67C23A"><School /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalSchools }}</div>
              <div class="stat-label">参与学校</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fef0f0">
              <el-icon :size="32" color="#F56C6C"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalStudents }}</div>
              <div class="stat-label">评估学生</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fdf6ec">
              <el-icon :size="32" color="#E6A23C"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avgProgress }}%</div>
              <div class="stat-label">平均进步</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 提示信息 -->
    <el-alert
      v-if="!currentSemester"
      title="提示"
      type="warning"
      description="请先在系统中设置当前学期，以便进行增值评价分析"
      :closable="false"
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  Document,
  TrendCharts,
  School,
  UserFilled,
  Reading,
  DataAnalysis,
  ArrowRight,
  Refresh,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { semesterApi } from '@/services/evaluation'

const router = useRouter()
const loading = ref(false)
const currentSemester = ref<any>(null)

// 统计数据
const stats = ref({
  totalReports: 0,
  totalSchools: 0,
  totalClasses: 0,
  totalStudents: 0,
  totalSemesters: 0,
  totalSubjects: 0,
  avgProgress: 0,
})

// 加载当前学期
async function loadCurrentSemester() {
  try {
    currentSemester.value = await semesterApi.getCurrent()
  } catch (error: any) {
    console.error('Failed to load current semester:', error)
    // 不显示错误提示，因为可能没有设置当前学期
  }
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    // TODO: 从API加载数据
    // 模拟数据
    stats.value = {
      totalReports: 12,
      totalSchools: 15,
      totalClasses: 120,
      totalStudents: 4500,
      totalSemesters: 4,
      totalSubjects: 9,
      avgProgress: 8.5,
    }

    // 获取当前学期
    await loadCurrentSemester()
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 导航方法
function navigateToEvaluationReport() {
  router.push('/district-admin/evaluation-report')
}

function navigateToSemesterPerformance() {
  router.push('/district-admin/semester-performance')
}

function navigateToSchoolComparison() {
  ElMessage.info('学校对比功能开发中...')
  // router.push('/district-admin/school-comparison')
}

function navigateToClassComparison() {
  ElMessage.info('班级对比功能开发中...')
  // router.push('/district-admin/class-comparison')
}

function navigateToSubjectAnalysis() {
  ElMessage.info('学科分析功能开发中...')
  // router.push('/district-admin/subject-analysis')
}

function navigateToProgressAnalysis() {
  ElMessage.info('进步幅度分析功能开发中...')
  // router.push('/district-admin/progress-analysis')
}

function navigateToMonitoringReports() {
  router.push('/district-admin/monitoring-reports')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.value-added-evaluation {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.function-card {
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.function-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  gap: 16px;
}

.card-icon {
  flex-shrink: 0;
}

.card-info {
  flex: 1;
}

.card-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.description {
  font-size: 14px;
  color: #606266;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.stats {
  display: flex;
  gap: 8px;
}

.card-arrow {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  color: #909399;
  font-size: 24px;
  opacity: 0;
  transition: opacity 0.3s;
}

.function-card:hover .card-arrow {
  opacity: 1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stat-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>
