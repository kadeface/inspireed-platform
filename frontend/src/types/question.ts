/**
 * 问答系统类型定义
 */

// ==================== 枚举类型 ====================

/**
 * 问题状态
 */
export enum QuestionStatus {
  PENDING = 'pending',     // 待回答
  ANSWERED = 'answered',   // 已回答
  RESOLVED = 'resolved',   // 已解决
  CLOSED = 'closed'        // 已关闭
}

/**
 * 提问类型
 */
export enum AskType {
  TEACHER = 'teacher',  // 仅向教师提问
  AI = 'ai',           // 仅向AI提问
  BOTH = 'both'        // 同时向教师和AI提问
}

/**
 * 回答者类型
 */
export enum AnswererType {
  TEACHER = 'teacher',
  AI = 'ai'
}

// ==================== 基础类型 ====================

/**
 * 用户简要信息
 */
export interface UserBrief {
  id: number
  username: string
  full_name?: string
  avatar_url?: string
}

/**
 * 课程简要信息
 */
export interface LessonBrief {
  id: number
  title: string
}

/**
 * Cell简要信息
 */
export interface CellBrief {
  id: number
  cell_type: string
  order: number
}

// ==================== 问题相关 ====================

/**
 * 问题基础接口
 */
export interface QuestionBase {
  title: string
  content: string
  lesson_id: number
  cell_id?: number
  ask_type: AskType
  is_public: boolean
}

/**
 * 创建问题请求
 */
export interface QuestionCreate extends QuestionBase {
}

/**
 * 更新问题请求
 */
export interface QuestionUpdate {
  title?: string
  content?: string
  status?: QuestionStatus
  is_public?: boolean
  is_pinned?: boolean
}

/**
 * 问题完整信息
 */
export interface Question extends QuestionBase {
  id: number
  student_id: number
  status: QuestionStatus
  is_pinned: boolean
  views: number
  upvotes: number
  created_at: string
  updated_at?: string
}

/**
 * 问题列表项（带统计信息）
 */
export interface QuestionListItem extends Question {
  student: UserBrief
  lesson: LessonBrief
  cell?: CellBrief
  answer_count: number
  has_ai_answer: boolean
  has_teacher_answer: boolean
}

/**
 * 问题详情（带回答）
 */
export interface QuestionDetail extends Question {
  student: UserBrief
  lesson: LessonBrief
  cell?: CellBrief
  answers: Answer[]
}

/**
 * 问题列表响应
 */
export interface QuestionListResponse {
  items: QuestionListItem[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

/**
 * 问题统计
 */
export interface QuestionStats {
  total: number
  pending: number
  answered: number
  resolved: number
  closed: number
}

// ==================== 回答相关 ====================

/**
 * 回答基础接口
 */
export interface AnswerBase {
  question_id: number
  content: any[]  // Cell数组，与Lesson.content格式相同
}

/**
 * 创建回答请求
 */
export interface AnswerCreate extends AnswerBase {
}

/**
 * 更新回答请求
 */
export interface AnswerUpdate {
  content?: any[]
  is_accepted?: boolean
}

/**
 * 回答完整信息
 */
export interface Answer extends AnswerBase {
  id: number
  answerer_type: AnswererType
  answerer_id?: number
  ai_model?: string
  ai_prompt_tokens?: number
  ai_completion_tokens?: number
  rating?: number
  is_accepted: boolean
  upvotes: number
  created_at: string
  updated_at?: string
  answerer?: UserBrief
}

// ==================== 点赞和评分 ====================

/**
 * 点赞请求
 */
export interface VoteCreate {
  question_id?: number
  answer_id?: number
}

/**
 * 评分请求
 */
export interface RatingCreate {
  rating: number  // 1-5星
}

// ==================== UI状态 ====================

/**
 * 问题筛选条件
 */
export interface QuestionFilter {
  lesson_id?: number
  status?: QuestionStatus
  sort?: 'recent' | 'popular' | 'upvotes'
  search?: string
}

/**
 * 提问表单数据
 */
export interface QuestionFormData {
  title: string
  content: string
  cell_id?: number
  ask_type: AskType
  is_public: boolean
}

