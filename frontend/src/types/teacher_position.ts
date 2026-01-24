/**
 * 教师职务类型相关类型定义
 */

export interface TeacherPositionTypeBase {
  name: string
  code?: string
  description?: string
  category?: string
  sort_order: number
  is_active: boolean
}

export interface TeacherPositionTypeCreate extends TeacherPositionTypeBase {}

export interface TeacherPositionTypeUpdate {
  name?: string
  code?: string
  description?: string
  category?: string
  sort_order?: number
  is_active?: boolean
}

export interface TeacherPositionTypeResponse extends TeacherPositionTypeBase {
  id: number
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface TeacherPositionTypeListResponse {
  position_types: TeacherPositionTypeResponse[]
  total: number
}
