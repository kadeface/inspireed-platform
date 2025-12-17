<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="handleClose"
  >
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="handleClose"></div>

    <div class="flex min-h-full items-center justify-center p-4" @click.stop>
      <div class="relative bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] flex flex-col" @click.stop>
        <!-- 头部 -->
        <div class="px-6 pt-6 pb-4 border-b flex-shrink-0">
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
        <div class="px-6 py-4 overflow-y-auto flex-1" @click.stop>
          <form @submit.prevent="handleSubmit" class="space-y-4" @click.stop>
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

            <!-- 上传方式选择 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                上传方式 <span class="text-red-500">*</span>
              </label>
              <div class="flex gap-2 mb-3">
                <button
                  type="button"
                  @click="uploadMode = 'file'"
                  :class="[
                    'flex-1 px-4 py-2 rounded-lg border-2 transition-all',
                    uploadMode === 'file'
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                  ]"
                >
                  <svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  上传文件
                </button>
                <button
                  type="button"
                  @click="uploadMode = 'code'"
                  :class="[
                    'flex-1 px-4 py-2 rounded-lg border-2 transition-all',
                    uploadMode === 'code'
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                  ]"
                >
                  <svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  粘贴HTML代码
                </button>
              </div>
            </div>

            <!-- 文件上传 -->
            <div v-if="uploadMode === 'file'">
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

            <!-- HTML代码输入 -->
            <div v-if="uploadMode === 'code'">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                HTML代码 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="htmlCode"
                rows="12"
                placeholder="粘贴或输入HTML代码..."
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900 placeholder:text-gray-400 font-mono text-sm"
                @input="handleHtmlCodeChange"
                @paste="handlePaste"
              ></textarea>
              <p class="mt-1 text-xs text-gray-500">
                从AI生成的代码直接粘贴到这里，系统会自动处理为HTML文件
              </p>
              <div v-if="htmlCode.trim()" class="mt-2 flex items-center gap-2">
                <button
                  type="button"
                  @click="previewHtmlCode"
                  class="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  预览
                </button>
                <button
                  type="button"
                  @click="clearHtmlCode"
                  class="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  清空
                </button>
                <span class="text-xs text-gray-500">
                  代码长度: {{ htmlCode.length }} 字符
                </span>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">学科分类</label>
              <select
                v-model="formData.subject_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white text-gray-900"
                @change="handleSubjectChange"
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

            <!-- 知识点分类选择器（仅当选择数学学科时显示） -->
            <div v-if="isMathSubject">
              <KnowledgePointSelector
                v-model="knowledgePointData"
              />
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
        <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3 flex-shrink-0 border-t">
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
import { ref, computed, onMounted, watch } from 'vue'
import { libraryService } from '@/services/library'
import { formatFileSize } from '@/types/library'
import { curriculumService } from '@/services/curriculum'
import type { Subject, Grade } from '@/types/curriculum'
import KnowledgePointSelector from './KnowledgePointSelector.vue'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  success: []
}>()

const uploading = ref(false)
const uploadMode = ref<'file' | 'code'>('file')
const selectedFile = ref<File | null>(null)
const htmlCode = ref<string>('')
const fileInput = ref<HTMLInputElement>()
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const loadingSubjects = ref(false)
const loadingGrades = ref(false)

// 切换上传模式时清理另一个模式的数据
watch(uploadMode, (newMode) => {
  if (newMode === 'file') {
    htmlCode.value = ''
  } else {
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
})

const formData = ref({
  title: '',
  description: '',
  visibility: 'school',
  subject_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
})

const knowledgePointData = ref<{
  category?: string
  name?: string
}>({})

// 检查是否选择了数学学科
const isMathSubject = computed(() => {
  if (!formData.value.subject_id) return false
  const mathSubject = subjects.value.find(s => s.id === formData.value.subject_id)
  return mathSubject?.name === '数学' || mathSubject?.name?.includes('数学')
})

const canSubmit = computed(() => {
  if (!formData.value.title.trim()) return false
  if (uploadMode.value === 'file') {
    return selectedFile.value !== null
  } else {
    return htmlCode.value.trim().length > 0
  }
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

// 处理HTML代码变化
const handleHtmlCodeChange = () => {
  // 可以在这里添加实时验证
}

// 处理粘贴事件
const handlePaste = (event: ClipboardEvent) => {
  // 粘贴后自动处理
  setTimeout(() => {
    // 确保HTML代码完整
    ensureHtmlComplete()
  }, 100)
}

// 确保HTML代码完整
const ensureHtmlComplete = () => {
  if (!htmlCode.value.trim()) return
  
  let code = htmlCode.value.trim()
  
  // 如果代码不包含完整的HTML结构，自动包装
  if (!code.includes('<!DOCTYPE') && !code.includes('<html')) {
    if (!code.includes('<head>')) {
      const title = formData.value.title || '交互式课件'
      code = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
</head>
<body>
${code}
</body>
</html>`
      htmlCode.value = code
    }
  }
}

// 预览HTML代码
const previewHtmlCode = () => {
  if (!htmlCode.value.trim()) {
    alert('请先输入HTML代码')
    return
  }
  
  ensureHtmlComplete()
  
  const blob = new Blob([htmlCode.value], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
  
  // 清理URL（延迟清理，确保窗口打开）
  setTimeout(() => {
    URL.revokeObjectURL(url)
  }, 1000)
}

// 清空HTML代码
const clearHtmlCode = () => {
  htmlCode.value = ''
}

// 将HTML代码转换为File对象
const htmlCodeToFile = (code: string, filename: string = 'interactive-courseware.html'): File => {
  const blob = new Blob([code], { type: 'text/html' })
  return new File([blob], filename, { type: 'text/html' })
}

const formatSize = (bytes: number) => formatFileSize(bytes)

// 处理学科变化
const handleSubjectChange = () => {
  // 当学科改变时，重置知识点数据
  if (!isMathSubject.value) {
    knowledgePointData.value = {}
  }
}

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
    visibility: 'school',
    subject_id: undefined,
    grade_id: undefined,
  }
  knowledgePointData.value = {}
  uploadMode.value = 'file'
  selectedFile.value = null
  htmlCode.value = ''
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
  if (!canSubmit.value) return

  uploading.value = true
  try {
    let fileToUpload: File
    
    if (uploadMode.value === 'file') {
      if (!selectedFile.value) return
      fileToUpload = selectedFile.value
    } else {
      // 粘贴HTML代码模式
      if (!htmlCode.value.trim()) {
        alert('请输入HTML代码')
        uploading.value = false
        return
      }
      
      // 确保HTML代码完整
      ensureHtmlComplete()
      
      // 将HTML代码转换为File对象
      const filename = `${formData.value.title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.html`
      fileToUpload = htmlCodeToFile(htmlCode.value, filename)
    }
    
    await libraryService.uploadAsset(fileToUpload, {
      title: formData.value.title,
      description: formData.value.description || undefined,
      visibility: formData.value.visibility,
      subject_id: formData.value.subject_id,
      grade_id: formData.value.grade_id,
      knowledge_point_category: knowledgePointData.value.category,
      knowledge_point_name: knowledgePointData.value.name,
    })
    
    emit('success')
    // 上传成功后重置表单，避免下次打开时仍显示上一次的内容
    resetForm()
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
