import { api } from './api'
import { snakeToCamel, camelToSnake } from '../utils/fieldConverter'
import type {
  ClassroomInfo,
  StudentInfo,
  ClassroomMembership,
  ClassroomMembershipCreate,
  ClassroomMembershipUpdate,
  ClassroomMemberBatchImportRequest,
  ClassroomMemberBatchImportResponse,
  AttendanceSessionCreate,
  AttendanceSession,
  AttendanceSessionWithEntries,
  AttendanceEntryUpdate,
  PositiveBehaviorTypeInfo,
  PositiveBehaviorCreate,
  PositiveBehavior,
  PositiveBehaviorLeaderboardEntry,
  DisciplineEventTypeInfo,
  DisciplineRecordCreate,
  DisciplineRecord,
  DutyRuleCreate,
  DutyRule,
  DutyGenerateRequest,
  DutyAssignment,
  DutyAssignmentUpdate,
  ClassroomSettingsUpdate,
  ClassroomSettings,
  ClassroomStats,
  StudentStats,
} from '../types/classroomAssistant'

export const classroomAssistantService = {
  // ==================== 班级和成员 ====================

  /**
   * 获取我可进入的班级列表
   */
  async getMyClassrooms(): Promise<ClassroomInfo[]> {
    const data = await api.get<any[]>('/classroom-assistant/classrooms/mine')
    return snakeToCamel<ClassroomInfo[]>(data)
  },

  /**
   * 获取班级所有成员列表
   */
  async getClassroomMembers(classroomId: number): Promise<ClassroomMembership[]> {
    const data = await api.get<any[]>(`/classroom-assistant/classrooms/${classroomId}/members`)
    return snakeToCamel<ClassroomMembership[]>(data)
  },

  /**
   * 获取班级学生列表
   */
  async getClassroomStudents(classroomId: number): Promise<StudentInfo[]> {
    const data = await api.get<any[]>(`/classroom-assistant/classrooms/${classroomId}/students`)
    return snakeToCamel<StudentInfo[]>(data)
  },

  /**
   * 添加班级成员
   */
  async addClassroomMember(
    classroomId: number,
    data: ClassroomMembershipCreate
  ): Promise<ClassroomMembership> {
    const requestData = camelToSnake({ ...data, classroomId })
    const response = await api.post<any>(
      `/classroom-assistant/classrooms/${classroomId}/members`,
      requestData
    )
    return snakeToCamel<ClassroomMembership>(response)
  },

  /**
   * 更新班级成员信息
   */
  async updateClassroomMember(
    classroomId: number,
    userId: number,
    data: ClassroomMembershipUpdate
  ): Promise<ClassroomMembership> {
    const requestData = camelToSnake(data)
    const response = await api.put<any>(
      `/classroom-assistant/classrooms/${classroomId}/members/${userId}`,
      requestData
    )
    return snakeToCamel<ClassroomMembership>(response)
  },

  /**
   * 移除班级成员
   */
  async removeClassroomMember(classroomId: number, userId: number): Promise<void> {
    return api.delete(`/classroom-assistant/classrooms/${classroomId}/members/${userId}`)
  },

  /**
   * 批量导入班级成员
   */
  async batchImportClassroomMembers(
    classroomId: number,
    data: ClassroomMemberBatchImportRequest
  ): Promise<ClassroomMemberBatchImportResponse> {
    const requestData = camelToSnake(data)
    const response = await api.post<any>(
      `/classroom-assistant/classrooms/${classroomId}/members/batch-import`,
      requestData
    )
    return snakeToCamel<ClassroomMemberBatchImportResponse>(response)
  },

  /**
   * 更新班级设置
   */
  async updateClassroomSettings(
    classroomId: number,
    settings: ClassroomSettingsUpdate
  ): Promise<ClassroomSettings> {
    const requestData = camelToSnake(settings)
    const data = await api.patch<any>(
      `/classroom-assistant/classrooms/${classroomId}/settings`,
      requestData
    )
    return snakeToCamel<ClassroomSettings>(data)
  },

  // ==================== 考勤 ====================

  /**
   * 创建考勤会话
   */
  async createAttendanceSession(
    classroomId: number,
    data: AttendanceSessionCreate
  ): Promise<AttendanceSession> {
    try {
      const requestData = camelToSnake(data)
      const response = await api.post<any>(
        `/classroom-assistant/classrooms/${classroomId}/attendance/sessions`,
        requestData
      )
      return snakeToCamel<AttendanceSession>(response)
    } catch (error: any) {
      console.error('创建考勤会话失败:', error)
      // 保留原始错误信息，让调用方可以访问 error.response
      const errorMessage = error.response?.data?.detail || error.message || '创建考勤会话失败'
      const newError = new Error(errorMessage)
      ;(newError as any).response = error.response
      throw newError
    }
  },

  /**
   * 获取当前未完成的考勤会话
   */
  async getCurrentAttendanceSession(classroomId: number): Promise<AttendanceSessionWithEntries | null> {
    const data = await api.get<any>(
      `/classroom-assistant/classrooms/${classroomId}/attendance/sessions/current`
    )
    if (!data) return null
    return snakeToCamel<AttendanceSessionWithEntries>(data)
  },

  /**
   * 获取考勤会话列表（历史记录）
   */
  async listAttendanceSessions(
    classroomId: number,
    includeUnfinished: boolean = false,
    limit: number = 50
  ): Promise<AttendanceSession[]> {
    const params = {
      include_unfinished: includeUnfinished,
      limit,
    }
    const data = await api.get<any[]>(
      `/classroom-assistant/classrooms/${classroomId}/attendance/sessions`,
      { params }
    )
    return data.map((s) => snakeToCamel<AttendanceSession>(s))
  },

  /**
   * 获取今日点名次数
   */
  async getTodayAttendanceCount(classroomId: number): Promise<number> {
    const data = await api.get<number>(
      `/classroom-assistant/classrooms/${classroomId}/attendance/sessions/today-count`
    )
    return data
  },

  /**
   * 获取考勤会话详情
   */
  async getAttendanceSession(sessionId: number): Promise<AttendanceSessionWithEntries> {
    const data = await api.get<any>(
      `/classroom-assistant/attendance/sessions/${sessionId}`
    )
    return snakeToCamel<AttendanceSessionWithEntries>(data)
  },

  /**
   * 更新考勤记录
   */
  async updateAttendanceEntry(
    sessionId: number,
    studentId: number,
    data: AttendanceEntryUpdate
  ): Promise<void> {
    const requestData = camelToSnake(data)
    return api.put(
      `/classroom-assistant/attendance/sessions/${sessionId}/entries/${studentId}`,
      requestData
    )
  },

  /**
   * 一键全到
   */
  async markAllPresent(sessionId: number): Promise<void> {
    return api.post(`/classroom-assistant/attendance/sessions/${sessionId}/mark-all-present`)
  },

  /**
   * 完成考勤会话
   */
  async completeAttendanceSession(sessionId: number): Promise<void> {
    return api.post(`/classroom-assistant/attendance/sessions/${sessionId}/complete`)
  },

  /**
   * 获取考勤记录详情（按状态筛选）
   */
  async getAttendanceEntriesByStatus(
    classroomId: number,
    status?: AttendanceStatus,
    fromDate?: string,
    toDate?: string
  ): Promise<AttendanceEntry[]> {
    const params: any = {}
    if (status) params.status = status
    if (fromDate) params.from_date = fromDate
    if (toDate) params.to_date = toDate
    
    const data = await api.get<any[]>(
      `/classroom-assistant/classrooms/${classroomId}/attendance/entries`,
      { params }
    )
    return data.map((e) => snakeToCamel<AttendanceEntry>(e))
  },

  // ==================== 正面行为 ====================

  /**
   * 获取正面行为类型列表
   */
  async getPositiveBehaviorTypes(): Promise<PositiveBehaviorTypeInfo[]> {
    const data = await api.get<any[]>('/classroom-assistant/positive-behaviors/types')
    return snakeToCamel<PositiveBehaviorTypeInfo[]>(data)
  },

  /**
   * 创建正面行为记录
   */
  async createPositiveBehavior(
    classroomId: number,
    data: PositiveBehaviorCreate
  ): Promise<PositiveBehavior> {
    const requestData = camelToSnake(data)
    const response = await api.post<any>(
      `/classroom-assistant/classrooms/${classroomId}/positive-behaviors`,
      requestData
    )
    return snakeToCamel<PositiveBehavior>(response)
  },

  /**
   * 查询正面行为记录
   */
  async getPositiveBehaviors(
    classroomId: number,
    params?: {
      studentId?: number
      fromDate?: string
      toDate?: string
    }
  ): Promise<PositiveBehavior[]> {
    const snakeParams = params ? camelToSnake(params) : undefined
    const data = await api.get<any[]>(
      `/classroom-assistant/classrooms/${classroomId}/positive-behaviors`,
      { params: snakeParams }
    )
    return snakeToCamel<PositiveBehavior[]>(data)
  },

  /**
   * 获取积分榜
   */
  async getPositiveBehaviorLeaderboard(
    classroomId: number,
    params?: {
      fromDate?: string
      toDate?: string
    }
  ): Promise<PositiveBehaviorLeaderboardEntry[]> {
    const snakeParams = params ? camelToSnake(params) : undefined
    const data = await api.get<any[]>(
      `/classroom-assistant/classrooms/${classroomId}/positive-behaviors/leaderboard`,
      { params: snakeParams }
    )
    return snakeToCamel<PositiveBehaviorLeaderboardEntry[]>(data)
  },

  /**
   * 获取本人的正面行为记录
   */
  async getMyPositiveBehaviors(params?: {
    fromDate?: string
    toDate?: string
  }): Promise<PositiveBehavior[]> {
    const snakeParams = params ? camelToSnake(params) : undefined
    const data = await api.get<any[]>('/classroom-assistant/users/me/positive-behaviors', {
      params: snakeParams,
    })
    return snakeToCamel<PositiveBehavior[]>(data)
  },

  // ==================== 纪律记录 ====================

  /**
   * 获取纪律事件类型列表
   */
  async getDisciplineEventTypes(): Promise<DisciplineEventTypeInfo[]> {
    const data = await api.get<any[]>('/classroom-assistant/discipline/event-types')
    return snakeToCamel<DisciplineEventTypeInfo[]>(data)
  },

  /**
   * 创建纪律记录
   */
  async createDisciplineRecord(
    classroomId: number,
    data: DisciplineRecordCreate
  ): Promise<DisciplineRecord> {
    const requestData = camelToSnake(data)
    const response = await api.post<any>(
      `/classroom-assistant/classrooms/${classroomId}/discipline/records`,
      requestData
    )
    return snakeToCamel<DisciplineRecord>(response)
  },

  /**
   * 查询纪律记录
   */
  async getDisciplineRecords(
    classroomId: number,
    params?: {
      studentId?: number
      fromDate?: string
      toDate?: string
    }
  ): Promise<DisciplineRecord[]> {
    const snakeParams = params ? camelToSnake(params) : undefined
    const data = await api.get<any[]>(
      `/classroom-assistant/classrooms/${classroomId}/discipline/records`,
      { params: snakeParams }
    )
    return snakeToCamel<DisciplineRecord[]>(data)
  },

  // ==================== 值日 ====================

  /**
   * 创建值日规则
   */
  async createDutyRule(classroomId: number, data: DutyRuleCreate): Promise<DutyRule> {
    const requestData = camelToSnake(data)
    const response = await api.post<any>(
      `/classroom-assistant/classrooms/${classroomId}/duty/rules`,
      requestData
    )
    return snakeToCamel<DutyRule>(response)
  },

  /**
   * 生成值日任务
   */
  async generateDutyAssignments(
    classroomId: number,
    data: DutyGenerateRequest
  ): Promise<void> {
    const requestData = camelToSnake(data)
    return api.post(`/classroom-assistant/classrooms/${classroomId}/duty/generate`, requestData)
  },

  /**
   * 获取今日值日任务
   */
  async getTodayDuty(classroomId: number): Promise<DutyAssignment[]> {
    const data = await api.get<any[]>(
      `/classroom-assistant/classrooms/${classroomId}/duty/today`
    )
    return snakeToCamel<DutyAssignment[]>(data)
  },

  /**
   * 获取今日值日任务
   */
  async getTodayDuty(classroomId: number): Promise<DutyAssignment[]> {
    return api.get<DutyAssignment[]>(
      `/classroom-assistant/classrooms/${classroomId}/duty/today`
    )
  },

  /**
   * 更新值日任务状态
   */
  async updateDutyAssignment(
    assignmentId: number,
    data: DutyAssignmentUpdate
  ): Promise<DutyAssignment> {
    const requestData = camelToSnake(data)
    const response = await api.patch<any>(
      `/classroom-assistant/duty/assignments/${assignmentId}`,
      requestData
    )
    return snakeToCamel<DutyAssignment>(response)
  },

  // ==================== 统计 ====================

  /**
   * 获取班级统计
   */
  async getClassroomStats(
    classroomId: number,
    params?: {
      fromDate?: string
      toDate?: string
    }
  ): Promise<ClassroomStats> {
    const snakeParams = params ? camelToSnake(params) : undefined
    const data = await api.get<any>(`/classroom-assistant/classrooms/${classroomId}/stats`, {
      params: snakeParams,
    })
    return snakeToCamel<ClassroomStats>(data)
  },

  /**
   * 获取学生本人统计
   */
  async getMyStats(params?: {
    fromDate?: string
    toDate?: string
  }): Promise<StudentStats> {
    const snakeParams = params ? camelToSnake(params) : undefined
    const data = await api.get<any>('/classroom-assistant/users/me/stats', { params: snakeParams })
    return snakeToCamel<StudentStats>(data)
  },
}
