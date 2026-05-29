/**
 * MathLab 课堂竞赛类型
 *
 * taskId 为 curriculum.js 中的字符串 id（无固定枚举）；专题课示例见 MATHLAB_CONTEST_TOPIC_TASK_EXAMPLES。
 */

/** 函数图像 / 微积分专题竞赛冒烟用 taskId */
export const MATHLAB_CONTEST_TOPIC_TASK_EXAMPLES = ['fg_l2_1', 'calc_l2_3'] as const

export type MathlabContestTopicTaskId = (typeof MATHLAB_CONTEST_TOPIC_TASK_EXAMPLES)[number]

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
