/**
 * 课堂会话类型定义
 */

export type ClassSessionStatus = 'pending' | 'active' | 'paused' | 'ended'

export interface ClassSession {
  id: number
  lessonId: number
  classroomId: number
  teacherId: number
  status: ClassSessionStatus
  scheduledStart?: string
  actualStart?: string
  endedAt?: string
  durationMinutes?: number
  currentCellId?: number
  currentActivityId?: number
  settings?: Record<string, any>
  totalStudents: number
  activeStudents: number
  createdAt: string
  updatedAt: string
  
  // 可选字段（从详情API返回）
  lessonTitle?: string
  classroomName?: string
  teacherName?: string
}

export interface ClassSessionCreate {
  lessonId: number
  classroomId: number
  scheduledStart?: string
  settings?: Record<string, any>
}

export interface ClassSessionUpdate {
  status?: ClassSessionStatus
  currentCellId?: number
  currentActivityId?: number
  settings?: Record<string, any>
}

export interface StudentParticipation {
  id: number
  sessionId: number
  studentId: number
  joinedAt: string
  lastActiveAt: string
  leftAt?: string
  isActive: boolean
  currentCellId?: number
  completedCells?: number[]
  progressPercentage: number
  
  // 可选字段
  studentName?: string
  studentEmail?: string
}

export interface NavigateToCellRequest {
  cellId?: number  // Cell的数字ID
  cellOrder?: number  // Cell的order（作为备选方案，用于UUID的情况）
  action?: 'toggle' | 'add' | 'remove'  // 操作类型：toggle（切换，默认）/ add（添加）/ remove（移除）
  multiSelect?: boolean  // 是否多选模式
  
  // 🆕 新增：直接传递 order 数组（推荐方式）
  displayCellOrders?: number[]
}

export interface StartActivityRequest {
  cellId: number
}

export interface SessionStatistics {
  totalStudents: number
  activeStudents: number
  completedStudents: number
  averageProgress: number
  studentsByProgress: {
    '0-25%': number
    '25-50%': number
    '50-75%': number
    '75-100%': number
    '100%': number
  }
}

export interface ClassroomEvent {
  type: 'session_started' | 'session_ended' | 'cell_changed' | 
        'activity_started' | 'activity_ended' | 'student_joined' | 
        'student_left' | 'student_progress' | 'statistics_updated'
  sessionId: number
  data: Record<string, any>
  timestamp: string
}

