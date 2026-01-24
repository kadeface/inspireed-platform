<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>管理系统管理员账号，包括超级管理员、区县管理员、学校管理员。管理员可以访问系统设置和组织架构管理。
      </p>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap items-center gap-4 mb-4">
        <!-- 筛选器 -->
        <select
          v-model="filters.admin_role"
          @change="loadAdmins"
          class="px-3 py-2 border rounded-lg"
        >
          <option value="">所有管理员类型</option>
          <option value="admin">超级管理员</option>
          <option value="district_admin">区县管理员</option>
          <option value="school_admin">学校管理员</option>
        </select>

        <select
          v-model="filters.region_id"
          @change="loadAdmins"
          class="px-3 py-2 border rounded-lg"
        >
          <option value="">所有区域</option>
          <option v-for="region in allRegions" :key="region.id" :value="region.id">
            {{ region.name }}
          </option>
        </select>

        <select
          v-model="filters.school_id"
          @change="loadAdmins"
          class="px-3 py-2 border rounded-lg"
        >
          <option value="">所有学校</option>
          <option v-for="school in filteredSchools" :key="school.id" :value="school.id">
            {{ school.name }}
          </option>
        </select>

        <input
          v-model="filters.search"
          @input="debouncedLoadAdmins"
          type="text"
          placeholder="搜索姓名、用户名、邮箱..."
          class="px-3 py-2 border rounded-lg w-64"
        />

        <button
          @click="loadAdmins"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          🔄 刷新
        </button>

        <div class="ml-auto flex gap-2">
          <button
            @click="openCreateAdminModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 添加管理员
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

    <!-- 管理员列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">管理员类型</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">所属区域/学校</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后登录</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">加载中...</td>
          </tr>
          <tr v-else-if="admins.length === 0">
            <td :colspan="9" class="px-6 py-4 text-center text-gray-500">暂无管理员数据</td>
          </tr>
          <tr v-else v-for="admin in admins" :key="admin.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ admin.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ admin.full_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ admin.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ admin.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                class="px-2 py-1 text-xs font-semibold rounded-full"
                :class="getAdminRoleBadgeClass(admin.role)"
              >
                {{ getAdminRoleDisplayName(admin.role) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ getAdminScopeDisplay(admin) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span v-if="admin.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                激活
              </span>
              <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                停用
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ admin.last_login ? formatDate(admin.last_login) : '从未登录' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button @click="editAdmin(admin)" class="text-blue-600 hover:text-blue-900">
                编辑
              </button>
              <button
                @click="toggleAdminStatus(admin)"
                :class="admin.is_active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
              >
                {{ admin.is_active ? '停用' : '激活' }}
              </button>
              <button @click="resetPassword(admin)" class="text-purple-600 hover:text-purple-900">
                重置密码
              </button>
              <button
                v-if="admin.role !== 'admin'"
                @click="deleteAdmin(admin)"
                class="text-red-600 hover:text-red-900"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          共 {{ total }} 位管理员
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage > 1 && loadAdmins(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-1 text-gray-600">
            第 {{ currentPage }} 页
          </span>
          <button
            @click="currentPage * pageSize < total && loadAdmins(currentPage + 1)"
            :disabled="currentPage * pageSize >= total"
            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑管理员对话框 -->
    <el-dialog
      v-model="showAdminModal"
      :title="editingAdmin ? '编辑管理员' : '添加管理员'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="adminForm" label-width="120px">
        <el-form-item label="姓名">
          <el-input v-model="adminForm.full_name" placeholder="请输入管理员姓名" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="adminForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="adminForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!editingAdmin" label="初始密码">
          <el-input v-model="adminForm.password" type="password" placeholder="请输入初始密码" />
        </el-form-item>
        <el-form-item label="管理员类型" required>
          <el-select v-model="adminForm.role" placeholder="请选择管理员类型" class="w-full" @change="handleAdminRoleChange">
            <el-option label="超级管理员" value="admin" />
            <el-option label="区县管理员" value="district_admin" />
            <el-option label="学校管理员" value="school_admin" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="adminForm.role === 'district_admin' || adminForm.role === 'school_admin'" label="所属区域" required>
          <el-select v-model="adminForm.region_id" placeholder="请选择区域" class="w-full" @change="handleRegionChange">
            <el-option v-for="region in allRegions" :key="region.id" :label="region.name" :value="region.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="adminForm.role === 'school_admin'" label="所属学校" required>
          <el-select v-model="adminForm.school_id" placeholder="请选择学校" class="w-full" :disabled="!adminForm.region_id">
            <el-option v-for="school in filteredSchools" :key="school.id" :label="school.name" :value="school.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="adminForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdminModal = false">取消</el-button>
        <el-button type="primary" @click="saveAdmin" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showImportDialog" title="批量导入管理员" width="800px">
      <div class="space-y-4">
        <el-alert title="导入说明" type="info" :closable="false" show-icon>
          <p>请按照模板格式填写管理员信息。支持导入的字段：用户名、姓名、邮箱、管理员类型、所属区域/学校。</p>
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
const admins = ref<User[]>([])
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
  admin_role?: string
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

// 对话框状态
const showAdminModal = ref(false)
const showImportDialog = ref(false)
const editingAdmin = ref<User | null>(null)

// 表单数据
const adminForm = ref({
  full_name: '',
  username: '',
  email: '',
  password: '',
  role: 'district_admin',
  region_id: undefined as number | undefined,
  school_id: undefined as number | undefined,
  is_active: true
})

// 导入相关
const uploadRef = ref()
const importFile = ref<File | null>(null)

// 防抖加载
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const debouncedLoadAdmins = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadAdmins(), 500)
}

// 加载数据
const loadAdmins = async (page?: number) => {
  if (page) currentPage.value = page
  loading.value = true
  try {
    // 获取管理员类型的用户
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      search: filters.value.search
    })
    // 筛选管理员角色
    admins.value = response.users.filter(u =>
      ['admin', 'district_admin', 'school_admin'].includes(u.role)
    )
    // 进一步筛选
    if (filters.value.admin_role) {
      admins.value = admins.value.filter(u => u.role === filters.value.admin_role)
    }
    if (filters.value.region_id) {
      admins.value = admins.value.filter(u => u.region_id === filters.value.region_id)
    }
    if (filters.value.school_id) {
      admins.value = admins.value.filter(u => u.school_id === filters.value.school_id)
    }
    total.value = admins.value.length
  } catch (error) {
    ElMessage.error('加载管理员列表失败')
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
const handleAdminRoleChange = () => {
  adminForm.value.region_id = undefined
  adminForm.value.school_id = undefined
}

const handleRegionChange = () => {
  adminForm.value.school_id = undefined
}

// 工具函数
const getAdminRoleDisplayName = (role: string): string => {
  const roleMap: Record<string, string> = {
    admin: '超级管理员',
    district_admin: '区县管理员',
    school_admin: '学校管理员'
  }
  return roleMap[role] || role
}

const getAdminRoleBadgeClass = (role: string): string => {
  const classMap: Record<string, string> = {
    admin: 'bg-red-100 text-red-800',
    district_admin: 'bg-purple-100 text-purple-800',
    school_admin: 'bg-orange-100 text-orange-800'
  }
  return classMap[role] || 'bg-gray-100 text-gray-800'
}

const getAdminScopeDisplay = (admin: User): string => {
  if (admin.role === 'admin') return '全局'
  if (admin.role === 'district_admin') return admin.region_name || '-'
  if (admin.role === 'school_admin') return admin.school_name || '-'
  return '-'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 管理员操作
const openCreateAdminModal = () => {
  editingAdmin.value = null
  resetForm()
  showAdminModal.value = true
}

const editAdmin = (admin: User) => {
  editingAdmin.value = admin
  adminForm.value = {
    full_name: admin.full_name || '',
    username: admin.username,
    email: admin.email,
    password: '',
    role: admin.role,
    region_id: admin.region_id || undefined,
    school_id: admin.school_id || undefined,
    is_active: admin.is_active
  }
  showAdminModal.value = true
}

const saveAdmin = async () => {
  if (!adminForm.value.username || !adminForm.value.email) {
    ElMessage.warning('请填写必填字段')
    return
  }
  if (!editingAdmin.value && !adminForm.value.password) {
    ElMessage.warning('请输入初始密码')
    return
  }

  saving.value = true
  try {
    if (editingAdmin.value) {
      await adminService.updateUser(editingAdmin.value.id, {
        username: adminForm.value.username,
        email: adminForm.value.email,
        full_name: adminForm.value.full_name,
        role: adminForm.value.role,
        region_id: adminForm.value.region_id,
        school_id: adminForm.value.school_id,
        is_active: adminForm.value.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await adminService.createUser({
        username: adminForm.value.username,
        email: adminForm.value.email,
        full_name: adminForm.value.full_name,
        password: adminForm.value.password,
        role: adminForm.value.role as any,
        region_id: adminForm.value.region_id,
        school_id: adminForm.value.school_id,
        is_active: adminForm.value.is_active
      })
      ElMessage.success('创建成功')
    }
    showAdminModal.value = false
    loadAdmins()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const toggleAdminStatus = async (admin: User) => {
  try {
    await adminService.toggleUserStatus(admin.id)
    ElMessage.success(admin.is_active ? '已停用' : '已激活')
    loadAdmins()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resetPassword = async (admin: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置管理员 ${admin.full_name || admin.username} 的密码吗？`,
      '重置密码',
      { type: 'warning' }
    )
    const result = await adminService.resetUserPassword(admin.id)
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

const deleteAdmin = async (admin: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 ${admin.full_name || admin.username} 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await adminService.deleteUser(admin.id)
    ElMessage.success('删除成功')
    loadAdmins()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  adminForm.value = {
    full_name: '',
    username: '',
    email: '',
    password: '',
    role: 'district_admin',
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
    ['用户名*', '姓名*', '邮箱*', '管理员类型*', '所属区域', '所属学校'],
    ['admin001', '张管理员', 'admin001@example.com', '区县管理员', '开平市', ''],
    ['admin002', '李管理员', 'admin002@example.com', '学校管理员', '开平市', '开平市第一中学']
  ]
  const ws = XLSX.utils.aoa_to_sheet(template)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '管理员导入模板')
  XLSX.writeFile(wb, '管理员导入模板.xlsx')
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
  loadAdmins()
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
