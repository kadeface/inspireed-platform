/** 未结束课堂与学生端可见窗口。窗口与后端学生列表一致。 */

const MINUTE_MS = 60 * 1000
const HOUR_MS = 60 * MINUTE_MS

export const STUDENT_TEACHING_VISIBLE_MS = 40 * MINUTE_MS
export const STUDENT_PREPARING_VISIBLE_MS = 48 * HOUR_MS

const UNFINISHED_STATUSES = new Set(['preparing', 'pending', 'teaching', 'active'])

type SessionLike = {
  status?: string | null
  actual_start?: string | null
  actualStart?: string | null
  created_at?: string | null
  createdAt?: string | null
}

function statusOf(session: SessionLike | null | undefined): string {
  return String(session?.status || '').toLowerCase()
}

function timestamp(session: SessionLike, keys: Array<keyof SessionLike>): number | null {
  for (const key of keys) {
    const value = session[key]
    if (value == null || value === '') continue
    const time = new Date(String(value)).getTime()
    if (Number.isFinite(time)) return time
  }
  return null
}

export function isUnfinishedClassSession(session: SessionLike | null | undefined): boolean {
  return UNFINISHED_STATUSES.has(statusOf(session))
}

/** 学生首页已经不会列出这场课。 */
export function isHiddenFromStudents(
  session: SessionLike | null | undefined,
  now = Date.now(),
): boolean {
  const status = statusOf(session)
  if (!session) return false

  if (status === 'teaching' || status === 'active') {
    const start = timestamp(session, ['actual_start', 'actualStart', 'created_at', 'createdAt'])
    if (start == null) return false
    return now - start > STUDENT_TEACHING_VISIBLE_MS
  }

  if (status === 'preparing' || status === 'pending') {
    const created = timestamp(session, ['created_at', 'createdAt'])
    if (created == null) return false
    return now - created > STUDENT_PREPARING_VISIBLE_MS
  }

  return false
}

function detailOf(error: { response?: { data?: { detail?: unknown } }; message?: unknown }): unknown {
  return error?.response?.data?.detail
}

function conflictText(error: { response?: { data?: { detail?: unknown } }; message?: unknown }): string {
  const detail = detailOf(error)
  const message = typeof error?.message === 'string' ? error.message : ''
  if (typeof detail === 'string') return `${detail} ${message}`
  if (detail && typeof detail === 'object') {
    const record = detail as { message?: unknown }
    const detailMessage = typeof record.message === 'string' ? record.message : ''
    return `${detailMessage} ${JSON.stringify(detail)} ${message}`
  }
  return message
}

export function isActiveSessionConflict(error: {
  response?: { data?: { detail?: unknown } }
  message?: unknown
}): boolean {
  const detail = detailOf(error)
  if (
    detail &&
    typeof detail === 'object' &&
    (detail as { code?: unknown }).code === 'active_session_exists'
  ) {
    return true
  }
  const text = conflictText(error)
  return (
    text.includes('已有活跃的课堂会话') ||
    text.includes('已有活跃会话') ||
    text.includes('已有未结束的会话')
  )
}

export function readExistingSessionId(error: {
  response?: { data?: { detail?: unknown } }
  message?: unknown
}): number | null {
  const detail = detailOf(error)
  if (detail && typeof detail === 'object' && !Array.isArray(detail)) {
    const id = Number((detail as { existing_session_id?: unknown }).existing_session_id)
    if (Number.isFinite(id) && id > 0) return id
  }

  const text = conflictText(error)
  const match =
    text.match(/"existing_session_id"\s*:\s*(\d+)/) ||
    text.match(/[（(]ID\s*[：:]\s*(\d+)[）)]/i) ||
    text.match(/ID\s*[：:]\s*(\d+)/i)
  if (!match) return null
  const id = parseInt(match[1], 10)
  return Number.isFinite(id) && id > 0 ? id : null
}
