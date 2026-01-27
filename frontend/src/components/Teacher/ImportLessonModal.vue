<template>
  <div
    v-if="show"
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
              导入教案
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
            <h4 class="text-sm font-semibold text-blue-900 mb-2">📋 导入说明</h4>
            <ul class="text-sm text-blue-800 space-y-1">
              <li>• 支持导入JSON或ZIP格式的教案文件</li>
              <li>• 可以导入其他教师导出的教案（包含在课程导出文件中）</li>
              <li>• 导入的教案会自动关联到对应的课程和章节</li>
              <li>• 如果文件包含资源文件（图片、PDF等），请使用ZIP格式</li>
              <li>• 导入的教案将创建为新的教案，不会覆盖现有教案</li>
            </ul>
          </div>

          <!-- 导入选项 -->
          <div class="mb-4">
            <label class="flex items-center">
              <input 
                type="checkbox" 
                v-model="importOptions.overwrite_existing"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              >
              <span class="ml-2 text-sm text-gray-700">覆盖已存在的教案（如果标题相同）</span>
            </label>
          </div>

          <!-- 文件选择 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">选择文件</label>
            <div class="flex items-center space-x-4">
              <input
                ref="fileInput"
                type="file"
                accept=".json,.zip"
                @change="handleFileSelect"
                class="hidden"
              >
              <button
                @click="() => fileInput?.click()"
                :disabled="importing"
                class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm font-medium rounded-xl hover:from-blue-600 hover:to-indigo-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                选择文件 (JSON/ZIP)
              </button>
              <span v-if="selectedFile" class="text-sm text-gray-600">
                已选择: {{ selectedFile.name }}
              </span>
            </div>
          </div>

          <!-- 导入按钮 -->
          <div v-if="selectedFile" class="mb-4">
            <button
              @click="handleImport"
              :disabled="importing"
              class="w-full inline-flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm font-medium rounded-xl hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="importing" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              {{ importing ? '导入中...' : '开始导入' }}
            </button>
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult" class="mt-6">
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 class="text-sm font-semibold text-gray-900 mb-3">导入结果</h4>
              
              <div class="space-y-2 mb-4">
                <div class="flex items-center justify-between">
                  <span class="text-gray-600">成功导入教案:</span>
                  <span class="font-semibold text-emerald-600">
                    {{ importResult.result?.lessons?.created ?? 0 }}
                  </span>
                </div>
                <div v-if="(importResult.result?.lessons?.skipped ?? 0) > 0" class="flex items-center justify-between">
                  <span class="text-gray-600">跳过教案:</span>
                  <span class="font-semibold text-yellow-600">
                    {{ importResult.result?.lessons?.skipped ?? 0 }}
                  </span>
                </div>
              </div>
              
              <div v-if="importResult.result?.warnings && importResult.result.warnings.length > 0" class="mt-4">
                <h5 class="text-sm font-medium text-yellow-600 mb-2">⚠️ 警告信息:</h5>
                <ul class="text-sm text-yellow-600 space-y-1">
                  <li v-for="warning in importResult.result.warnings" :key="warning" class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>{{ warning }}</span>
                  </li>
                </ul>
              </div>
              
              <div v-if="importResult.result?.errors && importResult.result.errors.length > 0" class="mt-4">
                <h5 class="text-sm font-medium text-red-600 mb-2">❌ 错误详情:</h5>
                <ul class="text-sm text-red-600 space-y-1">
                  <li v-for="error in importResult.result.errors" :key="error" class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>{{ error }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
          <button
            @click="handleClose"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all"
          >
            {{ importResult ? '关闭' : '取消' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import courseExportService, { type CourseImportOptions, type ImportResult } from '@/services/courseExport'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  success: []
}>()

const toast = useToast()

// 响应式数据
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)

// 导入选项
const importOptions = ref<CourseImportOptions>({
  overwrite_existing: false
})

// 监听show变化，重置状态
watch(() => props.show, (newVal) => {
  if (!newVal) {
    // 关闭时重置
    selectedFile.value = null
    importResult.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
})

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    const validation = courseExportService.validateImportFile(file)
    if (!validation.valid) {
      toast.error(validation.error || '文件格式不正确')
      return
    }
    
    selectedFile.value = file
    importResult.value = null
  }
}

// 处理导入
const handleImport = async () => {
  if (!selectedFile.value) return
  
  importing.value = true
  try {
    const result = await courseExportService.importCourses(selectedFile.value, importOptions.value)
    
    // 检查返回结果是否有效
    if (!result) {
      toast.error('导入失败：未收到服务器响应')
      return
    }
    
    // 检查是否有 summary 字段
    if (!result.summary) {
      console.error('Invalid import result:', result)
      toast.error('导入失败：服务器返回格式错误')
      return
    }
    
    importResult.value = result
    
    const hasErrors = (result.summary.total_errors ?? 0) > 0
    const hasWarnings = (result.summary.total_warnings ?? 0) > 0
    const hasCreatedLessons = (result.result?.lessons?.created ?? 0) > 0
    
    // 只要有成功导入的教案，就触发success事件（即使有警告或错误）
    if (hasCreatedLessons) {
      emit('success')
    }
    
    if (!hasErrors && !hasWarnings) {
      toast.success('教案导入成功')
    } else if (hasErrors) {
      toast.warning(`导入完成，但有 ${result.summary.total_errors} 个错误`)
    } else if (hasWarnings) {
      toast.warning(`导入完成，但有 ${result.summary.total_warnings} 个警告`)
    }
  } catch (error: any) {
    console.error('Failed to import lessons:', error)
    toast.error(error.response?.data?.detail || error.message || '导入教案失败')
  } finally {
    importing.value = false
  }
}

// 处理关闭
const handleClose = () => {
  emit('update:show', false)
}
</script>
