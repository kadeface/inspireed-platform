/**
 * 图编辑器数据迁移工具
 * 用于在 Vue Flow 和 AntV X6 之间转换数据格式
 */

import type { Cell } from '@antv/x6'
import type { FlowchartCellContent } from '@/types/cell'
import type { DiagramContent } from '@/types/diagram'

/**
 * 从 Vue Flow 数据格式迁移到 X6 格式
 */
export function migrateVueFlowToX6(vueFlowData: FlowchartCellContent): DiagramContent {
  const cells: Cell.Metadata[] = []

  // 迁移节点
  if (vueFlowData.nodes && Array.isArray(vueFlowData.nodes)) {
    vueFlowData.nodes.forEach((node) => {
      cells.push({
        id: node.id,
        shape: mapVueFlowNodeTypeToX6(node.type),
        x: node.position?.x || 0,
        y: node.position?.y || 0,
        label: node.label || '',
        data: node.data,
      })
    })
  }

  // 迁移边
  if (vueFlowData.edges && Array.isArray(vueFlowData.edges)) {
    vueFlowData.edges.forEach((edge) => {
      cells.push({
        id: edge.id,
        shape: 'edge',
        source: edge.source,
        target: edge.target,
        label: edge.label,
        attrs: {
          line: {
            stroke: '#5F95FF',
            strokeWidth: 2,
            targetMarker: {
              name: 'block',
              width: 12,
              height: 8,
            },
          },
        },
      })
    })
  }

  return {
    cells,
    metadata: {
      mode: 'flowchart',
      version: '2.0',
      updatedAt: Date.now(),
    },
  }
}

/**
 * 从 X6 格式迁移回 Vue Flow 格式（向后兼容）
 */
export function migrateX6ToVueFlow(x6Data: DiagramContent): FlowchartCellContent {
  const nodes: any[] = []
  const edges: any[] = []

  if (!x6Data.cells || !Array.isArray(x6Data.cells)) {
    return { nodes: [], edges: [] }
  }

  x6Data.cells.forEach((cell) => {
    if (cell.shape === 'edge' || cell.source || cell.target) {
      // 这是一条边
      edges.push({
        id: cell.id || `edge-${Date.now()}`,
        source: typeof cell.source === 'object' ? (cell.source as any).cell : cell.source,
        target: typeof cell.target === 'object' ? (cell.target as any).cell : cell.target,
        label: cell.label,
      })
    } else {
      // 这是一个节点
      const position = (cell as any).position || { x: cell.x || 0, y: cell.y || 0 }
      
      nodes.push({
        id: cell.id || `node-${Date.now()}`,
        type: mapX6NodeTypeToVueFlow(cell.shape || ''),
        label: cell.label || (cell as any).attrs?.label?.text || '',
        position: {
          x: position.x || 0,
          y: position.y || 0,
        },
        data: cell.data,
      })
    }
  })

  return {
    nodes,
    edges,
    style: {
      theme: 'light',
      layoutDirection: 'TB',
    },
  }
}

/**
 * 映射 Vue Flow 节点类型到 X6 节点类型
 */
function mapVueFlowNodeTypeToX6(vueFlowType: string): string {
  const typeMap: Record<string, string> = {
    start: 'flowchart-start',
    end: 'flowchart-end',
    process: 'flowchart-process',
    decision: 'flowchart-decision',
    loop: 'flowchart-loop',
    io: 'flowchart-io',
    document: 'flowchart-document',
    // 思维导图节点
    'mindmap-central': 'mindmap-central',
    'mindmap-branch': 'mindmap-main-branch',
    'mindmap-sub': 'mindmap-sub-branch',
    'mindmap-leaf': 'mindmap-leaf',
  }

  return typeMap[vueFlowType] || 'flowchart-process'
}

/**
 * 映射 X6 节点类型到 Vue Flow 节点类型
 */
function mapX6NodeTypeToVueFlow(x6Shape: string): string {
  const typeMap: Record<string, string> = {
    'flowchart-start': 'start',
    'flowchart-end': 'end',
    'flowchart-process': 'process',
    'flowchart-decision': 'decision',
    'flowchart-loop': 'loop',
    'flowchart-io': 'io',
    'flowchart-document': 'document',
    // 思维导图节点
    'mindmap-central': 'mindmap-central',
    'mindmap-main-branch': 'mindmap-branch',
    'mindmap-sub-branch': 'mindmap-sub',
    'mindmap-leaf': 'mindmap-leaf',
  }

  return typeMap[x6Shape] || 'process'
}

/**
 * 检测数据格式
 */
export function detectDataFormat(data: any): 'vue-flow' | 'x6' | 'unknown' {
  if (!data) return 'unknown'

  // 检查是否为 Vue Flow 格式
  if (data.nodes && data.edges && Array.isArray(data.nodes) && Array.isArray(data.edges)) {
    return 'vue-flow'
  }

  // 检查是否为 X6 格式
  if (data.cells && Array.isArray(data.cells)) {
    return 'x6'
  }

  return 'unknown'
}

/**
 * 自动迁移数据（智能检测格式）
 */
export function autoMigrateData(data: any): DiagramContent {
  const format = detectDataFormat(data)

  switch (format) {
    case 'vue-flow':
      return migrateVueFlowToX6(data)
    case 'x6':
      return data
    default:
      console.warn('Unknown data format, returning empty diagram')
      return {
        cells: [],
        metadata: {
          mode: 'flowchart',
          version: '2.0',
          updatedAt: Date.now(),
        },
      }
  }
}

/**
 * 验证图数据的有效性
 */
export function validateDiagramData(data: DiagramContent): boolean {
  if (!data || typeof data !== 'object') {
    return false
  }

  if (!data.cells || !Array.isArray(data.cells)) {
    return false
  }

  // 验证每个 cell 的基本结构
  return data.cells.every((cell) => {
    return cell.id && (cell.shape || cell.source || cell.target)
  })
}

