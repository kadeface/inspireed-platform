import type { QuestionStats } from './question'
import type { SubjectGroupStatistics } from './subjectGroup'

export type AssistantTopic = 'pdca' | 'lesson_plan' | 'qa' | 'study_support'

export type TeacherAssistantTopic = Extract<
  AssistantTopic,
  'pdca' | 'lesson_plan' | 'qa'
>

export interface AssistantLessonSnapshot {
  id: number
  title: string
  status?: string
  updated_at?: string
}

export interface AssistantContextPayload {
  lesson_summary?: Record<string, number>
  question_stats?: QuestionStats
  subject_group_stats?: SubjectGroupStatistics
  recent_lessons?: AssistantLessonSnapshot[]
  lesson_outline?: string
  progress?: number
}

export interface AssistantRequest {
  question: string
  topic?: AssistantTopic
  lesson_id?: number
  context?: AssistantContextPayload
}

export interface AssistantInsight {
  title: string
  detail: string
  metric?: string
}

export interface AssistantAction {
  label: string
  description?: string
}

export interface AssistantResponse {
  answer: string
  insights: AssistantInsight[]
  suggested_actions: AssistantAction[]
  follow_up_questions: string[]
  model_used?: string
  confidence?: number
  response_time_ms?: number
  context_used?: string[]
}

export type TeacherAssistantRequest = AssistantRequest
export type TeacherAssistantResponse = AssistantResponse
export type TeacherAssistantInsight = AssistantInsight
export type TeacherAssistantAction = AssistantAction
export type TeacherAssistantContextPayload = AssistantContextPayload
export type TeacherAssistantLessonSnapshot = AssistantLessonSnapshot
