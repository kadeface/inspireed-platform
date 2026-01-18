/**
 * 年级考试科目配置 API 服务
 */
import api from './api'

export interface GradeSubjectConfig {
  id: number
  grade_id: number
  subject_id: number
  full_score: number
  pass_line: number
  excellent_line: number
  good_line: number
  is_active: boolean
  display_order: number
  description?: string
  created_at: string
  updated_at: string
  created_by?: number
  grade_name?: string
  subject_name?: string
  subject_code?: string
}

export interface GradeSubjectsWithScores {
  grade_id: number
  grade_name: string
  grade_level: number
  subjects: GradeSubjectConfig[]
}

export interface GradeSubjectConfigCreate {
  grade_id: number
  subject_id: number
  full_score?: number
  pass_line?: number
  excellent_line?: number
  good_line?: number
  display_order?: number
  description?: string
}

export const examSubjectsService = {
  /**
   * 获取年级考试科目配置列表
   */
  async getGradeSubjectConfigs(params?: {
    grade_id?: number
    subject_id?: number
    is_active?: boolean
  }): Promise<GradeSubjectConfig[]> {
    return await api.get('/grade-subject-configs', { params })
  },

  /**
   * 获取某个年级的所有考试科目配置
   */
  async getGradeSubjects(gradeId: number): Promise<GradeSubjectsWithScores> {
    return await api.get(`/grade-subject-configs/by-grade/${gradeId}`)
  },

  /**
   * 创建年级考试科目配置
   */
  async createGradeSubjectConfig(
    data: GradeSubjectConfigCreate
  ): Promise<GradeSubjectConfig> {
    return await api.post('/grade-subject-configs', data)
  },

  /**
   * 批量创建年级考试科目配置
   */
  async bulkCreateGradeSubjectConfigs(
    configs: GradeSubjectConfigCreate[]
  ): Promise<GradeSubjectConfig[]> {
    return await api.post('/grade-subject-configs/bulk', { configs })
  },

  /**
   * 更新年级考试科目配置
   */
  async updateGradeSubjectConfig(
    configId: number,
    data: Partial<GradeSubjectConfigCreate> & {
      is_active?: boolean
    }
  ): Promise<GradeSubjectConfig> {
    return await api.put(`/grade-subject-configs/${configId}`, data)
  },

  /**
   * 删除年级考试科目配置
   */
  async deleteGradeSubjectConfig(configId: number): Promise<void> {
    return await api.delete(`/grade-subject-configs/${configId}`)
  },

  /**
   * 启用/禁用年级考试科目配置
   */
  async toggleGradeSubjectConfig(
    configId: number,
    isActive: boolean
  ): Promise<GradeSubjectConfig> {
    return await api.patch(`/grade-subject-configs/${configId}/toggle`, null, {
      params: { is_active: isActive }
    })
  },
}

export default examSubjectsService
