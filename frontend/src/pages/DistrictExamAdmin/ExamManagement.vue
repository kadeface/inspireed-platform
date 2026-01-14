<template>
  <div class="exam-management">
    <div class="header">
      <h1>考试管理</h1>
      <div class="header-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          创建考试
        </el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filters">
        <el-form-item label="学期">
          <el-select v-model="filters.semester_id" placeholder="选择学期" clearable>
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="考试类型">
          <el-select v-model="filters.exam_type" placeholder="选择类型" clearable>
            <el-option label="期中考试" value="midterm" />
            <el-option label="期末考试" value="final" />
            <el-option label="月考" value="monthly" />
            <el-option label="单元测试" value="unit" />
            <el-option label="模拟考试" value="mock" />
            <el-option label="区县统考" value="district_unified" />
            <el-option label="中考/高考" value="entrance" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已安排" value="scheduled" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadExams">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 考试列表 -->
    <el-table :data="exams" v-loading="loading" stripe>
      <el-table-column prop="name" label="考试名称" width="200" align="center" />
      <el-table-column prop="exam_type" label="类型" width="120" align="center">
        <template #default="{ row }">
          <el-tag>{{ getExamTypeName(row.exam_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="exam_date" label="考试日期" width="120" align="center">
        <template #default="{ row }">
          {{ row.exam_date ? row.exam_date.split('T')[0] : '' }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="说明" width="350" align="center" show-overflow-tooltip />
      <el-table-column label="操作" width="200" fixed="right" align="center">
        <template #default="{ row }">
          <el-button size="small" @click="viewExam(row)">查看</el-button>
          <el-button size="small" type="primary" @click="editExam(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteExam(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadExams"
        @current-change="loadExams"
      />
    </div>

    <!-- 创建/编辑考试对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingExam ? '编辑考试' : '创建考试'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="考试名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入考试名称" />
        </el-form-item>

        <el-form-item label="考试类型" prop="exam_type">
          <el-select v-model="form.exam_type" placeholder="选择类型">
            <el-option label="期中考试" value="midterm" />
            <el-option label="期末考试" value="final" />
            <el-option label="月考" value="monthly" />
            <el-option label="单元测试" value="unit" />
            <el-option label="模拟考试" value="mock" />
            <el-option label="区县统考" value="district_unified" />
            <el-option label="中考/高考" value="entrance" />
          </el-select>
        </el-form-item>

        <el-form-item label="年级" prop="grade_id">
          <el-select v-model="form.grade_id" placeholder="选择年级" clearable>
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="学期" prop="semester_id">
          <el-select v-model="form.semester_id" placeholder="选择学期">
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="考试日期" prop="exam_date">
          <el-date-picker
            v-model="form.exam_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入说明"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ editingExam ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { examApi, semesterApi } from '@/services/evaluation';
import { curriculumService } from '@/services/curriculum';
import type { Exam, Semester } from '@/types/evaluation';
import type { Grade } from '@/types/curriculum';

const router = useRouter();

// 响应式数据
const loading = ref(false);
const exams = ref<Exam[]>([]);
const semesters = ref<Semester[]>([]);
const grades = ref<Grade[]>([]);
const showCreateDialog = ref(false);
const editingExam = ref<Exam | null>(null);

// 返回
const goBack = () => {
  router.push('/district-admin/exams');
};
const submitting = ref(false);

// 筛选条件
const filters = reactive({
  semester_id: undefined,
  exam_type: undefined,
  status: undefined,
});

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

// 表单数据
const form = reactive({
  name: '',
  exam_type: '',
  grade_id: undefined,
  semester_id: undefined,
  exam_date: '',
  description: '',
});

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  semester_id: [{ required: true, message: '请选择学期', trigger: 'change' }],
  grade_id: [{ required: true, message: '请选择年级', trigger: 'change' }],
  exam_date: [{ required: true, message: '请选择考试日期', trigger: 'change' }],
};

const formRef = ref<FormInstance>();

// 加载考试列表
const loadExams = async () => {
  loading.value = true;
  try {
    const params: any = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
    };

    if (filters.semester_id) params.semester_id = filters.semester_id;
    if (filters.exam_type) params.exam_type = filters.exam_type;
    if (filters.status) params.status = filters.status;

    const result = await examApi.list(params);
    // 确保返回的是数组
    if (Array.isArray(result)) {
      exams.value = result;
    } else {
      console.error('API返回的数据不是数组:', result);
      exams.value = [];
      ElMessage.error('加载考试列表失败：数据格式错误');
    }
  } catch (error: any) {
    console.error('加载考试列表错误:', error);
    exams.value = [];
    ElMessage.error(error.response?.data?.detail || '加载考试列表失败');
  } finally {
    loading.value = false;
  }
};

// 加载学期列表
const loadSemesters = async () => {
  try {
    semesters.value = await semesterApi.list();
  } catch (error: any) {
    ElMessage.error('加载学期列表失败');
  }
};

// 加载年级列表
const loadGrades = async () => {
  try {
    grades.value = await curriculumService.getGrades();
  } catch (error: any) {
    ElMessage.error('加载年级列表失败');
  }
};

// 重置筛选
const resetFilters = () => {
  filters.semester_id = undefined;
  filters.exam_type = undefined;
  filters.status = undefined;
  loadExams();
};

// 查看考试
const viewExam = (exam: Exam) => {
  ElMessage.info(`查看考试: ${exam.name}`);
  // TODO: 实现查看详情功能
};

// 编辑考试
const editExam = (exam: Exam) => {
  editingExam.value = exam;
  Object.assign(form, {
    name: exam.name,
    exam_type: exam.exam_type,
    grade_id: exam.grade_id,
    semester_id: exam.semester_id,
    exam_date: exam.exam_date.split('T')[0],
    description: exam.description || '',
  });
  showCreateDialog.value = true;
};

// 删除考试
const deleteExam = async (exam: Exam) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除考试"${exam.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    await examApi.delete(exam.id);
    ElMessage.success('删除成功');
    loadExams();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

// 提交表单
const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    if (editingExam.value) {
      // 更新
      await examApi.update(editingExam.value.id, {
        name: form.name,
        exam_type: form.exam_type as any,
        grade_id: form.grade_id!,
        exam_date: form.exam_date + 'T00:00:00', // 转换为完整的 datetime 格式
      });
      ElMessage.success('更新成功');
    } else {
      // 创建
      await examApi.create({
        name: form.name,
        exam_type: form.exam_type as any,
        grade_id: form.grade_id!,
        semester_id: form.semester_id!,
        exam_date: form.exam_date + 'T00:00:00', // 转换为完整的 datetime 格式
      });
      ElMessage.success('创建成功');
    }

    showCreateDialog.value = false;
    loadExams();
  } catch (error: any) {
    // 处理 422 验证错误
    if (error.response?.status === 422 && Array.isArray(error.response?.data?.detail)) {
      const errors = error.response.data.detail.map((err: any) => {
        const field = err.loc?.join('.') || 'field';
        const msg = err.msg || 'validation error';
        return `${field}: ${msg}`;
      }).join('; ');
      ElMessage.error(`数据验证失败: ${errors}`);
      console.error('详细验证错误:', error.response.data.detail);
    } else {
      ElMessage.error(error.response?.data?.detail || '操作失败');
    }
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  editingExam.value = null;
  Object.assign(form, {
    name: '',
    exam_type: '',
    grade_id: undefined,
    semester_id: undefined,
    exam_date: '',
    description: '',
  });
  formRef.value?.resetFields();
};

// 获取考试类型名称
const getExamTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    midterm: '期中考试',
    final: '期末考试',
    monthly: '月考',
    unit: '单元测试',
    mock: '模拟考试',
    district_unified: '区县统考',
    entrance: '中考/高考',
  };
  return typeMap[type] || type;
};

// 获取状态名称
const getStatusName = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    scheduled: '已安排',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
  };
  return statusMap[status] || status;
};

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    draft: 'info',
    scheduled: '',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger',
  };
  return typeMap[status] || '';
};

// 组件挂载
onMounted(() => {
  loadGrades();
  loadSemesters();
  loadExams();
});
</script>

<style scoped>
.exam-management {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.filter-section :deep(.el-select) {
  width: auto;
  min-width: 120px;
}

.filter-section :deep(.el-select .el-input__wrapper) {
  width: auto;
  min-width: 120px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
