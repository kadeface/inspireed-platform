/**
 * 评分评论服务
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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
  private getAuthHeader() {
    const token = localStorage.getItem('token')
    return {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  }

  /**
   * 创建评论
   */
  async createReview(data: ReviewCreate): Promise<Review> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/reviews/`,
      data,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 更新评论
   */
  async updateReview(reviewId: number, data: ReviewUpdate): Promise<Review> {
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/reviews/${reviewId}`,
      data,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 删除评论
   */
  async deleteReview(reviewId: number): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/api/v1/reviews/${reviewId}`,
      this.getAuthHeader()
    )
  }

  /**
   * 获取课程的所有评论
   */
  async getLessonReviews(lessonId: number): Promise<ReviewWithUser[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/reviews/lesson/${lessonId}`,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 获取课程的评分统计
   */
  async getLessonRatingStats(lessonId: number): Promise<LessonRatingStats> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/reviews/lesson/${lessonId}/stats`,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 获取我对某课程的评论
   */
  async getMyReview(lessonId: number): Promise<Review | null> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/reviews/my/${lessonId}`,
      this.getAuthHeader()
    )
    return response.data
  }
}

export const reviewService = new ReviewService()

