/**
 * 课程体系相关类型定义
 */

// 学段定义
export interface EducationStage {
  id: number
  name: string
  code: string
  description?: string
  level: number // 1-小学, 2-初中, 3-高中
  is_active: boolean
  display_order: number
  created_at: string
  updated_at: string
}

// 教材版本
export interface TextbookVersion {
  id: number
  name: string
  code: string
  publisher: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// 教材
export interface Textbook {
  id: number
  subject_id: number
  grade_id: number
  version_id: number
  name: string
  semester: 'up' | 'down' // 上册/下册
  cover_image?: string
  is_active: boolean
  created_at: string
  updated_at: string
  subject?: Subject
  grade?: Grade
  version?: TextbookVersion
}

// 章节
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
  children?: Chapter[]
  resources_count?: number
}

export interface ChapterCreate {
  course_id: number
  parent_id?: number
  name: string
  code?: string
  description?: string
  display_order?: number
}

export interface ChapterUpdate {
  name?: string
  code?: string
  description?: string
  display_order?: number
  is_active?: boolean
}

export interface ChapterImportRow {
  name: string
  code: string
  description?: string
  display_order: number
  parent_code?: string
  is_active?: boolean
}

// 课程资源
export interface CourseResource {
  id: number
  chapter_id: number
  title: string
  type: 'course' | 'course_package' // 课程、课程包
  thumbnail?: string
  instructor: string
  publisher: string
  publish_date: string
  view_count: number
  like_count: number
  rating: number
  duration?: string
  is_featured: boolean
  tags: string[]
  grade: string
  subject: string
}

export interface Subject {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
  display_order: number
  created_at: string
  updated_at: string
}

export interface Grade {
  id: number
  name: string
  level: number
  stage_id: number // 关联学段
  is_active: boolean
  created_at: string
  updated_at: string
  stage?: EducationStage
}

export interface Course {
  id: number
  subject_id: number
  grade_id: number
  name: string
  code?: string
  description?: string
  is_active: boolean
  display_order: number
  created_by?: number
  created_at: string
  updated_at: string
  subject?: Subject
  grade?: Grade
}

export interface CourseCreate {
  subject_id: number
  grade_id: number
  name: string
  code?: string
  description?: string
  display_order?: number
}

export interface CourseUpdate {
  name?: string
  code?: string
  description?: string
  display_order?: number
  is_active?: boolean
}

// 树形结构节点
export interface CourseTreeNode {
  id: number
  name: string
  code?: string
  description?: string
  is_active: boolean
  lesson_count: number
}

export interface GradeTreeNode {
  id: number
  name: string
  level: number
  stage_id: number
  is_active: boolean
  courses: CourseTreeNode[]
  lesson_count: number
}

export interface SubjectTreeNode {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
  grades: GradeTreeNode[]
  lesson_count: number
}

export interface StageTreeNode {
  id: number
  name: string
  code: string
  level: number
  description?: string
  is_active: boolean
  subjects: SubjectTreeNode[]
  lesson_count: number
}

export interface CurriculumTree {
  subjects: SubjectTreeNode[]
  total_subjects: number
  total_grades: number
  total_courses: number
  total_lessons: number
}

