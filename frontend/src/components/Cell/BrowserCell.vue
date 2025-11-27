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
          <label>
            <input
              v-model="localConfig.allowNavigation"
              type="checkbox"
              @change="updateCell"
            />
            允许导航
          </label>
          <label>
            <input
              v-model="localConfig.showToolbar"
              type="checkbox"
              @change="updateCell"
            />
            显示工具栏
          </label>
        </div>
        
        <div class="form-group">
          <label>高度:</label>
          <input
            v-model="localConfig.height"
            type="text"
            placeholder="600px 或 100vh"
            @blur="updateCell"
          />
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

      <!-- 链接模式：当检测到 X-Frame-Options 限制时，直接显示链接卡片 -->
      <div v-if="useLinkMode" class="link-mode-card">
        <div class="link-card-content">
          <svg class="link-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <div class="link-info">
            <h3 class="link-title">网站链接</h3>
            <p class="link-url">{{ displayUrl }}</p>
            <p class="link-hint">该网站不允许在框架中显示，请在新窗口打开</p>
          </div>
          <button @click="openInNewWindow" class="link-open-btn">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            在新窗口打开
          </button>
        </div>
      </div>

      <!-- iframe 模式：尝试嵌入显示 -->
      <div v-else class="iframe-container" :style="iframeStyle">
        <iframe
          v-if="displayUrl"
          ref="iframeRef"
          :src="displayUrl"
          :sandbox="sandboxAttributes"
          frameborder="0"
          allowfullscreen
          @load="handleIframeLoad"
          @error="handleIframeError"
          class="browser-iframe"
        />
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        
        <!-- 错误状态（仅在 iframe 模式下显示，如果检测到错误会自动切换到链接模式） -->
        <div v-if="loadError && !useLinkMode" class="error-overlay">
          <div class="error-content">
            <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="error-title">无法在框架中显示</h3>
            <p class="error-message">{{ loadError }}</p>
            <div class="error-actions">
              <button @click="switchToLinkMode" class="retry-btn retry-btn-primary">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                切换到链接模式
              </button>
              <button @click="retryLoad" class="retry-btn">重试</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 工具栏 -->
      <div class="browser-toolbar">
        <button v-if="displayConfig?.showToolbar && !useLinkMode" @click="refreshIframe" class="toolbar-btn" title="刷新">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          刷新
        </button>
        <button v-if="!useLinkMode" @click="switchToLinkMode" class="toolbar-btn" title="切换到链接模式">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          链接模式
        </button>
        <button @click="openInNewWindow" class="toolbar-btn toolbar-btn-primary" title="在新窗口打开">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          在新窗口打开
        </button>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div v-else-if="!editable && !displayUrl" class="empty-state">
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
import { ref, watch, computed, onBeforeUnmount, onMounted } from 'vue'
import type { BrowserCell } from '../../types/cell'
import { useFullscreen } from '@/composables/useFullscreen'

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

const iframeRef = ref<HTMLIFrameElement>()
const localContent = ref({ ...props.cell.content })
const localConfig = ref<BrowserCell['config']>({ 
  allowFullscreen: true,
  allowNavigation: true,
  showToolbar: false,
  height: '600px',
  ...(props.cell.config || {})
})

const urlError = ref<string | null>(null)
const isLoading = ref(false)
const loadError = ref<string | null>(null)
const useLinkMode = ref(false) // 是否使用链接模式（当 iframe 被阻止时）

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

// iframe 样式
const iframeStyle = computed(() => {
  const height = displayConfig.value?.height || '600px'
  return {
    height: height,
    minHeight: '400px',
  }
})

