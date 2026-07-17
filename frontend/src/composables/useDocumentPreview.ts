import { computed, ref } from 'vue'
import { documentPreviewService } from '@/services/documentPreview'
import type { DocumentPreviewInfo } from '@/types/documentPreview'
import { getServerBaseUrl } from '@/utils/url'

const MARKDOWN_EXTS = new Set(['md', 'markdown', 'txt'])
const OFFICE_EXTS = new Set(['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'])
const IMAGE_EXTS = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'])

function toAbsoluteUrl(url: string | null | undefined): string | null {
  if (!url) return null
  if (url.startsWith('/uploads/')) return `${getServerBaseUrl()}${url}`
  // 开发态误写成 :5173/uploads/... 时改回后端
  try {
    const u = new URL(url, getServerBaseUrl())
    if (u.pathname.startsWith('/uploads/')) {
      return `${getServerBaseUrl()}${u.pathname}${u.search}`
    }
  } catch {
    /* keep */
  }
  return url
}

function looksLikePdf(url?: string | null): boolean {
  if (!url) return false
  return /\.pdf(?:[?#]|$)/i.test(url)
}

export function useDocumentPreview() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const info = ref<DocumentPreviewInfo | null>(null)
  const markdownContent = ref<string | null>(null)

  const previewAbsoluteUrl = computed(() => toAbsoluteUrl(info.value?.preview_url))

  const displayKind = computed(() => {
    if (!info.value) return 'none'
    const ext = (info.value.file_type || '').toLowerCase()
    if (MARKDOWN_EXTS.has(ext)) return 'markdown'
    // 已转 PDF，或预览地址本身就是 PDF
    if (
      info.value.converted_to_pdf ||
      ext === 'pdf' ||
      looksLikePdf(info.value.preview_url)
    ) {
      return 'pdf'
    }
    if (IMAGE_EXTS.has(ext)) return 'image'
    return 'unsupported'
  })

  async function loadMarkdownText(fileUrl: string | null | undefined) {
    markdownContent.value = null
    const abs = toAbsoluteUrl(fileUrl)
    if (!abs) return
    try {
      const res = await fetch(abs)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      markdownContent.value = await res.text()
    } catch (e: any) {
      error.value = e?.message || '无法加载 Markdown 内容'
    }
  }

  async function run(loader: () => Promise<DocumentPreviewInfo>) {
    loading.value = true
    error.value = null
    info.value = null
    markdownContent.value = null
    try {
      const data = await loader()
      info.value = data
      const ext = (data.file_type || '').toLowerCase()

      if (data.conversion_error && !data.converted_to_pdf && !looksLikePdf(data.preview_url)) {
        error.value = data.conversion_error
      } else if (MARKDOWN_EXTS.has(ext)) {
        await loadMarkdownText(data.preview_url || data.file_url)
      } else if (
        !data.converted_to_pdf &&
        !looksLikePdf(data.preview_url) &&
        OFFICE_EXTS.has(ext)
      ) {
        error.value = data.conversion_error || '文档转换失败，请下载原文件查看'
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
    markdownContent,
    previewAbsoluteUrl,
    displayKind,
    loadFromResource: (id: number) => run(() => documentPreviewService.getResourcePreview(id)),
    loadFromLibrary: (id: number) => run(() => documentPreviewService.getLibraryPreview(id)),
    loadFromFileUrl: (url: string) => run(() => documentPreviewService.getUploadPreview(url)),
    reset: () => {
      loading.value = false
      error.value = null
      info.value = null
      markdownContent.value = null
    },
  }
}
