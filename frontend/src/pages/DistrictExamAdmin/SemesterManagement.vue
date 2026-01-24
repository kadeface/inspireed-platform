<template>
  <div class="semester-management">
    <div class="header">
      <h1>学期管理</h1>
      <div class="header-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          创建学期
        </el-button>
      </div>
    </div>

    <!-- 学期列表 -->
    <el-table :data="semesters" v-loading="loading" stripe>
      <el-table-column prop="name" label="学期名称" width="200" />
      <el-table-column prop="year" label="学年" width="100" />
      <el-table-column prop="semester_type" label="学期类型" width="100">
        <template #default="{ row }">
          <el-tag>{{ row.semester_type === 'up' ? '上学期' : '下学期' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="start_date" label="开始日期" width="120" />
      <el-table-column prop="end_date" label="结束日期" width="120" />
      <el-table-column prop="is_current" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_current ? 'success' : 'info'">
            {{ row.is_current ? '当前学期' : '非当前' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_current"
            size="small"
            type="success"
            @click="setCurrentSemester(row)"
          >
            设为当前
          </el-button>
          <el-button size="small" @click="editSemester(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteSemester(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <!-- 创建/编辑学期对话框 -->
  <el-dialog
    v-model="showCreateDialog"
    :title="editingSemester ? '编辑学期' : '创建学期'"
    width="600px"
    @close="resetForm"
  >
    <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
      <el-form-item label="学年" prop="year">
        <el-input
          v-model="form.year"
          placeholder="请输入学年，格式：2023-2024"
          maxlength="9"
        />
      </el-form-item>

      <el-form-item label="学期类型" prop="semester_type">
        <el-radio-group v-model="form.semester_type">
          <el-radio value="up">上学期</el-radio>
          <el-radio value="down">下学期</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="学期名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="自动生成，可修改"
        >
          <template #append>
            <el-button @click="generateName">自动生成</el-button>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="开始日期" prop="start_date">
        <el-date-picker
          v-model="form.start_date"
          type="date"
          placeholder="选择开始日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="结束日期" prop="end_date">
        <el-date-picker
          v-model="form.end_date"
          type="date"
          placeholder="选择结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="设为当前学期">
        <el-switch v-model="form.is_current" />
        <span style="margin-left: 10px; color: #909399; font-size: 12px;">
          系统只能有一个当前学期
        </span>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="showCreateDialog = false">取消</el-button>
      <el-button type="primary" @click="submitForm" :loading="submitting">
        {{ editingSemester ? '更新' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { semesterApi } from '@/services/evaluation';
import type { Semester } from '@/types/evaluation';

const router = useRouter();

// 响应式数据
const loading = ref(false);
const semesters = ref<Semester[]>([]);
const showCreateDialog = ref(false);

// 返回
const goBack = () => {
  router.push('/district-admin/exams');
};
const editingSemester = ref<Semester | null>(null);
const submitting = ref(false);

// 表单数据
const form = reactive({
  year: `${new Date().getFullYear()}-${new Date().getFullYear() + 1}`,
  semester_type: 'up', // 'up' 表示上学期, 'down' 表示下学期
  name: '',
  start_date: '',
  end_date: '',
  is_current: false,
});

// 表单验证规则
const formRules = {
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

const formRef = ref<FormInstance>();

// 自动生成学期名称
const generateName = () => {
  const semesterText = form.semester_type === 'up' ? '上学期' : '下学期';
  form.name = `${form.year}学年${semesterText}`;
};

// 监听年份和学期类型变化，自动生成名称
watch(
  () => [form.year, form.semester_type],
  () => {
    generateName();
  }
);

// 加载学期列表
const loadSemesters = async () => {
  loading.value = true;
  try {
    const result = await semesterApi.list();
    // 确保返回的是数组
    if (Array.isArray(result)) {
      semesters.value = result;
    } else {
      console.error('API返回的数据不是数组:', result);
      semesters.value = [];
      ElMessage.error('加载学期列表失败：数据格式错误');
    }
  } catch (error: any) {
    console.error('加载学期列表错误:', error);
    semesters.value = [];
    ElMessage.error(error.response?.data?.detail || '加载学期列表失败');
  } finally {
    loading.value = false;
  }
};

// 编辑学期
const editSemester = (semester: Semester) => {
  editingSemester.value = semester;
  Object.assign(form, {
    year: semester.year,
    semester_type: semester.semester_type,
    name: semester.name,
    start_date: semester.start_date.split('T')[0],
    end_date: semester.end_date.split('T')[0],
    is_current: semester.is_current,
  });
  showCreateDialog.value = true;
};

// 删除学期
const deleteSemester = async (semester: Semester) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学期"${semester.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    await semesterApi.delete(semester.id);
    ElMessage.success('删除成功');
    loadSemesters();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

// 设为当前学期
const setCurrentSemester = async (semester: Semester) => {
  try {
    await ElMessageBox.confirm(
      `确定要将"${semester.name}"设为当前学期吗？这将取消其他学期的当前状态。`,
      '确认设置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    );

    await semesterApi.update(semester.id, { is_current: true });
    ElMessage.success('设置成功');
    loadSemesters();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '设置失败');
    }
  }
};

// 提交表单
const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    if (editingSemester.value) {
      // 更新
      await semesterApi.update(editingSemester.value.id, {
        year: form.year,
        semester_type: form.semester_type,
        name: form.name,
        start_date: form.start_date + 'T00:00:00', // 转换为完整的 datetime 格式
        end_date: form.end_date + 'T00:00:00', // 转换为完整的 datetime 格式
        is_current: form.is_current,
      });
      ElMessage.success('更新成功');
    } else {
      // 创建
      await semesterApi.create({
        year: form.year,
        semester_type: form.semester_type,
        name: form.name,
        start_date: form.start_date + 'T00:00:00', // 转换为完整的 datetime 格式
        end_date: form.end_date + 'T00:00:00', // 转换为完整的 datetime 格式
        is_current: form.is_current,
      });
      ElMessage.success('创建成功');
    }

    showCreateDialog.value = false;
    loadSemesters();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败');
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  editingSemester.value = null;
  const currentYear = new Date().getFullYear();
  Object.assign(form, {
    year: `${currentYear}-${currentYear + 1}`,
    semester_type: 'up', // 'up' 表示上学期
    name: '',
    start_date: '',
    end_date: '',
    is_current: false,
  });
  generateName();
  formRef.value?.resetFields();
};

// 组件挂载
onMounted(() => {
  loadSemesters();
});
</script>

<style scoped>
.semester-management {
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
</style>
