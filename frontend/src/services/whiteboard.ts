/**
 * 课堂白板 REST API
 */
import api from './api'

export interface WhiteboardStateDto {
  session_id: number
  cell_id: number
  document: Record<string, unknown>
  version: number
}

export interface SessionGroupsDto {
  session_id: number
  groups: Array<{ id: number; group_index: number; label: string }>
  members: Array<{ user_id: number; group_index: number; display_name?: string }>
}

export const whiteboardService = {
  async getState(sessionId: number, cellId: number): Promise<WhiteboardStateDto> {
    const res = await api.get(
      `/classroom-sessions/sessions/${sessionId}/whiteboard/${cellId}/state`
    )
    return res.data
  },

  async setMode(
    sessionId: number,
    cellId: number,
    mode: 'setup' | 'collaborate' | 'locked'
  ): Promise<WhiteboardStateDto> {
    const res = await api.patch(
      `/classroom-sessions/sessions/${sessionId}/whiteboard/${cellId}/mode`,
      { mode }
    )
    return res.data
  },

  async getGroups(sessionId: number): Promise<SessionGroupsDto> {
    const res = await api.get(`/classroom-sessions/sessions/${sessionId}/groups`)
    return res.data
  },

  async setupGroups(
    sessionId: number,
    groupCount: number,
    randomAssign = true
  ): Promise<SessionGroupsDto> {
    const res = await api.put(`/classroom-sessions/sessions/${sessionId}/groups/setup`, {
      group_count: groupCount,
      random_assign: randomAssign,
    })
    return res.data
  },
}
