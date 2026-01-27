/**
 * AntV X6 图编辑器类型定义
 */

import type { Cell, Node, Edge } from '@antv/x6'

export type DiagramMode = 'flowchart' | 'mindmap' | 'er-diagram' | 'org-chart'

export type DiagramExportFormat = 'png' | 'svg' | 'json' | 'pdf'

/**
 * 图数据内容
 */
export interface DiagramContent {
  cells: Cell.Metadata[]
  metadata?: {
    mode?: DiagramMode
    version?: string
    createdAt?: number
    updatedAt?: number
    createdBy?: number
  }
}

/**
 * 流程图节点类型
 */
export type FlowchartNodeType =
  | 'flowchart-start'
  | 'flowchart-end'
  | 'flowchart-process'
  | 'flowchart-decision'
  | 'flowchart-loop'
  | 'flowchart-io'
  | 'flowchart-document'

/**
 * 思维导图节点类型
 */
export type MindmapNodeType =
  | 'mindmap-central'
  | 'mindmap-main-branch'
  | 'mindmap-sub-branch'
  | 'mindmap-leaf'

/**
 * 节点模板
 */
export interface NodeTemplate {
  id: string
  label: string
  shape: string
  icon?: string
  description?: string
  category: 'flowchart' | 'mindmap' | 'common'
  defaultAttrs?: {
    width?: number
    height?: number
    [key: string]: any
  }
}

/**
 * 图编辑器配置
 */
export interface DiagramEditorConfig {
  mode: DiagramMode
  editable: boolean
  showToolbar?: boolean
  showSidebar?: boolean
  showMinimap?: boolean
  showGrid?: boolean
  showSnapline?: boolean
  enableKeyboard?: boolean
  enableHistory?: boolean
  enableSelection?: boolean
  enableClipboard?: boolean
  autoSave?: boolean
  autoSaveDelay?: number
}

/**
 * 工具栏按钮配置
 */
export interface ToolbarButton {
  id: string
  label: string
  icon: string
  disabled?: boolean
  visible?: boolean
  action: () => void
}

/**
 * 图验证结果
 */
export interface DiagramValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

/**
 * 历史记录状态
 */
export interface HistoryState {
  canUndo: boolean
  canRedo: boolean
  historySize: number
}

/**
 * 导出选项
 */
export interface ExportOptions {
  format: DiagramExportFormat
  filename?: string
  quality?: number
  backgroundColor?: string
  padding?: number
}

