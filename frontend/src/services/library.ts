/**
 * 资源库服务
 */

import api from './api'
import type {
  LibraryAssetSummary,
  LibraryAssetDetail,
  LibraryAssetListResponse,
  LibraryAssetUpdateRequest,
  LibraryAssetUploadResponse,
  LibraryAssetUsageResponse,
} from '../types/library'

export interface LibraryAssetListParams {
  query?: string
  asset_type?: string
  visibility?: string
  subject_id?: number
  grade_id?: number
  knowledge_point_category?: string
  status?: string
  page?: number
  page_size?: number
}

class LibraryService {
  private basePath = '/library/assets'

  /**
   * 获取资源库资产列表
   */
  async listAssets(params?: LibraryAssetListParams): Promise<LibraryAssetListResponse> {
    try {
      const queryParams = new URLSearchParams()
      if (params?.query) queryParams.append('query', params.query)
      if (params?.asset_type) queryParams.append('asset_type', params.asset_type)
      if (params?.visibility) queryParams.append('visibility', params.visibility)
      if (params?.subject_id) queryParams.append('subject_id', params.subject_id.toString())
      if (params?.grade_id !== undefined) queryParams.append('grade_id', params.grade_id.toString())
      if (params?.knowledge_point_category) queryParams.append('knowledge_point_category', params.knowledge_point_category)
      if (params?.status) queryParams.append('status', params.status)
      if (params?.page) queryParams.append('page', params.page.toString())
      if (params?.page_size) queryParams.append('page_size', params.page_size.toString())

      const queryString = queryParams.toString()
      const url = queryString ? `${this.basePath}?${queryString}` : this.basePath

      return await api.get<LibraryAssetListResponse>(url)
    } catch (error) {
      console.error('Failed to list library assets:', error)
      throw error
    }
  }

  /**
   * 获取资源库资产详情
   */
  async getAsset(id: number): Promise<LibraryAssetDetail> {
    try {
      return await api.get<LibraryAssetDetail>(`${this.basePath}/${id}`)
    } catch (error) {
      console.error(`Failed to get library asset ${id}:`, error)
      throw error
    }
  }

  /**
   * 上传资源到资源库
   */
  async uploadAsset(
    file: File,
    metadata: {
      title: string
      description?: string
      asset_type?: string
      visibility?: string
      subject_id?: number
      grade_id?: number
      knowledge_point_category?: string
      knowledge_point_name?: string
    }
  ): Promise<LibraryAssetUploadResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', metadata.title)
      if (metadata.description) formData.append('description', metadata.description)
      if (metadata.asset_type) formData.append('asset_type', metadata.asset_type)
      if (metadata.visibility) formData.append('visibility', metadata.visibility)
      if (metadata.subject_id) formData.append('subject_id', metadata.subject_id.toString())
      if (metadata.grade_id) formData.append('grade_id', metadata.grade_id.toString())
      if (metadata.knowledge_point_category) formData.append('knowledge_point_category', metadata.knowledge_point_category)
      if (metadata.knowledge_point_name) formData.append('knowledge_point_name', metadata.knowledge_point_name)

      return await api.post<LibraryAssetUploadResponse>(this.basePath, formData)
    } catch (error) {
      console.error('Failed to upload library asset:', error)
      throw error
    }
  }

  /**
   * 更新资源库资产
   */
  async updateAsset(id: number, data: LibraryAssetUpdateRequest): Promise<LibraryAssetDetail> {
    try {
      return await api.patch<LibraryAssetDetail>(`${this.basePath}/${id}`, data)
    } catch (error) {
      console.error(`Failed to update library asset ${id}:`, error)
      throw error
    }
  }

  /**
   * 删除资源库资产
   */
  async deleteAsset(id: number): Promise<void> {
    try {
      await api.delete(`${this.basePath}/${id}`)
    } catch (error) {
      console.error(`Failed to delete library asset ${id}:`, error)
      throw error
    }
  }

  /**
   * 获取资源库资产使用情况
   */
  async getAssetUsages(id: number): Promise<LibraryAssetUsageResponse> {
    try {
      return await api.get<LibraryAssetUsageResponse>(`${this.basePath}/${id}/usages`)
    } catch (error) {
      console.error(`Failed to get library asset usages ${id}:`, error)
      throw error
    }
  }

  /**
   * 增加资源库资产的点击次数
   */
  async incrementViewCount(id: number): Promise<{ message: string; view_count: number }> {
    try {
      return await api.post<{ message: string; view_count: number }>(
        `${this.basePath}/${id}/increment-view`,
        {}
      )
    } catch (error) {
      console.error(`Failed to increment view count for asset ${id}:`, error)
      throw error
    }
  }

  /**
   * 获取资源库资产的文件内容（用于编辑HTML等文本文件）
   */
  async getAssetContent(id: number): Promise<{ content: string }> {
    try {
      return await api.get<{ content: string }>(`${this.basePath}/${id}/content`)
    } catch (error) {
      console.error(`Failed to get asset content ${id}:`, error)
      throw error
    }
  }

  /**
   * 获取资源库统计信息（公开接口，无需登录）
   */
  async getPublicStatistics(): Promise<{ html_resource_count: number; lesson_count: number; cell_count: number }> {
    try {
      return await api.get<{ html_resource_count: number; lesson_count: number; cell_count: number }>('/public/curriculum/statistics/resources')
    } catch (error) {
      console.error('Failed to get public resource statistics:', error)
      throw error
    }
  }
}

export const libraryService = new LibraryService()
export default libraryService
