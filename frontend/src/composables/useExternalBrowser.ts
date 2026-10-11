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

/** 同一节课的外链共用一个标签，避免每打开一个网页就多一个标签。 */
export function buildWindowName(lessonId: string | number, _cellId?: string | number): string {
  return `inspireed_ext_${lessonId}`
}

function isOpenableHttpUrl(url: string): boolean {
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
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
  /** 授课页完整路径，外部窗口切回时使用 */
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
    const target = url?.trim() ?? ''
    // 必须顶层打开。套进本站 iframe 后，对方站点的登录 cookie（SameSite=Lax）
    // 不会随跨站嵌入发送，依赖作者身份的按钮（如飞象「教师大屏」）不会出现。
    if (!isOpenableHttpUrl(target)) return { ok: false, reason: 'invalid_url' }

    const windowName = buildWindowName(options.lessonId, options.cellId)
    const returnUrl = options.returnUrl?.trim() || defaultLessonReturnUrl(options.lessonId)

    try {
      window.name = buildLessonWindowName(options.lessonId)
    } catch {
      /* ignored */
    }

    const win = window.open(target, windowName)

    if (!win) {
      return { ok: false, reason: 'blocked' }
    }

    const session: ExternalBrowserSession = {
      url: target,
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

    const win = window.open(session.url, session.windowName)
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
