<template>
  <div class="pdf-resource-item">
    <!-- 资源头部 -->
    <div class="resource-header">
      <div class="resource-icon">
        <span class="icon-emoji">{{ resourceIcon }}</span>
      </div>
      <div class="resource-info">
        <h4 class="resource-title">{{ resource.title }}</h4>
        <p v-if="resource.description" class="resource-description">
          {{ resource.description }}
        </p>
        <div class="resource-meta">
          <span v-if="resource.file_size" class="meta-item">
            <svg class="meta-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
              <path fill-rule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clip-rule="evenodd" />
            </svg>
            {{ formatFileSize(resource.file_size) }}
          </span>
          <span v-if="resource.page_count" class="meta-item">
            <svg class="meta-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
            </svg>
            {{ resource.page_count }} 页
          </span>
          <span class="meta-item">
            <svg class="meta-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
            </svg>
            {{ resource.view_count }} 次查看
          </span>
          <span v-if="resource.is_official" class="meta-item official-badge">
            <svg class="meta-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            官方资源
          </span>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="resource-actions">
      <button 
        @click="handlePreview" 
        class="action-btn btn-preview"
        title="预览PDF"
      >
        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <span>预览</span>
      </button>
      
      <button 
        v-if="resource.is_downloadable"
        @click="handleDownload" 
        class="action-btn btn-download"
        title="下载PDF"
        :disabled="isDownloading"
      >
        <svg v-if="!isDownloading" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        <svg v-else class="btn-icon animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ isDownloading ? '下载中...' : '下载' }}</span>
      </button>
      
      <button 
        @click="handleCreateLesson" 
        class="action-btn btn-create"
        title="参考此资源创建教案"
      >
        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <span>创建教案</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Resource } from '../../types/resource'
import { formatFileSize, getResourceTypeIcon } from '../../types/resource'
import { resourceService } from '../../services/resource'
import { useToast } from '@/composables/useToast'
import { getServerBaseUrl } from '@/utils/url'

interface Props {
  resource: Resource
}

const props = defineProps<Props>()

const emit = defineEmits<{
  preview: [resourceId: number]
  'create-lesson': [resourceId: number]
}>()

const toast = useToast()
const isDownloading = ref(false)

// 资源图标
const resourceIcon = computed(() => getResourceTypeIcon(props.resource.resource_type))

// 预览 PDF
function handlePreview() {
  emit('preview', props.resource.id)
}

// 下载资源
async function handleDownload() {
  if (isDownloading.value) return
  
  isDownloading.value = true
  
  try {
    const result = await resourceService.downloadResource(props.resource.id)
    
    // 构建完整的下载URL（确保使用正确的后端地址）
    const baseURL = getServerBaseUrl()
    const fullDownloadUrl = `${baseURL}${result.download_url}`
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = fullDownloadUrl
    link.download = result.filename
    link.target = '_blank' // 避免跨域警告
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    toast.success('开始下载')
  } catch (error) {
    console.error('Download failed:', error)
    toast.error('下载失败，请重试')
  } finally {
    isDownloading.value = false
  }
}

// 创建教案
function handleCreateLesson() {
  emit('create-lesson', props.resource.id)
}
</script>

<style scoped>
.pdf-resource-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s;
}

.pdf-resource-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.resource-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.resource-icon {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-emoji {
  font-size: 1.5rem;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem;
  line-height: 1.5;
}

.resource-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.5rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.meta-icon {
  width: 1rem;
  height: 1rem;
}

.official-badge {
  color: #059669;
  font-weight: 500;
}

.resource-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-preview {
  background: #eff6ff;
  color: #2563eb;
}

.btn-preview:hover:not(:disabled) {
  background: #dbeafe;
}

.btn-download {
  background: #f0fdf4;
  color: #16a34a;
}

.btn-download:hover:not(:disabled) {
  background: #dcfce7;
}

.btn-create {
  background: #fef3c7;
  color: #d97706;
}

.btn-create:hover:not(:disabled) {
  background: #fde68a;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

