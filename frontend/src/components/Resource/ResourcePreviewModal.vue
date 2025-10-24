<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="modal-overlay"
      @click.self="close"
    >
      <div class="modal-container">
        <!-- 模态框头部 -->
        <div class="modal-header">
          <div class="header-left">
            <span class="header-icon">{{ fileIcon }}</span>
            <h3 class="header-title">{{ resource?.title || '资源预览' }}</h3>
          </div>
          <div class="header-actions">
            <button
              v-if="resource?.is_downloadable"
              @click="handleDownload"
              class="header-btn"
              title="下载"
              :disabled="isDownloading"
            >
              <svg v-if="!isDownloading" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <svg v-else class="btn-icon animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </button>
            <button
              v-if="canCreateLesson"
              @click="handleCreateLesson"
              class="header-btn btn-primary"
              title="参考此资源创建教案"
            >
              <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span class="btn-text">创建教案</span>
            </button>
            <button
              @click="close"
              class="header-btn"
              title="关闭"
            >
              <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 资源内容预览区 -->
        <div class="modal-body">
          <div v-if="isLoading" class="loading-container">
            <div class="spinner"></div>
            <p class="loading-text">加载资源中...</p>
          </div>

          <div v-else-if="error" class="error-container">
            <svg class="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="error-message">{{ error }}</p>
            <button @click="loadResource" class="retry-btn">重试</button>
          </div>

          <!-- PDF预览 -->
          <div v-else-if="fileType === 'pdf'" class="pdf-container">
            <iframe
              :src="previewUrl"
              class="preview-iframe"
              frameborder="0"
              @load="handleIframeLoad"
            />
          </div>

          <!-- 图片预览 -->
          <div v-else-if="fileType === 'image'" class="image-container">
            <img
              :src="previewUrl"
              :alt="resource?.title"
              class="preview-image"
              @load="handleImageLoad"
              @error="handleImageError"
            />
          </div>

          <!-- Office文档预览 -->
          <div v-else-if="fileType === 'office'" class="office-container">
            <div class="office-preview">
              <!-- 预览选项标签页 -->
              <div class="preview-tabs">
                <button 
                  @click="activePreviewTab = 'info'"
                  :class="['tab-btn', { active: activePreviewTab === 'info' }]"
                >
                  文件信息
                </button>
                <button 
                  @click="activePreviewTab = 'online'"
                  :class="['tab-btn', { active: activePreviewTab === 'online' }]"
                >
                  在线预览
                </button>
              </div>

              <!-- 文件信息标签页 -->
              <div v-if="activePreviewTab === 'info'" class="tab-content">
                <div class="office-icon">
                  <svg class="office-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="office-title">{{ resource?.title }}</h3>
                <p class="office-description">
                  {{ getOfficeDescription() }}
                </p>
                <div class="office-actions">
                  <button @click="handleDownload" class="office-btn">
                    <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    下载文件
                  </button>
                  <button v-if="canCreateLesson" @click="handleCreateLesson" class="office-btn btn-primary">
                    <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    创建教案
                  </button>
                </div>
              </div>

              <!-- 在线预览标签页 -->
              <div v-if="activePreviewTab === 'online'" class="tab-content">
                <div class="online-preview-options">
                  <!-- 转换后的PDF预览 -->
                  <div v-if="previewInfo?.converted_to_pdf" class="preview-method">
                    <h4 class="method-title">PDF预览</h4>
                    <p class="method-description">
                      已自动转换为PDF格式，可直接在浏览器中预览
                    </p>
                    <button @click="openConvertedPDF" class="preview-btn primary">
                      <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      查看PDF版本
                    </button>
                  </div>

                  <!-- 转换失败提示 -->
                  <div v-else-if="previewInfo?.conversion_error" class="preview-method error">
                    <h4 class="method-title">PDF转换失败</h4>
                    <p class="method-description">
                      {{ previewInfo.conversion_error }}
                    </p>
                    <div class="error-actions">
                      <button @click="retryConversion" class="preview-btn">
                        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        重试转换
                      </button>
                    </div>
                  </div>

                  <!-- 推荐预览方式 -->
                  <div class="preview-method recommended">
                    <h4 class="method-title">推荐预览方式</h4>
                    <p class="method-description">
                      为了获得最佳的预览效果，建议使用以下方式查看文档
                    </p>
                  </div>

                  <div class="preview-method">
                    <h4 class="method-title">Microsoft Office Online</h4>
                    <p class="method-description">
                      使用Microsoft Office Online查看文档，支持编辑和协作
                    </p>
                    <button @click="openOfficeOnline" class="preview-btn">
                      <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      在Office Online中打开
                    </button>
                  </div>

                  <div class="preview-method">
                    <h4 class="method-title">Google Docs Viewer</h4>
                    <p class="method-description">
                      使用Google文档查看器预览文档内容
                    </p>
                    <button @click="openGoogleViewer" class="preview-btn">
                      <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
                      </svg>
                      在Google Viewer中打开
                    </button>
                  </div>

                  <div class="preview-method">
                    <h4 class="method-title">本地应用</h4>
                    <p class="method-description">
                      下载文件并在本地Office应用中打开
                    </p>
                    <button @click="handleDownload" class="preview-btn">
                      <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      下载并在本地打开
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 其他文件类型 -->
          <div v-else class="other-file-container">
            <div class="other-file-preview">
              <div class="file-icon">
                <svg class="file-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 class="file-title">{{ resource?.title }}</h3>
              <p class="file-description">
                文件类型：{{ fileExtension.toUpperCase() }}
              </p>
              <div class="file-actions">
                <button @click="handleDownload" class="file-btn">
                  <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载文件
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部工具栏 -->
        <div v-if="!isLoading && !error" class="modal-footer">
          <div class="footer-left">
            <span v-if="resource?.page_count" class="page-info">
              共 {{ resource.page_count }} 页
            </span>
            <span v-if="resource?.file_size" class="file-size">
              {{ formatFileSize(resource.file_size) }}
            </span>
            <span class="file-type">
              {{ fileExtension.toUpperCase() }}
            </span>
          </div>
          <div v-if="canCreateLesson" class="footer-right">
            <button
              @click="handleCreateLesson"
              class="create-lesson-btn"
            >
              <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              参考此资源创建教案
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Resource } from '../../types/resource'
import { formatFileSize } from '../../types/resource'
import { resourceService } from '../../services/resource'

