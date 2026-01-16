<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>管理学生档案信息，包括基本信息、所属班级、学籍号等。支持批量导入学生。
      </p>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap items-center gap-4 mb-4">
        <!-- 筛选器 -->
        <select
          v-model="filters.region_id"
          @change="handleRegionChange"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有区域</option>
          <option v-for="region in allRegions" :key="region.id" :value="region.id">
            {{ region.name }}
          </option>
        </select>

        <select
          v-model="filters.school_id"
          @change="handleSchoolChange"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有学校</option>
          <option v-for="school in filteredSchools" :key="school.id" :value="school.id">
            {{ school.name }}
          </option>
        </select>

        <select
          v-model="filters.grade_id"
          @change="loadStudents"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有年级</option>
          <option v-for="grade in grades" :key="grade.id" :value="grade.id">
            {{ grade.name }}
          </option>
        </select>

        <select
          v-model="filters.classroom_id"
          @change="loadStudents"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有班级</option>
          <option v-for="classroom in filteredClassrooms" :key="classroom.id" :value="classroom.id">
            {{ classroom.name }}
          </option>
        </select>

        <input
          v-model="filters.search"
          @input="debouncedLoadStudents"
          type="text"
          placeholder="搜索姓名、学号、学籍号..."
          class="px-3 py-2 border rounded-lg w-64"
        />

        <button
          @click="loadStudents"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          🔄 刷新
        </button>

        <div class="ml-auto flex gap-2">
          <button
            @click="openCreateStudentModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 添加学生
          </button>
          <button
            @click="openImportDialog"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            📥 批量导入
          </button>
        </div>
      </div>
    </div>

    <!-- 学生列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学籍号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">所属班级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后登录</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">
              加载中...
            </td>
          </tr>
          <tr v-else-if="students.length === 0">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">
              暂无学生数据
            </td>
          </tr>
          <tr v-else v-for="student in students" :key="student.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ student.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ student.full_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.student_id_number || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ student.classroom_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="student.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                激活
              </span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                停用
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ student.last_login ? formatDate(student.last_login) : '从未登录' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button
                @click="editStudent(student)"
                class="text-blue-600 hover:text-blue-900"
              >
                编辑
              </button>
              <button
                @click="toggleStudentStatus(student)"
                :class="student.is_active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
              >
                {{ student.is_active ? '停用' : '激活' }}
              </button>
              <button
                @click="resetPassword(student)"
                class="text-purple-600 hover:text-purple-900"
              >
                重置密码
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          共 {{ total }} 位学生
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage > 1 && loadStudents(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-1 text-gray-600">
            第 {{ currentPage }} 页
          </span>
          <button
            @click="currentPage * pageSize < total && loadStudents(currentPage + 1)"
            :disabled="currentPage * pageSize >= total"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑学生对话框 -->
    <el-dialog
      v-model="showStudentModal"
      :title="editingStudent ? '编辑学生' : '添加学生'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="studentForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="studentForm.full_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="studentForm.username" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="学籍号">
          <el-input v-model="studentForm.student_id_number" placeholder="请输入学籍号（身份证号等）" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="studentForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!editingStudent" label="密码">
          <el-input v-model="studentForm.password" type="password" placeholder="请输入初始密码" />
        </el-form-item>
        <el-form-item label="所属学校">
          <el-select v-model="studentForm.school_id" @change="handleFormSchoolChange" placeholder="请选择学校" class="w-full">
            <el-option
              v-for="school in filteredSchools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="studentForm.grade_id" @change="handleFormGradeChange" placeholder="请选择年级" class="w-full" :disabled="!studentForm.school_id">
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="studentForm.classroom_id" placeholder="请选择班级" class="w-full" :disabled="!studentForm.school_id || !studentForm.grade_id">
            <el-option
              v-for="classroom in formClassrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学生类型">
          <el-select v-model="studentForm.student_type" placeholder="请选择学生类型" class="w-full">
            <el-option label="未分科" value="none" />
            <el-option label="文科" value="arts" />
            <el-option label="理科" value="science" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="studentForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStudentModal = false">取消</el-button>
        <el-button type="primary" @click="saveStudent" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入学生"
      width="800px"
    >
      <div class="space-y-4">
        <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          show-icon
        >
          <p>请按照模板格式填写学生信息。支持导入的字段：学号、姓名、学籍号、邮箱、所属学校、年级、班级。</p>
        </el-alert>

        <el-button type="primary" @click="downloadTemplate">
          📥 下载导入模板
        </el-button>

        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只支持 .xlsx 或 .xls 格式的 Excel 文件
            </div>
          </template>
        </el-upload>

        <div v-if="importPreview.length > 0" class="border rounded p-4">
          <h4 class="font-medium mb-2">导入预览（共 {{ importPreview.length }} 条）</h4>
          <el-table :data="importPreview" max-height="300" size="small">
            <el-table-column prop="username" label="学号" width="120" />
            <el-table-column prop="full_name" label="姓名" width="120" />
            <el-table-column prop="student_id_number" label="学籍号" width="150" />
            <el-table-column prop="email" label="邮箱" width="180" />
            <el-table-column prop="classroom_name" label="所属班级" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="startImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { adminService, type User, type Region, type School, type Classroom } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import type { UploadFile } from 'element-plus'
import type { Grade } from '@/types/curriculum'
import * as XLSX from 'xlsx'

// 状态管理
const students = ref<User[]>([])
const allRegions = ref<Region[]>([])
const allSchools = ref<School[]>([])
const allClassrooms = ref<Classroom[]>([])
const grades = ref<Grade[]>([])
const loading = ref(false)
const saving = ref(false)
const importing = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选器
const filters = ref<{
  region_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
  search?: string
}>({})

// 计算属性
const filteredSchools = computed(() => {
  if (filters.value.region_id) {
    return allSchools.value.filter(s => s.region_id === filters.value.region_id)
  }
  return allSchools.value
})

const filteredClassrooms = computed(() => {
  let result = allClassrooms.value
  if (filters.value.school_id) {
    result = result.filter(c => c.school_id === filters.value.school_id)
  }
  if (filters.value.grade_id) {
    result = result.filter(c => c.grade_id === filters.value.grade_id)
  }
  return result
})

const formClassrooms = computed(() => {
  let result = allClassrooms.value
  if (studentForm.value.school_id) {
    result = result.filter(c => c.school_id === studentForm.value.school_id)
  }
  if (studentForm.value.grade_id) {
    result = result.filter(c => c.grade_id === studentForm.value.grade_id)
  }
  return result
})

// 对话框状态
const showStudentModal = ref(false)
const showImportDialog = ref(false)
const editingStudent = ref<User | null>(null)

// 表单数据
const studentForm = ref({
  full_name: '',
  username: '',
  student_id_number: '',
  email: '',
  password: '',
  school_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
  classroom_id: undefined as number | undefined,
  student_type: 'none',
  is_active: true
})

// 导入相关
const uploadRef = ref()
const importFile = ref<File | null>(null)
const importPreview = ref<any[]>([])

// Toast
const toast = useToast()

// 防抖加载
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const debouncedLoadStudents = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadStudents(), 500)
}

