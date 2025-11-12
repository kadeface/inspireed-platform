<template>
  <div
    class="reference-material-cell"
    :contenteditable="editable ? 'false' : undefined"
  >
    <div class="reference-card">
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
          :disabled="!previewUrl"
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
      </div>

      <p v-if="!previewUrl && !downloadUrl" class="reference-empty">
        暂无可用的预览或下载链接。
      </p>
    </div>

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
import { ResourceType, getResourceTypeIcon, getResourceTypeName } from '@/types/resource'

interface Props {
  cell: ReferenceMaterialCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

defineEmits<{
  update: [ReferenceMaterialCell]
}>()

function sanitizeUrl(url?: string | null): string | null {
  if (!url) return null
  const trimmed = url.trim()
  if (!trimmed) return null

  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed
  }

  if (trimmed.startsWith('/')) {
    return `${window.location.origin}${trimmed}`
  }

  return null
}

const rawPreviewUrl = computed(() => sanitizeUrl(props.cell.content.preview_url))
const previewUrl = computed(() => rawPreviewUrl.value || sanitizeUrl(props.cell.content.download_url))
const downloadUrl = computed(() => sanitizeUrl(props.cell.content.download_url) || sanitizeUrl(props.cell.content.preview_url))
const showPreview = ref(false)

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

function handlePreview() {
  if (!previewUrl.value) return
  if (canEmbedPreview.value) {
    showPreview.value = true
  } else {
    openInNewTab(previewUrl.value)
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
  if (rawPreviewUrl.value.endsWith('.pdf')) {
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


