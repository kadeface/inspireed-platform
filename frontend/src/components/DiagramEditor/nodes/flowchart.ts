/**
 * 流程图节点注册
 */

import { Graph } from '@antv/x6'

export function registerFlowchartNodes() {
  // 开始节点
  Graph.registerNode(
    'flowchart-start',
    {
      inherit: 'ellipse',
      width: 100,
      height: 60,
      attrs: {
        body: {
          stroke: '#10B981',
          strokeWidth: 2,
          fill: '#D1FAE5',
        },
        label: {
          text: '开始',
          fontSize: 14,
          fontWeight: 'bold',
          fill: '#065F46',
        },
      },
      ports: {
        groups: {
          out: {
            position: 'bottom',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#10B981',
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

  // 结束节点
  Graph.registerNode(
    'flowchart-end',
    {
      inherit: 'ellipse',
      width: 100,
      height: 60,
      attrs: {
        body: {
          stroke: '#EF4444',
          strokeWidth: 2,
          fill: '#FEE2E2',
        },
        label: {
          text: '结束',
          fontSize: 14,
          fontWeight: 'bold',
          fill: '#991B1B',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'top',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#EF4444',
                strokeWidth: 2,
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

  // 处理节点
  Graph.registerNode(
    'flowchart-process',
    {
      inherit: 'rect',
      width: 140,
      height: 60,
      attrs: {
        body: {
          stroke: '#3B82F6',
          strokeWidth: 2,
          fill: '#DBEAFE',
          rx: 8,
          ry: 8,
        },
        label: {
          text: '处理',
          fontSize: 14,
          fill: '#1E3A8A',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'top',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#3B82F6',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out: {
            position: 'bottom',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#3B82F6',
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

  // 决策节点
  Graph.registerNode(
    'flowchart-decision',
    {
      inherit: 'polygon',
      width: 140,
      height: 80,
      attrs: {
        body: {
          refPoints: '0,10 10,0 20,10 10,20',
          stroke: '#F59E0B',
          strokeWidth: 2,
          fill: '#FEF3C7',
        },
        label: {
          text: '判断',
          fontSize: 14,
          fill: '#92400E',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'top',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#F59E0B',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out: {
            position: { name: 'absolute', args: { x: '100%', y: '50%' } },
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#F59E0B',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out2: {
            position: 'bottom',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#F59E0B',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
        },
        items: [
          { id: 'in', group: 'in' },
          { id: 'out-yes', group: 'out' },
          { id: 'out-no', group: 'out2' },
        ],
      },
    },
    true
  )

  // 循环节点
  Graph.registerNode(
    'flowchart-loop',
    {
      inherit: 'rect',
      width: 140,
      height: 60,
      attrs: {
        body: {
          stroke: '#8B5CF6',
          strokeWidth: 2,
          fill: '#EDE9FE',
          rx: 8,
          ry: 8,
        },
        label: {
          text: '循环',
          fontSize: 14,
          fill: '#5B21B6',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'top',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#8B5CF6',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out: {
            position: 'bottom',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#8B5CF6',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          loop: {
            position: { name: 'absolute', args: { x: 0, y: '50%' } },
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#8B5CF6',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
        },
        items: [
          { id: 'in', group: 'in' },
          { id: 'out', group: 'out' },
          { id: 'loop', group: 'loop' },
        ],
      },
    },
    true
  )

  // 输入/输出节点
  Graph.registerNode(
    'flowchart-io',
    {
      inherit: 'polygon',
      width: 140,
      height: 60,
      attrs: {
        body: {
          refPoints: '0,10 2,0 20,0 18,10',
          stroke: '#06B6D4',
          strokeWidth: 2,
          fill: '#CFFAFE',
        },
        label: {
          text: '输入/输出',
          fontSize: 14,
          fill: '#164E63',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'top',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#06B6D4',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out: {
            position: 'bottom',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#06B6D4',
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

  // 文档节点
  Graph.registerNode(
    'flowchart-document',
    {
      inherit: 'rect',
      width: 140,
      height: 60,
      attrs: {
        body: {
          stroke: '#EC4899',
          strokeWidth: 2,
          fill: '#FCE7F3',
          rx: 4,
          ry: 4,
        },
        label: {
          text: '文档',
          fontSize: 14,
          fill: '#831843',
        },
      },
      ports: {
        groups: {
          in: {
            position: 'top',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#EC4899',
                strokeWidth: 2,
                fill: '#fff',
              },
            },
          },
          out: {
            position: 'bottom',
            attrs: {
              circle: {
                r: 6,
                magnet: true,
                stroke: '#EC4899',
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
}

