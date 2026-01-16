<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>管理教研员账号，包括区县教研员和学校教研员。教研员可以参与考试管理和增值评价分析。
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
          <option value="">所有区域</option>
          <option v-for="region in allRegions" :key="region.id" :value="region.id">
            {{ region.name }}
          </option>
        </select>

        <select
          v-model="filters.school_id"
          @change="loadResearchers"
          class="px-3 py-2 border rounded-lg"
        >
          <option value="">所有学校</option>
          <option v-for="school in filteredSchools" :key="school.id" :value="school.id">
            {{ school.name }}
          </option>
        </select>

        <input
          v-model="filters.search"
          @input="debouncedLoadResearchers"
          type="text"
          placeholder="搜索姓名、用户名、邮箱..."
          class="px-3 py-2 border rounded-lg w-64"
        />

        <button
          @click="loadResearchers"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          🔄 刷新
        </button>

        <div class="ml-auto flex gap-2">
          <button
            @click="openCreateResearcherModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 添加教研员
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

    <!-- 教研员列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">所属区域</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">所属学校</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后登录</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">加载中...</td>
          </tr>
          <tr v-else-if="researchers.length === 0">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">暂无教研员数据</td>
          </tr>
          <tr v-else v-for="researcher in researchers" :key="researcher.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ researcher.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ researcher.full_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ researcher.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ researcher.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ researcher.region_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ researcher.school_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="researcher.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                激活
              </span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                停用
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ researcher.last_login ? formatDate(researcher.last_login) : '从未登录' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button @click="editResearcher(researcher)" class="text-blue-600 hover:text-blue-900">
                编辑
              </button>
              <button
                @click="toggleResearcherStatus(researcher)"
                :class="researcher.is_active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
              >
                {{ researcher.is_active ? '停用' : '激活' }}
              </button>
              <button @click="resetPassword(researcher)" class="text-purple-600 hover:text-purple-900">
                重置密码
              </button>
              <button @click="deleteResearcher(researcher)" class="text-red-600 hover:text-red-900">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          共 {{ total }} 位教研员
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage > 1 && loadResearchers(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-1 text-gray-600">
            第 {{ currentPage }} 页
          </span>
          <button
            @click="currentPage * pageSize < total && loadResearchers(currentPage + 1)"
            :disabled="currentPage * pageSize >= total"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑教研员对话框 -->
    <el-dialog
      v-model="showResearcherModal"
      :title="editingResearcher ? '编辑教研员' : '添加教研员'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="researcherForm" label-width="120px">
        <el-form-item label="姓名">
          <el-input v-model="researcherForm.full_name" placeholder="请输入教研员姓名" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="researcherForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="researcherForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!editingResearcher" label="初始密码">
          <el-input v-model="researcherForm.password" type="password" placeholder="请输入初始密码" />
        </el-form-item>
        <el-form-item label="所属区域" required>
          <el-select v-model="researcherForm.region_id" placeholder="请选择区域" class="w-full" @change="handleFormRegionChange">
            <el-option v-for="region in allRegions" :key="region.id" :label="region.name" :value="region.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属学校">
          <el-select v-model="researcherForm.school_id" placeholder="请选择学校（可选）" class="w-full" :disabled="!researcherForm.region_id" clearable>
            <el-option v-for="school in formFilteredSchools" :key="school.id" :label="school.name" :value="school.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="researcherForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResearcherModal = false">取消</el-button>
        <el-button type="primary" @click="saveResearcher" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showImportDialog" title="批量导入教研员" width="800px">
      <div class="space-y-4">
        <el-alert title="导入说明" type="info" :closable="false" show-icon>
          <p>请按照模板格式填写教研员信息。支持导入的字段：用户名、姓名、邮箱、所属区域、所属学校。</p>
        </el-alert>
        <el-button type="primary" @click="downloadTemplate">📥 下载导入模板</el-button>
        <el-upload ref="uploadRef" :auto-upload="false" :limit="1" accept=".xlsx,.xls" :on-change="handleFileChange" drag>
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">只支持 .xlsx 或 .xls 格式的 Excel 文件</div>
          </template>
        </el-upload>
      </div>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="startImport" :loading="importing">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import adminService, { type User, type Region, type School } from '@/services/admin'
import type { UploadFile } from 'element-plus'
import * as XLSX from 'xlsx'

// 状态管理
const researchers = ref<User[]>([])
const allRegions = ref<Region[]>([])
const allSchools = ref<School[]>([])
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
  search?: string
}>({})

// 计算属性
const filteredSchools = computed(() => {
  if (filters.value.region_id) {
    return allSchools.value.filter(s => s.region_id === filters.value.region_id)
  }
  return allSchools.value
})

const formFilteredSchools = computed(() => {
  if (researcherForm.value.region_id) {
    return allSchools.value.filter(s => s.region_id === researcherForm.value.region_id)
  }
  return allSchools.value
})

