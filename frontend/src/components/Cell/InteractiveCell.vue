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
            @click="useLibraryMode"
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
            @click="useHtmlMode"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            上传 HTML
          </button>
          <button
            :class="[
              'source-option-btn',
              sourceMode === 'collect' ? 'active' : ''
            ]"
            @click="useCollectMode"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            数据收集
          </button>
        </div>
      </div>

      <div v-if="sourceMode === 'collect'" class="form-group space-y-3">
        <p class="text-xs text-gray-500 leading-relaxed">
          把下面的提交地址写进页面。学生提交后，结果会出现在本单元。字段名由页面自己决定，建议带上「姓名」。
        </p>
        <label class="block text-sm font-medium text-gray-700">提交地址</label>
        <div class="url-input-wrapper">
          <input :value="collectSubmitUrl" type="text" readonly class="url-input" />
          <button type="button" class="preview-btn" title="复制提交地址" @click="copySubmitUrl">
            复制
          </button>
        </div>
        <p v-if="copyHint" class="text-xs text-green-700">{{ copyHint }}</p>
        <pre class="collect-snippet">fetch("{{ collectSubmitUrl }}", {
  method: "POST",
  headers: { "Content-Type": "text/plain;charset=UTF-8" },
  body: JSON.stringify({ 姓名: "张三", 完成: true })
})</pre>
      </div>

      <div v-if="sourceMode === 'library'" class="form-group space-y-3">
        <p class="text-xs text-gray-500 leading-relaxed">
          选择一条带访问链接的资源库课件。教师端与学生端使用同一份。
        </p>
        <div class="rounded-lg border border-gray-200 p-4 space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <button type="button" class="library-mini-btn" @click="openLibraryPicker">选择资源</button>
            <button
              v-if="selectedAsset || storedUrl"
              type="button"
              class="text-sm text-red-600 hover:text-red-800"
              @click="clearLibrary"
            >
              清除
            </button>
          </div>
          <div v-if="selectedAsset" class="selected-asset-card compact">
            <div class="flex items-center gap-3">
              <div class="flex-shrink-0 w-10 h-10 bg-purple-100 rounded flex items-center justify-center text-lg">🎮</div>
              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-900 truncate text-sm">{{ selectedAsset.title }}</h4>
                <p class="text-xs text-gray-500">{{ getAssetTypeLabel(selectedAsset.asset_type) }}</p>
              </div>
            </div>
          </div>
          <p v-else-if="storedUrl" class="text-xs text-gray-600 break-all">{{ storedUrl }}</p>
          <p v-else class="text-xs text-gray-400">未选择资源</p>
        </div>
      </div>

      <div v-if="sourceMode === 'html' || sourceMode === 'collect'" class="form-group space-y-4 mt-2">
        <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-4 mb-2">
          <div class="min-w-0 flex-1">
            <label class="block text-sm font-medium text-gray-700">HTML 代码</label>
            <p class="text-xs text-gray-500 mt-1 leading-relaxed">
              粘贴代码，或从本地上传 .html 文件。保存后教师端与学生端使用同一份。
            </p>
          </div>
          <button
            type="button"
            class="html-inline-upload-btn"
            title="从本地选择 .html 文件填入下方编辑器"
            @click="triggerLocalHtmlFile"
          >
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span>上传本地 HTML</span>
          </button>
        </div>
        <textarea
          v-model="htmlCode"
          @input="onHtmlInput"
          @paste="handlePaste"
          placeholder="粘贴或输入 HTML..."
          rows="12"
          class="html-code-input"
          :class="{ error: htmlError }"
        />
        <div class="html-actions mt-2 flex flex-wrap gap-2">
          <button
            v-if="htmlCode.trim()"
            type="button"
            @click="generateFromHtml"
            :disabled="isGeneratingHtml"
            class="generate-html-btn"
          >
            <div v-if="isGeneratingHtml" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            {{ isGeneratingHtml ? '生成中...' : '生成 / 包装文档' }}
          </button>
          <button
            v-if="htmlCode.trim()"
            type="button"
            @click="openSaveToLibraryModal"
            :disabled="isSavingToLibrary"
            class="save-to-library-btn"
          >
            {{ isSavingToLibrary ? '保存中...' : '存储到资源库' }}
          </button>
          <button v-if="htmlCode.trim()" type="button" @click="clearHtml" class="clear-html-btn">
            清空
          </button>
        </div>
        <p v-if="htmlError" class="error-text">{{ htmlError }}</p>
        <input
          ref="htmlFileInputRef"
          type="file"
          accept=".html,.htm,text/html"
          class="hidden"
          @change="onLocalHtmlFileChange"
        />
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

    <!-- 交互式课件显示区域。教师看收集结果时，表格在课件前面。 -->
    <div v-if="baseEmbedUrl || showCollectTable" class="interactive-display">
      <div v-if="displayContent.title || displayContent.description" class="interactive-info">
        <h3 v-if="displayContent.title" class="interactive-title">{{ displayContent.title }}</h3>
        <p v-if="displayContent.description" class="interactive-description">{{ displayContent.description }}</p>
      </div>

      <div v-if="showCollectTable" class="collect-board">
        <div class="collect-board-title">提交结果 {{ collectSubmissions.length }}</div>
        <p v-if="!collectSubmissions.length" class="collect-empty">还没有提交</p>
        <div v-else class="collect-table-wrap">
          <table class="collect-table">
            <thead>
              <tr>
                <th>姓名</th>
                <th>时间</th>
                <th v-for="column in collectColumns" :key="column">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in collectSubmissions" :key="row.id">
                <td>{{ row.student_label }}</td>
                <td>{{ formatCollectTime(row.created_at) }}</td>
                <td v-for="column in collectColumns" :key="column">{{ formatCollectValue(row.payload[column]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="baseEmbedUrl" class="iframe-container">
        <iframe
          ref="interactiveIframeRef"
          :src="iframeSrc || undefined"
          class="interactive-iframe"
          :style="iframeStyle"
          frameborder="0"
          allowfullscreen
          :sandbox="displayConfig?.sandbox?.join(' ') || 'allow-scripts allow-forms allow-popups'"
        ></iframe>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div v-if="!editable && !baseEmbedUrl" class="empty-state">
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
              <h3 class="text-xl font-semibold text-gray-900">选择课件资源</h3>
              <button @click="showLibraryPicker = false" class="text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-6">
              <AssetPicker ref="assetPicker" @select="handleAssetSelect" />
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
              <p class="text-xs text-gray-500 mb-3">把当前 HTML 存成资源库课件。</p>
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
import { getAssetTypeName } from '@/types/library'
import { useFullscreen } from '@/composables/useFullscreen'
import { libraryService } from '@/services/library'
import { coursewareService, type CollectSubmission } from '@/services/courseware'
import { getServerBaseUrl } from '@/utils/url'
import AssetPicker from '@/components/Library/AssetPicker.vue'
import KnowledgePointSelector from '@/components/Library/KnowledgePointSelector.vue'
import type { InteractiveViewerRole } from '@/utils/interactiveView'

interface Props {
  cell: InteractiveCell
  editable?: boolean
  /** 保留入参，课件本身不再按教师端 / 学生端分开展示 */
  interactiveViewerMode?: InteractiveViewerRole
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: InteractiveCell]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

const localContent = ref({ ...(props.cell.content || {}) })
const localConfig = ref<InteractiveCell['config']>({ 
  allowFullscreen: true,
  height: '800px',
  ...(props.cell.config || {})
})

function singleHtmlFromContent(c?: InteractiveCell['content']): string {
  if (!c) return ''
  return c.html_code?.trim() || c.student_html_code?.trim() || c.teacher_html_code?.trim() || ''
}

function singleAssetId(c?: InteractiveCell['content']): number | undefined {
  return c?.asset_id ?? c?.student_asset_id ?? c?.teacher_asset_id
}

function singleUrlFromContent(c?: InteractiveCell['content']): string {
  if (!c) return ''
  return c.url?.trim() || c.student_url?.trim() || c.teacher_url?.trim() || c.feixiang_url?.trim() || ''
}

function inferInteractiveSourceMode(c?: InteractiveCell['content']): 'library' | 'html' | 'collect' {
  if (!c) return 'html'
  if (c.collect_key?.trim()) return 'collect'
  if (singleAssetId(c)) return 'library'
  if (singleHtmlFromContent(c)) return 'html'
  if (singleUrlFromContent(c)) return 'library'
  return 'html'
}

const sourceMode = ref<'library' | 'html' | 'collect'>(inferInteractiveSourceMode(props.cell.content))
const showLibraryPicker = ref(false)
const selectedAsset = ref<LibraryAssetSummary | null>(null)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()
const htmlFileInputRef = ref<HTMLInputElement | null>(null)

const htmlCode = ref('')
const htmlError = ref<string | null>(null)
const isGeneratingHtml = ref(false)
const htmlBlobUrl = ref<string | null>(null)

const storedUrl = computed(() => singleUrlFromContent(localContent.value))

function generateBlobUrlFromHtml(html: string): string {
  const blob = new Blob([html], { type: 'text/html' })
  return URL.createObjectURL(blob)
}

function revokeHtmlBlob() {
  if (htmlBlobUrl.value) {
    URL.revokeObjectURL(htmlBlobUrl.value)
    htmlBlobUrl.value = null
  }
}
function refreshHtmlBlob() {
  revokeHtmlBlob()
  if (htmlCode.value.trim()) {
    htmlBlobUrl.value = generateBlobUrlFromHtml(htmlCode.value)
  }
}

function syncHtmlRefsFromCellContent(c?: InteractiveCell['content']) {
  htmlCode.value = singleHtmlFromContent(c)
  refreshHtmlBlob()
}

function getAssetTypeLabel(assetType: string) {
  return getAssetTypeName(assetType as any)
}

function openLibraryPicker() {
  showLibraryPicker.value = true
}

function triggerLocalHtmlFile() {
  htmlFileInputRef.value?.click()
}

function onLocalHtmlFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    htmlCode.value = String(reader.result ?? '')
    refreshHtmlBlob()
    htmlError.value = null
    if (sourceMode.value !== 'collect') sourceMode.value = 'html'
    updateCell()
    input.value = ''
  }
  reader.readAsText(file)
}

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

  // 如果是完整 URL，检查是否需要转换协议
  if (isValidUrl(url)) {
    // 如果当前页面是HTTPS，强制将资源URL转换为HTTPS
    if (window.location.protocol === 'https:') {
      return url.replace(/^http:\/\//i, 'https://')
    }
    return url
  }

  // 如果是相对路径，转换为完整 URL
  if (url.startsWith('/')) {
    const baseURL = getServerBaseUrl()
    return `${baseURL}${url}`
  }

  return null
}

// 非编辑模式下的HTML Blob URL（避免重复生成）
const displayHtmlBlobUrl = ref<string | null>(null)
const interactiveIframeRef = ref<HTMLIFrameElement | null>(null)

const readonlyHtmlSource = computed(() => {
  if (props.editable) return ''
  return singleHtmlFromContent(props.cell.content)
})

watch(
  () => [readonlyHtmlSource.value, props.editable] as const,
  () => {
    if (props.editable) return
    if (displayHtmlBlobUrl.value) {
      URL.revokeObjectURL(displayHtmlBlobUrl.value)
      displayHtmlBlobUrl.value = null
    }
    const src = readonlyHtmlSource.value.trim()
    if (src) {
      displayHtmlBlobUrl.value = generateBlobUrlFromHtml(src)
    }
  },
  { immediate: true }
)

function normalizeResolvedHttp(u: string | undefined | null): string | null {
  if (!u?.trim()) return null
  return resolveUrl(u.trim())
}

function contentHttpUrl(c?: InteractiveCell['content']): string | null {
  return normalizeResolvedHttp(singleUrlFromContent(c))
}

const baseEmbedUrl = computed(() => {
  if (props.editable) {
    if ((sourceMode.value === 'html' || sourceMode.value === 'collect') && htmlCode.value.trim() && htmlBlobUrl.value) {
      return htmlBlobUrl.value
    }
    return normalizeResolvedHttp(selectedAsset.value?.public_url) || contentHttpUrl(localContent.value)
  }
  const htmlReady = readonlyHtmlSource.value.trim() && displayHtmlBlobUrl.value
  if (htmlReady) return displayHtmlBlobUrl.value
  return contentHttpUrl(props.cell.content) || displayHtmlBlobUrl.value
})

const iframeSrc = computed(() => baseEmbedUrl.value)

const displayContent = computed(() => {
  return props.editable ? localContent.value : (props.cell.content || {} as InteractiveCell['content'])
})

const displayConfig = computed(() => {
  return props.editable ? localConfig.value : (props.cell.config || {} as InteractiveCell['config'])
})

const iframeStyle = computed(() => {
  const configuredWidth = displayConfig.value?.width?.trim()
  const configuredHeight = displayConfig.value?.height?.trim() || '800px'
  const height = isFullscreen.value && showCollectTable.value ? '100%' : configuredHeight

  return {
    width: '100%',
    maxWidth: configuredWidth && configuredWidth !== '100%' ? configuredWidth : '100%',
    height,
  }
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

function mapDetailToSummary(assetDetail: LibraryAssetDetail): LibraryAssetSummary {
  return {
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
    view_count: assetDetail.view_count,
  }
}

function clearSplitFields() {
  const c = localContent.value
  c.teacher_asset_id = undefined
  c.student_asset_id = undefined
  c.teacher_url = undefined
  c.student_url = undefined
  c.teacher_html_code = undefined
  c.student_html_code = undefined
  c.feixiang_url = undefined
}

function handleAssetSelect(asset: LibraryAssetSummary | null) {
  if (!asset) {
    clearLibrary()
    showLibraryPicker.value = false
    return
  }
  if (!asset.public_url?.trim()) {
    window.alert('该资源没有可用的访问链接，请选择其他资源或改为上传 HTML。')
    return
  }
  selectedAsset.value = asset
  localContent.value.title = localContent.value.title || asset.title
  if (asset.thumbnail_url) {
    localContent.value.thumbnail = asset.thumbnail_url || localContent.value.thumbnail
  }
  localContent.value.asset_id = asset.id
  localContent.value.url = asset.public_url || undefined
  htmlCode.value = ''
  revokeHtmlBlob()
  sourceMode.value = 'library'
  showLibraryPicker.value = false
  updateCell()
}

function clearLibrary() {
  selectedAsset.value = null
  localContent.value.asset_id = undefined
  localContent.value.url = undefined
  updateCell()
}

async function loadAssetDetail(assetId: number) {
  try {
    const assetDetail = await libraryService.getAsset(assetId)
    selectedAsset.value = mapDetailToSummary(assetDetail)
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
    console.error('Failed to load asset:', error)
  }
}

function persistHtmlToLocalContent() {
  const html = htmlCode.value.trim()
  localContent.value.html_code = html || undefined
  clearSplitFields()
  if (html) {
    localContent.value.url = undefined
    localContent.value.asset_id = undefined
    selectedAsset.value = null
  }
}

function onHtmlInput() {
  htmlError.value = null
  if (sourceMode.value !== 'collect') sourceMode.value = 'html'
  refreshHtmlBlob()
  updateCell()
}

// 处理粘贴事件（自动清理格式）
function handlePaste(_event: ClipboardEvent) {
  // 默认粘贴
}

function wrapHtmlFragment(trimmedHtml: string, docTitle: string): string {
  if (trimmedHtml.includes('<html') || trimmedHtml.includes('<!DOCTYPE')) {
    return trimmedHtml
  }
  if (trimmedHtml.includes('<head>')) {
    return trimmedHtml
  }
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${docTitle}</title>
</head>
<body>
${trimmedHtml}
</body>
</html>`
}

function generateFromHtml() {
  const raw = htmlCode.value
  if (!raw || !raw.trim()) {
    htmlError.value = '请输入HTML代码'
    return
  }

  isGeneratingHtml.value = true
  htmlError.value = null

  try {
    htmlCode.value = wrapHtmlFragment(raw.trim(), '交互式课件')
    refreshHtmlBlob()
    if (sourceMode.value !== 'collect') sourceMode.value = 'html'
    selectedAsset.value = null
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

function clearHtml() {
  htmlCode.value = ''
  revokeHtmlBlob()
  htmlError.value = null
  updateCell()
}

function openSaveToLibraryModal() {
  showSaveToLibraryModal.value = true
}

// 将HTML代码转换为File对象
function htmlCodeToFile(html: string, filename: string = 'interactive-courseware.html'): File {
  const blob = new Blob([html], { type: 'text/html' })
  return new File([blob], filename, { type: 'text/html' })
}

// 存储HTML代码到资源库
async function saveToLibrary() {
  const raw = htmlCode.value
  if (!raw || !raw.trim()) {
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
    let finalHtml = raw.trim()
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
      handleAssetSelect(mapDetailToSummary(assetDetail))
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

function ensureCollectKey() {
  if (!localContent.value.collect_key?.trim()) {
    localContent.value.collect_key = crypto.randomUUID()
  }
}

function useLibraryMode() {
  sourceMode.value = 'library'
  updateCell()
}

function useHtmlMode() {
  sourceMode.value = 'html'
  updateCell()
}

function useCollectMode() {
  sourceMode.value = 'collect'
  ensureCollectKey()
  updateCell()
}

const collectSubmitUrl = computed(() => {
  const key = localContent.value.collect_key?.trim()
  if (!key) return ''
  return `${getServerBaseUrl()}/api/v1/courseware/collect/${key}/submit`
})

const collectSubmissions = ref<CollectSubmission[]>([])
const copyHint = ref('')
let collectTimer: number | null = null

const showCollectBoard = computed(() => {
  if (!displayContent.value.collect_key?.trim()) return false
  return props.editable || props.interactiveViewerMode === 'teacher'
})

const showCollectTable = computed(() => {
  if (!showCollectBoard.value) return false
  return !props.editable || sourceMode.value === 'collect'
})

const collectColumns = computed(() => {
  const skip = new Set(['姓名', 'name', 'student_name', '学生'])
  const columns: string[] = []
  for (const row of collectSubmissions.value) {
    for (const key of Object.keys(row.payload || {})) {
      if (!skip.has(key) && !columns.includes(key)) columns.push(key)
    }
  }
  return columns
})

function formatCollectTime(value: string) {
  const hasZone = /(?:Z|[+-]\d{2}:\d{2})$/.test(value)
  const date = new Date(hasZone ? value : `${value}Z`)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false, month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function formatCollectValue(value: unknown) {
  if (value == null || value === '') return ''
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (typeof value === 'string' || typeof value === 'number') return String(value)
  return JSON.stringify(value)
}

async function refreshCollectSubmissions() {
  const key = (props.editable ? localContent.value.collect_key : props.cell.content?.collect_key)?.trim()
  if (!key || !showCollectBoard.value) return
  try {
    collectSubmissions.value = await coursewareService.listCollectSubmissions(key)
  } catch {
    /* 未登录或暂无权限时不打断编辑 */
  }
}

function stopCollectPolling() {
  if (collectTimer !== null) {
    window.clearInterval(collectTimer)
    collectTimer = null
  }
}

function startCollectPolling() {
  stopCollectPolling()
  if (!showCollectBoard.value) return
  void refreshCollectSubmissions()
  collectTimer = window.setInterval(() => {
    void refreshCollectSubmissions()
  }, 5000)
}

async function copySubmitUrl() {
  if (!collectSubmitUrl.value) return
  try {
    await navigator.clipboard.writeText(collectSubmitUrl.value)
    copyHint.value = '已复制'
  } catch {
    copyHint.value = '请手动复制地址'
  }
}

function updateCell() {
  if (sourceMode.value === 'html' || sourceMode.value === 'collect') {
    persistHtmlToLocalContent()
    if (sourceMode.value === 'collect') ensureCollectKey()
    else localContent.value.collect_key = undefined
  } else {
    localContent.value.html_code = undefined
    localContent.value.collect_key = undefined
    clearSplitFields()
    if (selectedAsset.value) {
      localContent.value.asset_id = selectedAsset.value.id
      localContent.value.url = selectedAsset.value.public_url || localContent.value.url
    }
  }
  const updatedCell: InteractiveCell = {
    ...props.cell,
    content: { ...localContent.value },
    config: localConfig.value ? { ...localConfig.value } : undefined
  }
  emit('update', updatedCell)
}

// 监听 props.cell 的变化，同步到本地状态
watch(
  () => props.cell,
  (newCell) => {
    if (!newCell) return
    localContent.value = { ...(newCell.content || {}) }
    const legacyUrl = singleUrlFromContent(newCell.content)
    if (legacyUrl) localContent.value.url = legacyUrl
    const legacyAssetId = singleAssetId(newCell.content)
    if (legacyAssetId) localContent.value.asset_id = legacyAssetId
    localConfig.value = {
      allowFullscreen: true,
      height: '800px',
      ...(newCell.config || {}),
    }

    syncHtmlRefsFromCellContent(newCell.content)

    if (legacyAssetId) {
      if (selectedAsset.value?.id !== legacyAssetId) loadAssetDetail(legacyAssetId)
    } else {
      selectedAsset.value = null
    }

    sourceMode.value = inferInteractiveSourceMode(newCell.content)
  },
  { deep: true, immediate: true }
)

onMounted(() => {
  const c = props.cell.content
  if (c) {
    const legacyUrl = singleUrlFromContent(c)
    if (legacyUrl) localContent.value.url = legacyUrl
    const legacyAssetId = singleAssetId(c)
    if (legacyAssetId) localContent.value.asset_id = legacyAssetId
    syncHtmlRefsFromCellContent(c)
    if (legacyAssetId) loadAssetDetail(legacyAssetId)
    sourceMode.value = inferInteractiveSourceMode(c)
  }
  startCollectPolling()
})

watch(showCollectBoard, () => {
  startCollectPolling()
})

onBeforeUnmount(() => {
  if (interactiveIframeRef.value?.src && interactiveIframeRef.value.src.startsWith('blob:')) {
    interactiveIframeRef.value.src = 'about:blank'
  }
  revokeHtmlBlob()
  stopCollectPolling()
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
  @apply h-full flex flex-col min-h-0;
}

.interactive-cell.fullscreen .collect-board {
  @apply max-h-[45%] shrink-0 overflow-hidden flex flex-col;
}

.interactive-cell.fullscreen .collect-table-wrap {
  @apply min-h-0;
}

.interactive-cell.fullscreen .iframe-container {
  @apply flex-1 min-h-0;
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
  @apply flex flex-wrap gap-2;
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

.selected-asset-card.compact {
  @apply p-3 border border-purple-200;
}

.library-mini-btn {
  @apply px-3 py-1.5 text-sm font-medium rounded-md bg-purple-600 text-white hover:bg-purple-700 transition-colors;
}

.library-mini-btn-secondary {
  @apply px-3 py-1.5 text-sm font-medium rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 transition-colors;
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
  @apply w-full rounded-lg overflow-x-auto overflow-y-hidden border border-gray-200;
}

.interactive-iframe {
  @apply block w-full max-w-full border-0;
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

.html-inline-upload-btn {
  @apply inline-flex items-center justify-center gap-2 self-start sm:flex-shrink-0 px-3 py-2 text-xs font-medium rounded-lg border border-gray-300 bg-white text-gray-700 shadow-sm hover:bg-gray-50 hover:border-gray-400 transition-colors;
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

.collect-snippet {
  @apply text-xs leading-relaxed bg-gray-900 text-gray-100 rounded-md p-3 overflow-x-auto whitespace-pre-wrap;
}

.collect-board {
  @apply mb-3 rounded-lg border border-gray-200 bg-white p-3 space-y-2;
}

.collect-board-title {
  @apply text-sm font-medium text-gray-900;
}

.collect-empty {
  @apply text-sm text-gray-400;
}

.collect-table-wrap {
  @apply overflow-auto max-h-80;
}

.collect-table {
  @apply w-full text-sm text-left border-collapse;
}

.collect-table th,
.collect-table td {
  @apply px-3 py-2 border-b border-gray-100 align-top;
}

.collect-table th {
  @apply sticky top-0 bg-gray-50 font-medium text-gray-700 whitespace-nowrap;
}

.collect-table td {
  @apply text-gray-800;
}
</style>
