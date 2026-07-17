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
            <h3 class="header-title">{{ displayTitle }}</h3>
          </div>
          <div class="header-actions">
            <button
              v-if="downloadUrl"
              @click="handleDownload"
              class="header-btn"
              title="下载"
            >
              <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span class="btn-text">下载</span>
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

        <!-- 内容预览区 -->
        <div class="modal-body">
          <div v-if="loading" class="loading-container">
            <div class="spinner"></div>
            <p class="loading-text">加载中...</p>
            <p class="loading-hint">如果是Office文档，首次预览可能需要较长时间进行格式转换，请耐心等待</p>
          </div>

          <div v-else-if="error" class="error-container">
            <svg class="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="error-message">{{ error }}</p>
            <div class="error-actions">
              <button @click="loadPreview" class="retry-btn">重试</button>
              <button v-if="downloadUrl" @click="handleDownload" class="retry-btn retry-btn-secondary">下载原文件</button>
            </div>
          </div>

          <!-- PDF预览（含Office转换后的PDF） -->
          <div v-else-if="displayKind === 'pdf'" class="pdf-container">
            <iframe
              :src="previewAbsoluteUrl ?? undefined"
              class="preview-iframe"
              frameborder="0"
            />
          </div>

          <!-- 图片预览 -->
          <div v-else-if="displayKind === 'image'" class="image-container">
            <img
              :src="previewAbsoluteUrl ?? undefined"
              :alt="displayTitle"
              class="preview-image"
              @error="error = '图片加载失败'"
            />
          </div>

          <!-- 不支持在线预览的文件类型 -->
          <div v-else class="other-file-container">
            <div class="other-file-preview">
              <div class="file-icon">
                <svg class="file-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 class="file-title">{{ displayTitle }}</h3>
              <p class="file-description">该文件类型暂不支持在线预览，请下载后查看</p>
              <div class="file-actions">
                <button v-if="downloadUrl" @click="handleDownload" class="file-btn">
                  <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载文件
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useDocumentPreview } from '@/composables/useDocumentPreview'
import { getServerBaseUrl } from '@/utils/url'

interface Props {
  modelValue: boolean
  mode: 'resource' | 'library' | 'file'
  resourceId?: number | null
  assetId?: number | null
  fileUrl?: string | null
  title?: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const { loading, error, info, previewAbsoluteUrl, displayKind, loadFromResource, loadFromLibrary, loadFromFileUrl, reset } = useDocumentPreview()

const displayTitle = computed(() => props.title || info.value?.title || '文档预览')

const fileIcon = computed(() => {
  const ext = info.value?.file_type
  if (!ext) return '📁'
  if (ext === 'pdf') return '📄'
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return '🖼️'
  if (['doc', 'docx'].includes(ext)) return '📝'
  if (['ppt', 'pptx'].includes(ext)) return '📊'
  if (['xls', 'xlsx'].includes(ext)) return '📈'
  return '📁'
})

const downloadUrl = computed(() => {
  let url = info.value?.file_url
  if (!url) return null
  if (url.startsWith('/uploads/')) url = `${getServerBaseUrl()}${url}`
  return url
})

function loadPreview() {
  if (props.mode === 'resource' && props.resourceId) {
    loadFromResource(props.resourceId)
  } else if (props.mode === 'library' && props.assetId) {
    loadFromLibrary(props.assetId)
  } else if (props.mode === 'file' && props.fileUrl) {
    loadFromFileUrl(props.fileUrl)
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    loadPreview()
  } else {
    reset()
  }
})

watch(() => [props.mode, props.resourceId, props.assetId, props.fileUrl], () => {
  if (props.modelValue) loadPreview()
})

function handleDownload() {
  if (!downloadUrl.value) return
  const link = document.createElement('a')
  link.href = downloadUrl.value
  link.download = displayTitle.value
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

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
  margin-bottom: 0.5rem;
}

.loading-hint {
  color: #9ca3af;
  font-size: 0.75rem;
  max-width: 400px;
  text-align: center;
  line-height: 1.5;
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

.error-actions {
  display: flex;
  gap: 0.75rem;
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

.retry-btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
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

.other-file-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.other-file-preview {
  text-align: center;
  max-width: 400px;
}

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

.file-icon-svg {
  width: 2rem;
  height: 2rem;
  color: #6b7280;
}

.file-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem;
}

.file-description {
  color: #6b7280;
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.file-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

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

.file-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
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