// iframe sandbox 属性
const sandboxAttributes = computed(() => {
  const sandbox = displayConfig.value?.sandbox || []
  const allowNavigation = displayConfig.value?.allowNavigation !== false
  
  // 基础安全限制
  const baseSandbox = [
    'allow-same-origin',
    'allow-scripts',
    'allow-forms',
    'allow-popups',
    'allow-popups-to-escape-sandbox',
  ]
  
  // 如果允许导航，添加 allow-top-navigation-by-user-activation
  if (allowNavigation) {
    baseSandbox.push('allow-top-navigation-by-user-activation')
  }
  
  // 合并用户自定义的 sandbox 属性
  return [...new Set([...baseSandbox, ...sandbox])].join(' ')
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

// 切换到链接模式
function switchToLinkMode() {
  useLinkMode.value = true
  loadError.value = null
  isLoading.value = false
}

// iframe 加载处理
function handleIframeLoad() {
  isLoading.value = false
  
  // 立即检查是否被 X-Frame-Options 阻止
  // 如果被阻止，访问 contentDocument 会抛出 SecurityError
  try {
    if (iframeRef.value?.contentWindow) {
      // 尝试访问内容，如果被阻止会抛出 SecurityError
      const iframeDoc = iframeRef.value.contentDocument || iframeRef.value.contentWindow?.document
      if (iframeDoc && iframeDoc.body) {
        // 成功访问，内容正常加载
        loadError.value = null
        useLinkMode.value = false
      } else {
        // 内容为空，可能被阻止，自动切换到链接模式
        switchToLinkMode()
      }
    }
  } catch (e: any) {
    // 跨域访问被阻止，说明网站设置了 X-Frame-Options，自动切换到链接模式
    if (e.name === 'SecurityError' || e.message.includes('Blocked a frame') || e.message.includes('cross-origin')) {
      switchToLinkMode()
    } else if (e.message.includes('frame') || e.message.includes('X-Frame')) {
      switchToLinkMode()
    } else {
      // 其他错误，可能是网络问题
      loadError.value = '网页加载失败，请检查网址是否正确或网络连接。'
    }
  }
}

// iframe 错误处理
function handleIframeError(event: Event) {
  isLoading.value = false
  
  // 检查是否是网络错误（522 等）
  const target = event.target as HTMLIFrameElement
  if (target) {
    // 522 错误通常是服务器超时
    loadError.value = '网页加载超时（服务器响应 522）。请检查网络连接，或点击"新窗口"按钮在新标签页中打开。'
  } else {
    loadError.value = '网页加载失败，请检查网址是否正确或网络连接。某些网站可能不允许在框架中显示。'
  }
}


// 重试加载
function retryLoad() {
  if (iframeRef.value && displayUrl.value) {
    loadError.value = null
    isLoading.value = true
    iframeRef.value.src = displayUrl.value
  }
}

// 刷新 iframe
function refreshIframe() {
  if (iframeRef.value) {
    isLoading.value = true
    loadError.value = null
    iframeRef.value.src = iframeRef.value.src
  }
}

// 在新窗口打开
function openInNewWindow() {
  if (displayUrl.value) {
    window.open(displayUrl.value, '_blank', 'noopener,noreferrer')
  }
}

// 监听 props.cell 的变化，同步到本地状态
watch(() => props.cell, (newCell) => {
  if (newCell && !props.editable) {
    // 非编辑模式下，如果 URL 变化，重置加载状态
    if (newCell.content?.url !== localContent.value.url) {
      localContent.value = { ...newCell.content }
      localConfig.value = {
        allowFullscreen: true,
        allowNavigation: true,
        showToolbar: false,
        height: '600px',
        ...(newCell.config || {})
      }
      isLoading.value = true
      loadError.value = null
    }
  }
}, { deep: true })

// 当 URL 变化时，设置加载状态
watch(() => displayUrl.value, (newUrl, oldUrl) => {
  if (newUrl && newUrl !== oldUrl && !props.editable) {
    isLoading.value = true
    loadError.value = null
  }
}, { immediate: true })

// 组件挂载时检查 URL
let errorHandler: ((event: ErrorEvent) => void) | null = null

onMounted(() => {
  if (props.cell.content?.url && !props.editable) {
    isLoading.value = true
    loadError.value = null
  }
  
  // 监听页面错误事件（捕获 X-Frame-Options 错误）
  errorHandler = (event: ErrorEvent) => {
    const errorMsg = event.message || ''
    if (errorMsg.includes('X-Frame-Options') || 
        errorMsg.includes('Refused to display') || 
        errorMsg.includes('frame') ||
        errorMsg.includes('frame-ancestors')) {
      switchToLinkMode()
      // 阻止错误继续传播
      event.preventDefault()
    }
  }
  
  window.addEventListener('error', errorHandler, true) // 使用捕获阶段
})

onBeforeUnmount(() => {
  if (errorHandler) {
    window.removeEventListener('error', errorHandler)
    errorHandler = null
  }
})

watch(() => props.cell.content?.url, (url) => {
  if (url && !props.editable) {
    isLoading.value = true
    loadError.value = null
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

.browser-cell.fullscreen .iframe-container {
  @apply flex-1;
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
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.url-input-wrapper {
  @apply flex gap-2;
}

.url-input {
  @apply flex-1;
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

.iframe-container {
  @apply relative w-full border border-gray-300 rounded-lg overflow-hidden bg-gray-100;
}

.browser-iframe {
  @apply w-full h-full border-0;
}

.loading-overlay {
  @apply absolute inset-0 flex flex-col items-center justify-center bg-white bg-opacity-90;
}

.loading-spinner {
  @apply w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-2;
}

.error-overlay {
  @apply absolute inset-0 flex items-center justify-center bg-white bg-opacity-95 p-6;
}

.error-content {
  @apply text-center max-w-md;
}

.error-icon {
  @apply w-16 h-16 text-amber-500 mx-auto mb-4;
}

.error-title {
  @apply text-lg font-semibold text-gray-900 mb-2;
}

.error-message {
  @apply text-sm text-gray-600 mb-6 leading-relaxed;
}

.error-actions {
  @apply flex flex-col sm:flex-row gap-3 justify-center items-stretch sm:items-center;
}

.retry-btn {
  @apply flex items-center justify-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium;
}

.retry-btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 shadow-md;
}

.browser-toolbar {
  @apply flex gap-2 mt-2 p-2 bg-gray-50 rounded-lg;
}

.toolbar-btn {
  @apply flex items-center gap-1 px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors;
}

.toolbar-btn-primary {
  @apply bg-blue-600 text-white border-blue-600 hover:bg-blue-700;
}

.toolbar-btn-primary {
  @apply bg-blue-600 text-white border-blue-600 hover:bg-blue-700;
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
  @apply w-full border-2 border-blue-200 rounded-lg bg-blue-50 p-6;
}

.link-card-content {
  @apply flex flex-col items-center text-center;
}

.link-icon {
  @apply w-16 h-16 text-blue-600 mb-4;
}

.link-info {
  @apply mb-6;
}

.link-title {
  @apply text-xl font-semibold text-gray-900 mb-2;
}

.link-url {
  @apply text-sm text-blue-600 mb-2 break-all;
}

.link-hint {
  @apply text-sm text-gray-600;
}

.link-open-btn {
  @apply flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md;
}
</style>

