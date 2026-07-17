<template>
  <div
    class="reference-material-cell"
    :contenteditable="editable ? 'false' : undefined"
  >
    <!-- 编辑态：空素材 → 上传 / 资源库 -->
    <div v-if="editable && !hasFile" class="reference-empty-state">
      <div class="empty-icon">📎</div>
      <h3 class="empty-title">参考素材</h3>
      <p class="empty-hint">上传 PDF / Word / PPT / Excel / Markdown，或从资源库选择</p>

      <div class="empty-actions">
        <button
          type="button"
          class="reference-button primary"
          :disabled="isUploading"
          @click="triggerUpload"
        >
          {{ isUploading ? `上传中 ${uploadProgress}%` : '上传文档' }}
        </button>
        <button
          type="button"
          class="reference-button"
          :disabled="isUploading"
          @click="openLibraryPicker"
        >
          从资源库选择
        </button>
      </div>

      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.md,.markdown,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/markdown,text/plain"
        @change="onFileSelected"
      />
    </div>

    <!-- 已有素材卡片 -->
    <div v-else class="reference-card">
      <div class="reference-body">
        <div class="reference-icon">
          <span class="text-2xl">{{ icon }}</span>
        </div>
        <div class="reference-info">
          <h3 class="reference-title">
            参考素材：{{ safeTitle }}
          </h3>
          <p class="reference-meta">
            类型：{{ typeLabel }}
            <span v-if="formattedUpdatedAt" class="reference-updated">
              · 更新：{{ formattedUpdatedAt }}
            </span>
          </p>
          <p class="reference-summary">
            {{ summaryText }}
          </p>
          <p v-if="cell.content.source_lesson_title" class="reference-source">
            来源教案：{{ cell.content.source_lesson_title }}
          </p>
          <div v-if="cell.content.tags?.length" class="reference-tags">
            <span
              v-for="tag in cell.content.tags.slice(0, 4)"
              :key="tag"
              class="reference-tag"
            >
              {{ tag }}
            </span>
            <span v-if="cell.content.tags.length > 4" class="reference-tag more">
              +{{ cell.content.tags.length - 4 }}
            </span>
          </div>
        </div>
      </div>

      <div class="reference-actions">
        <button
          type="button"
          class="reference-button primary"
          :disabled="!previewUrl && !downloadUrl"
          @click="handlePreview"
        >
          预览素材
        </button>
        <button
          type="button"
          class="reference-button"
          :disabled="!downloadUrl"
          @click="handleDownload"
        >
          下载素材
        </button>
        <template v-if="editable">
          <button
            type="button"
            class="reference-button"
            :disabled="isUploading"
            @click="triggerUpload"
          >
            {{ isUploading ? `上传中 ${uploadProgress}%` : '更换文件' }}
          </button>
          <button
            type="button"
            class="reference-button"
            :disabled="isUploading"
            @click="openLibraryPicker"
          >
            资源库
          </button>
        </template>
      </div>

      <p v-if="!previewUrl && !downloadUrl" class="reference-empty">
        暂无可用的预览或下载链接。
      </p>

      <input
        v-if="editable"
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.md,.markdown,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/markdown,text/plain"
        @change="onFileSelected"
      />
    </div>

    <DocumentPreviewModal
      v-model="showDocPreview"
      mode="file"
      :file-url="docPreviewFileUrl"
      :title="safeTitle"
    />

    <!-- 资源库选择 -->
    <teleport to="body">
      <div
        v-if="showLibraryPicker"
        class="fixed inset-0 z-[60] overflow-y-auto"
        @click.self="showLibraryPicker = false"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showLibraryPicker = false" />
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl">
            <div class="mb-4 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">选择参考素材</h3>
              <button
                type="button"
                class="text-gray-400 hover:text-gray-500"
                @click="showLibraryPicker = false"
              >
                ×
              </button>
            </div>
            <AssetPicker ref="assetPicker" @select="handleLibraryAssetSelect" />
          </div>
        </div>
      </div>
    </teleport>

    <transition name="fade">
      <div
        v-if="showPreview"
        class="preview-overlay"
        @click.self="closePreview"
      >
        <div class="preview-modal">
          <div class="preview-header">
            <h4 class="preview-title">{{ safeTitle }}</h4>
            <button class="preview-close" type="button" @click="closePreview">×</button>
          </div>
          <div class="preview-content">
            <iframe
              v-if="canEmbedPreview"
              :src="embedUrl"
              class="preview-frame"
              allowfullscreen
            ></iframe>
            <div v-else class="preview-fallback">
              <p class="preview-text">该素材暂不支持内嵌预览。</p>
              <a
                v-if="previewUrl"
                :href="previewUrl"
                target="_blank"
                rel="noopener"
                class="preview-link"
              >
                在新标签页打开预览
              </a>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ReferenceMaterialCell } from '@/types/cell'
