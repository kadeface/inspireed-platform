/**
 * MathLab 课堂竞赛类型
 */

export type MathlabContestStatus = 'preparing' | 'running' | 'ended'

export interface MathlabContest {
  id: number
  sessionId: number
  cellId?: number
  teacherId: number
  taskId: string
  status: MathlabContestStatus
  timeLimitSec?: number
  allowResubmit: boolean
  passThreshold: number
  settings?: Record<string, unknown>
  startedAt: string
  endedAt?: string
  endsAt?: string
}

export interface MathlabContestSubmission {
  id: number
  contestId: number
  studentId: number
  studentName?: string
  autoScore: number
  autoPassed: boolean
  finalScore: number
  passed: boolean
  elapsedSec?: number
  payload?: Record<string, unknown>
  submittedAt: string
  rank?: number
}

export interface MathlabContestLeaderboard {
  contest: MathlabContest
  submissions: MathlabContestSubmission[]
  submittedCount: number
  totalStudents: number
}

export interface MathlabContestStartRequest {
  cellId: number
  taskId?: string
  timeLimitSec?: number
  allowResubmit?: boolean
  passThreshold?: number
  settings?: Record<string, unknown>
}

export interface MathlabContestSubmitRequest {
  autoScore: number
  autoPassed: boolean
  elapsedSec?: number
  payload: Record<string, unknown>
}
