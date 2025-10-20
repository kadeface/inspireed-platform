<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="handleClose"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <!-- 遮罩层 -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>

        <!-- 对话框内容 -->
        <div class="relative w-full max-w-lg transform rounded-lg bg-white p-6 shadow-xl transition-all">
          <!-- 标题 -->
          <div class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900">创建新教案</h3>
            <p class="mt-1 text-sm text-gray-500">填写教案基本信息，开始创作</p>
          </div>

          <!-- 表单 -->
          <form @submit.prevent="handleSubmit">
            <!-- 课程选择 -->
            <div class="mb-4 p-4 bg-blue-50 rounded-md">
              <label class="block text-sm font-medium text-gray-700 mb-3">
                选择课程 <span class="text-red-500">*</span>
              </label>
              
              <!-- 学科选择 -->
              <div class="mb-3">
                <select
                  v-model="selectedSubjectId"
                  @change="handleSubjectChange"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">请选择学科</option>
                  <option 
                    v-for="subject in subjects" 
                    :key="subject.id" 
                    :value="subject.id"
                  >
                    {{ subject.name }}
                  </option>
                </select>
              </div>

              <!-- 年级选择 -->
              <div class="mb-3">
                <select
                  v-model="selectedGradeId"
                  @change="handleGradeChange"
                  :disabled="!selectedSubjectId"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  required
                >
                  <option value="">请选择年级</option>
                  <option 
                    v-for="grade in grades" 
                    :key="grade.id" 
                    :value="grade.id"
                  >
                    {{ grade.name }}
                  </option>
                </select>
              </div>

              <!-- 课程显示 -->
              <div v-if="selectedCourse" class="p-3 bg-white rounded border border-blue-200">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-blue-700">已选课程：</span>
                  <span class="text-sm text-gray-900">{{ selectedCourse.name }}</span>
                </div>
              </div>
              <div v-else-if="selectedSubjectId && selectedGradeId && !loadingCourse" class="p-3 bg-yellow-50 rounded border border-yellow-200">
                <p class="text-sm text-yellow-700">该学科和年级的课程不存在，请联系管理员创建</p>
              </div>
            </div>

            <!-- 教案标题 -->
            <div class="mb-4">
              <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
                教案标题 <span class="text-red-500">*</span>
              </label>
              <input
                id="title"
                v-model="formData.title"
                type="text"
                required
                placeholder="例如：Python 基础入门"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': errors.title }"
              />
              <p v-if="errors.title" class="mt-1 text-sm text-red-600">{{ errors.title }}</p>
            </div>

            <!-- 教案描述 -->
            <div class="mb-4">
              <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                教案描述
              </label>
              <textarea
                id="description"
                v-model="formData.description"
                rows="3"
                placeholder="简要描述教案内容和目标..."
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- 教案标签 -->
            <div class="mb-4">
              <label for="tags" class="block text-sm font-medium text-gray-700 mb-2">
                标签（可选）
              </label>
              <input
                id="tags"
                v-model="tagsInput"
                type="text"
                placeholder="用逗号分隔，例如：Python, 编程, 初级"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- 模板选择 -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-3">选择模板</label>
              <div class="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  v-for="template in templates"
                  :key="template.id"
                  @click="selectedTemplate = template.id"
                  :class="[
                    'p-4 border-2 rounded-lg text-center transition-all',
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300',
                  ]"
                >
                  <div class="text-2xl mb-2">{{ template.icon }}</div>
                  <div class="text-sm font-medium text-gray-900">{{ template.name }}</div>
                  <div class="text-xs text-gray-500 mt-1">{{ template.description }}</div>
                </button>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex justify-end gap-3">
              <button
                type="button"
                @click="handleClose"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ isSubmitting ? '创建中...' : '创建教案' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { LessonCreate } from '../../types/lesson'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import type { Subject, Grade, Course } from '../../types/curriculum'
import curriculumService from '../../services/curriculum'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  create: [lessonData: LessonCreate]
}>()

// 课程选择数据
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const selectedSubjectId = ref<number | string>('')
const selectedGradeId = ref<number | string>('')
const selectedCourse = ref<Course | null>(null)
const loadingCourse = ref(false)

