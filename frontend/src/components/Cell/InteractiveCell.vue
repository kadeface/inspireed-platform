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

      <!-- 从资源库选择（教师 / 学生可分别选择；可选任意带访问链接的资源） -->
      <div v-if="sourceMode === 'library'" class="form-group space-y-6">
        <p class="text-xs text-gray-500 leading-relaxed">
          教师大屏与学生活动可各选一条资源库素材（需带访问链接）；请选择类型或使用搜索筛选。
        </p>

        <div class="rounded-lg border border-gray-200 p-4 space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-sm font-medium text-gray-800">教师大屏 — 资源库</span>
            <button type="button" class="library-mini-btn" @click="openLibraryPicker('teacher')">选择资源</button>
            <button
              v-if="selectedTeacherAsset || localContent.teacher_url"
              type="button"
              class="text-sm text-red-600 hover:text-red-800"
              @click="clearLibrarySide('teacher')"
            >
              清除
            </button>
          </div>
          <div v-if="selectedTeacherAsset" class="selected-asset-card compact">
            <div class="flex items-center gap-3">
              <div class="flex-shrink-0 w-10 h-10 bg-purple-100 rounded flex items-center justify-center text-lg">🎮</div>
              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-900 truncate text-sm">{{ selectedTeacherAsset.title }}</h4>
                <p class="text-xs text-gray-500">{{ getAssetTypeLabel(selectedTeacherAsset.asset_type) }}</p>
              </div>
            </div>
          </div>
          <p v-else-if="localContent.teacher_url" class="text-xs text-gray-600 break-all">{{ localContent.teacher_url }}</p>
          <p v-else class="text-xs text-gray-400">未选择教师侧资源</p>
        </div>

        <div class="rounded-lg border border-gray-200 p-4 space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-sm font-medium text-gray-800">学生活动 — 资源库</span>
            <button type="button" class="library-mini-btn" @click="openLibraryPicker('student')">选择资源</button>
            <button
              v-if="selectedStudentAsset || localContent.student_url || localContent.url"
              type="button"
              class="text-sm text-red-600 hover:text-red-800"
              @click="clearLibrarySide('student')"
            >
              清除
            </button>
          </div>
          <div v-if="selectedStudentAsset" class="selected-asset-card compact">
            <div class="flex items-center gap-3">
              <div class="flex-shrink-0 w-10 h-10 bg-purple-100 rounded flex items-center justify-center text-lg">🎮</div>
              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-900 truncate text-sm">{{ selectedStudentAsset.title }}</h4>
                <p class="text-xs text-gray-500">{{ getAssetTypeLabel(selectedStudentAsset.asset_type) }}</p>
              </div>
            </div>
          </div>
          <p v-else-if="studentUrlModel" class="text-xs text-gray-600 break-all">{{ studentUrlModel }}</p>
          <p v-else class="text-xs text-gray-400">未选择学生侧资源</p>
        </div>
      </div>

      <!-- 输入 URL（教师 / 学生各一条） -->
      <div v-if="sourceMode === 'url'" class="form-group space-y-6">
        <p class="text-xs text-gray-500 leading-relaxed">
          为师生分别填写可嵌入的 http(s) 链接；保存后分别用于授课大屏与学生活动预览。
        </p>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">教师大屏 URL</label>
          <div class="url-input-wrapper">
            <input
              v-model="localContent.teacher_url"
              type="url"
              placeholder="https://example.com/teacher.html"
              @blur="validateUrlsAndUpdate"
              class="url-input"
              :class="{ error: teacherUrlError }"
            />
            <button
              v-if="localContent.teacher_url && isValidUrl(localContent.teacher_url)"
              type="button"
              @click="previewExternalUrl(localContent.teacher_url)"
              class="preview-btn"
              title="在新窗口预览"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </button>
          </div>
          <p v-if="teacherUrlError" class="error-text">{{ teacherUrlError }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">学生活动 URL</label>
          <div class="url-input-wrapper">
            <input
              v-model="studentUrlModel"
              type="url"
              placeholder="https://example.com/student.html"
              @blur="validateUrlsAndUpdate"
              class="url-input"
              :class="{ error: studentUrlError }"
            />
            <button
              v-if="studentUrlModel && isValidUrl(studentUrlModel)"
              type="button"
              @click="previewExternalUrl(studentUrlModel)"
              class="preview-btn"
              title="在新窗口预览"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </button>
          </div>
          <p v-if="studentUrlError" class="error-text">{{ studentUrlError }}</p>
        </div>
      </div>

      <!-- 粘贴 HTML（仅在选择「粘贴 HTML」模式时显示） -->
      <div v-if="sourceMode === 'html'" class="form-group space-y-8 mt-2">
        <div>
          <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-4 mb-2">
            <div class="min-w-0 flex-1">
              <label class="block text-sm font-medium text-gray-700">教师大屏 HTML</label>
              <p class="text-xs text-gray-500 mt-1 leading-relaxed">
                若此处留空，教师预览与授课大屏将自动使用「学生活动 HTML」（或旧版单页
                <code class="rounded bg-gray-100 px-0.5">html_code</code>）。
              </p>
            </div>
            <button
              type="button"
              class="html-inline-upload-btn"
              title="从本地选择 .html 文件填入下方编辑器"
              @click="triggerLocalHtmlFile('teacher')"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span>上传本地 HTML</span>
            </button>
          </div>
          <textarea
            v-model="teacherHtmlCode"
            @input="onTeacherHtmlInput"
            @paste="handlePaste"
            placeholder="粘贴或输入教师端大屏页面 HTML..."
            rows="10"
            class="html-code-input"
            :class="{ 'error': htmlError && htmlErrorField === 'teacher' }"
          />
          <div class="html-actions mt-2 flex flex-wrap gap-2">
            <button
              v-if="teacherHtmlCode.trim()"
              type="button"
              @click="generateFromHtml('teacher')"
              :disabled="isGeneratingTeacherHtml"
              class="generate-html-btn"
            >
              <div v-if="isGeneratingTeacherHtml" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {{ isGeneratingTeacherHtml ? '生成中...' : '生成 / 包装文档' }}
            </button>
            <button
              v-if="teacherHtmlCode.trim()"
              type="button"
              @click="openSaveToLibraryModal('teacher')"
              :disabled="isSavingToLibrary"
              class="save-to-library-btn"
            >
              {{ isSavingToLibrary && saveToLibrarySide === 'teacher' ? '保存中...' : '存储到资源库' }}
            </button>
            <button v-if="teacherHtmlCode.trim()" type="button" @click="clearTeacherHtml" class="clear-html-btn">
              清空教师端
            </button>
          </div>
        </div>
        <div>
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4 mb-2">
            <label class="block text-sm font-medium text-gray-700 sm:mb-0">学生活动 HTML</label>
            <button
              type="button"
              class="html-inline-upload-btn"
              title="从本地选择 .html 文件填入下方编辑器"
              @click="triggerLocalHtmlFile('student')"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span>上传本地 HTML</span>
            </button>
          </div>
          <textarea
            v-model="studentHtmlCode"
            @input="onStudentHtmlInput"
            @paste="handlePaste"
            placeholder="粘贴或输入学生端活动页 HTML..."
            rows="10"
            class="html-code-input"
            :class="{ 'error': htmlError && htmlErrorField === 'student' }"
          />
          <div class="html-actions mt-2 flex flex-wrap gap-2">
            <button
              v-if="studentHtmlCode.trim()"
              type="button"
              @click="generateFromHtml('student')"
              :disabled="isGeneratingStudentHtml"
              class="generate-html-btn"
            >
              <div v-if="isGeneratingStudentHtml" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {{ isGeneratingStudentHtml ? '生成中...' : '生成 / 包装文档' }}
            </button>
            <button
              v-if="studentHtmlCode.trim()"
              type="button"
              @click="openSaveToLibraryModal('student')"
              :disabled="isSavingToLibrary"
              class="save-to-library-btn"
            >
              {{ isSavingToLibrary && saveToLibrarySide === 'student' ? '保存中...' : '存储到资源库' }}
            </button>
            <button v-if="studentHtmlCode.trim()" type="button" @click="clearStudentHtml" class="clear-html-btn">
              清空学生端
            </button>
          </div>
        </div>
        <p v-if="htmlError" class="error-text">{{ htmlError }}</p>
        <p v-else class="hint-text">
          教师端与学生端可分别粘贴完整 HTML；保存后教案中分别存储。若仍使用单页 + URL 参数
          <code class="rounded bg-gray-100 px-1">view=teacher|student</code>，也可只在其中一栏粘贴并在课件内分支。
        </p>

        <input
          ref="teacherHtmlFileInputRef"
          type="file"
          accept=".html,.htm,text/html"
          class="hidden"
          @change="onLocalHtmlFileChange('teacher', $event)"
        />
        <input
          ref="studentHtmlFileInputRef"
          type="file"
          accept=".html,.htm,text/html"
          class="hidden"
          @change="onLocalHtmlFileChange('student', $event)"
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

    <!-- 交互式课件显示区域 -->
    <div v-if="baseEmbedUrl" class="interactive-display">
      <!-- 标题和描述显示 -->
      <div v-if="displayContent.title || displayContent.description" class="interactive-info">
        <h3 v-if="displayContent.title" class="interactive-title">{{ displayContent.title }}</h3>
        <p v-if="displayContent.description" class="interactive-description">{{ displayContent.description }}</p>
      </div>

      <!-- iframe 嵌入：ref 用于卸载前清空 src，避免 blob 被 revoke 后报错 -->
      <div class="iframe-container">
        <iframe
          ref="interactiveIframeRef"
          :src="iframeSrc || undefined"
          class="interactive-iframe"
          :style="iframeStyle"
          frameborder="0"
          allowfullscreen
          :sandbox="displayConfig?.sandbox?.join(' ') || 'allow-scripts allow-forms allow-popups'"
          @load="onInteractiveIframeLoad"
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
              <h3 class="text-xl font-semibold text-gray-900">
                {{ libraryPickSide === 'teacher' ? '选择教师大屏资源' : '选择学生活动资源' }}
              </h3>
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
              <p class="text-xs text-gray-500 mb-3">
                上传来源：<span class="font-medium text-gray-800">{{ saveToLibrarySide === 'teacher' ? '教师大屏 HTML' : '学生活动 HTML' }}</span>
              </p>
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
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import type { InteractiveCell } from '../../types/cell'
import type { LibraryAssetSummary, LibraryAssetDetail } from '../../types/library'
import { getAssetTypeName } from '@/types/library'
import { useFullscreen } from '@/composables/useFullscreen'
import { libraryService } from '@/services/library'
import { getServerBaseUrl } from '@/utils/url'
import AssetPicker from '@/components/Library/AssetPicker.vue'
import KnowledgePointSelector from '@/components/Library/KnowledgePointSelector.vue'
import type { InteractiveViewerRole } from '@/utils/interactiveView'
import {
  appendInteractiveViewToUrl,
  buildInspireedInteractiveViewMessage,
} from '@/utils/interactiveView'

interface Props {
  cell: InteractiveCell
  editable?: boolean
  /** 教师大屏 teacher / 学生活动 student；未传时默认 student */
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

const teacherUrlError = ref<string | null>(null)
const studentUrlError = ref<string | null>(null)

function interactiveHasAnyHtml(c?: InteractiveCell['content']): boolean {
  if (!c) return false
  return !!(c.html_code?.trim() || c.teacher_html_code?.trim() || c.student_html_code?.trim())
}

function inferInteractiveSourceMode(c?: InteractiveCell['content']): 'library' | 'html' | 'url' {
  if (!c) return 'html'
  if (c.teacher_asset_id || c.student_asset_id || c.asset_id) return 'library'
  if (interactiveHasAnyHtml(c)) return 'html'
  const hasUrl = !!(c.teacher_url?.trim() || c.student_url?.trim() || c.url?.trim())
  if (hasUrl) return 'url'
  return 'html'
}

const sourceMode = ref<'library' | 'html' | 'url'>(inferInteractiveSourceMode(props.cell.content))
const showLibraryPicker = ref(false)
const libraryPickSide = ref<'teacher' | 'student'>('student')
const selectedTeacherAsset = ref<LibraryAssetSummary | null>(null)
const selectedStudentAsset = ref<LibraryAssetSummary | null>(null)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()
const teacherHtmlFileInputRef = ref<HTMLInputElement | null>(null)
const studentHtmlFileInputRef = ref<HTMLInputElement | null>(null)

/** 教师 / 学生 双栏 HTML（编辑区） */
const teacherHtmlCode = ref('')
const studentHtmlCode = ref('')
const htmlError = ref<string | null>(null)
const htmlErrorField = ref<'teacher' | 'student' | null>(null)
const isGeneratingTeacherHtml = ref(false)
const isGeneratingStudentHtml = ref(false)
const teacherHtmlBlobUrl = ref<string | null>(null)
const studentHtmlBlobUrl = ref<string | null>(null)

function generateBlobUrlFromHtml(html: string): string {
  const blob = new Blob([html], { type: 'text/html' })
  return URL.createObjectURL(blob)
}

function revokeTeacherBlob() {
  if (teacherHtmlBlobUrl.value) {
    URL.revokeObjectURL(teacherHtmlBlobUrl.value)
    teacherHtmlBlobUrl.value = null
  }
}
function revokeStudentBlob() {
  if (studentHtmlBlobUrl.value) {
    URL.revokeObjectURL(studentHtmlBlobUrl.value)
    studentHtmlBlobUrl.value = null
  }
}
function refreshTeacherBlob() {
  revokeTeacherBlob()
  if (teacherHtmlCode.value.trim()) {
    teacherHtmlBlobUrl.value = generateBlobUrlFromHtml(teacherHtmlCode.value)
  }
}
function refreshStudentBlob() {
  revokeStudentBlob()
  if (studentHtmlCode.value.trim()) {
    studentHtmlBlobUrl.value = generateBlobUrlFromHtml(studentHtmlCode.value)
  }
}

function syncHtmlRefsFromCellContent(c?: InteractiveCell['content']) {
  teacherHtmlCode.value = c?.teacher_html_code || ''
  studentHtmlCode.value = c?.student_html_code || c?.html_code || ''
  refreshTeacherBlob()
  refreshStudentBlob()
}

const studentUrlModel = computed({
  get() {
    return localContent.value.student_url ?? localContent.value.url ?? ''
  },
  set(v: string) {
    const trimmed = v.trim()
    localContent.value.student_url = trimmed || undefined
    localContent.value.url = trimmed || undefined
  },
})

function getAssetTypeLabel(assetType: string) {
  return getAssetTypeName(assetType as any)
}

function openLibraryPicker(side: 'teacher' | 'student') {
  libraryPickSide.value = side
  showLibraryPicker.value = true
}

function triggerLocalHtmlFile(side: 'teacher' | 'student') {
  if (side === 'teacher') teacherHtmlFileInputRef.value?.click()
  else studentHtmlFileInputRef.value?.click()
}

function onLocalHtmlFileChange(side: 'teacher' | 'student', e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    const text = String(reader.result ?? '')
    if (side === 'teacher') {
      teacherHtmlCode.value = text
      refreshTeacherBlob()
    } else {
      studentHtmlCode.value = text
      refreshStudentBlob()
    }
    htmlError.value = null
    htmlErrorField.value = null
    updateCell()
    input.value = ''
  }
  reader.readAsText(file)
}

// 存储到资源库相关状态
const showSaveToLibraryModal = ref(false)
const saveToLibrarySide = ref<'teacher' | 'student'>('student')
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

const effectiveInteractiveView = computed<InteractiveViewerRole>(
  () => props.interactiveViewerMode ?? 'student'
)

/** 只读：当前角色应展示的 HTML 源码（用于生成 blob）。教师端无内容时依次使用学生 HTML、旧版 html_code。 */
const readonlyHtmlSource = computed(() => {
  if (props.editable) return ''
  const c = props.cell.content
  if (!c) return ''
  const role = effectiveInteractiveView.value
  const leg = c.html_code?.trim() || ''
  const t = c.teacher_html_code?.trim() || ''
  const s = c.student_html_code?.trim() || ''
  if (!t && !s && leg) return leg
  if (role === 'teacher') {
    return t || s || leg
  }
  return s || t || leg
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

function editableBlobForRole(role: InteractiveViewerRole): string | null {
  if (sourceMode.value !== 'html') return null
  if (role === 'teacher') {
    if (teacherHtmlCode.value.trim() && teacherHtmlBlobUrl.value) return teacherHtmlBlobUrl.value
    if (studentHtmlCode.value.trim() && studentHtmlBlobUrl.value) return studentHtmlBlobUrl.value
    return null
  }
  if (studentHtmlCode.value.trim() && studentHtmlBlobUrl.value) return studentHtmlBlobUrl.value
  if (teacherHtmlCode.value.trim() && teacherHtmlBlobUrl.value) return teacherHtmlBlobUrl.value
  return null
}

function editableHttpUrlForRole(role: InteractiveViewerRole): string | null {
  const lc = localContent.value
  if (role === 'teacher') {
    let u = normalizeResolvedHttp(lc.teacher_url)
    if (u) return u
    u = normalizeResolvedHttp(selectedTeacherAsset.value?.public_url)
    if (u) return u
    u = normalizeResolvedHttp(lc.student_url || lc.url)
    if (u) return u
    u = normalizeResolvedHttp(selectedStudentAsset.value?.public_url)
    return u
  }
  let u = normalizeResolvedHttp(lc.student_url || lc.url)
  if (u) return u
  u = normalizeResolvedHttp(selectedStudentAsset.value?.public_url)
  if (u) return u
  u = normalizeResolvedHttp(lc.teacher_url)
  if (u) return u
  u = normalizeResolvedHttp(selectedTeacherAsset.value?.public_url)
  return u
}

function readonlyHttpUrlForRole(
  c: InteractiveCell['content'] | undefined,
  role: InteractiveViewerRole
): string | null {
  if (!c) return null
  const legacy = c.url?.trim()
  if (role === 'teacher') {
    let u = normalizeResolvedHttp(c.teacher_url)
    if (u) return u
    u = normalizeResolvedHttp(c.student_url || legacy)
    return u
  }
  let u = normalizeResolvedHttp(c.student_url || legacy)
  if (u) return u
  u = normalizeResolvedHttp(c.teacher_url)
  return u
}

/** 嵌入用原始地址（不含 view 参数）。粘贴 HTML 优先于资源库 / URL；教师侧 URL/HTML 空时回落到学生侧。 */
const baseEmbedUrl = computed(() => {
  const role = effectiveInteractiveView.value
  if (props.editable) {
    const blob = editableBlobForRole(role)
    if (blob) return blob
    const http = editableHttpUrlForRole(role)
    if (http) return http
    return null
  }
  const c = props.cell.content
  const htmlReady = readonlyHtmlSource.value.trim() && displayHtmlBlobUrl.value
  if (htmlReady) return displayHtmlBlobUrl.value
  const httpReadonly = readonlyHttpUrlForRole(c, role)
  if (httpReadonly) return httpReadonly
  return displayHtmlBlobUrl.value
})

/** iframe 实际地址：http(s) 追加 view=；blob 不变，由 postMessage 传角色 */
const iframeSrc = computed(() => {
  const base = baseEmbedUrl.value
  if (!base) return null
  return appendInteractiveViewToUrl(base, effectiveInteractiveView.value) || base
})

function postInteractiveViewToIframe() {
  const frame = interactiveIframeRef.value
  if (!frame?.contentWindow || !iframeSrc.value) return
  const payload = buildInspireedInteractiveViewMessage(effectiveInteractiveView.value)
  let targetOrigin = '*'
  try {
    targetOrigin = new URL(frame.src).origin
  } catch {
    /* keep * */
  }
  try {
    frame.contentWindow.postMessage(payload, targetOrigin)
  } catch {
    try {
      frame.contentWindow.postMessage(payload, '*')
    } catch {
      /* ignore */
    }
  }
}

function onInteractiveIframeLoad() {
  nextTick(() => {
    postInteractiveViewToIframe()
    window.setTimeout(() => postInteractiveViewToIframe(), 50)
  })
}

watch([effectiveInteractiveView, iframeSrc], () => {
  nextTick(() => postInteractiveViewToIframe())
})

const displayContent = computed(() => {
  return props.editable ? localContent.value : (props.cell.content || {} as InteractiveCell['content'])
})

const displayConfig = computed(() => {
  return props.editable ? localConfig.value : (props.cell.config || {} as InteractiveCell['config'])
})

const iframeStyle = computed(() => {
  const configuredWidth = displayConfig.value?.width?.trim()
  const configuredHeight = displayConfig.value?.height?.trim() || '800px'

  return {
    width: '100%',
    maxWidth: configuredWidth && configuredWidth !== '100%' ? configuredWidth : '100%',
    height: configuredHeight,
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

function validateUrlsAndUpdate() {
  teacherUrlError.value = null
  studentUrlError.value = null
  const tu = localContent.value.teacher_url?.trim()
  const su = (localContent.value.student_url || localContent.value.url)?.trim()
  if (tu && !isValidUrl(tu)) {
    teacherUrlError.value = '请输入有效的网址（必须以 http:// 或 https:// 开头）'
    return
  }
  if (su && !isValidUrl(su)) {
    studentUrlError.value = '请输入有效的网址（必须以 http:// 或 https:// 开头）'
    return
  }
  updateCell()
}

function previewExternalUrl(rawUrl: string | undefined) {
  const u = rawUrl?.trim()
  if (!u || !isValidUrl(u)) return
  const resolved = resolveUrl(u) || u
  const withView = appendInteractiveViewToUrl(resolved, effectiveInteractiveView.value)
  if (withView) window.open(withView, '_blank', 'noopener,noreferrer')
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
  }
}

// 处理资源库资产选择（支持任意带 public_url 的类型；教师 / 学生分列）
function handleAssetSelect(asset: LibraryAssetSummary | null, forcedSide?: 'teacher' | 'student') {
  const side = forcedSide ?? libraryPickSide.value
  if (!asset) {
    clearLibrarySide(side)
    showLibraryPicker.value = false
    return
  }
  if (!asset.public_url?.trim()) {
    window.alert('该资源没有可用的访问链接，请选择其他资源或使用下方粘贴 HTML / 本地上传。')
    return
  }
  localContent.value.title = localContent.value.title || asset.title
  if (asset.thumbnail_url) {
    localContent.value.thumbnail = asset.thumbnail_url || localContent.value.thumbnail
  }
  if (side === 'teacher') {
    selectedTeacherAsset.value = asset
    localContent.value.teacher_asset_id = asset.id
    localContent.value.teacher_url = asset.public_url || undefined
  } else {
    selectedStudentAsset.value = asset
    localContent.value.student_asset_id = asset.id
    localContent.value.student_url = asset.public_url || undefined
    localContent.value.asset_id = asset.id
    localContent.value.url = asset.public_url || undefined
  }
  showLibraryPicker.value = false
  updateCell()
}

function clearLibrarySide(side: 'teacher' | 'student') {
  if (side === 'teacher') {
    selectedTeacherAsset.value = null
    localContent.value.teacher_asset_id = undefined
    localContent.value.teacher_url = undefined
  } else {
    selectedStudentAsset.value = null
    localContent.value.student_asset_id = undefined
    localContent.value.student_url = undefined
    localContent.value.asset_id = undefined
    localContent.value.url = undefined
  }
  updateCell()
}

async function loadTeacherAssetDetail(assetId: number) {
  try {
    const assetDetail = await libraryService.getAsset(assetId)
    selectedTeacherAsset.value = mapDetailToSummary(assetDetail)
    if (assetDetail.public_url) {
      localContent.value.teacher_url = assetDetail.public_url
    }
  } catch (error) {
    console.error('Failed to load teacher asset:', error)
  }
}

async function loadStudentAssetDetail(assetId: number) {
  try {
    const assetDetail = await libraryService.getAsset(assetId)
    selectedStudentAsset.value = mapDetailToSummary(assetDetail)
    if (assetDetail.public_url) {
      localContent.value.student_url = assetDetail.public_url
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
    console.error('Failed to load student asset:', error)
  }
}

// 将 refs 中的双栏 HTML 写入 content（并清除旧版单字段 html_code）
function persistDualHtmlToLocalContent() {
  const t = teacherHtmlCode.value.trim()
  const s = studentHtmlCode.value.trim()
  localContent.value.teacher_html_code = t || undefined
  localContent.value.student_html_code = s || undefined
  if (t || s) {
    localContent.value.html_code = undefined
  } else {
    localContent.value.html_code = undefined
    localContent.value.teacher_html_code = undefined
    localContent.value.student_html_code = undefined
  }
}

// 处理HTML代码变化（教师 / 学生）
function onTeacherHtmlInput() {
  htmlError.value = null
  htmlErrorField.value = null
  refreshTeacherBlob()
  updateCell()
}

function onStudentHtmlInput() {
  htmlError.value = null
  htmlErrorField.value = null
  refreshStudentBlob()
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

function generateFromHtml(side: 'teacher' | 'student') {
  const raw = side === 'teacher' ? teacherHtmlCode.value : studentHtmlCode.value
  if (!raw || !raw.trim()) {
    htmlError.value = '请输入HTML代码'
    htmlErrorField.value = side
    return
  }

  if (side === 'teacher') isGeneratingTeacherHtml.value = true
  else isGeneratingStudentHtml.value = true
  htmlError.value = null
  htmlErrorField.value = null

  try {
    const trimmedHtml = raw.trim()
    const finalHtml = wrapHtmlFragment(trimmedHtml, '交互式课件')

    if (side === 'teacher') {
      teacherHtmlCode.value = finalHtml
      refreshTeacherBlob()
    } else {
      studentHtmlCode.value = finalHtml
      refreshStudentBlob()
    }

    localContent.value.teacher_url = undefined
    localContent.value.student_url = undefined
    localContent.value.url = undefined
    localContent.value.asset_id = undefined
    localContent.value.teacher_asset_id = undefined
    localContent.value.student_asset_id = undefined
    selectedTeacherAsset.value = null
    selectedStudentAsset.value = null

    if (!localContent.value.title) {
      localContent.value.title = '交互式课件'
    }

    updateCell()
  } catch (error) {
    console.error('生成HTML课件失败:', error)
    htmlError.value = '生成课件失败，请检查HTML代码格式'
    htmlErrorField.value = side
  } finally {
    if (side === 'teacher') isGeneratingTeacherHtml.value = false
    else isGeneratingStudentHtml.value = false
  }
}

function clearTeacherHtml() {
  teacherHtmlCode.value = ''
  revokeTeacherBlob()
  htmlError.value = null
  htmlErrorField.value = null
  updateCell()
}

function clearStudentHtml() {
  studentHtmlCode.value = ''
  revokeStudentBlob()
  htmlError.value = null
  htmlErrorField.value = null
  updateCell()
}

function openSaveToLibraryModal(side: 'teacher' | 'student') {
  saveToLibrarySide.value = side
  showSaveToLibraryModal.value = true
}

// 将HTML代码转换为File对象
function htmlCodeToFile(html: string, filename: string = 'interactive-courseware.html'): File {
  const blob = new Blob([html], { type: 'text/html' })
  return new File([blob], filename, { type: 'text/html' })
}

// 存储HTML代码到资源库
async function saveToLibrary() {
  const raw =
    saveToLibrarySide.value === 'teacher' ? teacherHtmlCode.value : studentHtmlCode.value
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
      handleAssetSelect(
        {
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
        },
        saveToLibrarySide.value
      )
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

function syncLegacyInteractiveAliases() {
  const c = localContent.value
  c.asset_id = c.student_asset_id ?? c.teacher_asset_id ?? undefined
  const su = c.student_url?.trim()
  const tu = c.teacher_url?.trim()
  c.url = su || tu || undefined
}

// 更新 Cell
function updateCell() {
  persistDualHtmlToLocalContent()
  syncLegacyInteractiveAliases()
  const updatedCell: InteractiveCell = {
    ...props.cell,
    content: { ...localContent.value },
    config: localConfig.value ? { ...localConfig.value } : undefined
  }
  emit('update', updatedCell)
}

// 在新窗口预览
function previewUrl() {
  const url = iframeSrc.value
  if (url) window.open(url, '_blank', 'noopener,noreferrer')
}

// 监听 props.cell 的变化，同步到本地状态
watch(
  () => props.cell,
  (newCell) => {
    if (!newCell) return
    localContent.value = { ...(newCell.content || {}) }
    if (localContent.value.url && !localContent.value.student_url) {
      localContent.value.student_url = localContent.value.url
    }
    if (localContent.value.asset_id && !localContent.value.student_asset_id) {
      localContent.value.student_asset_id = localContent.value.asset_id
    }
    localConfig.value = {
      allowFullscreen: true,
      height: '800px',
      ...(newCell.config || {}),
    }

    syncHtmlRefsFromCellContent(newCell.content)

    const tid = newCell.content?.teacher_asset_id
    if (tid) {
      if (selectedTeacherAsset.value?.id !== tid) loadTeacherAssetDetail(tid)
    } else {
      selectedTeacherAsset.value = null
    }

    const sid = newCell.content?.student_asset_id ?? newCell.content?.asset_id
    if (sid) {
      if (selectedStudentAsset.value?.id !== sid) loadStudentAssetDetail(sid)
    } else {
      selectedStudentAsset.value = null
    }

    sourceMode.value = inferInteractiveSourceMode(newCell.content)
  },
  { deep: true, immediate: true }
)

// 组件挂载时补齐 legacy 字段并加载资产摘要（deep watch 会再跑一次，此处兜底）
onMounted(() => {
  const c = props.cell.content
  if (!c) return
  if (localContent.value.url && !localContent.value.student_url) {
    localContent.value.student_url = localContent.value.url
  }
  if (localContent.value.asset_id && !localContent.value.student_asset_id) {
    localContent.value.student_asset_id = localContent.value.asset_id
  }
  syncHtmlRefsFromCellContent(c)
  if (c.teacher_asset_id) loadTeacherAssetDetail(c.teacher_asset_id)
  const sid = c.student_asset_id ?? c.asset_id
  if (sid) loadStudentAssetDetail(sid)
  sourceMode.value = inferInteractiveSourceMode(c)
})

// 组件卸载时先清空 iframe src 再 revoke blob，避免 "Not allowed to load local resource: blob:..."
onBeforeUnmount(() => {
  if (interactiveIframeRef.value?.src && interactiveIframeRef.value.src.startsWith('blob:')) {
    interactiveIframeRef.value.src = 'about:blank'
  }
  revokeTeacherBlob()
  revokeStudentBlob()
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
</style>
