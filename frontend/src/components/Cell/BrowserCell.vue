<template>
  <div class="browser-cell cell-container" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
    <!-- 全屏按钮 -->
    <div v-if="!editable && displayConfig?.allowFullscreen !== false" class="cell-toolbar">
      <button
        class="cell-fullscreen-btn"
        :class="{ 'active': isFullscreen }"
        @click="toggleFullscreen"
        :title="isFullscreen ? '退出全屏 (Esc)' : '全屏查看'"
      >
        <svg v-if="!isFullscreen" class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
        <svg v-else class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span class="text-sm font-medium ml-1">{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
      </button>
    </div>
    
    <div v-if="editable" class="browser-editor">
      <!-- URL 输入区域 -->
      <div class="form-group">
        <label>网址 URL:</label>
        <div class="url-input-wrapper">
          <input
            v-model="localContent.url"
            type="url"
            placeholder="https://example.com"
            @blur="validateAndUpdate"
            class="url-input"
            :class="{ 'error': urlError }"
          />
          <button
            v-if="localContent.url && isValidUrl(localContent.url)"
            @click="previewUrl"
            class="preview-btn"
            title="在新窗口预览"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
        </div>
        <p v-if="urlError" class="error-text">{{ urlError }}</p>
        <p v-else class="hint-text">请输入有效的 http:// 或 https:// 网址</p>
      </div>

      <!-- 标题和描述 -->
      <div class="form-group">
        <label>标题（可选）:</label>
        <input
          v-model="localContent.title"
          type="text"
          placeholder="输入单元标题"
          @blur="updateCell"
        />
      </div>
      
      <div class="form-group">
        <label>描述（可选）:</label>
        <textarea
          v-model="localContent.description"
          placeholder="输入单元描述"
          rows="3"
          @blur="updateCell"
        />
      </div>

      <!-- 配置选项 -->
      <div class="browser-config">
        <h4>显示配置</h4>
        <div class="config-options">
          <label>
            <input
              v-model="localConfig.allowFullscreen"
              type="checkbox"
              @change="updateCell"
            />
            允许全屏
          </label>
        </div>
      </div>
    </div>

    <!-- 浏览器显示区域 -->
    <div v-if="displayUrl" class="browser-display">
      <!-- 标题和描述显示 -->
      <div v-if="displayContent.title || displayContent.description" class="browser-info">
        <h3 v-if="displayContent.title" class="browser-title">{{ displayContent.title }}</h3>
        <p v-if="displayContent.description" class="browser-description">{{ displayContent.description }}</p>
      </div>

      <!-- 链接卡片 -->
      <div class="link-mode-card" :class="{ 'fullscreen-preview': isFullscreenPreview }">
        <div class="link-card-content">
          <!-- 链接信息 -->
          <div class="link-header">
            <svg class="link-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <div class="link-info">
              <h3 class="link-title">网站链接</h3>
              <p class="link-url">{{ displayUrl }}</p>
            </div>
          </div>

          <!-- 二维码区域 -->
          <div class="qr-code-section">
            <img 
              v-if="qrCodeDataUrl"
              :src="qrCodeDataUrl" 
              @click="showLargeQR = true"
              class="qr-code"
              alt="二维码"
            />
            <div v-else class="qr-code-loading">
              <div class="loading-spinner-small"></div>
              <p>生成二维码中...</p>
            </div>
            <p class="qr-hint">点击二维码放大</p>
          </div>

          <!-- 打开按钮 -->
          <button @click="openInNewWindow" class="link-open-btn">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            在新窗口打开
          </button>
        </div>
      </div>
    </div>

    <!-- 放大二维码模态框 -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div
          v-if="showLargeQR"
          class="qr-modal-overlay"
          @click.self="showLargeQR = false"
          @keydown.esc="showLargeQR = false"
          tabindex="0"
        >
          <div class="qr-modal-content">
            <button @click="showLargeQR = false" class="qr-modal-close">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div class="qr-modal-body">
              <img 
                v-if="qrCodeLargeDataUrl"
                :src="qrCodeLargeDataUrl" 
                class="qr-code-large"
                alt="二维码（放大）"
              />
              <div v-else class="qr-code-loading-large">
                <div class="loading-spinner"></div>
                <p>生成二维码中...</p>
              </div>
              <p class="qr-modal-hint">用手机扫描二维码打开网站</p>
              <p class="qr-modal-url">{{ displayUrl }}</p>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 空状态提示 -->
    <div v-if="!editable && !displayUrl" class="empty-state">
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
      <p>未配置网址</p>
      <p v-if="props.cell.content?.url" class="text-xs text-gray-500 mt-2">
        当前URL: {{ props.cell.content.url }}
        <br>
        <span v-if="!isValidUrl(props.cell.content.url)" class="text-red-500">
          (URL格式无效)
        </span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onBeforeUnmount, onMounted, nextTick } from 'vue'
