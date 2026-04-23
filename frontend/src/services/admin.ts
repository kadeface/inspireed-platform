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

export interface ExamStats {
  totalExams: number
  totalStudents: number
  completedRate: number
  pendingTasks: number
}

export interface ValueAddedStats {
  totalReports: number
  avgProgress: number
  improvedSchools: number
  excellentClasses: number
}

export interface StudentImprover {
  id: number
  name: string
  school: string
  class: string
  improvement: number
}

export interface TopStudent {
  id: number
  name: string
  school: string
  class: string
  score: number
}

export interface SubjectTopper {
  subject: string
  name: string
  school: string
  score: number
}

export interface StudentAchievements {
  topImprovers: StudentImprover[]
  topStudents: TopStudent[]
  subjectToppers: SubjectTopper[]
}

export interface SchoolImproved {
  id: number
  name: string
  improvement: number
}

export interface SchoolQuality {
  id: number
  name: string
  avgScore: number
}

export interface SchoolValueAdded {
  id: number
  name: string
  valueIndex: number
}

export interface SchoolHighlights {
  topImprovedSchools: SchoolImproved[]
  topQualitySchools: SchoolQuality[]
  topValueAddedSchools: SchoolValueAdded[]
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string | null
  student_id_number?: string | null
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
  student_id_number?: string | null
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
  student_id_number?: string | null
  password?: string
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

export interface UnifiedImportItem {
  student_id_number?: string
  username?: string
  email?: string
  full_name?: string
  password?: string
  role?: string
  is_active?: boolean
  region_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
  seat_no?: number
  role_in_class?: string
  cadre_title?: string
  is_primary_class?: boolean
  student_no?: string
}

export interface UnifiedImportResult {
  message: string
  created_users: User[]
  added_members: Array<{
    user_id: number
    username: string
    full_name?: string
    classroom_id: number
    classroom_name?: string
  }>
  errors: string[]
  success_count: number
  error_count: number
  created_user_count: number
  added_member_count: number
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

export interface SchoolType {
  name: string
  school_count: number
}

export interface SchoolTypeListResponse {
  school_types: SchoolType[]
}

export interface SchoolImportError {
  row: number
  field?: string | null
  message: string
}

export interface SchoolImportResponse {
  total: number
  success: number
  failed: number
  created_regions: number
  created_schools: number
  updated_schools: number
  skipped_schools: number
  errors: SchoolImportError[]
}

export interface ClassroomImportError {
  row: number
  field?: string | null
  message: string
}

export interface ClassroomImportResponse {
  total: number
  success: number
  failed: number
  created: number
  updated: number
  skipped: number
  errors: ClassroomImportError[]
}

export interface SchoolRelationCheck {
  school_id: number
  school_name: string
  has_relations: boolean
  relations: {
    classrooms: number
    teachers_students: number
  } | null
}

export interface BatchDeleteSchoolsError {
  school_id: number
  school_name: string
  error: string
}

export interface BatchDeleteSchoolsResponse {
  total_requested: number
  deleted_count: number
  failed_count: number
  errors: BatchDeleteSchoolsError[]
}

export interface CheckSchoolRelationsResponse {
  schools: SchoolRelationCheck[]
}

export interface Classroom {
  id: number
  name: string
  school_id: number
  grade_id: number
  code?: string | null
  enrollment_year?: number | null
  head_teacher_id?: number | null
  capacity?: number | null
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

// ==================== 课室管理 (物理教室) ====================

export interface Room {
  id: number
  name: string
  code?: string | null
  school_id: number
  building?: string | null
  floor?: number | null
  room_type: string
  capacity?: number | null
  equipment?: string[] | null
  assigned_classroom_id?: number | null
  is_active: boolean
  description?: string | null
  created_at: string
  updated_at: string
}

export interface RoomCreate {
  name: string
  code?: string | null
  school_id: number
  building?: string | null
  floor?: number | null
  room_type: string
  capacity?: number | null
  equipment?: string[] | null
  assigned_classroom_id?: number | null
  is_active?: boolean
  description?: string | null
}

export interface RoomUpdate {
  name?: string
  code?: string | null
  school_id?: number
  building?: string | null
  floor?: number | null
  room_type?: string
  capacity?: number | null
  equipment?: string[] | null
  assigned_classroom_id?: number | null
  is_active?: boolean
  description?: string | null
}

export interface RoomResponse {
  id: number
  name: string
  code?: string | null
  school_id: number
  building?: string | null
  floor?: number | null
  room_type: string
  capacity?: number | null
  equipment?: string[] | null
  assigned_classroom_id?: number | null
  is_active: boolean
  description?: string | null
  created_at: string
  updated_at: string
}

export interface RoomListResponse {
  rooms: RoomResponse[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface RoomImportError {
  row: number
  field?: string | null
  message: string
}

export interface RoomImportResponse {
  total: number
  success: number
  failed: number
  created: number
  updated: number
  skipped: number
  errors: RoomImportError[]
}

export const adminService = {
  /**
   * 获取数据看板概览
   */
  async getDashboardOverview(): Promise<DashboardOverview> {
    return await api.get('/admin/dashboard/overview')
  },

  /**
   * 获取考试统计数据 (Mock)
   */
  async getExamStats(): Promise<ExamStats> {
    // 模拟API延迟
    await new Promise((resolve) => setTimeout(resolve, 300))
    return {
      totalExams: 12,
      totalStudents: 5420,
      completedRate: 85,
      pendingTasks: 3,
    }
  },

  /**
   * 获取增值评价统计数据 (Mock)
   */
  async getValueAddedStats(): Promise<ValueAddedStats> {
    await new Promise((resolve) => setTimeout(resolve, 300))
    return {
      totalReports: 24,
      avgProgress: 8.5,
      improvedSchools: 18,
      excellentClasses: 45,
    }
  },

  /**
   * 获取优秀学生展示数据 (Mock)
   */
  async getStudentAchievements(): Promise<StudentAchievements> {
    await new Promise((resolve) => setTimeout(resolve, 400))
    return {
      topImprovers: [
        { id: 1, name: '张小明', school: '开平市第一中学', class: '高一(3)班', improvement: 15.2 },
        { id: 2, name: '李华', school: '开平市开侨中学', class: '高二(1)班', improvement: 12.8 },
        { id: 3, name: '王芳', school: '台山市华侨中学', class: '高三(2)班', improvement: 11.5 },
      ],
      topStudents: [
        { id: 1, name: '陈思思', school: '开平市第一中学', class: '高三(1)班', score: 698 },
        { id: 2, name: '刘伟', school: '开平市开侨中学', class: '高三(2)班', score: 685 },
        { id: 3, name: '杨洋', school: '恩平市第一中学', class: '高三(3)班', score: 672 },
      ],
      subjectToppers: [
        { subject: '语文', name: '陈思思', school: '开平市第一中学', score: 138 },
        { subject: '数学', name: '刘伟', school: '开平市开侨中学', score: 145 },
        { subject: '英语', name: '杨洋', school: '恩平市第一中学', score: 142 },
        { subject: '物理', name: '赵强', school: '台山市华侨中学', score: 95 },
        { subject: '化学', name: '孙丽', school: '开平市第一中学', score: 98 },
      ],
    }
  },

  /**
   * 获取学校亮点数据 (Mock)
   */
  async getSchoolHighlights(): Promise<SchoolHighlights> {
    await new Promise((resolve) => setTimeout(resolve, 400))
    return {
      topImprovedSchools: [
        { id: 1, name: '开平市第一中学', improvement: 12.5 },
        { id: 2, name: '台山市华侨中学', improvement: 10.8 },
        { id: 3, name: '恩平市第一中学', improvement: 9.6 },
      ],
      topQualitySchools: [
        { id: 1, name: '开平市开侨中学', avgScore: 586 },
        { id: 2, name: '开平市第一中学', avgScore: 578 },
        { id: 3, name: '台山市华侨中学', avgScore: 572 },
      ],
      topValueAddedSchools: [
        { id: 1, name: '开平市第一中学', valueIndex: 1.25 },
        { id: 2, name: '台山市华侨中学', valueIndex: 1.18 },
        { id: 3, name: '恩平市第一中学', valueIndex: 1.12 },
      ],
    }
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
  async getUsers(
    params: {
      page?: number
      size?: number
      role?: string
      search?: string
      region_id?: number
      school_id?: number
      grade_id?: number
      classroom_id?: number
    } = {}
  ): Promise<UserListResponse> {
    // 集合根路径须带尾部 /，否则 FastAPI 可能 307 到 /admin/users/，重定向后浏览器不携带 Authorization → 401 Not authenticated
    return await api.get('/admin/users/', { params })
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
    return await api.post('/admin/users/', userData)
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
   * 批量删除用户
   */
  async batchDeleteUsers(userIds: number[]): Promise<{
    message: string
    deleted_count: number
    total_requested: number
    failed_count?: number
    failed_users?: Array<{ id: number; username: string; error: string }>
  }> {
    return await api.post('/admin/users/batch-delete', userIds)
  },

  /**
   * 预览按条件批量删除的用户
   */
  async previewBatchDeleteByFilter(filters: {
    role: string
    region_id?: number
    school_id?: number
    grade_id?: number
    classroom_id?: number
    confirm?: boolean
  }): Promise<{
    total_count: number
    preview_users: Array<{
      id: number
      username: string
      full_name?: string
      email: string
      school_name?: string
      grade_name?: string
      classroom_name?: string
    }>
    showing: number
    message: string
  }> {
    return await api.post('/admin/users/batch-delete-by-filter/preview', filters)
  },

  /**
   * 按条件批量删除用户（支持大规模删除）
   */
  async batchDeleteByFilter(filters: {
    role: string
    region_id?: number
    school_id?: number
    grade_id?: number
    classroom_id?: number
    confirm: boolean
  }): Promise<{
    message: string
    deleted_count: number
    exam_mappings_deleted: number
    exam_room_students_deleted: number
  }> {
    return await api.post('/admin/users/batch-delete-by-filter', filters)
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
  async resetUserPassword(
    userId: number
  ): Promise<{ message: string; new_password?: string; note?: string; password_length?: number }> {
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

  /**
   * 统一导入（支持创建用户和添加到班级）
   */
  async unifiedImport(items: UnifiedImportItem[]): Promise<UnifiedImportResult> {
    return await api.post('/admin/users/unified-import', { items })
  },

  /**
   * 下载统一导入模板
   */
  async getUnifiedImportTemplate(): Promise<{ template: string; filename: string; note: string }> {
    return await api.get('/admin/users/export/unified-template')
  },

  // ==================== 组织架构管理 ====================

  /**
   * 获取区域列表
   */
  async getRegions(
    params: {
      page?: number
      size?: number
      level?: number
      parent_id?: number
      search?: string
    } = {}
  ): Promise<RegionListResponse> {
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
  async getSchools(
    params: {
      page?: number
      size?: number
      region_id?: number
      school_type?: string
      search?: string
    } = {}
  ): Promise<SchoolListResponse> {
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
   * 获取所有学校类型（学段）
   * 从数据库动态获取所有不重复的 school_type 值
   */
  async getSchoolTypes(): Promise<SchoolTypeListResponse> {
    return await api.get('/admin/organization/school-types')
  },

  /**
   * 批量导入学校
   */
  async importSchools(file: File, autoCreateRegion: boolean = true): Promise<SchoolImportResponse> {
    const formData = new FormData()
    formData.append('file', file)
    // 注意：不要手动设置Content-Type，api.ts中的拦截器会自动处理FormData
    return await api.post('/admin/organization/schools/import', formData, {
      params: { auto_create_region: autoCreateRegion },
    })
  },

  /**
   * 获取班级列表
   */
  async getClassrooms(
    params: {
      page?: number
      size?: number
      school_id?: number
      grade_id?: number
      region_id?: number
      school_type?: string
      is_active?: boolean
      search?: string
    } = {}
  ): Promise<ClassroomListResponse> {
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
  },

  /**
   * 批量导入班级
   */
  async importClassrooms(
    file: File,
    schoolId?: number,
    regionId?: number,
    updateExisting: boolean = false,
    enrollmentYear?: number,
    capacity?: number
  ): Promise<ClassroomImportResponse> {
    const formData = new FormData()
    formData.append('file', file)
    // 注意：不要手动设置Content-Type，api.ts中的拦截器会自动处理FormData
    const params: Record<string, any> = {
      update_existing: updateExisting,
    }
    if (schoolId) params.school_id = schoolId
    if (regionId) params.region_id = regionId
    if (enrollmentYear) params.enrollment_year = enrollmentYear
    if (capacity) params.capacity = capacity

    return await api.post('/admin/organization/classrooms/import', formData, {
      params,
    })
  },

  // ==================== 课室管理 (物理教室) ====================

  /**
   * 获取课室列表
   */
  async getRooms(
    params: {
      page?: number
      size?: number
      school_id?: number
      room_type?: string
      building?: string
      search?: string
    } = {}
  ): Promise<RoomListResponse> {
    return await api.get('/admin/organization/rooms', { params })
  },

  /**
   * 获取课室详情
   */
  async getRoom(roomId: number): Promise<RoomResponse> {
    return await api.get(`/admin/organization/rooms/${roomId}`)
  },

  /**
   * 创建课室
   */
  async createRoom(roomData: RoomCreate): Promise<RoomResponse> {
    return await api.post('/admin/organization/rooms', roomData)
  },

  /**
   * 更新课室
   */
  async updateRoom(roomId: number, roomData: RoomUpdate): Promise<RoomResponse> {
    return await api.put(`/admin/organization/rooms/${roomId}`, roomData)
  },

  /**
   * 删除课室
   */
  async deleteRoom(roomId: number): Promise<{ message: string }> {
    return await api.delete(`/admin/organization/rooms/${roomId}`)
  },

  /**
   * 批量导入课室
   */
  async importRooms(file: File, updateExisting: boolean = false): Promise<RoomImportResponse> {
    const formData = new FormData()
    formData.append('file', file)
    return await api.post('/admin/organization/rooms/import', formData, {
      params: { update_existing: updateExisting },
    })
  },

  /**
   * 检查学校关联数据
   */
  async checkSchoolRelations(schoolIds: number[]): Promise<CheckSchoolRelationsResponse> {
    return await api.post('/admin/organization/schools/check-relations', { school_ids: schoolIds })
  },

  /**
   * 批量删除学校
   */
  async batchDeleteSchools(
    schoolIds: number[],
    cascadeDelete: boolean = false
  ): Promise<BatchDeleteSchoolsResponse> {
    return await api.post('/admin/organization/schools/batch-delete', {
      school_ids: schoolIds,
      cascade_delete: cascadeDelete,
    })
  },
}

export default adminService
