/**
 * MathLab 课堂竞赛 API
 */

import api from './api'
import type {
  MathlabContest,
  MathlabContestLeaderboard,
  MathlabContestStartRequest,
  MathlabContestSubmitRequest,
  MathlabContestSubmission,
} from '../types/mathlabContest'

function mapContest(raw: Record<string, unknown>): MathlabContest {
  return {
    id: Number(raw.id),
    sessionId: Number(raw.session_id ?? raw.sessionId),
    cellId: raw.cell_id != null ? Number(raw.cell_id) : raw.cellId != null ? Number(raw.cellId) : undefined,
    teacherId: Number(raw.teacher_id ?? raw.teacherId),
    taskId: String(raw.task_id ?? raw.taskId),
    status: String(raw.status).toLowerCase() as MathlabContest['status'],
    timeLimitSec: raw.time_limit_sec != null ? Number(raw.time_limit_sec) : raw.timeLimitSec != null ? Number(raw.timeLimitSec) : undefined,
    allowResubmit: Boolean(raw.allow_resubmit ?? raw.allowResubmit),
    passThreshold: Number(raw.pass_threshold ?? raw.passThreshold ?? 85),
    settings: (raw.settings as Record<string, unknown>) || {},
    startedAt: String(raw.started_at ?? raw.startedAt),
    endedAt: raw.ended_at ? String(raw.ended_at) : raw.endedAt ? String(raw.endedAt) : undefined,
    endsAt: raw.ends_at ? String(raw.ends_at) : raw.endsAt ? String(raw.endsAt) : undefined,
  }
}

function mapSubmission(raw: Record<string, unknown>): MathlabContestSubmission {
  return {
    id: Number(raw.id),
    contestId: Number(raw.contest_id ?? raw.contestId),
    studentId: Number(raw.student_id ?? raw.studentId),
    studentName: raw.student_name != null ? String(raw.student_name) : raw.studentName != null ? String(raw.studentName) : undefined,
    autoScore: Number(raw.auto_score ?? raw.autoScore),
    autoPassed: Boolean(raw.auto_passed ?? raw.autoPassed),
    finalScore: Number(raw.final_score ?? raw.finalScore),
    passed: Boolean(raw.passed),
    elapsedSec: raw.elapsed_sec != null ? Number(raw.elapsed_sec) : raw.elapsedSec != null ? Number(raw.elapsedSec) : undefined,
    payload: (raw.payload as Record<string, unknown>) || {},
    submittedAt: String(raw.submitted_at ?? raw.submittedAt),
    rank: raw.rank != null ? Number(raw.rank) : undefined,
  }
}

export const mathlabContestService = {
  async start(sessionId: number, body: MathlabContestStartRequest): Promise<MathlabContest> {
    const res = await api.post(
      `/classroom-sessions/sessions/${sessionId}/mathlab-contest/start`,
      {
        cell_id: body.cellId,
        task_id: body.taskId,
        time_limit_sec: body.timeLimitSec,
        allow_resubmit: body.allowResubmit ?? false,
        pass_threshold: body.passThreshold ?? 85,
        settings: body.settings,
      }
    )
    return mapContest(res as Record<string, unknown>)
  },

  async getActive(sessionId: number): Promise<MathlabContest | null> {
    const res = await api.get(
      `/classroom-sessions/sessions/${sessionId}/mathlab-contest/active`
    )
    if (!res) return null
    return mapContest(res as Record<string, unknown>)
  },

  async end(contestId: number): Promise<MathlabContest> {
    const res = await api.post(`/classroom-sessions/mathlab-contest/${contestId}/end`)
    return mapContest(res as Record<string, unknown>)
  },

  async updateTask(contestId: number, taskId: string): Promise<MathlabContest> {
    const res = await api.patch(`/classroom-sessions/mathlab-contest/${contestId}/task`, {
      task_id: taskId,
    })
    return mapContest(res as Record<string, unknown>)
  },

  async getLeaderboard(contestId: number): Promise<MathlabContestLeaderboard> {
    const res = await api.get(`/classroom-sessions/mathlab-contest/${contestId}/leaderboard`)
    const r = res as Record<string, unknown>
    return {
      contest: mapContest((r.contest as Record<string, unknown>) || r),
      submissions: ((r.submissions as Record<string, unknown>[]) || []).map(mapSubmission),
      submittedCount: Number(r.submitted_count ?? r.submittedCount ?? 0),
      totalStudents: Number(r.total_students ?? r.totalStudents ?? 0),
    }
  },

  async submit(contestId: number, body: MathlabContestSubmitRequest): Promise<MathlabContestSubmission> {
    const res = await api.post(`/classroom-sessions/mathlab-contest/${contestId}/submit`, {
      auto_score: body.autoScore,
      auto_passed: body.autoPassed,
      elapsed_sec: body.elapsedSec,
      payload: body.payload,
    })
    return mapSubmission(res as Record<string, unknown>)
  },

  async updateScore(
    submissionId: number,
    finalScore: number,
    passed?: boolean
  ): Promise<MathlabContestSubmission> {
    const res = await api.patch(
      `/classroom-sessions/mathlab-contest/submissions/${submissionId}/score`,
      { final_score: finalScore, passed }
    )
    return mapSubmission(res as Record<string, unknown>)
  },
}
