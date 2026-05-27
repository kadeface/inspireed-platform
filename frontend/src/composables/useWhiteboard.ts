/**
 * 课堂白板 WebSocket 桥接（师生共用）
 */
import { ref } from 'vue'
import { websocketService } from '@/services/websocket'
import type { WebSocketMessage } from '@/services/websocket'

type WhiteboardHandler = (type: string, data: Record<string, unknown>) => void

const handlers = new Set<WhiteboardHandler>()
let teacherSend: ((msg: WebSocketMessage) => void) | null = null

export function registerWhiteboardTeacherSend(fn: (msg: WebSocketMessage) => void) {
  teacherSend = fn
  return () => {
    if (teacherSend === fn) teacherSend = null
  }
}

export function sendWhiteboardWs(message: WebSocketMessage) {
  if (teacherSend) {
    teacherSend(message)
    return
  }
  websocketService.send(message)
}

export function handleWhiteboardWsMessage(message: WebSocketMessage) {
  const type = message.type
  if (!type?.startsWith('whiteboard.')) return
  handlers.forEach((h) => h(type, message.data || {}))
}

export function subscribeWhiteboard(handler: WhiteboardHandler) {
  handlers.add(handler)
  return () => handlers.delete(handler)
}

export function subscribeWhiteboardCell(
  sessionId: number,
  cellId: number,
  onEvent: WhiteboardHandler
) {
  const unsub = subscribeWhiteboard((type, data) => {
    if (Number(data.cell_id) !== cellId && Number(data.session_id) !== sessionId) {
      if (type !== 'whiteboard.groups') return
    }
    if (
      type.startsWith('whiteboard.') &&
      (data.cell_id == null || Number(data.cell_id) === cellId)
    ) {
      onEvent(type, data)
    }
  })
  sendWhiteboardWs({
    type: 'whiteboard.subscribe',
    timestamp: new Date().toISOString(),
    data: { cell_id: cellId, session_id: sessionId },
  })
  return unsub
}

export function sendWhiteboardOp(
  sessionId: number,
  cellId: number,
  op: Record<string, unknown>
) {
  sendWhiteboardWs({
    type: 'whiteboard.op',
    timestamp: new Date().toISOString(),
    data: { session_id: sessionId, cell_id: cellId, op },
  })
}

export const whiteboardSyncReady = ref(false)
