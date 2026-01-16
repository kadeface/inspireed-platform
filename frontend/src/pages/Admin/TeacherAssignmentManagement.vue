<template>
  <div class="teacher-assignment-management p-6">
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
      <h1 class="text-3xl font-bold text-gray-900">教师教学任务管理</h1>
      <p class="text-gray-600 mt-2">管理教师与学校、年级、班级、学科的关联关系</p>
    </div>

    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button
            @click="openCreateDialog"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + 创建教学任务
          </button>
          <button
            @click="loadAssignments"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
        </div>
        <div class="flex gap-2">
          <select
            v-model="filters.teacher_id"
            @change="loadAssignments"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有教师</option>
            <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
              {{ teacher.full_name || teacher.username }}
            </option>
          </select>
          <select
            v-model="filters.school_id"
            @change="loadAssignments"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有学校</option>
            <option v-for="school in schools" :key="school.id" :value="school.id">
              {{ school.name }}
            </option>
          </select>
          <select
            v-model="filters.grade_id"
            @change="loadAssignments"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有年级</option>
            <option v-for="grade in grades" :key="grade.id" :value="grade.id">
              {{ grade.name }}
            </option>
          </select>
          <select
            v-model="filters.subject_id"
            @change="loadAssignments"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有学科</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
          <select
            v-model="filters.semester_id"
            @change="loadAssignments"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">所有学期</option>
            <option v-for="semester in semesters" :key="semester.id" :value="semester.id">
              {{ semester.name }}
            </option>
          </select>
          <select
            v-model="filters.is_active"
            @change="loadAssignments"
            class="px-3 py-2 border rounded-lg"
          >
            <option :value="undefined">全部状态</option>
            <option :value="true">激活</option>
            <option :value="false">停用</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 任务列表表格 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              教师
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              学校
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              年级
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              班级
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              学科
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              学期
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              学年
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              任务类型
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              状态
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td colspan="10" class="px-6 py-4 text-center text-gray-500">
              加载中...
            </td>
          </tr>
          <tr v-else-if="assignments.length === 0">
            <td colspan="10" class="px-6 py-4 text-center text-gray-500">
              暂无数据
            </td>
          </tr>
          <tr v-else v-for="assignment in assignments" :key="assignment.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.teacher?.full_name || assignment.teacher?.username || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.school?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.grade?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.classroom?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.subject?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.semester?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ assignment.academic_year }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  assignment.assignment_type === 'head_teacher'
                    ? 'bg-purple-100 text-purple-800'
                    : 'bg-blue-100 text-blue-800'
                ]"
              >
                {{ getAssignmentTypeName(assignment.assignment_type) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  assignment.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                ]"
              >
                {{ assignment.is_active ? '激活' : '停用' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="editAssignment(assignment)"
                class="text-blue-600 hover:text-blue-900 mr-3"
              >
                编辑
              </button>
              <button
                @click="deleteAssignment(assignment)"
                class="text-red-600 hover:text-red-900"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex justify-between items-center">
      <div class="text-sm text-gray-700">
        共 {{ total }} 条记录，第 {{ page }} / {{ totalPages }} 页
      </div>
      <div class="flex gap-2">
        <button
          @click="page = 1; loadAssignments()"
          :disabled="page === 1"
          class="px-3 py-1 border rounded disabled:opacity-50"
        >
          首页
        </button>
        <button
          @click="page--; loadAssignments()"
          :disabled="page === 1"
          class="px-3 py-1 border rounded disabled:opacity-50"
        >
          上一页
        </button>
        <button
          @click="page++; loadAssignments()"
          :disabled="page >= totalPages"
          class="px-3 py-1 border rounded disabled:opacity-50"
        >
          下一页
        </button>
        <button
          @click="page = totalPages; loadAssignments()"
          :disabled="page >= totalPages"
          class="px-3 py-1 border rounded disabled:opacity-50"
        >
          末页
        </button>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingAssignment ? '编辑教学任务' : '创建教学任务'"
      width="600px"
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item label="教师" required>
          <el-select
            v-model="formData.teacher_id"
            placeholder="请选择教师"
            filterable
            class="w-full"
          >
            <el-option
              v-for="teacher in teachers"
              :key="teacher.id"
              :label="teacher.full_name || teacher.username"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学校" required>
          <el-select
            v-model="formData.school_id"
            placeholder="请选择学校"
            filterable
            class="w-full"
            @change="handleSchoolChange"
          >
            <el-option
              v-for="school in schools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年级" required>
          <el-select
            v-model="formData.grade_id"
            placeholder="请选择年级"
            class="w-full"
            @change="handleGradeChange"
          >
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" required>
          <el-select
            v-model="formData.classroom_id"
            placeholder="请选择班级"
            filterable
            class="w-full"
            :disabled="!formData.school_id || !formData.grade_id"
          >
            <el-option
              v-for="classroom in filteredClassrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学科" required>
          <el-select
            v-model="formData.subject_id"
            placeholder="请选择学科"
            class="w-full"
          >
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学期" required>
          <el-select
            v-model="formData.semester_id"
            placeholder="请选择学期"
            class="w-full"
          >
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学年" required>
          <el-input
            v-model="formData.academic_year"
            placeholder="如：2023-2024"
            maxlength="20"
          />
        </el-form-item>
        <el-form-item label="任务类型" required>
          <el-select
            v-model="formData.assignment_type"
            placeholder="请选择任务类型"
            class="w-full"
          >
            <el-option
              label="班主任"
              value="head_teacher"
            />
            <el-option
              label="学科教师"
              value="subject_teacher"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="formData.is_active"
            active-text="激活"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="saveAssignment" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useToast } from '@/composables/useToast'
import teacherApi from '@/services/teacher'
import adminService from '@/services/admin'
import curriculumService from '@/services/curriculum'
import { semesterApi } from '@/services/evaluation'
import type {
  TeacherTeachingAssignment,
  TeacherTeachingAssignmentCreate,
  TeacherTeachingAssignmentUpdate,
} from '@/types/teacher'
import type { User } from '@/services/admin'
import type { School, Classroom } from '@/services/admin'
import type { Grade, Subject } from '@/types/curriculum'
import type { Semester } from '@/types/evaluation'

const toast = useToast()

// 数据状态
const assignments = ref<TeacherTeachingAssignment[]>([])
const teachers = ref<User[]>([])
const schools = ref<School[]>([])
const grades = ref<Grade[]>([])
const subjects = ref<Subject[]>([])
const semesters = ref<Semester[]>([])
const classrooms = ref<Classroom[]>([])

// 分页状态
const page = ref(1)
const size = ref(10)
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / size.value))

