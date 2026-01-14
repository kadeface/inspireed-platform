<template>
  <div class="score-import">
    <div class="header">
      <h1>导入成绩</h1>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 导入流程 -->
    <el-row :gutter="20">
      <!-- 左侧：上传区域 -->
      <el-col :span="14">
        <el-card class="upload-section">
          <template #header>
            <div class="card-header">
              <span>📤 上传成绩单</span>
            </div>
          </template>

          <!-- 选择考试 -->
          <el-form :model="importForm" label-width="100px" style="margin-bottom: 20px;">
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
            
            <el-alert
              v-if="importForm.exam_id && subjects.length > 0"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            >
              <template #title>
                <span>该考试包含以下科目：{{ subjects.map(s => s.subject_name || `科目ID:${s.subject_id}`).join('、') }}</span>
              </template>
              <template #default>
                <p style="margin: 8px 0 0 0; font-size: 12px;">
                  成绩Excel中的科目列必须与上述科目名称完全匹配，不存在的科目将提示错误。
                </p>
              </template>
            </el-alert>
          </el-form>

          <!-- 上传区域 -->
          <div v-if="importForm.exam_id">
            <el-divider />

            <div class="template-download">
              <h4>📥 第一步：下载Excel模板</h4>
              <p>请先下载成绩导入模板，按照模板格式填写成绩数据。</p>
              <el-button type="primary" @click="downloadTemplate">
                <el-icon><Download /></el-icon>
                <span style="margin-left: 8px;">下载Excel模板</span>
              </el-button>
            </div>

            <el-divider />

            <div class="upload-area">
              <h4>📤 第二步：上传成绩单</h4>
              <el-upload
                ref="uploadRef"
                class="upload-demo"
                drag
                action="#"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-exceed="handleExceed"
                accept=".xlsx,.xls"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    只能上传 xlsx/xls 文件，且不超过 10MB
                  </div>
                </template>
              </el-upload>

              <div v-if="selectedFile" class="file-info">
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
                  <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </div>

            <div class="upload-actions">
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
          </div>

          <el-empty v-else description="请先选择考试" />
        </el-card>
      </el-col>

      <!-- 右侧：导入任务列表 -->
      <el-col :span="10">
        <el-card class="tasks-section">
          <template #header>
            <div class="card-header">
              <span>📋 导入记录</span>
              <el-button size="small" @click="loadImportTasks" :loading="loadingTasks">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <el-table :data="importTasks" v-loading="loadingTasks" stripe size="small">
            <el-table-column prop="task_name" label="任务名称" width="150" show-overflow-tooltip />
            <el-table-column prop="file_name" label="文件名" width="120" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getTaskStatusType(row.status)" size="small">
                  {{ getTaskStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :status="row.progress === 100 ? 'success' : ''" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" link @click="viewTaskDetail(row)">详情</el-button>
                <el-button
                  v-if="row.status === 'failed'"
                  size="small"
                  link
                  type="primary"
                  @click="retryTask(row)"
                >
                  重试
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 导入统计 -->
        <el-card class="stats-card" style="margin-top: 20px;">
          <template #header>
            <span>📊 导入统计</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="总任务数" :value="stats.total" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="成功" :value="stats.completed">
                <template #suffix>
                  <span style="color: #67c23a;">✓</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="失败" :value="stats.failed">
                <template #suffix>
                  <span style="color: #f56c6c;">✗</span>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

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
import type { UploadFile } from 'element-plus';
import { examApi, importTaskApi } from '@/services/evaluation';
import type { Exam, ExamSubject } from '@/types/evaluation';
import type { ImportTask } from '@/types/evaluation';

const router = useRouter();

// 响应式数据
const loadingTasks = ref(false);
const exams = ref<Exam[]>([]);
const subjects = ref<ExamSubject[]>([]);
const importTasks = ref<ImportTask[]>([]);
const selectedFile = ref<File | null>(null);
const importing = ref(false);

// 表单数据
const importForm = reactive({
  exam_id: undefined,
});

// 任务详情
const taskDetailVisible = ref(false);
const currentTask = ref<ImportTask | null>(null);
const taskErrors = ref<any[]>([]);

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
    exams.value = await examApi.list({ status: 'scheduled,in_progress,completed' });
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
    ['202401001', '11010120200101', '张三', '数学', '95', ''],
    ['202401001', '11010120200101', '张三', '语文', '88', ''],
    ['202401002', '11010120200102', '李四', '数学', '87', ''],
    ['202401002', '11010120200102', '李四', '语文', '92', ''],
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
    pollTaskStatus(task.id);
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建导入任务失败');
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
          ElMessage.success(`成绩导入完成！成功: ${task.processed_rows} 条`);
        } else {
          ElMessage.error(`成绩导入失败：${task.error_message || '未知错误'}`);
        }

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

// 重试任务
const retryTask = async (task: ImportTask) => {
  try {
    await importTaskApi.retry(task.id);
    ElMessage.success('已重新开始处理任务');
    await loadImportTasks();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '重试失败');
  }
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
  if (importForm.exam_id) {
    loadImportTasks();
  }
});
</script>

<style scoped>
.score-import {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.template-download,
.upload-area {
  padding: 20px 0;
}

.template-download h4,
.upload-area h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
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

.upload-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.tasks-section {
  height: 100%;
}

.tasks-section .el-card__body {
  padding: 0;
}

.tasks-section .el-table {
  margin: 0;
}
</style>
