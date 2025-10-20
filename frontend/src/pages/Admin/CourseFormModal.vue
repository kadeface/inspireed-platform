<template>
  <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="modal-content bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
      <h2 class="text-2xl font-bold mb-4">
        {{ course ? '编辑课程' : '创建课程' }}
      </h2>

      <form @submit.prevent="handleSubmit">
        <!-- Subject Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            学科 <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.subject_id"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
          <p v-if="course" class="text-xs text-gray-500 mt-1">学科不可修改</p>
        </div>

        <!-- Grade Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            年级 <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.grade_id"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="!!course"
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
          <p v-if="course" class="text-xs text-gray-500 mt-1">年级不可修改</p>
        </div>

        <!-- Course Name -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            课程名称 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="例如：一年级数学"
            required
          />
          <button
            v-if="!course && formData.subject_id && formData.grade_id"
            type="button"
            @click="autoGenerateName"
            class="text-xs text-blue-600 hover:text-blue-700 mt-1"
          >
            自动生成名称
          </button>
        </div>

        <!-- Course Code -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            课程代码
          </label>
          <input
            v-model="formData.code"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="例如：grade1-math"
          />
        </div>

        <!-- Description -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            课程描述
          </label>
          <textarea
            v-model="formData.description"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="3"
            placeholder="课程简介..."
          ></textarea>
        </div>

        <!-- Display Order -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            显示顺序
          </label>
          <input
            v-model.number="formData.display_order"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="0"
          />
        </div>

        <!-- Is Active (only for edit mode) -->
        <div v-if="course" class="mb-4">
          <label class="flex items-center">
            <input
              v-model="formData.is_active"
              type="checkbox"
              class="mr-2"
            />
            <span class="text-sm font-medium text-gray-700">启用该课程</span>
          </label>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-2 mt-6">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
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

onMounted(() => {
  if (props.course?.course) {
    const c = props.course.course
    formData.value = {
      subject_id: c.subject_id,
      grade_id: c.grade_id,
      name: c.name,
      code: c.code || '',
      description: c.description || '',
      display_order: c.display_order,
      is_active: c.is_active
    }
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

