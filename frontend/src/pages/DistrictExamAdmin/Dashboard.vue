<template>
  <div class="district-admin-dashboard">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1>增值评价管理</h1>
        <p class="subtitle">区县考试管理员工作台</p>
      </div>
      <div class="current-semester">
        <el-tag v-if="currentSemester" type="success" size="large">
          {{ currentSemester.name }}
        </el-tag>
        <el-tag v-else type="info" size="large">未设置当前学期</el-tag>
      </div>
    </div>

    <!-- 考试工作流区域 -->
    <el-card class="workflow-section" shadow="never">
      <template #header>
        <div class="workflow-header">
          <h2>📋 组织一次考试</h2>
          <p class="workflow-subtitle">完成以下三个步骤，即可完成增值评价数据准备</p>
        </div>
      </template>

      <!-- 工作流步骤 -->
      <div class="workflow-steps">
        <el-steps :active="0" finish-status="success" align-center>
          <el-step title="创建考试" description="设置考试基本信息" />
          <el-step title="导入考生信息" description="批量导入考生资料和考号" />
          <el-step title="导入成绩" description="批量导入考试成绩数据" />
        </el-steps>

        <!-- 快速操作按钮 -->
        <div class="workflow-actions">
          <el-button type="primary" size="large" @click="openExamDialog">
            <el-icon><Plus /></el-icon>
            <span style="margin-left: 8px;">创建新考试</span>
          </el-button>
          <el-button type="success" size="large" @click="openStudentImportDialog" :disabled="exams.length === 0">
            <el-icon><User /></el-icon>
            <span style="margin-left: 8px;">导入考生信息</span>
          </el-button>
          <el-button type="warning" size="large" @click="openScoreImportDialog" :disabled="exams.length === 0">
            <el-icon><Upload /></el-icon>
            <span style="margin-left: 8px;">导入成绩</span>
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 考试列表和状态 -->
    <el-card class="exam-list-section" shadow="never" style="margin-top: 20px;">
      <template #header>
        <div class="section-header">
          <h3>📊 考试列表</h3>
          <el-button size="small" @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="exams" v-loading="loading" stripe>
        <el-table-column prop="name" label="考试名称" width="200" />
        <el-table-column prop="exam_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ getExamTypeName(row.exam_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数据准备进度" width="200">
          <template #default="{ row }">
            <div class="progress-info">
              <el-progress
                :percentage="getExamProgress(row)"
                :status="getExamProgressStatus(row)"
                :stroke-width="8"
                :show-text="false"
              />
              <div class="progress-steps">
                <el-tag
                  :type="row.hasStudents ? 'success' : 'info'"
                  size="small"
                  style="margin-right: 8px;"
                >
                  {{ row.hasStudents ? '✓' : '○' }} 考生信息
                </el-tag>
                <el-tag
                  :type="row.hasScores ? 'success' : 'info'"
                  size="small"
                >
                  {{ row.hasScores ? '✓' : '○' }} 成绩数据
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="importStudentsForExam(row)">
              <el-icon><User /></el-icon>
              导入考生
            </el-button>
            <el-button size="small" link @click="importScoresForExam(row)">
              <el-icon><Upload /></el-icon>
              导入成绩
            </el-button>
            <el-button size="small" link type="danger" @click="deleteExam(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 其他功能区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 学期管理 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="openSemesterDialog">
          <div class="card-icon">
            <el-icon :size="40" color="#409eff">
              <component :is="'Calendar'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>学期管理</h3>
            <p>创建和管理学期</p>
            <div class="card-stats">
              <span>{{ semesters.length }} 个学期</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 评价报告 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="openEvaluationDialog">
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'DataAnalysis'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>评价报告</h3>
            <p>生成增值评价报告</p>
            <div class="card-stats">
              <span>{{ evaluations.length }} 个评价</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 学期表现 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="openPerformanceDialog">
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'TrendCharts'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>学期表现</h3>
            <p>查看学期统计</p>
            <div class="card-stats">
              <span>数据分析</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 导入任务 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="viewImportTasks">
          <div class="card-icon">
            <el-icon :size="40" color="#e6a23c">
              <component :is="'List'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>导入任务</h3>
            <p>查看导入历史</p>
            <div class="card-stats">
              <span>{{ importTasks.length }} 个任务</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学期管理对话框 -->
    <el-dialog
      v-model="semesterDialogVisible"
      title="学期管理"
      width="900px"
      @close="resetSemesterForm"
    >
      <!-- 快速创建学期表单 -->
      <div class="quick-create-section">
        <h4>快速创建学期</h4>
        <el-form :model="semesterForm" :rules="semesterRules" ref="semesterFormRef" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="学年" prop="year">
                <el-input
                  v-model="semesterForm.year"
                  placeholder="请输入学年，格式：2023-2024"
                  maxlength="9"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="学期类型" prop="semester_type">
                <el-radio-group v-model="semesterForm.semester_type">
                  <el-radio value="up">上学期</el-radio>
                  <el-radio value="down">下学期</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期" prop="start_date">
                <el-date-picker
                  v-model="semesterForm.start_date"
                  type="date"
                  placeholder="开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期" prop="end_date">
                <el-date-picker
                  v-model="semesterForm.end_date"
                  type="date"
                  placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="学期名称" prop="name">
            <el-input v-model="semesterForm.name" placeholder="自动生成或手动输入">
              <template #append>
                <el-button @click="generateSemesterName">自动生成</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="createSemester" :loading="semesterSubmitting">
              创建学期
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 学期列表 -->
      <div class="semester-list-section">
        <h4>学期列表</h4>
        <el-table :data="semesters" max-height="300" size="small">
          <el-table-column prop="name" label="名称" width="180" />
          <el-table-column prop="year" label="学年" width="80" />
          <el-table-column prop="semester_type" label="类型" width="80">
            <template #default="{ row }">
              {{ row.semester_type === 'up' ? '上' : '下' }}
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始" width="110" />
          <el-table-column prop="end_date" label="结束" width="110" />
          <el-table-column prop="is_current" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_current ? 'success' : 'info'" size="small">
                {{ row.is_current ? '当前' : '非当前' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button
                v-if="!row.is_current"
                size="small"
                type="success"
                link
                @click.stop="setCurrentSemester(row)"
              >
                设为当前
              </el-button>
              <el-button size="small" link @click.stop="deleteSemester(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 考试管理对话框 -->
    <el-dialog
      v-model="examDialogVisible"
      title="考试管理"
      width="1000px"
      @close="resetExamForm"
    >
      <!-- 快速创建考试表单 -->
      <div class="quick-create-section">
        <h4>快速创建考试</h4>
        <el-form :model="examForm" :rules="examRules" ref="examFormRef" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="考试名称" prop="name">
                <el-input v-model="examForm.name" placeholder="请输入考试名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="考试类型" prop="exam_type">
                <el-select v-model="examForm.exam_type" placeholder="选择类型" style="width: 100%;">
                  <el-option label="期中考试" value="midterm" />
                  <el-option label="期末考试" value="final" />
                  <el-option label="月考" value="monthly" />
                  <el-option label="模考" value="mock" />
                  <el-option label="统考" value="unified" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="学期" prop="semester_id">
                <el-select v-model="examForm.semester_id" placeholder="选择学期" style="width: 100%;">
                  <el-option
                    v-for="semester in semesters"
                    :key="semester.id"
                    :label="semester.name"
                    :value="semester.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="年级" prop="grade_id">
                <el-select v-model="examForm.grade_id" placeholder="选择年级" clearable style="width: 100%;">
                  <el-option
                    v-for="grade in grades"
                    :key="grade.id"
                    :label="grade.name"
                    :value="grade.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="考试日期" prop="exam_date">
                <el-date-picker
                  v-model="examForm.exam_date"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item>
            <el-button type="primary" @click="createExam" :loading="examSubmitting">
              创建考试
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 考试列表 -->
      <div class="exam-list-section">
        <h4>考试列表</h4>
        <el-table :data="exams" max-height="300" size="small">
          <el-table-column prop="name" label="考试名称" width="180" />
          <el-table-column prop="exam_type" label="类型" width="90">
            <template #default="{ row }">
              <el-tag size="small">{{ getExamTypeName(row.exam_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusName(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="exam_date" label="日期" width="110" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" link @click.stop="deleteExam(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 导入考生信息对话框 -->
    <el-dialog
      v-model="studentImportDialogVisible"
      title="导入考生信息"
      width="600px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="考生信息导入功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>批量导入考生基本资料</li>
          <li>Excel模板下载</li>
          <li>数据验证和错误提示</li>
          <li>导入进度显示</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 导入成绩对话框 -->
    <el-dialog
      v-model="scoreImportDialogVisible"
      title="导入成绩"
      width="700px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="成绩导入功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>Excel成绩单上传</li>
          <li>自动关联考试和科目</li>
          <li>数据验证和查重</li>
          <li>实时导入进度</li>
          <li>错误报告下载</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 评价报告对话框 -->
    <el-dialog
      v-model="evaluationDialogVisible"
      title="评价报告"
      width="700px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="评价报告功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>基线考试与结束考试对比</li>
          <li>增值评价自动计算</li>
          <li>多维度数据分析</li>
          <li>可视化图表展示</li>
          <li>报告导出</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 学期表现对话框 -->
    <el-dialog
      v-model="performanceDialogVisible"
      title="学期表现"
      width="700px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="学期表现功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>学期整体表现统计</li>
          <li>各学科成绩分析</li>
          <li>进步趋势展示</li>
          <li>优秀率/合格率对比</li>
          <li>数据可视化图表</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { semesterApi, examApi } from '@/services/evaluation';
import { curriculumService } from '@/services/curriculum';
import type { Semester, Exam } from '@/types/evaluation';
import type { Grade } from '@/types/curriculum';

// 扩展 Exam 类型以包含数据准备状态
interface ExamWithStatus extends Exam {
  hasStudents?: boolean;
  hasScores?: boolean;
}

const router = useRouter();

// 响应式数据
const loading = ref(false);
const semesters = ref<Semester[]>([]);
const exams = ref<ExamWithStatus[]>([]);
const grades = ref<Grade[]>([]);
const currentSemester = ref<Semester | null>(null);
const importTasks = ref([]);
const evaluations = ref([]);

// 对话框显示状态
const semesterDialogVisible = ref(false);
const examDialogVisible = ref(false);
const studentImportDialogVisible = ref(false);
const scoreImportDialogVisible = ref(false);
const evaluationDialogVisible = ref(false);
const performanceDialogVisible = ref(false);

// 学期表单
const semesterForm = reactive({
  year: `${new Date().getFullYear()}-${new Date().getFullYear() + 1}`,
  semester_type: 'up', // 'up' 表示上学期, 'down' 表示下学期
  name: '',
  start_date: '',
  end_date: '',
});

const semesterRules = {
  year: [
    { required: true, message: '请输入学年', trigger: 'blur' },
    {
      pattern: /^\d{4}-\d{4}$/,
      message: '学年格式不正确，应为：2023-2024',
      trigger: 'blur'
    }
  ],
  semester_type: [{ required: true, message: '请选择学期类型', trigger: 'change' }],
  name: [{ required: true, message: '请输入学期名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
};

const semesterFormRef = ref<FormInstance>();
const semesterSubmitting = ref(false);

// 考试表单
const examForm = reactive({
  name: '',
  exam_type: '',
  grade_id: undefined,
  semester_id: undefined,
  exam_date: '',
  description: '',
});

const examRules = {
  name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  semester_id: [{ required: true, message: '请选择学期', trigger: 'change' }],
  exam_date: [{ required: true, message: '请选择考试日期', trigger: 'change' }],
};

const examFormRef = ref<FormInstance>();
const examSubmitting = ref(false);

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    semesters.value = await semesterApi.list();
    const examsList = await examApi.list({ skip: 0, limit: 100 });
    
    // 为每个考试添加数据准备状态（这里需要调用API获取实际状态）
    // 暂时使用模拟数据，实际应该从后端获取
    exams.value = examsList.map((exam: Exam) => ({
      ...exam,
      hasStudents: false, // TODO: 从API获取是否有考生映射
      hasScores: false, // TODO: 从API获取是否有成绩数据
    })) as ExamWithStatus[];
    
    grades.value = await curriculumService.getGrades();

    // 查找当前学期
    currentSemester.value = semesters.value.find(s => s.is_current) || null;
  } catch (error: any) {
    console.error('加载数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 生成学期名称
const generateSemesterName = () => {
  const semesterText = semesterForm.semester_type === 'up' ? '上学期' : '下学期';
  semesterForm.name = `${semesterForm.year}学年${semesterText}`;
};

// 监听学期表单变化
watch(
  () => [semesterForm.year, semesterForm.semester_type],
  () => {
    generateSemesterName();
  }
);

// 打开对话框方法
const openSemesterDialog = () => {
  router.push('/district-admin/semesters');
};

const openExamDialog = () => {
  router.push('/district-admin/exam-management');
};

const openStudentImportDialog = () => {
  router.push('/district-admin/student-import');
};

const openScoreImportDialog = () => {
  router.push('/district-admin/score-import');
};

const openEvaluationDialog = () => {
  router.push('/district-admin/evaluation-report');
};

const openPerformanceDialog = () => {
  router.push('/district-admin/semester-performance');
};

const viewImportTasks = () => {
  router.push('/district-admin/score-import');
};

// 为指定考试导入考生信息
const importStudentsForExam = (exam: Exam) => {
  router.push({
    path: '/district-admin/student-import',
    query: { exam_id: exam.id.toString() }
  });
};

// 为指定考试导入成绩
const importScoresForExam = (exam: Exam) => {
  router.push({
    path: '/district-admin/score-import',
    query: { exam_id: exam.id.toString() }
  });
};

// 计算考试数据准备进度
const getExamProgress = (exam: ExamWithStatus): number => {
  let progress = 0;
  if (exam.hasStudents) progress += 50;
  if (exam.hasScores) progress += 50;
  return progress;
};

// 获取进度状态
const getExamProgressStatus = (exam: ExamWithStatus): string => {
  if (exam.hasStudents && exam.hasScores) return 'success';
  if (exam.hasStudents || exam.hasScores) return 'warning';
  return '';
};

// 学期操作
const createSemester = async () => {
  const valid = await semesterFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  semesterSubmitting.value = true;
  try {
    await semesterApi.create({
      year: semesterForm.year,
      semester_type: semesterForm.semester_type,
      name: semesterForm.name,
      start_date: semesterForm.start_date + 'T00:00:00', // 转换为完整的 datetime 格式
      end_date: semesterForm.end_date + 'T00:00:00', // 转换为完整的 datetime 格式
      is_current: false,
    });
    ElMessage.success('创建成功');
    resetSemesterForm();
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败');
  } finally {
    semesterSubmitting.value = false;
  }
};

const setCurrentSemester = async (semester: Semester) => {
  try {
    await ElMessageBox.confirm(
      `确定要将"${semester.name}"设为当前学期吗？`,
      '确认设置',
      { type: 'info' }
    );
    await semesterApi.update(semester.id, { is_current: true });
    ElMessage.success('设置成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '设置失败');
    }
  }
};

const deleteSemester = async (semester: Semester) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学期"${semester.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    );
    await semesterApi.delete(semester.id);
    ElMessage.success('删除成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

const resetSemesterForm = () => {
  const currentYear = new Date().getFullYear();
  semesterForm.year = `${currentYear}-${currentYear + 1}`;
  semesterForm.semester_type = 'up'; // 'up' 表示上学期
  semesterForm.name = '';
  semesterForm.start_date = '';
  semesterForm.end_date = '';
  generateSemesterName();
  semesterFormRef.value?.resetFields();
};

// 考试操作
const createExam = async () => {
  const valid = await examFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  examSubmitting.value = true;
  try {
    await examApi.create({
      name: examForm.name,
      exam_type: examForm.exam_type as any,
      grade_id: examForm.grade_id,
      semester_id: examForm.semester_id!,
      exam_date: examForm.exam_date,
      description: examForm.description,
    });
    ElMessage.success('创建成功');
    resetExamForm();
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败');
  } finally {
    examSubmitting.value = false;
  }
};

const deleteExam = async (exam: Exam) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除考试"${exam.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    );
    await examApi.delete(exam.id);
    ElMessage.success('删除成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

const resetExamForm = () => {
  examForm.name = '';
  examForm.exam_type = '';
  examForm.grade_id = undefined;
  examForm.semester_id = undefined;
  examForm.exam_date = '';
  examForm.description = '';
  examFormRef.value?.resetFields();
};

// 辅助函数
const getExamTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    midterm: '期中',
    final: '期末',
    monthly: '月考',
    mock: '模考',
    unified: '统考',
  };
  return typeMap[type] || type;
};

const getStatusName = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    scheduled: '已安排',
    in_progress: '进行中',
    completed: '已完成',
  };
  return statusMap[status] || status;
};

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    draft: 'info',
    scheduled: '',
    in_progress: 'warning',
    completed: 'success',
  };
  return typeMap[status] || '';
};

// 组件挂载
onMounted(() => {
  loadData();
  generateSemesterName();
});
</script>

<style scoped>
.district-admin-dashboard {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #909399;
}

.current-semester {
  flex-shrink: 0;
}

.cards-container {
  margin-bottom: 20px;
}

.function-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.function-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.function-card :deep(.el-card__body) {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: #f5f7fa;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #909399;
}

.card-stats {
  font-size: 13px;
  color: #67c23a;
  font-weight: 500;
}

.card-arrow {
  flex-shrink: 0;
  color: #c0c4cc;
  transition: color 0.3s;
}

.function-card:hover .card-arrow {
  color: #409eff;
}

/* 工作流区域样式 */
.workflow-section {
  margin-bottom: 20px;
}

.workflow-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.workflow-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.workflow-subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.workflow-steps {
  padding: 20px 0;
}

.workflow-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
  flex-wrap: wrap;
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

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-steps {
  display: flex;
  align-items: center;
}

.quick-create-section {
  margin-bottom: 20px;
}

.quick-create-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.semester-list-section h4,
.exam-list-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .function-card :deep(.el-card__body) {
    padding: 16px;
  }

  .card-icon {
    width: 48px;
    height: 48px;
  }
}
</style>
