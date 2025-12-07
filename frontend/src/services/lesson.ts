/**
 * Lesson API 服务
 * 封装所有教案相关的 API 调用
 */

import { api } from './api'
import type {
  Lesson,
  LessonCreate,
  LessonUpdate,
  LessonClassroom,
  LessonRelatedMaterialListResponse
} from '../types/lesson'
import type { LessonListParams, LessonListResponse } from '../types/api'
import type { 
  Resource, 
  CreateFromResourceRequest, 
  UpdateReferenceNotesRequest 
} from '../types/resource'

/**
 * Lesson API 服务类
 */
class LessonService {
  private readonly basePath = '/lessons'

  /**
   * 获取教案列表
   * @param params 查询参数（分页、搜索、状态过滤）
   * @returns 教案列表响应
   */
  async fetchLessons(params?: LessonListParams): Promise<LessonListResponse> {
    try {
      const response = await api.get<LessonListResponse>(this.basePath, {
        params: {
          page: params?.page || 1,
          page_size: params?.page_size || 20,
          status: params?.status,
          search: params?.search,
          course_id: params?.course_id,
          chapter_id: params?.chapter_id,
          subject_id: params?.subject_id,
          grade_id: params?.grade_id,
          creator_only: params?.creator_only,
        },
      })
      return response
    } catch (error: any) {
      console.error('Failed to fetch lessons:', error)
      throw new Error(error.response?.data?.detail || '获取教案列表失败')
    }
  }

  /**
   * 根据 ID 获取教案详情
   * @param id 教案 ID
   * @returns 教案详情
   */
  async fetchLessonById(id: number): Promise<Lesson> {
    try {
      const response = await api.get<Lesson>(`${this.basePath}/${id}`)
      return response
    } catch (error: any) {
      console.error(`Failed to fetch lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '获取教案详情失败')
    }
  }

  /**
   * 创建新教案
   * @param data 教案创建数据
   * @returns 创建的教案
   */
  async createLesson(data: LessonCreate): Promise<Lesson> {
    try {
      const response = await api.post<Lesson>(this.basePath, data)
      return response
    } catch (error: any) {
      console.error('Failed to create lesson:', error)
      throw new Error(error.response?.data?.detail || '创建教案失败')
    }
  }

  /**
   * 更新教案
   * @param id 教案 ID
   * @param data 教案更新数据
   * @returns 更新后的教案
   */
  async updateLesson(id: number, data: LessonUpdate): Promise<Lesson> {
    try {
      const response = await api.put<Lesson>(`${this.basePath}/${id}`, data)
      return response
    } catch (error: any) {
      console.error(`Failed to update lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '更新教案失败')
    }
  }

  /**
   * 删除教案
   * @param id 教案 ID
   */
  async deleteLesson(id: number): Promise<void> {
    try {
      await api.delete<void>(`${this.basePath}/${id}`)
    } catch (error: any) {
      console.error(`Failed to delete lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '删除教案失败')
    }
  }

  /**
   * 发布教案
   * @param id 教案 ID
   * @returns 发布后的教案
   */
  async publishLesson(id: number, classroomIds: number[]): Promise<Lesson> {
    try {
      const response = await api.post<Lesson>(`${this.basePath}/${id}/publish`, {
        classroom_ids: classroomIds
      })
      return response
    } catch (error: any) {
      console.error(`Failed to publish lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '发布教案失败')
    }
  }

  /**
   * 取消发布教案（切换回草稿状态）
   * @param id 教案 ID
   * @returns 取消发布后的教案
   */
  async unpublishLesson(id: number): Promise<Lesson> {
    try {
      const response = await api.post<Lesson>(`${this.basePath}/${id}/unpublish`)
      return response
    } catch (error: any) {
      console.error(`Failed to unpublish lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '取消发布教案失败')
    }
  }

  /**
   * 复制教案
   * @param id 教案 ID
   * @returns 复制的新教案
   */
  async duplicateLesson(id: number): Promise<Lesson> {
    try {
      const response = await api.post<Lesson>(`${this.basePath}/${id}/duplicate`)
      return response
    } catch (error: any) {
      console.error(`Failed to duplicate lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '复制教案失败')
    }
  }

  // ========== MVP: 基于资源创建教案相关方法 ==========

