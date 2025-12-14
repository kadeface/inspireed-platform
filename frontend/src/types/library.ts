/**
 * 资源库相关类型定义
 */

// 资源库资产类型
export const LibraryAssetType = {
  PDF: 'pdf',
  VIDEO: 'video',
  IMAGE: 'image',
  AUDIO: 'audio',
  DOCUMENT: 'document',
  LINK: 'link',
  ZIP: 'zip',
  INTERACTIVE: 'interactive',
  OTHER: 'other',
} as const

export type LibraryAssetType = typeof LibraryAssetType[keyof typeof LibraryAssetType]

// 可见性类型
export const AssetVisibility = {
  TEACHER_ONLY: 'teacher_only',
  SCHOOL: 'school',
} as const

export type AssetVisibility = typeof AssetVisibility[keyof typeof AssetVisibility]

// 资产状态
export const AssetStatus = {
  ACTIVE: 'active',
  PROCESSING: 'processing',
  DISABLED: 'disabled',
  DELETED: 'deleted',
} as const

export type AssetStatus = typeof AssetStatus[keyof typeof AssetStatus]

// 资源库资产摘要
export interface LibraryAssetSummary {
  id: number
  title: string
  asset_type: LibraryAssetType
  mime_type?: string
  size_bytes?: number
  thumbnail_url?: string
  public_url?: string
  page_count?: number
  duration_seconds?: number
  visibility: AssetVisibility
  status: AssetStatus
  subject_id?: number
  grade_id?: number
  updated_at: string
}

// 资源库资产详情
export interface LibraryAssetDetail {
  id: number
  school_id: number
  owner_user_id: number
  title: string
  description?: string
  asset_type: LibraryAssetType
  mime_type?: string
  size_bytes?: number
  storage_provider: string
  storage_key: string
  public_url?: string
  sha256?: string
  thumbnail_url?: string
  page_count?: number
  duration_seconds?: number
  visibility: AssetVisibility
  status: AssetStatus
  subject_id?: number
  grade_id?: number
  created_at: string
  updated_at: string
}

// 资源库资产列表响应
export interface LibraryAssetListResponse {
  items: LibraryAssetSummary[]
  total: number
  page: number
  page_size: number
}

// 创建资源库资产请求
export interface LibraryAssetCreateRequest {
  title: string
  description?: string
  asset_type?: LibraryAssetType
  visibility?: AssetVisibility
  subject_id?: number
  grade_id?: number
}

// 更新资源库资产请求
export interface LibraryAssetUpdateRequest {
  title?: string
  description?: string
  visibility?: AssetVisibility
  status?: AssetStatus
  subject_id?: number
  grade_id?: number
}

// 资源库资产上传响应
export interface LibraryAssetUploadResponse {
  id: number
  title: string
  asset_type: LibraryAssetType
  public_url?: string
  size_bytes?: number
  thumbnail_url?: string
}

// 资源库资产使用情况
export interface LibraryAssetUsage {
  resource_id: number
  resource_title: string
  chapter_id: number
  chapter_name: string
  course_id: number
  course_name: string
}

export interface LibraryAssetUsageResponse {
  asset_id: number
  asset_title: string
  usages: LibraryAssetUsage[]
  total_usages: number
}

// 工具函数：格式化文件大小
export function formatFileSize(bytes?: number): string {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 工具函数：获取资产类型图标
export function getAssetTypeIcon(type: LibraryAssetType): string {
  const iconMap: Record<LibraryAssetType, string> = {
    [LibraryAssetType.PDF]: '📋',
    [LibraryAssetType.VIDEO]: '🎥',
    [LibraryAssetType.IMAGE]: '🖼️',
    [LibraryAssetType.AUDIO]: '🎵',
    [LibraryAssetType.DOCUMENT]: '📄',
    [LibraryAssetType.LINK]: '🔗',
    [LibraryAssetType.ZIP]: '📦',
    [LibraryAssetType.INTERACTIVE]: '🎮',
    [LibraryAssetType.OTHER]: '📁',
  }
  return iconMap[type] || '📁'
}

// 工具函数：获取资产类型名称
export function getAssetTypeName(type: LibraryAssetType): string {
  const nameMap: Record<LibraryAssetType, string> = {
    [LibraryAssetType.PDF]: 'PDF 文档',
    [LibraryAssetType.VIDEO]: '视频',
    [LibraryAssetType.IMAGE]: '图片',
    [LibraryAssetType.AUDIO]: '音频',
    [LibraryAssetType.DOCUMENT]: '文档',
    [LibraryAssetType.LINK]: '链接',
    [LibraryAssetType.ZIP]: '压缩包',
    [LibraryAssetType.INTERACTIVE]: '交互式课件',
    [LibraryAssetType.OTHER]: '其他',
  }
  return nameMap[type] || '未知'
}

// 工具函数：获取可见性名称
export function getVisibilityName(visibility: AssetVisibility): string {
  const nameMap: Record<AssetVisibility, string> = {
    [AssetVisibility.TEACHER_ONLY]: '仅自己可见',
    [AssetVisibility.SCHOOL]: '全校可见',
  }
  return nameMap[visibility] || '未知'
}

// 资源目录树节点类型
export type ResourceTreeNodeKind = 'root' | 'category' | 'subject' | 'grade' | 'asset_type' | 'visibility'

export interface ResourceTreeNode {
  id: string
  label: string
  kind: ResourceTreeNodeKind
  subject_id?: number
  grade_id?: number | null  // null 表示"通用/跨年级"
  asset_type?: string
  children?: ResourceTreeNode[]
  icon?: string
  count?: number  // 该节点下的资源数量（可选，后续优化）
}

// 资源筛选条件
export interface ResourceFilter {
  subject_id?: number
  grade_id?: number | null  // null 表示只显示通用资源
  asset_type?: string
  visibility?: AssetVisibility
}
