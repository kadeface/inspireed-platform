import { api } from './api'
import type {
  AssistantRequest,
  AssistantResponse,
  TeacherAssistantRequest,
  TeacherAssistantResponse,
} from '@/types/assistant'

class AssistantService {
  private readonly teacherBasePath = '/teacher/assistant'
  private readonly studentBasePath = '/student/assistant'

  async askTeacherAssistant(
    payload: TeacherAssistantRequest
  ): Promise<TeacherAssistantResponse> {
    try {
      return await api.post<TeacherAssistantResponse>(
        `${this.teacherBasePath}/query`,
        payload
      )
    } catch (error: any) {
      console.error('Teacher assistant request failed:', error)
      throw new Error(error.response?.data?.detail || 'AI 助手服务暂不可用')
    }
  }

  async askStudentAssistant(
    payload: AssistantRequest
  ): Promise<AssistantResponse> {
    try {
      return await api.post<AssistantResponse>(
        `${this.studentBasePath}/query`,
        payload
      )
    } catch (error: any) {
      console.error('Student assistant request failed:', error)
      throw new Error(error.response?.data?.detail || 'AI 助手服务暂不可用')
    }
  }
}

export const assistantService = new AssistantService()
export default assistantService

