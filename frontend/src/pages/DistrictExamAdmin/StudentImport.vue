<template>
  <div class="student-import">
    <div class="header">
      <h1>导入考生信息</h1>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 导入流程步骤 -->
    <div class="steps-section">
      <el-steps :active="currentStep" finish-status="success">
        <el-step title="下载模板" />
        <el-step title="准备数据" />
        <el-step title="上传文件" />
        <el-step title="确认导入" />
      </el-steps>
    </div>

    <!-- 步骤1: 下载模板 -->
    <div v-if="currentStep === 0" class="step-content">
      <el-card class="template-card">
        <template #header>
          <div class="card-header">
            <span>📥 第一步：下载导入模板</span>
          </div>
        </template>

        <div class="template-info">
          <h3>Excel导入模板说明</h3>
          <p>请先下载Excel模板文件，按照模板格式填写考生信息后再上传。</p>

          <el-table :data="templateFields" border style="width: 100%; margin-top: 20px;">
            <el-table-column prop="field" label="字段名" width="150" />
            <el-table-column prop="required" label="是否必填" width="100" />
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例" width="150" />
          </el-table>
        </div>

        <div class="template-actions">
          <el-button type="primary" size="large" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            <span style="margin-left: 8px;">下载Excel模板</span>
          </el-button>
          <el-button size="large" @click="currentStep = 1">
            已有模板，下一步
            <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 步骤2: 准备数据 -->
    <div v-if="currentStep === 1" class="step-content">
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
              <li>请按照模板格式填写数据，不要修改列名</li>
              <li>所有必填字段都必须填写完整</li>
              <li>身份证号必须唯一，不能重复</li>
              <li>考生号必须唯一，不能重复</li>
              <li>班级格式：5年级1班=501，高一1班=1001</li>
              <li>建议单次导入不超过1000条记录</li>
            </ul>
          </el-alert>

          <h3>数据格式要求</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="市(区)">必填，如：北京市、朝阳区</el-descriptions-item>
            <el-descriptions-item label="学校">必填，学校全称</el-descriptions-item>
            <el-descriptions-item label="姓名">必填，学生真实姓名</el-descriptions-item>
            <el-descriptions-item label="身份证号">必填，18位身份证号，唯一标识</el-descriptions-item>
            <el-descriptions-item label="考生号">必填，考试唯一编号，不能重复</el-descriptions-item>
            <el-descriptions-item label="学校代码">选填，学校代码</el-descriptions-item>
            <el-descriptions-item label="班级" :span="2">必填，班级编号格式：5年级1班=501，高一1班=1001</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="prep-actions">
          <el-button size="large" @click="currentStep = 0">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button type="primary" size="large" @click="currentStep = 2">
            数据已准备好
            <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 步骤3: 上传文件 -->
    <div v-if="currentStep === 2" class="step-content">
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
            <el-descriptions :column="1" border>
              <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
              <el-descriptions-item label="文件类型">{{ selectedFile.name.split('.').pop() }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <div class="upload-actions">
          <el-button size="large" @click="currentStep = 1">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            size="large"
            @click="validateFile"
            :loading="validating"
            :disabled="!selectedFile"
          >
            验证文件
            <el-icon style="margin-left: 8px;"><CircleCheck /></el-icon>
          </el-button>
        </div>
      </el-card>

      <!-- 验证结果对话框 -->
      <el-dialog v-model="showValidationResult" title="文件验证结果" width="800px">
        <div v-if="validationResult">
          <el-alert
            :title="validationResult.valid ? '✅ 文件验证通过' : '❌ 文件验证失败'"
            :type="validationResult.valid ? 'success' : 'error'"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <div v-if="validationResult.valid">
            <h4>📊 数据统计</h4>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-statistic title="总记录数" :value="validationResult.totalRecords" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="有效记录" :value="validationResult.validRecords" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="无效记录" :value="validationResult.invalidRecords" />
              </el-col>
            </el-row>

            <div v-if="validationResult.errors && validationResult.errors.length > 0" style="margin-top: 20px;">
              <h4>⚠️ 数据问题</h4>
              <el-table :data="validationResult.errors" max-height="300" size="small">
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="field" label="字段" width="120" />
                <el-table-column prop="value" label="值" width="150" />
                <el-table-column prop="message" label="问题" />
              </el-table>
            </div>
          </div>

          <div v-else>
            <div style="margin-bottom: 20px;">
              <h4 style="margin: 0 0 10px 0; color: #f56c6c;">❌ 错误信息</h4>
              <p style="color: #606266; margin: 0;">{{ validationResult.message }}</p>
            </div>
            
            <div v-if="validationResult.errors && validationResult.errors.length > 0" style="margin-top: 20px;">
              <h4 style="margin: 0 0 10px 0;">⚠️ 详细错误列表</h4>
              <el-table :data="validationResult.errors" max-height="300" size="small" border>
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="field" label="字段" width="120" />
                <el-table-column prop="message" label="错误信息" />
              </el-table>
            </div>
          </div>
        </div>

        <template #footer>
          <el-button @click="showValidationResult = false">关闭</el-button>
          <el-button
            v-if="validationResult && validationResult.valid"
            type="primary"
            @click="confirmImport"
          >
            确认导入
          </el-button>
        </template>
      </el-dialog>
    </div>

    <!-- 步骤4: 导入进度 -->
    <div v-if="currentStep === 3" class="step-content">
      <el-card class="progress-card">
        <template #header>
          <div class="card-header">
            <span>📊 第四步：导入进度</span>
          </div>
        </template>

        <div class="progress-area">
          <el-progress
            :percentage="importProgress"
            :status="importStatus"
            :stroke-width="20"
          >
            <span>{{ importProgress }}%</span>
          </el-progress>

          <div class="progress-info">
            <p><strong>导入状态：</strong>{{ importStatusText }}</p>
            <p v-if="importedCount > 0"><strong>已导入：</strong>{{ importedCount }} 条</p>
            <p v-if="errorCount > 0"><strong>失败：</strong>{{ errorCount }} 条</p>
            <p v-if="totalCount > 0"><strong>总计：</strong>{{ totalCount }} 条</p>
          </div>

          <div v-if="importErrors.length > 0" class="error-list">
            <h4>导入错误详情</h4>
            <el-table :data="importErrors" max-height="300" size="small">
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column prop="student_id_number" label="学籍号" width="150" />
              <el-table-column prop="error" label="错误信息" />
            </el-table>
          </div>
        </div>

        <div class="progress-actions">
          <el-button
            v-if="importStatus !== 'success'"
            @click="resetImport"
            :disabled="importing"
          >
            重新导入
          </el-button>
          <el-button
            v-if="importStatus === 'success'"
            type="primary"
            @click="goBack"
          >
            完成
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { UploadFile, UploadProps } from 'element-plus';
import { evaluationService } from '@/services/evaluation';
import * as XLSX from 'xlsx';

const router = useRouter();
const route = useRoute();

// 从路由参数获取 exam_id
const examId = computed(() => {
  const id = route.params.exam_id || route.query.exam_id;
  return id ? Number(id) : null;
});

// 当前步骤
const currentStep = ref(0);

// 文件相关
const selectedFile = ref<File | null>(null);
const uploadRef = ref();
const validating = ref(false);

// 验证结果
const showValidationResult = ref(false);
const validationResult = ref<any>(null);

// 导入进度
const importProgress = ref(0);
const importStatus = ref<'exception' | 'success' | ''>('');
const importing = ref(false);
const importedCount = ref(0);
const errorCount = ref(0);
const totalCount = ref(0);
const importErrors = ref<any[]>([]);

// 导入状态文本
const importStatusText = computed(() => {
  if (importing.value) return '正在导入...';
  if (importStatus.value === 'success') return '导入完成';
  if (importStatus.value === 'exception') return '导入失败';
  return '等待开始...';
});

// 模板字段说明
const templateFields = [
  { field: '市(区)', required: '✅ 必填', description: '市或区名称，如：北京市、朝阳区', example: '北京市' },
  { field: '学校', required: '✅ 必填', description: '学校全称', example: '北京市第一中学' },
  { field: '姓名', required: '✅ 必填', description: '学生真实姓名', example: '张三' },
  { field: '身份证号', required: '✅ 必填', description: '18位身份证号，唯一标识', example: '110101200801011234' },
  { field: '考生号', required: '✅ 必填', description: '考试唯一编号，不能重复', example: '202401001' },
  { field: '学校代码', required: '⭕ 选填', description: '学校代码', example: '10001' },
  { field: '班级', required: '✅ 必填', description: '班级编号：5年级1班=501，高一1班=1001', example: '1001' },
];

// 返回
const goBack = () => {
  router.push('/district-admin/exams');
};

// 页面加载时检查 exam_id
onMounted(() => {
  if (!examId.value) {
    ElMessage.warning('缺少考试ID参数，请从考试管理页面进入');
    // 可以选择跳转到考试列表或显示选择考试的界面
    // 这里先显示警告，让用户知道需要从正确的入口进入
  }
});

// 下载模板
const downloadTemplate = () => {
  try {
    // 创建Excel模板数据
    const template = [
      ['市(区)*', '学校*', '姓名*', '身份证号*', '考生号*', '学校代码', '班级*'],
      ['开平市', '开平市第一中学', '张三', '110101200801011234', '202401001', '10001', '1001'],
      ['开平市', '开平市第一中学', '李四', '110101200802021234', '202401002', '10001', '1002'],
    ];

    // 创建工作簿
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(template);
    
    // 设置列宽
    ws['!cols'] = [
      { wch: 15 }, // 市(区)
      { wch: 20 }, // 学校
      { wch: 12 }, // 姓名
      { wch: 20 }, // 身份证号
      { wch: 15 }, // 考生号
      { wch: 12 }, // 学校代码
      { wch: 12 }, // 班级
    ];
    
    XLSX.utils.book_append_sheet(wb, ws, '考生信息');
    
    // 导出为Excel文件
    XLSX.writeFile(wb, '考生信息导入模板.xlsx');
    
    ElMessage.success('模板下载成功');
  } catch (error) {
    console.error('下载模板失败:', error);
    ElMessage.error('模板下载失败，请稍后重试');
  }
};

// 文件选择
const handleFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedFile.value = uploadFile.raw;
};

