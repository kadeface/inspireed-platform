<template>
  <div class="diagram-editor" ref="containerRef" :class="{ 'fullscreen': isFullscreen }">
    <DiagramToolbar
      :mode="mode"
      :can-undo="canUndo"
      :can-redo="canRedo"
      :is-fullscreen="isFullscreen"
      @change-mode="handleModeChange"
      @undo="handleUndo"
      @redo="handleRedo"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
      @fit-view="handleFitView"
      @toggle-fullscreen="toggleFullscreen"
      @export="handleExport"
    />

    <div class="editor-content">
      <DiagramSidebar
        v-if="showSidebar && editable"
        :mode="mode"
        @drag-start="handleDragStart"
      />

      <div
        class="canvas-wrapper"
        ref="canvasRef"
      >
        <!-- X6 画布将挂载在这里 -->
      </div>

      <!-- 小地图 -->
      <div v-if="showMinimap" class="minimap-container" ref="minimapRef"></div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Graph } from '@antv/x6'
import { Snapline } from '@antv/x6-plugin-snapline'
// import { Scroller } from '@antv/x6-plugin-scroller'  // 暂时禁用，会干扰 Dnd 坐标
import { Selection } from '@antv/x6-plugin-selection'
import { Keyboard } from '@antv/x6-plugin-keyboard'
import { History } from '@antv/x6-plugin-history'
import { Clipboard } from '@antv/x6-plugin-clipboard'
import { Export } from '@antv/x6-plugin-export'
import { MiniMap } from '@antv/x6-plugin-minimap'
import { Dnd } from '@antv/x6-plugin-dnd'

import DiagramToolbar from './DiagramToolbar.vue'
import DiagramSidebar from './DiagramSidebar.vue'
import { registerCustomNodes } from './nodes'
import { FlowchartMode } from './modes/FlowchartMode'
import { MindmapMode } from './modes/MindmapMode'
import type { DiagramContent, DiagramMode, DiagramExportFormat } from '@/types/diagram'

interface Props {
  mode?: DiagramMode
  content?: DiagramContent
  editable?: boolean
  showSidebar?: boolean
  showMinimap?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'flowchart',
  editable: false,
  showSidebar: true,
  showMinimap: true,
})

const emit = defineEmits<{
  update: [content: DiagramContent]
  'mode-change': [mode: DiagramMode]
}>()

const containerRef = ref<HTMLElement>()
const canvasRef = ref<HTMLElement>()
const minimapRef = ref<HTMLElement>()
let graph: Graph | null = null
let dnd: Dnd | null = null

const canUndo = ref(false)
const canRedo = ref(false)
const loading = ref(true)
const isFullscreen = ref(false)

