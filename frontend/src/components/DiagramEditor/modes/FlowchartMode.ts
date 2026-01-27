/**
 * 流程图模式配置
 */

import type { Graph, Node } from '@antv/x6'

export class FlowchartMode {
  apply(graph: Graph) {
    // 流程图模式的配置已在创建 Graph 时设置
    // 这里只注册快捷键
    this.registerShortcuts(graph)
  }

  private registerShortcuts(graph: Graph) {
    // Delete: 删除选中的节点/边
    graph.bindKey(['delete', 'backspace'], () => {
      const cells = graph.getSelectedCells()
      if (cells.length) {
        graph.removeCells(cells)
      }
      return false
    })

    // Ctrl+C: 复制
    graph.bindKey(['ctrl+c', 'meta+c'], () => {
      const cells = graph.getSelectedCells()
      if (cells.length) {
        graph.copy(cells)
      }
      return false
    })

    // Ctrl+V: 粘贴
    graph.bindKey(['ctrl+v', 'meta+v'], () => {
      if (!graph.isClipboardEmpty()) {
        const cells = graph.paste({ offset: 32 })
        graph.cleanSelection()
        graph.select(cells)
      }
      return false
    })

    // Ctrl+X: 剪切
    graph.bindKey(['ctrl+x', 'meta+x'], () => {
      const cells = graph.getSelectedCells()
      if (cells.length) {
        graph.cut(cells)
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

    // Ctrl+A: 全选
    graph.bindKey(['ctrl+a', 'meta+a'], () => {
      const nodes = graph.getNodes()
      if (nodes) {
        graph.select(nodes)
      }
      return false
    })
  }
}

