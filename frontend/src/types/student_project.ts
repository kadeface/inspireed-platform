/**
 * Student Project Types
 * All field names use snake_case to match backend API
 */

export const ProjectStatus = {
  DRAFT: 'draft',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  SUBMITTED: 'submitted',
} as const

export type ProjectStatus = typeof ProjectStatus[keyof typeof ProjectStatus]

export const ProjectStage = {
  ENGAGE: 'engage',
  EXPLORE: 'explore',
  EXPLAIN: 'explain',
  ELABORATE: 'elaborate',
  EVALUATE: 'evaluate',
} as const

export type ProjectStage = typeof ProjectStage[keyof typeof ProjectStage]

export interface ProjectCell {
  id?: number
  project_id?: number
  stage: ProjectStage
  cell_type: string
  title?: string
  content: any
  config?: any
  order: number
  created_at?: string
  updated_at?: string
}

export interface StudentProject {
  id: number
  title: string
  description?: string
  creator_id: number
  creator_name?: string
  project_type?: string
  status: ProjectStatus
  
  // 5E stage content
  engage_content: ProjectCell[]
  explore_content: ProjectCell[]
  explain_content: ProjectCell[]
  elaborate_content: ProjectCell[]
  evaluate_content: ProjectCell[]
  
  completion: {
    engage: number
    explore: number
    explain: number
    elaborate: number
    evaluate: number
  }
  
  cover_image_url?: string
  tags: string[]
  is_team_project: boolean
  team_members: number[]
  
  created_at: string
  updated_at: string
  submitted_at?: string
}

export interface StudentProjectCreate {
  title: string
  description?: string
  project_type?: string
}

export interface StudentProjectUpdate {
  title?: string
  description?: string
  status?: ProjectStatus
  cover_image_url?: string
  tags?: string[]
  engage_content?: any[]
  explore_content?: any[]
  explain_content?: any[]
  elaborate_content?: any[]
  evaluate_content?: any[]
}

export interface StudentProjectListParams {
  page?: number
  page_size?: number
  status?: ProjectStatus
}

export interface StudentProjectListResponse {
  items: StudentProject[]
  total: number
  page: number
  page_size: number
}

export interface StageContentUpdate {
  content: any[]
}

