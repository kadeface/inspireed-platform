<template>
  <div class="user-management p-6">
    <!-- 面包屑导航 -->
    <div class="mb-4">
      <router-link 
        to="/admin" 
        class="text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回管理员首页
      </router-link>
    </div>
    
    <div class="header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">用户管理</h1>
      <p class="text-gray-600 mt-2">管理员专属 - 管理平台用户账号</p>
    </div>

    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button
            @click="openCreateUserModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 创建用户
          </button>
          <button
            @click="openBatchImportModal"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            📥 批量导入
          </button>
          <button
            @click="refreshUsers"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </div>
        <div class="flex gap-2">
          <select v-model="roleFilter" @change="searchUsers" class="px-3 py-2 border rounded-lg">
            <option value="">所有角色</option>
            <option value="admin">管理员</option>
            <option value="researcher">教研员</option>
            <option value="teacher">教师</option>
            <option value="student">学生</option>
          </select>
          <input
            v-model="searchQuery"
            @input="searchUsers"
            type="text"
            placeholder="搜索用户..."
            class="px-3 py-2 border rounded-lg w-64"
          />
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                用户信息
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                角色
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                创建时间
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                最后登录
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ user.username.charAt(0).toUpperCase() }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ user.username }}</div>
                    <div class="text-sm text-gray-500">{{ user.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="getRoleBadgeClass(user.role)"
                >
                  {{ getRoleDisplayName(user.role) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ user.is_active ? '激活' : '未激活' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ user.last_login ? formatDate(user.last_login) : '从未登录' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex gap-2">
                  <button
                    @click="editUser(user)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    编辑
                  </button>
                  <button
                    @click="toggleUserStatus(user)"
                    :class="user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'"
                  >
                    {{ user.is_active ? '禁用' : '启用' }}
                  </button>
                  <button
                    @click="resetPassword(user)"
                    class="text-orange-600 hover:text-orange-900"
                  >
                    重置密码
                  </button>
                  <button
                    @click="deleteUser(user)"
                    class="text-red-600 hover:text-red-900"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页 -->
    <div class="mt-6 flex justify-between items-center">
      <div class="text-sm text-gray-700">
        显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalUsers) }} 条，共 {{ totalUsers }} 条
      </div>
      <div class="flex gap-2">
        <button
          @click="prevPage"
          :disabled="currentPage === 1"
          class="px-3 py-2 border rounded-lg disabled:opacity-50"
        >
          上一页
        </button>
        <span class="px-3 py-2">{{ currentPage }} / {{ totalPages }}</span>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 border rounded-lg disabled:opacity-50"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 创建/编辑用户模态框 -->
    <div v-if="showUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingUser ? '编辑用户' : '创建用户' }}
        </h3>
        <form @submit.prevent="saveUser">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">用户名</label>
              <input
                v-model="userForm.username"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">邮箱</label>
              <input
                v-model="userForm.email"
                type="email"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">角色</label>
              <select v-model="userForm.role" class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="admin">管理员</option>
                <option value="researcher">教研员</option>
                <option value="teacher">教师</option>
                <option value="student">学生</option>
              </select>
            </div>
            <div v-if="!editingUser">
              <label class="block text-sm font-medium text-gray-700">密码</label>
              <input
                v-model="userForm.password"
                type="password"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="userForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm text-gray-700">激活用户</span>
              </label>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="closeUserModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {{ editingUser ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 批量导入模态框 -->
    <BatchImportModal
      :show="showBatchImportModal"
      @close="showBatchImportModal = false"
      @success="onBatchImportSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminService, { type User, type UserCreate, type UserUpdate } from '@/services/admin'
import BatchImportModal from '@/components/Admin/BatchImportModal.vue'

const toast = useToast()

// 响应式数据
const users = ref<User[]>([])
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalUsers = ref(0)

// 模态框状态
const showUserModal = ref(false)
const showBatchImportModal = ref(false)
const editingUser = ref<User | null>(null)
const userForm = ref<UserCreate>({
  username: '',
  email: '',
  role: 'teacher',
  password: '',
  is_active: true
})

// 计算属性
const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize.value))

