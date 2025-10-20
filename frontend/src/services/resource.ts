/**
 * 资源相关服务（MVP）
 */
import api from './api'
import type {
  Resource,
  ResourceDetail,
  ResourceListResponse,
  ResourceCreate,
  ResourceUpdate,
  Chapter,
  ChapterWithChildren,
  ChapterCreate,
  ChapterUpdate,
  CreateFromResourceRequest,
  UpdateReferenceNotesRequest
} from '../types/resource'

/**
 * 资源服务
 */
export const resourceService = {
  /**
   * 获取资源列表（支持按章节筛选）
   */
  async listResources(params?: {
    chapter_id?: number
    resource_type?: string
    is_official?: boolean
  }): Promise<Resource[]> {
    const response = await api.get<Resource[]>('/resources/', { params })
    return response
  },

  /**
   * 获取章节的资源列表
   */
  async getChapterResources(
    chapterId: number,
    params?: {
      resource_type?: string
      page?: number
      page_size?: number
    }
  ): Promise<ResourceListResponse> {
    const data = await api.get<ResourceListResponse>(
      `/chapters/${chapterId}/resources`,
      { params }
    )
    return data
  },

  /**
   * 获取资源详情
   */
  async getResource(resourceId: number): Promise<ResourceDetail> {
    const response = await api.get<ResourceDetail>(`/resources/${resourceId}`)
    return response
  },

  /**
   * 创建资源（管理员）
   */
  async createResource(
    data: ResourceCreate,
    file?: File
  ): Promise<Resource> {
    const formData = new FormData()
    
    // 添加表单字段
    formData.append('chapter_id', data.chapter_id.toString())
    formData.append('title', data.title)
    if (data.description) formData.append('description', data.description)
    formData.append('resource_type', data.resource_type)
    if (data.is_official !== undefined) {
      formData.append('is_official', data.is_official.toString())
    }
    if (data.is_downloadable !== undefined) {
      formData.append('is_downloadable', data.is_downloadable.toString())
    }
    
    // 添加文件
    if (file) {
      formData.append('file', file)
    }
    
    console.log('发送请求到 /resources/', {
      chapter_id: data.chapter_id,
      title: data.title,
      resource_type: data.resource_type,
      file_name: file?.name
    })
    
    // 调试FormData内容
    console.log('FormData内容:')
    for (const [key, value] of formData.entries()) {
      console.log(`${key}:`, value, typeof value)
    }
    
    // 检查是否缺少必填字段
    const requiredFields = ['chapter_id', 'title', 'resource_type']
    const missingFields = requiredFields.filter(field => !formData.has(field))
    if (missingFields.length > 0) {
      console.error('缺少必填字段:', missingFields)
    }
    
    // 对于multipart/form-data，让axios自动设置Content-Type（包含boundary）
    console.log('准备发送请求，URL:', '/resources/')
    console.log('请求配置:', {
      method: 'POST',
      url: '/resources/',
      data: 'FormData对象'
    })
    
    const resource = await api.post<Resource>('/resources/', formData)
    
    console.log('创建的资源:', resource)
    return resource
  },

  /**
   * 上传资源到指定章节（便捷方法）
   */
  async uploadResourceToChapter(
    chapterId: number,
    file: File,
    title: string,
    description?: string,
    resourceType: string = 'document'
  ): Promise<number> {
    const data: ResourceCreate = {
      chapter_id: chapterId,
      title,
      description: description || '',
      resource_type: resourceType,
      is_official: true,
      is_downloadable: true
    }
    
    const resource = await this.createResource(data, file)
    return resource.id
  },

  /**
   * 更新资源（管理员）
   */
  async updateResource(
    resourceId: number,
    data: ResourceUpdate
  ): Promise<Resource> {
    const response = await api.put<Resource>(
      `/resources/${resourceId}`,
      data
    )
    return response
  },

  /**
   * 删除资源（管理员）
   */
  async deleteResource(resourceId: number): Promise<void> {
    await api.delete(`/resources/${resourceId}`)
  },

  /**
   * 下载资源
   */
  async downloadResource(resourceId: number): Promise<{
    download_url: string
    filename: string
  }> {
    const response = await api.post<{
      download_url: string
      filename: string
    }>(`/resources/${resourceId}/download`)
    return response
  },

  /**
   * 获取 PDF 预览 URL
   */
  getPDFPreviewUrl(resourceId: number): string {
    return `${api.defaults.baseURL}/resources/${resourceId}`
  }
}

/**
 * 章节服务
 */
export const chapterService = {
  /**
   * 获取课程的章节列表（树形结构）
   */
  async getCourseChapters(
    courseId: number,
    includeChildren: boolean = true
  ): Promise<ChapterWithChildren[]> {
    const response = await api.get(
      `/chapters/courses/${courseId}/chapters`,
      { params: { include_children: includeChildren } }
    )
    // api.get 已经返回 response.data，不需要再取 .data
    return response
  },

  /**
   * 获取章节详情
   */
  async getChapter(chapterId: number): Promise<Chapter> {
    const response = await api.get<Chapter>(`/chapters/${chapterId}`)
    return response
  },

  /**
   * 创建章节（管理员）
   */
  async createChapter(data: ChapterCreate): Promise<Chapter> {
    const response = await api.post<Chapter>('/chapters', data)
    return response
  },

  /**
   * 更新章节（管理员）
   */
  async updateChapter(
    chapterId: number,
    data: ChapterUpdate
  ): Promise<Chapter> {
    const response = await api.put<Chapter>(`/chapters/${chapterId}`, data)
    return response
  },

  /**
   * 删除章节（管理员）
   */
  async deleteChapter(chapterId: number): Promise<void> {
    await api.delete(`/chapters/${chapterId}`)
  }
}

/**
 * 导出默认对象
 */
export default {
  ...resourceService,
  chapter: chapterService
}

