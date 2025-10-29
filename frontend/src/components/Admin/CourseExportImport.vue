<template>
  <div class="course-export-import">
    <div class="header">
      <h2 class="text-2xl font-bold text-gray-800 mb-6">课程导出导入管理</h2>
      <p class="text-gray-600 mb-6">支持将课程数据导出为JSON文件，或从JSON文件导入课程数据到系统中</p>
    </div>

    <!-- 导出功能 -->
    <div class="export-section mb-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          导出课程数据
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">导出选项</label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input 
                  type="checkbox" 
                  v-model="exportOptions.include_lessons"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
                <span class="ml-2 text-sm text-gray-700">包含教案数据</span>
              </label>
              <label class="flex items-center">
                <input 
                  type="checkbox" 
                  v-model="exportOptions.include_resources"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
                <span class="ml-2 text-sm text-gray-700">包含资源数据</span>
              </label>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择课程</label>
            <select 
              v-model="selectedCourseId" 
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            >
              <option value="">选择要导出的课程</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <button
            @click="downloadTemplate"
            :disabled="downloading"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <svg v-if="downloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            下载模板
          </button>
          
          <button
            @click="exportSingleCourse"
            :disabled="!selectedCourseId || downloading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <svg v-if="downloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            导出选中课程
          </button>
          
          <button
            @click="exportAllCourses"
            :disabled="downloading"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <svg v-if="downloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            导出所有课程
          </button>
        </div>
      </div>
    </div>

    <!-- 导入功能 -->
    <div class="import-section">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
          </svg>
          导入课程数据
        </h3>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">导入选项</label>
          <label class="flex items-center">
            <input 
              type="checkbox" 
              v-model="importOptions.overwrite_existing"
              class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            >
            <span class="ml-2 text-sm text-gray-700">覆盖已存在的数据</span>
          </label>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">选择文件</label>
          <div class="flex items-center space-x-4">
            <input
              ref="fileInput"
              type="file"
              accept=".json"
              @change="handleFileSelect"
              class="hidden"
            >
            <button
              @click="$refs.fileInput.click()"
              class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              选择JSON文件
            </button>
            <span v-if="selectedFile" class="text-sm text-gray-600">
              已选择: {{ selectedFile.name }}
            </span>
          </div>
        </div>

        <div v-if="selectedFile" class="mb-4">
          <button
            @click="previewFile"
            :disabled="previewing"
            class="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center mr-2"
          >
            <svg v-if="previewing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            预览文件
          </button>
          
          <button
            @click="importCourses"
            :disabled="importing"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <svg v-if="importing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            开始导入
          </button>
        </div>

        <!-- 文件预览 -->
        <div v-if="filePreview" class="mb-4">
          <h4 class="text-md font-medium text-gray-800 mb-2">文件预览</h4>
          <div class="bg-gray-50 rounded-md p-4 max-h-64 overflow-y-auto">
            <pre class="text-sm text-gray-700">{{ JSON.stringify(filePreview, null, 2) }}</pre>
          </div>
        </div>

        <!-- 导入结果 -->
        <div v-if="importResult" class="mb-4">
          <h4 class="text-md font-medium text-gray-800 mb-2">导入结果</h4>
          <div class="bg-gray-50 rounded-md p-4">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ importResult.summary.total_created }}</div>
                <div class="text-sm text-gray-600">成功创建</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-yellow-600">{{ importResult.summary.total_skipped }}</div>
                <div class="text-sm text-gray-600">跳过重复</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ importResult.summary.total_errors }}</div>
                <div class="text-sm text-gray-600">错误数量</div>
              </div>
            </div>
            
            <div v-if="importResult.result.errors.length > 0" class="mt-4">
              <h5 class="text-sm font-medium text-red-600 mb-2">错误详情:</h5>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { toast } from '@/composables/useToast'
import courseExportService, { type CourseExportOptions, type CourseImportOptions, type ImportResult } from '@/services/courseExport'
import curriculumService from '@/services/curriculum'
import type { Course } from '@/types/curriculum'

// 响应式数据
const courses = ref<Course[]>([])
const selectedCourseId = ref<number | null>(null)
const selectedFile = ref<File | null>(null)
const downloading = ref(false)
const importing = ref(false)
const previewing = ref(false)
const filePreview = ref<any>(null)
const importResult = ref<ImportResult | null>(null)

// 导出选项
const exportOptions = ref<CourseExportOptions>({
  include_lessons: true,
  include_resources: true
})

// 导入选项
const importOptions = ref<CourseImportOptions>({
  overwrite_existing: false
})

// 加载课程列表
const loadCourses = async () => {
  try {
    const courseList = await curriculumService.getCourses()
    courses.value = courseList
  } catch (error) {
    console.error('Failed to load courses:', error)
    toast.error('加载课程列表失败')
  }
}

// 下载模板
const downloadTemplate = async () => {
  downloading.value = true
  try {
    const blob = await courseExportService.downloadTemplate()
    courseExportService.downloadFile(blob, '课程导出模板.json')
    toast.success('模板下载成功')
  } catch (error) {
    console.error('Failed to download template:', error)
    toast.error('模板下载失败')
  } finally {
    downloading.value = false
  }
}

// 导出单个课程
const exportSingleCourse = async () => {
  if (!selectedCourseId.value) return
  
  downloading.value = true
  try {
    const blob = await courseExportService.exportCourse(selectedCourseId.value, exportOptions.value)
    const courseName = courses.value.find(c => c.id === selectedCourseId.value)?.name || '课程'
    courseExportService.downloadFile(blob, `${courseName}_导出.json`)
    toast.success('课程导出成功')
  } catch (error) {
    console.error('Failed to export course:', error)
    toast.error('课程导出失败')
  } finally {
    downloading.value = false
  }
}

// 导出所有课程
const exportAllCourses = async () => {
  downloading.value = true
  try {
    const blob = await courseExportService.exportAllCourses(exportOptions.value)
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    courseExportService.downloadFile(blob, `完整课程体系导出_${timestamp}.json`)
    toast.success('所有课程导出成功')
  } catch (error) {
    console.error('Failed to export all courses:', error)
    toast.error('课程导出失败')
  } finally {
    downloading.value = false
  }
}

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
    filePreview.value = null
    importResult.value = null
  }
}

// 预览文件
const previewFile = async () => {
  if (!selectedFile.value) return
  
  previewing.value = true
  try {
    const preview = await courseExportService.previewImportFile(selectedFile.value)
    filePreview.value = preview
    toast.success('文件预览成功')
  } catch (error) {
    console.error('Failed to preview file:', error)
    toast.error('文件预览失败')
  } finally {
    previewing.value = false
  }
}

// 导入课程
const importCourses = async () => {
  if (!selectedFile.value) return
  
  importing.value = true
  try {
    const result = await courseExportService.importCourses(selectedFile.value, importOptions.value)
    importResult.value = result
    
    if (result.summary.total_errors === 0) {
      toast.success('课程导入成功')
    } else {
      toast.warning(`导入完成，但有 ${result.summary.total_errors} 个错误`)
    }
    
    // 重新加载课程列表
    await loadCourses()
  } catch (error) {
    console.error('Failed to import courses:', error)
    toast.error('课程导入失败')
  } finally {
    importing.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.course-export-import {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 2rem;
}

.export-section,
.import-section {
  margin-bottom: 2rem;
}

/* 自定义滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
