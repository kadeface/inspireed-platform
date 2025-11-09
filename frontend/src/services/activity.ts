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
    const response = await api.post('/activities/submissions', data)
    return response.data
  },

  /**
   * 获取提交详情
   */
  async getSubmission(submissionId: number): Promise<ActivitySubmission> {
    const response = await api.get(`/activities/submissions/${submissionId}`)
    return response.data
  },

  /**
   * 更新提交（保存草稿）
   */
  async updateSubmission(
    submissionId: number,
    data: UpdateActivitySubmissionRequest
  ): Promise<ActivitySubmission> {
    const response = await api.patch(`/activities/submissions/${submissionId}`, data)
    return response.data
  },

  /**
   * 正式提交活动
   */
  async submitActivity(
    submissionId: number,
    data: SubmitActivityRequest
  ): Promise<ActivitySubmission> {
    const response = await api.post(
      `/activities/submissions/${submissionId}/submit`,
      data
    )
    return response.data
  },

  /**
   * 获取我在某个教案中的所有提交
   */
  async getMyLessonSubmissions(lessonId: number): Promise<ActivitySubmission[]> {
    const response = await api.get(`/activities/lessons/${lessonId}/my-submissions`)
    return response.data
  },

  /**
   * 获取单个 Cell 的我的提交
   */
  async getMyCellSubmission(cellId: number): Promise<ActivitySubmission | null> {
    try {
      const response = await api.get(`/activities/cells/${cellId}/my-submission`)
      return response.data
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
    status?: string
  ): Promise<ActivitySubmission[]> {
    const params = status ? { status } : {}
    const response = await api.get(`/activities/cells/${cellId}/submissions`, { params })
    return response.data
  },

  /**
   * 评分
   */
  async gradeSubmission(
    submissionId: number,
    data: GradeActivityRequest
  ): Promise<ActivitySubmission> {
    const response = await api.post(
      `/activities/submissions/${submissionId}/grade`,
      data
    )
    return response.data
  },

  /**
   * 批量评分
   */
  async bulkGrade(submissionIds: number[], score: number, feedback?: string): Promise<any> {
    const response = await api.post('/activities/submissions/bulk-grade', {
      submission_ids: submissionIds,
      score,
      teacher_feedback: feedback,
    })
    return response.data
  },

  /**
   * 批量退回
   */
  async bulkReturn(submissionIds: number[], feedback: string): Promise<any> {
    const response = await api.post('/activities/submissions/bulk-return', {
      submission_ids: submissionIds,
      teacher_feedback: feedback,
    })
    return response.data
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
    const response = await api.post('/activities/peer-reviews/assign', {
      cell_id: data.cellId,
      lesson_id: data.lessonId,
      reviews_per_student: data.reviewsPerStudent,
      is_anonymous: data.isAnonymous,
    })
    return response.data
  },

  /**
   * 获取某个提交收到的所有互评
   */
  async getSubmissionPeerReviews(submissionId: number): Promise<PeerReview[]> {
    const response = await api.get(`/activities/submissions/${submissionId}/peer-reviews`)
    return response.data
  },

  /**
   * 获取我的互评任务（学生端）
   */
  async getMyPeerReviewTasks(status?: string): Promise<PeerReview[]> {
    const params = status ? { status } : {}
    const response = await api.get('/activities/my-peer-review-tasks', { params })
    return response.data
  },

  /**
   * 提交互评
   */
  async submitPeerReview(
    reviewId: number,
    data: CreatePeerReviewRequest
  ): Promise<PeerReview> {
    const response = await api.post(`/activities/peer-reviews/${reviewId}/submit`, data)
    return response.data
  },

  // ========== 统计 API ==========

  /**
   * 获取活动统计数据
   */
  async getStatistics(cellId: number): Promise<ActivityStatistics> {
    const response = await api.get(`/activities/cells/${cellId}/statistics`)
    return response.data
  },

  /**
   * 获取题目级统计
   */
  async getItemStatistics(cellId: number): Promise<ActivityItemStatistic[]> {
    const response = await api.get(
      `/activities/cells/${cellId}/item-statistics`
    )
    return response.data
  },

  /**
   * 获取流程图快照
   */
  async getFlowchartSnapshots(
    cellId: number,
    options: { studentId?: number } = {}
  ): Promise<FlowchartSnapshot[]> {
    const params = options.studentId ? { student_id: options.studentId } : undefined
    const response = await api.get(
      `/activities/cells/${cellId}/flowchart-snapshots`,
      { params }
    )
    return response.data
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
    const response = await api.get(
      `/activities/lessons/${lessonId}/formative-assessments`,
      { params }
    )
    return response.data
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
    const response = await api.post(
      `/activities/lessons/${lessonId}/formative-assessments/${studentId}/recompute`,
      undefined,
      { params }
    )
    return response.data
  },

  // ========== 离线同步 API ==========

  /**
   * 同步离线数据
   */
  async syncOfflineData(submissions: any[]): Promise<any> {
    const response = await api.post('/activities/submissions/sync', {
      submissions,
    })
    return response.data
  },

  // ========== 导出数据 API ==========

  /**
   * 导出提交数据
   */
  async exportSubmissions(cellId: number, format: 'csv' | 'xlsx' | 'json' = 'csv'): Promise<Blob> {
    const response = await api.get(`/activities/cells/${cellId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },
}

export default activityService

