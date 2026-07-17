import api from './api'
import type { DocumentPreviewInfo } from '../types/documentPreview'

/** Preview conversion can take a while; keep above backend LibreOffice 90s timeout. */
const PREVIEW_TIMEOUT_MS = 150_000

function previewRequestError(error: unknown): Error {
  const err = error as { code?: string; message?: string; response?: { data?: { detail?: string } } }
  if (err?.code === 'ECONNABORTED' || /timeout/i.test(err?.message || '')) {
    return new Error(
      '预览超时。若文档较大请稍后重试；若持续失败请确认服务器已安装 LibreOffice，或先下载原文件查看。'
    )
  }
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail) {
    return new Error(detail)
  }
  return error instanceof Error ? error : new Error('加载预览失败')
}

export const documentPreviewService = {
  async getResourcePreview(resourceId: number) {
    try {
      return await api.get<DocumentPreviewInfo>(`/resources/${resourceId}/preview`, {
        timeout: PREVIEW_TIMEOUT_MS,
      })
    } catch (e) {
      throw previewRequestError(e)
    }
  },
  async getLibraryPreview(assetId: number) {
    try {
      return await api.get<DocumentPreviewInfo>(`/library/assets/${assetId}/preview`, {
        timeout: PREVIEW_TIMEOUT_MS,
      })
    } catch (e) {
      throw previewRequestError(e)
    }
  },
  async getUploadPreview(fileUrl: string) {
    try {
      return await api.post<DocumentPreviewInfo>(
        '/upload/preview',
        { file_url: fileUrl },
        { timeout: PREVIEW_TIMEOUT_MS }
      )
    } catch (e) {
      throw previewRequestError(e)
    }
  },
}
