import api from './api'

export interface ReviewSession {
  activity_id: string
  name: string
  role: 'judge' | 'coordinator'
  scopes: Array<{ grade_band: string; subject: string }>
  expires_at?: string
}

export interface ReviewWork {
  work_id: string
  work_number: string
  title: string
  grade_band: string
  subject: string
  school_name?: string
  chapter_text?: string
  attachments: Array<{ name: string; format: string; url: string }>
  status?: string
  review_count?: number
  final_score?: number | null
}

export interface ReviewProgress {
  total_works: number
  scored_works: number
  unscored_works: number
}

export interface ScorePayload {
  score_total: number
  comment: string
}

// 管理端 - 活动相关
export interface ReviewActivity {
  activity_id: string
  name: string
  description?: string
  starts_at?: string
  ends_at?: string
  status?: string
  created_at?: string
}

export interface CreateActivityPayload {
  name: string
  description?: string
  starts_at?: string
  ends_at?: string
}

export interface ImportResult {
  works_upserted: number
  attachments_inserted: number
  warnings: string[]
}

export interface AssignmentRule {
  grade_band: string
  subject: string
  role: 'judge' | 'coordinator'
  name: string
  contact?: string
}

export interface AssignmentsPayload {
  rules: AssignmentRule[]
}

export interface AssignmentScope {
  grade_band: string
  subject: string
}

export interface AssignmentColumns {
  activity_id: string
  scope_count: number
  scopes: AssignmentScope[]
  columns: string[]
  example: Record<string, string>
}

export interface AccessLink {
  name: string
  role: 'judge' | 'coordinator'
  scope: string | AssignmentScope[]
  url: string
}

export interface GenerateLinksPayload {
  expires_at?: string
  regenerate?: boolean
}

export interface GenerateLinksResult {
  generated: number
  links: AccessLink[]
}

export interface UncoveredScope {
  grade_band: string
  subject: string
}

export interface SaveAssignmentsResult {
  saved: number
  uncovered_scopes?: UncoveredScope[]
  warnings?: string[]
}

function q(params: Record<string, string | number | undefined | null>): string {
  const usp = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    usp.set(key, String(value))
  })
  const s = usp.toString()
  return s ? `?${s}` : ''
}

export const reviewChannelApi = {
  // ========== 评委端 ==========
  getSession(token: string, activityId: string) {
    return api.get<ReviewSession>(
      `/review-channel/access/session${q({ token, activity_id: activityId })}`,
    )
  },

  listWorks(activityId: string, token: string, status?: 'scored' | 'unscored') {
    return api.get<{ items: ReviewWork[]; total: number }>(
      `/review-channel/activities/${activityId}/works${q({ token, status })}`,
    )
  },

  getWork(activityId: string, workId: string, token: string) {
    return api.get<ReviewWork>(
      `/review-channel/activities/${activityId}/works/${workId}${q({ token })}`,
    )
  },

  submitScore(activityId: string, workId: string, token: string, payload: ScorePayload) {
    return api.post<{ ok: boolean; submitted_at: string }>(
      `/review-channel/activities/${activityId}/works/${workId}/submit${q({ token })}`,
      payload,
    )
  },

  // ========== 教研员端 ==========
  getProgress(activityId: string, token: string) {
    return api.get<ReviewProgress>(
      `/review-channel/activities/${activityId}/progress${q({ token })}`,
    )
  },

  async downloadSummary(activityId: string, token: string): Promise<void> {
    const blob = await api.downloadFile(
      `/review-channel/activities/${activityId}/export/summary${q({ token, fmt: 'xlsx' })}`,
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `review-summary-${activityId}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },

  async downloadDetails(activityId: string, token: string): Promise<void> {
    const blob = await api.downloadFile(
      `/review-channel/activities/${activityId}/export/details${q({ token, fmt: 'xlsx' })}`,
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `review-details-${activityId}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },

  async downloadAccessLinks(activityId: string): Promise<void> {
    const blob = await api.downloadFile(
      `/review-channel/activities/${activityId}/access-links/export${q({ fmt: 'xlsx' })}`,
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `review-access-links-${activityId}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },

  // ========== 管理端 ==========
  // 活动管理
  createActivity(payload: CreateActivityPayload) {
    return api.post<ReviewActivity>('/review-channel/activities', payload)
  },

  // 作品导入
  async importWorks(activityId: string, file: File): Promise<ImportResult> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ImportResult>(
      `/review-channel/activities/${activityId}/works/import`,
      formData,
    )
  },

  // 分配配置
  getAssignments(activityId: string) {
    return api.get<{ rules: AssignmentRule[]; updated_at?: string }>(
      `/review-channel/activities/${activityId}/assignments`,
    )
  },

  saveAssignments(activityId: string, payload: AssignmentsPayload) {
    return api.put<SaveAssignmentsResult>(
      `/review-channel/activities/${activityId}/assignments`,
      payload,
    )
  },

  saveAssignmentsFromColumns(activityId: string, columnData: Record<string, string>) {
    return api.post<SaveAssignmentsResult>(
      `/review-channel/activities/${activityId}/assignments/from-columns`,
      columnData,
    )
  },

  getAssignmentColumns(activityId: string, maxJudgesPerScope = 3) {
    return api.get<AssignmentColumns>(
      `/review-channel/activities/${activityId}/assignment-columns${q({ max_judges_per_scope: maxJudgesPerScope })}`,
    )
  },

  async downloadAssignmentTemplate(activityId: string, maxJudgesPerScope = 3): Promise<void> {
    const blob = await api.downloadFile(
      `/review-channel/activities/${activityId}/assignments/template${q({ max_judges_per_scope: maxJudgesPerScope, fmt: 'xlsx' })}`,
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assignment-template-${activityId}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },

  async importAssignmentTemplate(activityId: string, file: File): Promise<SaveAssignmentsResult> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<SaveAssignmentsResult>(
      `/review-channel/activities/${activityId}/assignments/import-template`,
      formData,
    )
  },

  // 访问链接
  generateAccessLinks(activityId: string, payload: GenerateLinksPayload) {
    return api.post<GenerateLinksResult>(
      `/review-channel/activities/${activityId}/access-links/generate`,
      payload,
    )
  },

  // 重新计算汇总
  recomputeSummary(activityId: string) {
    return api.post<{ ok: boolean; progress: ReviewProgress }>(
      `/review-channel/activities/${activityId}/recompute`,
    )
  },
}
