/**
 * 班级教学助手相关类型定义
 */

// ==================== 基础类型 ====================

export enum RoleInClass {
  HEAD_TEACHER_PRIMARY = 'head_teacher_primary',
  HEAD_TEACHER_DEPUTY = 'head_teacher_deputy',
  SUBJECT_TEACHER = 'subject_teacher',
  CADRE = 'cadre',
  STUDENT = 'student',
}

export enum AttendanceStatus {
  PRESENT = 'present',
  LATE = 'late',
  LEAVE = 'leave',
  ABSENT = 'absent',
}

export enum PositiveBehaviorType {
  ACTIVE_RESPONSE = 'active_response',
  CORRECT_ANSWER = 'correct_answer',
  HELP_CLASSMATE = 'help_classmate',
  EXCELLENT_HOMEWORK = 'excellent_homework',
  PROACTIVE_THINKING = 'proactive_thinking',
  COLLABORATIVE_WORK = 'collaborative_work',
  OTHER = 'other',
}

export enum DisciplineEventType {
  // 课堂行为类
  TALKING = 'talking',
  WALKING = 'walking',
  NOT_PARTICIPATING = 'not_participating',
  SLEEPING = 'sleeping',
  DISTRACTED = 'distracted',
  // 课堂秩序类
  INTERRUPTING = 'interrupting',
  DISTURBING_OTHERS = 'disturbing_others',
  NOT_FOLLOWING_INSTRUCTIONS = 'not_following_instructions',
  // 作业与学习准备类
  MISSING_MATERIALS = 'missing_materials',
  HOMEWORK_INCOMPLETE = 'homework_incomplete',
  HOMEWORK_NOT_AS_REQUIRED = 'homework_not_as_required',
  // 课间与公共区域行为
  HALLWAY_ROUGHHOUSING = 'hallway_roughhousing',
  RUNNING_IN_HALLWAY = 'running_in_hallway',
  LOUD_NOISE = 'loud_noise',
  // 其他
  OTHER = 'other',
}

export enum DutyRotationType {
  DAILY = 'daily',
  WEEKLY = 'weekly',
}

export enum DutyAssignmentStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
}

// ==================== 班级和成员 ====================

export interface ClassroomInfo {
  id: number
  name: string
  code?: string | null
  schoolId: number
  gradeId: number
  headTeacherId?: number | null
  deputyHeadTeacherId?: number | null
  roleInClass?: RoleInClass | null
}

export interface StudentInfo {
  id: number
  username: string
  fullName?: string | null
  studentNo?: string | null
  seatNo?: number | null
  cadreTitle?: string | null
}

export interface ClassroomMembership {
  id: number
  classroomId: number
  userId: number
  roleInClass: RoleInClass
  isActive: boolean
  isPrimaryClass: boolean
  studentNo?: string | null
  seatNo?: number | null
  cadreTitle?: string | null
  createdAt: string
  updatedAt: string
  // 用户信息（可选）
  userName?: string | null
  userFullName?: string | null
  userEmail?: string | null
  userUsername?: string | null
}

export interface ClassroomMembershipCreate {
  classroomId: number
  userId: number
  roleInClass: RoleInClass
  studentNo?: string | null
  seatNo?: number | null
  cadreTitle?: string | null
  isPrimaryClass?: boolean
}

export interface ClassroomMembershipUpdate {
  roleInClass?: RoleInClass
  isActive?: boolean
  isPrimaryClass?: boolean
  studentNo?: string | null
  seatNo?: number | null
  cadreTitle?: string | null
}

export interface ClassroomMemberBatchItem {
  // 用户匹配字段（至少提供一个）
  userId?: number | null
  studentIdNumber?: string | null  // 学籍号（唯一，推荐使用）
  fullName?: string | null
  email?: string | null
  username?: string | null
  studentNo?: string | null  // 班级内的学号
  // 班级成员信息
  roleInClass?: RoleInClass
  seatNo?: number | null
  cadreTitle?: string | null
  isPrimaryClass?: boolean
}

export interface ClassroomMemberBatchImportRequest {
  members: ClassroomMemberBatchItem[]
}