// 文件超出限制
const handleExceed: UploadProps['onExceed'] = () => {
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

// 验证文件
const validateFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件');
    return;
  }

  if (!examId.value) {
    ElMessage.error('缺少考试ID，请从考试管理页面进入');
    return;
  }

  validating.value = true;

  try {
    // 调用后端API进行导入（后端会先验证再导入）
    const result = await evaluationService.exam.importStudents(
      examId.value,
      selectedFile.value
    );

    // 处理导入结果
    validationResult.value = {
      valid: result.failed === 0,
      totalRecords: result.total,
      validRecords: result.success,
      invalidRecords: result.failed,
      errors: result.errors.map(err => ({
        row: err.row,
        field: err.field || '',
        value: '',
        message: err.message,
      })),
    };

    showValidationResult.value = true;
    
    // 如果有错误，停留在验证步骤；如果全部成功，进入导入完成步骤
    if (result.failed > 0) {
      currentStep.value = 2; // 回到上传步骤，显示错误
    } else {
      currentStep.value = 3; // 进入导入完成步骤
      importProgress.value = 100;
      importStatus.value = 'success';
      importedCount.value = result.success;
      errorCount.value = result.failed;
      totalCount.value = result.total;
    }
  } catch (error: any) {
    console.error('导入失败:', error);
    
    // 获取详细的错误信息
    let errorMessage = '文件导入失败';
    let errorDetails: any[] = [];
    
    if (error.response) {
      // 如果是 HTTP 错误响应
      const errorData = error.response.data;
      if (errorData?.detail) {
        // 如果 detail 是字符串，说明是解析错误（如缺少必需列）
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } 
        // 如果 detail 是对象或数组，可能是验证错误
        else if (typeof errorData.detail === 'object') {
          errorMessage = '文件验证失败，请查看详细信息';
          if (Array.isArray(errorData.detail)) {
            errorDetails = errorData.detail.map((err: any, idx: number) => ({
              row: err.row || idx + 1,
              field: err.field || '',
              value: '',
              message: err.message || err.msg || JSON.stringify(err),
            }));
          }
        }
      } else {
        errorMessage = error.response.statusText || '请求失败';
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    ElMessage.error(errorMessage);
    
    validationResult.value = {
      valid: false,
      totalRecords: 0,
      validRecords: 0,
      invalidRecords: errorDetails.length || 1,
      errors: errorDetails,
      message: errorMessage,
    };
    showValidationResult.value = true;
  } finally {
    validating.value = false;
  }
};

