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
              添加资源到章节
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
          
          <!-- 章节信息 -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div class="flex items-center">
              <span class="text-blue-600 mr-2">📖</span>
              <div>
                <h4 class="font-medium text-blue-900">{{ chapter?.name }}</h4>
                <p class="text-sm text-blue-700">{{ chapter?.description || '暂无描述' }}</p>
              </div>
            </div>
          </div>

          <!-- Tab 切换 -->
          <div class="flex border-b border-gray-200 mb-4">
            <button
              @click="activeTab = 'upload'"
              :class="[
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'upload'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              上传文件
            </button>
            <button
              @click="activeTab = 'library'"
              :class="[
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'library'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              从资源库选择
            </button>
          </div>
        </div>

        <!-- 内容区 -->
        <div class="bg-white px-6 pb-6">
          <!-- 上传文件 Tab -->
          <form v-if="activeTab === 'upload'" @submit.prevent="handleSubmit" class="space-y-4">
            <!-- 资源标题 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源标题 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.title"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入资源标题"
                :disabled="loading"
                required
              />
            </div>

            <!-- 资源描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源描述
              </label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入资源描述"
                :disabled="loading"
              ></textarea>
            </div>

            <!-- 文件上传 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择文件 <span class="text-red-500">*</span>
              </label>
              <div
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleFileDrop"
                :class="[
                  'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
                  isDragging
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                ]"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.jpg,.jpeg,.png,.gif,.mp4,.mp3,.zip,.rar"
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
                      type="button"
                    >
                      点击选择文件
                    </button>
                  </p>
                  <p class="mt-1 text-xs text-gray-500">
                    支持 PDF、Word、PPT、Excel、图片、视频等格式
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
                    type="button"
                  >
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- 资源类型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源类型
              </label>
              <select
                v-model="formData.resource_type"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :disabled="loading"
              >
                <option value="document">文档</option>
                <option value="video">视频</option>
                <option value="audio">音频</option>
                <option value="image">图片</option>
                <option value="archive">压缩包</option>
                <option value="other">其他</option>
              </select>
            </div>
          </form>

          <!-- 从资源库选择 Tab -->
          <div v-else-if="activeTab === 'library'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源标题（可选，默认使用资产标题）
              </label>
              <input
                v-model="libraryFormData.title"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="留空则使用资产标题"
                :disabled="loading"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源描述（可选）
              </label>
              <textarea
                v-model="libraryFormData.description"
                rows="2"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="留空则使用资产描述"
                :disabled="loading"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择资源 <span class="text-red-500">*</span>
              </label>
              <AssetPicker ref="assetPicker" @select="handleAssetSelect" />
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
            v-if="activeTab === 'upload'"
            @click="handleSubmit"
            :disabled="!canUpload || loading"
            class="px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              上传中...
            </span>
            <span v-else>上传资源</span>
          </button>
          <button
            v-else-if="activeTab === 'library'"
            @click="handleLibrarySubmit"
            :disabled="!canSubmitFromLibrary || loading"
            class="px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              创建中...
            </span>
            <span v-else>引用资源</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import resourceService from '@/services/resource'
import type { Chapter } from '@/types/curriculum'
import type { LibraryAssetSummary } from '@/types/library'
import AssetPicker from '@/components/Library/AssetPicker.vue'

interface Props {
  isOpen: boolean
  chapter?: Chapter | null
}

interface ResourceFormData {
  title: string
  description: string
  resource_type: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
  'success': [resourceId: number]
}>()

const loading = ref(false)
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement>()
const activeTab = ref<'upload' | 'library'>('upload')
const selectedAsset = ref<LibraryAssetSummary | null>(null)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()

const formData = ref<ResourceFormData>({
  title: '',
  description: '',
  resource_type: 'document'
})

const libraryFormData = ref({
  title: '',
  description: '',
})

const canUpload = computed(() => {
  return formData.value.title.trim() && selectedFile.value !== null
})

const canSubmitFromLibrary = computed(() => {
  return selectedAsset.value !== null
})

