import { ref, readonly } from 'vue'
import {
  broadcastLessonReturn,
  buildLessonReturnMessage,
} from '@/utils/externalBrowserReturn'

const STORAGE_KEY = 'inspireed_external_browser'

export interface ExternalBrowserSession {
  url: string
  title: string
  windowName: string
  lessonId: string | number
  cellId: string | number
  returnUrl?: string
  openedAt: number
}

const activeSession = ref<ExternalBrowserSession | null>(null)

export function buildWindowName(lessonId: string | number, cellId: string | number): string {
  return `inspireed_ext_${lessonId}_${cellId}`
}

export function buildExternalBrowserPageUrl(options: {
  url: string
  lessonId: string | number
  cellId: string | number
  title?: string
  returnUrl?: string
}): string {
  const params = new URLSearchParams()
  params.set('url', options.url)
  params.set('lessonId', String(options.lessonId))
  params.set('cellId', String(options.cellId))
  if (options.title?.trim()) params.set('title', options.title.trim())
  if (options.returnUrl?.trim()) params.set('returnUrl', options.returnUrl.trim())
  const base = typeof window !== 'undefined' ? window.location.origin : ''
  return `${base}/external-browser?${params.toString()}`
}

function persist(session: ExternalBrowserSession | null) {
  try {
    if (session) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session))
    } else {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    /* private mode / quota */
  }
}

function restoreFromStorage() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw) as ExternalBrowserSession
    if (parsed?.url && parsed?.windowName) {
      activeSession.value = parsed
    }
  } catch {
    sessionStorage.removeItem(STORAGE_KEY)
  }
}

restoreFromStorage()

export type OpenExternalOptions = {
  lessonId: string | number
  cellId: string | number
  title?: string
  /** 授课页完整路径，用于外部窗口「继续听课」 */
  returnUrl?: string
}

export type OpenExternalResult =
  | { ok: true }
  | { ok: false; reason: 'blocked' | 'invalid_url' }

function defaultLessonReturnUrl(lessonId: string | number): string {
  return `/student/lesson/${lessonId}`
}

function buildLessonWindowName(lessonId: string | number): string {
  return `inspireed_lesson_${lessonId}`
}

function notifyLessonWindow(
  target: Window,
  cellId: string | number | undefined,
  origin: string
) {
  try {
    target.postMessage(buildLessonReturnMessage(cellId), origin)
  } catch {
    /* ignored */
  }
}

export function useExternalBrowser() {
  function openExternal(url: string, options: OpenExternalOptions): OpenExternalResult {
    if (!url?.trim()) return { ok: false, reason: 'invalid_url' }

    const windowName = buildWindowName(options.lessonId, options.cellId)
    const returnUrl = options.returnUrl?.trim() || defaultLessonReturnUrl(options.lessonId)

    try {
      window.name = buildLessonWindowName(options.lessonId)
    } catch {
      /* ignored */
    }

    const wrapperUrl = buildExternalBrowserPageUrl({
      url,
      lessonId: options.lessonId,
      cellId: options.cellId,
      title: options.title,
      returnUrl,
    })

    const win = window.open(wrapperUrl, windowName)

    if (!win) {
      return { ok: false, reason: 'blocked' }
    }

    const session: ExternalBrowserSession = {
      url,
      title: options.title?.trim() || '外部网页',
      windowName,
      lessonId: options.lessonId,
      cellId: options.cellId,
      returnUrl,
      openedAt: Date.now(),
    }

    activeSession.value = session
    persist(session)
    return { ok: true }
  }

  function focusExternal(): boolean {
    const session = activeSession.value
    if (!session) return false

    const wrapperUrl = buildExternalBrowserPageUrl({
      url: session.url,
      lessonId: session.lessonId,
      cellId: session.cellId,
      title: session.title,
      returnUrl: session.returnUrl,
    })

    const win = window.open(wrapperUrl, session.windowName)
    if (!win) return false

    try {
      win.focus()
    } catch {
      /* ignored */
    }
    return true
  }

  function focusLessonTab(opts?: {
    lessonId?: string | number | string[] | null
    cellId?: string | number | string[] | null
    returnUrl?: string
  }): boolean {
    const origin = window.location.origin
    const session = activeSession.value

    const lessonIdRaw = opts?.lessonId ?? session?.lessonId
    const lessonId = Array.isArray(lessonIdRaw) ? lessonIdRaw[0] : lessonIdRaw

    const cellIdRaw = opts?.cellId ?? session?.cellId
    const cellId = Array.isArray(cellIdRaw) ? cellIdRaw[0] : cellIdRaw

    const returnPath =
      opts?.returnUrl?.trim() ||
      session?.returnUrl?.trim() ||
      (lessonId != null && lessonId !== ''
        ? defaultLessonReturnUrl(lessonId)
        : null)

    if (!returnPath || lessonId == null || lessonId === '') return false

    const absoluteUrl = new URL(returnPath, origin).href
    const lessonWindowName = buildLessonWindowName(lessonId)

    broadcastLessonReturn(cellId)

    if (window.opener && !window.opener.closed) {
      notifyLessonWindow(window.opener, cellId, origin)
    }

    let lessonWin: Window | null = window.open(absoluteUrl, lessonWindowName)

    if (!lessonWin) {
      lessonWin = window.open('', lessonWindowName)
      if (lessonWin) {
        try {
          lessonWin.location.href = absoluteUrl
        } catch {
          lessonWin = null
        }
      }
    }

    if (!lessonWin) return false

    notifyLessonWindow(lessonWin, cellId, origin)

    try {
      lessonWin.focus()
    } catch {
      /* ignored */
    }

    return true
  }

  function dismissDock() {
    activeSession.value = null
    persist(null)
  }

  function scrollToLessonCell() {
    const session = activeSession.value
    if (!session) return

    const el = document.querySelector(`[data-cell-id="${session.cellId}"]`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  return {
    activeSession: readonly(activeSession),
    openExternal,
    focusExternal,
    focusLessonTab,
    dismissDock,
    scrollToLessonCell,
  }
}
