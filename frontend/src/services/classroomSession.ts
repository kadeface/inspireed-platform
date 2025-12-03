/**
 * 课堂会话 API 服务
 */

import api from './api'
import logger from '../utils/logger'
import type {
  ClassSession,
  ClassSessionCreate,
  ClassSessionUpdate,
  StudentParticipation,
  NavigateToCellRequest,
  StartActivityRequest,
  SessionStatistics,
  StudentPendingSession,
} from '../types/classroomSession'

export const classroomSessionService = {
  /**
   * 创建课堂会话
   */
  async createSession(lessonId: number, data: { classroom_id: number; scheduled_start?: string }): Promise<ClassSession> {
    try {
      const requestBody: any = {
        lesson_id: lessonId,
        classroom_id: data.classroom_id,
      }
      
      // 只在有值时才添加 scheduled_start
      if (data.scheduled_start) {
        requestBody.scheduled_start = data.scheduled_start
      }
      
      // 确保 settings 字段存在（后端需要，即使为空对象）
      // 后端会合并默认设置
      requestBody.settings = {}
      
      console.log('📤 Creating session with request:', {
        url: `/classroom-sessions/lessons/${lessonId}/sessions`,
        body: requestBody,
      })
      
      const response = await api.post(`/classroom-sessions/lessons/${lessonId}/sessions`, requestBody)
      
      // api.post 已经返回 response.data，所以 response 就是数据本身
      // 检查响应数据
      if (!response) {
        throw new Error('创建会话失败：服务器未返回数据')
      }
      
      // 检查是否是空对象
      if (typeof response === 'object' && Object.keys(response).length === 0) {
        throw new Error('创建会话失败：服务器返回了空数据')
      }
      
      // 确保返回的数据有 id 字段（可能是 id 或 _id，或者使用 snake_case 的字段名）
      const sessionId = (response as any).id || (response as any)._id || (response as any).session_id
      if (!sessionId) {
        console.error('Response missing id field:', response)
        throw new Error('创建会话失败：服务器返回的数据格式不正确（缺少 id 字段）')
      }
      
      // 如果响应使用 snake_case，可能需要转换，但目前直接返回
      // 确保返回的数据符合 ClassSession 接口
      const session = {
        ...(response as object),
        id: sessionId,
        // 处理可能的字段名差异
        lessonId: (response as any).lesson_id || (response as any).lessonId,
        classroomId: (response as any).classroom_id || (response as any).classroomId,
        teacherId: (response as any).teacher_id || (response as any).teacherId,
        status: (response as any).status,
        scheduledStart: (response as any).scheduled_start || (response as any).scheduledStart,
        actualStart: (response as any).actual_start || (response as any).actualStart,
        endedAt: (response as any).ended_at || (response as any).endedAt,
        durationMinutes: (response as any).duration_minutes || (response as any).durationMinutes,
        currentCellId: (response as any).current_cell_id || (response as any).currentCellId,
        currentActivityId: (response as any).current_activity_id || (response as any).currentActivityId,
        totalStudents: (response as any).total_students || (response as any).totalStudents || 0,
        activeStudents: (response as any).active_students || (response as any).activeStudents || 0,
        createdAt: (response as any).created_at || (response as any).createdAt,
        updatedAt: (response as any).updated_at || (response as any).updatedAt,
      } as ClassSession
      
      console.log('✅ Session created successfully:', session.id)
      return session
    } catch (error: any) {
      // 增强错误日志，显示完整的错误信息
      console.error('❌ Failed to create session:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        requestUrl: error.config?.url,
        requestData: error.config?.data,
      })
      
      // 提取详细的错误信息
      const errorDetail = error.response?.data?.detail || error.response?.data?.message || error.message
      
      // 如果错误信息是字符串数组（Pydantic验证错误），格式化为更友好的消息
      if (Array.isArray(errorDetail)) {
        const formattedErrors = errorDetail.map((err: any) => {
          const field = err.loc?.join('.') || 'field'
          const msg = err.msg || 'validation error'
          return `${field}: ${msg}`
        }).join('; ')
        throw new Error(`创建会话失败：${formattedErrors}`)
      }
      
      // 如果错误信息是对象，尝试提取关键信息
      if (typeof errorDetail === 'object') {
        const errorMessage = errorDetail.message || JSON.stringify(errorDetail)
        throw new Error(`创建会话失败：${errorMessage}`)
      }
      
      // 对于字符串错误（如"已有活跃会话"），保留原始错误以便调用者可以访问 response
      // 这样 TeacherControlPanel 可以提取会话ID等信息
      const newError = new Error(`创建会话失败：${errorDetail || '未知错误'}`)
      // 保留原始响应用于错误处理
      ;(newError as any).response = error.response
      throw newError
    }
  },

  /**
   * 获取会话详情
   */
  async getSession(sessionId: number): Promise<ClassSession> {
    try {
      // 获取会话
      // api.get 已经返回 response.data，所以 response 就是数据本身
      const response = await api.get(`/classroom-sessions/sessions/${sessionId}`)
      // 获取会话响应
      
      if (!response) {
        throw new Error('获取会话失败：服务器未返回数据')
      }
      
      // 确保 settings 对象存在
      const rawSettings = (response as any).settings || {}
      
      // 处理字段映射（snake_case 到 camelCase）
      const session = {
        ...(response as object),
        id: (response as any).id,
        lessonId: (response as any).lesson_id || (response as any).lessonId,
        classroomId: (response as any).classroom_id || (response as any).classroomId,
        teacherId: (response as any).teacher_id || (response as any).teacherId,
        status: (response as any).status,
        scheduledStart: (response as any).scheduled_start || (response as any).scheduledStart,
        actualStart: (response as any).actual_start || (response as any).actualStart,
        endedAt: (response as any).ended_at || (response as any).endedAt,
        durationMinutes: (response as any).duration_minutes || (response as any).durationMinutes,
        currentCellId: (response as any).current_cell_id || (response as any).currentCellId,
        currentActivityId: (response as any).current_activity_id || (response as any).currentActivityId,
        settings: rawSettings,  // 确保 settings 被正确映射（即使为空对象也要保留）
        totalStudents: (response as any).total_students || (response as any).totalStudents || 0,
        activeStudents: (response as any).active_students || (response as any).activeStudents || 0,
        createdAt: (response as any).created_at || (response as any).createdAt,
        updatedAt: (response as any).updated_at || (response as any).updatedAt,
        lessonTitle: (response as any).lesson_title || (response as any).lessonTitle,
        classroomName: (response as any).classroom_name || (response as any).classroomName,
        teacherName: (response as any).teacher_name || (response as any).teacherName,
      } as ClassSession
      
      return session
    } catch (error: any) {
      console.error('Get session error:', error)
      throw error
    }
  },

  /**
   * 获取学生待开始的课堂列表（pending状态的会话）
   */
  async getStudentPendingSessions(): Promise<StudentPendingSession[]> {
    try {
      const response = await api.get('/classroom-sessions/student/pending-sessions')
      
      // 确保返回数组
      const sessions = Array.isArray(response) ? response : []
      
      // 转换字段名：后端snake_case -> 前端camelCase
      return sessions.map((s: any) => ({
        id: s.id,
        lessonId: s.lesson_id || s.lessonId,
        lessonTitle: s.lesson_title || s.lessonTitle,
        teacherId: s.teacher_id || s.teacherId,
        teacherName: s.teacher_name || s.teacherName,
        classroomId: s.classroom_id || s.classroomId,
        classroomName: s.classroom_name || s.classroomName,
        status: s.status,
        createdAt: s.created_at || s.createdAt,
        scheduledStart: s.scheduled_start || s.scheduledStart,
        totalStudents: s.total_students || s.totalStudents || 0,
        activeStudents: s.active_students || s.activeStudents || 0,
      } as StudentPendingSession))
    } catch (error: any) {
      console.error('Get student pending sessions error:', error)
      throw error
    }
  },

  /**
   * 获取学生正在上课的课堂列表（active状态的会话）
   */
  async getStudentActiveSessions(): Promise<StudentPendingSession[]> {
    try {
      const response = await api.get('/classroom-sessions/student/active-sessions')
      
      // 确保返回数组
      const sessions = Array.isArray(response) ? response : []
      
      // 转换字段名：后端snake_case -> 前端camelCase
      return sessions.map((s: any) => ({
        id: s.id,
        lessonId: s.lesson_id || s.lessonId,
        lessonTitle: s.lesson_title || s.lessonTitle,
        teacherId: s.teacher_id || s.teacherId,
        teacherName: s.teacher_name || s.teacherName,
        classroomId: s.classroom_id || s.classroomId,
        classroomName: s.classroom_name || s.classroomName,
        status: s.status,
        createdAt: s.created_at || s.createdAt,
        scheduledStart: s.scheduled_start || s.scheduledStart,
        totalStudents: s.total_students || s.totalStudents || 0,
        activeStudents: s.active_students || s.activeStudents || 0,
      } as StudentPendingSession))
    } catch (error: any) {
      console.error('Get student active sessions error:', error)
      throw error
    }
  },

  /**
   * 获取教案的所有会话
   */
  async listSessions(lessonId: number, status?: string): Promise<ClassSession[]> {
    try {
      const params = status ? { status } : {}
      // api.get 已经返回 response.data，所以 response 就是数据本身
      const response = await api.get(`/classroom-sessions/lessons/${lessonId}/sessions`, { params })
      
      // 确保返回数组
      const sessions = Array.isArray(response) ? response : []
      
      // 转换字段名（如果需要）
      return sessions.map((s: any) => ({
        ...s,
        id: s.id,
        lessonId: s.lesson_id || s.lessonId,
        classroomId: s.classroom_id || s.classroomId,
        teacherId: s.teacher_id || s.teacherId,
        status: s.status,
        scheduledStart: s.scheduled_start || s.scheduledStart,
        actualStart: s.actual_start || s.actualStart,
        endedAt: s.ended_at || s.endedAt,
        durationMinutes: s.duration_minutes || s.durationMinutes,
        currentCellId: s.current_cell_id || s.currentCellId,
        currentActivityId: s.current_activity_id || s.currentActivityId,
        settings: s.settings || {},  // 确保 settings 被正确包含
        totalStudents: s.total_students || s.totalStudents || 0,
        activeStudents: s.active_students || s.activeStudents || 0,
        createdAt: s.created_at || s.createdAt,
        updatedAt: s.updated_at || s.updatedAt,
      } as ClassSession))
    } catch (error: any) {
      console.error('List sessions error:', error)
      throw error
    }
  },

  /**
   * 开始会话
   */
  async startSession(sessionId: number): Promise<ClassSession> {
    const response = await api.post<ClassSession>(`/classroom-sessions/sessions/${sessionId}/start`)
    return response
  },

  /**
   * 暂停会话
   */
  async pauseSession(sessionId: number): Promise<ClassSession> {
    const response = await api.post<ClassSession>(`/classroom-sessions/sessions/${sessionId}/pause`)
    return response
  },

  /**
   * 继续会话
   */
  async resumeSession(sessionId: number): Promise<ClassSession> {
    const response = await api.post<ClassSession>(`/classroom-sessions/sessions/${sessionId}/resume`)
    return response
  },

  /**
   * 结束会话
   */
  async endSession(sessionId: number, notes?: string): Promise<ClassSession> {
    const response = await api.post<ClassSession>(`/classroom-sessions/sessions/${sessionId}/end`, {
      notes,
    })
    return response
  },

  /**
   * 导航到Cell
   */
  async navigateToCell(sessionId: number, data: NavigateToCellRequest): Promise<ClassSession> {
    try {
      // 导航到 Cell
      const requestData: any = {}
      if (data.cellId !== undefined) {
        requestData.cell_id = data.cellId
      }
      if (data.cellOrder !== undefined) {
        requestData.cell_order = data.cellOrder
      }
      if (data.action !== undefined) {
        requestData.action = data.action
      }
      if (data.multiSelect !== undefined) {
        requestData.multi_select = data.multiSelect
      }
      // 🆕 新增：支持 display_cell_orders（推荐方式）
      if (data.displayCellOrders !== undefined) {
        requestData.display_cell_orders = data.displayCellOrders
      }
      const response = await api.post(`/classroom-sessions/sessions/${sessionId}/navigate`, requestData)
      // 导航响应
      
      // 检查响应是否为空或格式不正确
      if (!response || typeof response !== 'object') {
        console.error('导航响应格式错误:', response)
        throw new Error('导航失败：服务器返回的数据格式不正确')
      }
      
      // 处理字段映射（snake_case 到 camelCase）
      const settings = (response as any).settings || {}
      
      const session = {
        ...(response as object),
        id: (response as any).id,
        lessonId: (response as any).lesson_id || (response as any).lessonId,
        classroomId: (response as any).classroom_id || (response as any).classroomId,
        teacherId: (response as any).teacher_id || (response as any).teacherId,
        status: (response as any).status,
        scheduledStart: (response as any).scheduled_start || (response as any).scheduledStart,
        actualStart: (response as any).actual_start || (response as any).actualStart,
        endedAt: (response as any).ended_at || (response as any).endedAt,
        durationMinutes: (response as any).duration_minutes || (response as any).durationMinutes,
        currentCellId: (response as any).current_cell_id ?? (response as any).currentCellId ?? null,
        currentActivityId: (response as any).current_activity_id ?? (response as any).currentActivityId ?? null,
        settings: settings,  // 确保 settings 被正确映射
        totalStudents: (response as any).total_students || (response as any).totalStudents || 0,
        activeStudents: (response as any).active_students || (response as any).activeStudents || 0,
        createdAt: (response as any).created_at || (response as any).createdAt,
        updatedAt: (response as any).updated_at || (response as any).updatedAt,
      } as ClassSession
      
      return session
    } catch (error: any) {
      console.error('导航失败:', error)
      
      // 显示详细的错误信息
      if (error.response) {
        // 提取详细错误信息
        const errorDetail = error.response.data?.detail || error.response.data?.message || JSON.stringify(error.response.data)
        throw new Error(`导航失败: ${errorDetail}`)
      } else if (error.request) {
        throw new Error('导航失败：服务器无响应')
      } else {
        throw error
      }
    }
  },

  /**
   * 开始活动
   */
  async startActivity(sessionId: number, data: StartActivityRequest): Promise<ClassSession> {
    const response = await api.post<ClassSession>(`/classroom-sessions/sessions/${sessionId}/start-activity`, data)
    return response
  },

  /**
   * 结束活动
   */
  async endActivity(sessionId: number): Promise<ClassSession> {
    const response = await api.post<ClassSession>(`/classroom-sessions/sessions/${sessionId}/end-activity`)
    return response
  },

  /**
   * 获取参与者列表
   */
  async getParticipants(sessionId: number, isActive?: boolean): Promise<StudentParticipation[]> {
    try {
      logger.poll('获取参与者列表', { sessionId, isActive })
      const params = isActive !== undefined ? { is_active: isActive } : {}
      // api.get 已经返回 response.data，所以 response 就是数据本身
      const response = await api.get(`/classroom-sessions/sessions/${sessionId}/participants`, { params })
      logger.debug('参与者列表响应', response)
      
      if (!response) {
        logger.warn('参与者列表为空')
        return []
      }
      
      // 确保是数组
      const participants = Array.isArray(response) ? response : []
      logger.debug(`找到 ${participants.length} 个参与者`)
      
      // 处理字段映射（snake_case 到 camelCase）
      return participants.map((p: any) => {
        const participant = {
          ...p,
          id: p.id,
          sessionId: p.session_id || p.sessionId,
          studentId: p.student_id || p.studentId,
          joinedAt: p.joined_at || p.joinedAt,
          lastActiveAt: p.last_active_at || p.lastActiveAt,
          leftAt: p.left_at || p.leftAt,
          isActive: p.is_active ?? p.isActive ?? true, // 重点：处理 is_active 字段
          currentCellId: p.current_cell_id ?? p.currentCellId ?? null,
          completedCells: p.completed_cells || p.completedCells || [],
          progressPercentage: p.progress_percentage || p.progressPercentage || 0,
          studentName: p.student_name || p.studentName,
          studentEmail: p.student_email || p.studentEmail,
        }
        
        return participant
      })
    } catch (error: any) {
      logger.error('获取参与者列表失败:', error)
      logger.error('错误详情:', {
        message: error.message,
        response: error.response,
        status: error.response?.status,
        data: error.response?.data,
      })
      throw error
    }
  },

  /**
   * 加入会话（学生）
   */
  async joinSession(sessionId: number): Promise<StudentParticipation> {
    try {
      // 加入会话
      // api.post 已经返回 response.data，所以 response 就是数据本身
      const response = await api.post(`/classroom-sessions/sessions/${sessionId}/join`)
      // 加入会话响应
      
      if (!response) {
        throw new Error('加入会话失败：服务器未返回数据')
      }
      
      // 处理字段映射（如果需要）
      const participation = {
        ...(response as object),
        id: (response as any).id,
        sessionId: (response as any).session_id || (response as any).sessionId,
        studentId: (response as any).student_id || (response as any).studentId,
        joinedAt: (response as any).joined_at || (response as any).joinedAt,
        lastActiveAt: (response as any).last_active_at || (response as any).lastActiveAt,
        leftAt: (response as any).left_at || (response as any).leftAt,
        isActive: (response as any).is_active ?? (response as any).isActive ?? true,
        currentCellId: (response as any).current_cell_id ?? (response as any).currentCellId ?? null,
        completedCells: (response as any).completed_cells || (response as any).completedCells || [],
        progressPercentage: (response as any).progress_percentage || (response as any).progressPercentage || 0,
        studentName: (response as any).student_name || (response as any).studentName,
        studentEmail: (response as any).student_email || (response as any).studentEmail,
      }
      
      return participation
    } catch (error: any) {
      console.error('加入会话失败:', error)
      throw error
    }
  },

  /**
   * 离开会话（学生）
   */
  async leaveSession(sessionId: number): Promise<void> {
    await api.post(`/classroom-sessions/sessions/${sessionId}/leave`)
  },

  /**
   * 获取会话统计
   */
  async getStatistics(sessionId: number): Promise<SessionStatistics> {
    const response = await api.get<SessionStatistics>(`/classroom-sessions/sessions/${sessionId}/statistics`)
    return response
  },

  /**
   * 更新显示模式（全屏/窗口）
   */
  async updateDisplayMode(sessionId: number, displayMode: 'fullscreen' | 'window'): Promise<ClassSession> {
    try {
      const response = await api.post(`/classroom-sessions/sessions/${sessionId}/display-mode`, {
        display_mode: displayMode,
      })
      
      // 处理字段映射（snake_case 到 camelCase）
      const settings = (response as any).settings || {}
      
      const session = {
        ...(response as object),
        id: (response as any).id,
        lessonId: (response as any).lesson_id || (response as any).lessonId,
        classroomId: (response as any).classroom_id || (response as any).classroomId,
        teacherId: (response as any).teacher_id || (response as any).teacherId,
        status: (response as any).status,
        scheduledStart: (response as any).scheduled_start || (response as any).scheduledStart,
        actualStart: (response as any).actual_start || (response as any).actualStart,
        endedAt: (response as any).ended_at || (response as any).endedAt,
        durationMinutes: (response as any).duration_minutes || (response as any).durationMinutes,
        currentCellId: (response as any).current_cell_id ?? (response as any).currentCellId ?? null,
        currentActivityId: (response as any).current_activity_id ?? (response as any).currentActivityId ?? null,
        settings: settings,
        totalStudents: (response as any).total_students || (response as any).totalStudents || 0,
        activeStudents: (response as any).active_students || (response as any).activeStudents || 0,
        createdAt: (response as any).created_at || (response as any).createdAt,
        updatedAt: (response as any).updated_at || (response as any).updatedAt,
      } as ClassSession
      
      return session
    } catch (error: any) {
      console.error('更新显示模式失败:', error)
      throw error
    }
  },
}

export default classroomSessionService

