<template>
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="modal-content bg-white rounded-lg shadow-xl p-5 w-full max-w-md max-h-[90vh] overflow-y-auto">
      <h2 class="text-xl font-bold mb-3">
        {{ course ? '编辑课程' : '创建课程' }}
      </h2>

      <form @submit.prevent="handleSubmit">
        <!-- Subject and Grade in one row -->
        <div class="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              学科 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.subject_id"
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="!!course"
              required
            >
              <option value="">请选择学科</option>
              <option 
                v-for="subject in activeSubjects" 
                :key="subject.id" 
                :value="subject.id"
              >
                {{ subject.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              年级 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.grade_id"
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="{ 'border-orange-300': course && originalGradeId && formData.grade_id !== originalGradeId }"
              required
            >
              <option value="">请选择年级</option>
              <option 
                v-for="grade in activeGrades" 
                :key="grade.id" 
                :value="grade.id"
              >
                {{ grade.name }}
              </option>
            </select>
          </div>
        </div>
        <p v-if="course" class="text-xs text-gray-500 mb-3 -mt-2">学科不可修改</p>
        
        <!-- 年级变更警告 -->
        <div 
          v-if="course && originalGradeId && formData.grade_id !== originalGradeId && (courseStats.lesson_count > 0 || courseStats.chapter_count > 0)"
          class="mb-3 p-3 bg-orange-50 border border-orange-200 rounded-lg"
        >
          <div class="flex items-start gap-2">
            <span class="text-orange-600 text-lg">⚠️</span>
            <div class="flex-1">
              <p class="text-sm font-medium text-orange-800 mb-1">年级变更警告</p>
              <p class="text-xs text-orange-700">
                该课程下有 <strong>{{ courseStats.lesson_count }}</strong> 个教案和 
                <strong>{{ courseStats.chapter_count }}</strong> 个章节。
                调整年级后，这些数据将保留在当前课程下。
              </p>
            </div>
          </div>
        </div>

        <!-- Course Name -->
        <div class="mb-3">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            课程名称 <span class="text-red-500">*</span>
          </label>
          <div class="flex gap-2">
            <input
              v-model="formData.name"
              type="text"
              class="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="例如：一年级数学"
              required
            />
            <button
              v-if="!course && formData.subject_id && formData.grade_id"
              type="button"
              @click="autoGenerateName"
              class="px-3 py-1.5 text-xs text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg whitespace-nowrap"
            >
              自动生成
            </button>
          </div>
        </div>

        <!-- Advanced Options (Collapsible) -->
        <div class="mb-3">
          <button
            type="button"
            @click="showAdvanced = !showAdvanced"
            class="flex items-center text-sm text-gray-600 hover:text-gray-800 w-full"
          >
            <span>高级选项</span>
            <svg
              :class="['ml-1 w-4 h-4 transition-transform', showAdvanced ? 'rotate-180' : '']"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <div v-show="showAdvanced" class="mt-2 space-y-3">
            <!-- Course Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                课程代码
              </label>
              <input
                v-model="formData.code"
                type="text"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例如：grade1-math"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                课程描述
              </label>
              <textarea
                v-model="formData.description"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="2"
                placeholder="课程简介..."
              ></textarea>
            </div>

            <!-- Display Order -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                显示顺序
              </label>
              <input
                v-model.number="formData.display_order"
                type="number"
                class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
              />
            </div>

            <!-- Is Active (only for edit mode) -->
            <div v-if="course">
              <label class="flex items-center">
                <input
                  v-model="formData.is_active"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm font-medium text-gray-700">启用该课程</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-2 mt-4 pt-3 border-t">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            type="submit"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {{ course ? '保存' : '创建' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Course, Subject, Grade, CourseCreate, CourseUpdate } from '@/types/curriculum'
import curriculumService from '@/services/curriculum'

interface Props {
  course?: {
    course?: Course
    subject?: Subject
    grade?: Grade
  } | null
  subjects?: Subject[]
  grades?: Grade[]
}

const props = withDefaults(defineProps<Props>(), {
  subjects: () => [],
  grades: () => []
})
const emit = defineEmits<{
  close: []
  save: [data: CourseCreate | CourseUpdate]
}>()

const showAdvanced = ref(false)
const originalGradeId = ref<number | null>(null)
const courseStats = ref({ lesson_count: 0, chapter_count: 0 })

const formData = ref<{
  subject_id: number | string
  grade_id: number | string
  name: string
  code: string
  description: string
  display_order: number
  is_active: boolean
}>({
  subject_id: '',
  grade_id: '',
  name: '',
  code: '',
  description: '',
  display_order: 0,
  is_active: true
})

const activeSubjects = computed(() => 
  props.subjects?.filter(s => s.is_active) || []
)

const activeGrades = computed(() => 
  props.grades?.filter(g => g.is_active) || []
)

// 获取课程统计数据
async function loadCourseStats(courseId: number) {
  try {
    const courseWithChapters = await curriculumService.getCourseWithChapters(courseId)
    courseStats.value = {
      lesson_count: courseWithChapters.total_lessons || 0,
      chapter_count: courseWithChapters.total_chapters || 0
    }
  } catch (error) {
    console.error('Failed to load course stats:', error)
    // 如果获取失败，使用默认值
    courseStats.value = { lesson_count: 0, chapter_count: 0 }
  }
}

onMounted(async () => {
  if (props.course?.course) {
    const c = props.course.course
    originalGradeId.value = c.grade_id
    formData.value = {
      subject_id: c.subject_id,
      grade_id: c.grade_id,
      name: c.name,
      code: c.code || '',
      description: c.description || '',
      display_order: c.display_order,
      is_active: c.is_active
    }
    // Show advanced options by default when editing if there's any data
    showAdvanced.value = !!(c.code || c.description || c.display_order)
    
    // 加载课程统计数据
    await loadCourseStats(c.id)
  }
})

function autoGenerateName() {
  const subject = props.subjects.find(s => s.id === formData.value.subject_id)
  const grade = props.grades.find(g => g.id === formData.value.grade_id)
  
  if (subject && grade) {
    formData.value.name = curriculumService.generateCourseName(subject.name, grade.name)
  }
}

function handleSubmit() {
  if (!formData.value.subject_id || !formData.value.grade_id) {
    alert('请选择学科和年级')
    return
  }

  if (props.course?.course) {
    // Update mode - only send changed fields
    const updateData: CourseUpdate = {
      name: formData.value.name,
      code: formData.value.code || undefined,
      description: formData.value.description || undefined,
      display_order: formData.value.display_order,
      is_active: formData.value.is_active
    }
    
    // 如果年级改变了，包含 grade_id
    if (originalGradeId.value !== null && formData.value.grade_id !== originalGradeId.value) {
      updateData.grade_id = Number(formData.value.grade_id)
    }
    
    emit('save', updateData)
  } else {
    // Create mode
    const createData: CourseCreate = {
      subject_id: Number(formData.value.subject_id),
      grade_id: Number(formData.value.grade_id),
      name: formData.value.name,
      code: formData.value.code || undefined,
      description: formData.value.description || undefined,
      display_order: formData.value.display_order
    }
    emit('save', createData)
  }
}
</script>

<style scoped>
.modal-overlay {
  animation: fadeIn 0.2s ease-in-out;
}

.modal-content {
  animation: slideIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>

