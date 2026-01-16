<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>此页面专门用于管理所有班级的成员（添加教师、学生到班级）。班级信息的创建、编辑和删除请在"学校管理"标签页中的"班级管理"功能中操作。
      </p>
    </div>

    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button
            @click="loadAllClassrooms"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </div>
        <div class="flex gap-2">
          <select
            v-model="allClassroomRegionFilter"
            @change="handleRegionFilterChange"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有县区</option>
            <option v-for="region in allRegions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
          <select
            v-model="allClassroomSchoolFilter"
            @change="loadAllClassrooms"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有学校</option>
            <option v-for="school in filteredSchoolsForClassroom" :key="school.id" :value="school.id">
              {{ school.name }}
            </option>
          </select>
          <select
            v-model="allClassroomGradeFilter"
            @change="handleGradeFilterChange"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有年级</option>
            <option v-for="grade in grades" :key="grade.id" :value="grade.id">
              {{ grade.name }}
            </option>
          </select>
          <input
            v-model="allClassroomSearchQuery"
            @keyup.enter="loadAllClassrooms"
            type="text"
            placeholder="搜索学校或班级名称..."
            class="px-3 py-2 border rounded-lg w-64"
          />
        </div>
      </div>
    </div>

    <!-- 班级列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="allClassroomsLoading" class="p-6 text-center text-gray-500">
        加载中...
      </div>
      <div v-else-if="allClassrooms.length === 0" class="p-6 text-center text-gray-500">
        暂无班级
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">班级名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">年级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="classroom in allClassrooms" :key="classroom.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ classroom.name }}</div>
              <div class="text-xs text-gray-500">编码：{{ classroom.code || '—' }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ getSchoolNameById(classroom.school_id) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ getGradeName(classroom.grade_id) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="classroom.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
              >
                {{ classroom.is_active ? '激活' : '未激活' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="openMemberManager(classroom)"
                class="text-indigo-600 hover:text-indigo-900 font-medium"
              >
                成员管理
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 成员管理对话框 -->
    <el-dialog
      v-model="showMemberManager"
      :title="`${selectedClassroom?.name || ''} - 成员管理`"
      width="1200px"
      :close-on-click-modal="false"
    >
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex gap-2">
            <el-button type="primary" @click="openAddMemberModal">+ 添加成员</el-button>
          </div>
          <el-button @click="loadMembers">🔄 刷新</el-button>
        </div>
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-2 text-sm text-blue-800">
          💡 <strong>提示：</strong>添加学生成员时，建议填写<strong>学号</strong>和<strong>座号</strong>，便于后续的考勤管理和座位管理。
        </div>

        <div v-if="membersLoading" class="text-center text-gray-500 py-8">
          加载中...
        </div>
        <div v-else-if="members.length === 0" class="text-center text-gray-500 py-12 border-2 border-dashed rounded-lg">
          暂无成员，请点击"添加成员"按钮添加
        </div>
        <el-table v-else :data="members" border>
          <el-table-column prop="userFullName" label="姓名" width="120">
            <template #default="{ row }">
              <div>{{ row.userFullName || row.userName || '未设置' }}</div>
              <div class="text-xs text-gray-500">ID: {{ row.userId }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="userUsername" label="用户名/邮箱" width="200">
            <template #default="{ row }">
              <div>{{ row.userUsername || '—' }}</div>
              <div class="text-xs text-gray-400">{{ row.userEmail || '' }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="roleInClass" label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="getRoleTagType(row.roleInClass)" size="small">
                {{ getRoleName(row.roleInClass) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="studentNo" label="学号" width="100" />
          <el-table-column prop="seatNo" label="座号" width="80" />
          <el-table-column prop="cadreTitle" label="职务" width="120" />
          <el-table-column prop="isActive" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.isActive ? 'success' : 'danger'" size="small">
                {{ row.isActive ? '活跃' : '非活跃' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="editMember(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="removeMember(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加/编辑成员对话框 -->
    <el-dialog
      v-model="showMemberModal"
      :title="editingMember ? '编辑成员' : '添加成员'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="memberForm" label-width="120px" v-if="!batchAddMode">
        <el-form-item label="选择用户" required v-if="!editingMember">
          <div class="space-y-2">
            <div class="flex gap-2">
              <el-input
                v-model="userSearchQuery"
                @input="searchUsersForMember"
                placeholder="搜索用户名、姓名或邮箱..."
                clearable
              />
              <el-select v-model="userRoleFilter" @change="onUserRoleFilterChange" placeholder="角色" style="width: 120px">
                <el-option label="所有角色" value="" />
                <el-option label="教师" value="teacher" />
                <el-option label="学生" value="student" />
              </el-select>
            </div>
            <div v-if="userSearchLoading" class="text-center text-gray-500 py-2 text-sm">搜索中...</div>
            <div v-else-if="searchedUsers.length > 0" class="max-h-48 overflow-y-auto border rounded-lg">
              <div
                v-for="user in searchedUsers"
                :key="user.id"
                @click="selectUserForMember(user)"
                class="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
                :class="{ 'bg-blue-100': memberForm.userId === user.id }"
              >
                <div class="font-medium">{{ user.full_name || user.username }}</div>
                <div class="text-xs text-gray-500">ID: {{ user.id }} | {{ user.username }} | {{ user.email }}</div>
              </div>
            </div>
            <div v-if="selectedUserInfo" class="p-2 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="text-sm font-medium text-blue-900">已选择：{{ selectedUserInfo.full_name || selectedUserInfo.username }}</div>
              <div class="text-xs text-blue-700">ID: {{ selectedUserInfo.id }} | {{ selectedUserInfo.email }}</div>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="用户ID" required>
          <el-input-number
            v-model="memberForm.userId"
            :disabled="!!editingMember"
            @input="onUserIdInput"
            placeholder="请输入用户ID"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="memberForm.roleInClass" placeholder="请选择角色" style="width: 100%">
            <el-option :label="'正班主任'" :value="RoleInClass.HEAD_TEACHER_PRIMARY" />
            <el-option :label="'副班主任'" :value="RoleInClass.HEAD_TEACHER_DEPUTY" />
            <el-option :label="'任课教师'" :value="RoleInClass.SUBJECT_TEACHER" />
            <el-option :label="'班干部'" :value="RoleInClass.CADRE" />
            <el-option :label="'学生'" :value="RoleInClass.STUDENT" />
          </el-select>
        </el-form-item>
        <el-form-item label="学号" v-if="memberForm.roleInClass === RoleInClass.STUDENT">
          <el-input v-model="memberForm.studentNo" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="座号" v-if="memberForm.roleInClass === RoleInClass.STUDENT">
          <el-input-number v-model="memberForm.seatNo" placeholder="请输入座号" style="width: 100%" />
        </el-form-item>
        <el-form-item label="职务" v-if="memberForm.roleInClass === RoleInClass.CADRE">
          <el-input v-model="memberForm.cadreTitle" placeholder="请输入职务" />
        </el-form-item>
        <el-form-item label="是否主班级">
          <el-switch v-model="memberForm.isPrimaryClass" />
        </el-form-item>
        <div v-if="memberError" class="text-red-600 text-sm mb-4">{{ memberError }}</div>
      </el-form>

      <!-- 批量添加模式 -->
      <div v-else class="space-y-4">
        <el-form-item label="选择来源班级" required>
          <el-select
            v-model="sourceClassroomFilter"
            @change="loadSourceClassroomStudents"
            placeholder="请选择班级"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="classroom in allClassrooms"
              :key="classroom.id"
              :label="`${classroom.name} (${classroom.code || `ID: ${classroom.id}`})`"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <div v-if="sourceStudentsLoading" class="text-center text-gray-500 py-4">加载中...</div>
        <div v-else-if="sourceClassroomFilter && sourceClassroomStudents.length > 0" class="border rounded-lg">
          <div class="bg-gray-50 px-4 py-2 border-b flex items-center justify-between">
            <span class="text-sm font-medium">学生列表（{{ sourceClassroomStudents.length }} 人）</span>
            <el-button size="small" @click="toggleSelectAllStudents">
              {{ selectedStudentIds.size === sourceClassroomStudents.length ? '取消全选' : '全选' }}
            </el-button>
          </div>
          <div class="max-h-64 overflow-y-auto">
            <div
              v-for="student in sourceClassroomStudents"
              :key="student.userId"
              @click="toggleStudentSelection(student.userId)"
              class="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0 flex items-center gap-3"
              :class="{ 'bg-blue-50': selectedStudentIds.has(student.userId) }"
            >
              <el-checkbox
                :model-value="selectedStudentIds.has(student.userId)"
                @click.stop="toggleStudentSelection(student.userId)"
              />
              <div class="flex-1">
                <div class="font-medium">{{ student.userFullName || student.userName || '未设置' }}</div>
                <div class="text-xs text-gray-500">
                  ID: {{ student.userId }} | {{ student.userUsername || '' }}
                  <span v-if="student.studentNo" class="ml-2 text-blue-600">学号: {{ student.studentNo }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="selectedStudentIds.size > 0" class="bg-blue-50 px-4 py-2 border-t">
            <span class="text-sm text-blue-700 font-medium">已选择 {{ selectedStudentIds.size }} 个学生</span>
          </div>
        </div>
        <div v-else-if="sourceClassroomFilter && !sourceStudentsLoading" class="text-center text-gray-500 py-4 border rounded-lg">
          该班级暂无学生
        </div>
        <div v-if="memberError" class="text-red-600 text-sm">{{ memberError }}</div>
      </div>

      <template #footer>
        <el-button @click="closeMemberModal">取消</el-button>
        <el-button
          v-if="!batchAddMode"
          type="primary"
          @click="saveMember"
          :loading="memberSaving"
        >
          保存
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="batchAddMembers"
          :loading="memberSaving"
          :disabled="selectedStudentIds.size === 0"
        >
          批量添加 ({{ selectedStudentIds.size }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useToast } from '@/composables/useToast'
import adminService, { type Region, type School, type Classroom, type User } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type { Grade } from '@/types/curriculum'
import type {
  ClassroomMembership,
  ClassroomMembershipCreate,
  ClassroomMembershipUpdate,
} from '@/types/classroomAssistant'
import { RoleInClass } from '@/types/classroomAssistant'

const toast = useToast()

// 状态管理
const allClassrooms = ref<Classroom[]>([])
const allClassroomsLoading = ref(false)
const allClassroomSearchQuery = ref('')
const allClassroomRegionFilter = ref<number | ''>('')
const allClassroomSchoolFilter = ref<number | ''>('')
const allClassroomGradeFilter = ref<number | ''>('')
const allRegions = ref<Region[]>([])
const schools = ref<School[]>([])
const grades = ref<Grade[]>([])

// 成员管理状态
const showMemberManager = ref(false)
const selectedClassroom = ref<Classroom | null>(null)
const members = ref<ClassroomMembership[]>([])
const membersLoading = ref(false)
const showMemberModal = ref(false)
const editingMember = ref<ClassroomMembership | null>(null)
const memberSaving = ref(false)
const memberError = ref('')
const memberForm = ref<ClassroomMembershipCreate & { userId: number }>({
  classroomId: 0,
  userId: 0,
  roleInClass: RoleInClass.STUDENT,
  studentNo: null,
  seatNo: null,
  cadreTitle: null,
  isPrimaryClass: false,
})

// 用户搜索状态
const userSearchQuery = ref('')
const userRoleFilter = ref<string>('')
const searchedUsers = ref<User[]>([])
const userSearchLoading = ref(false)
const selectedUserInfo = ref<User | null>(null)

// 批量添加成员状态
const batchAddMode = ref(false)
const sourceClassroomFilter = ref<number | ''>('')
const sourceClassroomStudents = ref<ClassroomMembership[]>([])
const sourceStudentsLoading = ref(false)
const selectedStudentIds = ref<Set<number>>(new Set())

// 计算属性
const filteredSchoolsForClassroom = computed(() => {
  let filtered = schools.value
  if (allClassroomRegionFilter.value) {
    filtered = filtered.filter(school => school.region_id === Number(allClassroomRegionFilter.value))
  }
  if (allClassroomGradeFilter.value) {
    const schoolIdsInGrade = new Set(
      allClassrooms.value
        .filter(c => c.grade_id === Number(allClassroomGradeFilter.value))
        .map(c => c.school_id)
    )
    filtered = filtered.filter(school => schoolIdsInGrade.has(school.id))
  }
  return filtered
})

// 方法
async function loadAllRegions() {
  try {
    const response = await adminService.getRegions({ size: 1000 })
    allRegions.value = response.regions
  } catch (error: any) {
    console.error('Failed to load all regions:', error)
  }
}

async function loadGradesList() {
  try {
    grades.value = await curriculumService.getGrades(true)
  } catch (error: any) {
    console.error('Failed to load grades:', error)
  }
}

function getGradeName(gradeId?: number | null): string {
  if (!gradeId) return '—'
  const grade = grades.value.find(g => g.id === gradeId)
  return grade ? grade.name : `年级 #${gradeId}`
}

function getSchoolNameById(schoolId: number): string {
  const school = schools.value.find((s) => s.id === schoolId)
  return school?.name || `学校${schoolId}`
}

function handleRegionFilterChange() {
  allClassroomSchoolFilter.value = ''
  loadAllClassrooms()
}

function handleGradeFilterChange() {
  allClassroomSchoolFilter.value = ''
  loadAllClassrooms()
}

async function loadAllClassrooms() {
  try {
    allClassroomsLoading.value = true
    if (allRegions.value.length === 0) {
      await loadAllRegions()
    }
    if (schools.value.length === 0) {
      const allSchoolsResponse = await adminService.getSchools({ page: 1, size: 1000 })
      schools.value = allSchoolsResponse.schools
    }
    if (grades.value.length === 0) {
      await loadGradesList()
    }
    const response = await adminService.getClassrooms({
      page: 1,
      size: 100,
      region_id: allClassroomRegionFilter.value ? Number(allClassroomRegionFilter.value) : undefined,
      school_id: allClassroomSchoolFilter.value ? Number(allClassroomSchoolFilter.value) : undefined,
      grade_id: allClassroomGradeFilter.value ? Number(allClassroomGradeFilter.value) : undefined,
      search: allClassroomSearchQuery.value || undefined,
    })
    allClassrooms.value = response.classrooms
    const schoolIds = [...new Set(response.classrooms.map(c => c.school_id))]
    const missingSchoolIds = schoolIds.filter(id => !schools.value.find(s => s.id === id))
    if (missingSchoolIds.length > 0) {
      const allSchoolsResponse = await adminService.getSchools({ page: 1, size: 1000 })
      schools.value = allSchoolsResponse.schools
    }
  } catch (error: any) {
    console.error('Failed to load all classrooms:', error)
    toast.error(error.response?.data?.detail || '加载班级列表失败')
  } finally {
    allClassroomsLoading.value = false
  }
}

async function openMemberManager(classroom: Classroom) {
  selectedClassroom.value = classroom
  showMemberManager.value = true
  await loadMembers()
}

function closeMemberManager() {
  showMemberManager.value = false
  selectedClassroom.value = null
  members.value = []
}

async function loadMembers() {
  if (!selectedClassroom.value) return
  
  try {
    membersLoading.value = true
    members.value = await classroomAssistantService.getClassroomMembers(selectedClassroom.value.id)
  } catch (error: any) {
    console.error('加载成员列表失败:', error)
    toast.error(error.response?.data?.detail || '加载成员列表失败')
  } finally {
    membersLoading.value = false
  }
}

function getRoleName(role: RoleInClass): string {
  const roleMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: '正班主任',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: '副班主任',
    [RoleInClass.SUBJECT_TEACHER]: '任课教师',
    [RoleInClass.CADRE]: '班干部',
    [RoleInClass.STUDENT]: '学生',
  }
  return roleMap[role] || role
}

function getRoleTagType(role: RoleInClass): string {
  const typeMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: 'danger',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: 'warning',
    [RoleInClass.SUBJECT_TEACHER]: 'primary',
    [RoleInClass.CADRE]: 'success',
    [RoleInClass.STUDENT]: 'info',
  }
  return typeMap[role] || ''
}

function openAddMemberModal() {
  if (!selectedClassroom.value) return
  editingMember.value = null
  memberError.value = ''
  userSearchQuery.value = ''
  userRoleFilter.value = ''
  searchedUsers.value = []
  selectedUserInfo.value = null
  batchAddMode.value = false
  sourceClassroomFilter.value = ''
  sourceClassroomStudents.value = []
  selectedStudentIds.value = new Set()
  memberForm.value = {
    classroomId: selectedClassroom.value.id,
    userId: 0,
    roleInClass: RoleInClass.STUDENT,
    studentNo: null,
    seatNo: null,
    cadreTitle: null,
    isPrimaryClass: false,
  }
  showMemberModal.value = true
}

async function searchUsersForMember() {
  if (!userSearchQuery.value && !userRoleFilter.value) {
    searchedUsers.value = []
    return
  }
  
  try {
    userSearchLoading.value = true
    const response = await adminService.getUsers({
      page: 1,
      size: 20,
      role: userRoleFilter.value || undefined,
      search: userSearchQuery.value || undefined,
    })
    searchedUsers.value = response.users
  } catch (error: any) {
    console.error('搜索用户失败:', error)
    toast.error(error.response?.data?.detail || '搜索用户失败')
  } finally {
    userSearchLoading.value = false
  }
}

function onUserRoleFilterChange() {
  if (userRoleFilter.value === 'student') {
    memberForm.value.roleInClass = RoleInClass.STUDENT
  } else if (userRoleFilter.value === 'teacher') {
    memberForm.value.roleInClass = RoleInClass.SUBJECT_TEACHER
  }
  searchUsersForMember()
}

function selectUserForMember(user: User) {
  memberForm.value.userId = user.id
  selectedUserInfo.value = user
  autoSetRoleFromUser(user)
}

function autoSetRoleFromUser(user: User) {
  if (user.role === 'student') {
    memberForm.value.roleInClass = RoleInClass.STUDENT
  } else if (user.role === 'teacher' || user.role === 'admin' || user.role === 'researcher') {
    memberForm.value.roleInClass = RoleInClass.SUBJECT_TEACHER
  }
}

async function onUserIdInput() {
  const userId = memberForm.value.userId
  
  if (selectedUserInfo.value && selectedUserInfo.value.id !== userId) {
    selectedUserInfo.value = null
  }
  
  if (userId && userId > 0 && !selectedUserInfo.value) {
    try {
      const user = await adminService.getUser(userId)
      selectedUserInfo.value = user
      autoSetRoleFromUser(user)
    } catch (error: any) {
      console.debug('获取用户信息失败:', error)
    }
  }
}

function editMember(member: ClassroomMembership) {
  editingMember.value = member
  memberError.value = ''
  memberForm.value = {
    classroomId: member.classroomId,
    userId: member.userId,
    roleInClass: member.roleInClass,
    studentNo: member.studentNo || null,
    seatNo: member.seatNo || null,
    cadreTitle: member.cadreTitle || null,
    isPrimaryClass: member.isPrimaryClass,
  }
  batchAddMode.value = false
  showMemberModal.value = true
}

function closeMemberModal() {
  showMemberModal.value = false
  editingMember.value = null
  memberError.value = ''
  userSearchQuery.value = ''
  userRoleFilter.value = ''
  searchedUsers.value = []
  selectedUserInfo.value = null
  batchAddMode.value = false
  sourceClassroomFilter.value = ''
  sourceClassroomStudents.value = []
  selectedStudentIds.value = new Set()
}

async function saveMember() {
  if (!selectedClassroom.value) return
  
  try {
    memberSaving.value = true
    memberError.value = ''
    
    if (editingMember.value) {
      const updateData: ClassroomMembershipUpdate = {
        roleInClass: memberForm.value.roleInClass,
        studentNo: memberForm.value.studentNo || null,
        seatNo: memberForm.value.seatNo || null,
        cadreTitle: memberForm.value.cadreTitle || null,
        isPrimaryClass: memberForm.value.isPrimaryClass,
      }
      await classroomAssistantService.updateClassroomMember(
        selectedClassroom.value.id,
        editingMember.value.userId,
        updateData
      )
      ElMessage.success('成员信息更新成功')
    } else {
      const createData: ClassroomMembershipCreate = {
        classroomId: selectedClassroom.value.id,
        userId: memberForm.value.userId,
        roleInClass: memberForm.value.roleInClass,
        studentNo: memberForm.value.studentNo || null,
        seatNo: memberForm.value.seatNo || null,
        cadreTitle: memberForm.value.cadreTitle || null,
        isPrimaryClass: memberForm.value.isPrimaryClass,
      }
      await classroomAssistantService.addClassroomMember(selectedClassroom.value.id, createData)
      ElMessage.success('成员添加成功')
    }
    
    closeMemberModal()
    await loadMembers()
  } catch (error: any) {
    console.error('保存成员失败:', error)
    memberError.value = error.response?.data?.detail || error.message || '保存失败，请重试'
  } finally {
    memberSaving.value = false
  }
}

async function loadSourceClassroomStudents() {
  if (!sourceClassroomFilter.value) {
    sourceClassroomStudents.value = []
    selectedStudentIds.value = new Set()
    return
  }
  
  try {
    sourceStudentsLoading.value = true
    const sourceMembers = await classroomAssistantService.getClassroomMembers(Number(sourceClassroomFilter.value))
    let students = sourceMembers.filter(m => m.roleInClass === RoleInClass.STUDENT)
    
    if (selectedClassroom.value) {
      try {
        const currentMembers = await classroomAssistantService.getClassroomMembers(selectedClassroom.value.id)
        const currentMemberUserIds = new Set(currentMembers.filter(m => m.isActive).map(m => m.userId))
        students = students.filter(s => !currentMemberUserIds.has(s.userId))
      } catch (error) {
        console.warn('获取当前班级成员失败:', error)
      }
    }
    
    sourceClassroomStudents.value = students
    selectedStudentIds.value = new Set()
  } catch (error: any) {
    console.error('加载班级学生失败:', error)
    toast.error(error.response?.data?.detail || '加载班级学生失败')
    sourceClassroomStudents.value = []
  } finally {
    sourceStudentsLoading.value = false
  }
}

function toggleStudentSelection(userId: number) {
  if (selectedStudentIds.value.has(userId)) {
    selectedStudentIds.value.delete(userId)
  } else {
    selectedStudentIds.value.add(userId)
  }
}

function toggleSelectAllStudents() {
  if (selectedStudentIds.value.size === sourceClassroomStudents.value.length) {
    selectedStudentIds.value = new Set()
  } else {
    selectedStudentIds.value = new Set(sourceClassroomStudents.value.map(s => s.userId))
  }
}

async function batchAddMembers() {
  if (!selectedClassroom.value || selectedStudentIds.value.size === 0) return
  
  try {
    memberSaving.value = true
    memberError.value = ''
    
    const errors: string[] = []
    let successCount = 0
    
    for (const userId of selectedStudentIds.value) {
      try {
        const student = sourceClassroomStudents.value.find(s => s.userId === userId)
        if (!student) continue
        
        const createData: ClassroomMembershipCreate = {
          classroomId: selectedClassroom.value.id,
          userId: userId,
          roleInClass: RoleInClass.STUDENT,
          studentNo: student.studentNo || null,
          seatNo: student.seatNo || null,
          cadreTitle: null,
          isPrimaryClass: false,
        }
        
        await classroomAssistantService.addClassroomMember(selectedClassroom.value.id, createData)
        successCount++
      } catch (error: any) {
        const studentName = sourceClassroomStudents.value.find(s => s.userId === userId)?.userFullName || `ID: ${userId}`
        const errorMsg = error.response?.data?.detail || '添加失败'
        errors.push(`${studentName}: ${errorMsg}`)
        console.error(`添加成员失败 (userId: ${userId}):`, error)
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功添加 ${successCount} 个成员${errors.length > 0 ? `，${errors.length} 个失败` : ''}`)
    }
    
    if (errors.length > 0 && successCount === 0) {
      memberError.value = errors.join('\n')
      ElMessage.error('批量添加失败')
    }
    
    if (successCount > 0) {
      closeMemberModal()
      await loadMembers()
    }
  } catch (error: any) {
    console.error('批量添加成员失败:', error)
    memberError.value = error.response?.data?.detail || '批量添加失败'
    ElMessage.error(error.response?.data?.detail || '批量添加失败')
  } finally {
    memberSaving.value = false
  }
}

async function removeMember(member: ClassroomMembership) {
  if (!selectedClassroom.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要移除用户 ${member.userFullName || member.userName || `ID: ${member.userId}`} 吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await classroomAssistantService.removeClassroomMember(selectedClassroom.value.id, member.userId)
    ElMessage.success('成员移除成功')
    await loadMembers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('移除成员失败:', error)
      ElMessage.error(error.response?.data?.detail || error.message || '移除失败，请重试')
    }
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadAllRegions(),
    loadGradesList(),
    loadAllClassrooms(),
  ])
})
</script>

<style scoped>
.space-y-6 > * + * {
  margin-top: 1.5rem;
}
</style>
