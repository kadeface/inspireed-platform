/**
 * Cell工具函数
 *
 * 用于处理Cell相关的操作和显示逻辑
 */

import type { Cell } from '@/types/cell'
import { getCellId as getCellIdUtil } from '@/utils/cellId'

/**
 * 获取Cell类型标签
 * @param type - Cell类型
 * @returns 类型标签文本
 */
export function getCellTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text: '文本',
    code: '代码',
    activity: '活动',
    video: '视频',
    flowchart: '流程图',
    qa: '问答',
    browser: '浏览器',
    interactive: '互动',
    reference_material: '参考资料',
  }
  return labels[type] || type
}

/**
 * 获取Cell类型emoji（用于非图标场景）
 * @param type - Cell类型
 * @returns emoji字符串
 */
export function getCellTypeEmoji(type: string): string {
  const emojis: Record<string, string> = {
    text: '📄',
    code: '💻',
    activity: '📝',
    video: '📹',
    flowchart: '📊',
    qa: '❓',
    browser: '🌐',
    interactive: '🎮',
    reference_material: '📚',
  }
  return emojis[type] || '📦'
}

/**
 * 判断模块是否激活
 * @param cell - Cell对象
 * @param index - Cell索引
 * @param session - 会话对象
 * @param displayCellOrders - 显示的Cell orders
 * @param selectedCellIndex - 选中的Cell索引
 * @returns 是否激活
 */
export function isModuleActive(
  cell: Cell,
  index: number,
  session: any,
  displayCellOrders: number[],
  selectedCellIndex: number
): boolean {
  if (!session) return false

  // 多选模式：优先使用 displayCellOrders
  if (displayCellOrders.length > 0) {
    const cellOrder = cell.order !== undefined ? cell.order : index
    return displayCellOrders.includes(cellOrder)
  }

  // 单选模式：使用 current_cell_id 或 selectedCellIndex
  if (selectedCellIndex >= 0 && selectedCellIndex === index) {
    return true
  }

  const currentId = session.current_cell_id
  if (!currentId || currentId === 0) return false

  const cellId = getCellIdUtil(cell)
  if (typeof cellId === 'number' && cellId === currentId) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === currentId) return true
  }

  return false
}

/**
 * 判断活动模块是否激活
 * @param cell - Cell对象
 * @param index - Cell索引
 * @param session - 会话对象
 * @returns 是否激活
 */
export function isModuleActivityActive(cell: Cell, index: number, session: any): boolean {
  if (cell.type !== 'activity') return false
  if (!session?.current_activity_id) return false

  const cellId = getCellIdUtil(cell)
  if (typeof cellId === 'number' && cellId === session.current_activity_id) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === session.current_activity_id) return true
  }
  return false
}

/**
 * 获取模块提示信息
 * @param cell - Cell对象
 * @param index - Cell索引
 * @param isActive - 是否激活
 * @returns 提示文本
 */
export function getModuleTooltip(cell: Cell, index: number, isActive: boolean): string {
  const typeLabel = getCellTypeLabel(cell.type)
  const title = cell.title || `模块 ${index + 1}`
  const status = isActive ? ' (已选中)' : ''
  return `${index + 1}. ${title} - ${typeLabel}${status}`
}

/**
 * 获取当前模块索引
 * @param lessonContentCells - 课程内容Cells数组
 * @param session - 会话对象
 * @returns 当前模块索引，未找到返回-1
 */
export function getCurrentModuleIndex(lessonContentCells: Cell[], session: any): number {
  if (!lessonContentCells.length || !session) return -1

  return lessonContentCells.findIndex(cell => {
    const cellId = getCellIdUtil(cell)
    const currentId = session.current_cell_id
    if (!currentId) return false

    // 尝试匹配数字ID
    if (typeof cellId === 'number' && cellId === currentId) return true
    // 尝试匹配字符串ID（转换为数字）
    if (typeof cellId === 'string') {
      const numId = parseInt(cellId)
      if (!isNaN(numId) && numId === currentId) return true
    }
    return false
  })
}

/**
 * 根据order获取Cell
 * @param order - Cell的order值
 * @param lessonContentCells - 课程内容Cells数组
 * @returns 找到的Cell，未找到返回null
 */
export function getCellByOrder(order: number, lessonContentCells: Cell[]): Cell | null {
  if (!lessonContentCells.length) return null

  return lessonContentCells.find((cell, index) => {
    const cellOrder = cell.order !== undefined ? cell.order : index
    return cellOrder === order
  }) || null
}

/**
 * 获取文本预览（去除HTML标签，截取前N字符）
 * @param cell - Cell对象
 * @param maxLength - 最大长度
 * @returns 预览文本
 */
export function getTextPreview(cell: Cell, maxLength: number = 100): string {
  if (cell.type !== 'text') return ''

  const content = (cell as any).content
  if (!content?.html) return '文本内容'

  // 去除HTML标签
  const text = content.html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  return text.slice(0, maxLength) + (text.length > maxLength ? '...' : '')
}

/**
 * 获取代码预览（截取前50行）
 * @param cell - Cell对象
 * @returns 代码预览文本
 */
export function getCodePreview(cell: Cell): string {
  if (cell.type !== 'code') return ''

  const content = (cell as any).content
  if (!content?.code) return '// 代码内容'

  const lines = content.code.split('\n')
  return lines.slice(0, 10).join('\n') + (lines.length > 10 ? '\n...' : '')
}

/**
 * 处理缩略图加载错误
 * @param event - 错误事件
 */
export function handleThumbnailError(event: Event): void {
  const img = event.target as HTMLImageElement
  if (img) {
    img.style.display = 'none'
    // 显示默认图标
    const parent = img.parentElement
    if (parent && !parent.querySelector('.preview-thumbnail-content')) {
      const content = document.createElement('div')
      content.className = 'preview-thumbnail-content'
      content.innerHTML = `
        <svg class="preview-thumbnail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      `
      parent.appendChild(content)
    }
  }
}

/**
 * 设置模块项引用（用于Vue的ref处理）
 * @param refs - Map存储的引用
 * @param el - 元素
 * @param index - 索引
 */
export function setModuleItemRef(refs: Map<number, HTMLElement>, el: any, index: number): void {
  if (el) {
    // 处理 Vue 组件实例
    const element = (el as any).$el || el
    if (element instanceof HTMLElement) {
      refs.set(index, element)
    }
  } else {
    refs.delete(index)
  }
}

/**
 * 滚动到选中的模块
 * @param moduleListRef - 模块列表容器引用
 * @param moduleItemRefs - 模块项引用Map
 * @param selectedCellIndex - 选中的Cell索引
 */
export function scrollToSelectedModule(
  moduleListRef: ReturnType<typeof import('vue').ref<HTMLElement | null>>,
  moduleItemRefs: Map<number, HTMLElement>,
  selectedCellIndex: number
): void {
  if (selectedCellIndex < 0 || !moduleListRef.value) return

  const moduleElement = moduleItemRefs.get(selectedCellIndex)
  if (moduleElement) {
    // 使用平滑滚动，将模块滚动到视口中心
    moduleElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    })
  }
}