// 筛选状态
const filters = ref({
  teacher_id: undefined as number | undefined,
  school_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
  classroom_id: undefined as number | undefined,
  subject_id: undefined as number | undefined,
  semester_id: undefined as number | undefined,
  is_active: undefined as boolean | undefined,
})

// 对话框状态
const showDialog = ref(false)
const editingAssignment = ref<TeacherTeachingAssignment | null>(null)
const saving = ref(false)
const loading = ref(false)

// 表单数据
const formData = ref<TeacherTeachingAssignmentCreate>({
  teacher_id: 0,
  school_id: 0,
  grade_id: 0,
  classroom_id: 0,
  subject_id: 0,
  semester_id: 0,
  academic_year: '',
  assignment_type: 'subject_teacher',
  is_active: true,
})

// 计算属性：过滤后的班级列表
const filteredClassrooms = computed(() => {
  if (!formData.value.school_id || !formData.value.grade_id) {
    return []
  }
  return classrooms.value.filter(
    (c) => c.school_id === formData.value.school_id && c.grade_id === formData.value.grade_id
  )
})

// 方法
function getAssignmentTypeName(type: string): string {
  return type === 'head_teacher' ? '班主任' : '学科教师'
}

async function loadAssignments() {
  loading.value = true
  try {
    const response = await teacherApi.getAssignments({
      ...filters.value,
      page: page.value,
      size: size.value,
    })
    assignments.value = response.assignments
    total.value = response.total
  } catch (error: any) {
    console.error('Failed to load assignments:', error)
    ElMessage.error(error.response?.data?.detail || '加载教学任务列表失败')
  } finally {
    loading.value = false
  }
}

