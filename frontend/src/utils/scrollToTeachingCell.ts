/**
 * 授课预览：将主内容区滚动到与导播台当前模块对应的 Cell（CellContainer 上的 data-cell-*）
 */

import type { Lesson } from '@/types/lesson'
import type { Cell } from '@/types/cell'
import { getCellId } from '@/utils/cellId'
import {
  normalizeContentToSections,
  sectionsToFlatCells,
  isContentWithSections,
} from '@/utils/lessonContent'

function escapeAttrSelector(value: string): string {
  if (typeof CSS !== 'undefined' && typeof CSS.escape === 'function') {
    return CSS.escape(value)
  }
  return value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')
}

export function scrollToTeachingPreviewCell(options: {
  cellId?: string | number | null
  flatIndex?: number | null
}): void {
  const { cellId, flatIndex } = options
  let el: Element | null = null

  if (cellId != null && cellId !== '') {
    const idStr = String(cellId)
    el = document.querySelector(`[data-cell-id="${escapeAttrSelector(idStr)}"]`)
  }

  if (!el && typeof flatIndex === 'number' && flatIndex >= 0) {
    el = document.querySelector(`[data-cell-index="${flatIndex}"]`)
  }

  el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

/** 与导播台 lessonContentCells 一致：全课扁平 Cell 列表 */
export function getFlatCellsFromLesson(lesson: Lesson | null | undefined): Cell[] {
  if (!lesson?.content) return []
  const c = lesson.content
  if (Array.isArray(c)) return c
  if (isContentWithSections(c)) {
    return sectionsToFlatCells(normalizeContentToSections(c))
  }
  return []
}

/**
 * 根据会话状态解析应在预览区滚动的扁平索引与 cellId（与 TeacherControlPanel 的 currentModuleIndex 规则对齐）
 */
export function getTeachingPreviewScrollTarget(
  session: Record<string, unknown> | null | undefined,
  lesson: Lesson | null | undefined
): { flatIndex: number; cellId: string | number | null } {
  const flatCells = getFlatCellsFromLesson(lesson)
  if (!session || flatCells.length === 0) return { flatIndex: -1, cellId: null }

  const settings = (session.settings || {}) as Record<string, unknown>
  const orders = settings.display_cell_orders as number[] | undefined
  if (Array.isArray(orders) && orders.length > 0) {
    const firstOrder = orders[0]
    const index = flatCells.findIndex((cell, idx) => {
      const cellOrder = cell.order !== undefined ? cell.order : idx
      return cellOrder === firstOrder
    })
    if (index >= 0) {
      const c = flatCells[index]
      return {
        flatIndex: index,
        cellId: c?.id != null && c.id !== '' ? c.id : null,
      }
    }
  }

  const rawCid = session.current_cell_id ?? session.currentCellId
  if (rawCid !== undefined && rawCid !== null && rawCid !== 0 && rawCid !== '0') {
    const currentId =
      typeof rawCid === 'string' && /^\d+$/.test(rawCid.trim())
        ? parseInt(rawCid, 10)
        : rawCid
    const index = flatCells.findIndex((cell, idx) => {
      const id = getCellId(cell)
      if (typeof id === 'number' && id === currentId) return true
      if (typeof id === 'string' && typeof currentId === 'number') {
        const numId = parseInt(id, 10)
        if (!isNaN(numId) && numId === currentId) return true
      }
      if (typeof id === 'string' && String(id) === String(currentId)) return true
      if (idx === currentId) return true
      if (cell.order !== undefined && cell.order === currentId) return true
      return false
    })
    if (index >= 0) {
      const c = flatCells[index]
      return {
        flatIndex: index,
        cellId: c?.id != null && c.id !== '' ? c.id : null,
      }
    }
  }

  return { flatIndex: -1, cellId: null }
}
