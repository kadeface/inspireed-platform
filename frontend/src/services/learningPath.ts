/**
 * 学习路径服务
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface LearningPathLesson {
  id: number
  learning_path_id: number
  lesson_id: number
  order_index: number
  is_required: boolean
  created_at: string
  lesson_title?: string
  lesson_description?: string | null
  lesson_cover_image?: string | null
  lesson_difficulty?: string | null
  lesson_rating?: number
  lesson_duration?: number | null
}

export interface LearningPath {
  id: number
  title: string
  description: string | null
  creator_id: number
  difficulty_level: string
  cover_image_url: string | null
  is_published: boolean
  estimated_hours: number | null
  created_at: string
  updated_at: string
}

export interface LearningPathWithLessons extends LearningPath {
  lessons: LearningPathLesson[]
  lesson_count: number
  creator_name: string
}

export interface LearningPathListItem extends LearningPath {
  lesson_count: number
  creator_name: string
}

export interface LearningPathCreate {
  title: string
  description?: string
  difficulty_level?: string
  cover_image_url?: string
  estimated_hours?: number
  lessons?: Array<{
    lesson_id: number
    order_index: number
    is_required?: boolean
  }>
}

export interface LearningPathUpdate {
  title?: string
  description?: string
  difficulty_level?: string
  cover_image_url?: string
  estimated_hours?: number
  is_published?: boolean
}

class LearningPathService {
  private getAuthHeader() {
    const token = localStorage.getItem('token')
    return {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  }

  /**
   * 创建学习路径（教师/研究员）
   */
  async createLearningPath(data: LearningPathCreate): Promise<LearningPath> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/learning-paths/`,
      data,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 更新学习路径
   */
  async updateLearningPath(pathId: number, data: LearningPathUpdate): Promise<LearningPath> {
    const response = await axios.put(
      `${API_BASE_URL}/api/v1/learning-paths/${pathId}`,
      data,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 删除学习路径
   */
  async deleteLearningPath(pathId: number): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/api/v1/learning-paths/${pathId}`,
      this.getAuthHeader()
    )
  }

  /**
   * 获取学习路径列表
   */
  async getLearningPaths(publishedOnly: boolean = true): Promise<LearningPathListItem[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/learning-paths/`,
      {
        ...this.getAuthHeader(),
        params: { published_only: publishedOnly }
      }
    )
    return response.data
  }

  /**
   * 获取学习路径详情
   */
  async getLearningPath(pathId: number): Promise<LearningPathWithLessons> {
    const response = await axios.get(
      `${API_BASE_URL}/api/v1/learning-paths/${pathId}`,
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 向学习路径添加课程
   */
  async addLessonToPath(
    pathId: number,
    lessonId: number,
    orderIndex: number,
    isRequired: boolean = true
  ): Promise<LearningPathLesson> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/learning-paths/${pathId}/lessons`,
      {
        lesson_id: lessonId,
        order_index: orderIndex,
        is_required: isRequired
      },
      this.getAuthHeader()
    )
    return response.data
  }

  /**
   * 从学习路径移除课程
   */
  async removeLessonFromPath(pathId: number, lessonId: number): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/api/v1/learning-paths/${pathId}/lessons/${lessonId}`,
      this.getAuthHeader()
    )
  }
}

export const learningPathService = new LearningPathService()