interface Props {
  modelValue: boolean
  resourceId: number | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'create-lesson': [resourceId: number]
}>()

const resource = ref<Resource | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const isDownloading = ref(false)
const activePreviewTab = ref('info')

// 文件扩展名
const fileExtension = computed(() => {
  if (!resource.value?.file_url) return ''
  const url = resource.value.file_url
  const lastDot = url.lastIndexOf('.')
  return lastDot > -1 ? url.substring(lastDot + 1).toLowerCase() : ''
})

// 文件类型
const fileType = computed(() => {
  const ext = fileExtension.value
  if (ext === 'pdf') return 'pdf'
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return 'image'
  if (['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(ext)) return 'office'
  return 'other'
})

// 文件图标
const fileIcon = computed(() => {
  const ext = fileExtension.value
  if (ext === 'pdf') return '📄'
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return '🖼️'
  if (['doc', 'docx'].includes(ext)) return '📝'
  if (['ppt', 'pptx'].includes(ext)) return '📊'
  if (['xls', 'xlsx'].includes(ext)) return '📈'
  return '📁'
})

// 预览URL
const previewUrl = computed(() => {
  // 优先使用转换后的PDF URL
  let url = previewInfo.value?.preview_url || resource.value?.file_url
  if (!url) return null
  
  if (url.startsWith('/uploads/')) {
    const baseURL = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
    url = `${baseURL}${url}`
  }
  
  return url
})

// 是否可以创建教案
const canCreateLesson = computed(() => {
  return fileType.value === 'pdf' || fileType.value === 'office'
})

// 监听 resourceId 变化
watch(() => props.resourceId, (newId) => {
  if (newId && props.modelValue) {
    loadResource()
  }
}, { immediate: true })

// 监听模态框打开
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.resourceId) {
    loadResource()
  }
})

// 预览信息
const previewInfo = ref<any>(null)

// 加载资源信息
async function loadResource() {
  if (!props.resourceId) return
  
  isLoading.value = true
  error.value = null
  
  try {
    // 获取基本资源信息
    resource.value = await resourceService.getResource(props.resourceId)
    
    // 获取预览信息（包括Office文档转换）
    previewInfo.value = await resourceService.getResourcePreview(props.resourceId)
  } catch (err: any) {
    error.value = err.message || '加载资源失败'
    console.error('Failed to load resource:', err)
  } finally {
    isLoading.value = false
  }
}

