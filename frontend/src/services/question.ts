/**
 * 问答系统API服务
 */
import { api } from './api'
import type {
  QuestionCreate,
  QuestionUpdate,
  QuestionDetail,
  QuestionListItem,
  QuestionListResponse,
  QuestionStats,
  AnswerCreate,
  AnswerUpdate,
  Answer,
  RatingCreate,
  QuestionStatus
} from '@/types/question'

/**
 * Question API服务类
 */
class QuestionService {
  private readonly basePath = '/questions'

  // ==================== 学生端API ====================

  /**
   * 创建问题（学生）
   * @param data 问题数据
   * @returns 创建的问题详情
   */
  async createQuestion(data: QuestionCreate): Promise<QuestionDetail> {
    try {
      const response = await api.post<QuestionDetail>(this.basePath, data)
      return response
    } catch (error: any) {
      console.error('Failed to create question:', error)
      throw new Error(error.response?.data?.detail || '提交问题失败')
    }
  }

  /**
   * 获取我的问题列表（学生）
   * @param params 查询参数
   * @returns 问题列表
   */
  async getMyQuestions(params?: {
    lesson_id?: number
    status?: QuestionStatus
    page?: number
    page_size?: number
  }): Promise<QuestionListResponse> {
    try {
      const response = await api.get<QuestionListResponse>(`${this.basePath}/my`, { params })
      return response
    } catch (error: any) {
      console.error('Failed to get my questions:', error)
      throw new Error(error.response?.data?.detail || '获取问题列表失败')
    }
  }

  /**
   * 获取课程的所有公开问答
   * @param lessonId 课程ID
   * @param params 查询参数
   * @returns 问题列表
   */
  async getLessonQuestions(
    lessonId: number,
    params?: {
      sort?: 'recent' | 'popular' | 'upvotes'
      page?: number
      page_size?: number
    }
  ): Promise<QuestionListResponse> {
    try {
      const response = await api.get<QuestionListResponse>(
        `${this.basePath}/lesson/${lessonId}`,
        { params }
      )
      return response
    } catch (error: any) {
      console.error('Failed to get lesson questions:', error)
      throw new Error(error.response?.data?.detail || '获取课程问答失败')
    }
  }

  /**
   * 获取问题详情
   * @param id 问题ID
   * @returns 问题详情
   */
  async getQuestionDetail(id: number): Promise<QuestionDetail> {
    try {
      const response = await api.get<QuestionDetail>(`${this.basePath}/${id}`)
      return response
    } catch (error: any) {
      console.error('Failed to get question detail:', error)
      throw new Error(error.response?.data?.detail || '获取问题详情失败')
    }
  }

  /**
   * 标记问题为已解决（学生）
   * @param id 问题ID
   * @returns 更新后的问题
   */
  async resolveQuestion(id: number): Promise<QuestionDetail> {
    try {
      const response = await api.put<QuestionDetail>(`${this.basePath}/${id}/resolve`)
      return response
    } catch (error: any) {
      console.error('Failed to resolve question:', error)
      throw new Error(error.response?.data?.detail || '标记问题失败')
    }
  }

  // ==================== 教师端API ====================

  /**
   * 获取待回答的问题列表（教师）
   * @param params 查询参数
   * @returns 问题列表
   */
  async getTeacherPendingQuestions(params?: {
    lesson_id?: number
    sort?: 'created_at' | 'upvotes'
    page?: number
    page_size?: number
  }): Promise<QuestionListResponse> {
    try {
      const response = await api.get<QuestionListResponse>(
        `${this.basePath}/teacher/pending`,
        { params }
      )
      return response
    } catch (error: any) {
      console.error('Failed to get teacher pending questions:', error)
      throw new Error(error.response?.data?.detail || '获取待回答问题失败')
    }
  }

  /**
   * 获取问题统计（教师）
   * @param lessonId 课程ID（可选）
   * @returns 统计数据
   */
  async getQuestionStats(lessonId?: number): Promise<QuestionStats> {
    try {
      const params = lessonId ? { lesson_id: lessonId } : undefined
      const response = await api.get<QuestionStats>(
        `${this.basePath}/teacher/stats`,
        { params }
      )
      return response
    } catch (error: any) {
      console.error('Failed to get question stats:', error)
      throw new Error(error.response?.data?.detail || '获取统计数据失败')
    }
  }

  /**
   * 置顶/取消置顶问题（教师）
   * @param id 问题ID
   * @returns 更新后的问题
   */
  async pinQuestion(id: number): Promise<QuestionDetail> {
    try {
      const response = await api.put<QuestionDetail>(`${this.basePath}/${id}/pin`)
      return response
    } catch (error: any) {
      console.error('Failed to pin question:', error)
      throw new Error(error.response?.data?.detail || '置顶问题失败')
    }
  }

  // ==================== 回答相关API ====================

  /**
   * 教师回答问题
   * @param data 回答数据（包含Cell数组）
   * @returns 创建的回答
   */
  async createAnswer(data: AnswerCreate): Promise<Answer> {
    try {
      const response = await api.post<Answer>(`${this.basePath}/answers`, data)
      return response
    } catch (error: any) {
      console.error('Failed to create answer:', error)
      throw new Error(error.response?.data?.detail || '提交回答失败')
    }
  }

  /**
   * 更新回答（教师）
   * @param id 回答ID
   * @param data 更新数据
   * @returns 更新后的回答
   */
  async updateAnswer(id: number, data: AnswerUpdate): Promise<Answer> {
    try {
      const response = await api.put<Answer>(`${this.basePath}/answers/${id}`, data)
      return response
    } catch (error: any) {
      console.error('Failed to update answer:', error)
      throw new Error(error.response?.data?.detail || '更新回答失败')
    }
  }

  /**
   * 对回答评分（学生）
   * @param id 回答ID
   * @param rating 评分数据
   * @returns 更新后的回答
   */
  async rateAnswer(id: number, rating: RatingCreate): Promise<Answer> {
    try {
      const response = await api.post<Answer>(
        `${this.basePath}/answers/${id}/rate`,
        rating
      )
      return response
    } catch (error: any) {
      console.error('Failed to rate answer:', error)
      throw new Error(error.response?.data?.detail || '评分失败')
    }
  }
}

// 导出单例
export const questionService = new QuestionService()
export default questionService

