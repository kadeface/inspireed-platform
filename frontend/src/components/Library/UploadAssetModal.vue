<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="handleClose"
  >
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="handleClose"></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative bg-white rounded-lg shadow-xl max-w-lg w-full">
        <!-- 头部 -->
        <div class="px-6 pt-6 pb-4 border-b">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900">上传资源到资源库</h3>
            <button @click="handleClose" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容 -->
        <div class="px-6 py-4">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源标题 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.title"
                type="text"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900 placeholder:text-gray-400"
                placeholder="请输入资源标题"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">资源描述</label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900 placeholder:text-gray-400"
                placeholder="请输入资源描述"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择文件 <span class="text-red-500">*</span>
              </label>
              <input
                ref="fileInput"
                type="file"
                @change="handleFileSelect"
                class="hidden"
              />
              <div
                v-if="!selectedFile"
                @click="$refs.fileInput.click()"
                class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-purple-400"
              >
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mt-2 text-sm text-gray-600">点击选择文件</p>
              </div>
              <div v-else class="flex items-center justify-between p-4 border rounded-lg">
                <div class="flex items-center">
                  <svg class="h-10 w-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div class="ml-3">
                    <p class="text-sm font-medium">{{ selectedFile.name }}</p>
                    <p class="text-xs text-gray-500">{{ formatSize(selectedFile.size) }}</p>
                  </div>
                </div>
                <button @click="clearFile" type="button" class="text-red-500 hover:text-red-700">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">学科分类</label>
              <select
                v-model="formData.subject_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900"
              >
                <option :value="undefined">不分类</option>
                <option
                  v-for="subject in subjects"
                  :key="subject.id"
                  :value="subject.id"
                >
                  {{ subject.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">年级分类</label>
              <select
                v-model="formData.grade_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900"
              >
                <option :value="undefined">不分类（跨年级通用）</option>
                <option
                  v-for="grade in grades"
                  :key="grade.id"
                  :value="grade.id"
                >
                  {{ grade.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">可见性</label>
              <select
                v-model="formData.visibility"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900"
              >
                <option value="teacher_only">仅自己可见</option>
                <option value="school">全校可见</option>
              </select>
            </div>
          </form>
        </div>

        <!-- 底部 -->
        <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3">
          <button
            @click="handleClose"
            :disabled="uploading"
            class="px-4 py-2 border rounded-lg hover:bg-gray-100 disabled:opacity-50"
          >
            取消
          </button>
          <button
            @click="handleSubmit"
            :disabled="!canSubmit || uploading"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            <span v-if="uploading">上传中...</span>
            <span v-else>上传</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { libraryService } from '@/services/library'
import { formatFileSize } from '@/types/library'
import { curriculumService } from '@/services/curriculum'
import type { Subject, Grade } from '@/types/curriculum'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  success: []
}>()

const uploading = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement>()
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const loadingSubjects = ref(false)
const loadingGrades = ref(false)

const formData = ref({
  title: '',
  description: '',
  visibility: 'teacher_only',
  subject_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
})

const canSubmit = computed(() => {
  return formData.value.title.trim() && selectedFile.value !== null
})

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    if (!formData.value.title.trim()) {
      formData.value.title = target.files[0].name.replace(/\.[^/.]+$/, '')
    }
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatSize = (bytes: number) => formatFileSize(bytes)

const handleClose = () => {
  if (!uploading.value) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    visibility: 'teacher_only',
    subject_id: undefined,
    grade_id: undefined,
  }
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 加载学科列表
const loadSubjects = async () => {
  loadingSubjects.value = true
  try {
    subjects.value = await curriculumService.getSubjects()
  } catch (error) {
    console.error('Failed to load subjects:', error)
  } finally {
    loadingSubjects.value = false
  }
}

// 加载年级列表
const loadGrades = async () => {
  loadingGrades.value = true
  try {
    grades.value = await curriculumService.getGrades()
  } catch (error) {
    console.error('Failed to load grades:', error)
  } finally {
    loadingGrades.value = false
  }
}

onMounted(() => {
  loadSubjects()
  loadGrades()
})

const handleSubmit = async () => {
  if (!canSubmit.value || !selectedFile.value) return

  uploading.value = true
  try {
    await libraryService.uploadAsset(selectedFile.value, {
      title: formData.value.title,
      description: formData.value.description || undefined,
      visibility: formData.value.visibility,
      subject_id: formData.value.subject_id,
      grade_id: formData.value.grade_id,
    })
    
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('Upload failed:', error)
    alert(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
/* 下拉选项样式 */
select option {
  background-color: white;
  color: rgb(17, 24, 39); /* text-gray-900 */
}

/* 选择框的下拉箭头颜色 */
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}
</style>
