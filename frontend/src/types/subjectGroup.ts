/**
 * 学科教研组相关类型定义
 */

export enum GroupScope {
  SCHOOL = 'school',
  REGION = 'region',
  NATIONAL = 'national',
}

export enum MemberRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  MEMBER = 'member',
}

// ==================== 教研组相关 ====================

export interface SubjectGroup {
  id: number
  name: string
  description?: string
  subject_id: number
  grade_id?: number
  scope: GroupScope
  school_id?: number
  region_id?: number
  creator_id: number
  is_active: boolean
  is_public: boolean
  member_count: number
  lesson_count: number
  cover_image_url?: string
  created_at: string
  updated_at: string
  // 额外字段
  subject_name?: string
  grade_name?: string
  school_name?: string
  region_name?: string
  creator_name?: string
  user_role?: MemberRole
}

export interface SubjectGroupCreate {
  name: string
  description?: string
  subject_id: number
  grade_id?: number
  scope: GroupScope
  school_id?: number
  region_id?: number
  is_public?: boolean
  cover_image_url?: string
}

export interface SubjectGroupUpdate {
  name?: string
  description?: string
  grade_id?: number
  is_public?: boolean
  cover_image_url?: string
}

export interface SubjectGroupListResponse {
  items: SubjectGroup[]
  total: number
  page: number
  page_size: number
}

// ==================== 成员关系相关 ====================

export interface GroupMembership {
  id: number
  group_id: number
  user_id: number
  role: MemberRole
  is_active: boolean
  joined_at: string
  updated_at: string
  // 额外字段
  user_name?: string
  user_email?: string
  user_avatar_url?: string
}

export interface GroupMembershipCreate {
  user_id: number
  role?: MemberRole
}

export interface GroupMembershipUpdate {
  role?: MemberRole
  is_active?: boolean
}

export interface GroupMembershipListResponse {
  items: GroupMembership[]
  total: number
  page: number
  page_size: number
}

// ==================== 共享教学设计相关 ====================

export interface SharedLesson {
  id: number
  group_id: number
  lesson_id: number
  sharer_id: number
  share_note?: string
  is_active: boolean
  view_count: number
  download_count: number
  like_count: number
  shared_at: string
  updated_at: string
  // 额外字段
  lesson_title?: string
  lesson_description?: string
  lesson_cover_image_url?: string
  lesson_cell_count?: number
  lesson_estimated_duration?: number
  sharer_name?: string
  sharer_avatar_url?: string
  group_name?: string
}

export interface SharedLessonCreate {
  lesson_id: number
  share_note?: string
}

export interface SharedLessonUpdate {
  share_note?: string
  is_active?: boolean
}

export interface SharedLessonListResponse {
  items: SharedLesson[]
  total: number
  page: number
  page_size: number
}

// ==================== 统计信息 ====================

export interface SubjectGroupStatistics {
  total_groups: number
  total_members: number
  total_shared_lessons: number
  my_groups: number
  my_shared_lessons: number
}

// ==================== 查询参数 ====================

export interface SubjectGroupQueryParams {
  subject_id?: number
  grade_id?: number
  scope?: GroupScope
  school_id?: number
  region_id?: number
  is_public?: boolean
  my_groups?: boolean
  page?: number
  page_size?: number
}

export interface SharedLessonQueryParams {
  page?: number
  page_size?: number
}

export interface GroupMemberQueryParams {
  page?: number
  page_size?: number
}

