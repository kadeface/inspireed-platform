/**
 * 收藏服务
 */
import { api } from './api'

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
  /**
   * 添加收藏
   */
  async addFavorite(lessonId: number): Promise<Favorite> {
    return await api.post<Favorite>('/favorites/', { lesson_id: lessonId })
  }

  /**
   * 取消收藏
   */
  async removeFavorite(lessonId: number): Promise<void> {
    await api.delete(`/favorites/${lessonId}`)
  }

  /**
   * 获取我的收藏列表
   */
  async getMyFavorites(): Promise<FavoriteWithLesson[]> {
    return await api.get<FavoriteWithLesson[]>('/favorites/')
  }

  /**
   * 检查是否已收藏
   */
  async checkFavorite(lessonId: number): Promise<boolean> {
    return await api.get<boolean>(`/favorites/check/${lessonId}`)
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

