<template>
  <div class="score-import">
    <div class="header">
      <h1>导入成绩</h1>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 步骤条 -->
    <div class="steps-container">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="选择考试" />
        <el-step title="下载模板" />
        <el-step title="准备数据" />
        <el-step title="上传文件" />
        <el-step title="确认导入" />
      </el-steps>
    </div>

    <!-- 主内容区域：导入流程 -->
    <el-row>
      <el-col :span="24">
        <!-- 步骤0: 选择考试 -->
        <div v-if="currentStep === 0" class="step-content">
          <el-card class="exam-select-card">
            <template #header>
              <div class="card-header">
                <span>📋 第零步：选择考试</span>
              </div>
            </template>

            <div class="exam-select-content">
              <p class="step-description">请先选择要导入成绩的考试，系统会根据考试信息生成对应的导入模板。</p>

              <el-form :model="importForm" label-width="100px" style="margin-top: 20px;">
                <el-form-item label="选择考试" required>
                  <el-select
                    v-model="importForm.exam_id"
                    placeholder="请选择考试"
                    style="width: 100%;"
                    @change="loadExamSubjects"
                  >
                    <el-option
                      v-for="exam in exams"
                      :key="exam.id"
                      :label="`${exam.name} (${exam.exam_date.split('T')[0]})`"
                      :value="exam.id"
                    />
                  </el-select>
                </el-form-item>
              </el-form>

              <el-alert
                v-if="importForm.exam_id && subjects.length > 0"
                title="考试科目信息"
                type="info"
                :closable="false"
                style="margin-top: 20px;"
              >
                <template #default>
                  <p style="margin: 8px 0;">
                    <strong>该考试包含以下科目：</strong>{{ subjects.map(s => s.subject_name || `科目ID:${s.subject_id}`).join('、') }}
                  </p>
                  <p style="margin: 8px 0; font-size: 12px; color: #909399;">
                    注意：成绩Excel中的科目列必须与上述科目名称完全匹配，不存在的科目将提示错误。
                  </p>
                </template>
              </el-alert>

              <div class="step-actions">
                <el-button
                  type="primary"
                  size="large"
                  @click="currentStep = 1"
                  :disabled="!importForm.exam_id"
                >
                  下一步：下载模板
                  <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 步骤1: 下载模板 -->
        <div v-if="currentStep === 1" class="step-content">
          <el-card class="template-card">
            <template #header>
              <div class="card-header">
                <span>📥 第一步：下载Excel模板</span>
              </div>
            </template>

            <div class="template-info">
              <h3>Excel导入模板说明</h3>
              <p>请先下载Excel模板文件，按照模板格式填写成绩数据后再上传。</p>

              <el-table :data="templateFields" border style="width: 100%; margin-top: 20px;">
                <el-table-column prop="field" label="字段名" width="120" />
                <el-table-column prop="required" label="是否必填" width="100" />
                <el-table-column prop="description" label="说明" />
                <el-table-column prop="example" label="示例" width="150" />
              </el-table>

              <el-alert
                v-if="importForm.exam_id && subjects.length > 0"
                title="当前考试科目"
                type="info"
                :closable="false"
                style="margin-top: 20px;"
              >
                <template #default>
                  <p style="margin: 8px 0;">
                    <strong>该考试包含以下科目：</strong>{{ subjects.map(s => s.subject_name || `科目ID:${s.subject_id}`).join('、') }}
                  </p>
                  <p style="margin: 8px 0; font-size: 12px; color: #909399;">
                    Excel中的"科目"列必须是上述科目名称之一。
                  </p>
                </template>
              </el-alert>
            </div>

            <div class="step-actions">
              <el-button size="large" @click="currentStep = 0">
                <el-icon><ArrowLeft /></el-icon>
                <span style="margin-left: 8px;">上一步</span>
              </el-button>
              <el-button type="primary" size="large" @click="downloadTemplate">
                <el-icon><Download /></el-icon>
                <span style="margin-left: 8px;">下载Excel模板</span>
              </el-button>
              <el-button type="success" size="large" @click="currentStep = 2">
                已下载模板，下一步
                <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 步骤2: 准备数据 -->
        <div v-if="currentStep === 2" class="step-content">
          <el-card class="data-prep-card">
            <template #header>
              <div class="card-header">
                <span>📝 第二步：准备数据</span>
              </div>
            </template>

            <div class="prep-info">
              <el-alert
                title="数据准备注意事项"
                type="warning"
                :closable="false"
                style="margin-bottom: 20px;"
              >
                <ul>
                  <li>请按照模板格式填写数据，<strong>不要修改列名</strong></li>
                  <li>所有带 <code>*</code> 的字段都是必填项</li>
                  <li><strong>考号</strong>必须是在系统中已分配的考号</li>
                  <li><strong>学籍号</strong>必须与系统中的学生学籍号一致</li>
                  <li><strong>科目名称</strong>必须与考试包含的科目名称完全匹配</li>
                  <li>原始分必须是数字，不能为空（缺考标记为0）</li>
                  <li>同一学生在同一科目只能有一条成绩记录</li>
                  <li>建议单次导入不超过 <strong>1000条</strong> 记录</li>
                </ul>
              </el-alert>

              <el-descriptions title="数据格式示例" :column="1" border style="margin-top: 20px;">
                <el-descriptions-item label="考号">
                  <code>202401001</code> - 必须是该考试已分配的考号
                </el-descriptions-item>
                <el-descriptions-item label="学籍号">
                  <code>110101200501011234</code> - 学生身份证号或学籍号
                </el-descriptions-item>
                <el-descriptions-item label="姓名">
                  <code>张三</code> - 学生姓名（用于核对）
                </el-descriptions-item>
                <el-descriptions-item label="科目">
                  <code>数学</code> - 必须是考试包含的科目之一
                </el-descriptions-item>
                <el-descriptions-item label="原始分">
                  <code>95</code> - 数字，缺考填0
                </el-descriptions-item>
                <el-descriptions-item label="缺考">
                  <code>是/否</code> - 缺考填"是"，否则留空
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="step-actions">
              <el-button size="large" @click="currentStep = 1">
                <el-icon><ArrowLeft /></el-icon>
                <span style="margin-left: 8px;">上一步</span>
              </el-button>
              <el-button type="primary" size="large" @click="currentStep = 3">
                数据已准备好，下一步
                <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 步骤3: 上传文件 -->
        <div v-if="currentStep === 3" class="step-content">
          <el-card class="upload-card">
            <template #header>
              <div class="card-header">
                <span>📤 第三步：上传文件</span>
              </div>
            </template>

            <div class="upload-area">
              <el-upload
                ref="uploadRef"
                class="upload-demo"
                drag
                action="#"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-exceed="handleExceed"
                accept=".xlsx,.xls,.csv"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 xlsx/xls/csv 文件，且不超过 10MB
                  </div>
                </template>
              </el-upload>

              <div v-if="selectedFile" class="file-info">
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
                  <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </div>

            <div class="step-actions">
              <el-button size="large" @click="currentStep = 2">
                <el-icon><ArrowLeft /></el-icon>
                <span style="margin-left: 8px;">上一步</span>
              </el-button>
              <el-button
                type="primary"
                size="large"
                @click="startImport"
                :loading="importing"
                :disabled="!selectedFile"
              >
                <el-icon><Upload /></el-icon>
                <span style="margin-left: 8px;">开始导入</span>
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 步骤4: 确认导入 -->
        <div v-if="currentStep === 4" class="step-content">
          <el-card class="result-card">
            <template #header>
              <div class="card-header">
                <span>✅ 第四步：导入完成</span>
              </div>
            </template>

            <div class="result-info">
              <el-result
                :icon="importResult.success ? 'success' : 'error'"
                :title="importResult.title"
                :sub-title="importResult.message"
              >
                <template #extra>
                  <div class="result-actions">
                    <el-button type="primary" @click="currentStep = 0; importForm.exam_id = undefined;">
                      导入更多成绩
                    </el-button>
                    <el-button @click="goBack">返回考试列表</el-button>
                  </div>
                </template>
              </el-result>

              <div v-if="importResult.task" class="task-detail">
                <el-divider />
                <h4>导入任务详情</h4>
                <el-descriptions :column="2" border style="margin-top: 15px;">
                  <el-descriptions-item label="任务名称">{{ importResult.task.task_name }}</el-descriptions-item>
                  <el-descriptions-item label="状态">
                    <el-tag :type="getTaskStatusType(importResult.task.status)">
                      {{ getTaskStatusText(importResult.task.status) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="总行数">{{ importResult.task.total_rows || 0 }}</el-descriptions-item>
                  <el-descriptions-item label="已处理">{{ importResult.task.processed_rows || 0 }}</el-descriptions-item>
                  <el-descriptions-item label="成功">{{ (importResult.task.processed_rows || 0) - (importResult.task.failed_rows || 0) }}</el-descriptions-item>
                  <el-descriptions-item label="失败">{{ importResult.task.failed_rows || 0 }}</el-descriptions-item>
                </el-descriptions>

                <div v-if="importResult.errors.length > 0" style="margin-top: 20px;">
                  <h4>错误详情</h4>
                  <el-table :data="importResult.errors" max-height="300" size="small" style="margin-top: 10px;">
                    <el-table-column prop="row" label="行号" width="80" />
                    <el-table-column prop="exam_number" label="考号" width="120" />
                    <el-table-column prop="error" label="错误信息" />
                  </el-table>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 导入记录区域（底部独立区域） -->
    <div v-if="importForm.exam_id" class="tasks-section">
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <span>📋 导入记录</span>
            <el-button size="small" @click="loadImportTasks" :loading="loadingTasks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <el-table :data="importTasks" v-loading="loadingTasks" stripe size="small" max-height="500">
          <el-table-column prop="task_name" label="任务名称" width="200" show-overflow-tooltip />
          <el-table-column prop="file_name" label="文件名" width="180" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getTaskStatusType(row.status)" size="small">
                {{ getTaskStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.progress" :status="row.progress === 100 ? 'success' : ''" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="total_rows" label="总行数" width="100" />
          <el-table-column prop="processed_rows" label="已处理" width="100" />
          <el-table-column prop="failed_rows" label="失败" width="80" />
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ row }">
              <el-button size="small" link @click="viewTaskDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 导入统计 -->
        <div class="stats-section">
          <el-divider />
          <h4>📊 导入统计</h4>
          <el-row :gutter="15" style="margin-top: 10px;">
            <el-col :span="6">
              <el-statistic title="总任务" :value="stats.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功" :value="stats.completed">
                <template #suffix>
                  <span style="color: #67c23a;">✓</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败" :value="stats.failed">
                <template #suffix>
                  <span style="color: #f56c6c;">✗</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="处理中" :value="stats.total - stats.completed - stats.failed">
                <template #suffix>
                  <span style="color: #e6a23c;">⏳</span>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="taskDetailVisible" title="导入任务详情" width="800px">
      <div v-if="currentTask">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ currentTask.task_name }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ currentTask.file_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getTaskStatusType(currentTask.status)">
              {{ getTaskStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">
            {{ currentTask.progress }}%
          </el-descriptions-item>
          <el-descriptions-item label="总行数">{{ currentTask.total_rows || 0 }}</el-descriptions-item>
          <el-descriptions-item label="已处理">{{ currentTask.processed_rows || 0 }}</el-descriptions-item>
          <el-descriptions-item label="失败">{{ currentTask.failed_rows || 0 }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentTask.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentTask.error_message" style="margin-top: 20px;">
          <h4>错误信息</h4>
          <el-alert
            :title="currentTask.error_message"
            type="error"
            :closable="false"
          />
        </div>

        <div v-if="taskErrors.length > 0" style="margin-top: 20px;">
          <h4>错误详情</h4>
          <el-table :data="taskErrors" max-height="300" size="small">
            <el-table-column prop="row" label="行号" width="80" />
            <el-table-column prop="exam_number" label="考号" width="120" />
            <el-table-column prop="error" label="错误信息" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowRight, ArrowLeft, Download, Upload, UploadFilled, Refresh } from '@element-plus/icons-vue';
import type { UploadFile } from 'element-plus';
import { examApi, importTaskApi } from '@/services/evaluation';
import type { Exam, ExamSubject } from '@/types/evaluation';
import type { ImportTask } from '@/types/evaluation';

const router = useRouter();

// 当前步骤
const currentStep = ref(0);

// 响应式数据
const loadingTasks = ref(false);
const exams = ref<Exam[]>([]);
const subjects = ref<ExamSubject[]>([]);
const importTasks = ref<ImportTask[]>([]);
const selectedFile = ref<File | null>(null);
const importing = ref(false);

// 表单数据
const importForm = reactive({
  exam_id: undefined as number | undefined,
});

// 导入结果
const importResult = reactive({
  success: false,
  title: '',
  message: '',
  task: null as ImportTask | null,
  errors: [] as any[],
});

// 任务详情
const taskDetailVisible = ref(false);
const currentTask = ref<ImportTask | null>(null);
const taskErrors = ref<any[]>([]);

// 模板字段说明
const templateFields = [
  { field: '考号*', required: '是', description: '考试分配的考号（准考证号）', example: '202401001' },
  { field: '学籍号*', required: '是', description: '学生身份证号或学籍号', example: '110101200501011234' },
  { field: '姓名', required: '否', description: '学生姓名（用于核对）', example: '张三' },
  { field: '科目*', required: '是', description: '科目名称（必须与考试科目一致）', example: '数学' },
  { field: '原始分', required: '是', description: '成绩分数（数字，缺考填0）', example: '95' },
  { field: '缺考', required: '否', description: '是否缺考（是/否，留空表示正常）', example: '否' },
];

// 统计数据
const stats = computed(() => {
  const total = importTasks.value.length;
  const completed = importTasks.value.filter(t => t.status === 'completed').length;
  const failed = importTasks.value.filter(t => t.status === 'failed').length;
  return { total, completed, failed };
});

// 返回
const goBack = () => {
  router.push('/district-admin/exams');
};

// 加载考试列表
const loadExams = async () => {
  try {
    // 不过滤状态，加载所有考试（包括草稿状态）
    exams.value = await examApi.list();
  } catch (error: any) {
    ElMessage.error('加载考试列表失败');
  }
};

// 加载考试科目（用于显示和验证）
const loadExamSubjects = async () => {
  if (!importForm.exam_id) {
    subjects.value = [];
    return;
  }

  try {
    // 获取考试的科目列表
    subjects.value = await examApi.getSubjects(importForm.exam_id);
    // 同时加载导入任务列表
    await loadImportTasks();
  } catch (error: any) {
    console.error('加载科目列表失败:', error);
    subjects.value = [];
  }
};

// 加载导入任务列表
const loadImportTasks = async () => {
  loadingTasks.value = true;
  try {
    importTasks.value = await importTaskApi.list({
      exam_id: importForm.exam_id,
    });
  } catch (error: any) {
    console.error('加载导入任务失败:', error);
  } finally {
    loadingTasks.value = false;
  }
};

// 下载模板
const downloadTemplate = () => {
  if (!importForm.exam_id) {
    ElMessage.warning('请先选择考试');
    return;
  }

  const exam = exams.value.find(e => e.id === importForm.exam_id);

  if (!exam) {
    ElMessage.error('考试信息不存在');
    return;
  }

  // 创建CSV模板（支持多科目）
  const template = [
    [`${exam.name}_成绩单`],
    ['考号*', '学籍号*', '姓名', '科目*', '原始分', '缺考'],
    ['202401001', '110101200501011234', '张三', '数学', '95', ''],
    ['202401001', '110101200501011234', '张三', '语文', '88', ''],
    ['202401002', '110101200501011235', '李四', '数学', '87', ''],
    ['202401002', '110101200501011235', '李四', '语文', '92', ''],
    ['', '', '', '', '', ''],
  ];

  const csvContent = template.map(row => row.join(',')).join('\n');
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${exam.name}_成绩导入模板.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  ElMessage.success('模板下载成功');
};

// 文件选择
const handleFileChange = (uploadFile: any) => {
  selectedFile.value = uploadFile.raw;
};

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件');
};

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

// 开始导入
const startImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件');
    return;
  }

  importing.value = true;

  try {
    const exam = exams.value.find(e => e.id === importForm.exam_id);
    const taskName = `${exam?.name}_成绩导入`;

    // 调用后端API创建导入任务
    const task = await importTaskApi.create(
      taskName,
      importForm.exam_id!,
      selectedFile.value,
      true // 自动处理
    );

    ElMessage.success('导入任务已创建，正在后台处理...');

    // 清空文件选择
    selectedFile.value = null;

    // 刷新任务列表
    await loadImportTasks();

    // 开始轮询任务状态
    await pollTaskStatus(task.id);
  } catch (error: any) {
    importResult.success = false;
    importResult.title = '导入失败';
    importResult.message = error.response?.data?.detail || '创建导入任务失败';
    importResult.task = null;
    importResult.errors = [];
    currentStep.value = 4;
  } finally {
    importing.value = false;
  }
};

// 轮询任务状态
const pollTaskStatus = async (taskId: number) => {
  const interval = setInterval(async () => {
    try {
      const task = await importTaskApi.get(taskId);

      // 更新任务列表中的对应任务
      const index = importTasks.value.findIndex(t => t.id === taskId);
      if (index !== -1) {
        importTasks.value[index] = task;
      }

      // 如果任务完成或失败，停止轮询
      if (task.status === 'completed' || task.status === 'failed') {
        clearInterval(interval);

        if (task.status === 'completed') {
          importResult.success = true;
          importResult.title = '导入成功';
          importResult.message = `成功导入 ${task.processed_rows} 条成绩记录`;
          importResult.task = task;
          importResult.errors = [];
          ElMessage.success(`成绩导入完成！成功: ${task.processed_rows} 条`);
        } else {
          // 获取错误详情
          try {
            const errorDetail = await importTaskApi.getErrors(task.id);
            importResult.success = false;
            importResult.title = '导入失败';
            importResult.message = task.error_message || '导入过程中出现错误';
            importResult.task = task;
            importResult.errors = errorDetail.errors || [];
            ElMessage.error(`成绩导入失败：${task.error_message || '未知错误'}`);
          } catch (err) {
            importResult.success = false;
            importResult.title = '导入失败';
            importResult.message = task.error_message || '导入过程中出现错误';
            importResult.task = task;
            importResult.errors = [];
            ElMessage.error(`成绩导入失败：${task.error_message || '未知错误'}`);
          }
        }

        // 进入结果页面
        currentStep.value = 4;

        // 刷新任务列表
        await loadImportTasks();
      }
    } catch (error) {
      console.error('获取任务状态失败:', error);
      clearInterval(interval);
    }
  }, 2000); // 每2秒轮询一次
};

// 查看任务详情
const viewTaskDetail = async (task: ImportTask) => {
  currentTask.value = task;

  // 如果有错误，获取错误详情
  if (task.status === 'failed' && task.id) {
    try {
      const errorDetail = await importTaskApi.getErrors(task.id);
      taskErrors.value = errorDetail.errors || [];
    } catch (error) {
      console.error('获取错误详情失败:', error);
    }
  } else {
    taskErrors.value = [];
  }

  taskDetailVisible.value = true;
};

// 获取任务状态类型
const getTaskStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  };
  return typeMap[status] || '';
};

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  };
  return textMap[status] || status;
};

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return '-';
  const date = new Date(time);
  return date.toLocaleString('zh-CN');
};

// 组件挂载
onMounted(() => {
  loadExams();
});
</script>

<style scoped>
.score-import {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.steps-container {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.step-content {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.step-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.exam-select-content,
.template-info,
.prep-info,
.upload-area,
.result-info {
  padding: 20px 0;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.upload-demo {
  width: 100%;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin: 20px 0;
}

.el-upload__text {
  font-size: 14px;
  color: #606266;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
}

.file-info {
  margin-top: 20px;
}

.tasks-section {
  margin-top: 30px;
}

.tasks-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-section {
  padding: 15px 0;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.task-detail {
  margin-top: 30px;
}

code {
  background: #F5F7FA;
  padding: 2px 6px;
  border-radius: 3px;
  color: #E6A23C;
  font-family: 'Courier New', monospace;
}
</style>