// 获取Office文档描述
function getOfficeDescription() {
  const ext = fileExtension.value
  if (['doc', 'docx'].includes(ext)) {
    return 'Microsoft Word 文档，建议下载后在本地查看'
  }
  if (['ppt', 'pptx'].includes(ext)) {
    return 'Microsoft PowerPoint 演示文稿，建议下载后在本地查看'
  }
  if (['xls', 'xlsx'].includes(ext)) {
    return 'Microsoft Excel 电子表格，建议下载后在本地查看'
  }
  return 'Office 文档，建议下载后在本地查看'
}

// iframe 加载完成
function handleIframeLoad() {
  console.log('PDF loaded successfully')
}

// 图片加载完成
function handleImageLoad() {
  console.log('Image loaded successfully')
}

// 图片加载失败
function handleImageError() {
  error.value = '图片加载失败'
}

// 下载资源
async function handleDownload() {
  if (!props.resourceId || isDownloading.value) return
  
  isDownloading.value = true
  
  try {
    const result = await resourceService.downloadResource(props.resourceId)
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = result.download_url
    link.download = result.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Download failed:', error)
    alert('下载失败，请重试')
  } finally {
    isDownloading.value = false
  }
}

// 创建教案
function handleCreateLesson() {
  if (!props.resourceId) return
  emit('create-lesson', props.resourceId)
  close()
}

// 打开Microsoft Office Online
function openOfficeOnline() {
  if (!previewUrl.value) return
  
  // Microsoft Office Online URL格式
  const officeOnlineUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(previewUrl.value)}`
  window.open(officeOnlineUrl, '_blank')
}

// 打开转换后的PDF
function openConvertedPDF() {
  if (!previewInfo.value?.preview_url) return
  
  let url = previewInfo.value.preview_url
  if (url.startsWith('/uploads/')) {
    const baseURL = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
    url = `${baseURL}${url}`
  }
  
  window.open(url, '_blank')
}

// 打开Google Docs Viewer
function openGoogleViewer() {
  if (!previewUrl.value) return
  
  // Google Docs Viewer URL格式
  const googleViewerUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(previewUrl.value)}&embedded=true`
  window.open(googleViewerUrl, '_blank')
}

// 重试转换
async function retryConversion() {
  if (!props.resourceId) return
  
  try {
    // 重新加载预览信息
    previewInfo.value = await resourceService.getResourcePreview(props.resourceId)
  } catch (error) {
    console.error('重试转换失败:', error)
  }
}

// 关闭模态框
function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 1200px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  font-size: 1.5rem;
}

.header-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.header-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.header-btn.btn-primary {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.header-btn.btn-primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

.btn-text {
  display: none;
}

@media (min-width: 640px) {
  .btn-text {
    display: inline;
  }
}

.modal-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: #6b7280;
  font-size: 0.875rem;
}

.error-icon {
  width: 3rem;
  height: 3rem;
  color: #ef4444;
}

.error-message {
  color: #6b7280;
  text-align: center;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.pdf-container,
.image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0.375rem;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.office-container,
.other-file-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

/* 预览标签页样式 */
.preview-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: #374151;
  background: #f9fafb;
}

.tab-btn.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  text-align: center;
}

/* 在线预览选项样式 */
.online-preview-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 600px;
  margin: 0 auto;
}

.preview-method {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: #f9fafb;
  text-align: left;
}

.preview-method.error {
  border-color: #fca5a5;
  background: #fef2f2;
}

.preview-method.error .method-title {
  color: #dc2626;
}

.preview-method.recommended {
  border-color: #10b981;
  background: #f0fdf4;
}

.preview-method.recommended .method-title {
  color: #059669;
}

.error-actions {
  margin-top: 1rem;
}

.method-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem;
}

.method-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 1rem;
  line-height: 1.5;
}

.preview-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preview-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.preview-btn.primary {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.preview-btn.primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.office-preview,
.other-file-preview {
  text-align: center;
  max-width: 400px;
}

.office-icon,
.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  background: #f3f4f6;
  border-radius: 50%;
}

.office-icon-svg,
.file-icon-svg {
  width: 2rem;
  height: 2rem;
  color: #6b7280;
}

.office-title,
.file-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem;
}

.office-description,
.file-description {
  color: #6b7280;
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.office-actions,
.file-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.office-btn,
.file-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.office-btn:hover,
.file-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.office-btn.btn-primary,
.file-btn.btn-primary {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.office-btn.btn-primary:hover,
.file-btn.btn-primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.page-info,
.file-size,
.file-type {
  padding: 0.25rem 0.5rem;
  background: white;
  border-radius: 0.25rem;
  border: 1px solid #e5e7eb;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.create-lesson-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.create-lesson-btn:hover {
  background: #2563eb;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
