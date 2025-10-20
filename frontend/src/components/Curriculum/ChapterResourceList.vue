<template>
  <div class="resource-list">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载资源中...</span>
    </div>

    <!-- Resource List -->
    <div v-else-if="resources.length > 0" class="resources">
      <div v-for="resource in resources" :key="resource.id" class="resource-item">
        <div class="resource-icon">
          <span v-if="resource.resource_type === 'pdf'">📄</span>
          <span v-else-if="resource.resource_type === 'video'">🎥</span>
          <span v-else-if="resource.resource_type === 'document'">📃</span>
          <span v-else>🔗</span>
        </div>
        
        <div class="resource-info">
          <div class="resource-title">
            {{ resource.title }}
            <span v-if="resource.is_official" class="official-badge">官方</span>
          </div>
          <div class="resource-meta">
            <span v-if="resource.file_size" class="meta-item">
              {{ formatFileSize(resource.file_size) }}
            </span>
            <span v-if="resource.page_count" class="meta-item">
              {{ resource.page_count }} 页
            </span>
            <span class="meta-item">
              {{ formatDate(resource.created_at) }}
            </span>
            <span v-if="resource.download_count > 0" class="meta-item">
              下载 {{ resource.download_count }} 次
            </span>
          </div>
          <div v-if="resource.description" class="resource-desc">
            {{ resource.description }}
          </div>
        </div>

        <div class="resource-actions">
          <button
            v-if="resource.is_downloadable"
            @click="handleDownload(resource)"
            class="action-btn action-btn-primary"
            title="下载资源"
          >
            <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            下载
          </button>
          <button
            @click="handleView(resource)"
            class="action-btn action-btn-secondary"
            title="查看详情"
          >
            <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            查看
          </button>
          <button
            v-if="canDelete"
            @click="handleDelete(resource)"
            class="action-btn action-btn-danger"
            title="删除资源"
          >
            <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
      <p class="empty-text">暂无资源</p>
      <p class="empty-hint">点击上方"上传"按钮添加资源</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { resourceService } from '@/services/resource'
import { useToast } from '@/composables/useToast'
import type { ResourceResponse } from '@/types/resource'

interface Props {
  chapterId: number
  canDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canDelete: true
})

const emit = defineEmits<{
  view: [resource: ResourceResponse]
  refresh: []
}>()

const toast = useToast()
const loading = ref(false)
const resources = ref<ResourceResponse[]>([])

// 加载资源列表
async function loadResources() {
  if (!props.chapterId) return
  
  loading.value = true
  try {
    resources.value = await resourceService.listResources({ chapter_id: props.chapterId })
  } catch (error: any) {
    console.error('Failed to load resources:', error)
    toast.error('加载资源失败')
  } finally {
    loading.value = false
  }
}

// 下载资源
async function handleDownload(resource: ResourceResponse) {
  try {
    const result = await resourceService.downloadResource(resource.id)
    
    // 直接使用后端返回的完整文件名（已包含扩展名）
    const fullFilename = result.filename || resource.title
    
    // 构建完整的下载URL（确保使用正确的后端地址）
    const baseURL = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'
    const fullDownloadUrl = `${baseURL}${result.download_url}`
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = fullDownloadUrl
    link.download = fullFilename
    link.target = '_blank' // 在新窗口中打开，避免跨域警告
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    toast.success('开始下载')
    
  } catch (error: any) {
    console.error('Failed to download resource:', error)
    toast.error('下载失败，请重试')
  }
  
  // 刷新列表（更新下载次数）- 移到try-catch外面，避免影响下载成功提示
  try {
    await loadResources()
  } catch (error) {
    console.error('Failed to refresh resource list:', error)
    // 不显示toast，因为下载已经成功了
  }
}

// 查看资源
function handleView(resource: ResourceResponse) {
  emit('view', resource)
}

// 删除资源
async function handleDelete(resource: ResourceResponse) {
  // 使用 confirm 作为临时解决方案，后续可以改为自定义确认对话框
  if (!confirm(`确定要删除资源"${resource.title}"吗？此操作不可撤销。`)) {
    return
  }
  
  try {
    await resourceService.deleteResource(resource.id)
    toast.success('资源删除成功')
    
    // 刷新列表
    loadResources()
    emit('refresh')
  } catch (error: any) {
    console.error('Failed to delete resource:', error)
    toast.error(error.response?.data?.detail || '删除失败')
  }
}

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN')
}

// 监听 chapterId 变化
watch(() => props.chapterId, () => {
  loadResources()
}, { immediate: true })

// 暴露刷新方法
defineExpose({
  refresh: loadResources
})
</script>

<style scoped>
.resource-list {
  padding: 0.5rem 0;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.resources {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.resource-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.resource-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.resource-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: #111827;
  margin-bottom: 0.25rem;
}

.official-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.resource-desc {
  font-size: 0.813rem;
  color: #6b7280;
  margin-top: 0.375rem;
  line-height: 1.5;
}

.resource-actions {
  display: flex;
  gap: 0.375rem;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.icon {
  width: 1rem;
  height: 1rem;
}

.action-btn-primary {
  background: #3b82f6;
  color: white;
}

.action-btn-primary:hover {
  background: #2563eb;
}

.action-btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.action-btn-secondary:hover {
  background: #f9fafb;
}

.action-btn-danger {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn-danger:hover {
  background: #fecaca;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  width: 3rem;
  height: 3rem;
  color: #d1d5db;
  margin-bottom: 0.75rem;
}

.empty-text {
  font-size: 0.938rem;
  color: #6b7280;
  font-weight: 500;
  margin: 0 0 0.25rem;
}

.empty-hint {
  font-size: 0.813rem;
  color: #9ca3af;
  margin: 0;
}
</style>

