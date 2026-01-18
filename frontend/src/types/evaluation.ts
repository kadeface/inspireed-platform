/**
 * 增值评价系统类型定义
 */

// ============================================================================
// 枚举类型
// ============================================================================

/** 用户角色 */
export enum UserRole {
  ADMIN = 'admin',
  DISTRICT_ADMIN = 'district_admin',
  SCHOOL_ADMIN = 'school_admin',
  RESEARCHER = 'researcher',
  TEACHER = 'teacher',
  STUDENT = 'student',
}

/** 学生类型 */
export enum StudentType {
  NONE = 'none',
  ARTS = 'arts',
  SCIENCE = 'science',
}

/** 考试类型 */
export enum ExamType {
  MIDTERM = 'midterm',
  FINAL = 'final',
  MONTHLY = 'monthly',
  MOCK = 'mock',
  UNIFIED = 'unified',
  OTHER = 'other',
}

/** 考试状态 */
export enum ExamStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

/** 导入任务状态 */
export enum ImportStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/** 评价范围类型 */
export enum ScopeType {
  REGION = 'region',
  SCHOOL = 'school',
  CLASSROOM = 'classroom',
}

// ============================================================================
// 学期管理
// ============================================================================

export interface Semester {
  id: number;
  year: string; // 学年，格式：2023-2024
  semester_type: string; // 'up' 表示上学期, 'down' 表示下学期
  name: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  region_id?: number;
  created_at: string;
  updated_at: string;
}

export interface SemesterCreate {
  year: string; // 学年，格式：2023-2024
  semester_type: string; // 'up' 表示上学期, 'down' 表示下学期
  name: string;
  start_date: string; // ISO 格式日期时间字符串，如 "2025-01-01T00:00:00"
  end_date: string; // ISO 格式日期时间字符串，如 "2025-06-30T00:00:00"
  is_current?: boolean;
  region_id?: number;
}

export interface SemesterUpdate {
  year?: string; // 学年，格式：2023-2024
  semester_type?: string; // 'up' 表示上学期, 'down' 表示下学期
  name?: string;
  start_date?: string; // ISO 格式日期时间字符串
  end_date?: string; // ISO 格式日期时间字符串
  is_current?: boolean;
  region_id?: number;
}

// ============================================================================
// 考试管理
// ============================================================================

