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
        :preload="editable ? 'none' : 'metadata'"
        @loadedmetadata="handleVideoLoaded"
        @timeupdate="handleTimeUpdate"
        @ended="handleVideoEnded"
        @error="handleVideoError"
      >
        您的浏览器不支持视频播放
      </video>
      
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
const displayVideoUrl = computed(() => {
  return props.editable ? (localContent.value.videoUrl || props.cell.content?.videoUrl) : (props.cell.content?.videoUrl)
})

const displayContent = computed(() => {
  return props.editable ? localContent.value : (props.cell.content || {} as VideoCell['content'])
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
        localContent.value = { ...newCell.content }
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
        localContent.value = { ...newCell.content }
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

    // 构建完整的视频 URL
    let videoUrl = response.file_url
    if (videoUrl.startsWith('/uploads/')) {
      // 构建完整 URL
      const baseURL = getServerBaseUrl()
      videoUrl = `${baseURL}${videoUrl}`
    }

    // 清理临时 blob URL
    if (blobUrl.value === tempBlobUrl) {
      URL.revokeObjectURL(tempBlobUrl)
      blobUrl.value = null
    }

    // 更新为服务器 URL
    isUpdatingFromProps = true
    localContent.value.videoUrl = videoUrl
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

// 处理资源库视频选择
function handleVideoAssetSelect(asset: LibraryAssetSummary | null) {
  if (asset && asset.asset_type === 'video') {
    selectedVideoAsset.value = asset
    isUpdatingFromProps = true
    localContent.value.videoUrl = asset.public_url || ''
    localContent.value.title = localContent.value.title || asset.title
    localContent.value.description = localContent.value.description || undefined
    localContent.value.thumbnail = asset.thumbnail_url || undefined
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
  const updatedCell: VideoCell = {
    ...props.cell,
    content: { ...localContent.value },
    config: { ...localConfig.value }
  }
  emit('update', updatedCell)
}

function handleVideoLoaded() {
  if (videoPlayer.value) {
    localContent.value.duration = videoPlayer.value.duration
    updateCell()
  }
}

function handleTimeUpdate() {
  // 可以在这里添加时间更新逻辑
}

function handleVideoEnded() {
  // 视频播放结束处理
}

function handleVideoError(event: Event) {
  const video = event.target as HTMLVideoElement
  console.error('视频加载错误:', {
    error: video.error,
    networkState: video.networkState,
    readyState: video.readyState,
    src: video.src
  })
  
  if (video.error) {
    let errorMessage = '视频加载失败'
    switch (video.error.code) {
      case video.error.MEDIA_ERR_ABORTED:
        errorMessage = '视频加载被中止'
        break
      case video.error.MEDIA_ERR_NETWORK:
        errorMessage = '网络错误导致视频加载失败'
        break
      case video.error.MEDIA_ERR_DECODE:
        errorMessage = '视频解码失败'
        break
      case video.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
        errorMessage = '视频格式不支持或源不可用'
        break
    }
    console.error(errorMessage)
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

// 组件卸载前清理 blob URL
onBeforeUnmount(() => {
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
  @apply w-full;
}

.video-player video {
  @apply w-full max-w-full rounded-lg shadow-lg;
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
