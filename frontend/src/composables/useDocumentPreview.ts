import { computed, ref } from 'vue'
import { documentPreviewService } from '@/services/documentPreview'
import type { DocumentPreviewInfo } from '@/types/documentPreview'
import { getServerBaseUrl } from '@/utils/url'

export function useDocumentPreview() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const info = ref<DocumentPreviewInfo | null>(null)

  const previewAbsoluteUrl = computed(() => {
    let url = info.value?.preview_url
    if (!url) return null
    if (url.startsWith('/uploads/')) url = `${getServerBaseUrl()}${url}`
    return url
  })

  const displayKind = computed(() => {
    if (!info.value) return 'none'
    if (info.value.converted_to_pdf || info.value.file_type === 'pdf') return 'pdf'
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(info.value.file_type)) return 'image'
    return 'unsupported'
  })

  async function run(loader: () => Promise<DocumentPreviewInfo>) {
    loading.value = true
    error.value = null
    info.value = null
    try {
      const data = await loader()
      info.value = data
      if (
        data.conversion_error &&
        !data.converted_to_pdf &&
        !data.can_preview_directly &&
        ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(data.file_type)
      ) {
        error.value = data.conversion_error
      }
    } catch (e: any) {
      error.value = e?.message || '加载预览失败'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    info,
    previewAbsoluteUrl,
    displayKind,
    loadFromResource: (id: number) => run(() => documentPreviewService.getResourcePreview(id)),
    loadFromLibrary: (id: number) => run(() => documentPreviewService.getLibraryPreview(id)),
    loadFromFileUrl: (url: string) => run(() => documentPreviewService.getUploadPreview(url)),
    reset: () => {
      loading.value = false
      error.value = null
      info.value = null
    },
  }
}
