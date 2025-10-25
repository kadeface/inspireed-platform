<template>
  <div class="video-cell">
    <div v-if="editable" class="video-editor">
      <!-- 视频上传/选择区域 -->
      <div v-if="!cell.content.videoUrl" class="video-upload">
        <div class="upload-area" @click="triggerFileUpload">
          <svg class="upload-icon" viewBox="0 0 24 24">
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
          </svg>
          <p>点击上传视频文件</p>
          <p class="upload-hint">支持 MP4, WebM, OGG 格式</p>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="video/*"
          @change="handleFileUpload"
          style="display: none"
        />
      </div>

      <!-- 视频URL输入 -->
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
    <div v-if="cell.content.videoUrl" class="video-player">
      <video
        ref="videoPlayer"
        :src="cell.content.videoUrl"
        :poster="cell.content.thumbnail"
        :controls="cell.config?.controls !== false"
        :autoplay="cell.config?.autoplay"
        :loop="cell.config?.loop"
        :muted="cell.config?.muted"
        :preload="editable ? 'none' : 'metadata'"
        @loadedmetadata="handleVideoLoaded"
        @timeupdate="handleTimeUpdate"
        @ended="handleVideoEnded"
      >
        您的浏览器不支持视频播放
      </video>
      
      <!-- 视频信息显示 -->
      <div v-if="cell.content.title || cell.content.description" class="video-info-display">
        <h3 v-if="cell.content.title">{{ cell.content.title }}</h3>
        <p v-if="cell.content.description">{{ cell.content.description }}</p>
        <div v-if="cell.content.duration" class="video-duration">
          时长: {{ formatDuration(cell.content.duration) }}
        </div>
      </div>

      <!-- 章节导航 -->
      <div v-if="cell.content.chapters && cell.content.chapters.length > 0" class="video-chapters">
        <h4>章节导航</h4>
        <div class="chapters-list">
          <button
            v-for="(chapter, index) in cell.content.chapters"
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { VideoCell } from '../../types/cell'

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

const fileInput = ref<HTMLInputElement>()
const videoPlayer = ref<HTMLVideoElement>()

const localContent = ref({ ...props.cell.content })
const localConfig = ref({ ...props.cell.config })

// 监听内容变化
watch([localContent, localConfig], () => {
  updateCell()
}, { deep: true })

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleFileUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // 这里应该上传到服务器，获取URL
  // 暂时使用本地URL作为示例
  const videoUrl = URL.createObjectURL(file)
  localContent.value.videoUrl = videoUrl
  localContent.value.title = file.name.replace(/\.[^/.]+$/, "")
  
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
</script>

<style scoped>
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
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.video-url-input {
  @apply mb-4;
}

.video-url-input label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.video-url-input input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500;
}
</style>