// 确认导入（验证通过后，实际导入已在验证步骤完成）
const confirmImport = () => {
  showValidationResult.value = false;
  // 导入已在 validateFile 中完成，这里只是关闭对话框
  if (validationResult.value && validationResult.value.valid) {
    ElMessage.success(`导入完成！成功 ${validationResult.value.validRecords} 条`);
  }
};

// 重置导入
const resetImport = () => {
  currentStep.value = 0;
  selectedFile.value = null;
  validationResult.value = null;
  importProgress.value = 0;
  importStatus.value = '';
  importedCount.value = 0;
  errorCount.value = 0;
  totalCount.value = 0;
  importErrors.value = [];
  if (uploadRef.value) {
    uploadRef.value.clearFiles();
  }
};
</script>

<style scoped>
.student-import {
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

.steps-section {
  margin-bottom: 30px;
}

.step-content {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.template-info,
.prep-info,
.upload-area,
.progress-area {
  margin-bottom: 20px;
}

.template-info h3,
.prep-info h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
}

.template-actions,
.prep-actions,
.upload-actions,
.progress-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
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

.progress-info {
  margin: 20px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.progress-info p {
  margin: 8px 0;
  font-size: 14px;
}

.error-list {
  margin-top: 20px;
}

.error-list h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
}
</style>
