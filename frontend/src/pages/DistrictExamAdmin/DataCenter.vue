<template>
  <div class="data-center">
    <!-- 页面头部 -->
    <div class="header">
      <div class="flex items-center gap-4">
        <el-button @click="router.back()" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">数据中心</h1>
          <p class="text-gray-600 mt-1 text-sm">考试数据分析与统计报告</p>
        </div>
      </div>
      <div class="header-actions">
        <el-tag v-if="currentSemester" type="success" size="large" effect="dark" class="semester-tag">
          {{ currentSemester.name }}
        </el-tag>
      </div>
    </div>

    <!-- 考试选择器 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filters">
        <el-form-item label="选择考试">
          <el-select
            v-model="selectedExamId"
            placeholder="请选择考试进行深度分析"
            style="width: 360px"
            filterable
            @change="loadExamData"
          >
            <el-option
              v-for="exam in exams"
              :key="exam.id"
              :label="`${exam.name} (${exam.exam_date ? exam.exam_date.split('T')[0] : ''})`"
              :value="exam.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadExamData" :disabled="!selectedExamId">
            <el-icon class="mr-1"><Search /></el-icon>
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据展示区域 -->
    <div v-if="overview" v-loading="loading" class="data-content space-y-8 pb-10">
      <!-- 核心指标卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="stat-card stat-blue">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">参与学生</div>
            <div class="stat-value">{{ overview.total_students }} <small>人</small></div>
          </div>
        </div>
        
        <div class="stat-card stat-green">
          <div class="stat-icon">
            <el-icon><School /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">参与学校</div>
            <div class="stat-value">{{ overview.total_schools }} <small>所</small></div>
          </div>
        </div>

        <div class="stat-card stat-purple">
          <div class="stat-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">参与班级</div>
            <div class="stat-value">{{ overview.total_classes }} <small>个</small></div>
          </div>
        </div>

        <div class="stat-card stat-orange">
          <div class="stat-icon">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">考试科目</div>
            <div class="stat-value">{{ overview.total_subjects }} <small>科</small></div>
          </div>
        </div>
      </div>

      <!-- 考试基础信息 -->
      <div class="info-strip">
        <div class="info-item">
          <span class="dot bg-blue-500"></span>
          <span class="label">考试名称：</span>
          <span class="value">{{ overview.exam_name }}</span>
        </div>
        <div class="info-item">
          <span class="dot bg-green-500"></span>
          <span class="label">类型：</span>
          <el-tag size="small" effect="light" round>{{ getExamTypeName(overview.exam_type) }}</el-tag>
        </div>
        <div class="info-item">
          <span class="dot bg-purple-500"></span>
          <span class="label">级别：</span>
          <el-tag size="small" :type="getExamLevelType(overview.exam_level)" effect="light" round>
            {{ getExamLevelName(overview.exam_level) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="dot bg-orange-500"></span>
          <span class="label">日期：</span>
          <span class="value text-gray-500 font-mono">{{ overview.exam_date.split('T')[0] }}</span>
        </div>
      </div>

      <!-- 科目统计报告 -->
      <section class="report-section">
        <div class="section-title">
          <div class="title-left">
            <el-icon><DataAnalysis /></el-icon>
            <h2>科目统计报告</h2>
          </div>
          <p class="title-desc">全域科目平均得分与表现分布直观分析</p>
        </div>
        <el-card shadow="never" class="modern-card">
          <el-table :data="overview.subject_statistics" stripe class="modern-table">
            <el-table-column prop="subject_name" label="科目名称" width="140" fixed>
              <template #default="{ row }">
                <span class="font-bold text-gray-800">{{ row.subject_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="full_score" label="满分" width="90" align="center" />
            <el-table-column prop="student_count" label="人数" width="100" align="center" />
            <el-table-column prop="average_score" label="平均分" width="110" align="center">
              <template #default="{ row }">
                <div class="score-pill">
                  <span class="score">{{ row.average_score }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="分数极值" align="center">
              <el-table-column prop="max_score" label="最高分" width="90" align="center">
                 <template #default="{ row }">
                  <span class="text-green-600 font-medium">{{ row.max_score }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="min_score" label="最低分" width="90" align="center">
                <template #default="{ row }">
                  <span class="text-gray-400">{{ row.min_score }}</span>
                </template>
              </el-table-column>
            </el-table-column>
            <el-table-column label="质量等级分布" min-width="400" align="center">
              <template #default="{ row }">
                <div class="rate-distribution">
                  <div class="rate-item">
                    <span class="rate-label">优秀</span>
                    <el-progress :percentage="row.excellent_rate" color="#67C23A" :stroke-width="8" :show-text="false" />
                    <span class="rate-value text-green-600">{{ row.excellent_rate }}%</span>
                  </div>
                  <div class="rate-item">
                    <span class="rate-label">及格</span>
                    <el-progress :percentage="row.pass_rate" color="#E6A23C" :stroke-width="8" :show-text="false" />
                    <span class="rate-value text-orange-600">{{ row.pass_rate }}%</span>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </section>

      <!-- 区县统考：学校统计 -->
      <section v-if="overview.exam_level === 'district'" class="report-section">
        <div class="section-title">
          <div class="title-left">
            <el-icon><School /></el-icon>
            <h2>各学校成绩统计</h2>
          </div>
          <p class="title-desc">对比全区各校整体教学质量与各学科差异</p>
        </div>
        <el-card shadow="never" class="modern-card">
          <el-table :data="schoolStatistics" stripe max-height="600" class="modern-table">
            <el-table-column prop="school_name" label="学校名称" width="220" fixed show-overflow-tooltip>
              <template #default="{ row }">
                <div class="flex items-center gap-2">
                  <span class="school-icon">🏫</span>
                  <span class="font-medium text-gray-900">{{ row.school_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="student_count" label="人数" width="90" align="center" />
            <el-table-column
              v-for="subject in overview.subject_statistics"
              :key="`school-${subject.subject_id}`"
              :label="subject.subject_name"
              width="130"
              align="center"
            >
              <template #header>
                <div class="subject-header">
                  <span>{{ subject.subject_name }}</span>
                  <small>平均分</small>
                </div>
              </template>
              <template #default="{ row }">
                <div :class="['subject-score', getSubjectScoreClass(row, subject.subject_id, 'average_score')]">
                  {{ getSchoolSubjectScore(row, subject.subject_id, 'average_score') }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </section>

      <!-- 班级统计 -->
      <section class="report-section">
        <div class="section-title">
          <div class="title-left">
            <el-icon><TrendCharts /></el-icon>
            <h2>{{ overview.exam_level === 'district' ? '各班级成绩统计 (全区)' : '各班级成绩统计' }}</h2>
          </div>
          <div class="flex items-center gap-4">
            <el-input
              v-model="classSearchQuery"
              placeholder="搜索班级或所属学校..."
              size="default"
              style="width: 280px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
        <el-card shadow="never" class="modern-card">
          <el-table :data="filteredClassStatistics" stripe max-height="650" class="modern-table">
            <el-table-column prop="school_name" label="所属学校" width="200" v-if="overview.exam_level === 'district'" show-overflow-tooltip />
            <el-table-column prop="classroom_name" label="班级名称" width="160" align="center">
              <template #default="{ row }">
                <span class="font-medium text-blue-600">{{ row.classroom_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="student_count" label="人数" width="90" align="center" />
            <el-table-column
              v-for="subject in overview.subject_statistics"
              :key="`class-${subject.subject_id}`"
              :label="subject.subject_name"
              min-width="160"
              align="center"
            >
              <template #default="{ row }">
                <div class="flex flex-col items-center gap-1 py-1">
                  <span :class="['font-bold', getSubjectScoreClass(row, subject.subject_id, 'average_score')]">
                    {{ getClassSubjectScore(row, subject.subject_id, 'average_score') }}
                  </span>
                  <div class="flex items-center gap-1 text-[11px] text-gray-400">
                    <span>优秀率</span>
                    <span class="text-green-500 font-medium">{{ getClassSubjectScore(row, subject.subject_id, 'excellent_rate') }}%</span>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </section>
    </div>

    <!-- 空状态 -->
    <div v-if="!overview && !loading" class="welcome-container">
      <el-empty description=" " :image-size="300">
        <template #description>
          <div class="empty-text">
            <h3 class="text-xl font-bold text-gray-700 mb-2">准备好开启数据洞察了吗？</h3>
            <p class="text-gray-400">在上方选择一个考试，系统将立即为您呈现多维度的分析看板</p>
          </div>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  ArrowLeft,
  User,
  School,
  OfficeBuilding,
  Reading,
  DataAnalysis,
  TrendCharts
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useSemesterStore } from '@/store/semester'
import { productionSameOriginApiV1, sanitizeViteApiUrlForProduction } from '@/utils/runtimeApiBase'

const router = useRouter()
const semesterStore = useSemesterStore()
const currentSemester = computed(() => semesterStore.currentSemester)

const loading = ref(false)
const selectedExamId = ref<number | null>(null)
const classSearchQuery = ref('')

const exams = ref<any[]>([])
const overview = ref<any>(null)
const schoolStatistics = ref<any[]>([])
const classroomStatistics = ref<any[]>([])

const filters = reactive({
  exam_id: null,
})

// 动态获取API基础URL
function getApiBaseUrl(): string {
  const hostname = window.location.hostname
  const protocol = window.location.protocol

  if (import.meta.env.VITE_API_BASE_URL) {
    const envApiUrl = import.meta.env.VITE_API_BASE_URL
    if (envApiUrl.startsWith('http://') || envApiUrl.startsWith('https://')) {
      const sanitized = sanitizeViteApiUrlForProduction(envApiUrl)
      if (sanitized) return sanitized
      return envApiUrl
    }
  }

  if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
    if (hostname.includes('--')) {
      const backendHostname = hostname.replace(/--\d+/, '--8000')
      return `https://${backendHostname}/api/v1`
    }
  }

  if (!import.meta.env.DEV) {
    return productionSameOriginApiV1()
  }
  const apiProtocol = protocol === 'https:' ? 'https:' : 'http:'
  return `${apiProtocol}//${hostname}:8000/api/v1`
}

const API_BASE_URL = getApiBaseUrl()

// 获取token
function getAuthToken(): string {
  return localStorage.getItem('access_token') || ''
}

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 加载考试列表
async function loadExams() {
  loading.value = true
  try {
    const response = await apiClient.get('/exams/')
    exams.value = response.data || []
  } catch (error: any) {
    console.error('加载考试列表失败:', error)
    ElMessage.error('加载考试列表失败')
  } finally {
    loading.value = false
  }
}

// 加载考试数据
async function loadExamData() {
  if (!selectedExamId.value) return

  loading.value = true
  try {
    // 获取概览
    const overviewResponse = await apiClient.get(`/exams/${selectedExamId.value}/statistics/overview`)
    overview.value = overviewResponse.data

    // 根据考试级别获取不同数据
    if (overview.value.exam_level === 'district') {
      // 区县统考：获取学校和班级统计
      const districtResponse = await apiClient.get(`/exams/${selectedExamId.value}/statistics/district`)
      schoolStatistics.value = districtResponse.data.school_statistics || []
      classroomStatistics.value = districtResponse.data.classroom_statistics || []
    } else {
      // 校级考试：获取班级统计
      const schoolResponse = await apiClient.get(`/exams/${selectedExamId.value}/statistics/school`)
      schoolStatistics.value = []
      classroomStatistics.value = schoolResponse.data.classroom_statistics || []
    }

    ElMessage.success('分析数据加载成功')
  } catch (error: any) {
    console.error('加载考试数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载考试数据失败')
  } finally {
    loading.value = false
  }
}

// 辅助函数：从学校统计中获取科目分数
function getSchoolSubjectScore(school: any, subjectId: number, field: string): any {
  const subject = school.subjects?.find((s: any) => s.subject_id === subjectId)
  return subject ? subject[field] : '-'
}

// 辅助函数：从班级统计中获取科目分数
function getClassSubjectScore(classroom: any, subjectId: number, field: string): any {
  const subject = classroom.subjects?.find((s: any) => s.subject_id === subjectId)
  return subject ? subject[field] : '-'
}

// 辅助函数：根据分数高低返回样式类
function getSubjectScoreClass(entity: any, subjectId: number, field: string): string {
  const value = entity.subjects?.find((s: any) => s.subject_id === subjectId)?.[field]
  if (typeof value !== 'number') return ''

  if (field === 'average_score') {
    if (value >= 85) return 'score-high'
    if (value >= 75) return 'score-mid'
    if (value >= 60) return 'score-low'
    return 'score-fail'
  }
  return ''
}

// 过滤班级统计
const filteredClassStatistics = computed(() => {
  if (!classSearchQuery.value) return classroomStatistics.value

  const query = classSearchQuery.value.toLowerCase()
  return classroomStatistics.value.filter((c: any) =>
    c.classroom_name?.toLowerCase().includes(query) ||
    c.school_name?.toLowerCase().includes(query)
  )
})

// 获取考试类型名称
function getExamTypeName(type: string): string {
  const typeMap: Record<string, string> = {
    monthly: '月考',
    midterm: '期中考试',
    final: '期末考试',
    mock: '模拟考试',
    unit: '单元测试',
    district_unified: '区县统考',
  }
  return typeMap[type] || type
}

// 获取考试级别名称
function getExamLevelName(level: string): string {
  const levelMap: Record<string, string> = {
    school: '校级',
    district: '区县',
    city: '市级',
  }
  return levelMap[level] || level
}

// 获取考试级别标签类型
function getExamLevelType(level: string): string {
  const typeMap: Record<string, string> = {
    school: 'info',
    district: 'warning',
    city: 'success',
  }
  return typeMap[level] || ''
}

onMounted(async () => {
  await semesterStore.fetchCurrentSemester()
  await loadExams()
})
</script>

<style scoped>
.data-center {
  padding: 24px;
  background: #f8fafc;
  min-h: 100vh;
}

/* Header Styles */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
}

/* Filter Section */
.filter-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

/* Stat Cards Modern Design */
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-label {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
}

.stat-value small {
  font-size: 14px;
  font-weight: 400;
  opacity: 0.7;
}

/* Stat Colors */
.stat-blue { background: #eff6ff; border-color: #dbeafe; color: #1d4ed8; }
.stat-blue .stat-icon { background: #dbeafe; }
.stat-green { background: #f0fdf4; border-color: #dcfce7; color: #15803d; }
.stat-green .stat-icon { background: #dcfce7; }
.stat-purple { background: #faf5ff; border-color: #f3e8ff; color: #7e22ce; }
.stat-purple .stat-icon { background: #f3e8ff; }
.stat-orange { background: #fff7ed; border-color: #ffedd5; color: #c2410c; }
.stat-orange .stat-icon { background: #ffedd5; }

/* Info Strip */
.info-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  padding: 20px 32px;
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.info-item .label {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
}

.info-item .value {
  font-size: 15px;
  color: #1e293b;
  font-weight: 600;
}

/* Report Sections */
.report-section {
  animation: fadeIn 0.5s ease-out;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 16px;
  padding: 0 4px;
}

.title-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #334155;
}

.title-left .el-icon {
  font-size: 22px;
  color: #3b82f6;
}

.title-desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 4px 0 0 32px;
}

/* Modern Card & Table */
.modern-card {
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

:deep(.modern-table) {
  --el-table-header-bg-color: #f8fafc;
  --el-table-border-color: #f1f5f9;
}

:deep(.modern-table th.el-table__cell) {
  font-weight: 600;
  color: #64748b;
  height: 56px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

:deep(.modern-table td.el-table__cell) {
  padding: 12px 0;
}

/* Score visualization */
.score-pill {
  display: inline-flex;
  padding: 4px 12px;
  background: #f1f5f9;
  border-radius: 20px;
  font-weight: 700;
  color: #2563eb;
}

.rate-distribution {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}

.rate-item {
  display: grid;
  grid-template-columns: 50px 1fr 60px;
  align-items: center;
  gap: 12px;
}

.rate-label {
  font-size: 12px;
  color: #64748b;
  text-align: right;
}

.rate-value {
  font-size: 13px;
  font-weight: 600;
  text-align: right;
}

.subject-header {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.subject-header small {
  font-size: 10px;
  font-weight: 400;
  color: #94a3b8;
}

.subject-score {
  font-weight: 600;
  font-size: 15px;
}

.score-high { color: #16a34a; }
.score-mid { color: #2563eb; }
.score-low { color: #d97706; }
.score-fail { color: #dc2626; }

/* Empty state text */
.empty-text {
  margin-top: 16px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