import type { LibraryAssetSummary } from '@/types/library'
import { ResourceType, getResourceTypeIcon, getResourceTypeName } from '@/types/resource'
import DocumentPreviewModal from '@/components/Resource/DocumentPreviewModal.vue'
import AssetPicker from '@/components/Library/AssetPicker.vue'
import api from '@/services/api'
import { getServerBaseUrl } from '@/utils/url'

interface Props {
  cell: ReferenceMaterialCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [ReferenceMaterialCell]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const showLibraryPicker = ref(false)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()

function sanitizeUrl(url?: string | null): string | null {
  if (!url) return null
  const trimmed = url.trim()
  if (!trimmed) return null
  const serverBase = getServerBaseUrl()

  if (/^https?:\/\//i.test(trimmed)) {
    try {
      const u = new URL(trimmed)
      // 资源路径统一走后端，避免误用前端 :5173
      if (u.pathname.startsWith('/uploads/')) {
        return `${serverBase}${u.pathname}${u.search}`
      }
    } catch {
      /* fall through */
    }
    if (window.location.protocol === 'https:') {
      return trimmed.replace(/^http:\/\//i, 'https://')
    }
    return trimmed
  }

  if (trimmed.startsWith('/uploads/')) {
    return `${serverBase}${trimmed}`
  }

  if (trimmed.startsWith('/')) {
    return `${serverBase}${trimmed}`
  }

  if (/\.(pdf|docx?|xlsx?|pptx?|md|markdown|txt|png|jpe?g|gif|webp|svg)$/i.test(trimmed)) {
    return `${serverBase}/uploads/resources/${trimmed}`
  }

  return null
}

const rawPreviewUrl = computed(() => sanitizeUrl(props.cell.content.preview_url))
const previewUrl = computed(() => rawPreviewUrl.value || sanitizeUrl(props.cell.content.download_url))
const downloadUrl = computed(() => sanitizeUrl(props.cell.content.download_url) || sanitizeUrl(props.cell.content.preview_url))
const hasFile = computed(() => Boolean(previewUrl.value || downloadUrl.value))

const showPreview = ref(false)
const showDocPreview = ref(false)
const docPreviewFileUrl = ref<string | null>(null)

const resolvedType = computed(() => {
  const candidate = props.cell.content.resource_type as ResourceType
  return Object.values(ResourceType).includes(candidate) ? candidate : null
})

const typeLabel = computed(() => {
  if (resolvedType.value) {
    return getResourceTypeName(resolvedType.value)
  }
  return '素材'
})

const icon = computed(() => {
  if (resolvedType.value) {
    return getResourceTypeIcon(resolvedType.value)
  }
  return '📁'
})

const safeTitle = computed(() => props.cell.content.title || '未命名素材')

const summaryText = computed(() => {
  if (props.cell.content.summary) {
    return props.cell.content.summary
  }
  return '该素材暂无摘要，可使用下方链接查看完整内容。'
})

const formattedUpdatedAt = computed(() => {
  const value = props.cell.content.updated_at
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString()
})

function openInNewTab(url: string | null) {
  if (!url) return
  window.open(url, '_blank', 'noopener')
}

function isDocumentPreviewUrl(url: string | null): boolean {
  if (!url) return false
  return /\.(pdf|docx?|pptx?|xlsx?|md|markdown|txt)(?:[?#]|$)/i.test(url)
}

function isAllowedDocument(filename: string): boolean {
  return /\.(pdf|docx?|pptx?|xlsx?|md|markdown|txt)$/i.test(filename)
}

function inferResourceType(filename: string, assetType?: string): string {
  if (assetType === 'pdf' || /\.pdf$/i.test(filename)) return ResourceType.PDF
  if (/\.(md|markdown|txt)$/i.test(filename)) return ResourceType.DOCUMENT
  if (assetType === 'document' || isAllowedDocument(filename)) return ResourceType.DOCUMENT
  return assetType || ResourceType.DOCUMENT
}

function extractFilename(url: string): string {
  if (!url || url.startsWith('blob:') || url.startsWith('data:')) return url
  if (!url.includes('/') && !url.startsWith('http://') && !url.startsWith('https://')) {
    return url
  }
  try {
    const urlObj = new URL(url)
    return urlObj.pathname.split('/').pop() || url
  } catch {
    if (url.includes('/')) {
      const parts = url.split('/')
      return parts[parts.length - 1].split('?')[0].split('#')[0] || url
    }
  }
  return url
}

function applyMaterial(payload: {
  title: string
  fileUrl: string
  materialId?: number
  resourceType?: string
  summary?: string
  fileSize?: number
  tags?: string[]
}) {
  const resourceType = payload.resourceType || inferResourceType(payload.title)
  emit('update', {
    ...props.cell,
    content: {
      ...props.cell.content,
      material_id: payload.materialId ?? (props.cell.content.material_id || -Date.now()),
      title: payload.title,
      summary:
        payload.summary ||
        (payload.fileSize
          ? `上传文档 · ${(payload.fileSize / 1024).toFixed(1)} KB`
          : props.cell.content.summary || '教案内文档素材'),
      resource_type: resourceType,
      preview_url: payload.fileUrl,
      download_url: payload.fileUrl,
      tags: payload.tags ?? props.cell.content.tags ?? ['上传文档'],
      updated_at: new Date().toISOString(),
      is_accessible: true,
    },
  })
}

function triggerUpload() {
  fileInput.value?.click()
}

function openLibraryPicker() {
  showLibraryPicker.value = true
}

async function onFileSelected(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  if (!isAllowedDocument(file.name)) {
    alert('请选择 PDF / Word / PPT / Excel / Markdown 文档')
    return
  }

  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    alert('文件大小不能超过 50MB')
    return
  }

  isUploading.value = true
  uploadProgress.value = 0
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<{ file_url: string; filename?: string; file_size?: number }>(
      '/upload/',
      formData,
      {
        onUploadProgress: (e) => {
          if (e.total) uploadProgress.value = Math.round((e.loaded * 100) / e.total)
        },
        timeout: 300000,
      }
    )

    const fileUrl = response.file_url
    const originalFilename = response.filename || file.name
    const filenameForDb = extractFilename(fileUrl)
    const downloadUrl = fileUrl.startsWith('http://') || fileUrl.startsWith('https://')
      ? fileUrl
      : `${getServerBaseUrl()}/uploads/resources/${filenameForDb}`

    applyMaterial({
      title: originalFilename,
      fileUrl: downloadUrl,
      resourceType: inferResourceType(originalFilename),
      fileSize: response.file_size ?? file.size,
      tags: ['上传文档'],
    })
    uploadProgress.value = 100
  } catch (err: any) {
    console.error(err)
    alert(err.response?.data?.detail || err.message || '上传失败')
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

function handleLibraryAssetSelect(asset: LibraryAssetSummary | null) {
  if (!asset) {
    showLibraryPicker.value = false
    return
  }

  const fileUrl = asset.public_url || ''
  const title = asset.title || '资源文件'
  if (!fileUrl && !isAllowedDocument(title)) {
    alert('请选择 PDF / Word / PPT / Excel / Markdown 类文档资源')
    return
  }

  if (
    asset.asset_type &&
    !['pdf', 'document', 'other'].includes(asset.asset_type) &&
    !isAllowedDocument(title) &&
    !isDocumentPreviewUrl(fileUrl)
  ) {
    alert('参考素材仅支持文档类型（PDF / Office / Markdown）')
    return
  }

  applyMaterial({
    title,
    fileUrl: fileUrl || `${getServerBaseUrl()}/uploads/resources/${extractFilename(title)}`,
    materialId: asset.id,
    resourceType: inferResourceType(title, asset.asset_type),
    summary: asset.size_bytes
      ? `资源库 · ${(asset.size_bytes / 1024).toFixed(1)} KB`
      : '来自资源库',
    tags: ['资源库'],
  })
  showLibraryPicker.value = false
}

function handlePreview() {
  const url = previewUrl.value || downloadUrl.value
  if (!url) return

  if (
    resolvedType.value === ResourceType.PDF ||
    resolvedType.value === ResourceType.DOCUMENT ||
    isDocumentPreviewUrl(url)
  ) {
    docPreviewFileUrl.value = url
    showDocPreview.value = true
    return
  }

  if (canEmbedPreview.value) {
    showPreview.value = true
  } else {
    openInNewTab(url)
  }
}

function handleDownload() {
  openInNewTab(downloadUrl.value)
}

const canEmbedPreview = computed(() => {
  const url = rawPreviewUrl.value
  if (!url) return false
  return /\.(pdf|png|jpe?g|gif|webp|svg)$/i.test(url)
})

const embedUrl = computed(() => {
  if (!rawPreviewUrl.value) return ''
  if (/\.pdf(?:[?#]|$)/i.test(rawPreviewUrl.value)) {
    return `${rawPreviewUrl.value}#toolbar=0`
  }
  return rawPreviewUrl.value
})

function closePreview() {
  showPreview.value = false
}
</script>

<style scoped>
.reference-material-cell {
  @apply bg-white;
}

.reference-empty-state {
  @apply flex flex-col items-center justify-center gap-3 px-6 py-10 text-center border-2 border-dashed border-slate-200 rounded-lg m-2;
}

.empty-icon {
  @apply text-4xl;
}

.empty-title {
  @apply text-base font-semibold text-gray-900;
}

.empty-hint {
  @apply text-sm text-gray-500;
}

.empty-actions {
  @apply flex flex-wrap items-center justify-center gap-3 mt-2;
}

.hidden {
  display: none;
}

.reference-card {
  @apply flex flex-col gap-4 p-4;
}

.reference-body {
  @apply flex gap-4;
}

.reference-icon {
  @apply flex items-start justify-center w-12 h-12 rounded-lg bg-blue-50 text-blue-600;
}

.reference-info {
  @apply flex-1 space-y-2;
}

.reference-title {
  @apply text-lg font-semibold text-gray-900;
}

.reference-meta {
  @apply text-sm text-gray-500 flex items-center flex-wrap gap-1;
}

.reference-updated {
  @apply text-xs text-gray-400;
}

.reference-summary {
  @apply text-sm text-gray-700 leading-relaxed;
}

.reference-source {
  @apply text-sm text-gray-500;
}

.reference-tags {
  @apply flex flex-wrap gap-2 pt-1;
}

.reference-tag {
  @apply px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700;
}

.reference-tag.more {
  @apply bg-gray-100 text-gray-600;
}

.reference-actions {
  @apply flex flex-wrap gap-3;
}

.reference-button {
  @apply px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed;
}

.reference-button.primary {
  @apply bg-blue-600 text-white border-transparent hover:bg-blue-700;
}

.reference-empty {
  @apply text-xs text-gray-400;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.preview-overlay {
  @apply fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4;
}

.preview-modal {
  @apply bg-white rounded-xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col overflow-hidden;
}

.preview-header {
  @apply flex items-center justify-between px-4 py-3 border-b border-gray-200;
}

.preview-title {
  @apply text-base font-semibold text-gray-900;
}

.preview-close {
  @apply text-2xl leading-none text-gray-500 hover:text-gray-700;
}

.preview-content {
  @apply flex-1 bg-gray-100;
}

.preview-frame {
  @apply w-full h-full border-0 bg-white;
}

.preview-fallback {
  @apply h-full flex flex-col items-center justify-center gap-4 text-sm text-gray-600;
}

.preview-link {
  @apply text-blue-600 hover:text-blue-700 underline;
}
.preview-text {
  @apply text-gray-500;
}
</style>
