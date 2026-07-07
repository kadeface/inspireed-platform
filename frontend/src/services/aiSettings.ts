import { api } from './api'
import type { AISettingsResponse, AISettingsUpdateRequest } from '@/types/aiSettings'

function extractErrorMessage(error: any, fallback: string): string {
  return error?.response?.data?.detail || fallback
}

class AISettingsService {
  private readonly basePath = '/admin/ai-settings'

  async getSettings(): Promise<AISettingsResponse> {
    try {
      return await api.get<AISettingsResponse>(this.basePath)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载 AI 配置失败'))
    }
  }

  async updateSettings(payload: AISettingsUpdateRequest): Promise<AISettingsResponse> {
    try {
      return await api.put<AISettingsResponse>(this.basePath, payload)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '保存 AI 配置失败'))
    }
  }
}

export const aiSettingsService = new AISettingsService()
export default aiSettingsService
