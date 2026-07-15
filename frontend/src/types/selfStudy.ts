export type SelfStudySessionPhase =
  | 'awaiting_question'
  | 'guiding'
  | 'awaiting_reupload'
  | 'explanation_unlocked'
  | 'handed_off'
  | 'completed'

export type SelfStudyResultJudgment =
  | 'incorrect'
  | 'correct_unexplained'
  | 'understood'
  | 'needs_teacher'

export type SelfStudyTurnKind =
  | 'question'
  | 'probe'
  | 'hint'
  | 'explanation'
  | 'summary'

export type SelfStudySpeaker = 'student' | 'ai' | 'system'

export type SelfStudyTutorStyle = 'default' | 'socratic' | 'feynman' | 'confucius'

export interface SelfStudyUploadCheckResponse {
  accepted: boolean
  upload_token?: string
  storage_key?: string
  file_url?: string
  problem_text_preview?: string | null
  student_work_text_preview?: string | null
  message?: string | null
}

export interface SelfStudyCurrentAIMessage {
  turn_index: number
  turn_kind: SelfStudyTurnKind
  content_text: string
}

export interface SelfStudyTurn {
  turn_index: number
  speaker: SelfStudySpeaker
  turn_kind: SelfStudyTurnKind
  content_text: string
  meta_json?: Record<string, any> | null
  created_at?: string
}

export interface SelfStudySession {
  id: number
  student_id: number
  mode: string
  subject: string
  grade_band: string
  tutor_style?: SelfStudyTutorStyle
  original_image_url: string
  revised_image_url?: string | null
  problem_text?: string | null
  student_work_text?: string | null
  session_phase: SelfStudySessionPhase
  result_judgment?: SelfStudyResultJudgment | null
  primary_error_type?: string | null
  guidance_round_count: number
  explanation_unlocked: boolean
  can_view_explanation: boolean
  can_handoff_to_teacher: boolean
  teacher_handoff_status?: 'pending' | 'answered' | 'closed' | null
  teacher_reply_text?: string | null
  teacher_reply_image_url?: string | null
  summary_before?: string | null
  summary_after?: string | null
  current_ai_message?: SelfStudyCurrentAIMessage | null
  turns: SelfStudyTurn[]
  created_at: string
  updated_at: string
}

export interface SelfStudyHistoryItem {
  id: number
  subject: string
  grade_band: string
  thumbnail_url: string
  result_judgment?: SelfStudyResultJudgment | null
  session_phase: SelfStudySessionPhase
  created_at: string
}

export interface SelfStudyHistoryResponse {
  items: SelfStudyHistoryItem[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface SelfStudyHandoffCreateResponse {
  handoff_id: number
  session_id: number
  status: 'pending' | 'answered' | 'closed'
  teacher_reply_expected: boolean
  created_at: string
}

export interface SelfStudyTeacherHandoffListItem {
  id: number
  session_id: number
  student_id: number
  student_name: string
  status: 'pending' | 'answered' | 'closed'
  title: string
  created_at: string
}

export interface SelfStudyTeacherHandoffListResponse {
  items: SelfStudyTeacherHandoffListItem[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface SelfStudyTeacherHandoffDetail {
  id: number
  session_id: number
  student_id: number
  student_name: string
  status: 'pending' | 'answered' | 'closed'
  title: string
  original_image_url: string
  revised_image_url?: string | null
  voice_transcript_raw?: string | null
  question_text_confirmed?: string | null
  ai_guidance_summary: string[]
  student_last_confusion?: string | null
  summary_before?: string | null
  summary_after?: string | null
  teacher_reply_text?: string | null
  teacher_reply_image_url?: string | null
  created_at: string
  answered_at?: string | null
}

export interface SelfStudyTeacherHandoffReplyResponse {
  id: number
  status: 'pending' | 'answered' | 'closed'
  teacher_reply: {
    reply_text: string
    annotated_image_url?: string | null
    answered_at?: string | null
  }
}
