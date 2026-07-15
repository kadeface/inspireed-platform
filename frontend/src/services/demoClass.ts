/**
 * 实验班演示账号 API 服务
 */
import api from './api'

export interface DemoClassStatus {
  school_ready: boolean
  classroom_ready: boolean
  school_id: number | null
  classroom_id: number | null
  school_name: string
  classroom_name: string
  target_accounts: number
  ready_accounts: number
  missing_usernames: string[]
  account_rule: string
}

export interface DemoClassProvisionResult {
  school_id: number
  classroom_id: number
  created_users: number
  skipped_users: number
  created_memberships: number
  conflicts: string[]
  message: string
}

export interface DemoClassResetResult {
  reset_count: number
  message: string
}

export const demoClassService = {
  async getStatus(): Promise<DemoClassStatus> {
    return await api.get('/admin/demo-class/status')
  },
  async provision(): Promise<DemoClassProvisionResult> {
    return await api.post('/admin/demo-class/provision')
  },
  async resetPasswords(): Promise<DemoClassResetResult> {
    return await api.post('/admin/demo-class/reset-passwords')
  },
}

export default demoClassService

/** 生成 st01~st60 / 123456 的账号清单文本，用于一键复制 */
export function buildAccountListText(): string {
  const lines: string[] = []
  for (let i = 1; i <= 60; i++) {
    const u = `st${String(i).padStart(2, '0')}`
    lines.push(`${u} / 123456`)
  }
  return lines.join('\n')
}