// 对话框状态
const showResearcherModal = ref(false)
const showImportDialog = ref(false)
const editingResearcher = ref<User | null>(null)

// 表单数据
const researcherForm = ref({
  full_name: '',
  username: '',
  email: '',
  password: '',
  region_id: undefined as number | undefined,
  school_id: undefined as number | undefined,
  is_active: true
})

// 导入相关
const uploadRef = ref()
const importFile = ref<File | null>(null)

// 防抖加载
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const debouncedLoadResearchers = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadResearchers(), 500)
}

// 加载数据
const loadResearchers = async (page?: number) => {
  if (page) currentPage.value = page
  loading.value = true
  try {
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      role: 'researcher',
      search: filters.value.search
    })
    let filteredUsers = response.users
    if (filters.value.region_id) {
      filteredUsers = filteredUsers.filter(u => u.region_id === filters.value.region_id)
    }
    if (filters.value.school_id) {
      filteredUsers = filteredUsers.filter(u => u.school_id === filters.value.school_id)
    }
    researchers.value = filteredUsers
    total.value = filteredUsers.length
  } catch (error) {
    ElMessage.error('加载教研员列表失败')
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
  loadResearchers()
}

const handleFormRegionChange = () => {
  researcherForm.value.school_id = undefined
}

// 工具函数
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 教研员操作
const openCreateResearcherModal = () => {
  editingResearcher.value = null
  resetForm()
  showResearcherModal.value = true
}

const editResearcher = (researcher: User) => {
  editingResearcher.value = researcher
  researcherForm.value = {
    full_name: researcher.full_name || '',
    username: researcher.username,
    email: researcher.email,
    password: '',
    region_id: researcher.region_id || undefined,
    school_id: researcher.school_id || undefined,
    is_active: researcher.is_active
  }
  showResearcherModal.value = true
}

const saveResearcher = async () => {
  if (!researcherForm.value.username || !researcherForm.value.email || !researcherForm.value.region_id) {
    ElMessage.warning('请填写必填字段')
    return
  }
  if (!editingResearcher.value && !researcherForm.value.password) {
    ElMessage.warning('请输入初始密码')
    return
  }

  saving.value = true
  try {
    if (editingResearcher.value) {
      await adminService.updateUser(editingResearcher.value.id, {
        username: researcherForm.value.username,
        email: researcherForm.value.email,
        full_name: researcherForm.value.full_name,
        region_id: researcherForm.value.region_id,
        school_id: researcherForm.value.school_id,
        is_active: researcherForm.value.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await adminService.createUser({
        username: researcherForm.value.username,
        email: researcherForm.value.email,
        full_name: researcherForm.value.full_name,
        password: researcherForm.value.password,
        role: 'researcher',
        region_id: researcherForm.value.region_id,
        school_id: researcherForm.value.school_id,
        is_active: researcherForm.value.is_active
      })
      ElMessage.success('创建成功')
    }
    showResearcherModal.value = false
    loadResearchers()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const toggleResearcherStatus = async (researcher: User) => {
  try {
    await adminService.toggleUserStatus(researcher.id)
    ElMessage.success(researcher.is_active ? '已停用' : '已激活')
    loadResearchers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resetPassword = async (researcher: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置教研员 ${researcher.full_name || researcher.username} 的密码吗？`,
      '重置密码',
      { type: 'warning' }
    )
    const result = await adminService.resetUserPassword(researcher.id)
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

const deleteResearcher = async (researcher: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除教研员 ${researcher.full_name || researcher.username} 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await adminService.deleteUser(researcher.id)
    ElMessage.success('删除成功')
    loadResearchers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  researcherForm.value = {
    full_name: '',
    username: '',
    email: '',
    password: '',
    region_id: undefined,
    school_id: undefined,
    is_active: true
  }
}

// 导入相关
const openImportDialog = () => {
  importFile.value = null
  showImportDialog.value = true
}

const downloadTemplate = () => {
  const template = [
    ['用户名*', '姓名*', '邮箱*', '所属区域*', '所属学校'],
    ['researcher001', '张教研员', 'researcher001@example.com', '开平市', ''],
    ['researcher002', '李教研员', 'researcher002@example.com', '开平市', '开平市第一中学']
  ]
  const ws = XLSX.utils.aoa_to_sheet(template)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '教研员导入模板')
  XLSX.writeFile(wb, '教研员导入模板.xlsx')
}

const handleFileChange = (file: UploadFile) => {
  importFile.value = file.raw as File
}

const startImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importing.value = true
  try {
    // TODO: 实现批量导入逻辑
    ElMessage.success('导入功能待实现')
    showImportDialog.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 生命周期
onMounted(() => {
  loadRegions()
  loadSchools()
  loadResearchers()
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
