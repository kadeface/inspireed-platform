export interface DocumentPreviewInfo {
  title?: string | null
  file_url: string
  file_type: string
  file_size?: number | null
  page_count?: number | null
  can_preview_directly: boolean
  preview_url: string
  converted_to_pdf: boolean
  conversion_error?: string | null
  resource_id?: number
  asset_id?: number
}
