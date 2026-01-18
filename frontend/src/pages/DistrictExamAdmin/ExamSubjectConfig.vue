<template>
  <div class="exam-subject-config p-6">
    <div class="header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">考试科目配置</h1>
      <p class="text-gray-600 mt-2">配置每个年级的考试科目及分数设置</p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-white p-4 rounded-lg shadow">
        <div class="text-sm text-gray-600">已配置年级</div>
        <div class="text-2xl font-bold text-blue-600">{{ configuredGradesCount }}</div>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <div class="text-sm text-gray-600">总配置数</div>
        <div class="text-2xl font-bold text-green-600">{{ totalConfigsCount }}</div>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <div class="text-sm text-gray-600">可用学科</div>
        <div class="text-2xl font-bold text-purple-600">{{ subjectsCount }}</div>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <div class="text-sm text-gray-600">可用年级</div>
        <div class="text-2xl font-bold text-orange-600">{{ gradesCount }}</div>
      </div>
    </div>

    <!-- 年级选择器 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">选择年级</h2>
      <div class="flex gap-3 flex-wrap">
        <button
          v-for="grade in grades"
          :key="grade.id"
          @click="selectGrade(grade.id)"
          :class="[
            'px-6 py-3 rounded-lg font-medium transition-all',
            selectedGradeId === grade.id
              ? 'bg-blue-600 text-white shadow-lg scale-105'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ grade.name }}
          <span v-if="getGradeSubjectCount(grade.id) > 0" class="ml-2 text-sm opacity-80">
            ({{ getGradeSubjectCount(grade.id) }}科)
          </span>
        </button>
      </div>
    </div>

    <!-- 考试科目配置列表 -->
    <div v-if="selectedGradeId" class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">
          {{ getSelectedGradeName() }} - 考试科目配置
        </h2>
        <button
          @click="openAddSubjectModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          添加考试科目
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-500">
        加载中...
      </div>

      <!-- Empty State -->
      <div v-else-if="currentSubjects.length === 0" class="text-center py-12 text-gray-500">
        <div class="text-6xl mb-4">📋</div>
        <p class="text-lg font-medium">暂无考试科目配置</p>
        <p class="text-sm mt-2">点击"添加考试科目"开始配置</p>
      </div>

      <!-- Subject List -->
      <div v-else class="space-y-3">
        <div
          v-for="subject in currentSubjects"
          :key="subject.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
          :class="{ 'opacity-50': !subject.is_active }"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span class="text-lg font-semibold">{{ subject.subject_name }}</span>
                <span class="text-sm text-gray-500">({{ subject.subject_code }})</span>
                <span v-if="!subject.is_active" class="px-2 py-1 bg-red-100 text-red-600 text-xs rounded">
                  已禁用
                </span>
              </div>
              <div class="flex gap-6 text-sm">
                <span class="text-gray-600">
                  满分：<span class="font-semibold text-gray-900">{{ subject.full_score }}</span>分
                </span>
                <span class="text-gray-600">
                  及格线：<span class="font-semibold text-gray-900">{{ subject.pass_line }}</span>分
                </span>
                <span class="text-gray-600">
                  优秀线：<span class="font-semibold text-gray-900">{{ subject.excellent_line }}</span>分
                </span>
                <span class="text-gray-600">
                  良好线：<span class="font-semibold text-gray-900">{{ subject.good_line }}</span>分
                </span>
                <span v-if="subject.description" class="text-gray-500">
                  {{ subject.description }}
                </span>
              </div>
            </div>
            <div class="flex gap-2">
              <button
                @click="editSubject(subject)"
                class="px-3 py-1.5 text-sm bg-blue-100 text-blue-600 rounded hover:bg-blue-200"
              >
                编辑
              </button>
              <button
                @click="toggleSubjectStatus(subject)"
                class="px-3 py-1.5 text-sm rounded"
                :class="subject.is_active
                  ? 'bg-red-100 text-red-600 hover:bg-red-200'
                  : 'bg-green-100 text-green-600 hover:bg-green-200'"
              >
                {{ subject.is_active ? '禁用' : '启用' }}
              </button>
              <button
                @click="deleteSubjectConfirm(subject)"
                class="px-3 py-1.5 text-sm bg-red-100 text-red-600 rounded hover:bg-red-200"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit/Add Modal -->
    <el-dialog
      v-model="showSubjectModal"
      :title="editingSubject ? '编辑考试科目' : '添加考试科目'"
      width="600px"
      @close="closeSubjectModal"
    >
      <el-form :model="subjectForm" :rules="subjectRules" ref="subjectFormRef" label-width="120px">
        <el-form-item label="学科" prop="subject_id">
          <el-select
            v-model="subjectForm.subject_id"
            placeholder="选择学科"
            filterable
            :disabled="editingSubject !== null"
            style="width: 100%"
          >
            <el-option
              v-for="subject in availableSubjects"
              :key="subject.id"
              :label="`${subject.name} (${subject.code})`"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="满分" prop="full_score">
          <el-input-number v-model="subjectForm.full_score" :min="1" :max="1000" />
          <div class="text-xs text-gray-500 mt-1">该科目在考试中的总分</div>
        </el-form-item>
        <el-form-item label="及格线" prop="pass_line">
          <el-input-number v-model="subjectForm.pass_line" :min="0" :max="subjectForm.full_score" />
          <div class="text-xs text-gray-500 mt-1">达到此分数视为及格</div>
        </el-form-item>
        <el-form-item label="优秀线" prop="excellent_line">
          <el-input-number v-model="subjectForm.excellent_line" :min="0" :max="subjectForm.full_score" />
          <div class="text-xs text-gray-500 mt-1">达到此分数视为优秀</div>
        </el-form-item>
        <el-form-item label="良好线" prop="good_line">
          <el-input-number v-model="subjectForm.good_line" :min="0" :max="subjectForm.full_score" />
          <div class="text-xs text-gray-500 mt-1">达到此分数视为良好</div>
        </el-form-item>
        <el-form-item label="显示顺序">
          <el-input-number v-model="subjectForm.display_order" :min="0" />
          <div class="text-xs text-gray-500 mt-1">数值越小越靠前</div>
        </el-form-item>
        <el-form-item label="备注说明">
          <el-input
            v-model="subjectForm.description"
            type="textarea"
            :rows="2"
            placeholder="选填，关于该科目配置的说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeSubjectModal">取消</el-button>
        <el-button type="primary" @click="saveSubject" :loading="saving">
          {{ editingSubject ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import examSubjectsService, { type GradeSubjectConfig, type GradeSubjectConfigCreate } from '@/services/examSubjects'
import curriculumService from '@/services/curriculum'
import { useToast } from '@/composables/useToast'
import type { Grade, Subject } from '@/types/curriculum'

const toast = useToast()

// Data
const grades = ref<Grade[]>([])
const subjects = ref<Subject[]>([])
const allConfigs = ref<GradeSubjectConfig[]>([])
const selectedGradeId = ref<number | null>(null)
const loading = ref(false)
const saving = ref(false)

// Modal
const showSubjectModal = ref(false)
const editingSubject = ref<GradeSubjectConfig | null>(null)
const subjectForm = ref<GradeSubjectConfigCreate>({
  grade_id: 0,
  subject_id: 0,
  full_score: 100,
  pass_line: 60,
  excellent_line: 85,
  good_line: 75,
  display_order: 0,
})

const subjectRules = {
  subject_id: [{ required: true, message: '请选择学科', trigger: 'change' }],
  full_score: [{ required: true, message: '请输入满分', trigger: 'blur' }],
  pass_line: [{ required: true, message: '请输入及格线', trigger: 'blur' }],
  excellent_line: [{ required: true, message: '请输入优秀线', trigger: 'blur' }],
  good_line: [{ required: true, message: '请输入良好线', trigger: 'blur' }],
}

// Computed
const currentSubjects = computed(() => {
  if (!selectedGradeId.value) return []
  return allConfigs.value.filter(c => c.grade_id === selectedGradeId.value)
})

const configuredGradesCount = computed(() => {
  const gradeIds = new Set(allConfigs.value.map(c => c.grade_id))
  return gradeIds.size
})

const totalConfigsCount = computed(() => allConfigs.value.length)

const subjectsCount = computed(() => subjects.value.length)

const gradesCount = computed(() => grades.value.length)

const availableSubjects = computed(() => {
  if (!selectedGradeId.value) return []
  const configuredSubjectIds = currentSubjects.value.map(c => c.subject_id)
  return subjects.value.filter(s => !configuredSubjectIds.includes(s.id))
})

// Methods
const selectGrade = async (gradeId: number) => {
  selectedGradeId.value = gradeId
  await loadGradeSubjects(gradeId)
}

const getSelectedGradeName = () => {
  if (!selectedGradeId.value) return ''
  const grade = grades.value.find(g => g.id === selectedGradeId.value)
  return grade?.name || ''
}

const getGradeSubjectCount = (gradeId: number) => {
  return allConfigs.value.filter(c => c.grade_id === gradeId).length
}

const loadGrades = async () => {
  try {
    const data = await curriculumService.getGrades()
    grades.value = data
  } catch (error) {
    console.error('Failed to load grades:', error)
    toast.error('加载年级失败')
  }
}

const loadSubjects = async () => {
  try {
    const data = await curriculumService.getSubjects()
    subjects.value = data
  } catch (error) {
    console.error('Failed to load subjects:', error)
    toast.error('加载学科失败')
  }
}

const loadAllConfigs = async () => {
  try {
    const data = await examSubjectsService.getGradeSubjectConfigs()
    allConfigs.value = data
  } catch (error) {
    console.error('Failed to load configs:', error)
    toast.error('加载配置失败')
  }
}

const loadGradeSubjects = async (gradeId: number) => {
  loading.value = true
  try {
    const data = await examSubjectsService.getGradeSubjects(gradeId)
    // 更新 allConfigs 中的数据
    const existingOtherGrades = allConfigs.value.filter(c => c.grade_id !== gradeId)
    allConfigs.value = [...existingOtherGrades, ...data.subjects]
  } catch (error) {
    console.error('Failed to load grade subjects:', error)
    toast.error('加载年级科目失败')
  } finally {
    loading.value = false
  }
}

const openAddSubjectModal = () => {
  if (!selectedGradeId.value) {
    toast.warning('请先选择年级')
    return
  }
  if (availableSubjects.value.length === 0) {
    toast.warning('所有学科都已配置，请先删除不需要的配置')
    return
  }
  editingSubject.value = null
  subjectForm.value = {
    grade_id: selectedGradeId.value,
    subject_id: 0,
    full_score: 100,
    pass_line: 60,
    excellent_line: 85,
    good_line: 75,
    display_order: currentSubjects.value.length,
  }
  showSubjectModal.value = true
}

const editSubject = (subject: GradeSubjectConfig) => {
  editingSubject.value = subject
  subjectForm.value = {
    grade_id: subject.grade_id,
    subject_id: subject.subject_id,
    full_score: subject.full_score,
    pass_line: subject.pass_line,
    excellent_line: subject.excellent_line,
    good_line: subject.good_line,
    display_order: subject.display_order,
    description: subject.description,
  }
  showSubjectModal.value = true
}

const closeSubjectModal = () => {
  showSubjectModal.value = false
  editingSubject.value = null
}

const saveSubject = async () => {
  try {
    saving.value = true

    if (editingSubject.value) {
      // 更新
      await examSubjectsService.updateGradeSubjectConfig(
        editingSubject.value.id,
        subjectForm.value
      )
      toast.success('更新成功')
    } else {
      // 创建
      await examSubjectsService.createGradeSubjectConfig(subjectForm.value)
      toast.success('添加成功')
    }

    await loadGradeSubjects(selectedGradeId.value!)
    await loadAllConfigs()
    closeSubjectModal()
  } catch (error: any) {
    console.error('Failed to save subject:', error)
    toast.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const toggleSubjectStatus = async (subject: GradeSubjectConfig) => {
  try {
    await examSubjectsService.toggleGradeSubjectConfig(
      subject.id,
      !subject.is_active
    )
    toast.success(subject.is_active ? '已禁用' : '已启用')
    await loadGradeSubjects(selectedGradeId.value!)
    await loadAllConfigs()
  } catch (error: any) {
    console.error('Failed to toggle status:', error)
    toast.error(error.response?.data?.detail || '操作失败')
  }
}

const deleteSubjectConfirm = (subject: GradeSubjectConfig) => {
  if (!confirm(`确定要删除"${subject.subject_name}"的配置吗？此操作不可撤销。`)) {
    return
  }

  deleteSubject(subject.id)
}

const deleteSubject = async (configId: number) => {
  try {
    await examSubjectsService.deleteGradeSubjectConfig(configId)
    toast.success('删除成功')
    await loadGradeSubjects(selectedGradeId.value!)
    await loadAllConfigs()
  } catch (error: any) {
    console.error('Failed to delete:', error)
    toast.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(async () => {
  await Promise.all([
    loadGrades(),
    loadSubjects(),
    loadAllConfigs(),
  ])
})
</script>

<style scoped>
.exam-subject-config {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
