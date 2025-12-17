<template>
  <div class="interactive-cell cell-container" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
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
    
    <div v-if="editable" class="interactive-editor">
      <!-- 资源选择方式 -->
      <div class="form-group">
        <label>选择方式:</label>
        <div class="source-options">
          <button
            :class="[
              'source-option-btn',
              sourceMode === 'library' ? 'active' : ''
            ]"
            @click="sourceMode = 'library'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            从资源库选择
          </button>
          <button
            :class="[
              'source-option-btn',
              sourceMode === 'html' ? 'active' : ''
            ]"
            @click="sourceMode = 'html'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            粘贴HTML代码
          </button>
          <button
            :class="[
              'source-option-btn',
              sourceMode === 'url' ? 'active' : ''
            ]"
            @click="sourceMode = 'url'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            输入URL
          </button>
        </div>
      </div>

      <!-- 从资源库选择 -->
      <div v-if="sourceMode === 'library'" class="form-group">
        <label>选择交互式课件:</label>
        <div class="library-picker-wrapper">
          <button
            v-if="!selectedAsset"
            @click="showLibraryPicker = true"
            class="library-picker-btn"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            点击选择资源库中的交互式课件
          </button>
          <div v-else class="selected-asset-card">
            <div class="flex items-center gap-3">
              <div class="flex-shrink-0 w-12 h-12 bg-purple-100 rounded flex items-center justify-center">
                <span class="text-2xl">🎮</span>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-900 truncate">{{ selectedAsset.title }}</h4>
                <p class="text-sm text-gray-500">交互式课件</p>
              </div>
              <button
                @click="clearAsset"
                class="text-red-500 hover:text-red-700"
                title="清除选择"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 粘贴HTML代码 -->
      <div v-if="sourceMode === 'html'" class="form-group">
        <label>HTML代码:</label>
        <div class="html-editor-wrapper">
          <textarea
            v-model="htmlCode"
            @input="handleHtmlCodeChange"
            @paste="handlePaste"
            placeholder="粘贴或输入HTML代码..."
            rows="12"
            class="html-code-input"
            :class="{ 'error': htmlError }"
          ></textarea>
          <div class="html-actions">
            <button
              v-if="htmlCode && htmlCode.trim()"
              @click="generateFromHtml"
              :disabled="isGeneratingHtml"
              class="generate-html-btn"
            >
              <svg v-if="!isGeneratingHtml" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              {{ isGeneratingHtml ? '生成中...' : '生成课件' }}
            </button>
            <button
              v-if="htmlCode && htmlCode.trim()"
              @click="showSaveToLibraryModal = true"
              :disabled="isSavingToLibrary"
              class="save-to-library-btn"
            >
              <svg v-if="!isSavingToLibrary" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              {{ isSavingToLibrary ? '保存中...' : '存储到资源库' }}
            </button>
            <button
              v-if="htmlCode && htmlCode.trim()"
              @click="clearHtmlCode"
              class="clear-html-btn"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              清空
            </button>
          </div>
        </div>
        <p v-if="htmlError" class="error-text">{{ htmlError }}</p>
        <p v-else class="hint-text">粘贴完整的HTML代码，系统将自动生成可用的交互式课件</p>
      </div>

      <!-- 输入URL -->
      <div v-if="sourceMode === 'url'" class="form-group">
        <label>课件URL:</label>
        <div class="url-input-wrapper">
          <input
            v-model="localContent.url"
            type="url"
            placeholder="https://example.com/interactive.html"
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
          placeholder="输入课件标题"
          @blur="updateCell"
        />
      </div>
      
      <div class="form-group">
        <label>描述（可选）:</label>
        <textarea
          v-model="localContent.description"
          placeholder="输入课件描述"
          rows="3"
          @blur="updateCell"
        />
      </div>

      <!-- 配置选项 -->
      <div class="interactive-config">
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

    <!-- 交互式课件显示区域 -->
    <div v-if="displayUrl" class="interactive-display">
      <!-- 标题和描述显示 -->
      <div v-if="displayContent.title || displayContent.description" class="interactive-info">
        <h3 v-if="displayContent.title" class="interactive-title">{{ displayContent.title }}</h3>
        <p v-if="displayContent.description" class="interactive-description">{{ displayContent.description }}</p>
      </div>

      <!-- iframe 嵌入 -->
      <div class="iframe-container">
        <iframe
          :src="displayUrl"
          class="interactive-iframe"
          :style="{
            width: displayConfig?.width || '100%',
            height: displayConfig?.height || '800px'
          }"
          frameborder="0"
          allowfullscreen
          :sandbox="displayConfig?.sandbox?.join(' ') || 'allow-scripts allow-same-origin allow-forms allow-popups'"
        ></iframe>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div v-if="!editable && !displayUrl" class="empty-state">
      <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
      <p>未配置交互式课件</p>
    </div>

    <!-- 资源库选择器模态框 -->
    <Teleport to="body">
      <div
        v-if="showLibraryPicker"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="showLibraryPicker = false"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showLibraryPicker = false"></div>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between">
              <h3 class="text-xl font-semibold text-gray-900">选择交互式课件</h3>
              <button @click="showLibraryPicker = false" class="text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-6">
              <AssetPicker
                ref="assetPicker"
                @select="handleAssetSelect"
                filter-type="interactive"
              />
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 存储到资源库模态框 -->
    <Teleport to="body">
      <div
        v-if="showSaveToLibraryModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="showSaveToLibraryModal = false"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showSaveToLibraryModal = false"></div>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full">
            <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between">
              <h3 class="text-xl font-semibold text-gray-900">存储到资源库</h3>
              <button @click="showSaveToLibraryModal = false" class="text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="px-6 py-4">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  标题 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="saveToLibraryForm.title"
                  type="text"
                  placeholder="输入课件标题"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder:text-gray-400 focus:border-blue-500"
                  @keyup.enter="saveToLibrary"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  描述（可选）
                </label>
                <textarea
                  v-model="saveToLibraryForm.description"
                  rows="3"
                  placeholder="输入课件描述"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder:text-gray-400 focus:border-blue-500"
                />
              </div>
              <!-- 知识点分类选择器 -->
              <div class="mb-4">
                <KnowledgePointSelector
                  v-model="saveToLibraryForm.knowledgePoint"
                />
              </div>
              <div v-if="saveToLibraryError" class="mb-4 text-sm text-red-600">
                {{ saveToLibraryError }}
              </div>
              <div class="flex gap-2 justify-end">
                <button
                  @click="showSaveToLibraryModal = false"
                  class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                  :disabled="isSavingToLibrary"
                >
                  取消
                </button>
                <button
                  @click="saveToLibrary"
                  :disabled="isSavingToLibrary || !saveToLibraryForm.title.trim()"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ isSavingToLibrary ? '保存中...' : '保存' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import type { InteractiveCell } from '../../types/cell'
