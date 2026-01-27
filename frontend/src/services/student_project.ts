/**
 * Student Project API 服务
 * 封装所有学生项目相关的 API 调用
 * 使用 snake_case 命名以匹配后端
 */

import { api } from './api'
import type {
  StudentProject,
  StudentProjectCreate,
  StudentProjectUpdate,
  StudentProjectListParams,
  StudentProjectListResponse,
  StageContentUpdate,
} from '../types/student_project'

/**
 * Student Project API 服务类
 */
class StudentProjectService {
  private readonly base_path = '/student/projects'

  /**
   * 获取项目列表
   * @param params 查询参数（分页、状态过滤）
   * @returns 项目列表响应
   */
  async fetch_projects(params?: StudentProjectListParams): Promise<StudentProjectListResponse> {
    try {
      const response = await api.get<StudentProjectListResponse>(this.base_path, {
        params: {
          page: params?.page || 1,
          page_size: params?.page_size || 20,
          status: params?.status,
        },
      })
      return response
    } catch (error: any) {
      console.error('Failed to fetch projects:', error)
      throw new Error(error.response?.data?.detail || '获取项目列表失败')
    }
  }

  /**
   * 根据 ID 获取项目详情
   * @param id 项目 ID
   * @returns 项目详情
   */
  async fetch_project_by_id(id: number): Promise<StudentProject> {
    try {
      const response = await api.get<StudentProject>(`${this.base_path}/${id}`)
      return response
    } catch (error: any) {
      console.error(`Failed to fetch project ${id}:`, error)
      throw new Error(error.response?.data?.detail || '获取项目详情失败')
    }
  }

  /**
   * 创建新项目
   * @param data 项目创建数据
   * @returns 创建的项目
   */
  async create_project(data: StudentProjectCreate): Promise<StudentProject> {
    try {
      const response = await api.post<StudentProject>(this.base_path, data)
      return response
    } catch (error: any) {
      console.error('Failed to create project:', error)
      throw new Error(error.response?.data?.detail || '创建项目失败')
    }
  }

  /**
   * 更新项目
   * @param id 项目 ID
   * @param data 项目更新数据
   * @returns 更新后的项目
   */
  async update_project(id: number, data: StudentProjectUpdate): Promise<StudentProject> {
    try {
      const response = await api.put<StudentProject>(`${this.base_path}/${id}`, data)
      return response
    } catch (error: any) {
      console.error(`Failed to update project ${id}:`, error)
      throw new Error(error.response?.data?.detail || '更新项目失败')
    }
  }

  /**
   * 删除项目
   * @param id 项目 ID
   */
  async delete_project(id: number): Promise<void> {
    try {
      await api.delete(`${this.base_path}/${id}`)
    } catch (error: any) {
      console.error(`Failed to delete project ${id}:`, error)
      throw new Error(error.response?.data?.detail || '删除项目失败')
    }
  }

  /**
   * 更新指定阶段的内容
   * @param id 项目 ID
   * @param stage 阶段名称 (engage, explore, explain, elaborate, evaluate)
   * @param content 阶段内容
   * @returns 更新后的项目
   */
  async update_stage_content(
    id: number,
    stage: string,
    content: any[]
  ): Promise<StudentProject> {
    try {
      const response = await api.put<StudentProject>(
        `${this.base_path}/${id}/stages/${stage}`,
        { content }
      )
      return response
    } catch (error: any) {
      console.error(`Failed to update stage ${stage} for project ${id}:`, error)
      throw new Error(error.response?.data?.detail || '更新阶段内容失败')
    }
  }
}

export const student_project_service = new StudentProjectService()

