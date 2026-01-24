import type { Cell } from './cell'

/**
 * 大环节（Section）类型 - 存于 Lesson.content.sections 中的结构
 */
export interface SectionInContent {
  id: string
  name: string
  type: 'default' | 'custom'
  order: number
  is_collapsed?: boolean
  cells: Cell[]
}

/**
 * Lesson.content 新格式：按大环节组织
 */
export interface LessonContentWithSections {
  sections: SectionInContent[]
}

/**
 * 大环节（Section）类型 - API 返回
 */
export interface Section {
  id: number | string  // 支持字符串ID（新建时）
  lesson_id: number
  name: string
  type: 'default' | 'custom'
  order: number
  is_collapsed?: boolean
  cells: Cell[]
  created_at?: string
  updated_at?: string
}

/**
 * 创建大环节请求
 */
export interface SectionCreate {
  lesson_id: number
  name: string
  type?: 'default' | 'custom'
  order?: number
  is_collapsed?: boolean
}

/**
 * 更新大环节请求
 */
export interface SectionUpdate {
  name?: string
  order?: number
  is_collapsed?: boolean
}

/**
 * 移动大环节请求
 */
export interface SectionMove {
  new_order: number
}

/**
 * 移动 Cell 到指定大环节请求
 */
export interface CellMoveRequest {
  section_id: number
  new_order?: number
}
