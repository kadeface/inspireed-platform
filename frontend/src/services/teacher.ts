/**
 * 教师教学任务管理 API 服务
 */

import api from './api'
import type {
  TeacherTeachingAssignment,
  TeacherTeachingAssignmentCreate,
  TeacherTeachingAssignmentUpdate,
  TeacherTeachingAssignmentListResponse,
  TeacherTeachingAssignmentQueryParams,
  TeacherAssignmentImportResponse,
} from '@/types/teacher'

export const teacherApi = {
  /**
   * 创建教学任务
   */
  async createAssignment(
    data: TeacherTeachingAssignmentCreate
  ): Promise<TeacherTeachingAssignment> {
    return await api.post('/teachers/assignments', data)
  },

  /**
   * 获取教学任务列表
   */
  async getAssignments(
    params: TeacherTeachingAssignmentQueryParams = {}
  ): Promise<TeacherTeachingAssignmentListResponse> {
    return await api.get('/teachers/assignments', { params })
  },

  /**
   * 获取单个教学任务
   */
  async getAssignment(id: number): Promise<TeacherTeachingAssignment> {
    return await api.get(`/teachers/assignments/${id}`)
  },

  /**
   * 更新教学任务
   */
  async updateAssignment(
    id: number,
    data: TeacherTeachingAssignmentUpdate
  ): Promise<TeacherTeachingAssignment> {
    return await api.put(`/teachers/assignments/${id}`, data)
  },

  /**
   * 删除教学任务
   */
  async deleteAssignment(id: number): Promise<void> {
    return await api.delete(`/teachers/assignments/${id}`)
  },

  /**
   * 获取某教师的所有教学任务
   */
  async getTeacherAssignments(
    teacherId: number,
    semesterId?: number,
    isActive?: boolean
  ): Promise<TeacherTeachingAssignmentListResponse> {
    return await api.get(`/teachers/${teacherId}/assignments`, {
      params: {
        semester_id: semesterId,
        is_active: isActive,
      },
    })
  },

  /**
   * 批量导入教学任务
   */
  async importAssignments(
    file: File,
    updateExisting: boolean = false,
    autoCreateTeachers: boolean = false,
    autoCreateSemesters: boolean = false
  ): Promise<TeacherAssignmentImportResponse> {
    const formData = new FormData()
    formData.append('file', file)
    return await api.post('/teachers/assignments/import', formData, {
      params: {
        update_existing: updateExisting,
        auto_create_teachers: autoCreateTeachers,
        auto_create_semesters: autoCreateSemesters,
      },
    })
  },
}

export default teacherApi
