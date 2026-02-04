<template>
  <div class="video-cell cell-container" :class="{ 'fullscreen': isFullscreen }" ref="containerRef">
    <!-- 全屏按钮 -->
    <div v-if="!editable" class="cell-toolbar">
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
    
    <div v-if="editable" class="video-editor">
      <!-- 视频选择方式 -->
      <div v-if="!cell.content.videoUrl" class="video-source-options">
        <div class="form-group">
          <label>选择方式:</label>
          <div class="source-options">
            <button
              :class="[
                'source-option-btn',
                videoSourceMode === 'library' ? 'active' : ''
              ]"
              @click="videoSourceMode = 'library'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              从资源库选择
            </button>
            <button
              :class="[
                'source-option-btn',
                videoSourceMode === 'upload' ? 'active' : ''
              ]"
              @click="videoSourceMode = 'upload'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              上传文件
            </button>
            <button
              :class="[
                'source-option-btn',
                videoSourceMode === 'url' ? 'active' : ''
              ]"
              @click="videoSourceMode = 'url'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              输入URL
            </button>
          </div>
        </div>

        <!-- 从资源库选择 -->
        <div v-if="videoSourceMode === 'library'" class="form-group">
          <label>选择视频资源:</label>
          <div class="library-picker-wrapper">
            <button
              v-if="!selectedVideoAsset"
              @click="showVideoLibraryPicker = true"
              class="library-picker-btn"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              点击选择资源库中的视频
            </button>
            <div v-else class="selected-asset-card">
              <div class="flex items-center gap-3">
                <div class="flex-shrink-0 w-12 h-12 bg-red-100 rounded flex items-center justify-center">
                  <span class="text-2xl">🎥</span>
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-medium text-gray-900 truncate">{{ selectedVideoAsset.title }}</h4>
                  <p class="text-sm text-gray-500">视频资源</p>
                </div>
                <button
                  @click="clearVideoAsset"
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

        <!-- 上传文件 -->
        <div v-if="videoSourceMode === 'upload'" class="video-upload">
          <div v-if="!isUploading" class="upload-area" @click="triggerFileUpload">
            <svg class="upload-icon" viewBox="0 0 24 24">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
            </svg>
            <p>点击上传视频文件</p>
            <p class="upload-hint">支持 MP4, WebM, OGG 格式</p>
          </div>
          <div v-else class="upload-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
            </div>
            <p class="progress-text">上传中... {{ uploadProgress }}%</p>
            <p v-if="uploadError" class="error-text">{{ uploadError }}</p>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="video/*"
            @change="handleFileUpload"
            style="display: none"
            :disabled="isUploading"
          />
        </div>

        <!-- 输入URL -->
        <div v-if="videoSourceMode === 'url'" class="video-url-input">
          <label>视频URL:</label>
          <input
            v-model="localContent.videoUrl"
            type="url"
            placeholder="https://example.com/video.mp4"
            @blur="updateCell"
          />
        </div>
      </div>

      <!-- 视频URL输入（已有视频时） -->
      <div v-else class="video-url-input">
        <label>视频URL:</label>
        <input
          v-model="localContent.videoUrl"
          type="url"
          placeholder="https://example.com/video.mp4"
          @blur="updateCell"
        />
      </div>

      <!-- 视频信息编辑 -->
      <div v-if="cell.content.videoUrl" class="video-info">
        <div class="form-group">
          <label>视频标题:</label>
          <input
            v-model="localContent.title"
            type="text"
            placeholder="输入视频标题"
            @blur="updateCell"
          />
        </div>
        
        <div class="form-group">
          <label>视频描述:</label>
          <textarea
            v-model="localContent.description"
            placeholder="输入视频描述"
            @blur="updateCell"
          />
        </div>

        <!-- 视频配置 -->
        <div class="video-config">
          <h4>播放配置</h4>
          <div class="config-options">
            <label>
              <input
                v-model="localConfig.autoplay"
                type="checkbox"
                @change="updateCell"
              />
              自动播放
            </label>
            <label>
              <input
                v-model="localConfig.controls"
                type="checkbox"
                @change="updateCell"
              />
              显示控制条
            </label>
            <label>
              <input
                v-model="localConfig.loop"
                type="checkbox"
                @change="updateCell"
              />
              循环播放
            </label>
            <label>
              <input
                v-model="localConfig.muted"
                type="checkbox"
                @change="updateCell"
              />
              静音播放
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 视频播放器 -->
    <!-- 在编辑模式下使用 localContent，确保上传后立即显示；非编辑模式下使用 props -->
    <div v-if="displayVideoUrl" class="video-player">
      <video
        ref="videoPlayer"
        :src="displayVideoUrl"
        :poster="displayContent.thumbnail"
        :controls="displayConfig?.controls !== false"
        :autoplay="displayConfig?.autoplay"
        :loop="displayConfig?.loop"
        :muted="displayConfig?.muted"
        :preload="'metadata'"
        crossorigin="anonymous"
        @loadedmetadata="handleVideoLoaded"
        @timeupdate="handleTimeUpdate"
        @ended="handleVideoEnded"
        @error="handleVideoError"
      >
        您的浏览器不支持视频播放
      </video>
      
      <!-- 视频加载错误提示 -->
      <div v-if="videoLoadError" class="video-error-overlay">
        <div class="video-error-content">
          <svg class="video-error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="video-error-message">{{ videoLoadError }}</p>
          <div class="video-error-actions">
            <button @click="retryVideoLoad" class="video-retry-btn" :disabled="isCheckingVideo">
              {{ isCheckingVideo ? '检查中...' : '重试' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 视频信息显示 -->
      <div v-if="displayContent.title || displayContent.description" class="video-info-display">
        <h3 v-if="displayContent.title">{{ displayContent.title }}</h3>
        <p v-if="displayContent.description">{{ displayContent.description }}</p>
        <div v-if="displayContent.duration" class="video-duration">
          时长: {{ formatDuration(displayContent.duration) }}
        </div>
      </div>

      <!-- 章节导航 -->
      <div v-if="displayContent.chapters && displayContent.chapters.length > 0" class="video-chapters">
        <h4>章节导航</h4>
        <div class="chapters-list">
          <button
            v-for="(chapter, index) in displayContent.chapters"
            :key="index"
            @click="seekTo(chapter.startTime)"
            class="chapter-item"
          >
            <span class="chapter-time">{{ formatTime(chapter.startTime) }}</span>
            <span class="chapter-title">{{ chapter.title }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 资源库选择器模态框 -->
    <Teleport to="body">
      <div
        v-if="showVideoLibraryPicker"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="showVideoLibraryPicker = false"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showVideoLibraryPicker = false"></div>
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between">
              <h3 class="text-xl font-semibold text-gray-900">选择视频资源</h3>
              <button @click="showVideoLibraryPicker = false" class="text-gray-400 hover:text-gray-500">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-6">
              <AssetPicker
                ref="assetPicker"
                @select="handleVideoAssetSelect"
                filter-type="video"
              />
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import type { VideoCell } from '../../types/cell'
import type { LibraryAssetSummary } from '../../types/library'
import api from '../../services/api'
import { getServerBaseUrl } from '@/utils/url'
// 不再需要 normalizeResourceUrl，后端现在返回完整URL
import { useFullscreen } from '@/composables/useFullscreen'
import AssetPicker from '@/components/Library/AssetPicker.vue'

interface Props {
  cell: VideoCell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<{
  update: [cell: VideoCell]
}>()

const containerRef = ref<HTMLElement | null>(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(containerRef)

const fileInput = ref<HTMLInputElement>()
const videoPlayer = ref<HTMLVideoElement>()

const localContent = ref({ ...props.cell.content })
const localConfig = ref({ ...props.cell.config })

// 视频来源选择模式
const videoSourceMode = ref<'library' | 'upload' | 'url'>('upload')
const showVideoLibraryPicker = ref(false)
const selectedVideoAsset = ref<LibraryAssetSummary | null>(null)
const assetPicker = ref<InstanceType<typeof AssetPicker>>()

// 在编辑模式下使用 localContent，确保上传后立即显示；非编辑模式下使用 props
// 注意：后端现在返回完整URL，前端可以直接使用
const displayVideoUrl = computed(() => {
  const url = props.editable ? (localContent.value.videoUrl || props.cell.content?.videoUrl) : (props.cell.content?.videoUrl)
  // 如果是blob URL或data URL，直接返回
  if (url && (url.startsWith('blob:') || url.startsWith('data:'))) {
    return url
  }
  // 如果URL是文件名（不包含/），需要转换为完整URL（向后兼容旧数据）
  if (url && !url.includes('/') && !url.startsWith('http://') && !url.startsWith('https://')) {
    const baseURL = getServerBaseUrl()
    return `${baseURL}/uploads/resources/${url}`
  }
  // 其他情况（完整URL或相对路径），直接返回
  // 后端API应该已经返回完整URL，这里保留向后兼容
  return url
})

const displayContent = computed((): VideoCell['content'] => {
  const content = props.editable ? localContent.value : (props.cell.content || {} as VideoCell['content'])
  // 处理thumbnail URL（后端应该返回完整URL，这里保留向后兼容）
  if (content.thumbnail) {
    // 如果thumbnail是blob URL，过滤掉它（blob URL不应该存储到数据库，也不应该用于poster）
    // blob URL是临时性的，不应该持久化，应该使用data URL或服务器URL
    if (content.thumbnail.startsWith('blob:')) {
      // 返回没有thumbnail的内容（设为undefined），让视频显示第一帧
      return {
        ...content,
        thumbnail: undefined
      }
    }
    // 如果是data URL，可以直接使用（用于临时生成的缩略图）
    if (content.thumbnail.startsWith('data:')) {
      return content
    }
    // 如果URL是文件名（不包含/），需要转换为完整URL（向后兼容旧数据）
    if (!content.thumbnail.includes('/') && !content.thumbnail.startsWith('http://') && !content.thumbnail.startsWith('https://')) {
      const baseURL = getServerBaseUrl()
      return {
        ...content,
        thumbnail: `${baseURL}/uploads/resources/${content.thumbnail}`
      }
    }
    // 如果已经是完整URL，直接返回
    return content
  }
  return content
})

const displayConfig = computed(() => {
  return props.editable ? localConfig.value : (props.cell.config || {} as VideoCell['config'])
})

// 保存 blob URL 以便清理
const blobUrl = ref<string | null>(null)

// 上传状态
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadError = ref<string | null>(null)

// 视频加载错误状态
const videoLoadError = ref<string | null>(null)
const isCheckingVideo = ref(false)

// 标志位：是否正在从 props 同步数据（避免循环触发）
let isUpdatingFromProps = false

// 监听 props.cell 的变化，同步到本地状态
// 但只有当 props 的 videoUrl 确实变化时才更新，避免覆盖用户正在编辑的内容
watch(() => props.cell, (newCell) => {
  if (newCell) {
    // 只有当 props 的 videoUrl 与当前 localContent 不同时才同步
    // 这确保了父组件更新后，本地状态能同步，但不会覆盖正在编辑的内容
    if (newCell.content?.videoUrl && newCell.content.videoUrl !== localContent.value.videoUrl) {
      // 如果 props 中的 videoUrl 不是 blob URL（说明是服务器 URL），则同步
      // 如果 props 中的 videoUrl 是 blob URL，可能是同一文件的不同 blob URL 实例，需要检查
      if (!newCell.content.videoUrl.startsWith('blob:')) {
        // 服务器 URL，直接同步
        isUpdatingFromProps = true
        // 过滤掉blob URL的thumbnail，因为它们不应该从数据库加载
        const contentToSync = { ...newCell.content }
        if (contentToSync.thumbnail && contentToSync.thumbnail.startsWith('blob:')) {
          delete contentToSync.thumbnail
        }
        localContent.value = contentToSync
        localConfig.value = { ...(newCell.config || {}) }
        isUpdatingFromProps = false
      } else if (newCell.content.videoUrl !== blobUrl.value) {
        // 不同的 blob URL，可能是从其他地方来的，需要同步
        // 清理旧的 blob URL
        if (blobUrl.value && blobUrl.value !== newCell.content.videoUrl) {
          URL.revokeObjectURL(blobUrl.value)
        }
        blobUrl.value = newCell.content.videoUrl
        isUpdatingFromProps = true
        // 过滤掉blob URL的thumbnail
        const contentToSync = { ...newCell.content }
        if (contentToSync.thumbnail && contentToSync.thumbnail.startsWith('blob:')) {
          delete contentToSync.thumbnail
        }
        localContent.value = contentToSync
        localConfig.value = { ...(newCell.config || {}) }
        isUpdatingFromProps = false
      }
    }
  }
}, { deep: true })

// 监听本地内容变化，但避免在同步 props 时触发
watch([localContent, localConfig], () => {
  if (!isUpdatingFromProps) {
    updateCell()
  }
}, { deep: true })

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleFileUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // 验证文件类型
  const allowedTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime', 'video/x-msvideo']
  const fileExt = file.name.split('.').pop()?.toLowerCase()
  const allowedExtensions = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv']
  
  if (!allowedExtensions.includes(fileExt || '')) {
    uploadError.value = `不支持的文件格式：.${fileExt}。支持格式：${allowedExtensions.join(', ')}`
    return
  }

  // 验证文件大小（限制为 500MB）
  const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB
  if (file.size > MAX_FILE_SIZE) {
    uploadError.value = `文件太大（${(file.size / 1024 / 1024).toFixed(2)}MB）。最大支持 500MB`
    return
  }

  // 清理旧的 blob URL（如果存在）
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = null
  }

  // 初始化上传状态
  isUploading.value = true
  uploadProgress.value = 0
  uploadError.value = null

  try {
    // 创建临时 blob URL 用于预览（在上传期间）
    const tempBlobUrl = URL.createObjectURL(file)
    blobUrl.value = tempBlobUrl
    
    // 先设置临时 URL 用于即时预览
    isUpdatingFromProps = true
    localContent.value.videoUrl = tempBlobUrl
    localContent.value.title = file.name.replace(/\.[^/.]+$/, "")
    isUpdatingFromProps = false

    // 准备上传到服务器
    const formData = new FormData()
    formData.append('file', file)

    // 上传文件（带进度监听）
    const response = await api.post<{
      file_url: string
      file_size: number
      filename: string
    }>('/upload/', formData, {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      },
      timeout: 300000, // 5分钟超时，适应大文件上传
    })

    // 后端返回完整URL，提取文件名保存到数据库
    const videoUrl = response.file_url
    const filename = extractFilename(videoUrl)

    // 清理临时 blob URL
    if (blobUrl.value === tempBlobUrl) {
      URL.revokeObjectURL(tempBlobUrl)
      blobUrl.value = null
    }

    // 保存文件名到localContent（数据库存储文件名）
    isUpdatingFromProps = true
    localContent.value.videoUrl = filename
    isUpdatingFromProps = false

    uploadProgress.value = 100
    
    // 手动触发更新
    updateCell()

    // 清空文件输入，允许重复选择同一个文件
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (error: any) {
    console.error('视频上传失败:', error)
    
    // 清理临时 blob URL
    if (blobUrl.value) {
      URL.revokeObjectURL(blobUrl.value)
      blobUrl.value = null
    }
    
    // 恢复为空状态
    isUpdatingFromProps = true
    localContent.value.videoUrl = ''
    isUpdatingFromProps = false

    // 显示错误信息
    if (error.response?.data?.detail) {
      uploadError.value = typeof error.response.data.detail === 'string' 
        ? error.response.data.detail 
        : error.response.data.detail[0]?.msg || '上传失败'
    } else if (error.message) {
      uploadError.value = error.message
    } else {
      uploadError.value = '视频上传失败，请稍后重试'
    }
  } finally {
    isUploading.value = false
    // 延迟清空错误信息
    if (uploadError.value) {
      setTimeout(() => {
        uploadError.value = null
      }, 5000)
    }
  }
}

// 从URL中提取文件名（用于保存到数据库）
function extractFilename(url: string): string {
  if (!url || url.startsWith('blob:') || url.startsWith('data:')) {
    return url
  }
  
  // 如果已经是纯文件名（不包含路径分隔符），直接返回
  if (!url.includes('/') && !url.startsWith('http://') && !url.startsWith('https://')) {
    return url
  }
  
  try {
    const urlObj = new URL(url)
    // 从路径中提取文件名（最后一个路径段）
    const filename = urlObj.pathname.split('/').pop() || ''
    return filename || url
  } catch {
    // URL解析失败，尝试直接提取文件名
    // 支持格式：/uploads/resources/xxx.png 或 http://host:port/uploads/resources/xxx.png
    if (url.includes('/')) {
      const parts = url.split('/')
      const filename = parts[parts.length - 1]
      // 移除查询参数和hash
      return filename.split('?')[0].split('#')[0] || url
    }
  }
  return url
}

// 处理资源库视频选择
function handleVideoAssetSelect(asset: LibraryAssetSummary | null) {
  if (asset && asset.asset_type === 'video') {
    selectedVideoAsset.value = asset
    isUpdatingFromProps = true
    // 从完整URL中提取文件名保存到数据库
    localContent.value.videoUrl = extractFilename(asset.public_url || '')
    localContent.value.title = localContent.value.title || asset.title
    localContent.value.description = localContent.value.description || undefined
    // thumbnail也需要提取文件名
    localContent.value.thumbnail = asset.thumbnail_url ? extractFilename(asset.thumbnail_url) : undefined
    if (asset.duration_seconds) {
      localContent.value.duration = asset.duration_seconds
    }
    isUpdatingFromProps = false
    showVideoLibraryPicker.value = false
    updateCell()
  } else {
    selectedVideoAsset.value = null
  }
}

// 清除选择的视频资产
function clearVideoAsset() {
  selectedVideoAsset.value = null
  isUpdatingFromProps = true
  localContent.value.videoUrl = ''
  isUpdatingFromProps = false
  updateCell()
}

function updateCell() {
  // 在保存到数据库前，确保所有URL都是文件名
  const contentToSave = { ...localContent.value }
  
  // 提取videoUrl的文件名
  if (contentToSave.videoUrl) {
    contentToSave.videoUrl = extractFilename(contentToSave.videoUrl)
  }
  
  // 提取thumbnail的文件名（过滤掉blob URL和data URL，因为它们不应该保存到数据库）
  if (contentToSave.thumbnail) {
    // blob URL和data URL不应该保存到数据库
    if (contentToSave.thumbnail.startsWith('blob:') || contentToSave.thumbnail.startsWith('data:')) {
      delete contentToSave.thumbnail
    } else {
      contentToSave.thumbnail = extractFilename(contentToSave.thumbnail)
    }
  }
  
  const updatedCell: VideoCell = {
    ...props.cell,
    content: contentToSave,
    config: { ...localConfig.value }
  }
  emit('update', updatedCell)
}

function handleVideoLoaded() {
  if (videoPlayer.value) {
    const video = videoPlayer.value
    
    // 更新视频时长（仅在编辑模式下更新localContent）
    if (props.editable) {
      localContent.value.duration = video.duration
    }
    
    // 如果没有thumbnail，从视频第一帧生成缩略图
    const currentThumbnail = props.editable 
      ? localContent.value.thumbnail 
      : (props.cell.content?.thumbnail)
    
    // 忽略blob URL，因为它们不应该用于poster（临时性的）
    const validThumbnail = currentThumbnail && !currentThumbnail.startsWith('blob:')
    
    if (!validThumbnail && video.videoWidth > 0 && video.videoHeight > 0) {
      generateVideoThumbnail()
    }
    
    if (props.editable) {
      updateCell()
    }
  }
}

// 从视频第一帧生成缩略图
function generateVideoThumbnail() {
  if (!videoPlayer.value) return
  
  const video = videoPlayer.value
  
  // 确保视频已加载元数据
  if (video.readyState < 1) {
    // 如果视频还没加载，等待加载完成
    const onLoadedData = () => {
      captureFirstFrame()
      video.removeEventListener('loadeddata', onLoadedData)
    }
    video.addEventListener('loadeddata', onLoadedData, { once: true })
    return
  }
  
  captureFirstFrame()
  
  function captureFirstFrame() {
    // 创建一个canvas来截取视频帧
    const canvas = document.createElement('canvas')
    const videoWidth = video.videoWidth || 640
    const videoHeight = video.videoHeight || 360
    
    if (videoWidth === 0 || videoHeight === 0) {
      // 视频尺寸还未确定，稍后再试
      setTimeout(() => captureFirstFrame(), 100)
      return
    }
    
    canvas.width = videoWidth
    canvas.height = videoHeight
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // 将视频的第一帧绘制到canvas上
    try {
      // 保存当前播放时间
      const originalTime = video.currentTime
      
      // 设置当前时间为第一帧（0秒）
      video.currentTime = 0
      
      // 等待视频seek到第一帧
      const onSeeked = () => {
        try {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
          
          // 恢复原来的播放时间（如果需要）
          // video.currentTime = originalTime
          
          // 将canvas转换为data URL（避免blob URL的问题）
          // 使用data URL可以直接设置到poster属性，不需要存储到响应式数据中
          try {
            const dataUrl = canvas.toDataURL('image/png', 0.8)
            
            // 直接更新video元素的poster属性（这样无论编辑模式还是非编辑模式都能显示）
            if (videoPlayer.value) {
              videoPlayer.value.poster = dataUrl
            }
          } catch (error: any) {
            // Canvas被污染（CORS问题），无法生成缩略图
            // 这种情况下，不设置poster，让浏览器自然显示第一帧
            if (error.name === 'SecurityError' || error.message?.includes('Tainted')) {
              console.debug('视频跨域，无法生成缩略图，将使用浏览器默认的第一帧显示')
              // 不设置poster，让video元素自己显示第一帧（preload="metadata"时浏览器会自动显示第一帧）
            } else {
              console.warn('生成视频缩略图失败:', error)
            }
          }
        } catch (error) {
          console.warn('截取视频第一帧失败:', error)
        }
        video.removeEventListener('seeked', onSeeked)
      }
      
      video.addEventListener('seeked', onSeeked, { once: true })
    } catch (error) {
      console.warn('生成视频缩略图失败:', error)
    }
  }
}

function handleTimeUpdate() {
  // 可以在这里添加时间更新逻辑
}

function handleVideoEnded() {
  // 视频播放结束处理
}

async function handleVideoError(event: Event) {
  const video = event.target as HTMLVideoElement
  const videoUrl = video.src
  
  console.error('视频加载错误:', {
    error: video.error,
    networkState: video.networkState,
    readyState: video.readyState,
    src: videoUrl
  })
  
  // 清除之前的错误
  videoLoadError.value = null
  
  if (video.error) {
    let errorMessage = '视频加载失败'
    let errorCode = video.error.code
    
    switch (errorCode) {
      case video.error.MEDIA_ERR_ABORTED:
        errorMessage = '视频加载被中止'
        break
      case video.error.MEDIA_ERR_NETWORK:
        errorMessage = '网络错误导致视频加载失败'
        // 检查文件是否存在
        await checkVideoFileExists(videoUrl)
        break
      case video.error.MEDIA_ERR_DECODE:
        errorMessage = '视频解码失败，可能是文件损坏或格式不支持'
        break
      case video.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
        errorMessage = '视频格式不支持或源不可用'
        // 检查文件是否存在
        await checkVideoFileExists(videoUrl)
        break
    }
    
    // 如果 networkState 是 3 (NETWORK_NO_SOURCE)，可能是文件不存在
    if (video.networkState === 3) {
      errorMessage = '视频文件不存在或无法访问'
      await checkVideoFileExists(videoUrl)
    }
    
    videoLoadError.value = errorMessage
    console.error(errorMessage, { errorCode, networkState: video.networkState, url: videoUrl })
  }
}

// 检查视频文件是否存在
async function checkVideoFileExists(videoUrl: string) {
  if (!videoUrl || videoUrl.startsWith('blob:') || videoUrl.startsWith('data:')) {
    return
  }
  
  isCheckingVideo.value = true
  try {
    const response = await fetch(videoUrl, { method: 'HEAD' })
    if (!response.ok) {
      if (response.status === 404) {
        videoLoadError.value = '视频文件不存在（404错误），请检查文件是否已上传'
      } else if (response.status === 403) {
        videoLoadError.value = '无权访问视频文件（403错误）'
      } else {
        videoLoadError.value = `视频文件访问失败（HTTP ${response.status}）`
      }
    } else {
      // 文件存在，可能是格式或解码问题
      if (!videoLoadError.value) {
        videoLoadError.value = '视频文件存在但无法播放，可能是格式不支持或文件损坏'
      }
    }
  } catch (error: any) {
    console.error('检查视频文件失败:', error)
    if (error.message?.includes('CORS')) {
      videoLoadError.value = '视频文件访问被CORS策略阻止，请检查服务器配置'
    } else if (error.message?.includes('Failed to fetch')) {
      videoLoadError.value = '无法连接到服务器，请检查网络连接'
    } else {
      videoLoadError.value = `检查视频文件时出错: ${error.message || '未知错误'}`
    }
  } finally {
    isCheckingVideo.value = false
  }
}

// 重试加载视频
function retryVideoLoad() {
  videoLoadError.value = null
  if (videoPlayer.value) {
    videoPlayer.value.load()
  }
}

function seekTo(time: number) {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = time
  }
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function formatTime(seconds: number): string {
  return formatDuration(seconds)
}

// 组件卸载前先清空 video src 再 revoke blob，避免 "Not allowed to load local resource: blob:..."
onBeforeUnmount(() => {
  if (videoPlayer.value?.src && videoPlayer.value.src.startsWith('blob:')) {
    videoPlayer.value.removeAttribute('src')
    videoPlayer.value.load()
  }
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = null
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
.video-cell.fullscreen {
  @apply fixed inset-0 z-50 bg-black overflow-auto;
}

.video-cell.fullscreen .video-player {
  @apply flex flex-col items-center justify-center min-h-screen p-8;
}

.video-cell.fullscreen .video-player video {
  @apply max-w-full max-h-[80vh];
}

.video-cell {
  @apply w-full;
}

.video-upload {
  @apply border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors;
}

.upload-icon {
  @apply w-12 h-12 mx-auto mb-4 text-gray-400;
}

.video-player {
  @apply w-full relative;
}

.video-player video {
  @apply w-full max-w-full rounded-lg shadow-lg;
}

.video-error-overlay {
  @apply absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-lg;
  z-index: 10;
}

.video-error-content {
  @apply bg-white rounded-lg p-6 max-w-md mx-4 text-center;
}

.video-error-icon {
  @apply w-12 h-12 text-red-500 mx-auto mb-4;
}

.video-error-message {
  @apply text-gray-800 mb-4 text-sm;
}

.video-error-actions {
  @apply flex justify-center gap-2;
}

.video-retry-btn {
  @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors;
}

.video-info-display {
  @apply mt-4 p-4 bg-gray-50 rounded-lg;
}

.video-chapters {
  @apply mt-4;
}

.chapters-list {
  @apply space-y-2;
}

.chapter-item {
  @apply w-full text-left p-2 rounded hover:bg-gray-100 transition-colors;
}

.chapter-time {
  @apply text-sm text-gray-500 mr-2;
}

.chapter-title {
  @apply font-medium;
}

.video-config {
  @apply mt-4 p-4 bg-gray-50 rounded-lg;
}

/* 视频来源选择样式 */
.video-source-options {
  @apply mb-4;
}

.source-options {
  @apply flex gap-2;
}

.source-option-btn {
  @apply flex items-center gap-2 px-4 py-2 border-2 border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all;
}

.source-option-btn.active {
  @apply border-blue-500 bg-blue-50 text-blue-700;
}

.library-picker-wrapper {
  @apply w-full;
}

.library-picker-btn {
  @apply w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all flex items-center justify-center gap-2 text-gray-600;
}

.selected-asset-card {
  @apply w-full p-4 border-2 border-purple-200 rounded-lg bg-purple-50;
}

.config-options {
  @apply grid grid-cols-2 gap-2 mt-2;
}

.config-options label {
  @apply flex items-center space-x-2;
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

.video-url-input {
  @apply mb-4;
}

.video-url-input label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.video-url-input input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900;
}

.video-url-input input::placeholder {
  @apply text-gray-400;
}

.video-url-input input:focus {
  @apply border-blue-500 bg-white;
}

.upload-progress {
  @apply p-6 text-center;
}

.progress-bar {
  @apply w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-4;
}

.progress-fill {
  @apply h-full bg-blue-500 transition-all duration-300 ease-out;
}

.progress-text {
  @apply text-sm text-gray-600 mb-2;
}

.error-text {
  @apply text-sm text-red-600 mt-2;
}
</style>
