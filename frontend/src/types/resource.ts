/**
 * 资源相关类型定义（MVP）
 */

// 资源类型
export const ResourceType = {
  PDF: 'pdf',
  VIDEO: 'video',
  DOCUMENT: 'document',
  LINK: 'link',
} as const

export type ResourceType = typeof ResourceType[keyof typeof ResourceType]

// 章节类型
export interface Chapter {
  id: number
  course_id: number
  parent_id?: number
  name: string
  code?: string
  description?: string
  display_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// 带子章节的章节类型
export interface ChapterWithChildren extends Chapter {
  children: ChapterWithChildren[]
  resources_count: number
}

// 资源库资产摘要类型
export interface LibraryAssetSummary {
  id: number
  title: string
  asset_type: string
  mime_type?: string
  size_bytes?: number
  thumbnail_url?: string
  public_url?: string
  page_count?: number
  duration_seconds?: number
  visibility: string
  status: string
  updated_at: string
}

// 资源基础类型
export interface Resource {
  id: number
  chapter_id: number
  title: string
  description?: string
  resource_type: ResourceType
  
  // 资源库引用
  asset_id?: number
  asset?: LibraryAssetSummary
  
  // 文件相关（当 asset_id 为空时使用）
  file_url?: string
  file_size?: number  // 字节
  page_count?: number  // PDF 页数
  thumbnail_url?: string
  
  // 解析后的文件URL（优先使用 file_url，否则使用 asset.public_url）
  resolved_file_url?: string
  
  // 权限和状态
  is_official: boolean
  is_downloadable: boolean
  is_active: boolean
  display_order: number
  
  // 统计
  view_count: number
  download_count: number
  
  // 创建者
  created_by?: number
  
  // 时间戳
  created_at: string
  updated_at: string
}

// 资源详情类型（包含关联信息）
export interface ResourceDetail extends Resource {
  chapter?: {
    id: number
    name: string
    course_id: number
  }
  lessons_count: number  // 基于此资源创建的教案数量
}

// 资源列表响应
export interface ResourceListResponse {
  items: Resource[]
  total: number
  page: number
  page_size: number
}

// 创建资源请求
export interface ResourceCreate {
  chapter_id: number
  title: string
  description?: string
  resource_type: ResourceType
  is_official?: boolean
  is_downloadable?: boolean
  display_order?: number
}

// 更新资源请求
export interface ResourceUpdate {
  title?: string
  description?: string
  is_official?: boolean
  is_downloadable?: boolean
  is_active?: boolean
  display_order?: number
}

// 章节创建请求
export interface ChapterCreate {
  course_id: number
  parent_id?: number
  name: string
  code?: string
  description?: string
  display_order?: number
}

// 章节更新请求
export interface ChapterUpdate {
  name?: string
  code?: string
  description?: string
  display_order?: number
  is_active?: boolean
}

// 基于资源创建教案的请求
export interface CreateFromResourceRequest {
  reference_resource_id: number
  title: string
  description?: string
  reference_notes?: string
  tags?: string[]
  estimated_duration?: number  // 分钟
}

// 更新参考笔记请求
export interface UpdateReferenceNotesRequest {
  notes: string
}

// 工具函数：格式化文件大小
export function formatFileSize(bytes?: number): string {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 工具函数：获取资源类型图标
export function getResourceTypeIcon(type: ResourceType): string {
  const iconMap: Record<ResourceType, string> = {
    [ResourceType.PDF]: '📋',
    [ResourceType.VIDEO]: '🎥',
    [ResourceType.DOCUMENT]: '📄',
    [ResourceType.LINK]: '🔗'
  }
  return iconMap[type] || '📁'
}

// 工具函数：获取资源类型名称
export function getResourceTypeName(type: ResourceType): string {
  const nameMap: Record<ResourceType, string> = {
    [ResourceType.PDF]: 'PDF 文档',
    [ResourceType.VIDEO]: '视频',
    [ResourceType.DOCUMENT]: '文档',
    [ResourceType.LINK]: '链接'
  }
  return nameMap[type] || '未知'
}

