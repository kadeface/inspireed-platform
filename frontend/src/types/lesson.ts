import type { Cell } from './cell'
import type { Course } from './curriculum'
import type { Resource } from './resource'

export const LessonStatus = {
  DRAFT: 'draft',
  PUBLISHED: 'published',
  ARCHIVED: 'archived',
} as const

export type LessonStatus = typeof LessonStatus[keyof typeof LessonStatus]

export interface Lesson {
  id: number
  title: string
  description?: string
  creator_id: number
  course_id: number
  status: LessonStatus
  content: Cell[]
  version: number
  parent_id?: number
  national_resource_id?: string
  tags?: string[]
  cover_image_url?: string
  created_at: string
  updated_at: string
  published_at?: string
  course?: Course
  
  // MVP: 参考资源相关字段
  reference_resource_id?: number
  reference_resource?: Resource
  reference_notes?: string
  cell_count: number
  estimated_duration?: number  // 预计时长（分钟）
  view_count: number
}

export interface LessonCreate {
  title: string
  description?: string
  course_id: number
  content?: Cell[]
  tags?: string[]
}

export interface LessonUpdate {
  title?: string
  description?: string
  course_id?: number
  content?: Cell[]
  tags?: string[]
  status?: LessonStatus
}

