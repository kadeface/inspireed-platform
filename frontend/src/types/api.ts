/**
 * 通用 API 响应类型定义
 */

import type { Lesson, LessonStatus } from './lesson'

/**
 * 标准 API 响应格式
 */
export interface ApiResponse<T> {
  data: T
  message?: string
}

/**
 * 分页响应格式
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/**
 * 教案列表查询参数
 */
export interface LessonListParams {
  page?: number
  page_size?: number
  status?: LessonStatus
  search?: string
  course_id?: number
  chapter_id?: number
  subject_id?: number
  grade_id?: number
}

/**
 * 教案列表响应类型
 */
export type LessonListResponse = PaginatedResponse<Lesson>

/**
 * API 错误响应
 */
export interface ApiError {
  detail: string
  status_code?: number
}

