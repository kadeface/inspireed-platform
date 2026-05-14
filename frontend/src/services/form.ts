/**
 * Form Service - 互动表单API服务
 */

import { createLogger } from '../utils/logger'
import apiClient from './api'

const logger = createLogger('FormService')

import type {
  FormCell,
  FormCellCreate,
  FormCellUpdate,
  FormResponse,
  FormResponseCreate,
  FormResults,
} from '../types/form'

/**
 * Form Service
 */
export class FormService {
  /**
   * 创建表单
   */
  async createForm(data: FormCellCreate): Promise<FormCell> {
    logger.debug('创建表单', data)
    const response = await apiClient.post<FormCell>('/forms/', data)
    return response.data
  }

  /**
   * 获取表单详情
   */
  async getForm(formCellId: number): Promise<FormCell> {
    logger.debug('获取表单', formCellId)
    const response = await apiClient.get<FormCell>(`/forms/${formCellId}`)
    return response.data
  }

  /**
   * 更新表单
   */
  async updateForm(formCellId: number, data: FormCellUpdate): Promise<FormCell> {
    logger.debug('更新表单', formCellId, data)
    const response = await apiClient.put<FormCell>(`/forms/${formCellId}`, data)
    return response.data
  }

  /**
   * 删除表单
   */
  async deleteForm(formCellId: number): Promise<void> {
    logger.debug('删除表单', formCellId)
    await apiClient.delete(`/forms/${formCellId}`)
  }

  /**
   * 提交答案
   */
  async submitResponse(
    formCellId: number,
    data: FormResponseCreate
  ): Promise<FormResponse> {
    logger.debug('提交答案', formCellId, data)
    const response = await apiClient.post<FormResponse>(
      `/forms/${formCellId}/submit`,
      data
    )
    return response.data
  }

  /**
   * 获取结果统计
   */
  async getResults(formCellId: number): Promise<FormResults> {
    logger.debug('获取结果', formCellId)
    const response = await apiClient.get<FormResults>(`/forms/${formCellId}/results`)
    return response.data
  }
}

// 单例
export const formService = new FormService()