// 移除客户端过滤，使用服务端分页和搜索

// 方法
function getRoleDisplayName(role: string): string {
  const roleMap = {
    admin: '管理员',
    researcher: '教研员',
    teacher: '教师',
    student: '学生'
  }
  return roleMap[role] || role
}

function getRoleBadgeClass(role: string): string {
  const classMap = {
    admin: 'bg-purple-100 text-purple-800',
    researcher: 'bg-green-100 text-green-800',
    teacher: 'bg-orange-100 text-orange-800',
    student: 'bg-indigo-100 text-indigo-800'
  }
  return classMap[role] || 'bg-gray-100 text-gray-800'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadUsers() {
  loading.value = true
  try {
    const response = await adminService.getUsers({
      page: currentPage.value,
      size: pageSize.value,
      role: roleFilter.value || undefined,
      search: searchQuery.value || undefined
    })
    users.value = response.users
    totalUsers.value = response.total
  } catch (error: any) {
    console.error('Failed to load users:', error)
    toast.error(error.response?.data?.detail || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function searchUsers() {
  currentPage.value = 1
  loadUsers()
}

function refreshUsers() {
  loadUsers()
  toast.success('用户列表已刷新')
}

function openCreateUserModal() {
  editingUser.value = null
  userForm.value = {
    username: '',
    email: '',
    role: 'teacher',
    password: '',
    is_active: true
  }
  showUserModal.value = true
}

function editUser(user: User) {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    email: user.email,
    role: user.role,
    password: '',
    is_active: user.is_active
  }
  showUserModal.value = true
}

function closeUserModal() {
  showUserModal.value = false
  editingUser.value = null
}

async function saveUser() {
  try {
    if (editingUser.value) {
      const updateData: UserUpdate = {
        username: userForm.value.username,
        email: userForm.value.email,
        role: userForm.value.role,
        is_active: userForm.value.is_active
      }
      await adminService.updateUser(editingUser.value.id, updateData)
      toast.success('用户更新成功')
    } else {
      await adminService.createUser(userForm.value)
      toast.success('用户创建成功')
    }
    closeUserModal()
    loadUsers()
  } catch (error: any) {
    console.error('Failed to save user:', error)
    toast.error(error.response?.data?.detail || '保存用户失败')
  }
}

async function toggleUserStatus(user: User) {
  try {
    const result = await adminService.toggleUserStatus(user.id)
    user.is_active = result.is_active
    toast.success(result.message)
  } catch (error: any) {
    console.error('Failed to toggle user status:', error)
    toast.error(error.response?.data?.detail || '操作失败')
  }
}

async function resetPassword(user: User) {
  if (!confirm(`确定要重置用户 ${user.username} 的密码吗？`)) {
    return
  }
  
  try {
    const result = await adminService.resetUserPassword(user.id)
    toast.success(`${result.message}，新密码：${result.new_password}`)
  } catch (error: any) {
    console.error('Failed to reset password:', error)
    toast.error(error.response?.data?.detail || '重置密码失败')
  }
}

async function deleteUser(user: User) {
  if (!confirm(`确定要删除用户 ${user.username} 吗？此操作不可撤销。`)) {
    return
  }
  
  try {
    await adminService.deleteUser(user.id)
    users.value = users.value.filter(u => u.id !== user.id)
    totalUsers.value -= 1
    toast.success('用户删除成功')
  } catch (error: any) {
    console.error('Failed to delete user:', error)
    toast.error(error.response?.data?.detail || '删除用户失败')
  }
}

function openBatchImportModal() {
  showBatchImportModal.value = true
}

function onBatchImportSuccess() {
  loadUsers()
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    loadUsers()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadUsers()
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.stat-card {
  @apply p-4 bg-gray-50 rounded-lg;
}
</style>
