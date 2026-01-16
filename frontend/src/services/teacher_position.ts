/**
 * 教师职务类型API服务
 */

import api from './api'
import type {
  TeacherPositionTypeCreate,
  TeacherPositionTypeUpdate,
  TeacherPositionTypeResponse,
  TeacherPositionTypeListResponse,
} from '@/types/teacher_position'

export const teacherPositionApi = {
  /**
   * 创建职务类型
   */
  async createPositionType(
    data: TeacherPositionTypeCreate
  ): Promise<TeacherPositionTypeResponse> {
    return await api.post('/teacher-positions/', data)
  },

  /**
   * 获取职务类型列表
   */
  async getPositionTypes(params?: {
    category?: string
    is_active?: boolean
    search?: string
  }): Promise<TeacherPositionTypeListResponse> {
    return await api.get('/teacher-positions/', { params })
  },

  /**
   * 获取单个职务类型
   */
  async getPositionType(
    positionTypeId: number
  ): Promise<TeacherPositionTypeResponse> {
    return await api.get(`/teacher-positions/${positionTypeId}`)
  },

  /**
   * 更新职务类型
   */
  async updatePositionType(
    positionTypeId: number,
    data: TeacherPositionTypeUpdate
  ): Promise<TeacherPositionTypeResponse> {
    return await api.put(`/teacher-positions/${positionTypeId}`, data)
  },

  /**
   * 删除职务类型
   */
  async deletePositionType(positionTypeId: number): Promise<void> {
    return await api.delete(`/teacher-positions/${positionTypeId}`)
  },
}
