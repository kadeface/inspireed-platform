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
      console.log('📤 Sending AI Assistant request:', {
        path: `${this.teacherBasePath}/query`,
        hasAgentPrompt: !!payload.context?.agent_prompt,
        questionLength: payload.question?.length,
        topic: payload.topic,
      })
      
      const response = await api.post<TeacherAssistantResponse>(
        `${this.teacherBasePath}/query`,
        payload
      )
      
      console.log('📥 AI Assistant response received:', {
        model: response.model_used,
        confidence: response.confidence,
        answerLength: response.answer?.length,
      })
      
      return response
    } catch (error: any) {
      console.error('❌ Teacher assistant request failed:', {
        error,
        errorType: error?.constructor?.name,
        errorMessage: error?.message,
        responseStatus: error?.response?.status,
        responseData: error?.response?.data,
        requestUrl: error?.config?.url,
        requestMethod: error?.config?.method,
      })
      
      // 保留原始错误信息，让调用方处理
      throw error
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

