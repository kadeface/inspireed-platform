<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <DashboardHeader
      title="班级教学助手 - 成员管理"
      :subtitle="selectedClassroom ? `班级：${selectedClassroom.name}` : '选择班级开始管理'"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    >
      <template #default>
        <div class="flex items-center gap-3 flex-wrap">
          <button
            @click="showAddModal = true"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-cyan-600 rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            添加成员
          </button>
          <button
            @click="handleBack"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            返回
          </button>
        </div>
      </template>
    </DashboardHeader>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="!selectedClassroom" class="bg-white/80 backdrop-blur-sm border border-dashed border-gray-200 rounded-2xl p-12 text-center text-gray-500 shadow-lg">
        请选择一个班级开始管理
      </div>

      <div v-else class="space-y-6">
        <!-- 成员列表 -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-lg font-bold text-gray-900">班级成员列表</h2>
            <p class="text-sm text-gray-500 mt-1">管理班级教学助手中的成员，包括教师和学生</p>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">姓名/用户名</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学号</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">座号</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">职务</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="loading">
                  <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto mb-2"></div>
                    加载中...
                  </td>
                </tr>
                <tr v-else-if="members.length === 0">
                  <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                    暂无成员，点击"添加成员"按钮开始添加
                  </td>
                </tr>
                <tr v-else v-for="member in members" :key="member.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{{ getUserName(member.userId) }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getRoleBadgeClass(member.roleInClass)">
                      {{ getRoleName(member.roleInClass) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ member.studentNo || '—' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ member.seatNo || '—' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ member.cadreTitle || '—' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      @click="editMember(member)"
                      class="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      编辑
                    </button>
                    <button
                      @click="removeMember(member)"
                      class="text-red-600 hover:text-red-900"
                    >
                      移除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- 添加/编辑成员模态框 -->
    <div
      v-if="showAddModal || showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ showEditModal ? '编辑成员' : '添加成员' }}
          </h2>
          <button
            @click="closeModal"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveMember" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用户ID <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.userId"
              type="number"
              required
              :disabled="showEditModal"
              placeholder="请输入用户ID"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <p class="text-xs text-gray-500 mt-1">提示：可以通过用户管理页面查找用户ID</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              角色 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.roleInClass"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="RoleInClass.HEAD_TEACHER_PRIMARY">正班主任</option>
              <option :value="RoleInClass.HEAD_TEACHER_DEPUTY">副班主任</option>
              <option :value="RoleInClass.SUBJECT_TEACHER">任课教师</option>
              <option :value="RoleInClass.CADRE">班干部</option>
              <option :value="RoleInClass.STUDENT">学生</option>
            </select>
          </div>

          <div v-if="formData.roleInClass === RoleInClass.STUDENT">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              学号
            </label>
            <input
              v-model="formData.studentNo"
              type="text"
              placeholder="请输入学号"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div v-if="formData.roleInClass === RoleInClass.STUDENT">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              座号
            </label>
            <input
              v-model.number="formData.seatNo"
              type="number"
              placeholder="请输入座号"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div v-if="formData.roleInClass === RoleInClass.CADRE">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              职务名称
            </label>
            <input
              v-model="formData.cadreTitle"
              type="text"
              placeholder="请输入职务名称（如：班长、学习委员等）"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="flex items-center">
              <input
                v-model="formData.isPrimaryClass"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">设为主班级/默认进入班级</span>
            </label>
            <div class="mt-2 text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-2">
              💡 <strong>主班级说明：</strong>
              <ul class="list-disc list-inside mt-1 space-y-0.5">
                <li>当一个学生同时属于多个班级时，标记为"主班级"的班级会作为默认班级使用</li>
                <li>系统在查询学生统计信息、显示班级信息时会优先使用主班级的数据</li>
                <li>如果学生只属于一个班级，建议勾选此项</li>
                <li>如果学生属于多个班级，建议将最重要的班级（如主修班）标记为主班级</li>
              </ul>
            </div>
          </div>

          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {{ error }}
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type {
  ClassroomInfo,
  ClassroomMembership,
  ClassroomMembershipCreate,
  ClassroomMembershipUpdate,
  RoleInClass,
} from '@/types/classroomAssistant'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const classroomId = computed(() => Number(route.params.classroomId))

const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const loading = ref(false)
const saving = ref(false)
const members = ref<ClassroomMembership[]>([])
const userMap = ref<Map<number, { username: string; fullName?: string }>>(new Map())
const selectedClassroom = ref<ClassroomInfo | null>(null)

const showAddModal = ref(false)
const showEditModal = ref(false)
const editingMember = ref<ClassroomMembership | null>(null)
const error = ref('')

const formData = ref<ClassroomMembershipCreate & { userId: number }>({
  classroomId: classroomId.value,
  userId: 0,
  roleInClass: RoleInClass.STUDENT,
  studentNo: null,
  seatNo: null,
  cadreTitle: null,
  isPrimaryClass: false,
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleBack = () => {
  router.push('/teacher/class-assistant')
}

const loadClassroom = async () => {
  try {
    const classrooms = await classroomAssistantService.getMyClassrooms()
    selectedClassroom.value = classrooms.find((c) => c.id === classroomId.value) || null
  } catch (error) {
    console.error('加载班级信息失败:', error)
  }
}

const loadMembers = async () => {
  if (!classroomId.value) return
  
  try {
    loading.value = true
    members.value = await classroomAssistantService.getClassroomMembers(classroomId.value)
    
    // 尝试获取用户信息（这里需要用户信息，但暂时使用ID显示）
    // 后续可以添加API来批量获取用户信息
    members.value.forEach((member) => {
      if (!userMap.value.has(member.userId)) {
        userMap.value.set(member.userId, {
          username: `用户${member.userId}`,
          fullName: undefined,
        })
      }
    })
  } catch (error: any) {
    console.error('加载成员列表失败:', error)
    error.value = error.response?.data?.detail || '加载成员列表失败'
  } finally {
    loading.value = false
  }
}

const getUserName = (userId: number): string => {
  const user = userMap.value.get(userId)
  return user?.fullName || user?.username || `用户${userId}`
}

const getRoleName = (role: RoleInClass): string => {
  const roleMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: '正班主任',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: '副班主任',
    [RoleInClass.SUBJECT_TEACHER]: '任课教师',
    [RoleInClass.CADRE]: '班干部',
    [RoleInClass.STUDENT]: '学生',
  }
  return roleMap[role] || role
}

const getRoleBadgeClass = (role: RoleInClass): string => {
  const classMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: 'bg-purple-100 text-purple-800',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: 'bg-indigo-100 text-indigo-800',
    [RoleInClass.SUBJECT_TEACHER]: 'bg-blue-100 text-blue-800',
    [RoleInClass.CADRE]: 'bg-yellow-100 text-yellow-800',
    [RoleInClass.STUDENT]: 'bg-green-100 text-green-800',
  }
  return classMap[role] || 'bg-gray-100 text-gray-800'
}

const resetForm = () => {
  formData.value = {
    classroomId: classroomId.value,
    userId: 0,
    roleInClass: RoleInClass.STUDENT,
    studentNo: null,
    seatNo: null,
    cadreTitle: null,
    isPrimaryClass: false,
  }
  error.value = ''
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingMember.value = null
  resetForm()
}

const editMember = (member: ClassroomMembership) => {
  editingMember.value = member
  formData.value = {
    classroomId: member.classroomId,
    userId: member.userId,
    roleInClass: member.roleInClass,
    studentNo: member.studentNo || null,
    seatNo: member.seatNo || null,
    cadreTitle: member.cadreTitle || null,
    isPrimaryClass: member.isPrimaryClass,
  }
  showEditModal.value = true
}

const saveMember = async () => {
  try {
    saving.value = true
    error.value = ''
    
    if (showEditModal.value && editingMember.value) {
      // 更新成员
      const updateData: ClassroomMembershipUpdate = {
        roleInClass: formData.value.roleInClass,
        studentNo: formData.value.studentNo || null,
        seatNo: formData.value.seatNo || null,
        cadreTitle: formData.value.cadreTitle || null,
        isPrimaryClass: formData.value.isPrimaryClass,
      }
      await classroomAssistantService.updateClassroomMember(
        classroomId.value,
        editingMember.value.userId,
        updateData
      )
    } else {
      // 添加成员
      const createData: ClassroomMembershipCreate = {
        classroomId: classroomId.value,
        userId: formData.value.userId,
        roleInClass: formData.value.roleInClass,
        studentNo: formData.value.studentNo || null,
        seatNo: formData.value.seatNo || null,
        cadreTitle: formData.value.cadreTitle || null,
        isPrimaryClass: formData.value.isPrimaryClass,
      }
      await classroomAssistantService.addClassroomMember(classroomId.value, createData)
    }
    
    closeModal()
    await loadMembers()
  } catch (error: any) {
    console.error('保存成员失败:', error)
    error.value = error.response?.data?.detail || error.message || '保存失败，请重试'
  } finally {
    saving.value = false
  }
}

const removeMember = async (member: ClassroomMembership) => {
  if (!confirm(`确定要移除成员 ${getUserName(member.userId)} 吗？`)) {
    return
  }
  
  try {
    await classroomAssistantService.removeClassroomMember(classroomId.value, member.userId)
    await loadMembers()
  } catch (error: any) {
    console.error('移除成员失败:', error)
    alert(error.response?.data?.detail || error.message || '移除失败，请重试')
  }
}

onMounted(async () => {
  await loadClassroom()
  await loadMembers()
})
</script>