  /**
   * 基于参考资源创建教案
   * @param data 创建教案请求数据
   * @returns 创建的教案
   */
  async createFromResource(data: CreateFromResourceRequest): Promise<Lesson> {
    try {
      const response = await api.post<Lesson>(`${this.basePath}/from-resource`, data)
      return response
    } catch (error: any) {
      console.error('Failed to create lesson from resource:', error)
      throw new Error(error.response?.data?.detail || '基于资源创建教案失败')
    }
  }

  /**
   * 获取教案的参考资源
   * @param id 教案 ID
   * @returns 参考资源详情，如果没有则返回 null
   */
  async getReferenceResource(id: number): Promise<Resource | null> {
    try {
      const response = await api.get<Resource | null>(
        `${this.basePath}/${id}/reference-resource`
      )
      return response
    } catch (error: any) {
      console.error(`Failed to get reference resource for lesson ${id}:`, error)
      // 如果没有参考资源，返回 null 而不是抛出错误
      if (error.response?.status === 404) {
        return null
      }
      throw new Error(error.response?.data?.detail || '获取参考资源失败')
    }
  }

  /**
   * 更新教案的参考笔记
   * @param id 教案 ID
   * @param notes 参考笔记内容
   * @returns 更新后的教案
   */
  async updateReferenceNotes(id: number, notes: string): Promise<Lesson> {
    try {
      const data: UpdateReferenceNotesRequest = { notes }
      const response = await api.put<Lesson>(
        `${this.basePath}/${id}/reference-notes`,
        data
      )
      return response
    } catch (error: any) {
      console.error(`Failed to update reference notes for lesson ${id}:`, error)
      throw new Error(error.response?.data?.detail || '更新参考笔记失败')
    }
  }

  /**
   * 获取指定章节下的教案列表
   * @param chapterId 章节ID
   * @param params 查询参数
   * @returns 教案列表响应
   */
  async fetchChapterLessons(chapterId: number, params?: LessonListParams): Promise<LessonListResponse> {
    try {
      const response = await api.get<LessonListResponse>(`${this.basePath}/chapter/${chapterId}`, {
        params: {
          page: params?.page || 1,
          page_size: params?.page_size || 20,
          status: params?.status,
          search: params?.search,
        },
      })
      return response
    } catch (error: any) {
      console.error(`Failed to fetch lessons for chapter ${chapterId}:`, error)
      throw new Error(error.response?.data?.detail || '获取章节教案列表失败')
    }
  }

  /**
   * 获取推荐课程
   * @param limit 推荐数量，默认10
   * @returns 推荐的课程列表
   */
  async fetchRecommendedLessons(limit: number = 10): Promise<LessonListResponse> {
    try {
      const response = await api.get<LessonListResponse>(`${this.basePath}/recommended`, {
        params: { limit }
      })
      return response
    } catch (error: any) {
      console.error('Failed to fetch recommended lessons:', error)
      throw new Error(error.response?.data?.detail || '获取推荐课程失败')
    }
  }

  /**
   * 获取课程关联素材列表
   * @param courseId 课程 ID
   * @param params 查询参数
   */
  async fetchRelatedMaterials(
    courseId: number,
    params?: {
      search?: string
      resource_type?: string
      page?: number
      page_size?: number
    }
  ): Promise<LessonRelatedMaterialListResponse> {
    try {
      const response = await api.get<LessonRelatedMaterialListResponse>(
        `${this.basePath}/courses/${courseId}/related-materials`,
        {
          params: {
            search: params?.search,
            resource_type: params?.resource_type,
            page: params?.page || 1,
            page_size: params?.page_size || 10,
          },
        }
      )
      return response
    } catch (error: any) {
      console.error(`Failed to fetch related materials for course ${courseId}:`, error)
      throw new Error(error.response?.data?.detail || '获取关联素材失败')
    }
  }

  /**
   * 获取可用于发布的班级列表
   */
  async fetchAvailableClassrooms(): Promise<LessonClassroom[]> {
    try {
      const response = await api.get<LessonClassroom[]>(`${this.basePath}/available-classrooms`)
      return response
    } catch (error: any) {
      console.error('Failed to fetch available classrooms:', error)
      throw new Error(error.response?.data?.detail || '获取班级列表失败')
    }
  }
}

// 导出单例实例
export const lessonService = new LessonService()