import type { LibraryAssetSummary, LibraryAssetDetail } from '../../types/library'
import { useFullscreen } from '@/composables/useFullscreen'
import { libraryService } from '@/services/library'
import { getServerBaseUrl } from '@/utils/url'
import AssetPicker from '@/components/Library/AssetPicker.vue'
import KnowledgePointSelector from '@/components/Library/KnowledgePointSelector.vue'

interface Props {
  cell: InteractiveCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<{
  update: [cell: InteractiveCell]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

const localContent = ref({ ...props.cell.content })
const localConfig = ref<InteractiveCell['config']>({ 
  allowFullscreen: true,
  height: '800px',
  ...(props.cell.config || {})
})

const urlError = ref<string | null>(null)
const sourceMode = ref<'library' | 'html' | 'url'>(
  props.cell.content.asset_id ? 'library' : (props.cell.content.html_code ? 'html' : 'url')
)
const showLibraryPicker = ref(false)
const selectedAsset = ref<LibraryAssetSummary | null>(null)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()

// HTML代码相关状态
const htmlCode = ref<string>(props.cell.content.html_code || '')
const htmlError = ref<string | null>(null)
const isGeneratingHtml = ref(false)
const htmlBlobUrl = ref<string | null>(null)

// 存储到资源库相关状态
const showSaveToLibraryModal = ref(false)
const isSavingToLibrary = ref(false)
const saveToLibraryError = ref<string | null>(null)
const saveToLibraryForm = ref({
  title: '',
  description: '',
  knowledgePoint: {} as { category?: string; name?: string }
})

// 解析 URL（处理相对路径）
function resolveUrl(url: string | undefined): string | null {
  if (!url) return null
  
  // 如果是完整 URL，直接返回
  if (isValidUrl(url)) {
    return url
  }
  
  // 如果是相对路径，转换为完整 URL
  if (url.startsWith('/')) {
    const baseURL = getServerBaseUrl()
    return `${baseURL}${url}`
  }
  
  return null
}

// 从HTML代码生成Blob URL
function generateBlobUrlFromHtml(html: string): string {
  const blob = new Blob([html], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  return url
}

// 非编辑模式下的HTML Blob URL（避免重复生成）
const displayHtmlBlobUrl = ref<string | null>(null)

// 在编辑模式下使用 localContent，非编辑模式下使用 props
const displayUrl = computed(() => {
  // 优先使用 URL（无论是从资源库选择、直接输入URL还是HTML代码生成）
  let url: string | undefined
  
  if (props.editable) {
    // 编辑模式
    if (selectedAsset.value?.public_url) {
      url = selectedAsset.value.public_url
    } else if (localContent.value.url) {
      url = localContent.value.url
    } else if (htmlCode.value && htmlCode.value.trim() && htmlBlobUrl.value) {
      // 如果有HTML代码，使用生成的Blob URL
      url = htmlBlobUrl.value
    }
  } else {
    // 非编辑模式：从 cell.content 获取
    if (props.cell.content?.url) {
      url = props.cell.content.url
    } else if (props.cell.content?.html_code && displayHtmlBlobUrl.value) {
      // 如果有HTML代码，使用已生成的Blob URL
      url = displayHtmlBlobUrl.value
    }
  }
  
  return resolveUrl(url) || url || null
})

const displayContent = computed(() => {
  return props.editable ? localContent.value : (props.cell.content || {} as InteractiveCell['content'])
})

const displayConfig = computed(() => {
  return props.editable ? localConfig.value : (props.cell.config || {} as InteractiveCell['config'])
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

// 处理资源库资产选择
function handleAssetSelect(asset: LibraryAssetSummary | null) {
  if (asset && asset.asset_type === 'interactive') {
    selectedAsset.value = asset
    localContent.value.asset_id = asset.id
    localContent.value.url = asset.public_url || undefined
    localContent.value.title = localContent.value.title || asset.title
    localContent.value.description = localContent.value.description || undefined
    localContent.value.thumbnail = asset.thumbnail_url || undefined
    showLibraryPicker.value = false
    updateCell()
  } else {
    selectedAsset.value = null
    localContent.value.asset_id = undefined
  }
}

// 清除选择的资产
function clearAsset() {
  selectedAsset.value = null
  localContent.value.asset_id = undefined
  localContent.value.url = undefined
  updateCell()
}

// 处理HTML代码变化
function handleHtmlCodeChange() {
  htmlError.value = null
  // 实时更新本地内容
  localContent.value.html_code = htmlCode.value
  // 如果有HTML代码，生成Blob URL用于预览
  if (htmlCode.value && htmlCode.value.trim()) {
    // 清理旧的Blob URL
    if (htmlBlobUrl.value) {
      URL.revokeObjectURL(htmlBlobUrl.value)
    }
    htmlBlobUrl.value = generateBlobUrlFromHtml(htmlCode.value)
  } else {
    if (htmlBlobUrl.value) {
      URL.revokeObjectURL(htmlBlobUrl.value)
      htmlBlobUrl.value = null
    }
  }
  updateCell()
}

// 处理粘贴事件（自动清理格式）
function handlePaste(event: ClipboardEvent) {
  // 允许默认粘贴行为，但会在input事件中处理
  // 可以在这里添加额外的处理逻辑
}

// 从HTML代码生成课件
function generateFromHtml() {
  if (!htmlCode.value || !htmlCode.value.trim()) {
    htmlError.value = '请输入HTML代码'
    return
  }
  
  isGeneratingHtml.value = true
  htmlError.value = null
  
  try {
    // 验证HTML代码（基本检查）
    const trimmedHtml = htmlCode.value.trim()
    
    // 如果没有基本的HTML结构，尝试包装
    let finalHtml = trimmedHtml
    if (!trimmedHtml.includes('<html') && !trimmedHtml.includes('<!DOCTYPE')) {
      // 如果没有完整的HTML结构，添加基本结构
      if (!trimmedHtml.includes('<head>')) {
        finalHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>交互式课件</title>
</head>
<body>
${trimmedHtml}
</body>
</html>`
      }
    }
    
    // 更新HTML代码
    htmlCode.value = finalHtml
    localContent.value.html_code = finalHtml
    
    // 生成Blob URL
    if (htmlBlobUrl.value) {
      URL.revokeObjectURL(htmlBlobUrl.value)
    }
    htmlBlobUrl.value = generateBlobUrlFromHtml(finalHtml)
    
    // 清除URL（如果之前有）
    localContent.value.url = undefined
    localContent.value.asset_id = undefined
    
    // 如果没有标题，设置默认标题
    if (!localContent.value.title) {
      localContent.value.title = '交互式课件'
    }
    
    updateCell()
  } catch (error) {
    console.error('生成HTML课件失败:', error)
    htmlError.value = '生成课件失败，请检查HTML代码格式'
  } finally {
    isGeneratingHtml.value = false
  }
}

// 清空HTML代码
function clearHtmlCode() {
  htmlCode.value = ''
  localContent.value.html_code = undefined
  if (htmlBlobUrl.value) {
    URL.revokeObjectURL(htmlBlobUrl.value)
    htmlBlobUrl.value = null
  }
  htmlError.value = null
  updateCell()
}

// 将HTML代码转换为File对象
function htmlCodeToFile(htmlCode: string, filename: string = 'interactive-courseware.html'): File {
  const blob = new Blob([htmlCode], { type: 'text/html' })
  return new File([blob], filename, { type: 'text/html' })
}

// 存储HTML代码到资源库
async function saveToLibrary() {
  if (!htmlCode.value || !htmlCode.value.trim()) {
    saveToLibraryError.value = 'HTML代码不能为空'
    return
  }

  if (!saveToLibraryForm.value.title.trim()) {
    saveToLibraryError.value = '请输入标题'
    return
  }

  isSavingToLibrary.value = true
  saveToLibraryError.value = null

  try {
    // 确保HTML代码是完整的
    let finalHtml = htmlCode.value.trim()
    if (!finalHtml.includes('<html') && !finalHtml.includes('<!DOCTYPE')) {
      if (!finalHtml.includes('<head>')) {
        finalHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${saveToLibraryForm.value.title}</title>
</head>
<body>
${finalHtml}
</body>
</html>`
      }
    }

    // 将HTML代码转换为File对象
    const htmlFile = htmlCodeToFile(finalHtml, `${saveToLibraryForm.value.title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.html`)

    // 上传到资源库
    const result = await libraryService.uploadAsset(htmlFile, {
      title: saveToLibraryForm.value.title,
      description: saveToLibraryForm.value.description || undefined,
      asset_type: 'interactive',
      visibility: 'teacher_only',
      knowledge_point_category: saveToLibraryForm.value.knowledgePoint.category,
      knowledge_point_name: saveToLibraryForm.value.knowledgePoint.name
    })

    // 上传成功，可以选择是否使用刚上传的资源
    if (confirm(`保存成功！是否使用刚保存的资源？`)) {
      // 加载刚上传的资源信息并设置为当前使用的资源
      const assetDetail = await libraryService.getAsset(result.id)
      handleAssetSelect({
        id: assetDetail.id,
        title: assetDetail.title,
        asset_type: assetDetail.asset_type as any,
        public_url: assetDetail.public_url,
        thumbnail_url: assetDetail.thumbnail_url,
        size_bytes: assetDetail.size_bytes,
        visibility: assetDetail.visibility as any,
        status: assetDetail.status as any,
        updated_at: assetDetail.updated_at,
        subject_id: assetDetail.subject_id,
        grade_id: assetDetail.grade_id,
      })
      sourceMode.value = 'library'
    }

    // 重置表单并关闭模态框
    saveToLibraryForm.value = { title: '', description: '', knowledgePoint: {} }
    showSaveToLibraryModal.value = false
  } catch (error: any) {
    console.error('保存到资源库失败:', error)
    saveToLibraryError.value = error?.response?.data?.detail || error?.message || '保存失败，请重试'
  } finally {
    isSavingToLibrary.value = false
  }
}

// 监听模态框打开，初始化表单
watch(showSaveToLibraryModal, (isOpen) => {
  if (isOpen) {
    // 使用当前标题或默认标题
    saveToLibraryForm.value.title = localContent.value.title || '交互式课件'
    saveToLibraryForm.value.description = localContent.value.description || ''
    saveToLibraryForm.value.knowledgePoint = {}
    saveToLibraryError.value = null
  }
})

// 更新 Cell
function updateCell() {
  const updatedCell: InteractiveCell = {
    ...props.cell,
    content: { ...localContent.value },
    config: localConfig.value ? { ...localConfig.value } : undefined
  }
  emit('update', updatedCell)
}

// 在新窗口预览
function previewUrl() {
  const url = displayUrl.value
  if (url && isValidUrl(url)) {
    window.open(url, '_blank', 'noopener,noreferrer')
  }
}

// 加载资产详情
async function loadAssetDetail(assetId: number) {
  try {
    const assetDetail: LibraryAssetDetail = await libraryService.getAsset(assetId)
    selectedAsset.value = {
      id: assetDetail.id,
      title: assetDetail.title,
      asset_type: assetDetail.asset_type as any,
      public_url: assetDetail.public_url,
      thumbnail_url: assetDetail.thumbnail_url,
      size_bytes: assetDetail.size_bytes,
      visibility: assetDetail.visibility as any,
      status: assetDetail.status as any,
      updated_at: assetDetail.updated_at,
      subject_id: assetDetail.subject_id,
      grade_id: assetDetail.grade_id,
    }
    // 更新本地内容
    if (assetDetail.public_url) {
      localContent.value.url = assetDetail.public_url
    }
    if (!localContent.value.title && assetDetail.title) {
      localContent.value.title = assetDetail.title
    }
    if (!localContent.value.description && assetDetail.description) {
      localContent.value.description = assetDetail.description
    }
    if (assetDetail.thumbnail_url) {
      localContent.value.thumbnail = assetDetail.thumbnail_url
    }
  } catch (error) {
    console.error('Failed to load asset detail:', error)
  }
}

// 监听 props.cell 的变化，同步到本地状态
watch(() => props.cell, (newCell) => {
  if (newCell) {
    localContent.value = { ...newCell.content }
    localConfig.value = {
      allowFullscreen: true,
      height: '800px',
      ...(newCell.config || {})
    }
    
    // 同步HTML代码
    if (newCell.content.html_code) {
      htmlCode.value = newCell.content.html_code
      if (props.editable) {
        if (htmlBlobUrl.value) {
          URL.revokeObjectURL(htmlBlobUrl.value)
        }
        htmlBlobUrl.value = generateBlobUrlFromHtml(newCell.content.html_code)
      } else {
        // 非编辑模式
        if (displayHtmlBlobUrl.value) {
          URL.revokeObjectURL(displayHtmlBlobUrl.value)
        }
        displayHtmlBlobUrl.value = generateBlobUrlFromHtml(newCell.content.html_code)
      }
    } else {
      // 清除HTML相关的Blob URL
      if (htmlBlobUrl.value) {
        URL.revokeObjectURL(htmlBlobUrl.value)
        htmlBlobUrl.value = null
      }
      if (displayHtmlBlobUrl.value) {
        URL.revokeObjectURL(displayHtmlBlobUrl.value)
        displayHtmlBlobUrl.value = null
      }
    }
    
    // 如果 cell 有 asset_id，需要加载资产信息
    if (newCell.content.asset_id && !selectedAsset.value) {
      loadAssetDetail(newCell.content.asset_id)
      sourceMode.value = 'library'
    } else if (newCell.content.html_code) {
      sourceMode.value = 'html'
    } else if (newCell.content.url) {
      sourceMode.value = 'url'
    }
  }
}, { deep: true, immediate: true })

// 监听 sourceMode 变化
watch(() => sourceMode.value, (newMode) => {
  if (newMode === 'url' && selectedAsset.value) {
    // 切换到 URL 模式时，保留 URL 但清除 asset_id
    localContent.value.asset_id = undefined
  } else if (newMode === 'html') {
    // 切换到 HTML 模式时，清除其他来源
    localContent.value.asset_id = undefined
    localContent.value.url = undefined
  } else if (newMode === 'library') {
    // 切换到资源库模式时，清除HTML代码
    htmlCode.value = ''
    localContent.value.html_code = undefined
    if (htmlBlobUrl.value) {
      URL.revokeObjectURL(htmlBlobUrl.value)
      htmlBlobUrl.value = null
    }
  }
})

// 组件挂载时，如果已有 asset_id，加载资产详情
onMounted(() => {
  if (props.cell.content?.asset_id && !selectedAsset.value) {
    loadAssetDetail(props.cell.content.asset_id)
    sourceMode.value = 'library'
  } else if (props.cell.content?.html_code) {
    sourceMode.value = 'html'
    htmlCode.value = props.cell.content.html_code
    if (props.editable) {
      htmlBlobUrl.value = generateBlobUrlFromHtml(props.cell.content.html_code)
    } else {
      // 非编辑模式，生成显示用的Blob URL
      displayHtmlBlobUrl.value = generateBlobUrlFromHtml(props.cell.content.html_code)
    }
  } else if (props.cell.content?.url) {
    sourceMode.value = 'url'
  }
})

// 组件卸载时清理Blob URL
onBeforeUnmount(() => {
  if (htmlBlobUrl.value) {
    URL.revokeObjectURL(htmlBlobUrl.value)
    htmlBlobUrl.value = null
  }
  if (displayHtmlBlobUrl.value) {
    URL.revokeObjectURL(displayHtmlBlobUrl.value)
    displayHtmlBlobUrl.value = null
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
.interactive-cell.fullscreen {
  @apply fixed inset-0 z-50 bg-white overflow-auto;
}

.interactive-cell.fullscreen .interactive-display {
  @apply h-full flex flex-col;
}

.interactive-cell {
  @apply w-full;
}

/* 编辑器样式 */
.interactive-editor {
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

/* 资源选择方式按钮 */
.source-options {
  @apply flex gap-2;
}

.source-option-btn {
  @apply flex items-center gap-2 px-4 py-2 border-2 border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all;
}

.source-option-btn.active {
  @apply border-blue-500 bg-blue-50 text-blue-700;
}

/* 资源库选择器 */
.library-picker-wrapper {
  @apply w-full;
}

.library-picker-btn {
  @apply w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all flex items-center justify-center gap-2 text-gray-600;
}

.selected-asset-card {
  @apply w-full p-4 border-2 border-purple-200 rounded-lg bg-purple-50;
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

.interactive-config {
  @apply mt-4 p-4 bg-gray-50 rounded-lg;
}

.interactive-config h4 {
  @apply text-sm font-semibold text-gray-700 mb-2;
}

.config-options {
  @apply grid grid-cols-1 gap-2 mb-4;
}

.config-options label {
  @apply flex items-center space-x-2 cursor-pointer;
}

/* 显示区域样式 */
.interactive-display {
  @apply w-full;
}

.interactive-info {
  @apply mb-4 p-4 bg-gray-50 rounded-lg;
}

.interactive-title {
  @apply text-lg font-semibold text-gray-900 mb-2;
}

.interactive-description {
  @apply text-sm text-gray-600;
}

.iframe-container {
  @apply w-full rounded-lg overflow-hidden border border-gray-200;
}

.interactive-iframe {
  @apply w-full border-0;
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

/* HTML编辑器样式 */
.html-editor-wrapper {
  @apply w-full;
}

.html-code-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm bg-white text-gray-900;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  resize: vertical;
  min-height: 200px;
}

.html-code-input::placeholder {
  @apply text-gray-400;
}

.html-code-input:focus {
  @apply border-blue-500 bg-white;
}

.html-code-input.error {
  @apply border-red-500 focus:ring-red-500;
}

.html-actions {
  @apply flex gap-2 mt-2;
}

.generate-html-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.clear-html-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors;
}

.save-to-library-btn {
  @apply flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
