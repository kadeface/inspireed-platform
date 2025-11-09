/**
 * 管理员 API 服务
 */
import api from './api'

export interface UserStats {
  total_users: number
  admin_count: number
  researcher_count: number
  teacher_count: number
  student_count: number
  active_users: number
  inactive_users: number
}

export interface ContentStats {
  total_courses: number
  active_courses: number
  total_lessons: number
  published_lessons: number
  draft_lessons: number
  total_resources: number
}

export interface ActivityStats {
  users_created_today: number
  users_created_this_week: number
  users_created_this_month: number
  lessons_created_today: number
  lessons_created_this_week: number
  lessons_created_this_month: number
}

export interface DashboardOverview {
  user_stats: UserStats
  content_stats: ContentStats
  activity_stats: ActivityStats
  last_updated: string
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string | null
  role: string
  is_active: boolean
  created_at: string
  last_login?: string
  region_id?: number | null
  school_id?: number | null
  grade_id?: number | null
  classroom_id?: number | null
  region_name?: string | null
  school_name?: string | null
  grade_name?: string | null
  classroom_name?: string | null
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface UserCreate {
  username: string
  full_name?: string | null
  email: string
  password: string
  role: string
  is_active: boolean
  region_id?: number | null
  school_id?: number | null
  grade_id?: number | null
  classroom_id?: number | null
}

export interface UserUpdate {
  username?: string
  email?: string
  full_name?: string | null
  role?: string
  is_active?: boolean
  region_id?: number | null
  school_id?: number | null
  grade_id?: number | null
  classroom_id?: number | null
}

export interface BatchImportResult {
  message: string
  created_users: User[]
  errors: string[]
  success_count: number
  error_count: number
}

export interface Region {
  id: number
  name: string
  code: string
  level: number
  parent_id?: number
  is_active: boolean
  description?: string
  created_at: string
  updated_at: string
}

export interface School {
  id: number
  name: string
  code: string
  region_id: number
  school_type: string
  address?: string
  phone?: string
  email?: string
  principal?: string
  is_active: boolean
  description?: string
  created_at: string
  updated_at: string
  region?: Region
}

export interface RegionListResponse {
  regions: Region[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface SchoolListResponse {
  schools: School[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface Classroom {
  id: number
  name: string
  school_id: number
  grade_id: number
  code?: string | null
  enrollment_year?: number | null
  head_teacher_id?: number | null
  is_active: boolean
  description?: string | null
  created_at: string
  updated_at: string
}

export interface ClassroomListResponse {
  classrooms: Classroom[]
  total: number
  page: number
  size: number
  total_pages: number
}

export const adminService = {
  /**
   * 获取数据看板概览
   */
  async getDashboardOverview(): Promise<DashboardOverview> {
    return await api.get('/admin/dashboard/overview')
  },

  /**
   * 获取用户统计数据
   */
  async getUserStats(): Promise<UserStats> {
    return await api.get('/admin/dashboard/user-stats')
  },

  /**
   * 获取用户列表
   */
  async getUsers(params: {
    page?: number
    size?: number
    role?: string
    search?: string
  } = {}): Promise<UserListResponse> {
    return await api.get('/admin/users', { params })
  },

  /**
   * 获取用户详情
   */
  async getUser(userId: number): Promise<User> {
    return await api.get(`/admin/users/${userId}`)
  },

  /**
   * 创建用户
   */
  async createUser(userData: UserCreate): Promise<User> {
    return await api.post('/admin/users', userData)
  },

  /**
   * 更新用户
   */
  async updateUser(userId: number, userData: UserUpdate): Promise<User> {
    return await api.put(`/admin/users/${userId}`, userData)
  },

  /**
   * 删除用户
   */
  async deleteUser(userId: number): Promise<void> {
    return await api.delete(`/admin/users/${userId}`)
  },

  /**
   * 切换用户状态
   */
  async toggleUserStatus(userId: number): Promise<{ message: string; is_active: boolean }> {
    return await api.patch(`/admin/users/${userId}/toggle-status`)
  },

  /**
   * 重置用户密码
   */
  async resetUserPassword(userId: number): Promise<{ message: string; new_password: string }> {
    return await api.post(`/admin/users/${userId}/reset-password`)
  },

  /**
   * 批量导入用户
   */
  async batchImportUsers(users: UserCreate[]): Promise<BatchImportResult> {
    return await api.post('/admin/users/batch-import', { users })
  },

  /**
   * 下载导入模板
   */
  async getImportTemplate(): Promise<{ template: string; filename: string }> {
    return await api.get('/admin/users/export/template')
  },

  // ==================== 组织架构管理 ====================

  /**
   * 获取区域列表
   */
  async getRegions(params: {
    page?: number
    size?: number
    level?: number
    parent_id?: number
    search?: string
  } = {}): Promise<RegionListResponse> {
    return await api.get('/admin/organization/regions', { params })
  },

  /**
   * 获取区域详情
   */
  async getRegion(regionId: number): Promise<Region> {
    return await api.get(`/admin/organization/regions/${regionId}`)
  },

  /**
   * 创建区域
   */
  async createRegion(regionData: Partial<Region>): Promise<Region> {
    return await api.post('/admin/organization/regions', regionData)
  },

  /**
   * 更新区域
   */
  async updateRegion(regionId: number, regionData: Partial<Region>): Promise<Region> {
    return await api.put(`/admin/organization/regions/${regionId}`, regionData)
  },

  /**
   * 删除区域
   */
  async deleteRegion(regionId: number): Promise<void> {
    return await api.delete(`/admin/organization/regions/${regionId}`)
  },

  /**
   * 获取区域树形结构
   */
  async getRegionTree(): Promise<{ tree: any[] }> {
    return await api.get('/admin/organization/regions/tree')
  },

  /**
   * 获取学校列表
   */
  async getSchools(params: {
    page?: number
    size?: number
    region_id?: number
    school_type?: string
    search?: string
  } = {}): Promise<SchoolListResponse> {
    return await api.get('/admin/organization/schools', { params })
  },

  /**
   * 获取学校详情
   */
  async getSchool(schoolId: number): Promise<School> {
    return await api.get(`/admin/organization/schools/${schoolId}`)
  },

  /**
   * 创建学校
   */
  async createSchool(schoolData: Partial<School>): Promise<School> {
    return await api.post('/admin/organization/schools', schoolData)
  },

  /**
   * 更新学校
   */
  async updateSchool(schoolId: number, schoolData: Partial<School>): Promise<School> {
    return await api.put(`/admin/organization/schools/${schoolId}`, schoolData)
  },

  /**
   * 删除学校
   */
  async deleteSchool(schoolId: number): Promise<void> {
    return await api.delete(`/admin/organization/schools/${schoolId}`)
  },

  /**
   * 根据区域获取学校列表
   */
  async getSchoolsByRegion(regionId: number): Promise<{ schools: School[] }> {
    return await api.get(`/admin/organization/schools/by-region/${regionId}`)
  },

  /**
   * 获取班级列表
   */
  async getClassrooms(params: {
    page?: number
    size?: number
    school_id?: number
    grade_id?: number
    is_active?: boolean
    search?: string
  } = {}): Promise<ClassroomListResponse> {
    return await api.get('/admin/organization/classrooms', { params })
  },

  /**
   * 创建班级
   */
  async createClassroom(data: Partial<Classroom>): Promise<Classroom> {
    return await api.post('/admin/organization/classrooms', data)
  },

  /**
   * 更新班级
   */
  async updateClassroom(classroomId: number, data: Partial<Classroom>): Promise<Classroom> {
    return await api.put(`/admin/organization/classrooms/${classroomId}`, data)
  },

  /**
   * 删除班级
   */
  async deleteClassroom(classroomId: number): Promise<void> {
    return await api.delete(`/admin/organization/classrooms/${classroomId}`)
  }
}

export default adminService

