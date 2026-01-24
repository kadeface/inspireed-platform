<template>
  <div class="exam-room-management">
    <div class="header">
      <h1>考场管理 - {{ examName }}</h1>
      <div class="header-actions">
        <el-button @click="goBack">返回考试列表</el-button>
        <el-button type="primary" @click="showAssignDialog = true" v-if="!hasRooms">
          分配考场
        </el-button>
        <el-dropdown split-button type="warning" @click="exportExamNumbers" v-if="examInfo?.exam_level === 'city'">
          📥 市级考号管理
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="showImportDialog = true">
                📥 导入市级考号
              </el-dropdown-item>
              <el-dropdown-item @click="downloadTemplate">
                📄 下载导入模板
              </el-dropdown-item>
              <el-dropdown-item @click="exportExamNumbers">
                📤 导出考号映射表
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="success" @click="exportAllDocuments" :loading="exporting" v-if="hasRooms">
          📦 批量导出所有文档
        </el-button>
        <el-button type="success" @click="loadExamRooms" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 考试信息 -->
    <el-card class="exam-info" v-if="examInfo">
      <template #header>
        <span>考试信息</span>
      </template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="考试名称">{{ examInfo.name }}</el-descriptions-item>
        <el-descriptions-item label="考试类型">
          <el-tag>{{ getExamTypeName(examInfo.exam_type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="考试日期">
          {{ examInfo.exam_date ? examInfo.exam_date.split('T')[0] : '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(examInfo.status)">
            {{ getStatusName(examInfo.status) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 考场列表 -->
    <el-card class="rooms-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>考场列表 ({{ rooms.length }} 个考场)</span>
          <div class="extra-info" v-if="rooms.length > 0">
            <span>共 {{ totalStudents }} 名学生</span>
          </div>
        </div>
      </template>

      <el-empty v-if="!loading && rooms.length === 0" description="暂无考场，请先分配考场">
        <el-button type="primary" @click="showAssignDialog = true">分配考场</el-button>
      </el-empty>

      <el-table :data="rooms" stripe v-else>
        <el-table-column prop="id" label="考场ID" width="80" align="center" />
        <el-table-column prop="name" label="考场名称" width="120" align="center" />
        <el-table-column prop="capacity" label="容量" width="80" align="center" />
        <el-table-column prop="seat_count" label="已分配" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.seat_count >= row.capacity ? 'warning' : 'success'">
              {{ row.seat_count }} / {{ row.capacity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_number_start" label="考号范围" width="180" align="center">
          <template #default="{ row }">
            {{ row.exam_number_start }} ~ {{ row.exam_number_end }}
          </template>
        </el-table-column>
        <el-table-column prop="arrangement_type" label="编排类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.arrangement_type === 'by_class'" type="info">按班级</el-tag>
            <el-tag v-else type="warning">混排</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="viewStudents(row)">
              👥 查看学生
            </el-button>
            <el-dropdown split-button type="primary" @click="exportSeatingChart(row)">
              📄 导出文档
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="exportSeatingChart(row)">
                    📄 座位表
                  </el-dropdown-item>
                  <el-dropdown-item @click="exportExamTickets(row)">
                    🎫 准考证
                  </el-dropdown-item>
                  <el-dropdown-item @click="exportProctorHandbook(row)">
                    📋 监考手册
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 分配考场对话框 -->
    <el-dialog
      v-model="showAssignDialog"
      title="自动分配考场"
      width="500px"
      @close="resetAssignForm"
    >
      <el-form :model="assignForm" :rules="assignRules" ref="assignFormRef" label-width="120px">
        <el-form-item label="每考场人数" prop="capacity_per_room">
          <el-input-number
            v-model="assignForm.capacity_per_room"
            :min="10"
            :max="100"
            :step="5"
          />
          <span class="form-tip">建议：30人/考场</span>
        </el-form-item>

        <el-form-item label="编排类型" prop="arrangement_type">
          <el-radio-group v-model="assignForm.arrangement_type">
            <el-radio value="by_class">按班级（同班学生在一起）</el-radio>
            <el-radio value="mixed">混排（不同班级学生混合）</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="座位排列" prop="seat_pattern">
          <el-radio-group v-model="assignForm.seat_pattern">
            <el-radio value="sequential">顺序排列</el-radio>
            <el-radio value="s_shape">S型排列</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="使用现有教室" prop="use_existing_rooms">
          <el-switch v-model="assignForm.use_existing_rooms" />
          <span class="form-tip">自动分配可用教室作为考场</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" @click="assignRooms" :loading="assigning">
          开始分配
        </el-button>
      </template>
    </el-dialog>

    <!-- 学生列表对话框 -->
    <el-dialog
      v-model="showStudentsDialog"
      :title="`${currentRoom?.name} - 学生列表 (${students.length}人)`"
      width="900px"
    >
      <el-table :data="students" max-height="500" stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="exam_number" label="考号" width="120" align="center" />
        <el-table-column prop="student_name" label="姓名" width="100" align="center" />
        <el-table-column prop="student_id_number" label="学籍号" width="180" align="center" />
        <el-table-column prop="seat_number" label="座位号" width="80" align="center">
          <template #default="{ row }">
            {{ row.seat_number?.toString().padStart(2, '0') }}
          </template>
        </el-table-column>
        <el-table-column prop="school_id" label="学校ID" width="80" align="center" />
        <el-table-column prop="classroom_id" label="班级ID" width="80" align="center" />
      </el-table>
    </el-dialog>

    <!-- 导入市级考号对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入市级考号"
      width="600px"
      @close="resetImportDialog"
    >
      <div class="import-instructions">
        <p><strong>说明：</strong></p>
        <ul>
          <li>请先下载导入模板，填写市级考试院下发的正式考号</li>
          <li>Excel格式：校级考号* | 市级考号* | 姓名* | 学校</li>
          <li>校级考号必须是8位数字，市级考号必须是10位数字</li>
          <li>导入后会覆盖自动生成的考号</li>
        </ul>
      </div>

      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将Excel文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只支持 .xlsx 或 .xls 格式，文件大小不超过10MB
          </div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="submitImport" :loading="importing" :disabled="!importFile">
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入结果对话框 -->
    <el-dialog
      v-model="showImportResultDialog"
      title="导入结果"
      width="700px"
    >
      <div class="import-result">
        <el-result
          :icon="importResult.success > 0 && importResult.failed === 0 ? 'success' : 'warning'"
          :title="importResult.success > 0 && importResult.failed === 0 ? '导入成功' : '导入完成'"
        >
          <template #sub-title>
            <div class="result-summary">
              <p>总记录数：<strong>{{ importResult.total }}</strong></p>
              <p>成功：<el-text type="success">{{ importResult.success }}</el-text></p>
              <p>失败：<el-text type="danger">{{ importResult.failed }}</el-text></p>
              <p>创建：<el-text type="primary">{{ importResult.created }}</el-text></p>
              <p>更新：<el-text type="warning">{{ importResult.updated }}</el-text></p>
            </div>
          </template>
          <template #extra>
            <el-table
              v-if="importResult.errors.length > 0"
              :data="importResult.errors"
              max-height="300"
              stripe
              size="small"
            >
              <el-table-column prop="row" label="行号" width="80" align="center" />
              <el-table-column prop="field" label="字段" width="120" align="center" />
              <el-table-column prop="message" label="错误信息" show-overflow-tooltip />
            </el-table>
            <el-empty v-else description="没有错误" :image-size="100" />
          </template>
        </el-result>
      </div>

      <template #footer>
        <el-button type="primary" @click="showImportResultDialog = false">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import type { UploadInstance, UploadFile } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 数据
const examId = ref<number>(parseInt(route.params.examId as string))
const examInfo = ref<any>(null)
const examName = ref('')
const rooms = ref<any[]>([])
const loading = ref(false)
const exporting = ref(false)
const showAssignDialog = ref(false)
const showStudentsDialog = ref(false)
const showImportDialog = ref(false)
const showImportResultDialog = ref(false)
const currentRoom = ref<any>(null)
const students = ref<any[]>([])
const assigning = ref(false)
const importing = ref(false)
const importFile = ref<File | null>(null)
const uploadRef = ref<UploadInstance>()
const importResult = ref({
  total: 0,
  success: 0,
  failed: 0,
  created: 0,
  updated: 0,
  skipped: 0,
  errors: [] as any[]
})

// 分配表单
const assignForm = ref({
  capacity_per_room: 30,
  arrangement_type: 'by_class',
  seat_pattern: 's_shape',
  use_existing_rooms: true
})

const assignRules = {
  capacity_per_room: [
    { required: true, message: '请输入每考场人数', trigger: 'blur' }
  ],
  arrangement_type: [
    { required: true, message: '请选择编排类型', trigger: 'change' }
  ],
  seat_pattern: [
    { required: true, message: '请选择座位排列', trigger: 'change' }
  ]
}

const assignFormRef = ref()

// 计算属性
const hasRooms = computed(() => rooms.value.length > 0)
const totalStudents = computed(() => rooms.value.reduce((sum, room) => sum + (room.seat_count || 0), 0))

// API 基础 URL
const getApiBaseUrl = () => {
  const hostname = window.location.hostname
  const protocol = window.location.protocol

  if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
    if (hostname.includes('--')) {
      const backendHostname = hostname.replace(/--\d+/, '--8000')
      return `${protocol}//${backendHostname}/api/v1`
    }
    return `${protocol}//${hostname}:8000/api/v1`
  }
  return `${protocol}//${hostname}:8000/api/v1`
}

// 加载考试信息
const loadExamInfo = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${getApiBaseUrl()}/exams/${examId.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    examInfo.value = response.data
    examName.value = response.data.name
  } catch (error: any) {
    console.error('加载考试信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载考试信息失败')
  }
}

// 加载考场列表
const loadExamRooms = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${getApiBaseUrl()}/exams/${examId.value}/rooms`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    rooms.value = response.data
  } catch (error: any) {
    console.error('加载考场列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载考场列表失败')
  } finally {
    loading.value = false
  }
}

// 查看学生
const viewStudents = async (room: any) => {
  currentRoom.value = room
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${getApiBaseUrl()}/exams/${examId.value}/rooms/${room.id}/students`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    students.value = response.data
    showStudentsDialog.value = true
  } catch (error: any) {
    console.error('加载学生列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载学生列表失败')
  }
}

// 分配考场
const assignRooms = async () => {
  assigning.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.post(
      `${getApiBaseUrl()}/exams/${examId.value}/rooms/auto-assign`,
      assignForm.value,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )

    ElMessage.success('考场分配成功')
    showAssignDialog.value = false
    await loadExamRooms()
  } catch (error: any) {
    console.error('分配考场失败:', error)
    ElMessage.error(error.response?.data?.detail || '分配考场失败')
  } finally {
    assigning.value = false
  }
}

// 导出座位表
const exportSeatingChart = async (room: any) => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${getApiBaseUrl()}/exams/${examId.value}/rooms/${room.id}/export/seating-chart.pdf`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )

    // 下载文件
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${examInfo.value.name}_${room.name}_座位表_${new Date().toISOString().split('T')[0]}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('座位表导出成功')
  } catch (error: any) {
    console.error('导出座位表失败:', error)
    ElMessage.error('导出座位表失败')
  }
}

// 导出准考证
const exportExamTickets = async (room: any) => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${getApiBaseUrl()}/exams/${examId.value}/rooms/${room.id}/export/exam-tickets.pdf`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )

    // 下载文件
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${examInfo.value.name}_${room.name}_准考证_${new Date().toISOString().split('T')[0]}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('准考证导出成功')
  } catch (error: any) {
    console.error('导出准考证失败:', error)
    ElMessage.error('导出准考证失败')
  }
}

// 导出监考手册
const exportProctorHandbook = async (room: any) => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${getApiBaseUrl()}/exams/${examId.value}/rooms/${room.id}/export/proctor-handbook.pdf`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )

    // 下载文件
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${examInfo.value.name}_${room.name}_监考手册_${new Date().toISOString().split('T')[0]}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('监考手册导出成功')
  } catch (error: any) {
    console.error('导出监考手册失败:', error)
    ElMessage.error('导出监考手册失败')
  }
}

// 批量导出所有文档
const exportAllDocuments = async () => {
  if (!examId.value) {
    ElMessage.error('考试ID不存在')
    return
  }

  exporting.value = true
  try {
    ElMessage.info({
      message: '正在生成所有文档，请稍候...',
      duration: 2000
    })

    await examRoomService.exportAllDocuments(examId.value)

    ElMessage.success('批量导出成功！')
  } catch (error: any) {
    console.error('批量导出失败:', error)
    ElMessage.error(error.response?.data?.detail || '批量导出失败')
  } finally {
    exporting.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/district-admin/exam-list')
}

// 重置分配表单
const resetAssignForm = () => {
  assignForm.value = {
    capacity_per_room: 30,
    arrangement_type: 'by_class',
    seat_pattern: 's_shape',
    use_existing_rooms: true
  }
  assignFormRef.value?.resetFields()
}

// 获取考试类型名称
const getExamTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    midterm: '期中考试',
    final: '期末考试',
    monthly: '月考',
    unit: '单元测试',
    mock: '模拟考试',
    district_unified: '区县统考',
    entrance: '中考/高考'
  }
  return typeMap[type] || type
}

// 获取状态名称
const getStatusName = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    scheduled: '已安排',
    in_progress: '进行中',
    completed: '已完成'
  }
  return statusMap[status] || status
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    draft: 'info',
    scheduled: 'warning',
    in_progress: 'primary',
    completed: 'success'
  }
  return typeMap[status] || ''
}

// 下载导入模板
const downloadTemplate = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${getApiBaseUrl()}/import/template/city_exam_number`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )

    // 下载文件
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `city_exam_number_import_template.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('模板下载成功')
  } catch (error: any) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

// 导出考号映射表
const exportExamNumbers = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${getApiBaseUrl()}/exams/${examId.value}/exam-numbers/export`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )

    // 下载文件
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${examInfo.value.name}_考号映射表_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('考号映射表导出成功')
  } catch (error: any) {
    console.error('导出考号映射表失败:', error)
    if (error.response?.status === 404) {
      ElMessage.error('该考试暂无考号映射数据，请先进行考场编排')
    } else {
      ElMessage.error('导出考号映射表失败')
    }
  }
}

