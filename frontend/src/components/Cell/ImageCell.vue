<template>
  <div class="image-cell cell-container rounded-lg border border-gray-100 bg-white p-4">
    <div v-if="editable" class="space-y-4">
      <div
        v-if="!localContent.src"
        class="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 py-12 transition hover:border-blue-400 hover:bg-blue-50/40"
        @click="triggerFileInput"
      >
        <span class="text-3xl">🖼️</span>
        <p class="mt-2 text-sm font-medium text-gray-700">点击上传图片</p>
        <p class="mt-1 text-xs text-gray-500">或填写下方图片地址</p>
      </div>

      <div v-else class="space-y-3">
        <div class="relative overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
          <img
            :src="displaySrc"
            :alt="localContent.alt || ''"
            class="mx-auto max-h-[480px] w-full object-contain"
            @error="onImgError"
          />
          <div
            v-if="isUploading"
            class="absolute inset-0 flex items-center justify-center bg-black/40 text-sm font-medium text-white"
          >
            上传中 {{ uploadProgress }}%
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
            @click="triggerFileInput"
          >
            更换图片
          </button>
          <button
            type="button"
            class="rounded-lg border border-red-200 bg-white px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
            @click="clearImage"
          >
            清除
          </button>
        </div>
      </div>

      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        class="hidden"
        @change="onFileSelected"
      />

      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">图片地址（URL 或文件名）</label>
        <input
          v-model="localContent.src"
          type="text"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="https://... 或上传后自动填入"
          @blur="persist"
        />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">替代文本（无障碍）</label>
        <input
          v-model="localContent.alt"
          type="text"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="简述图片内容"
          @blur="persist"
        />
      </div>
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">说明文字（可选）</label>
        <input
          v-model="localContent.caption"
          type="text"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="显示在图片下方"
          @blur="persist"
        />
      </div>
    </div>

    <div v-else class="image-cell-view">
      <figure class="mx-auto" :style="figureStyle">
        <img
          v-if="displaySrc"
          :src="displaySrc"
          :alt="localContent.alt || ''"
          class="w-full rounded-lg object-contain shadow-sm"
          loading="lazy"
          @error="onImgError"
        />
        <p v-else class="py-8 text-center text-sm text-gray-500">暂无图片</p>
        <figcaption
          v-if="localContent.caption"
          class="mt-2 text-center text-sm text-gray-600"
        >
          {{ localContent.caption }}
        </figcaption>
      </figure>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { Cell, ImageCell as ImageCellType } from '../../types/cell'
import { CellType } from '../../types/cell'
import api from '../../services/api'
import { getServerBaseUrl } from '../../utils/url'
import { normalizeResourceUrl } from '../../utils/normalizeResourceUrl'

interface Props {
  cell: Cell
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [cell: Cell]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)
const uploadProgress = ref(0)

const localContent = reactive({
  src: '',
  alt: '',
  caption: '',
})

function syncFromCell() {
  const c = (props.cell as ImageCellType).content
  localContent.src = c?.src ?? ''
  localContent.alt = c?.alt ?? ''
  localContent.caption = c?.caption ?? ''
}

watch(
  () => props.cell,
  () => {
    syncFromCell()
  },
  { deep: true, immediate: true }
)

const align = computed(() => (props.cell as ImageCellType).config?.align ?? 'center')
const maxWidth = computed(() => (props.cell as ImageCellType).config?.maxWidth ?? '100%')

const figureStyle = computed(() => ({
  maxWidth: maxWidth.value,
  marginLeft: align.value === 'left' ? '0' : align.value === 'right' ? 'auto' : 'auto',
  marginRight: align.value === 'right' ? '0' : align.value === 'left' ? 'auto' : 'auto',
}))

function extractFilename(url: string): string {
  if (!url || url.startsWith('blob:') || url.startsWith('data:')) return url
  if (!url.includes('/') && !url.startsWith('http://') && !url.startsWith('https://')) return url
  try {
    const urlObj = new URL(url, getServerBaseUrl())
    const filename = urlObj.pathname.split('/').pop() || ''
    return filename.split('?')[0].split('#')[0] || url
  } catch {
    if (url.includes('/')) {
      const parts = url.split('/')
      const filename = parts[parts.length - 1]
      return filename.split('?')[0].split('#')[0] || url
    }
    return url
  }
}

function resolveDisplaySrc(src: string): string {
  if (!src) return ''
  if (src.startsWith('blob:') || src.startsWith('data:')) return src
  if (src.startsWith('http://') || src.startsWith('https://')) {
    return normalizeResourceUrl(src)
  }
  if (src.startsWith('/uploads/')) {
    return `${getServerBaseUrl()}${src}`
  }
  if (src.startsWith('/')) {
    return `${getServerBaseUrl()}${src}`
  }
  if (/\.(png|jpe?g|gif|webp|svg|avif)$/i.test(src)) {
    return `${getServerBaseUrl()}/uploads/resources/${src}`
  }
  return src
}

const displaySrc = computed(() => resolveDisplaySrc(localContent.src))

function triggerFileInput() {
  fileInputRef.value?.click()
}

function persist() {
  const updated: ImageCellType = {
    ...(props.cell as ImageCellType),
    type: CellType.IMAGE,
    content: {
      src: localContent.src.trim(),
      alt: localContent.alt?.trim() || undefined,
      caption: localContent.caption?.trim() || undefined,
    },
  }
  emit('update', updated)
}

function clearImage() {
  localContent.src = ''
  persist()
}

function onImgError() {
  // 静默：错误图片由浏览器处理
}

async function onFileSelected(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || !file.type.startsWith('image/')) {
    if (file) alert('请选择图片文件')
    return
  }
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    alert('图片文件大小不能超过 10MB')
    return
  }

  isUploading.value = true
  uploadProgress.value = 0
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<{ file_url: string; filename?: string }>('/upload/', formData, {
      onUploadProgress: (e) => {
        if (e.total) uploadProgress.value = Math.round((e.loaded * 100) / e.total)
      },
      timeout: 300000,
    })
    const filename = extractFilename(response.file_url)
    localContent.src = filename
    persist()
    uploadProgress.value = 100
  } catch (err: any) {
    console.error(err)
    alert(err.response?.data?.detail || err.message || '上传失败')
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.image-cell-view img {
  max-height: min(70vh, 720px);
}
</style>
