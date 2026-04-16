<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-slate-50 border border-slate-200 rounded-xl p-5 flex items-start gap-3">
      <div class="bg-indigo-100 text-indigo-600 rounded-lg p-2 shrink-0">
        <el-icon :size="20"><InfoFilled /></el-icon>
      </div>
      <div>
        <h3 class="text-sm font-bold text-slate-800 mb-1">管理员账号管理</h3>
        <p class="text-sm text-slate-500 leading-relaxed">
          管理系统的所有管理员账号，包括超级管理员、区县管理员和学校管理员。不同角色的管理员拥有不同的权限范围：超级管理员（全局）、区县管理员（特定区域）、学校管理员（特定学校）。
        </p>
      </div>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
      <div class="flex items-center justify-between gap-3 overflow-x-auto">
        <!-- 左侧筛选器 -->
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <el-select
            v-model="filters.admin_role"
            placeholder="类型"
            @change="loadAdmins"
            clearable
            class="!w-32 shrink-0"
          >
            <el-option label="超级管理员" value="admin" />
            <el-option label="区县管理员" value="district_admin" />
            <el-option label="学校管理员" value="school_admin" />
          </el-select>

          <el-select
            v-model="filters.region_id"
            placeholder="区域"
            @change="loadAdmins"
            clearable
            class="!w-32 shrink-0"
          >
            <el-option v-for="region in allRegions" :key="region.id" :label="region.name" :value="region.id" />
          </el-select>

          <el-select
            v-model="filters.school_id"
            placeholder="学校"
            @change="loadAdmins"
            clearable
            class="!w-40 shrink-0"
          >
            <el-option v-for="school in filteredSchools" :key="school.id" :label="school.name" :value="school.id" />
          </el-select>

          <el-input
            v-model="filters.search"
            @input="debouncedLoadAdmins"
            placeholder="搜索..."
            class="!w-48 shrink-0"
            :prefix-icon="Search"
            clearable
          />
          
          <el-button @click="loadAdmins" :icon="Refresh" circle plain />
        </div>

        <!-- 右侧操作按钮 -->
        <div class="flex items-center gap-2 shrink-0">
          <el-button type="success" @click="openImportDialog" :icon="Upload">导入</el-button>
          <el-button type="primary" @click="openCreateAdminModal" :icon="Plus">添加</el-button>
        </div>
      </div>
    </div>

    <!-- 管理员列表 -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
      <el-table
        :data="admins"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column label="管理员信息" min-width="200">
          <template #default="{ row }">
            <div class="flex items-center gap-3">
              <el-avatar :size="32" class="bg-indigo-100 text-indigo-600 text-xs font-bold">
                {{ (row.full_name || row.username).charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="flex flex-col">
                <span class="text-sm font-medium text-slate-900">{{ row.full_name || '-' }}</span>
                <span class="text-xs text-slate-500">{{ row.username }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="角色类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small" effect="light" class="border-0">
              {{ getAdminRoleDisplayName(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="管辖范围" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="text-slate-600">{{ getAdminScopeDisplay(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-1.5">
              <div
                class="w-2 h-2 rounded-full"
                :class="row.is_active ? 'bg-emerald-500' : 'bg-rose-500'"
              ></div>
              <span class="text-sm" :class="row.is_active ? 'text-slate-700' : 'text-slate-400'">
                {{ row.is_active ? '正常' : '停用' }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="最后登录" width="160" align="center">
          <template #default="{ row }">
            <span class="text-xs text-slate-500">{{
              row.last_login ? formatDate(row.last_login) : '从未登录'
            }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-2">
              <el-button link type="primary" size="small" @click="editAdmin(row)">编辑</el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleMoreActions(cmd, row)">
                <el-button link type="info" size="small">
                  更多 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="toggle_status">
                      <span :class="row.is_active ? 'text-amber-600' : 'text-emerald-600'">
                        {{ row.is_active ? '停用账号' : '激活账号' }}
                      </span>
                    </el-dropdown-item>
                    <el-dropdown-item command="reset_password">重置密码</el-dropdown-item>
                    <el-dropdown-item
                      v-if="row.role !== 'admin'"
                      command="delete"
                      class="text-rose-500"
                      divided
                    >
                      删除账号
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div
        class="px-5 py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50"
      >
        <span class="text-sm text-slate-500">共 {{ total }} 条记录</span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, sizes"
          @size-change="loadAdmins"
          @current-change="loadAdmins"
          background
        />
      </div>
    </div>

    <!-- 添加/编辑管理员对话框 -->
    <el-dialog
      v-model="showAdminModal"
      :title="editingAdmin ? '编辑管理员' : '添加管理员'"
      width="640px"
      align-center
      destroy-on-close
      @close="resetForm"
      class="rounded-xl"
    >
      <el-form :model="adminForm" label-width="100px" class="mt-2" label-position="left">
        <div class="bg-slate-50 p-4 rounded-lg border border-slate-100 mb-6">
          <h4 class="text-sm font-bold text-slate-800 mb-4 border-l-4 border-indigo-500 pl-3">
            基本信息
          </h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="姓名" required>
                <el-input v-model="adminForm.full_name" placeholder="真实姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="用户名" required>
                <el-input v-model="adminForm.username" placeholder="登录账号" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="邮箱" required class="mb-0">
            <el-input v-model="adminForm.email" placeholder="contact@example.com" />
          </el-form-item>
        </div>

        <div class="bg-slate-50 p-4 rounded-lg border border-slate-100 mb-6">
          <h4 class="text-sm font-bold text-slate-800 mb-4 border-l-4 border-indigo-500 pl-3">
            权限配置
          </h4>
          <el-form-item label="账号类型" required>
            <el-radio-group v-model="adminForm.role" @change="handleAdminRoleChange">
              <el-radio-button value="admin">超级管理员</el-radio-button>
              <el-radio-button value="district_admin">区县管理员</el-radio-button>
              <el-radio-button value="school_admin">学校管理员</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <transition name="el-fade-in">
            <div v-if="adminForm.role !== 'admin'" class="space-y-4">
              <el-form-item
                label="所属区域"
                :required="adminForm.role === 'district_admin' || adminForm.role === 'school_admin'"
              >
                <el-select
                  v-model="adminForm.region_id"
                  placeholder="选择管辖区域"
                  class="w-full"
                  @change="handleRegionChange"
                >
                  <el-option
                    v-for="region in allRegions"
                    :key="region.id"
                    :label="region.name"
                    :value="region.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item v-if="adminForm.role === 'school_admin'" label="所属学校" required>
                <el-select
                  v-model="adminForm.school_id"
                  placeholder="选择管辖学校"
                  class="w-full"
                  :disabled="!adminForm.region_id"
                  no-data-text="请先选择区域"
                >
                  <el-option
                    v-for="school in filteredSchools"
                    :key="school.id"
                    :label="school.name"
                    :value="school.id"
                  />
                </el-select>
              </el-form-item>
            </div>
          </transition>
        </div>

        <div
          class="flex items-center justify-between bg-slate-50 p-4 rounded-lg border border-slate-100"
        >
          <span class="text-sm font-medium text-slate-700">账号状态</span>
          <el-switch
            v-model="adminForm.is_active"
            inline-prompt
            active-text="启用"
            inactive-text="停用"
            style="--el-switch-on-color: #10b981; --el-switch-off-color: #f43f5e"
          />
        </div>

        <div v-if="!editingAdmin" class="mt-6">
          <el-form-item label="初始密码">
            <el-input
              v-model="adminForm.password"
              type="password"
              show-password
              placeholder="默认建议使用强密码"
            />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-3 pt-2">
          <el-button @click="showAdminModal = false">取消</el-button>
          <el-button type="primary" @click="saveAdmin" :loading="saving"
            >确认{{ editingAdmin ? '保存' : '创建' }}</el-button
          >
        </div>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入管理员"
      width="600px"
      align-center
      class="rounded-xl"
    >
      <el-steps :active="1" finish-status="success" simple class="mb-6">
        <el-step title="下载模板" />
        <el-step title="上传文件" />
        <el-step title="完成导入" />
      </el-steps>

      <div class="space-y-6">
        <div class="bg-indigo-50 border border-indigo-100 rounded-lg p-4 flex gap-4 items-center">
          <div class="bg-white p-2 rounded-md border border-indigo-100 shrink-0">
            <el-icon :size="24" class="text-indigo-500"><Document /></el-icon>
          </div>
          <div class="flex-1">
            <h4 class="text-sm font-bold text-indigo-900 mb-1">第一步：获取导入模板</h4>
            <p class="text-xs text-indigo-700">
              请下载标准模板，并按照格式要求填写管理员信息。支持批量创建区县和学校管理员。
            </p>
          </div>
          <el-button @click="downloadTemplate" size="small" type="primary" plain
            >下载模板</el-button
          >
        </div>

        <div>
          <h4 class="text-sm font-bold text-slate-800 mb-3">第二步：上传填写好的文件</h4>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
            drag
            class="w-full"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或 <em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip text-slate-400 text-center mt-2">
                仅支持 .xlsx 或 .xls 格式文件，文件大小不超过 5MB
              </div>
            </template>
          </el-upload>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full pt-4 border-t border-slate-100">
          <el-button link type="info" @click="showImportDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="startImport"
            :loading="importing"
            :disabled="!importFile"
          >
            开始导入
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  InfoFilled,
  Search,
  Refresh,
  Upload,
  Plus,
  ArrowDown,
  Document,
} from '@element-plus/icons-vue'
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
    return allSchools.value.filter((s) => s.region_id === filters.value.region_id)
  }
  // 在表单中如果选择了区域，也需要过滤学校
  if (adminForm.value.region_id) {
    return allSchools.value.filter((s) => s.region_id === adminForm.value.region_id)
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
  is_active: true,
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
  if (typeof page === 'number') currentPage.value = page
  loading.value = true
  try {
    // 获取管理员类型的用户
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      search: filters.value.search,
    })
    // 筛选管理员角色 (注意：实际后端应该直接支持 role 筛选，这里如果是全量获取再筛选可能会有问题，假设后端支持)
    // 暂时保持原有逻辑，如果是全量返回再前端筛选
    // 如果后端支持 search 参数查找所有管理员，那么：
    admins.value = response.users.filter((u) =>
      ['admin', 'district_admin', 'school_admin'].includes(u.role)
    )

    // 前端筛选逻辑保留，以防后端没完全支持组合筛选
    if (filters.value.admin_role) {
      admins.value = admins.value.filter((u) => u.role === filters.value.admin_role)
    }
    if (filters.value.region_id) {
      admins.value = admins.value.filter((u) => u.region_id === filters.value.region_id)
    }
    if (filters.value.school_id) {
      admins.value = admins.value.filter((u) => u.school_id === filters.value.school_id)
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

const handleMoreActions = (command: string, row: User) => {
  if (command === 'toggle_status') toggleAdminStatus(row)
  else if (command === 'reset_password') resetPassword(row)
  else if (command === 'delete') deleteAdmin(row)
}

// 工具函数
const getAdminRoleDisplayName = (role: string): string => {
  const roleMap: Record<string, string> = {
    admin: '超级管理员',
    district_admin: '区县管理员',
    school_admin: '学校管理员',
  }
  return roleMap[role] || role
}

const getRoleTagType = (role: string) => {
  const map: Record<string, string> = {
    admin: 'danger',
    district_admin: 'warning',
    school_admin: 'primary',
  }
  return map[role] || 'info'
}

const getAdminScopeDisplay = (admin: User): string => {
  if (admin.role === 'admin') return '全局'
  if (admin.role === 'district_admin') return admin.region_name || '-'
  if (admin.role === 'school_admin') return admin.school_name || '-'
  return '-'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
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
    is_active: admin.is_active,
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
        is_active: adminForm.value.is_active,
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
        is_active: adminForm.value.is_active,
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
      { type: 'warning', confirmButtonText: '确认重置', cancelButtonText: '取消' }
    )
    const result = await adminService.resetUserPassword(admin.id)
    if (result.new_password) {
      ElMessageBox.alert(`新密码：${result.new_password}`, '密码重置成功', {
        type: 'success',
        confirmButtonText: '复制',
        callback: () => {
          navigator.clipboard.writeText(result.new_password!)
        },
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

const deleteAdmin = async (admin: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 ${admin.full_name || admin.username} 吗？此操作不可恢复。`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
      }
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
    is_active: true,
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
    ['admin002', '李管理员', 'admin002@example.com', '学校管理员', '开平市', '开平市第一中学'],
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
    await new Promise((resolve) => setTimeout(resolve, 1000)) // 模拟耗时
    ElMessage.success('导入功能待后端接口对接')
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
  border-color: #e2e8f0;
  background-color: #f8fafc;
}

.el-upload :deep(.el-upload-dragger:hover) {
  border-color: #6366f1;
  background-color: #eff6ff;
}
</style>
