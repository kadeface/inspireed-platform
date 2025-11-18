/**
 * 节点注册入口
 */

import { registerFlowchartNodes } from './flowchart'
import { registerMindmapNodes, registerMindmapEdges } from './mindmap'

/**
 * 注册所有自定义节点
 */
export function registerCustomNodes() {
  registerFlowchartNodes()
  registerMindmapNodes()
  registerMindmapEdges()
}

export { registerFlowchartNodes, registerMindmapNodes, registerMindmapEdges }