// 处理文件选择
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    importFile.value = file.raw
  }
}

// 提交导入
const submitImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }

  importing.value = true
  try {
    const token = localStorage.getItem('access_token')
    const formData = new FormData()
    formData.append('file', importFile.value)

    const response = await axios.post(
      `${getApiBaseUrl()}/import?strategy_type=city_exam_number&exam_id=${examId.value}`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    // 保存导入结果
    importResult.value = response.data

    // 关闭导入对话框，显示结果对话框
    showImportDialog.value = false
    showImportResultDialog.value = true

    if (response.data.failed === 0) {
      ElMessage.success(`导入成功！共 ${response.data.total} 条记录`)
    } else {
      ElMessage.warning(`导入完成：成功 ${response.data.success} 条，失败 ${response.data.failed} 条`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败，请检查文件格式是否正确')
  } finally {
    importing.value = false
  }
}

// 重置导入对话框
const resetImportDialog = () => {
  importFile.value = null
  uploadRef.value?.clearFiles()
  importResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: []
  }
}

// 初始化
onMounted(() => {
  loadExamInfo()
  loadExamRooms()
})
</script>

<style scoped>
.exam-room-management {
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

.exam-info {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.extra-info {
  font-size: 14px;
  color: #909399;
}

.rooms-card {
  margin-bottom: 20px;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.import-instructions {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.import-instructions ul {
  margin: 10px 0 0 20px;
  padding: 0;
}

.import-instructions li {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}

.upload-demo {
  margin-top: 20px;
}

.result-summary {
  text-align: left;
  padding: 20px;
}

.result-summary p {
  margin: 8px 0;
  font-size: 14px;
}

.import-result :deep(.el-result__icon) {
  font-size: 48px;
}
</style>