export interface Exam {
  id: number;
  name: string;
  exam_type: ExamType;
  status: ExamStatus;
  semester_id: number;
  grade_id?: number;
  region_id?: number;
  school_id?: number;
  exam_date: string;
  description?: string;
  statistics?: Record<string, any>;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface ExamCreate {
  name: string;
  exam_type: ExamType;
  semester_id: number;
  exam_date: string;
  grade_id?: number;
  region_id?: number;
  school_id?: number;
  description?: string;
}

export interface ExamUpdate {
  name?: string;
  exam_type?: ExamType;
  status?: ExamStatus;
  exam_date?: string;
  semester_id?: number;
  grade_id?: number;
  region_id?: number;
  school_id?: number;
  description?: string;
}

export interface ExamSubject {
  id: number;
  exam_id: number;
  subject_id: number;
  full_score: number;
  pass_line: number;
  excellent_line: number;
  good_line: number;
  subject_name?: string; // 科目名称（从Subject表获取）
}

// ============================================================================
// 成绩管理
// ============================================================================

export interface Score {
  id: number;
  exam_id: number;
  subject_id: number;
  student_id: number;
  raw_score: number;
  standard_score?: number;
  percentile?: number;
  grade_level?: string;
  is_absent: boolean;
  is_cheated: boolean;
}

export interface ExamScoreStatistics {
  exam_id: number;
  subject_id?: number;
  total_count: number;
  absent_count: number;
  cheated_count: number;
  valid_count: number;
  average_score: number;
  max_score: number;
  min_score: number;
  excellent_rate: number;
  good_rate: number;
  pass_rate: number;
  fail_rate: number;
  score_distribution: {
    '90-100': number;
    '80-89': number;
    '70-79': number;
    '60-69': number;
    '0-59': number;
  };
}

// ============================================================================
// 日常表现成绩
// ============================================================================

export interface DailyPerformanceScore {
  id: number;
  student_id: number;
  classroom_id: number;
  semester_id: number;
  period_name: string;
  start_date: string;
  end_date: string;
  positive_behavior_count: number;
  positive_behavior_points: number;
  discipline_count: number;
  discipline_points: number;
  attendance_present: number;
  attendance_late: number;
  attendance_leave: number;
  attendance_absent: number;
  duty_completed_count: number;
  final_score: number;
  grade_level: string;
  detail_scores: Record<string, any>;
  recorded_by_user_id: number;
  recorded_at: string;
  created_at: string;
  updated_at: string;
}

export interface DailyPerformanceScoreCreate {
  student_id: number;
  classroom_id?: number;
  semester_id?: number;
  period_name: string;
  start_date: string;
  end_date: string;
  weights?: {
    attendance?: number;
    behavior?: number;
    discipline?: number;
    duty?: number;
  };
}

// ============================================================================
// 高中总分评价
// ============================================================================

export interface ExamTotalScore {
  id: number;
  exam_id: number;
  student_id: number;
  student_type: StudentType;
  total_score: number;
  c9_line: number;
  special_control_line: number;
  undergraduate_line: number;
  junior_college_line: number;
  reached_c9: boolean;
  reached_special_control: boolean;
  reached_undergraduate: boolean;
  reached_junior_college: boolean;
  recorded_at: string;
}

export interface ExamTotalScoreCreate {
  exam_id: number;
  student_id: number;
  total_score: number;
  student_type: StudentType;
  score_lines?: {
    c9_line?: number;
    special_control_line?: number;
    undergraduate_line?: number;
    junior_college_line?: number;
  };
}

// ============================================================================
// 导入任务
// ============================================================================

export interface ImportTask {
  id: number;
  task_name: string;
  task_type: string;
  exam_id?: number;
  file_url: string;
  file_name: string;
  file_size: number;
  status: ImportStatus;
  progress: number;
  total_rows?: number;
  processed_rows?: number;
  failed_rows?: number;
  error_message?: string;
  error_details?: Record<string, any>;
  created_by: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ImportTaskCreate {
  task_name: string;
  exam_id: number;
  file_url: string;
  file_name: string;
  file_size: number;
}

// ============================================================================
// 增值评价
// ============================================================================

export interface ValueAddedEvaluation {
  id: number;
  name: string;
  scope_type: ScopeType;
  scope_id?: number;
  baseline_exam_id: number;
  endline_exam_id: number;
  subject_id?: number;
  region_id?: number;
  school_id?: number;
  classroom_id?: number;
  baseline_value?: number;
  endline_value?: number;
  value_added?: number;
  value_added_rate?: number;
  is_significant: boolean;
  p_value?: number;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface ValueAddedEvaluationCreate {
  name: string;
  scope_type: ScopeType;
  scope_id: number;
  baseline_exam_id: number;
  endline_exam_id: number;
  subject_id?: number;
  region_id?: number;
  school_id?: number;
  classroom_id?: number;
  metrics?: string[];
  score_lines?: Record<string, number>;
}

export interface ValueAddedEvaluationSummary {
  evaluation_id: number;
  name: string;
  scope_type: string;
  scope_id?: number;
  baseline_exam: {
    id: number;
    name: string;
    date: string;
  };
  endline_exam: {
    id: number;
    name: string;
    date: string;
  };
  subject: {
    id: number;
    name: string;
  };
  metrics: Array<{
    metric_id: number;
    metric_name: string;
    metric_code: string;
    baseline_rate: number;
    endline_rate: number;
    value_added: number;
    improvement: string;
  }>;
  created_at?: string;
}

// ============================================================================
// 通用类型
// ============================================================================

export interface PaginationParams {
  page?: number;
  page_size?: number;
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
}

// ============================================================================
// 考场安排
// ============================================================================

export interface ExamRoom {
  id: number;
  exam_id: number;
  name: string;
  school_id: number;
  room_id?: number;
  capacity: number;
  seat_count: number;
  exam_number_start?: string;
  exam_number_end?: string;
  arrangement_type: 'by_class' | 'mixed';
  seat_pattern: 'sequential' | 's_shape';
  students: ExamRoomStudent[];
  proctors: ExamProctor[];
  created_at: string;
  updated_at: string;
}

export interface ExamRoomStudent {
  id: number;
  room_id: number;
  student_id: number;
  exam_number: string;
  seat_number: number;
  table_number?: number;
  student_id_number?: string;
  student_name?: string;
  school_id?: number;
  classroom_id?: number;
  created_at: string;
}

export interface ExamProctor {
  id: number;
  room_id: number;
  user_id: number;
  proctor_type: 'primary' | 'assistant';
  responsibilities?: string[];
  created_at: string;
}

export interface AutoAssignRoomsRequest {
  capacity_per_room: number;
  arrangement_type: 'by_class' | 'mixed';
  seat_pattern: 'sequential' | 's_shape';
  use_existing_rooms: boolean;
}

export interface AutoAssignProctorsRequest {
  auto_assign: boolean;
  avoid_own_class: boolean;
  same_school_only: boolean;
}

export interface ProctorAssignmentResponse {
  message: string;
  total_proctors: number;
  rooms_assigned: number;
}

