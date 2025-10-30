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
        class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl"
      >
        <!-- 头部 -->
        <div class="bg-white px-6 pt-6">
          <div class="flex items-center justify-between mb-4">
            <h3
              class="text-xl font-semibold text-gray-900"
              id="modal-title"
            >
              批量导入章节
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
          
          <!-- 说明文字 -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3 flex-1">
                <h4 class="text-sm font-medium text-blue-800 mb-1">
                  导入说明
                </h4>
                <ul class="text-sm text-blue-700 space-y-1 list-disc list-inside">
                  <li>支持 Excel (.xlsx, .xls) 和 CSV (.csv) 格式</li>
                  <li>必需列：名称(name)、编码(code)、显示顺序(display_order)</li>
                  <li>可选列：描述(description)、父章节编码(parent_code)、是否启用(is_active)</li>
                  <li>使用 parent_code 建立父子关系，父章节需在子章节之前导入</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 内容区 -->
        <div class="bg-white px-6 pb-6">
          <!-- 课程选择（带搜索过滤） -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              选择课程 <span class="text-red-500">*</span>
            </label>
            <!-- 搜索框 -->
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索 学科/年级/课程名 或 课程编码..."
              class="w-full mb-2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="loading"
            />
            <select
              v-model="selectedCourseId"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="loading"
            >
              <option :value="null">请选择课程</option>
              <option
                v-for="course in filteredCourses"
                :key="course.id"
                :value="course.id"
              >
                {{ formatCourseLabel(course) }}
              </option>
            </select>
          </div>

          <!-- 下载模板 -->
          <div class="mb-6">
            <button
              @click="downloadTemplate"
              :disabled="downloading"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ downloading ? '下载中...' : '下载导入模板' }}
            </button>
          </div>

          <!-- 文件上传区 -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              上传文件 <span class="text-red-500">*</span>
            </label>
            <div
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleFileDrop"
              :class="[
                'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                isDragging
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              ]"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".xlsx,.xls,.csv"
                class="hidden"
                @change="handleFileSelect"
              />
              
              <div v-if="!selectedFile">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mt-2 text-sm text-gray-600">
                  拖拽文件到此处，或
                  <button
                    @click="$refs.fileInput.click()"
                    class="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    点击选择文件
                  </button>
                </p>
                <p class="mt-1 text-xs text-gray-500">
                  支持 Excel 或 CSV 格式
                </p>
              </div>

              <div v-else class="flex items-center justify-between">
                <div class="flex items-center">
                  <svg class="h-10 w-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div class="ml-3 text-left">
                    <p class="text-sm font-medium text-gray-900">
                      {{ selectedFile.name }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ formatFileSize(selectedFile.size) }}
                    </p>
                  </div>
                </div>
                <button
                  @click="clearFile"
                  class="text-red-500 hover:text-red-700 transition-colors"
                >
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult" class="mb-6">
            <div
              :class="[
                'rounded-lg p-4',
                importResult.success
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              ]"
            >
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg
                    v-if="importResult.success"
                    class="h-5 w-5 text-green-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <svg
                    v-else
                    class="h-5 w-5 text-red-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3
                    :class="[
                      'text-sm font-medium',
                      importResult.success ? 'text-green-800' : 'text-red-800'
                    ]"
                  >
                    {{ importResult.message }}
                  </h3>
                  <div
                    v-if="importResult.details"
                    :class="[
                      'mt-2 text-sm',
                      importResult.success ? 'text-green-700' : 'text-red-700'
                    ]"
                  >
                    <p>{{ importResult.details }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="mb-6">
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-red-800">
                    导入失败
                  </h3>
                  <div class="mt-2 text-sm text-red-700">
                    <p>{{ error }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
            @click="handleImport"
            :disabled="!canImport || loading"
            class="px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              导入中...
            </span>
            <span v-else>开始导入</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import curriculumService from '@/services/curriculum'
import type { Course } from '@/types/curriculum'

// 供下拉使用的课程类型，允许携带学科/年级名称
type CourseOption = Course & { subject_name?: string; grade_name?: string }

interface Props {
  isOpen: boolean
  courses: CourseOption[]
}

interface ImportResult {
  success: boolean
  message: string
  details?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
  'success': []
}>()

const selectedCourseId = ref<number | null>(null)
const searchQuery = ref('')
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const loading = ref(false)
const downloading = ref(false)
const error = ref<string | null>(null)
const importResult = ref<ImportResult | null>(null)
const fileInput = ref<HTMLInputElement>()

const canImport = computed(() => {
  return selectedCourseId.value !== null && selectedFile.value !== null
})

// 过滤后的课程列表
const filteredCourses = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.courses
  return props.courses.filter(c => {
    const parts = [
      c.name ?? '',
      c.code ?? '',
      (c as any).subject_name ?? '',
      (c as any).grade_name ?? ''
    ]
    return parts.some(p => String(p).toLowerCase().includes(q))
  })
})

function formatCourseLabel(course: CourseOption) {
  const subject = (course as any).subject_name
  const grade = (course as any).grade_name
  const code = course.code ? `（${course.code}）` : ''
  if (subject || grade) {
    return `${subject ?? ''} · ${grade ?? ''} / ${course.name}${code}`.replace(' ·  / ', ' / ')
  }
  return `${course.name}${code}`
}

function handleClose() {
  if (!loading.value) {
    resetForm()
    emit('close')
  }
}

function resetForm() {
  selectedCourseId.value = null
  selectedFile.value = null
  error.value = null
  importResult.value = null
  isDragging.value = false
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    error.value = null
    importResult.value = null
  }
}

function handleFileDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    // 验证文件类型
    const validTypes = ['.xlsx', '.xls', '.csv']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (validTypes.includes(fileExtension)) {
      selectedFile.value = file
      error.value = null
      importResult.value = null
    } else {
      error.value = '请上传 Excel 或 CSV 格式的文件'
    }
  }
}

function clearFile() {
  selectedFile.value = null
  error.value = null
  importResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

async function downloadTemplate() {
  downloading.value = true
  error.value = null
  
  try {
    const blob = await curriculumService.downloadChapterTemplate()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '章节导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = err.message || '下载模板失败，请稍后重试'
  } finally {
    downloading.value = false
  }
}

async function handleImport() {
  if (!selectedCourseId.value || !selectedFile.value) {
    return
  }

  loading.value = true
  error.value = null
  importResult.value = null

  try {
    const result = await curriculumService.batchImportChapters(
      selectedCourseId.value,
      selectedFile.value
    )
    
    importResult.value = {
      success: true,
      message: '导入成功！',
      details: result.message || `成功导入 ${result.chapters.length} 个章节`
    }
    
    // 延迟关闭，让用户看到成功消息
    setTimeout(() => {
      emit('success')
      handleClose()
    }, 1500)
  } catch (err: any) {
    error.value = err.message || '导入失败，请检查文件格式和内容'
    importResult.value = {
      success: false,
      message: '导入失败',
      details: err.message
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 可选：添加一些自定义样式 */
</style>

