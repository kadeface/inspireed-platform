import { api } from './api'
import type {
  SelfStudyHandoffCreateResponse,
  SelfStudyHistoryResponse,
  SelfStudySession,
  SelfStudyTeacherHandoffDetail,
  SelfStudyTeacherHandoffListResponse,
  SelfStudyTeacherHandoffReplyResponse,
  SelfStudyUploadCheckResponse,
} from '@/types/selfStudy'

function extractErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && typeof detail.detail === 'string') return detail.detail
  return fallback
}

class SelfStudyService {
  private readonly basePath = '/self-study'

  async checkUpload(file: File, source: 'upload' | 'paste' = 'upload'): Promise<SelfStudyUploadCheckResponse> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('source', source)
    try {
      return await api.post<SelfStudyUploadCheckResponse>(`${this.basePath}/uploads/check`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } catch (error: any) {
      const detail = error?.response?.data?.detail
      if (detail && typeof detail === 'object') {
        const normalized = new Error(detail.detail || '图片检查失败')
        ;(normalized as any).error_code = detail.error_code
        ;(normalized as any).suggestions = detail.suggestions || []
        throw normalized
      }
      throw new Error(extractErrorMessage(error, '图片检查失败'))
    }
  }

  async createSession(payload: {
    upload_token: string
    voice_transcript_raw?: string
    question_text_confirmed: string
    input_mode: 'voice' | 'text'
  }): Promise<SelfStudySession> {
    try {
      return await api.post<SelfStudySession>(`${this.basePath}/sessions`, payload)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '创建会话失败'))
    }
  }

  async getSession(sessionId: number): Promise<SelfStudySession> {
    try {
      return await api.get<SelfStudySession>(`${this.basePath}/sessions/${sessionId}`)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载会话失败'))
    }
  }

  async appendTurn(
    sessionId: number,
    payload: {
      voice_transcript_raw?: string
      question_text_confirmed: string
      input_mode: 'voice' | 'text'
    }
  ): Promise<SelfStudySession> {
    try {
      return await api.post<SelfStudySession>(`${this.basePath}/sessions/${sessionId}/turns`, payload)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '发送提问失败'))
    }
  }

  async reuploadRevision(
    sessionId: number,
    file: File,
    payload?: {
      voice_transcript_raw?: string
      question_text_confirmed?: string
    }
  ): Promise<SelfStudySession> {
    const formData = new FormData()
    formData.append('file', file)
    if (payload?.voice_transcript_raw) formData.append('voice_transcript_raw', payload.voice_transcript_raw)
    if (payload?.question_text_confirmed) formData.append('question_text_confirmed', payload.question_text_confirmed)
    try {
      return await api.post<SelfStudySession>(`${this.basePath}/sessions/${sessionId}/reupload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '重新上传失败'))
    }
  }

  async unlockExplanation(sessionId: number): Promise<SelfStudySession> {
    try {
      return await api.post<SelfStudySession>(`${this.basePath}/sessions/${sessionId}/unlock-explanation`)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '解锁标准解释失败'))
    }
  }

  async createHandoff(
    sessionId: number,
    student_last_confusion: string
  ): Promise<SelfStudyHandoffCreateResponse> {
    try {
      return await api.post<SelfStudyHandoffCreateResponse>(`${this.basePath}/sessions/${sessionId}/handoff`, {
        student_last_confusion,
      })
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '转交老师失败'))
    }
  }

  async completeSession(
    sessionId: number,
    payload: {
      summary_before: string
      summary_after: string
    }
  ): Promise<SelfStudySession> {
    try {
      return await api.post<SelfStudySession>(`${this.basePath}/sessions/${sessionId}/complete`, payload)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '保存总结失败'))
    }
  }

  async listHistory(params?: {
    page?: number
    page_size?: number
    result_judgment?: string
    session_phase?: string
  }): Promise<SelfStudyHistoryResponse> {
    try {
      return await api.get<SelfStudyHistoryResponse>(`${this.basePath}/student/history`, { params })
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载学习记录失败'))
    }
  }

  async listTeacherHandoffs(params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<SelfStudyTeacherHandoffListResponse> {
    try {
      return await api.get<SelfStudyTeacherHandoffListResponse>(`${this.basePath}/teacher/handoffs`, { params })
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载教师处理队列失败'))
    }
  }

  async getTeacherHandoff(handoffId: number): Promise<SelfStudyTeacherHandoffDetail> {
    try {
      return await api.get<SelfStudyTeacherHandoffDetail>(`${this.basePath}/teacher/handoffs/${handoffId}`)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载教师处理详情失败'))
    }
  }

  async replyTeacherHandoff(
    handoffId: number,
    payload: {
      reply_text: string
      annotated_image_storage_key?: string
    }
  ): Promise<SelfStudyTeacherHandoffReplyResponse> {
    try {
      return await api.post<SelfStudyTeacherHandoffReplyResponse>(
        `${this.basePath}/teacher/handoffs/${handoffId}/reply`,
        payload
      )
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '提交教师回复失败'))
    }
  }

  async uploadAnnotatedImage(file: File): Promise<string> {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await api.post<{ file_url: string }>('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const segments = response.file_url.split('/')
      return segments[segments.length - 1]
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '上传标注图片失败'))
    }
  }
}

export const selfStudyService = new SelfStudyService()
export default selfStudyService