import type { BrowserCell } from '../../types/cell'
import { useFullscreen } from '@/composables/useFullscreen'
import QRCode from 'qrcode'

interface Props {
  cell: BrowserCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<{
  update: [cell: BrowserCell]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

const localContent = ref({ ...props.cell.content })
const localConfig = ref<BrowserCell['config']>({ 
  allowFullscreen: true,
  ...(props.cell.config || {})
})

const urlError = ref<string | null>(null)

// 二维码相关
const qrCodeDataUrl = ref<string | null>(null)
const qrCodeLargeDataUrl = ref<string | null>(null)
const showLargeQR = ref(false)
const isGeneratingQR = ref(false)

// 在编辑模式下使用 localContent，非编辑模式下使用 props
const displayUrl = computed(() => {
  const url = props.editable ? localContent.value.url : (props.cell.content?.url || '')
  return url && isValidUrl(url) ? url : null
})

const displayContent = computed(() => {
  return props.editable ? localContent.value : (props.cell.content || {} as BrowserCell['content'])
})

const displayConfig = computed(() => {
  return props.editable ? localConfig.value : (props.cell.config || {} as BrowserCell['config'])
})

// URL 验证
function isValidUrl(url: string): boolean {
  if (!url || !url.trim()) return false
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

// 验证并更新
function validateAndUpdate() {
  urlError.value = null
  
  if (!localContent.value.url || !localContent.value.url.trim()) {
    // 允许为空（编辑中）
    updateCell()
    return
  }
  
  if (!isValidUrl(localContent.value.url)) {
    urlError.value = '请输入有效的网址（必须以 http:// 或 https:// 开头）'
    return
  }
  
  updateCell()
}

// 更新 Cell
function updateCell() {
  const updatedCell: BrowserCell = {
    ...props.cell,
    content: { ...localContent.value },
    config: localConfig.value ? { ...localConfig.value } : undefined
  }
  emit('update', updatedCell)
}

// 在新窗口预览
function previewUrl() {
  if (localContent.value.url && isValidUrl(localContent.value.url)) {
    window.open(localContent.value.url, '_blank', 'noopener,noreferrer')
  }
}


// 在新窗口打开
function openInNewWindow() {
  if (displayUrl.value) {
    window.open(displayUrl.value, '_blank', 'noopener,noreferrer')
  }
}

// 生成二维码
async function generateQRCode(url: string, size: number = 200): Promise<string | null> {
  if (!url) return null
  
  try {
    const dataUrl = await QRCode.toDataURL(url, {
      width: size,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
    return dataUrl
  } catch (error) {
    console.error('生成二维码失败:', error)
    return null
  }
}

// 生成二维码（基础尺寸）
async function generateNormalQR() {
  if (!displayUrl.value || isGeneratingQR.value) return
  
  isGeneratingQR.value = true
  try {
    const size = isFullscreenPreview.value ? 300 : 200
    const dataUrl = await generateQRCode(displayUrl.value, size)
    qrCodeDataUrl.value = dataUrl
  } finally {
    isGeneratingQR.value = false
  }
}

// 生成大尺寸二维码（用于放大模态框）
async function generateLargeQR() {
  if (!displayUrl.value || qrCodeLargeDataUrl.value) return
  
  try {
    const size = isFullscreenPreview.value ? 600 : 500
    const dataUrl = await generateQRCode(displayUrl.value, size)
    qrCodeLargeDataUrl.value = dataUrl
  } catch (error) {
    console.error('生成大尺寸二维码失败:', error)
  }
}

// 检测是否在全屏预览模式（通过检查父元素）
const isFullscreenPreview = computed(() => {
  if (!containerRef.value) return false
  // 检查是否在全屏预览的上下文中
  const parent = containerRef.value.closest('.fixed.inset-0')
  return !!parent || isFullscreen.value
})

// 监听 props.cell 的变化，同步到本地状态
watch(() => props.cell, (newCell) => {
  if (newCell && !props.editable) {
    // 非编辑模式下，如果 URL 变化，重新生成二维码
    if (newCell.content?.url !== localContent.value.url) {
      localContent.value = { ...newCell.content }
      localConfig.value = {
        allowFullscreen: true,
        ...(newCell.config || {})
      }
      // 重置并重新生成二维码
      qrCodeDataUrl.value = null
      qrCodeLargeDataUrl.value = null
      if (displayUrl.value) {
        nextTick(() => {
          generateNormalQR()
        })
      }
    }
  }
}, { deep: true })

// 当 URL 变化时，生成二维码
watch(() => displayUrl.value, (newUrl, oldUrl) => {
  if (newUrl && newUrl !== oldUrl && !props.editable) {
    // 重置二维码
    qrCodeDataUrl.value = null
    qrCodeLargeDataUrl.value = null
    // 生成新二维码
    nextTick(() => {
      generateNormalQR()
    })
  }
}, { immediate: true })

// 当显示放大模态框时，生成大尺寸二维码
watch(() => showLargeQR.value, (show) => {
  if (show && displayUrl.value && !qrCodeLargeDataUrl.value) {
    generateLargeQR()
  }
})


onMounted(() => {
  // 生成二维码
  if (displayUrl.value && !props.editable) {
    nextTick(() => {
      generateNormalQR()
    })
  }
})

// 监听 ESC 键关闭二维码模态框
let escKeyHandler: ((e: KeyboardEvent) => void) | null = null

onMounted(() => {
  escKeyHandler = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && showLargeQR.value) {
      showLargeQR.value = false
    }
  }
  window.addEventListener('keydown', escKeyHandler)
})

onBeforeUnmount(() => {
  if (escKeyHandler) {
    window.removeEventListener('keydown', escKeyHandler)
    escKeyHandler = null
  }
})

</script>

<style scoped>
/* 全屏按钮样式 */
.cell-toolbar {
  @apply flex justify-end mb-2;
}

.cell-fullscreen-btn {
  @apply flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors;
}

.cell-fullscreen-btn.active {
  @apply bg-red-50 hover:bg-red-100 text-red-700;
}

.cell-fullscreen-btn .icon {
  @apply w-4 h-4;
}

/* 全屏模式样式 */
.browser-cell.fullscreen {
  @apply fixed inset-0 z-50 bg-white overflow-auto;
}

.browser-cell.fullscreen .browser-display {
  @apply h-full flex flex-col;
}

.browser-cell {
  @apply w-full;
}

/* 编辑器样式 */
.browser-editor {
  @apply p-4;
}

.form-group {
  @apply mb-4;
}

.form-group label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.form-group input,
.form-group textarea {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900;
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  @apply text-gray-400;
}

.form-group input:focus,
.form-group textarea:focus {
  @apply border-blue-500 bg-white;
}

.url-input-wrapper {
  @apply flex gap-2;
}

.url-input {
  @apply flex-1 bg-white text-gray-900;
}

.url-input::placeholder {
  @apply text-gray-400;
}

.url-input:focus {
  @apply bg-white;
}

.url-input.error {
  @apply border-red-500 focus:ring-red-500;
}

.preview-btn {
  @apply px-3 py-2 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors;
}

.error-text {
  @apply text-sm text-red-600 mt-1;
}

.hint-text {
  @apply text-xs text-gray-500 mt-1;
}

.browser-config {
  @apply mt-4 p-4 bg-gray-50 rounded-lg;
}

.browser-config h4 {
  @apply text-sm font-semibold text-gray-700 mb-2;
}

.config-options {
  @apply grid grid-cols-1 gap-2 mb-4;
}

.config-options label {
  @apply flex items-center space-x-2 cursor-pointer;
}

/* 浏览器显示区域 */
.browser-display {
  @apply w-full;
}

.browser-info {
  @apply mb-4 p-4 bg-gray-50 rounded-lg;
}

.browser-title {
  @apply text-lg font-semibold text-gray-900 mb-2;
}

.browser-description {
  @apply text-sm text-gray-600;
}


.empty-state {
  @apply flex flex-col items-center justify-center p-12 text-center;
}

.empty-icon {
  @apply w-16 h-16 text-gray-400 mb-4;
}

.empty-state p {
  @apply text-gray-500;
}

/* 链接模式样式 */
.link-mode-card {
  @apply w-full border-2 border-blue-200 rounded-lg bg-white p-6;
}

.link-mode-card.fullscreen-preview {
  @apply p-8;
}

.link-card-content {
  @apply flex flex-col items-center text-center gap-6;
}

.link-header {
  @apply flex flex-col items-center gap-3;
}

.link-icon {
  @apply w-12 h-12 text-blue-600;
}

.link-mode-card.fullscreen-preview .link-icon {
  @apply w-16 h-16;
}

.link-info {
  @apply flex flex-col items-center gap-2;
}

.link-title {
  @apply text-lg font-semibold text-gray-900;
}

.link-mode-card.fullscreen-preview .link-title {
  @apply text-xl;
}

.link-url {
  @apply text-sm text-blue-600 break-all max-w-md;
}

.link-mode-card.fullscreen-preview .link-url {
  @apply text-base;
}

/* 二维码区域 */
.qr-code-section {
  @apply flex flex-col items-center gap-3;
}

.qr-code {
  @apply border-2 border-gray-200 rounded-lg p-2 bg-white cursor-pointer transition-all hover:border-blue-400 hover:shadow-lg;
  width: 200px;
  height: 200px;
}

.link-mode-card.fullscreen-preview .qr-code {
  width: 300px;
  height: 300px;
}

.qr-hint {
  @apply text-sm text-gray-500;
}

.link-mode-card.fullscreen-preview .qr-hint {
  @apply text-base;
}

.qr-code-loading {
  @apply flex flex-col items-center justify-center gap-2 border-2 border-gray-200 rounded-lg bg-gray-50;
  width: 200px;
  height: 200px;
}

.link-mode-card.fullscreen-preview .qr-code-loading {
  width: 300px;
  height: 300px;
}

.loading-spinner-small {
  @apply w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin;
}

.loading-spinner {
  @apply w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4;
}

/* 打开按钮 */
.link-open-btn {
  @apply flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md text-base min-w-[200px];
}

.link-mode-card.fullscreen-preview .link-open-btn {
  @apply px-12 py-5 text-lg min-w-[280px];
}

/* 二维码模态框 */
.qr-modal-overlay {
  @apply fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-80 p-4;
}

.qr-modal-content {
  @apply relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8;
}

.qr-modal-close {
  @apply absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors;
}

.qr-modal-body {
  @apply flex flex-col items-center gap-4;
}

.qr-code-large {
  @apply border-4 border-gray-200 rounded-lg p-4 bg-white;
  width: 500px;
  height: 500px;
}

.qr-code-loading-large {
  @apply flex flex-col items-center justify-center gap-4 border-4 border-gray-200 rounded-lg bg-gray-50;
  width: 500px;
  height: 500px;
}

.qr-modal-hint {
  @apply text-lg font-semibold text-gray-900 mt-2;
}

.qr-modal-url {
  @apply text-sm text-blue-600 break-all max-w-md text-center;
}

/* 模态框过渡动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-active .qr-modal-content,
.modal-fade-leave-active .qr-modal-content {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .qr-modal-content,
.modal-fade-leave-to .qr-modal-content {
  transform: scale(0.9);
  opacity: 0;
}
</style>

