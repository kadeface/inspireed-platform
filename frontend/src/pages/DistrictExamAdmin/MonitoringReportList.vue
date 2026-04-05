<template>
  <div class="monitoring-report-list">
    <div class="page-header flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <el-button @click="router.back()" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">质量监测报告</h1>
          <p class="text-gray-500 text-sm mt-1">导入并查看小学/初中质量监测统计表</p>
        </div>
      </div>
      <el-button type="primary" @click="showImportDialog = true">
        <el-icon><Upload /></el-icon>
        导入报告
      </el-button>
    </div>

    <!-- 筛选 -->
    <el-card class="filter-card mb-4">
      <el-form :inline="true" :model="filters">
        <el-form-item label="学年">
          <el-select v-model="filters.academic_year" placeholder="全部" clearable style="width: 140px" @change="loadList">
            <el-option v-for="y in yearOptions" :key="y" :label="y" :value="y" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select v-model="filters.semester_type" placeholder="全部" clearable style="width: 120px" @change="loadList">
            <el-option label="上学期" value="up" />
            <el-option label="下学期" value="down" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.report_type" placeholder="全部" clearable style="width: 120px" @change="loadList">
            <el-option label="小学" value="primary" />
            <el-option label="初中" value="junior_high" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="loadList">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card>
      <el-table v-loading="loading" :data="list" stripe>
        <el-table-column prop="name" label="报告名称" min-width="220" />
        <el-table-column prop="report_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.report_type === 'primary' ? 'success' : 'primary'" size="small">
              {{ row.report_type === 'primary' ? '小学' : '初中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="academic_year" label="学年" width="110" />
        <el-table-column prop="semester_type" label="学期" width="80">
          <template #default="{ row }">
            {{ row.semester_type === 'up' ? '上学期' : '下学期' }}
          </template>
        </el-table-column>
        <el-table-column prop="source_file" label="来源文件" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="导入时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="goDetail(row.id)">查看</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && list.length === 0" description="暂无报告，请导入" />
    </el-card>

    <!-- 导入弹窗 -->
    <el-dialog v-model="showImportDialog" title="导入质量监测报告" width="500" :close-on-click-modal="false" @close="resetImportForm">
      <el-form ref="importFormRef" :model="importForm" :rules="importRules" label-width="100px">
        <el-form-item label="报告类型" prop="report_type">
          <el-radio-group v-model="importForm.report_type">
            <el-radio value="primary">小学</el-radio>
            <el-radio value="junior_high">初中</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="报告名称" prop="name">
          <el-input v-model="importForm.name" placeholder="如：25-26学年第一学期小学质量监测" />
        </el-form-item>
        <el-form-item label="学年" prop="academic_year">
          <el-select v-model="importForm.academic_year" placeholder="请选择学年" style="width: 180px" clearable>
            <el-option v-for="y in yearOptions" :key="y" :label="y" :value="y" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期" prop="semester_type">
          <el-select v-model="importForm.semester_type" placeholder="请选择" style="width: 180px">
            <el-option label="上学期" value="up" />
            <el-option label="下学期" value="down" />
          </el-select>
        </el-form-item>
        <el-form-item label="Excel 文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="onFileChange"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <span class="text-gray-400 text-xs">支持 .xlsx、.xls 格式</span>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="submitImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Upload } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { monitoringReportApi } from '@/services/evaluation'
import type { MonitoringReport } from '@/types/evaluation'

const router = useRouter()
const loading = ref(false)
const list = ref<MonitoringReport[]>([])

const filters = reactive({
  academic_year: '',
  semester_type: '',
  report_type: '',
})

const yearOptions = ref<string[]>([])
for (let y = new Date().getFullYear(); y >= 2020; y--) {
  yearOptions.value.push(`${y}-${y + 1}`)
}
const defaultAcademicYear = () => yearOptions.value[0] ?? ''

async function loadList() {
  loading.value = true
  try {
    const res = await monitoringReportApi.list({
      academic_year: filters.academic_year || undefined,
      semester_type: filters.semester_type || undefined,
      report_type: filters.report_type || undefined,
    })
    list.value = Array.isArray(res) ? res : (res as any)?.data ?? []
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

function formatDate(s: string) {
  if (!s) return '-'
  const d = new Date(s)
  return d.toLocaleString('zh-CN')
}

function goDetail(id: number) {
  router.push(`/district-admin/monitoring-reports/${id}`)
}

async function handleDelete(id: number) {
  try {
    await monitoringReportApi.delete(id)
    ElMessage.success('已删除')
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// 导入
const showImportDialog = ref(false)
const importing = ref(false)
const uploadRef = ref()
const importFormRef = ref<FormInstance>()
const importForm = reactive({
  report_type: 'primary' as 'primary' | 'junior_high',
  name: '',
  academic_year: defaultAcademicYear(),
  semester_type: 'up' as 'up' | 'down',
  file: null as File | null,
})

const importRules: FormRules = {
  report_type: [{ required: true, message: '请选择类型' }],
  name: [{ required: true, message: '请输入报告名称' }],
  academic_year: [{ required: true, message: '请输入学年' }],
  semester_type: [{ required: true, message: '请选择学期' }],
}

function onFileChange(uploadFile: any) {
  importForm.file = uploadFile?.raw ?? null
}

function resetImportForm() {
  importForm.report_type = 'primary'
  importForm.name = ''
  importForm.academic_year = defaultAcademicYear()
  importForm.semester_type = 'up'
  importForm.file = null
  uploadRef.value?.clearFiles()
}

async function submitImport() {
  if (!importForm.file) {
    ElMessage.warning('请选择 Excel 文件')
    return
  }
  importing.value = true
  try {
    await monitoringReportApi.import(importForm.file, {
      report_type: importForm.report_type,
      name: importForm.name,
      academic_year: importForm.academic_year,
      semester_type: importForm.semester_type,
    })
    ElMessage.success('导入成功')
    showImportDialog.value = false
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.monitoring-report-list {
  padding: 20px;
}
.filter-card :deep(.el-form-item) {
  margin-bottom: 0;
}
</style>
