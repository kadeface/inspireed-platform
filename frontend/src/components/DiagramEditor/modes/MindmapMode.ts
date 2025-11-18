/**
 * 思维导图模式配置
 */

import type { Graph, Node } from '@antv/x6'

export class MindmapMode {
  apply(graph: Graph) {
    // 思维导图模式的配置已在创建 Graph 时设置
    // 这里只注册快捷键和启用自动布局
    this.registerShortcuts(graph)
    this.enableAutoLayout(graph)
  }

  private registerShortcuts(graph: Graph) {
    // Tab: 添加子节点
    graph.bindKey('tab', () => {
      const selected = graph.getSelectedCells()
      if (selected.length === 1 && selected[0].isNode()) {
        this.addChildNode(graph, selected[0] as Node)
      }
      return false
    })

    // Enter: 添加兄弟节点
    graph.bindKey('enter', () => {
      const selected = graph.getSelectedCells()
      if (selected.length === 1 && selected[0].isNode()) {
        this.addSiblingNode(graph, selected[0] as Node)
      }
      return false
    })

    // Delete/Backspace: 删除节点
    graph.bindKey(['delete', 'backspace'], () => {
      const selected = graph.getSelectedCells()
      if (selected.length > 0) {
        graph.removeCells(selected)
      }
      return false
    })

    // Ctrl+Z: 撤销
    graph.bindKey(['ctrl+z', 'meta+z'], () => {
      graph.undo()
      return false
    })

    // Ctrl+Shift+Z 或 Ctrl+Y: 重做
    graph.bindKey(['ctrl+shift+z', 'ctrl+y', 'meta+shift+z', 'meta+y'], () => {
      graph.redo()
      return false
    })
  }

  private addChildNode(graph: Graph, parent: Node) {
    const parentPos = parent.position()
    const parentSize = parent.size()

    // 获取父节点的层级
    const parentLevel = (parent.getData() as any)?.level || 0

    // 根据层级选择节点类型
    let nodeShape = 'mindmap-leaf'
    if (parentLevel === 0) {
      nodeShape = 'mindmap-main-branch'
    } else if (parentLevel === 1) {
      nodeShape = 'mindmap-sub-branch'
    }

    // 计算子节点位置
    const childX = parentPos.x + parentSize.width + 100
    const childY = parentPos.y

    const child = graph.addNode({
      shape: nodeShape,
      x: childX,
      y: childY,
      label: '新节点',
      data: {
        level: parentLevel + 1,
      },
    })

    // 添加连线
    graph.addEdge({
      shape: 'mindmap-edge',
      source: { cell: parent, port: 'out' },
      target: { cell: child, port: 'in' },
    })

    // 触发自动布局
    setTimeout(() => this.autoLayout(graph, parent), 100)

    // 选中新节点
    graph.cleanSelection()
    graph.select(child)
  }

  private addSiblingNode(graph: Graph, node: Node) {
    // 查找父节点
    const incomingEdges = graph.getIncomingEdges(node)
    if (incomingEdges && incomingEdges.length > 0) {
      const parent = incomingEdges[0].getSourceNode()
      if (parent) {
        this.addChildNode(graph, parent)
      }
    }
  }

  private enableAutoLayout(graph: Graph) {
    // 监听节点添加/删除，自动触发布局
    graph.on('node:added', (args) => {
      const { node } = args
      const incomingEdges = graph.getIncomingEdges(node)
      if (incomingEdges && incomingEdges.length > 0) {
        const parent = incomingEdges[0].getSourceNode()
        if (parent) {
          setTimeout(() => this.autoLayout(graph, parent), 100)
        }
      }
    })

    graph.on('node:removed', (args) => {
      const { node } = args
      // 可以添加节点删除后的布局调整逻辑
    })
  }

  private autoLayout(graph: Graph, rootNode: Node) {
    // 使用树形布局算法
    const children = this.getChildren(graph, rootNode)

    if (children.length === 0) return

    const rootPos = rootNode.position()
    const rootSize = rootNode.size()
    const spacing = 60
    const offsetX = rootSize.width + 100

    // 垂直排列子节点
    const totalHeight = (children.length - 1) * spacing
    let startY = rootPos.y + rootSize.height / 2 - totalHeight / 2

    children.forEach((child, index) => {
      const childSize = child.size()
      child.position({
        x: rootPos.x + offsetX,
        y: startY + index * spacing - childSize.height / 2,
      })

      // 递归布局子节点的子节点
      this.autoLayout(graph, child)
    })
  }

  private getChildren(graph: Graph, node: Node): Node[] {
    const outgoingEdges = graph.getOutgoingEdges(node)
    if (!outgoingEdges) return []

    return outgoingEdges
      .map((edge) => edge.getTargetNode())
      .filter((n): n is Node => n !== null)
  }
}

