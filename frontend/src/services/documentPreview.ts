import api from './api'
import type { DocumentPreviewInfo } from '../types/documentPreview'

export const documentPreviewService = {
  getResourcePreview(resourceId: number) {
    return api.get<DocumentPreviewInfo>(`/resources/${resourceId}/preview`)
  },
  getLibraryPreview(assetId: number) {
    return api.get<DocumentPreviewInfo>(`/library/assets/${assetId}/preview`)
  },
  getUploadPreview(fileUrl: string) {
    return api.post<DocumentPreviewInfo>('/upload/preview', { file_url: fileUrl })
  },
}
