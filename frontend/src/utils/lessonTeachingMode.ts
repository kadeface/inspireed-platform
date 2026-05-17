/** 教师端授课（预览）模式、课堂会话与 URL / sessionStorage 同步 */

import { readGuestAccessCode } from '@/utils/guestSession'

export const LESSON_PREVIEW_QUERY = 'mode'
export const GUEST_ACCESS_CODE_QUERY = 'code'
export const LESSON_PREVIEW_QUERY_VALUE = 'preview'
export const LESSON_SESSION_QUERY = 'sessionId'

export interface TeachingContextSnapshot {
  preview: boolean
  sessionId?: number | null
}

export function teachingPreviewStorageKey(lessonId: string | number): string {
  return `inspireed_lesson_${lessonId}_teaching_preview`
}

export function teachingContextStorageKey(lessonId: string | number): string {
  return `inspireed_lesson_${lessonId}_teaching_context`
}

export function isTeacherLessonPath(path: string): boolean {
  return /\/(teacher|researcher)\/lesson\//.test(path)
}

export function parseSessionIdParam(
  raw: string | string[] | undefined | null
): number | null {
  const s = typeof raw === 'string' ? raw : Array.isArray(raw) ? raw[0] : null
  if (!s?.trim()) return null
  const n = parseInt(s, 10)
  return Number.isFinite(n) && n > 0 ? n : null
}

export function saveTeachingContext(
  lessonId: string | number,
  ctx: TeachingContextSnapshot
) {
  try {
    if (!ctx.preview) {
      sessionStorage.removeItem(teachingPreviewStorageKey(lessonId))
      sessionStorage.removeItem(teachingContextStorageKey(lessonId))
      return
    }
    sessionStorage.setItem(teachingPreviewStorageKey(lessonId), '1')
    sessionStorage.setItem(teachingContextStorageKey(lessonId), JSON.stringify(ctx))
  } catch {
    /* ignored */
  }
}

export function readTeachingContext(lessonId: string | number): TeachingContextSnapshot | null {
  try {
    const raw = sessionStorage.getItem(teachingContextStorageKey(lessonId))
    if (!raw) return null
    const parsed = JSON.parse(raw) as TeachingContextSnapshot
    if (parsed && typeof parsed === 'object') return parsed
  } catch {
    sessionStorage.removeItem(teachingContextStorageKey(lessonId))
  }
  return null
}

export function readPreviewModeFromRoute(
  query: Record<string, string | string[] | undefined | null>
): boolean {
  const mode = query[LESSON_PREVIEW_QUERY]
  if (mode === LESSON_PREVIEW_QUERY_VALUE) return true
  if (Array.isArray(mode) && mode[0] === LESSON_PREVIEW_QUERY_VALUE) return true
  return false
}

export function buildLessonReturnPath(
  path: string,
  query: Record<string, string | string[] | undefined | null>,
  lessonId: string | number
): string {
  const q: Record<string, string> = {}
  for (const [key, val] of Object.entries(query)) {
    if (typeof val === 'string' && val) q[key] = val
    else if (Array.isArray(val) && val[0]) q[key] = val[0]
  }

  if (isTeacherLessonPath(path)) {
    const ctx = readTeachingContext(lessonId)

    if (q[LESSON_PREVIEW_QUERY] !== LESSON_PREVIEW_QUERY_VALUE) {
      try {
        if (
          sessionStorage.getItem(teachingPreviewStorageKey(lessonId)) === '1' ||
          ctx?.preview
        ) {
          q[LESSON_PREVIEW_QUERY] = LESSON_PREVIEW_QUERY_VALUE
        }
      } catch {
        /* ignored */
      }
    }

    const sessionFromQuery = parseSessionIdParam(q[LESSON_SESSION_QUERY])
    const sessionFromCtx = ctx?.sessionId
    const sessionId = sessionFromQuery ?? sessionFromCtx
    if (sessionId != null && !q[LESSON_SESSION_QUERY]) {
      q[LESSON_SESSION_QUERY] = String(sessionId)
    }
  }

  if (path === '/guest' || path.startsWith('/guest/')) {
    const fromQuery = q[GUEST_ACCESS_CODE_QUERY]
    const fromStorage = readGuestAccessCode()
    const code = (fromQuery || fromStorage || '').trim().toUpperCase()
    if (code.length >= 6) {
      q[GUEST_ACCESS_CODE_QUERY] = code
    }
  }

  const search = new URLSearchParams(q).toString()
  return search ? `${path}?${search}` : path
}
