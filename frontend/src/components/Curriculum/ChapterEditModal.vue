<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
  >
    <!-- 背景遮罩 -->
    <div
      class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
      @click="handleClose"
    ></div>

    <!-- 模态框内容 -->
    <div class="flex min-h-full items-center justify-center p-4">
      <div
        class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg"
      >
        <!-- 头部 -->
        <div class="bg-white px-6 pt-6">
          <div class="flex items-center justify-between mb-4">
            <h3
              class="text-xl font-semibold text-gray-900"
              id="modal-title"
            >
              {{ chapter ? '编辑章节' : '添加章节' }}
            </h3>
            <button
              @click="handleClose"
              class="text-gray-400 hover:text-gray-500 transition-colors"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容区 -->
        <div class="bg-white px-6 pb-6">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <!-- 课程选择 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                所属课程 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="formData.course_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :disabled="loading"
                required
              >
                <option :value="0">请选择课程</option>
                <option
                  v-for="course in courses"
                  :key="course.id"
                  :value="course.id"
                >
                  {{ course.name }}
                </option>
              </select>
            </div>

            <!-- 章节名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                章节名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.name"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入章节名称"
                :disabled="loading"
                required
              />
            </div>

            <!-- 章节编码 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                章节编码 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.code"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入章节编码"
                :disabled="loading"
                required
              />
            </div>

            <!-- 章节描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                章节描述
              </label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入章节描述"
                :disabled="loading"
              ></textarea>
            </div>

            <!-- 显示顺序 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                显示顺序
              </label>
              <input
                v-model.number="formData.display_order"
                type="number"
                min="0"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入显示顺序"
                :disabled="loading"
              />
            </div>

            <!-- 父章节选择 -->
            <div v-if="parentChapters.length > 0">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                父章节
              </label>
              <select
                v-model="formData.parent_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :disabled="loading"
              >
                <option :value="undefined">无（顶级章节）</option>
                <option
                  v-for="parent in parentChapters"
                  :key="parent.id"
                  :value="parent.id"
                >
                  {{ parent.name }}
                </option>
              </select>
            </div>

            <!-- 是否启用 -->
            <div class="flex items-center">
              <input
                v-model="formData.is_active"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                :disabled="loading"
              />
              <label class="ml-2 block text-sm text-gray-700">
                启用此章节
              </label>
            </div>
          </form>
        </div>

        <!-- 底部按钮 -->
        <div class="bg-gray-50 px-6 py-4 flex items-center justify-end space-x-3">
          <button
            @click="handleClose"
            :disabled="loading"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            取消
          </button>
          <button
            @click="handleSubmit"
            :disabled="!canSave || loading"
            class="px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              保存中...
            </span>
            <span v-else>保存</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import curriculumService from '@/services/curriculum'
import type { Course, Chapter, ChapterCreate } from '@/types/curriculum'

interface Props {
  isOpen: boolean
  chapter?: Chapter | null
  courses: Course[]
}

type ChapterFormData = ChapterCreate & {
  is_active: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
  'save': [data: ChapterFormData]
}>()

const loading = ref(false)
const parentChapters = ref<Chapter[]>([])

const formData = ref<ChapterFormData>({
  course_id: 0,
  name: '',
  code: '',
  description: '',
  display_order: 0,
  parent_id: undefined,
  is_active: true
})

const canSave = computed(() => {
  return formData.value.course_id > 0 && 
         formData.value.name.trim() && 
         formData.value.code.trim()
})

// 监听课程变化，加载父章节选项
watch(() => formData.value.course_id, async (newCourseId) => {
  if (newCourseId) {
    try {
      const chapters = await curriculumService.getCourseChapters(newCourseId, true)
      // 只显示顶级章节作为父章节选项
      parentChapters.value = chapters.filter(ch => !ch.parent_id)
    } catch (error) {
      console.error('Failed to load parent chapters:', error)
      parentChapters.value = []
    }
  } else {
    parentChapters.value = []
  }
})

// 监听章节变化，初始化表单数据
watch(() => props.chapter, (newChapter) => {
  if (newChapter) {
    formData.value = {
      course_id: newChapter.course_id,
      name: newChapter.name,
      code: newChapter.code || '',
      description: newChapter.description || '',
      display_order: newChapter.display_order,
      parent_id: newChapter.parent_id,
      is_active: newChapter.is_active
    }
  } else {
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  formData.value = {
    course_id: 0,
    name: '',
    code: '',
    description: '',
    display_order: 0,
    parent_id: undefined,
    is_active: true
  }
}

function handleClose() {
  if (!loading.value) {
    resetForm()
    emit('close')
  }
}

async function handleSubmit() {
  if (!canSave.value) return
  
  loading.value = true
  try {
    emit('save', { ...formData.value })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 可选：添加一些自定义样式 */
</style>
