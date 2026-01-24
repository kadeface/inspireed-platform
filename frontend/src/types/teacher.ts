/**
 * 教师教学任务相关类型定义
 */

/**
 * 教学任务类型枚举
 */
export enum TeachingAssignmentType {
  HEAD_TEACHER = 'head_teacher',          // 班主任
  SUBJECT_TEACHER = 'subject_teacher',   // 学科教师
}

/**
 * 教师教学任务
 */
export interface TeacherTeachingAssignment {
  id: number
  teacher_id: number
  school_id: number
  grade_id: number
  classroom_id: number
  subject_id: number
  semester_id: number
  academic_year: string
  assignment_type: TeachingAssignmentType
  is_active: boolean
  created_at: string
  updated_at: string
  // 关联对象（可选）
  teacher?: {
    id: number
    full_name: string
    email: string
  }
  school?: {
    id: number
    name: string
    code: string
  }
  grade?: {
    id: number
    name: string
    level: number
  }
  classroom?: {
    id: number
    name: string
    code: string
  }
  subject?: {
    id: number
    name: string
    code: string
  }
  semester?: {
    id: number
    name: string
    year: string
    semester_type: string
  }
}

/**
 * 创建教学任务请求
 */
export interface TeacherTeachingAssignmentCreate {
  teacher_id: number
  school_id: number
  grade_id: number
  classroom_id: number
  subject_id: number
  semester_id: number
  academic_year: string
  assignment_type: TeachingAssignmentType
  is_active?: boolean
}

/**
 * 更新教学任务请求
 */
export interface TeacherTeachingAssignmentUpdate {
  teacher_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
  subject_id?: number
  semester_id?: number
  academic_year?: string
  assignment_type?: TeachingAssignmentType
  is_active?: boolean
}

/**
 * 教学任务列表响应
 */
export interface TeacherTeachingAssignmentListResponse {
  assignments: TeacherTeachingAssignment[]
  total: number
  page: number
  size: number
  total_pages: number
}

/**
 * 教学任务查询参数
 */
export interface TeacherTeachingAssignmentQueryParams {
  teacher_id?: number
  school_id?: number
  grade_id?: number
  classroom_id?: number
  subject_id?: number
  semester_id?: number
  region_id?: number
  is_active?: boolean
  page?: number
  size?: number
}

/**
 * 教学任务导入错误
 */
export interface TeacherAssignmentImportError {
  row: number
  field?: string | null
  message: string
}

/**
 * 新创建的教师信息
 */
export interface CreatedTeacherInfo {
  teacher_name: string
  username: string
  email: string
  password: string
  school_name: string
  school_code: string
  grade_name?: string | null
  classroom_code?: string | null
  classroom_name?: string | null
  row_number: number
}

export interface CreatedSemesterInfo {
  semester_name: string
  academic_year: string
  semester_number: number
  semester_type: string
  start_date?: string | null
  end_date?: string | null
  row_number: number
}

/**
 * 教学任务批量导入响应
 */
export interface TeacherAssignmentImportResponse {
  total: number
  success: number
  failed: number
  created: number
  updated: number
  skipped: number
  errors: TeacherAssignmentImportError[]
  created_teachers?: CreatedTeacherInfo[]
  created_semesters?: CreatedSemesterInfo[]
}