onMounted(async () => {
  if (!canvasRef.value) return

  // 注册自定义节点和边
  registerCustomNodes()

  await nextTick()

  // 初始化画布
  graph = new Graph({
    container: canvasRef.value,
    width: canvasRef.value.clientWidth,
    height: canvasRef.value.clientHeight,
    autoResize: true,
    panning: {
      enabled: props.editable,
      modifiers: 'shift',  // 按住 Shift 键拖拽画布
    },
    mousewheel: {
      enabled: true,
      modifiers: ['ctrl', 'meta'],  // Ctrl/Cmd + 滚轮缩放
      minScale: 0.1,
      maxScale: 3,
    },
    connecting: props.mode === 'mindmap' ? {
      snap: false,
      allowBlank: false,
      allowLoop: false,
      allowNode: true,
      allowEdge: false,
      allowMulti: false,
      highlight: true,
      connector: {
        name: 'smooth',
        args: { radius: 20 },
      },
      router: {
        name: 'er',
        args: { offset: 'center', direction: 'H' },
      },
      createEdge() {
        return graph!.createEdge({
          shape: 'mindmap-edge',
          attrs: {
            line: {
              stroke: '#A78BFA',
              strokeWidth: 2,
              targetMarker: null,
            },
          },
          zIndex: 0,
        })
      },
      validateConnection({ sourceView, targetView, sourceMagnet, targetMagnet }: any) {
        if (sourceView === targetView) return false
        if (!sourceMagnet || sourceMagnet.getAttribute('port-group') !== 'out') return false
        if (!targetMagnet || targetMagnet.getAttribute('port-group') !== 'in') return false
        return true
      },
    } : {
      snap: true,
      allowBlank: false,
      allowLoop: false,
      allowNode: true,
      allowEdge: false,
      allowMulti: false,
      highlight: true,
      connector: 'rounded',
      router: {
        name: 'er',
        args: { offset: 25, direction: 'V' },
      },
      createEdge() {
        return graph!.createEdge({
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
          zIndex: 0,
        })
      },
      validateConnection({ sourceView, targetView, sourceMagnet, targetMagnet }: any) {
        if (sourceView === targetView) return false
        if (!sourceMagnet || sourceMagnet.getAttribute('port-group') !== 'out') return false
        if (!targetMagnet || targetMagnet.getAttribute('port-group') !== 'in') return false
        return true
      },
    },
    grid: {
      size: 10,
      visible: true,
      type: 'dot',
      args: {
        color: '#e0e0e0',
        thickness: 1,
      },
    },
    highlighting: {
      magnetAdsorbed: {
        name: 'stroke',
        args: {
          attrs: {
            fill: '#5F95FF',
            stroke: '#5F95FF',
          },
        },
      },
    },
  })

  // 加载插件
  loadPlugins()

  // 应用模式配置
  applyModeConfig(props.mode)

  // 初始加载内容（不触发 watch）
  if (props.content && props.content.cells && props.content.cells.length > 0) {
    isUpdating = true
    loadContent(props.content)
    setTimeout(() => {
      isUpdating = false
    }, 200)
  }

  // 监听变化
  if (props.editable) {
    setupEventListeners()
  }

  loading.value = false
})

onUnmounted(() => {
  if (graph) {
    graph.dispose()
    graph = null
  }
  
  // 移除全屏监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
})

// 监听浏览器全屏状态变化（用户按 Esc 退出全屏）
function handleFullscreenChange() {
  const isCurrentlyFullscreen = !!(
    document.fullscreenElement ||
    (document as any).webkitFullscreenElement ||
    (document as any).mozFullScreenElement
  )
  
  if (!isCurrentlyFullscreen && isFullscreen.value) {
    isFullscreen.value = false
    setTimeout(() => {
      if (graph) {
        graph.resize()
      }
    }, 100)
  }
}

// 添加全屏监听
document.addEventListener('fullscreenchange', handleFullscreenChange)
document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
document.addEventListener('mozfullscreenchange', handleFullscreenChange)

function loadPlugins() {
  if (!graph) return

  // 对齐辅助线
  graph.use(
    new Snapline({
      enabled: true,
      sharp: true,
    })
  )

  // 注释掉 Scroller 插件，因为它会干扰 Dnd 的坐标计算
  // 改用 Graph 内置的 panning 功能
  /*
  if (props.editable) {
    graph.use(
      new Scroller({
        enabled: true,
        pannable: false,
        pageVisible: false,
        pageBreak: false,
        autoResize: true,
      })
    )
  }
  */

  // 框选
  if (props.editable) {
    graph.use(
      new Selection({
        enabled: true,
        multiple: true,
        rubberband: true,
        movable: true,
        showNodeSelectionBox: true,
      })
    )
  }

  // 键盘快捷键
  if (props.editable) {
    graph.use(
      new Keyboard({
        enabled: true,
        global: false,
      })
    )
  }

  // 撤销/重做
  if (props.editable) {
    graph.use(
      new History({
        enabled: true,
        stackSize: 50,
      })
    )
  }

  // 复制粘贴
  if (props.editable) {
    graph.use(
      new Clipboard({
        enabled: true,
      })
    )
  }

  // 导出
  graph.use(new Export())

  // 小地图
  if (props.showMinimap && minimapRef.value) {
    graph.use(
      new MiniMap({
        container: minimapRef.value,
        width: 200,
        height: 160,
        padding: 10,
        scalable: false,
        minScale: 0.1,
        maxScale: 1,
      })
    )
  }

  // 拖拽添加节点（必须在 graph 创建后初始化）
  if (props.editable && graph) {
    dnd = new Dnd({
      target: graph,
      scaled: true,
      animation: true,
      validateNode: () => true,
    })
  }
}

