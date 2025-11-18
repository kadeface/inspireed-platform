/**
 * 思维导图节点注册
 */

import { Graph } from '@antv/x6'

export function registerMindmapNodes() {
  // 中心节点
  Graph.registerNode(
    'mindmap-central',
    {
      inherit: 'rect',
      width: 180,
      height: 60,
      attrs: {
        body: {
          stroke: '#5F95FF',
          strokeWidth: 3,
          fill: '#EFF4FF',
          rx: 30,
          ry: 30,
        },
        label: {
          text: '中心主题',
          fontSize: 18,
          fontWeight: 'bold',
          fill: '#1F2937',
        },
      },
      ports: {
        groups: {
          out: {
            position: 'right',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#5F95FF',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
        },
        items: [{ id: 'out', group: 'out' }],
      },
    },
    true
  )

  // 一级分支节点
  Graph.registerNode(
    'mindmap-main-branch',
    {
      inherit: 'rect',
      width: 140,
      height: 50,
      attrs: {
        body: {
          stroke: '#10B981',
          strokeWidth: 2,
          fill: '#ECFDF5',
          rx: 25,
          ry: 25,
        },
        label: {
          text: '一级分支',
          fontSize: 15,
          fontWeight: '600',
          fill: '#1F2937',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'left',
            attrs: {
              circle: {
                r: 5,
                magnet: true,
                stroke: '#10B981',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out: {
            position: 'right',
            attrs: {
              circle: {
                r: 5,
                magnet: true,
                stroke: '#10B981',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
        },
        items: [
          { id: 'in', group: 'in' },
          { id: 'out', group: 'out' },
        ],
      },
    },
    true
  )

  // 二级分支节点
  Graph.registerNode(
    'mindmap-sub-branch',
    {
      inherit: 'rect',
      width: 120,
      height: 40,
      attrs: {
        body: {
          stroke: '#F59E0B',
          strokeWidth: 1.5,
          fill: '#FEF3C7',
          rx: 20,
          ry: 20,
        },
        label: {
          text: '二级分支',
          fontSize: 14,
          fill: '#1F2937',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'left',
            attrs: {
              circle: {
                r: 4,
                magnet: true,
                stroke: '#F59E0B',
                strokeWidth: 1.5,
                fill: '#fff',
              },
            },
          },
          out: {
            position: 'right',
            attrs: {
              circle: {
                r: 4,
                magnet: true,
                stroke: '#F59E0B',
                strokeWidth: 1.5,
                fill: '#fff',
              },
            },
          },
        },
        items: [
          { id: 'in', group: 'in' },
          { id: 'out', group: 'out' },
        ],
      },
    },
    true
  )

  // 叶子节点
  Graph.registerNode(
    'mindmap-leaf',
    {
      inherit: 'rect',
      width: 100,
      height: 35,
      attrs: {
        body: {
          stroke: '#8B5CF6',
          strokeWidth: 1,
          fill: '#F5F3FF',
          rx: 18,
          ry: 18,
        },
        label: {
          text: '叶子',
          fontSize: 13,
          fill: '#1F2937',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'left',
            attrs: {
              circle: {
                r: 3,
                magnet: true,
                stroke: '#8B5CF6',
                strokeWidth: 1,
                fill: '#fff',
              },
            },
          },
        },
        items: [{ id: 'in', group: 'in' }],
      },
    },
    true
  )
}

/**
 * 注册思维导图连线
 */
export function registerMindmapEdges() {
  Graph.registerEdge(
    'mindmap-edge',
    {
      inherit: 'edge',
      attrs: {
        line: {
          stroke: '#A78BFA',
          strokeWidth: 2,
          targetMarker: null,
        },
      },
      connector: {
        name: 'smooth',
        args: {
          radius: 20,
        },
      },
      router: {
        name: 'er',
        args: {
          offset: 'center',
          direction: 'H',
        },
      },
    },
    true
  )
}