async function loadTeachers() {
  try {
    const response = await adminService.getUsers({ role: 'teacher', size: 1000 })
    teachers.value = response.users
  } catch (error: any) {
    console.error('Failed to load teachers:', error)
  }
}

async function loadSchools() {
  try {
    const response = await adminService.getSchools({ size: 1000 })
    schools.value = response.schools
  } catch (error: any) {
    console.error('Failed to load schools:', error)
  }
}

async function loadGrades() {
  try {
    grades.value = await curriculumService.getGrades(true)
  } catch (error: any) {
    console.error('Failed to load grades:', error)
  }
}

async function loadSubjects() {
  try {
    subjects.value = await curriculumService.getSubjects(true)
  } catch (error: any) {
    console.error('Failed to load subjects:', error)
  }
}

async function loadSemesters() {
  try {
    semesters.value = await semesterApi.list({ size: 1000 })
  } catch (error: any) {
    console.error('Failed to load semesters:', error)
  }
}

async function loadClassrooms() {
  try {
    const response = await adminService.getClassrooms({ size: 1000 })
    classrooms.value = response.classrooms
  } catch (error: any) {
    console.error('Failed to load classrooms:', error)
  }
}

function openCreateDialog() {
  editingAssignment.value = null
  formData.value = {
    teacher_id: 0,
    school_id: 0,
    grade_id: 0,
    classroom_id: 0,
    subject_id: 0,
    semester_id: 0,
    academic_year: '',
    assignment_type: 'subject_teacher',
    is_active: true,
  }
  showDialog.value = true
}

function editAssignment(assignment: TeacherTeachingAssignment) {
  editingAssignment.value = assignment
  formData.value = {
    teacher_id: assignment.teacher_id,
    school_id: assignment.school_id,
    grade_id: assignment.grade_id,
    classroom_id: assignment.classroom_id,
    subject_id: assignment.subject_id,
    semester_id: assignment.semester_id,
    academic_year: assignment.academic_year,
    assignment_type: assignment.assignment_type,
    is_active: assignment.is_active,
  }
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
  editingAssignment.value = null
}

function handleSchoolChange() {
  formData.value.grade_id = 0
  formData.value.classroom_id = 0
}

function handleGradeChange() {
  formData.value.classroom_id = 0
}

async function saveAssignment() {
  if (!formData.value.teacher_id || !formData.value.school_id || !formData.value.grade_id ||
      !formData.value.classroom_id || !formData.value.subject_id || !formData.value.semester_id ||
      !formData.value.academic_year || !formData.value.assignment_type) {
    ElMessage.warning('请填写所有必填字段')
    return
  }

  saving.value = true
  try {
    if (editingAssignment.value) {
      // 更新
      const updateData: TeacherTeachingAssignmentUpdate = {
        teacher_id: formData.value.teacher_id,
        school_id: formData.value.school_id,
        grade_id: formData.value.grade_id,
        classroom_id: formData.value.classroom_id,
        subject_id: formData.value.subject_id,
        semester_id: formData.value.semester_id,
        academic_year: formData.value.academic_year,
        assignment_type: formData.value.assignment_type,
        is_active: formData.value.is_active,
      }
      await teacherApi.updateAssignment(editingAssignment.value.id, updateData)
      ElMessage.success('教学任务更新成功')
    } else {
      // 创建
      await teacherApi.createAssignment(formData.value as TeacherTeachingAssignmentCreate)
      ElMessage.success('教学任务创建成功')
    }
    closeDialog()
    loadAssignments()
  } catch (error: any) {
    console.error('Failed to save assignment:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteAssignment(assignment: TeacherTeachingAssignment) {
  try {
    await ElMessageBox.confirm(
      `确定要删除该教学任务吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await teacherApi.deleteAssignment(assignment.id)
    ElMessage.success('删除成功')
    loadAssignments()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete assignment:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadTeachers(),
    loadSchools(),
    loadGrades(),
    loadSubjects(),
    loadSemesters(),
    loadClassrooms(),
    loadAssignments(),
  ])
})
</script>

<style scoped>
.teacher-assignment-management {
  min-height: 100vh;
  background-color: #f9fafb;
}
</style>
