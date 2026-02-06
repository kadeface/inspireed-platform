import type { ActivityCellContent } from './activity'
import type { ResourceType } from './resource'

export const CellType = {
  TEXT: 'TEXT',
  VIDEO: 'VIDEO',
  CODE: 'CODE',
  SIM: 'SIM',
  // QA: 'QA', // 已移除教师端问答功能
  CHART: 'CHART',
  CONTEST: 'CONTEST',
  ACTIVITY: 'ACTIVITY',  // 教学活动（测验、问卷、作业、评价）
  FLOWCHART: 'FLOWCHART',  // 流程图
  BROWSER: 'BROWSER',  // 浏览器单元
  INTERACTIVE: 'INTERACTIVE',  // 交互式课件单元
  REFERENCE_MATERIAL: 'REFERENCE_MATERIAL',
} as const

export type CellType = typeof CellType[keyof typeof CellType]

export interface CellBase {
  id: number | string  // 支持字符串ID（如"cell-1"）
  type: CellType
  order: number
  title?: string
  stage_label?: string
  editable: boolean
  
  // 🎓 学习科学字段
  cognitive_level?: 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create'
  prerequisite_cells?: (string | number)[]  // 前置单元ID列表
  mastery_criteria?: {
    min_attempts?: number
    min_accuracy?: number
    max_time_seconds?: number
  }
}

export interface TextCellContent {
  html: string
  json?: any // TipTap JSON格式
  markdown?: string // Markdown格式（可选）
  editorMode?: 'html' | 'markdown' // 编辑器模式
}

export interface TextCell extends CellBase {
  type: typeof CellType.TEXT
  content: TextCellContent
}

export interface CodeCellContent {
  code: string
  language: 'python' | 'javascript' | 'html'
  output?: any
}

export interface CodeCell extends CellBase {
  type: typeof CellType.CODE
  content: CodeCellContent
  config: {
    timeout?: number
    maxMemory?: number
    environment?: 'jupyterlite' | 'jupyterhub'
  }
}

export interface SimCellContent {
  type: 'phet' | 'threejs' | 'matterjs' | 'iframe' | 'custom' | 'hardware'
  // PhET simulation
  phetSim?: string // PhET simulation name/ID
  phetCategory?: 'physics' | 'chemistry' | 'biology' | 'earth' | 'math'
  // Hardware simulation
  hardwareSim?: string // Hardware simulation ID (from hardware-simulations.ts)
  hardwarePlatform?: 'wokwi' | 'tinkercad' | 'circuitjs' | 'custom'
  hardwareCategory?: 'arduino' | 'esp32' | 'circuit' | 'microcontroller'
  // Generic iframe/URL
  url?: string
  // Simulation configuration
  config: {
    width?: number
    height?: number
    locale?: string
    autoplay?: boolean
    fullScreen?: boolean
    [key: string]: any
  }
}

export interface SimCell extends CellBase {
  type: typeof CellType.SIM
  content: SimCellContent
}

export interface ChartCellContent {
  chartType: 'bar' | 'line' | 'pie' | 'scatter'
  data: any
  options: any
}

export interface ChartCell extends CellBase {
  type: typeof CellType.CHART
  content: ChartCellContent
}

export interface ContestCellContent {
  title: string
  description: string
  rules: any
  leaderboard?: Array<{ userId: number; score: number; rank: number }>
}

export interface ContestCell extends CellBase {
  type: typeof CellType.CONTEST
  content: ContestCellContent
}

export interface VideoCellContent {
  videoUrl: string
  title?: string
  description?: string
  duration?: number  // 视频时长（秒）
  thumbnail?: string  // 缩略图URL
  subtitles?: Array<{
    language: string
    url: string
  }>
  chapters?: Array<{
    title: string
    startTime: number  // 开始时间（秒）
    endTime: number    // 结束时间（秒）
  }>
}

export interface VideoCell extends CellBase {
  type: typeof CellType.VIDEO
  content: VideoCellContent
  config: {
    autoplay?: boolean
    controls?: boolean
    loop?: boolean
    muted?: boolean
    startTime?: number  // 开始播放时间
    endTime?: number    // 结束播放时间
    playbackRate?: number  // 播放速度
  }
}

// Activity Cell
export interface ActivityCell extends CellBase {
  type: typeof CellType.ACTIVITY
  content: ActivityCellContent
  config?: {
    allowOffline?: boolean  // 允许离线答题
  }
}

// Flowchart Cell
export interface FlowchartNode {
  id: string
  type: 'start' | 'process' | 'decision' | 'loop' | 'end' | 'custom'
  label: string
  position: { x: number; y: number }
  data?: any
}

export interface FlowchartEdge {
  id: string
  source: string  // 源节点ID
  target: string  // 目标节点ID
  label?: string
}

export interface FlowchartCellContent {
  nodes: FlowchartNode[]
  edges: FlowchartEdge[]
  style?: {
    theme?: 'light' | 'dark'
    layoutDirection?: 'TB' | 'LR' | 'BT' | 'RL'  // Top-Bottom, Left-Right
  }
}

export interface FlowchartCell extends CellBase {
  type: typeof CellType.FLOWCHART
  content: FlowchartCellContent
  config?: {
    editable?: boolean  // 学生是否可编辑
    showMinimap?: boolean  // 显示缩略图
  }
}

export interface ReferenceMaterialCellContent {
  material_id: number
  title: string
  summary?: string
  resource_type: ResourceType | string
  source_lesson_id?: number
  source_lesson_title?: string
  preview_url?: string
  download_url?: string
  tags?: string[]
  updated_at?: string
  is_accessible?: boolean
}

export interface ReferenceMaterialCell extends CellBase {
  type: typeof CellType.REFERENCE_MATERIAL
  content: ReferenceMaterialCellContent
}

export interface BrowserCellContent {
  url: string                    // 目标网址
  title?: string                 // 单元标题
  description?: string           // 单元描述
  thumbnail?: string             // 缩略图URL（可选）
}

export interface BrowserCell extends CellBase {
  type: typeof CellType.BROWSER
  content: BrowserCellContent
  config?: {
    allowFullscreen?: boolean      // 是否允许全屏（默认true）
    allowNavigation?: boolean       // 是否允许导航（默认true）
    sandbox?: string[]             // iframe sandbox 属性（安全控制）
    width?: string                 // iframe 宽度（默认100%）
    height?: string                // iframe 高度（默认600px）
    showToolbar?: boolean          // 是否显示工具栏（默认false）
  }
}

export interface InteractiveCellContent {
  asset_id?: number                // 资源库资产ID（如果从资源库选择）
  url?: string                     // 交互式课件URL（直接输入URL时使用）
  html_code?: string               // HTML代码（粘贴HTML代码时使用）
  title?: string                   // 课件标题
  description?: string             // 课件描述
  thumbnail?: string               // 缩略图URL
}

export interface InteractiveCell extends CellBase {
  type: typeof CellType.INTERACTIVE
  content: InteractiveCellContent
  config?: {
    allowFullscreen?: boolean      // 是否允许全屏（默认true）
    width?: string                 // iframe 宽度（默认100%）
    height?: string                // iframe 高度（默认800px）
    sandbox?: string[]             // iframe sandbox 属性（安全控制）
  }
}

export type Cell =
  | TextCell
  | CodeCell
  | SimCell
  | ChartCell
  | ContestCell
  | VideoCell
  | ActivityCell
  | FlowchartCell
  | BrowserCell
  | InteractiveCell
  | ReferenceMaterialCell