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

        <!-- 导入说明 -->
        <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 class="text-sm font-semibold text-blue-900 mb-2">📋 导入说明</h4>
          <ul class="text-sm text-blue-800 space-y-1">
            <li>• 支持导入JSON或ZIP格式的课程数据文件</li>
            <li>• 可以导入其他教师编写的教案（包含在课程导出文件中）</li>
            <li>• 导入的教案会自动关联到对应的课程和章节</li>
            <li>• 导入的教案状态将设置为"已发布"（共享状态）</li>
            <li>• 如果文件包含资源文件（图片、PDF等），请使用ZIP格式</li>
          </ul>
        </div>

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
              accept=".json,.zip"
              @change="handleFileSelect"
              class="hidden"
            >
            <button
              @click="() => { const input = $refs.fileInput as HTMLInputElement; input?.click(); }"
              class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              选择文件 (JSON/ZIP)
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
        <div v-if="importResult && importResult.summary && importResult.result" class="mb-4">
          <h4 class="text-md font-medium text-gray-800 mb-2">导入结果</h4>
          <div class="bg-gray-50 rounded-md p-4">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ importResult.summary?.total_created ?? 0 }}</div>
                <div class="text-sm text-gray-600">成功创建</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-yellow-600">{{ importResult.summary?.total_skipped ?? 0 }}</div>
                <div class="text-sm text-gray-600">跳过重复</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ importResult.summary?.total_errors ?? 0 }}</div>
                <div class="text-sm text-gray-600">错误数量</div>
              </div>
            </div>
            
            <!-- 详细统计 -->
            <div v-if="importResult.result" class="mt-4 border-t pt-4">
              <h5 class="text-sm font-medium text-gray-700 mb-2">详细统计:</h5>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                <div>
                  <span class="text-gray-600">课程:</span>
                  <span class="ml-2 font-semibold text-blue-600">
                    +{{ importResult.result.courses?.created ?? 0 }} 
                    <span v-if="importResult.result.courses?.skipped > 0" class="text-yellow-600">
                      (跳过{{ importResult.result.courses?.skipped }})
                    </span>
                  </span>
                </div>
                <div>
                  <span class="text-gray-600">章节:</span>
                  <span class="ml-2 font-semibold text-purple-600">
                    +{{ importResult.result.chapters?.created ?? 0 }}
                    <span v-if="importResult.result.chapters?.skipped > 0" class="text-yellow-600">
                      (跳过{{ importResult.result.chapters?.skipped }})
                    </span>
                  </span>
                </div>
                <div>
                  <span class="text-gray-600">教案:</span>
                  <span class="ml-2 font-semibold text-orange-600">
                    +{{ importResult.result.lessons?.created ?? 0 }}
                    <span v-if="importResult.result.lessons?.skipped > 0" class="text-yellow-600">
                      (跳过{{ importResult.result.lessons?.skipped }})
                    </span>
                  </span>
                </div>
                <div>
                  <span class="text-gray-600">资源:</span>
                  <span class="ml-2 font-semibold text-green-600">
                    +{{ importResult.result.resources?.created ?? 0 }}
                    <span v-if="importResult.result.resources?.skipped > 0" class="text-yellow-600">
                      (跳过{{ importResult.result.resources?.skipped }})
                    </span>
                  </span>
                </div>
              </div>
            </div>
            
            <div v-if="importResult.result?.errors && importResult.result.errors.length > 0" class="mt-4">
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
    
    if (result.summary.total_errors === 0) {
      toast.success('课程导入成功')
    } else {
      toast.warning(`导入完成，但有 ${result.summary.total_errors} 个错误`)
    }
    
    // 重新加载课程列表
    await loadCourses()
  } catch (error: any) {
    console.error('Failed to import courses:', error)
    console.error('Error response:', error.response)
    console.error('Error data:', error.response?.data)
    console.error('Error detail:', error.response?.data?.detail)
    
    // 强制输出完整的错误信息
    let errorDetail = ''
    if (error.response?.data) {
      console.error('=== 完整错误信息 ===')
      console.error(JSON.stringify(error.response.data, null, 2))
      console.error('=== 错误详情 ===')
      if (error.response.data.detail) {
        errorDetail = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail)
        console.error('Detail:', errorDetail)
      }
      if (error.response.data.message) {
        console.error('Message:', error.response.data.message)
      }
    }
    
    // 提取详细的错误信息
    let errorMessage = '课程导入失败'
    
    if (error.response?.data) {
      // FastAPI 错误格式：{ detail: "错误信息" }
      if (error.response.data.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = `导入失败: ${error.response.data.detail}`
        } else if (Array.isArray(error.response.data.detail)) {
          // 处理验证错误数组
          const errors = error.response.data.detail.map((err: any) => {
            if (err.loc && err.msg) {
              return `${err.loc.join('.')}: ${err.msg}`
            }
            return err.msg || err
          })
          errorMessage = `导入失败: ${errors.join('; ')}`
        } else {
          errorMessage = `导入失败: ${JSON.stringify(error.response.data.detail)}`
        }
      } else if (error.response.data.message) {
        errorMessage = `导入失败: ${error.response.data.message}`
      } else if (typeof error.response.data === 'string') {
        errorMessage = `导入失败: ${error.response.data}`
      } else {
        errorMessage = `导入失败: ${JSON.stringify(error.response.data)}`
      }
    } else if (error.message) {
      errorMessage = `导入失败: ${error.message}`
    }
    
    // 显示错误信息
    toast.error(errorMessage)
    
    // 如果是开发环境，也显示详细的错误信息
    if (import.meta.env.DEV && errorDetail) {
      console.error('详细错误信息:', errorDetail)
    }
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
