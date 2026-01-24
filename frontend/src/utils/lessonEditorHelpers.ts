/**
 * LessonEditor 使用的纯工具函数（无 Vue 依赖）
 */

import type { Cell } from '../types/cell'
import { CellType } from '../types/cell'

export function stripHtmlTags(html: string): string {
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export function markdownToHtml(markdown: string): string {
  const trimmed = markdown.trim()
  if (!trimmed) return ''

  const blocks = trimmed.split(/\n{2,}/)
  return blocks
    .map((block) => {
      const lines = block.split('\n')
      const htmlLines = lines.map((line) => escapeHtml(line))
      return `<p>${htmlLines.join('<br />')}</p>`
    })
    .join('')
}

const CELL_TYPE_NAMES: Record<string, string> = {
  [CellType.TEXT]: '文本单元',
  [CellType.CODE]: '代码单元',
  [CellType.PARAM]: '参数单元',
  [CellType.SIM]: '仿真单元',
  [CellType.CHART]: '图表单元',
  [CellType.CONTEST]: '竞赛单元',
  [CellType.VIDEO]: '视频单元',
  [CellType.ACTIVITY]: '活动单元',
  [CellType.FLOWCHART]: '流程图单元',
  [CellType.BROWSER]: '浏览器单元',
  [CellType.INTERACTIVE]: '交互式课件单元',
  [CellType.REFERENCE_MATERIAL]: '参考素材单元',
}

export function getCellTypeName(cellType: string): string {
  return CELL_TYPE_NAMES[cellType] || '未知单元'
}

export function summarizeCell(cell: Cell, index: number): string | null {
  const orderLabel = `第${index + 1}单元`
  const typeMap: Record<string, string> = {
    [CellType.TEXT]: '文本',
    [CellType.CODE]: '代码',
    [CellType.PARAM]: '参数',
    [CellType.SIM]: '仿真',
    [CellType.CHART]: '图表',
    [CellType.CONTEST]: '竞赛',
    [CellType.VIDEO]: '视频',
    [CellType.ACTIVITY]: '活动',
    [CellType.FLOWCHART]: '流程图',
    [CellType.INTERACTIVE]: '交互式课件',
    [CellType.REFERENCE_MATERIAL]: '参考素材',
  }

  const typeLabel = typeMap[cell.type] || '单元'
  let detail = ''

  if (cell.type === CellType.TEXT && (cell as any).content?.html) {
    const plain = stripHtmlTags((cell as any).content.html ?? '')
    if (plain) {
      detail = plain.slice(0, 28)
      if (plain.length > 28) detail += '…'
    }
  } else if (cell.type === CellType.ACTIVITY && (cell as any).content?.title) {
    detail = (cell as any).content.title
  } else if (cell.type === CellType.VIDEO && (cell as any).content?.title) {
    detail = (cell as any).content.title
  } else if (cell.type === CellType.FLOWCHART) {
    detail = '流程设计'
  } else if (cell.type === CellType.SIM) {
    detail = '仿真互动'
  }

  const parts = [orderLabel, typeLabel]
  if (detail) parts.push(`：${detail}`)
  return parts.join('')
}