// 监听章节变化，重置表单
watch(() => props.chapter, (newChapter) => {
  if (newChapter) {
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  formData.value = {
    title: '',
    description: '',
    resource_type: 'document'
  }
  libraryFormData.value = {
    title: '',
    description: '',
  }
  selectedFile.value = null
  selectedAsset.value = null
  isDragging.value = false
  activeTab.value = 'upload'
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function handleAssetSelect(asset: LibraryAssetSummary | null) {
  selectedAsset.value = asset
}

function handleClose() {
  if (!loading.value) {
    resetForm()
    emit('close')
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    selectedFile.value = file
    // 自动使用文件名（去掉扩展名）作为资源标题
    if (!formData.value.title.trim()) {
      formData.value.title = file.name.replace(/\.[^/.]+$/, '')
    }
  }
}

function handleFileDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    selectedFile.value = file
    // 自动使用文件名（去掉扩展名）作为资源标题
    if (!formData.value.title.trim()) {
      formData.value.title = file.name.replace(/\.[^/.]+$/, '')
    }
  }
}

function clearFile() {
  selectedFile.value = null
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

async function handleSubmit() {
  if (!canUpload.value || !props.chapter || !selectedFile.value) return
  
  loading.value = true
  try {
    console.log('开始上传资源:', {
      chapterId: props.chapter.id,
      title: formData.value.title,
      description: formData.value.description,
      resourceType: formData.value.resource_type,
      file: selectedFile.value?.name
    })
    
    const resourceId = await resourceService.uploadResourceToChapter(
      props.chapter.id,
      selectedFile.value,
      formData.value.title,
      formData.value.description,
      formData.value.resource_type
    )
    
    console.log('上传成功，资源ID:', resourceId)
    emit('success', resourceId)
    handleClose()
  } catch (error: any) {
    console.error('上传失败，详细错误:', error)
    console.error('错误响应:', error.response)
    console.error('错误详情:', error.response?.data)
    console.error('错误详情数组内容:', error.response?.data?.detail)
    if (error.response?.data?.detail && Array.isArray(error.response.data.detail)) {
      error.response.data.detail.forEach((item, index) => {
        console.error(`错误详情[${index}]:`, item)
      })
    }
    
    // 显示详细的错误信息
    let errorMessage = '上传失败，请稍后重试'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.detail) {
        // 处理FastAPI的验证错误格式
        if (Array.isArray(error.response.data.detail)) {
          const errors = error.response.data.detail.map((err: any) => {
            if (err.loc && err.msg) {
              return `${err.loc.join('.')}: ${err.msg}`
            }
            return err.msg || err
          })
          errorMessage = errors.join('\n')
        } else {
          errorMessage = error.response.data.detail
        }
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message
      } else {
        errorMessage = JSON.stringify(error.response.data)
      }
    }
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

async function handleLibrarySubmit() {
  if (!canSubmitFromLibrary.value || !props.chapter || !selectedAsset.value) return
  
  loading.value = true
  try {
    console.log('开始引用资源库资产:', {
      chapterId: props.chapter.id,
      assetId: selectedAsset.value.id,
      title: libraryFormData.value.title || selectedAsset.value.title,
      description: libraryFormData.value.description,
    })
    
    const resourceId = await resourceService.createResourceFromAsset(
      props.chapter.id,
      selectedAsset.value.id,
      libraryFormData.value.title || selectedAsset.value.title,
      libraryFormData.value.description
    )
    
    console.log('引用成功，资源ID:', resourceId)
    emit('success', resourceId)
    handleClose()
  } catch (error: any) {
    console.error('引用失败，详细错误:', error)
    
    let errorMessage = '引用失败，请稍后重试'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.detail) {
        if (Array.isArray(error.response.data.detail)) {
          const errors = error.response.data.detail.map((err: any) => {
            if (err.loc && err.msg) {
              return `${err.loc.join('.')}: ${err.msg}`
            }
            return err.msg || err
          })
          errorMessage = errors.join('\n')
        } else {
          errorMessage = error.response.data.detail
        }
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message
      }
    }
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 可选：添加一些自定义样式 */
</style>
