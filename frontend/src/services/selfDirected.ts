import { api } from './api'

export type SelfDirectedTutorStyle = 'default' | 'socratic' | 'feynman' | 'confucius'

export interface SelfDirectedPracticeOption {
  key: string
  label: string
}

export interface SelfDirectedPracticeItem {
  id: string
  prompt: string
  type: 'short_answer' | 'multiple_choice'
  rubric: string
  options?: SelfDirectedPracticeOption[]
  correct_option?: string
}

export interface SelfDirectedCurriculumSource {
  id: string
  title: string
  unit?: string
  stage_name?: string
  mathlab_url: string
  goals?: string[]
  hint?: string
}

export interface SelfDirectedLesson {
  title: string
  objective: string
  explanation_md: string
  diagram_mermaid?: string | null
  practice: SelfDirectedPracticeItem[]
  mastery_prompt: string
  reference_card_md: string
  concept_tags: string[]
  curriculum_sources?: SelfDirectedCurriculumSource[]
}

export interface SelfDirectedSession {
  id: number
  student_id: number
  goal_text: string
  mission_why?: string | null
  mission_success?: string | null
  tutor_style: string
  status: 'generating' | 'in_progress' | 'completed' | 'failed' | string
  prior_summary?: string | null
  lesson_json?: SelfDirectedLesson | null
  check_answers_json?: Record<string, any> | null
  vault_lesson_path?: string | null
  error_message?: string | null
  created_at: string
  updated_at: string
  completed_at?: string | null
}

export interface PracticeFeedbackItem {
  id: string
  ok: boolean
  feedback: string
}

function extractErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && typeof detail.detail === 'string') return detail.detail
  return fallback
}

class SelfDirectedService {
  private readonly basePath = '/self-directed'

  async createSession(payload: {
    goal_text: string
    mission_why?: string
    mission_success?: string
    tutor_style?: SelfDirectedTutorStyle
  }): Promise<SelfDirectedSession> {
    try {
      return await api.post<SelfDirectedSession>(`${this.basePath}/sessions`, payload)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '创建学习会话失败'))
    }
  }

  async getSession(sessionId: number): Promise<SelfDirectedSession> {
    try {
      return await api.get<SelfDirectedSession>(`${this.basePath}/sessions/${sessionId}`)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载学习会话失败'))
    }
  }

  async submitPractice(
    sessionId: number,
    answers: { id: string; answer: string }[],
  ): Promise<{ items: PracticeFeedbackItem[] }> {
    try {
      return await api.post<{ items: PracticeFeedbackItem[] }>(
        `${this.basePath}/sessions/${sessionId}/practice`,
        { answers },
      )
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '提交练习失败'))
    }
  }

  async completeSession(
    sessionId: number,
    payload: {
      mastery_answer: string
      practice_answers: { id: string; answer: string }[]
    },
  ): Promise<SelfDirectedSession> {
    try {
      return await api.post<SelfDirectedSession>(
        `${this.basePath}/sessions/${sessionId}/complete`,
        payload,
      )
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '完成本课失败'))
    }
  }
}

export const selfDirectedService = new SelfDirectedService()
export default selfDirectedService
