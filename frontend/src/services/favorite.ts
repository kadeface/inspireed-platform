/**
 * 收藏服务
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface Favorite {
  id: number
  user_id: number
  lesson_id: number
  created_at: string
}

export interface FavoriteWithLesson extends Favorite {
  lesson_title: string
  lesson_description: string | null
  lesson_cover_image: string | null
  lesson_difficulty: string | null
  lesson_rating: number
}

class FavoriteService {
  private getAuthHeader() {
    const token = localStorage.getItem('token')
    return {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  }

  /**
   * 添加收藏
   */
  async addFavorite(lessonId: number): Promise<Favorite> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/favorites/`,
      { lesson_id: lessonId },
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 取消收藏
   */
  async removeFavorite(lessonId: number): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/api/v1/favorites/${lessonId}`,
      this.getAuthHeader()
    )
  }

  /**
   * 获取我的收藏列表
   */
  async getMyFavorites(): Promise<FavoriteWithLesson[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/favorites/`,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 检查是否已收藏
   */
  async checkFavorite(lessonId: number): Promise<boolean> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/favorites/check/${lessonId}`,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 切换收藏状态
   */
  async toggleFavorite(lessonId: number): Promise<boolean> {
    const isFavorited = await this.checkFavorite(lessonId)
    
    if (isFavorited) {
      await this.removeFavorite(lessonId)
      return false
    } else {
      await this.addFavorite(lessonId)
      return true
    }
  }
}

export const favoriteService = new FavoriteService()

