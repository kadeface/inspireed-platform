import type { ActivityCellContent } from './activity'
import type { ResourceType } from './resource'

export const CellType = {
  TEXT: 'text',
  VIDEO: 'video',
  CODE: 'code',
  SIM: 'sim',
  // QA: 'qa', // 已移除教师端问答功能
  CHART: 'chart',
  CONTEST: 'contest',
  PARAM: 'param',
  ACTIVITY: 'activity',  // 教学活动（测验、问卷、作业、评价）
  FLOWCHART: 'flowchart',  // 流程图
  REFERENCE_MATERIAL: 'reference_material',
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

export interface ParamCellContent {
  schema: any // JSON Schema
  values: Record<string, any>
}

export interface ParamCell extends CellBase {
  type: typeof CellType.PARAM
  content: ParamCellContent
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

export type Cell =
  | TextCell
  | CodeCell
  | ParamCell
  | SimCell
  | ChartCell
  | ContestCell
  | VideoCell
  | ActivityCell
  | FlowchartCell
  | ReferenceMaterialCell