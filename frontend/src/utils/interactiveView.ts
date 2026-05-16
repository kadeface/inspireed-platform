/**
 * 交互式课件「教师大屏 / 学生活动」方案一：单入口 URL，由父页面传 view 与 postMessage。
 * 课件可读取 URL 查询参数 view=teacher|student，或监听 postMessage（见 buildInspireedInteractiveViewMessage）。
 */

export type InteractiveViewerRole = 'teacher' | 'student'

/** URL 查询参数名，与课件约定一致 */
export const INTERACTIVE_VIEW_QUERY_KEY = 'view'

export const INSPIREED_INTERACTIVE_MESSAGE_TYPE = 'INSPIREED_INTERACTIVE_VIEW' as const

export function buildInspireedInteractiveViewMessage(view: InteractiveViewerRole) {
  return {
    source: 'inspireed-platform',
    type: INSPIREED_INTERACTIVE_MESSAGE_TYPE,
    view,
  } as const
}

/**
 * 为 http(s) 或相对路径解析后的地址追加 view=teacher|student。
 * blob: 与 about: 原样返回（由父页 postMessage 传递角色）。
 */
export function appendInteractiveViewToUrl(
  url: string | null | undefined,
  view: InteractiveViewerRole
): string | null {
  if (!url || !url.trim()) return null
  const u = url.trim()
  if (u.startsWith('blob:') || u.startsWith('about:')) return u

  try {
    const base = typeof window !== 'undefined' ? window.location.href : 'http://localhost/'
    const parsed = new URL(u, base)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return u
    }
    parsed.searchParams.set(INTERACTIVE_VIEW_QUERY_KEY, view)
    return parsed.toString()
  } catch {
    return u
  }
}
