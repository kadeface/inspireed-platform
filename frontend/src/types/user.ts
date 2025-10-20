export enum UserRole {
  ADMIN = 'admin',
  TEACHER = 'teacher',
  STUDENT = 'student',
  RESEARCHER = 'researcher',
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

