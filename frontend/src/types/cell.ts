export const CellType = {
  TEXT: 'text',
  VIDEO: 'video',
  CODE: 'code',
  SIM: 'sim',
  QA: 'qa',
  CHART: 'chart',
  CONTEST: 'contest',
  PARAM: 'param',
} as const

export type CellType = typeof CellType[keyof typeof CellType]

export interface CellBase {
  id: string
  type: CellType
  order: number
  title?: string
  editable: boolean
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
  type: 'threejs' | 'matterjs' | 'iframe'
  url?: string
  config: any
}

export interface SimCell extends CellBase {
  type: typeof CellType.SIM
  content: SimCellContent
}

export interface QACellContent {
  question?: string
  answer?: string
  isAIAnswer: boolean
}

export interface QACell extends CellBase {
  type: typeof CellType.QA
  content: QACellContent
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

export type Cell =
  | TextCell
  | CodeCell
  | ParamCell
  | SimCell
  | QACell
  | ChartCell
  | ContestCell
  | VideoCell