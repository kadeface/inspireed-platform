/** 外部浏览窗口 → 授课页：切回并定位到 Cell */

export const INSPIREED_RETURN_TO_LESSON = 'INSPIREED_RETURN_TO_LESSON' as const

/** 跨标签通知授课页（不依赖 window.opener） */
export const LESSON_RETURN_CHANNEL = 'inspireed-lesson-return' as const

export type LessonReturnMessage = {
  source: 'inspireed-platform'
  type: typeof INSPIREED_RETURN_TO_LESSON
  cellId?: string | number
}

export function buildLessonReturnMessage(cellId?: string | number): LessonReturnMessage {
  return {
    source: 'inspireed-platform',
    type: INSPIREED_RETURN_TO_LESSON,
    ...(cellId != null && cellId !== '' ? { cellId } : {}),
  }
}

export function isLessonReturnMessage(data: unknown): data is LessonReturnMessage {
  if (!data || typeof data !== 'object') return false
  const d = data as LessonReturnMessage
  return d.source === 'inspireed-platform' && d.type === INSPIREED_RETURN_TO_LESSON
}

export function scrollToLessonCell(cellId?: string | number) {
  if (cellId == null || cellId === '') return
  const el = document.querySelector(`[data-cell-id="${cellId}"]`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

export function handleLessonReturnMessage(data: unknown) {
  if (!isLessonReturnMessage(data)) return
  scrollToLessonCell(data.cellId)
}

/** 从外部浏览页广播「继续听课」 */
export function broadcastLessonReturn(cellId?: string | number) {
  const message = buildLessonReturnMessage(cellId)
  try {
    const channel = new BroadcastChannel(LESSON_RETURN_CHANNEL)
    channel.postMessage(message)
    channel.close()
  } catch {
    /* BroadcastChannel unsupported */
  }
  return message
}
