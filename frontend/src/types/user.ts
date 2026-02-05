export enum UserRole {
  ADMIN = 'admin',
  TEACHER = 'teacher',
  STUDENT = 'student',
  RESEARCHER = 'researcher',
  DISTRICT_ADMIN = 'district_admin',
  SCHOOL_ADMIN = 'school_admin',
}

/** 将 UserRole 映射为中文显示名称 */
export function getRoleDisplayName(role: UserRole | string | undefined): string {
  if (!role) return '管理员'
  const r = typeof role === 'string' ? role : String(role)
  const map: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
    researcher: '教研员',
    district_admin: '区县考试管理员',
    school_admin: '校级管理员',
  }
  return map[r] ?? '管理员'
}

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  role: UserRole
  is_active: boolean
  is_superuser: boolean
  avatar_url?: string
  region_id?: number | null
  school_id?: number | null
  grade_id?: number | null
  classroom_id?: number | null
  region_name?: string | null
  school_name?: string | null
  grade_name?: string | null
  classroom_name?: string | null
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
  role: UserRole
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

