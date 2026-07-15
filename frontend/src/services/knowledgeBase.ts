import { api } from './api'

export interface KnowledgeBaseNoteItem {
  path: string
  title: string
  size: number
  updated_at: string
}

export interface KnowledgeBaseNoteListResponse {
  items: KnowledgeBaseNoteItem[]
  total: number
  root_exists: boolean
}

export interface KnowledgeBaseNoteContent {
  path: string
  title: string
  content_markdown: string
}

export interface KnowledgeBasePriorResponse {
  query: string
  prior_summary: string
  has_prior: boolean
}

function extractErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && typeof detail.detail === 'string') return detail.detail
  return fallback
}

class KnowledgeBaseService {
  private readonly basePath = '/knowledge-base'

  async listNotes(): Promise<KnowledgeBaseNoteListResponse> {
    try {
      return await api.get<KnowledgeBaseNoteListResponse>(`${this.basePath}/notes`)
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载知识库失败'))
    }
  }

  async getNote(path: string): Promise<KnowledgeBaseNoteContent> {
    try {
      return await api.get<KnowledgeBaseNoteContent>(`${this.basePath}/notes/content`, {
        params: { path },
      })
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '加载笔记失败'))
    }
  }

  async getPrior(query: string): Promise<KnowledgeBasePriorResponse> {
    try {
      return await api.get<KnowledgeBasePriorResponse>(`${this.basePath}/prior`, {
        params: { q: query },
      })
    } catch (error: any) {
      throw new Error(extractErrorMessage(error, '查询先前知识失败'))
    }
  }
}

export const knowledgeBaseService = new KnowledgeBaseService()
export default knowledgeBaseService