export interface ClassroomMemberBatchImportResponse {
  message: string
  successCount: number
  errorCount: number
  errors: string[]
  createdMembers: ClassroomMembership[]
}

// ==================== 考勤 ====================

export interface AttendanceSessionCreate {
  windowSeconds?: number
}

export interface AttendanceSession {
  id: number
  classroomId: number
  initiatedByUserId: number
  startedAt: string
  endedAt?: string | null
  windowSeconds: number
  createdAt: string
}

export interface AttendanceEntry {
  id: number
  sessionId: number
  studentId: number
  status: AttendanceStatus
  updatedByUserId: number
  updatedAt: string
}

export interface AttendanceSessionWithEntries extends AttendanceSession {
  entries: AttendanceEntry[]
}

export interface AttendanceEntryUpdate {
  status: AttendanceStatus
}

// ==================== 正面行为 ====================

export interface PositiveBehaviorTypeInfo {
  type: PositiveBehaviorType
  name: string
  points: number
  description?: string | null
}

export interface PositiveBehaviorCreate {
  studentId: number
  behaviorType: PositiveBehaviorType
  customBehaviorText?: string | null
  note?: string | null
}

export interface PositiveBehavior {
  id: number
  classroomId: number
  studentId: number
  behaviorType: PositiveBehaviorType
  customBehaviorText?: string | null
  points: number
  note?: string | null
  recordedByUserId: number
  recordedAt: string
}

export interface PositiveBehaviorLeaderboardEntry {
  studentId: number
  studentName: string
  totalPoints: number
  recordCount: number
}

// ==================== 纪律记录 ====================

export interface DisciplineEventTypeInfo {
  type: DisciplineEventType
  name: string
  category: string
  description?: string | null
}

export interface DisciplineRecordCreate {
  studentId: number
  eventType: DisciplineEventType
  customEventText?: string | null
  note?: string | null
}

export interface DisciplineRecord {
  id: number
  classroomId: number
  studentId: number
  eventType: DisciplineEventType
  customEventText?: string | null
  note?: string | null
  recordedByUserId: number
  recordedAt: string
}

// ==================== 值日 ====================

export interface DutyRuleCreate {
  rotationType: DutyRotationType
  startDate: string
  memberUserIds: number[]
  groupSize?: number
}

export interface DutyRule {
  id: number
  classroomId: number
  rotationType: DutyRotationType
  startDate: string
  memberUserIds: number[]
  groupSize: number
  createdAt: string
  updatedAt: string
}

export interface DutyGenerateRequest {
  days?: number
  weeks?: number
}

export interface DutyAssignment {
  id: number
  classroomId: number
  ruleId?: number | null
  dutyDate: string
  assigneeUserId: number
  status: DutyAssignmentStatus
  completedByUserId?: number | null
  completedAt?: string | null
}

export interface DutyAssignmentUpdate {
  status: DutyAssignmentStatus
}

// ==================== 班级设置 ====================

export interface ClassroomSettingsUpdate {
  show_positive_behaviors_publicly?: boolean
  show_discipline_publicly?: boolean
}

export interface ClassroomSettings {
  show_positive_behaviors_publicly: boolean
  show_discipline_publicly: boolean
}

// ==================== 统计 ====================

export interface AttendanceStats {
  totalSessions: number
  presentCount: number
  lateCount: number
  leaveCount: number
  absentCount: number
  attendanceRate: number
}

export interface PositiveBehaviorStats {
  totalPoints: number
  totalRecords: number
  pointsByType: Record<string, number>
}

export interface DisciplineStats {
  totalRecords: number
  recordsByType: Record<string, number>
}

export interface DutyStats {
  totalAssignments: number
  completedCount: number
  pendingCount: number
  completionRate: number
}

export interface ClassroomStats {
  classroomId: number
  periodStart: string
  periodEnd: string
  attendance?: AttendanceStats | null
  positiveBehaviors?: PositiveBehaviorStats | null
  discipline?: DisciplineStats | null
  duty?: DutyStats | null
}

export interface StudentStats {
  studentId: number
  periodStart: string
  periodEnd: string
  attendance?: AttendanceStats | null
  positiveBehaviors?: PositiveBehaviorStats | null
  discipline?: DisciplineStats | null
  duty?: DutyStats | null
}
