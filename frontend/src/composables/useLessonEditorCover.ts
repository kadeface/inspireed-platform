/**
 * 教案编辑器 - 封面上传、预览、裁剪
 */

import { ref, computed, watch } from 'vue'
import { useLessonStore } from '../store/lesson'
import { lessonService } from '../services/lesson'
import api from '../services/api'
import { getServerBaseUrl } from '../utils/url'

export function useLessonEditorCover(
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void
) {
  const lessonStore = useLessonStore()

  const coverImageInput = ref<HTMLInputElement | null>(null)
  const isUploadingCoverImage = ref(false)
  const showCoverImagePreview = ref(false)
  const coverImagePreviewUrl = ref('')
  const coverImagePreviewFile = ref<File | null>(null)
  const coverImagePreview = ref<HTMLImageElement | null>(null)
  const imageQuality = ref(85)
  const maxImageWidth = ref(1920)
  const maxImageHeight = ref(1080)
  const coverImageLoadError = ref(false)

  const coverImageUrl = computed(() => {
    const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
    const url = (cur as any)?.cover_image_url
    if (!url) return null
    if (typeof url === 'string' && (url.startsWith('http://') || url.startsWith('https://'))) return url
    if (typeof url === 'string' && url.startsWith('/')) return `${getServerBaseUrl()}${url}`
    return url
  })

  watch(
    () => ((lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson)?.cover_image_url,
    () => { coverImageLoadError.value = false }
  )

  function triggerCoverImageUpload() {
    coverImageInput.value?.click()
  }

  function handleCoverImageSelect(e: Event) {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      showToast('error', '请选择图片文件')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      showToast('error', '图片文件大小不能超过10MB')
      return
    }
    coverImagePreviewFile.value = file
    coverImagePreviewUrl.value = URL.createObjectURL(file)
    showCoverImagePreview.value = true
  }

  function cancelCoverImageEdit() {
    showCoverImagePreview.value = false
    if (coverImagePreviewUrl.value) {
      URL.revokeObjectURL(coverImagePreviewUrl.value)
      coverImagePreviewUrl.value = ''
    }
    coverImagePreviewFile.value = null
    imageQuality.value = 85
    maxImageWidth.value = 1920
    maxImageHeight.value = 1080
    if (coverImageInput.value) coverImageInput.value.value = ''
  }

  function processImage(
    file: File,
    maxW: number,
    maxH: number,
    quality: number
  ): Promise<File> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        let w = img.width, h = img.height
        if (w > maxW || h > maxH) {
          const r = Math.min(maxW / w, maxH / h)
          w = Math.round(w * r)
          h = Math.round(h * r)
        }
        const canvas = document.createElement('canvas')
        canvas.width = w
        canvas.height = h
        const ctx = canvas.getContext('2d')
        if (!ctx) { reject(new Error('无法创建Canvas上下文')); return }
        ctx.drawImage(img, 0, 0, w, h)
        canvas.toBlob(
          (blob) => {
            if (!blob) { reject(new Error('图片处理失败')); return }
            resolve(new File([blob], file.name, { type: file.type, lastModified: Date.now() }))
          },
          file.type,
          quality
        )
      }
      img.onerror = () => reject(new Error('图片加载失败'))
      img.src = URL.createObjectURL(file)
    })
  }

  async function processAndUploadCoverImage() {
    const file = coverImagePreviewFile.value
    const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
    if (!file || !cur) return
    isUploadingCoverImage.value = true
    try {
      const processed = await processImage(
        file,
        maxImageWidth.value,
        maxImageHeight.value,
        imageQuality.value / 100
      )
      const formData = new FormData()
      formData.append('file', processed, file.name)
      const res = await api.post<{ file_url: string }>('/upload/', formData, { timeout: 30000 })
      const imageUrl = res.file_url
      ;(cur as any).cover_image_url = imageUrl
      await lessonService.updateLesson((cur as any).id, { cover_image_url: imageUrl })
      showToast('success', '封面图片上传成功')
      cancelCoverImageEdit()
    } catch (e: any) {
      console.error('上传封面图片失败:', e)
      showToast('error', e.response?.data?.detail || '上传封面图片失败')
    } finally {
      isUploadingCoverImage.value = false
    }
  }

  return {
    coverImageInput,
    isUploadingCoverImage,
    showCoverImagePreview,
    coverImagePreviewUrl,
    coverImagePreviewFile,
    coverImagePreview,
    imageQuality,
    maxImageWidth,
    maxImageHeight,
    coverImageLoadError,
    coverImageUrl,
    triggerCoverImageUpload,
    handleCoverImageSelect,
    cancelCoverImageEdit,
    processAndUploadCoverImage,
  }
}