// 表单数据
const formData = ref({
  title: '',
  description: '',
})

const tagsInput = ref('')
const selectedTemplate = ref('blank')
const isSubmitting = ref(false)
const errors = ref<Record<string, string>>({})

// 加载学科和年级
onMounted(async () => {
  try {
    const [subjectsData, gradesData] = await Promise.all([
      curriculumService.getSubjects(),
      curriculumService.getGrades()
    ])
    subjects.value = subjectsData
    grades.value = gradesData
  } catch (error) {
    console.error('Failed to load curriculum data:', error)
  }
})

// 处理学科变更
async function handleSubjectChange() {
  selectedGradeId.value = ''
  selectedCourse.value = null
}

// 处理年级变更
async function handleGradeChange() {
  if (!selectedSubjectId.value || !selectedGradeId.value) {
    selectedCourse.value = null
    return
  }

  loadingCourse.value = true
  try {
    const course = await curriculumService.getCourseBySubjectAndGrade(
      Number(selectedSubjectId.value),
      Number(selectedGradeId.value)
    )
    selectedCourse.value = course
  } catch (error) {
    console.error('Failed to load course:', error)
    selectedCourse.value = null
  } finally {
    loadingCourse.value = false
  }
}

// 模板定义
const templates = [
  {
    id: 'blank',
    name: '空白教案',
    icon: '📄',
    description: '从零开始',
  },
  {
    id: 'theory',
    name: '理论课',
    icon: '📚',
    description: '含文本单元',
  },
  {
    id: 'lab',
    name: '实验课',
    icon: '💻',
    description: '含代码单元',
  },
]

// 解析标签
const parsedTags = computed(() => {
  if (!tagsInput.value.trim()) return []
  return tagsInput.value
    .split(',')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)
})

// 根据模板生成初始内容
function generateTemplateContent(templateId: string): Cell[] {
  switch (templateId) {
    case 'theory':
      return [
        {
          id: uuidv4(),
          type: CellType.TEXT,
          order: 0,
          editable: true,
          content: {
            html: '<h2>课程概述</h2><p>在此输入课程内容...</p>',
          },
        } as Cell,
      ]
    case 'lab':
      return [
        {
          id: uuidv4(),
          type: CellType.TEXT,
          order: 0,
          editable: true,
          content: {
            html: '<h2>实验说明</h2><p>在此输入实验要求...</p>',
          },
        } as Cell,
        {
          id: uuidv4(),
          type: CellType.CODE,
          order: 1,
          editable: true,
          content: {
            code: '# 在此编写代码\nprint("Hello, World!")',
            language: 'python' as const,
          },
          config: {
            environment: 'jupyterlite' as const,
          },
        } as Cell,
      ]
    default:
      return []
  }
}

// 表单验证
function validateForm(): boolean {
  errors.value = {}
  
  if (!selectedCourse.value) {
    alert('请选择课程')
    return false
  }
  
  if (!formData.value.title.trim()) {
    errors.value.title = '请输入教案标题'
    return false
  }
  
  if (formData.value.title.length > 100) {
    errors.value.title = '标题不能超过100个字符'
    return false
  }
  
  return true
}

// 提交表单
function handleSubmit() {
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  const lessonData: LessonCreate = {
    title: formData.value.title.trim(),
    description: formData.value.description.trim() || undefined,
    course_id: selectedCourse.value!.id,
    tags: parsedTags.value.length > 0 ? parsedTags.value : undefined,
    content: generateTemplateContent(selectedTemplate.value),
  }
  
  emit('create', lessonData)
  
  // 延迟重置，避免闪烁
  setTimeout(() => {
    isSubmitting.value = false
  }, 500)
}

// 关闭对话框
function handleClose() {
  emit('update:modelValue', false)
}

// 重置表单
function resetForm() {
  formData.value = {
    title: '',
    description: '',
  }
  tagsInput.value = ''
  selectedTemplate.value = 'blank'
  selectedSubjectId.value = ''
  selectedGradeId.value = ''
  selectedCourse.value = null
  errors.value = {}
  isSubmitting.value = false
}

// 监听对话框关闭，重置表单
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    setTimeout(resetForm, 300) // 等待动画完成
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