function applyModeConfig(mode: DiagramMode) {
  if (!graph) return

  let modeConfig
  switch (mode) {
    case 'flowchart':
      modeConfig = new FlowchartMode()
      break
    case 'mindmap':
      modeConfig = new MindmapMode()
      break
  }

  if (modeConfig) {
    modeConfig.apply(graph)
  }
}

function loadContent(content: DiagramContent) {
  if (!graph || !content || !content.cells) return

  try {
    graph.fromJSON({ cells: content.cells })
    
    // 自动居中显示
    setTimeout(() => {
      graph?.centerContent()
    }, 100)
  } catch (error) {
    console.error('Failed to load diagram content:', error)
  }
}

function setupEventListeners() {
  if (!graph) return

  // 监听内容变化
  const events = ['node:added', 'node:removed', 'node:changed', 'edge:added', 'edge:removed', 'edge:changed']
  events.forEach((event) => {
    graph!.on(event, handleChange)
  })

  // 监听节点添加
  graph.on('node:added', ({ node }) => {
    requestAnimationFrame(() => {
      node.toFront()
      graph?.drawBackground()
      
      // 如果是第一个节点，居中显示
      const allNodes = graph?.getNodes() || []
      if (allNodes.length === 1) {
        setTimeout(() => {
          graph?.centerContent({ padding: 50 })
        }, 100)
      }
    })
  })

  // 监听双击编辑
  graph.on('node:dblclick', ({ node }) => {
    const currentLabel = node.label as string || ''
    const newLabel = prompt('请输入节点文本:', currentLabel)
    if (newLabel !== null) {
      node.setAttrs({
        label: {
          text: newLabel,
        },
      })
      node.label = newLabel
    }
  })

  // 更新撤销/重做状态
  graph.on('history:change', () => {
    canUndo.value = graph!.canUndo()
    canRedo.value = graph!.canRedo()
  })
}

function handleChange() {
  if (!graph || isUpdating) return

  const content: DiagramContent = {
    cells: graph.toJSON().cells,
    metadata: {
      mode: props.mode,
      updatedAt: Date.now(),
    },
  }
  
  lastEmittedContent = JSON.stringify(content.cells)
  emit('update', content)
}

function handleUndo() {
  graph?.undo()
}

function handleRedo() {
  graph?.redo()
}

function handleZoomIn() {
  graph?.zoom(0.1)
}

function handleZoomOut() {
  graph?.zoom(-0.1)
}

function handleFitView() {
  graph?.centerContent()
}

