<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>管理教师档案信息，包括基本信息、所属学校、职务、联系方式等。支持批量导入教师。
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
          @change="() => loadTeachers()"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有学校</option>
          <option v-for="school in filteredSchools" :key="school.id" :value="school.id">
            {{ school.name }}
          </option>
        </select>

        <input
          v-model="filters.search"
          @input="debouncedLoadTeachers"
          type="text"
          placeholder="搜索姓名、邮箱、工号..."
          class="px-3 py-2 border rounded-lg w-64"
        />

        <button
          @click="() => loadTeachers()"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 whitespace-nowrap"
        >
          🔄 刷新
        </button>

        <div class="ml-auto flex gap-2">
          <button
            @click="openCreateTeacherModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 添加教师
          </button>
          <button
            @click="openImportDialog"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            📥 批量导入
          </button>
          <button
            @click="openBatchDeleteByFilterDialog"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            🗑️ 批量删除（按区域/学校）
          </button>
        </div>
      </div>
    </div>

    <!-- 批量选择工具栏 -->
    <div v-if="selectedTeachers.length > 0" class="bg-blue-50 border-b border-blue-200 px-6 py-3 flex items-center justify-between">
      <div class="text-sm text-blue-800">
        已选择 <span class="font-bold">{{ selectedTeachers.length }}</span> 位教师
      </div>
      <div class="flex gap-2">
        <button
          @click="batchDeleteTeachers"
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
        >
          批量删除
        </button>
        <button
          @click="clearSelection"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
        >
          取消选择
        </button>
      </div>
    </div>

    <!-- 教师列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase w-12">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isSomeSelected"
                @change="toggleSelectAll"
                class="h-4 w-4 text-blue-600 rounded"
              />
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">工号/用户名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">所属学校</th>
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
          <tr v-else-if="teachers.length === 0">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">
              暂无教师数据
            </td>
          </tr>
          <tr v-else v-for="teacher in teachers" :key="teacher.id" :class="{ 'bg-blue-50': selectedTeachers.includes(teacher.id) }">
            <td class="px-6 py-4 whitespace-nowrap">
              <input
                type="checkbox"
                :checked="selectedTeachers.includes(teacher.id)"
                @change="toggleTeacherSelection(teacher.id)"
                class="h-4 w-4 text-blue-600 rounded"
              />
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ teacher.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ teacher.full_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ teacher.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ teacher.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ teacher.school_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="teacher.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                激活
              </span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                停用
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ teacher.last_login ? formatDate(teacher.last_login) : '从未登录' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button
                @click="editTeacher(teacher)"
                class="text-blue-600 hover:text-blue-900"
              >
                编辑
              </button>
              <button
                @click="toggleTeacherStatus(teacher)"
                :class="teacher.is_active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
              >
                {{ teacher.is_active ? '停用' : '激活' }}
              </button>
              <button
                @click="resetPassword(teacher)"
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
          共 {{ total }} 位教师
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage > 1 && loadTeachers(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-1 text-gray-600">
            第 {{ currentPage }} 页
          </span>
          <button
            @click="currentPage * pageSize < total && loadTeachers(currentPage + 1)"
            :disabled="currentPage * pageSize >= total"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑教师对话框 -->
    <el-dialog
      v-model="showTeacherModal"
      :title="editingTeacher ? '编辑教师' : '添加教师'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="teacherForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="teacherForm.full_name" placeholder="请输入教师姓名" />
        </el-form-item>
        <el-form-item label="工号/用户名">
          <el-input v-model="teacherForm.username" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="teacherForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!editingTeacher" label="密码">
          <el-input v-model="teacherForm.password" type="password" placeholder="请输入初始密码" />
        </el-form-item>
        <el-form-item label="所属学校">
          <el-select v-model="teacherForm.school_id" placeholder="输入学校名称搜索或选择学校" class="w-full" filterable>
            <el-option
              v-for="school in filteredSchools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="teacherForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTeacherModal = false">取消</el-button>
        <el-button type="primary" @click="saveTeacher" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入教师"
      width="800px"
    >
      <div class="space-y-4">
        <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          show-icon
        >
          <p>请按照模板格式填写教师信息。支持导入的字段：工号、姓名、邮箱、所属学校。</p>
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
            <el-table-column prop="username" label="工号" width="120" />
            <el-table-column prop="full_name" label="姓名" width="120" />
            <el-table-column prop="email" label="邮箱" width="180" />
            <el-table-column prop="school_name" label="所属学校" />
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

    <!-- 批量删除（按区域/学校）对话框 -->
    <el-dialog
      v-model="showBatchDeleteByFilterDialog"
      title="批量删除教师（按区域/学校）"
      width="700px"
    >
      <div class="space-y-4">
        <el-alert
          title="危险操作"
          type="error"
          :closable="false"
          show-icon
        >
          <p>此操作将批量删除符合条件的教师及其相关数据，不可撤销！</p>
          <p class="mt-2 text-sm">
            将同时删除：
            <br>- 教师账号
            <br>- 相关教学任务
            <br>- 考场监考安排
          </p>
        </el-alert>

        <el-form :model="batchDeleteForm" label-width="100px">
          <el-form-item label="所属区域">
            <el-select
              v-model="batchDeleteForm.region_id"
              @change="handleBatchDeleteRegionChange"
              placeholder="选择区域（不选则删除所有区域）"
              clearable
              class="w-full"
            >
              <el-option
                v-for="region in allRegions"
                :key="region.id"
                :label="region.name"
                :value="region.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="所属学校">
            <el-select
              v-model="batchDeleteForm.school_id"
              placeholder="输入学校名称搜索或选择学校（不选则删除所有学校）"
              clearable
              filterable
              class="w-full"
              :disabled="!batchDeleteForm.region_id"
            >
              <el-option
                v-for="school in filteredSchoolsForBatchDelete"
                :key="school.id"
                :label="school.name"
                :value="school.id"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <div v-if="previewResult" class="border rounded p-4 bg-gray-50">
          <h4 class="font-medium mb-2">删除预览</h4>
          <p class="text-lg font-bold text-red-600">{{ previewResult.message }}</p>
          <div v-if="previewResult.preview_users && previewResult.preview_users.length > 0" class="mt-3">
            <p class="text-sm text-gray-600 mb-2">部分教师列表（显示前{{ previewResult.showing }}个）：</p>
            <el-table :data="previewResult.preview_users" max-height="200" size="small">
              <el-table-column prop="username" label="工号" width="100" />
              <el-table-column prop="full_name" label="姓名" width="100" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="school_name" label="学校" />
            </el-table>
          </div>
        </div>

        <div class="flex gap-2">
          <el-button
            type="warning"
            @click="previewBatchDelete"
            :loading="previewing"
            :disabled="deleting"
          >
            🔍 预览删除范围
          </el-button>
          <el-button
            v-if="previewResult"
            type="danger"
            @click="confirmBatchDelete"
            :loading="deleting"
            :disabled="!previewResult || previewResult.total_count === 0"
          >
            ⚠️ 确认删除
          </el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="showBatchDeleteByFilterDialog = false" :disabled="deleting">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { adminService, type User, type Region, type School } from '@/services/admin'
import type { UploadFile } from 'element-plus'
import * as XLSX from 'xlsx'

// 状态管理
const teachers = ref<User[]>([])
const allRegions = ref<Region[]>([])
const allSchools = ref<School[]>([])
const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const selectedTeachers = ref<number[]>([])
const showBatchDeleteByFilterDialog = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选器
const filters = ref<{
  region_id?: number
  school_id?: number
  search?: string
}>({})

// 计算属性
const filteredSchools = computed(() => {
  if (filters.value.region_id) {
    return allSchools.value.filter(s => s.region_id === filters.value.region_id)
  }
  return allSchools.value
})

// 批量删除对话框中使用的学校筛选（根据选择的区域过滤）
const filteredSchoolsForBatchDelete = computed(() => {
  if (batchDeleteForm.value.region_id) {
    return allSchools.value.filter(s => s.region_id === batchDeleteForm.value.region_id)
  }
  return allSchools.value
})

// 批量选择相关
const isAllSelected = computed(() => {
  return teachers.value.length > 0 && selectedTeachers.value.length === teachers.value.length
})

const isSomeSelected = computed(() => {
  return selectedTeachers.value.length > 0 && selectedTeachers.value.length < teachers.value.length
})

// 对话框状态
const showTeacherModal = ref(false)
const showImportDialog = ref(false)
const editingTeacher = ref<User | null>(null)

// 批量删除相关
const batchDeleteForm = ref<{
  region_id?: number
  school_id?: number
}>({
  region_id: undefined,
  school_id: undefined
})

const previewResult = ref<any>(null)
const previewing = ref(false)
const deleting = ref(false)

// 表单数据
const teacherForm = ref({
  full_name: '',
  username: '',
  email: '',
  password: '',
  school_id: undefined as number | undefined,
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
const debouncedLoadTeachers = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadTeachers(), 500)
}

// 加载数据
const loadTeachers = async (page?: number) => {
  if (page) currentPage.value = page
  loading.value = true
  try {
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      role: 'teacher',
      search: filters.value.search,
      // 需要后端支持按学校筛选，暂时在前端过滤
    })
    teachers.value = response.users.filter(u => {
      if (filters.value.school_id) return u.school_id === filters.value.school_id
      return true
    })
    total.value = teachers.value.length
  } catch (error: unknown) {
    const d = (error as { response?: { data?: { detail?: unknown } } })?.response?.data
      ?.detail
    const detail =
      typeof d === 'string' ? d : Array.isArray(d) ? JSON.stringify(d) : ''
    toast.error(detail ? `加载教师列表失败：${detail}` : '加载教师列表失败')
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

// 事件处理
const handleRegionChange = () => {
  filters.value.school_id = undefined
  loadTeachers()
}

// 教师操作
const openCreateTeacherModal = () => {
  editingTeacher.value = null
  resetForm()
  showTeacherModal.value = true
}

const editTeacher = (teacher: User) => {
  editingTeacher.value = teacher
  teacherForm.value = {
    full_name: teacher.full_name || '',
    username: teacher.username,
    email: teacher.email,
    password: '',
    school_id: teacher.school_id || undefined,
    is_active: teacher.is_active
  }
  showTeacherModal.value = true
}

const saveTeacher = async () => {
  // 表单验证
  if (!teacherForm.value.username) {
    ElMessage.warning('请输入工号')
    return
  }
  if (!teacherForm.value.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  if (!editingTeacher.value && !teacherForm.value.password) {
    ElMessage.warning('请输入密码')
    return
  }

  saving.value = true
  try {
    if (editingTeacher.value) {
      await adminService.updateUser(editingTeacher.value.id, {
        username: teacherForm.value.username,
        email: teacherForm.value.email,
        full_name: teacherForm.value.full_name,
        school_id: teacherForm.value.school_id,
        is_active: teacherForm.value.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await adminService.createUser({
        username: teacherForm.value.username,
        email: teacherForm.value.email,
        full_name: teacherForm.value.full_name,
        password: teacherForm.value.password,
        role: 'teacher',
        school_id: teacherForm.value.school_id,
        is_active: teacherForm.value.is_active
      })
      ElMessage.success('创建成功')
    }
    showTeacherModal.value = false
    loadTeachers()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const toggleTeacherStatus = async (teacher: User) => {
  try {
    await adminService.toggleUserStatus(teacher.id)
    ElMessage.success(teacher.is_active ? '已停用' : '已激活')
    loadTeachers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resetPassword = async (teacher: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置教师 ${teacher.full_name || teacher.username} 的密码吗？`,
      '重置密码',
      { type: 'warning' }
    )
    const result = await adminService.resetUserPassword(teacher.id)
    if (result.new_password) {
      ElMessageBox.alert(`新密码：${result.new_password}`, '密码重置成功', {
        type: 'success',
        confirmButtonText: '复制',
        callback: () => {
          navigator.clipboard.writeText(result.new_password!)
        }
      })
    } else {
      ElMessageBox.alert(
        result.note || '新密码已生成，请通过安全渠道告知用户（接口不返回明文密码）。',
        '密码重置成功',
        { type: 'success', confirmButtonText: '知道了' }
      )
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置密码失败')
    }
  }
}

const resetForm = () => {
  teacherForm.value = {
    full_name: '',
    username: '',
    email: '',
    password: '',
    school_id: undefined,
    is_active: true
  }
}

// 批量选择和删除
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedTeachers.value = []
  } else {
    selectedTeachers.value = teachers.value.map(t => t.id)
  }
}

const toggleTeacherSelection = (teacherId: number) => {
  const index = selectedTeachers.value.indexOf(teacherId)
  if (index > -1) {
    selectedTeachers.value.splice(index, 1)
  } else {
    selectedTeachers.value.push(teacherId)
  }
}

const clearSelection = () => {
  selectedTeachers.value = []
}

const batchDeleteTeachers = async () => {
  if (selectedTeachers.value.length === 0) {
    toast.warning('请先选择要删除的教师')
    return
  }

  const teacherNames = teachers.value
    .filter(t => selectedTeachers.value.includes(t.id))
    .map(t => t.full_name || t.username)
    .join(', ')

  if (!confirm(`确定要删除以下 ${selectedTeachers.value.length} 位教师吗？\n\n${teacherNames}\n\n此操作不可撤销。`)) {
    return
  }

  try {
    const result = await adminService.batchDeleteUsers(selectedTeachers.value)
    teachers.value = teachers.value.filter(t => !selectedTeachers.value.includes(t.id))
    total.value -= result.deleted_count
    toast.success(
      `成功删除 ${result.deleted_count} 位教师` +
      (result.failed_count ? `，失败 ${result.failed_count} 位` : '')
    )
    clearSelection()
  } catch (error: any) {
    console.error('Failed to batch delete teachers:', error)
    toast.error(error.response?.data?.detail || '批量删除教师失败')
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
    ['工号*', '姓名*', '邮箱*', '所属学校*'],
    ['T001', '张老师', 'zhang@example.com', '示例学校'],
    ['T002', '李老师', 'li@example.com', '示例学校']
  ]
  const ws = XLSX.utils.aoa_to_sheet(template)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '教师导入模板')
  XLSX.writeFile(wb, '教师导入模板.xlsx')
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
    const users = importPreview.value.map(row => ({
      username: row['工号*'],
      full_name: row['姓名*'],
      email: row['邮箱*'],
      password: '123456', // 默认密码
      role: 'teacher' as const,
      is_active: true,
      school_id: allSchools.value.find(s => s.name === row['所属学校*'])?.id
    }))

    const result = await adminService.batchImportUsers(users)
    ElMessage.success(`成功导入 ${result.success_count} 位教师`)
    showImportDialog.value = false
    loadTeachers()
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 批量删除（按条件）相关
const openBatchDeleteByFilterDialog = () => {
  batchDeleteForm.value = {
    region_id: filters.value.region_id,
    school_id: filters.value.school_id
  }
  previewResult.value = null
  showBatchDeleteByFilterDialog.value = true
}

const handleBatchDeleteRegionChange = () => {
  // 区域变化时，清空学校选择
  batchDeleteForm.value.school_id = undefined
}

const previewBatchDelete = async () => {
  previewing.value = true
  previewResult.value = null
  try {
    const result = await adminService.previewBatchDeleteByFilter({
      role: 'teacher',
      region_id: batchDeleteForm.value.region_id,
      school_id: batchDeleteForm.value.school_id
    })
    previewResult.value = result
    toast.success(`找到 ${result.total_count} 位教师`)
  } catch (error: any) {
    console.error('Failed to preview batch delete:', error)
    toast.error(error.response?.data?.detail || '预览失败')
  } finally {
    previewing.value = false
  }
}

const confirmBatchDelete = async () => {
  if (!previewResult.value || previewResult.value.total_count === 0) {
    toast.warning('没有要删除的教师')
    return
  }

  if (!confirm(`确定要删除 ${previewResult.value.total_count} 位教师吗？\n\n此操作不可撤销，将同时删除：\n- 教师账号\n- 相关教学任务\n- 考场监考安排`)) {
    return
  }

  deleting.value = true
  try {
    const result = await adminService.batchDeleteByFilter({
      role: 'teacher',
      region_id: batchDeleteForm.value.region_id,
      school_id: batchDeleteForm.value.school_id,
      confirm: true
    })
    toast.success(
      `成功删除 ${result.deleted_count} 位教师\n` +
      `同时删除了 ${result.exam_mappings_deleted} 条考号映射\n` +
      `和 ${result.exam_room_students_deleted} 条考场安排记录`
    )
    showBatchDeleteByFilterDialog.value = false
    loadTeachers() // 刷新列表
  } catch (error: any) {
    console.error('Failed to batch delete by filter:', error)
    toast.error(error.response?.data?.detail || '批量删除失败')
  } finally {
    deleting.value = false
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
  loadTeachers()
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
