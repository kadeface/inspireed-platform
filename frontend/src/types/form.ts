/**
 * Form Cell Types - 互动表单类型定义
 */

import type { Cell } from './cell'

// 表单类型
export type FormType = 'single_choice' | 'multiple_choice' | 'ranking'

// 表单选项
export interface FormOption {
  id?: string
  text: string
  order: number
  image_url?: string | null
}

// 表单设置
export interface FormSettings {
  anonymous?: boolean // 匿名模式
  allow_change?: boolean // 允许修改答案
  show_results?: boolean // 显示结果
  auto_stop?: boolean // 自动停止
}

// 表单单元格（扩展自Cell）
export interface FormCell extends Cell {
  cell_type: 'FORM'
  title: string | null
  description: string | null
  options: FormOption[]
  settings: FormSettings
  time_limit: number | null
  created_by: number
  created_at: string
  updated_at: string
}

// 创建表单请求
export interface FormCellCreate {
  cell_type: FormType
  title: string
  description?: string
  options: FormOptionCreate[]
  settings?: FormSettings
  time_limit?: number
}

// 创建选项请求
export interface FormOptionCreate {
  text: string
  order?: number
  image_url?: string
}

// 更新表单请求
export interface FormCellUpdate {
  cell_type?: FormType
  title?: string
  description?: string
  options?: FormOptionCreate[]
  settings?: FormSettings
  time_limit?: number
}

// 表单响应
export interface FormResponse {
  id: number
  form_cell_id: number
  answers: Answer[]
  submitted_at: string
  session_id?: number
  user_id?: number
}

// 答案
export interface Answer {
  option_id: string
  order?: number // 用于排序题
}

// 提交答案请求
export interface FormResponseCreate {
  answers: Answer[]
  session_id?: number
  user_id?: number
}

// 表单结果统计
export interface FormResults {
  form_cell_id: number
  total_responses: number
  option_stats: OptionStats[]
  response_rate: number
}

// 选项统计
export interface OptionStats {
  option_id: string
  text: string
  count?: number
  percentage?: number
  average_rank?: number // 用于排序题
}

// WebSocket 消息类型
export type FormWSMessageType =
  | 'connection_established'
  | 'form_started'
  | 'form_stopped'
  | 'submit_success'
  | 'new_response'
  | 'results_update'
  | 'error'

// WebSocket 消息
export interface FormWSMessage {
  type: FormWSMessageType
  form_cell_id: number
  user_id?: number
  role?: string
  is_active?: boolean
  total_responses?: number
  detail?: string
  timestamp?: string
}

// 表单房间状态
export interface FormRoomState {
  is_active: boolean
  participants: Set<number>
  response_count: number
}