async function handleExport(format: DiagramExportFormat) {
  if (!graph) return

  try {
    switch (format) {
      case 'png':
        await graph.exportPNG('diagram.png', {
          backgroundColor: '#ffffff',
          padding: 20,
        })
        break
      case 'svg':
        await graph.exportSVG('diagram.svg')
        break
      case 'json':
        const json = graph.toJSON()
        const blob = new Blob([JSON.stringify(json, null, 2)], {
          type: 'application/json',
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'diagram.json'
        a.click()
        URL.revokeObjectURL(url)
        break
    }
  } catch (error) {
    console.error('Export failed:', error)
    alert('导出失败，请重试')
  }
}

function handleModeChange(newMode: DiagramMode) {
  emit('mode-change', newMode)
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
  
  if (isFullscreen.value) {
    // 进入全屏
    if (containerRef.value) {
      if (containerRef.value.requestFullscreen) {
        containerRef.value.requestFullscreen()
      } else if ((containerRef.value as any).webkitRequestFullscreen) {
        (containerRef.value as any).webkitRequestFullscreen()
      } else if ((containerRef.value as any).mozRequestFullScreen) {
        (containerRef.value as any).mozRequestFullScreen()
      }
    }
    
    // 延迟调整画布大小，确保全屏后尺寸正确
    setTimeout(() => {
      if (graph) {
        graph.resize()
        graph.centerContent({ padding: 50 })
      }
    }, 100)
  } else {
    // 退出全屏
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if ((document as any).webkitExitFullscreen) {
      (document as any).webkitExitFullscreen()
    } else if ((document as any).mozCancelFullScreen) {
      (document as any).mozCancelFullScreen()
    }
    
    // 延迟调整画布大小
    setTimeout(() => {
      if (graph) {
        graph.resize()
      }
    }, 100)
  }
}

function handleDragStart(node: any, event: MouseEvent) {
  if (!graph || !dnd) return

  try {
    const nodeTemplate = graph.createNode({
      shape: node.shape,
      width: node.width,
      height: node.height,
    })

    dnd.start(nodeTemplate, event)
    
    // 拖拽结束后重绘画布
    const onDragEnd = () => {
      setTimeout(() => {
        if (graph) {
          graph.drawBackground()
        }
      }, 50)
    }
    
    document.addEventListener('mouseup', onDragEnd, { once: true })
  } catch (error) {
    console.error('Failed to start drag:', error)
  }
}

// 监听模式变化
watch(
  () => props.mode,
  (newMode) => {
    applyModeConfig(newMode)
  }
)

// 监听内容变化
let lastEmittedContent: string | null = null
let isUpdating = false

watch(
  () => props.content,
  (newContent, oldContent) => {
    if (isUpdating || !newContent || !graph) return
    
    // 比较节点 ID 列表
    const currentCells = graph.toJSON().cells
    const newCells = newContent.cells || []
    
    const currentIds = currentCells.map(c => c.id).sort().join(',')
    const newIds = newCells.map(c => c.id).sort().join(',')
    
    // 只有当节点 ID 列表不同时才重新加载
    if (currentIds !== newIds) {
      isUpdating = true
      loadContent(newContent)
      setTimeout(() => {
        isUpdating = false
      }, 100)
    }
  },
  { deep: true }
)
</script>

<style scoped>
.diagram-editor {
  @apply w-full flex flex-col bg-gray-50 relative;
  min-height: 500px;
  height: 500px;
  transition: all 0.3s ease;
}

.diagram-editor.fullscreen {
  @apply fixed inset-0 z-50 bg-white;
  height: 100vh !important;
  width: 100vw !important;
  min-height: 100vh;
}

.diagram-editor.fullscreen .editor-content {
  height: calc(100vh - 56px) !important;
}

.diagram-editor.fullscreen .canvas-wrapper {
  flex: 1;
  height: 100% !important;
  min-height: calc(100vh - 56px) !important;
}

.editor-content {
  @apply flex-1 flex relative;
  min-width: 0;
  overflow-x: visible;
  overflow-y: auto;
}

.canvas-wrapper {
  @apply flex-1 bg-white relative;
  min-height: 400px;
  height: 100%;
  overflow: visible;
}

/* 修复全屏模式下拖拽预览不可见的问题 */
.diagram-editor.fullscreen :deep(.x6-graph-dnd-dragging) {
  z-index: 9999 !important;
  pointer-events: none;
}

.diagram-editor.fullscreen :deep(.x6-graph-dnd-ghost) {
  z-index: 9999 !important;
  opacity: 0.7;
}

/* 确保拖拽时的节点可见 */
:deep(.x6-graph-dnd-dragging) {
  z-index: 1000 !important;
  opacity: 0.7 !important;
  pointer-events: none;
}

:deep(.x6-graph-dnd-ghost) {
  z-index: 1000 !important;
  opacity: 0.5 !important;
}

/* X6 拖拽相关的全局样式 */
:deep(.x6-widget-dnd) {
  position: fixed !important;
  z-index: 10000 !important;
  pointer-events: none;
}

:deep(.x6-widget-dnd-dragging) {
  opacity: 0.8 !important;
  cursor: move !important;
}

.minimap-container {
  @apply absolute bottom-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden;
  z-index: 10;
}

.loading-overlay {
  @apply absolute inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-50;
}

.loading-spinner {
  @apply w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin;
}

/* X6 样式覆盖 */
:deep(.x6-graph) {
  @apply w-full h-full;
}

:deep(.x6-graph-scroller) {
  @apply w-full h-full;
}

:deep(.x6-widget-minimap) {
  border: none !important;
}
</style>