// 加载数据
const loadStudents = async (page?: number) => {
  if (page) currentPage.value = page
  loading.value = true
  try {
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      role: 'student',
      search: filters.value.search,
    })
    // 在前端过滤（因为后端可能不支持所有筛选条件）
    let filteredUsers = response.users
    if (filters.value.school_id) {
      filteredUsers = filteredUsers.filter(u => u.school_id === filters.value.school_id)
    }
    if (filters.value.grade_id) {
      filteredUsers = filteredUsers.filter(u => u.grade_id === filters.value.grade_id)
    }
    if (filters.value.classroom_id) {
      filteredUsers = filteredUsers.filter(u => u.classroom_id === filters.value.classroom_id)
    }
    students.value = filteredUsers
    total.value = filteredUsers.length
  } catch (error) {
    toast.error('加载学生列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadRegions = async () => {
  try {
    const response = await adminService.getRegions({ size: 1000 })
    allRegions.value = response.regions
  } catch (error) {
    console.error('加载区域失败:', error)
  }
}

const loadSchools = async () => {
  try {
    const response = await adminService.getSchools({ size: 1000 })
    allSchools.value = response.schools
  } catch (error) {
    console.error('加载学校失败:', error)
  }
}

const loadClassrooms = async () => {
  try {
    const response = await adminService.getClassrooms({ size: 1000 })
    allClassrooms.value = response.classrooms
  } catch (error) {
    console.error('加载班级失败:', error)
  }
}

const loadGrades = async () => {
  try {
    grades.value = await curriculumService.getGrades(true)
  } catch (error) {
    console.error('加载年级失败:', error)
  }
}

// 事件处理
const handleRegionChange = () => {
  filters.value.school_id = undefined
  filters.value.grade_id = undefined
  filters.value.classroom_id = undefined
  loadStudents()
}

const handleSchoolChange = () => {
  filters.value.grade_id = undefined
  filters.value.classroom_id = undefined
  loadStudents()
}

const handleFormSchoolChange = () => {
  studentForm.value.grade_id = undefined
  studentForm.value.classroom_id = undefined
}

const handleFormGradeChange = () => {
  studentForm.value.classroom_id = undefined
}

// 学生操作
const openCreateStudentModal = () => {
  editingStudent.value = null
  resetForm()
  showStudentModal.value = true
}

const editStudent = (student: User) => {
  editingStudent.value = student
  studentForm.value = {
    full_name: student.full_name || '',
    username: student.username,
    student_id_number: student.student_id_number || '',
    email: student.email,
    password: '',
    school_id: student.school_id || undefined,
    grade_id: student.grade_id || undefined,
    classroom_id: student.classroom_id || undefined,
    student_type: (student as any).student_type || 'none',
    is_active: student.is_active
  }
  showStudentModal.value = true
}

const saveStudent = async () => {
  if (!studentForm.value.username) {
    ElMessage.warning('请输入学号')
    return
  }
  if (!studentForm.value.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  if (!editingStudent.value && !studentForm.value.password) {
    ElMessage.warning('请输入密码')
    return
  }

  saving.value = true
  try {
    if (editingStudent.value) {
      await adminService.updateUser(editingStudent.value.id, {
        username: studentForm.value.username,
        email: studentForm.value.email,
        full_name: studentForm.value.full_name,
        student_id_number: studentForm.value.student_id_number,
        school_id: studentForm.value.school_id,
        grade_id: studentForm.value.grade_id,
        classroom_id: studentForm.value.classroom_id,
        is_active: studentForm.value.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await adminService.createUser({
        username: studentForm.value.username,
        email: studentForm.value.email,
        full_name: studentForm.value.full_name,
        student_id_number: studentForm.value.student_id_number,
        password: studentForm.value.password,
        role: 'student',
        school_id: studentForm.value.school_id,
        grade_id: studentForm.value.grade_id,
        classroom_id: studentForm.value.classroom_id,
        is_active: studentForm.value.is_active
      })
      ElMessage.success('创建成功')
    }
    showStudentModal.value = false
    loadStudents()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const toggleStudentStatus = async (student: User) => {
  try {
    await adminService.toggleUserStatus(student.id)
    ElMessage.success(student.is_active ? '已停用' : '已激活')
    loadStudents()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resetPassword = async (student: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置学生 ${student.full_name || student.username} 的密码吗？`,
      '重置密码',
      { type: 'warning' }
    )
    const result = await adminService.resetUserPassword(student.id)
    ElMessageBox.alert(`新密码：${result.new_password}`, '密码重置成功', {
      type: 'success',
      confirmButtonText: '复制',
      callback: () => {
        navigator.clipboard.writeText(result.new_password)
      }
    })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置密码失败')
    }
  }
}

const resetForm = () => {
  studentForm.value = {
    full_name: '',
    username: '',
    student_id_number: '',
    email: '',
    password: '',
    school_id: undefined,
    grade_id: undefined,
    classroom_id: undefined,
    student_type: 'none',
    is_active: true
  }
}

// 导入相关
const openImportDialog = () => {
  importFile.value = null
  importPreview.value = []
  showImportDialog.value = true
}

const downloadTemplate = () => {
  const template = [
    ['学号*', '姓名*', '学籍号', '邮箱*', '所属学校*', '年级*', '班级*'],
    ['S001', '张同学', '123456789012345678', 'zhang@example.com', '示例学校', '七年级', '七年级1班'],
    ['S002', '李同学', '987654321098765432', 'li@example.com', '示例学校', '七年级', '七年级2班']
  ]
  const ws = XLSX.utils.aoa_to_sheet(template)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学生导入模板')
  XLSX.writeFile(wb, '学生导入模板.xlsx')
}

const handleFileChange = (file: UploadFile) => {
  importFile.value = file.raw as File
  const reader = new FileReader()
  reader.onload = (e) => {
    const data = new Uint8Array(e.target?.result as ArrayBuffer)
    const workbook = XLSX.read(data, { type: 'array' })
    const worksheet = workbook.Sheets[workbook.SheetNames[0]]
    const json = XLSX.utils.sheet_to_json(worksheet) as any[]
    importPreview.value = json
  }
  reader.readAsArrayBuffer(file.raw as File)
}

const startImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importing.value = true
  try {
    // 调用批量导入API
    const users = importPreview.value.map(row => {
      // 查找对应的班级ID
      const classroom = allClassrooms.value.find(c => c.name === row['班级*'])
      return {
        username: row['学号*'],
        full_name: row['姓名*'],
        student_id_number: row['学籍号'],
        email: row['邮箱*'],
        password: '123456', // 默认密码
        role: 'student' as const,
        is_active: true,
        school_id: classroom?.school_id,
        grade_id: classroom?.grade_id,
        classroom_id: classroom?.id
      }
    })

    const result = await adminService.batchImportUsers(users)
    ElMessage.success(`成功导入 ${result.success_count} 位学生`)
    showImportDialog.value = false
    loadStudents()
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 工具函数
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadRegions()
  loadSchools()
  loadClassrooms()
  loadGrades()
  loadStudents()
})
</script>

<style scoped>
.el-upload {
  width: 100%;
}

.el-upload :deep(.el-upload-dragger) {
  width: 100%;
}
</style>
