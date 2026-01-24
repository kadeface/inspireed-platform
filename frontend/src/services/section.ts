/**
 * Section（大环节）API 服务
 * 封装所有大环节相关的 API 调用
 */

import { api } from './api'
import type {
  Section,
  SectionCreate,
  SectionUpdate,
  SectionMove,
  CellMoveRequest,
} from '../types/section'

/**
 * Section API 服务类
 */
class SectionService {
  private readonly basePath = '/lessons'

  /**
   * 获取教案的所有大环节列表（包含 Cells）
   */
  async fetchSections(lessonId: number): Promise<Section[]> {
    try {
      const response = await api.get<Section[]>(`${this.basePath}/${lessonId}/sections`)
      return response
    } catch (error: any) {
      console.error('Failed to fetch sections:', error)
      throw new Error(error.response?.data?.detail || '获取大环节列表失败')
    }
  }

  /**
   * 创建大环节
   */
  async createSection(lessonId: number, data: SectionCreate): Promise<Section> {
    try {
      const response = await api.post<Section>(`${this.basePath}/${lessonId}/sections`, {
        ...data,
        lesson_id: lessonId,
      })
      return response
    } catch (error: any) {
      console.error('Failed to create section:', error)
      throw new Error(error.response?.data?.detail || '创建大环节失败')
    }
  }

  /**
   * 获取大环节详情
   */
  async getSection(sectionId: number): Promise<Section> {
    try {
      const response = await api.get<Section>(`/sections/${sectionId}`)
      return response
    } catch (error: any) {
      console.error('Failed to get section:', error)
      throw new Error(error.response?.data?.detail || '获取大环节详情失败')
    }
  }

  /**
   * 更新大环节
   */
  async updateSection(sectionId: number, data: SectionUpdate): Promise<Section> {
    try {
      const response = await api.put<Section>(`/sections/${sectionId}`, data)
      return response
    } catch (error: any) {
      console.error('Failed to update section:', error)
      throw new Error(error.response?.data?.detail || '更新大环节失败')
    }
  }

  /**
   * 删除大环节
   */
  async deleteSection(sectionId: number): Promise<void> {
    try {
      await api.delete(`/sections/${sectionId}`)
    } catch (error: any) {
      console.error('Failed to delete section:', error)
      throw new Error(error.response?.data?.detail || '删除大环节失败')
    }
  }

  /**
   * 移动大环节（调整顺序）
   */
  async moveSection(sectionId: number, data: SectionMove): Promise<Section> {
    try {
      const response = await api.post<Section>(`/sections/${sectionId}/move`, data)
      return response
    } catch (error: any) {
      console.error('Failed to move section:', error)
      throw new Error(error.response?.data?.detail || '移动大环节失败')
    }
  }

  /**
   * 移动 Cell 到指定大环节
   */
  async moveCellToSection(cellId: number, data: CellMoveRequest): Promise<void> {
    try {
      await api.post(`/cells/${cellId}/move`, data)
    } catch (error: any) {
      console.error('Failed to move cell:', error)
      throw new Error(error.response?.data?.detail || '移动 Cell 失败')
    }
  }

  /**
   * 迁移教案到默认大环节结构
   */
  async migrateLessonToSections(lessonId: number): Promise<{
    message: string
    sections_created: number
    cells_migrated: number
  }> {
    try {
      const response = await api.post<{
        message: string
        sections_created: number
        cells_migrated: number
      }>(`${this.basePath}/${lessonId}/migrate-sections`)
      return response
    } catch (error: any) {
      console.error('Failed to migrate lesson:', error)
      throw new Error(error.response?.data?.detail || '迁移教案失败')
    }
  }
}

export const sectionService = new SectionService()
