/**
 * 评分评论服务
 */
import { api } from './api'

export interface Review {
  id: number
  user_id: number
  lesson_id: number
  rating: number
  comment: string | null
  created_at: string
  updated_at: string
}

export interface ReviewWithUser extends Review {
  user_name: string
  user_avatar: string | null
}

export interface ReviewCreate {
  lesson_id: number
  rating: number
  comment?: string
}

export interface ReviewUpdate {
  rating: number
  comment?: string
}

export interface LessonRatingStats {
  lesson_id: number
  average_rating: number
  review_count: number
  rating_distribution: Record<number, number>
}

class ReviewService {
  /**
   * 创建评论
   */
  async createReview(data: ReviewCreate): Promise<Review> {
    return await api.post<Review>('/reviews/', data)
  }

  /**
   * 更新评论
   */
  async updateReview(reviewId: number, data: ReviewUpdate): Promise<Review> {
    return await api.put<Review>(`/reviews/${reviewId}`, data)
  }

  /**
   * 删除评论
   */
  async deleteReview(reviewId: number): Promise<void> {
    await api.delete(`/reviews/${reviewId}`)
  }

  /**
   * 获取课程的所有评论
   */
  async getLessonReviews(lessonId: number): Promise<ReviewWithUser[]> {
    return await api.get<ReviewWithUser[]>(`/reviews/lesson/${lessonId}`)
  }

  /**
   * 获取课程的评分统计
   */
  async getLessonRatingStats(lessonId: number): Promise<LessonRatingStats> {
    return await api.get<LessonRatingStats>(`/reviews/lesson/${lessonId}/stats`)
  }

  /**
   * 获取我对某课程的评论
   */
  async getMyReview(lessonId: number): Promise<Review | null> {
    return await api.get<Review | null>(`/reviews/my/${lessonId}`)
  }
}

export const reviewService = new ReviewService()

