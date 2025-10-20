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
            <span class="header-icon">📋</span>
            <h3 class="header-title">{{ resource?.title || 'PDF 预览' }}</h3>
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

        <!-- PDF 内容区 -->
        <div class="modal-body">
          <div v-if="isLoading" class="loading-container">
            <div class="spinner"></div>
            <p class="loading-text">加载PDF中...</p>
          </div>

          <div v-else-if="error" class="error-container">
            <svg class="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="error-message">{{ error }}</p>
            <button @click="loadResource" class="retry-btn">重试</button>
          </div>

          <div v-else-if="pdfUrl" class="pdf-container">
            <iframe
              :src="pdfUrl"
              class="pdf-iframe"
              frameborder="0"
              @load="handleIframeLoad"
            />
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
          </div>
          <div class="footer-right">
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

// PDF URL
const pdfUrl = computed(() => {
  if (!props.resourceId || !resource.value?.file_url) return null
  // 直接使用后端提供的 file_url
  return resource.value.file_url
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

// 加载资源信息
async function loadResource() {
  if (!props.resourceId) return
  
  isLoading.value = true
  error.value = null
  
  try {
    resource.value = await resourceService.getResource(props.resourceId)
  } catch (err: any) {
    error.value = err.message || '加载资源失败'
    console.error('Failed to load resource:', err)
  } finally {
    isLoading.value = false
  }
}

// iframe 加载完成
function handleIframeLoad() {
  console.log('PDF loaded successfully')
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
  flex: 1;
  min-width: 0;
}

.header-icon {
  font-size: 1.5rem;
}

.header-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.header-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #d1d5db;
}

.header-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-btn.btn-primary {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.header-btn.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
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
  overflow: hidden;
  position: relative;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.error-icon {
  width: 3rem;
  height: 3rem;
  color: #ef4444;
}

.error-message {
  margin-top: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #2563eb;
}

.pdf-container {
  width: 100%;
  height: 100%;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
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

.page-info::before {
  content: '📄';
  margin-right: 0.25rem;
}

.file-size::before {
  content: '💾';
  margin-right: 0.25rem;
}

.create-lesson-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.create-lesson-btn:hover {
  background: #2563eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

