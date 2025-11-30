/**
 * 教学活动 API 服务
 */

import api from './api'
import type {
  ActivitySubmission,
  ActivityItemStatistic,
  FlowchartSnapshot,
  FormativeAssessmentRecord,
  CreateActivitySubmissionRequest,
  UpdateActivitySubmissionRequest,
  SubmitActivityRequest,
  GradeActivityRequest,
  PeerReview,
  CreatePeerReviewRequest,
  ActivityStatistics,
} from '../types/activity'

/**
 * 活动提交相关 API
 */
export const activityService = {
  // ========== 学生端 API ==========

  /**
   * 创建活动提交（草稿）
   */
  async createSubmission(
    data: CreateActivitySubmissionRequest
  ): Promise<ActivitySubmission> {
    // 转换驼峰命名为蛇形命名以匹配后端API
    // 注意：cellId 可能是数字或 UUID 字符串，后端现在都支持
    const requestData: any = {
      cell_id: data.cellId,  // 可以是数字或 UUID 字符串
      lesson_id: data.lessonId,
      responses: data.responses || {}, // 确保 responses 始终存在
    }
    
    // 添加 sessionId（课堂模式）
    if (data.sessionId !== undefined) {
      requestData.session_id = data.sessionId
      console.log('✅ 添加 session_id 到请求:', data.sessionId)
    } else {
      console.warn('⚠️ data.sessionId 是 undefined，未添加到请求')
    }
    
    // started_at 需要是 ISO 字符串格式，Pydantic 会自动转换为 datetime
    if (data.startedAt !== undefined) {
      // 确保是有效的 ISO 字符串
      const startedAt = typeof data.startedAt === 'string'
        ? data.startedAt
        : (data.startedAt as unknown) instanceof Date
          ? (data.startedAt as unknown as Date).toISOString()
          : String(data.startedAt)
      requestData.started_at = startedAt
    }
    
    if (data.processTrace !== undefined) {
      requestData.process_trace = data.processTrace
    }
    if (data.context !== undefined) {
      requestData.context = data.context
    }
    if (data.activityPhase !== undefined) {
      requestData.activity_phase = data.activityPhase
    }
    if (data.attemptNo !== undefined) {
      requestData.attempt_no = data.attemptNo
    }
    
    console.log('📤 Creating submission:', {
      cell_id: requestData.cell_id,
      lesson_id: requestData.lesson_id,
      session_id: requestData.session_id,  // 🔍 添加 session_id 到日志
      responses_count: Object.keys(requestData.responses).length,
      started_at: requestData.started_at,
    })
    
    try {
      const response = await api.post<ActivitySubmission>('/activities/submissions', requestData)
      return response
    } catch (error: any) {
      console.error('❌ Create submission failed:', {
        status: error.response?.status,
        data: error.response?.data,
        request: requestData,
      })
      throw error
    }
  },

  /**
   * 获取提交详情
   */
  async getSubmission(submissionId: number): Promise<ActivitySubmission> {
    const response = await api.get<ActivitySubmission>(`/activities/submissions/${submissionId}`)
    return response
  },

  /**
   * 更新提交（保存草稿）
   */
  async updateSubmission(
    submissionId: number,
    data: UpdateActivitySubmissionRequest
  ): Promise<ActivitySubmission> {
    // 转换驼峰命名为蛇形命名以匹配后端API
    const requestData: any = {}
    if (data.responses !== undefined) {
      requestData.responses = data.responses
    }
    if (data.status !== undefined) {
      requestData.status = data.status
    }
    if (data.sessionId !== undefined) {
      requestData.session_id = data.sessionId  // ✅ 支持更新 session_id
    }
    if (data.timeSpent !== undefined) {
      requestData.time_spent = data.timeSpent
    }
    if (data.processTrace !== undefined) {
      requestData.process_trace = data.processTrace
    }
    if (data.context !== undefined) {
      requestData.context = data.context
    }
    if (data.activityPhase !== undefined) {
      requestData.activity_phase = data.activityPhase
    }
    if (data.attemptNo !== undefined) {
      requestData.attempt_no = data.attemptNo
    }
    
    const response = await api.patch<ActivitySubmission>(`/activities/submissions/${submissionId}`, requestData)
    return response
  },

  /**
   * 正式提交活动
   */
  async submitActivity(
    submissionId: number,
    data: SubmitActivityRequest
  ): Promise<ActivitySubmission> {
    // 转换驼峰命名为蛇形命名以匹配后端API
    const requestData: any = {
      responses: data.responses,
    }
    if (data.sessionId !== undefined) {
      requestData.session_id = data.sessionId
    }
    if (data.timeSpent !== undefined) {
      requestData.time_spent = data.timeSpent
    }
    if (data.processTrace !== undefined) {
      requestData.process_trace = data.processTrace
    }
    if (data.context !== undefined) {
      requestData.context = data.context
    }
    if (data.activityPhase !== undefined) {
      requestData.activity_phase = data.activityPhase
    }
    if (data.attemptNo !== undefined) {
      requestData.attempt_no = data.attemptNo
    }
    
    console.log('📤 Submitting activity:', {
      submissionId,
      sessionId: requestData.session_id,
      timeSpent: requestData.time_spent,
      responsesCount: Object.keys(requestData.responses).length,
    })
    
    try {
      const response = await api.post<ActivitySubmission>(
        `/activities/submissions/${submissionId}/submit`,
        requestData
      )
      console.log('✅ Activity submitted successfully:', { 
        submissionId: response.id, 
        status: response.status 
      })
      return response
    } catch (error: any) {
      console.error('❌ Submit activity failed:', {
        submissionId,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      })
      throw error
    }
  },

  /**
   * 获取我在某个教案中的所有提交
   */
  async getMyLessonSubmissions(lessonId: number): Promise<ActivitySubmission[]> {
    const response = await api.get<ActivitySubmission[]>(`/activities/lessons/${lessonId}/my-submissions`)
    return response
  },

  /**
   * 获取单个 Cell 的我的提交
   */
  async getMyCellSubmission(cellId: number): Promise<ActivitySubmission | null> {
    try {
      const response = await api.get<ActivitySubmission>(`/activities/cells/${cellId}/my-submission`)
      return response
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  // ========== 教师端 API ==========

  /**
   * 获取 Cell 的所有提交（教师端）
   */
  async getCellSubmissions(
    cellId: number,
    status?: string,
    sessionId?: number,
    lessonId?: number
  ): Promise<ActivitySubmission[]> {
    const params: Record<string, any> = {}
    if (status) params.status = status
    if (sessionId) params.session_id = sessionId
    if (lessonId) params.lesson_id = lessonId
    // 🆕 只在有 sessionId 时才包含未开始的学生（课堂模式）
    // 没有 sessionId 时（课后模式），只返回实际提交记录
    params.include_not_started = !!sessionId
    const response = await api.get<ActivitySubmission[]>(`/activities/cells/${cellId}/submissions`, { params })
    return response
  },

  /**
   * 评分
   */
  async gradeSubmission(
    submissionId: number,
    data: GradeActivityRequest
  ): Promise<ActivitySubmission> {
    const response = await api.post<ActivitySubmission>(
      `/activities/submissions/${submissionId}/grade`,
      data
    )
    return response
  },

  /**
   * 批量评分
   */
  async bulkGrade(submissionIds: number[], score: number, feedback?: string): Promise<any> {
    const response = await api.post<any>('/activities/submissions/bulk-grade', {
      submission_ids: submissionIds,
      score,
      teacher_feedback: feedback,
    })
    return response
  },

  /**
   * 批量退回
   */
  async bulkReturn(submissionIds: number[], feedback: string): Promise<any> {
    const response = await api.post<any>('/activities/submissions/bulk-return', {
      submission_ids: submissionIds,
      teacher_feedback: feedback,
    })
    return response
  },

  // ========== 互评 API ==========

  /**
   * 分配互评任务（教师端）
   */
  async assignPeerReviews(data: {
    cellId: number
    lessonId: number
    reviewsPerStudent: number
    isAnonymous: boolean
  }): Promise<any> {
    const response = await api.post<any>('/activities/peer-reviews/assign', {
      cell_id: data.cellId,
      lesson_id: data.lessonId,
      reviews_per_student: data.reviewsPerStudent,
      is_anonymous: data.isAnonymous,
    })
    return response
  },

  /**
   * 获取某个提交收到的所有互评
   */
  async getSubmissionPeerReviews(submissionId: number): Promise<PeerReview[]> {
    const response = await api.get<PeerReview[]>(`/activities/submissions/${submissionId}/peer-reviews`)
    return response
  },

  /**
   * 获取我的互评任务（学生端）
   */
  async getMyPeerReviewTasks(status?: string): Promise<PeerReview[]> {
    const params = status ? { status } : {}
    const response = await api.get<PeerReview[]>('/activities/my-peer-review-tasks', { params })
    return response
  },

  /**
   * 提交互评
   */
  async submitPeerReview(
    reviewId: number,
    data: CreatePeerReviewRequest
  ): Promise<PeerReview> {
    const response = await api.post<PeerReview>(`/activities/peer-reviews/${reviewId}/submit`, data)
    return response
  },

  // ========== 统计 API ==========

  /**
   * 获取活动统计数据
   */
  async getStatistics(cellId: number): Promise<ActivityStatistics> {
    const response = await api.get<ActivityStatistics>(`/activities/cells/${cellId}/statistics`)
    return response
  },

  /**
   * 获取题目级统计
   */
  async getItemStatistics(cellId: number): Promise<ActivityItemStatistic[]> {
    const response = await api.get<ActivityItemStatistic[]>(
      `/activities/cells/${cellId}/item-statistics`
    )
    return response
  },

  /**
   * 获取流程图快照
   */
  async getFlowchartSnapshots(
    cellId: number,
    options: { studentId?: number } = {}
  ): Promise<FlowchartSnapshot[]> {
    const params = options.studentId ? { student_id: options.studentId } : undefined
    const response = await api.get<FlowchartSnapshot[]>(
      `/activities/cells/${cellId}/flowchart-snapshots`,
      { params }
    )
    return response
  },

  /**
   * 获取课程的过程性评估摘要
   */
  async getFormativeAssessments(
    lessonId: number,
    filters: { studentId?: number; phase?: string; riskLevel?: string } = {}
  ): Promise<FormativeAssessmentRecord[]> {
    const params: Record<string, any> = {}
    if (filters.studentId !== undefined) params.student_id = filters.studentId
    if (filters.phase) params.phase = filters.phase
    if (filters.riskLevel) params.risk_level = filters.riskLevel
    const response = await api.get<FormativeAssessmentRecord[]>(
      `/activities/lessons/${lessonId}/formative-assessments`,
      { params }
    )
    return response
  },

  /**
   * 重新计算指定学生的过程性评估
   */
  async recomputeFormativeAssessment(
    lessonId: number,
    studentId: number,
    phase?: string
  ): Promise<FormativeAssessmentRecord> {
    const params = phase ? { phase } : undefined
    const response = await api.post<FormativeAssessmentRecord>(
      `/activities/lessons/${lessonId}/formative-assessments/${studentId}/recompute`,
      undefined,
      { params }
    )
    return response
  },

  // ========== 离线同步 API ==========

  /**
   * 同步离线数据
   */
  async syncOfflineData(submissions: any[]): Promise<any> {
    const response = await api.post<any>('/activities/submissions/sync', {
      submissions,
    })
    return response
  },

  // ========== 导出数据 API ==========

  /**
   * 导出提交数据
   */
  async exportSubmissions(cellId: number, format: 'csv' | 'xlsx' | 'json' = 'csv'): Promise<Blob> {
    // 注意：这个方法比较特殊，api.get 内部会检查 responseType: 'blob'
    // 并且在 api.ts 中 downloadFile 方法已经正确处理了 Blob 类型
    // 但为了统一，我们仍然使用 api.downloadFile，但如果不存在这个方法，
    // 就需要保留 response.data，因为 Blob 响应是特殊的
    const response = await api.downloadFile(`/activities/cells/${cellId}/export`, {
      params: { format },
    })
    return response
  },
}

export default activityService

