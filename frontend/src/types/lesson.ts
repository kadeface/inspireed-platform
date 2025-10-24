import type { Cell } from './cell'
import type { Course, Chapter } from './curriculum'
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
  chapter_id?: number  // 所属章节ID
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
  chapter?: Chapter  // 章节信息
  
  // MVP: 参考资源相关字段
  reference_resource_id?: number
  reference_resource?: Resource
  reference_notes?: string
  cell_count: number
  estimated_duration?: number  // 预计时长（分钟）
  view_count: number
  
  // 教师信息
  creator_name?: string
  creator_avatar?: string
  
  // 难度和评分（学生端增强）
  difficulty_level?: string
  average_rating?: number
  review_count?: number
}

export interface LessonCreate {
  title: string
  description?: string
  course_id: number
  chapter_id?: number  // 所属章节ID
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

