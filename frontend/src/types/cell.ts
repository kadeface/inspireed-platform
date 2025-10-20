export enum CellType {
  TEXT = 'text',
  CODE = 'code',
  PARAM = 'param',
  SIM = 'sim',
  QA = 'qa',
  CHART = 'chart',
  CONTEST = 'contest',
}

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
  type: CellType.TEXT
  content: TextCellContent
}

export interface CodeCellContent {
  code: string
  language: 'python' | 'javascript' | 'html'
  output?: any
}

export interface CodeCell extends CellBase {
  type: CellType.CODE
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
  type: CellType.PARAM
  content: ParamCellContent
}

export interface SimCellContent {
  type: 'threejs' | 'matterjs' | 'iframe'
  url?: string
  config: any
}

export interface SimCell extends CellBase {
  type: CellType.SIM
  content: SimCellContent
}

export interface QACellContent {
  question?: string
  answer?: string
  isAIAnswer: boolean
}

export interface QACell extends CellBase {
  type: CellType.QA
  content: QACellContent
}

export interface ChartCellContent {
  chartType: 'bar' | 'line' | 'pie' | 'scatter'
  data: any
  options: any
}

export interface ChartCell extends CellBase {
  type: CellType.CHART
  content: ChartCellContent
}

export interface ContestCellContent {
  title: string
  description: string
  rules: any
  leaderboard?: Array<{ userId: number; score: number; rank: number }>
}

export interface ContestCell extends CellBase {
  type: CellType.CONTEST
  content: ContestCellContent
}

export type Cell =
  | TextCell
  | CodeCell
  | ParamCell
  | SimCell
  | QACell
  | ChartCell
  | ContestCell

