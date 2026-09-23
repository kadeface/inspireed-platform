/**
 * 编辑器插入单元后，把对应 Cell 滚进可视区域。
 * 不依赖 cellListRef：那个 ref 在编辑页没有绑到真实 DOM。
 */

function escapeAttrSelector(value: string): string {
  if (typeof CSS !== 'undefined' && typeof CSS.escape === 'function') {
    return CSS.escape(value)
  }
  return value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')
}

export function findInsertedCellElement(
  cellIdOrIndex: string | number,
  root: ParentNode = document
): HTMLElement | null {
  const selector =
    typeof cellIdOrIndex === 'string'
      ? `[data-cell-id="${escapeAttrSelector(cellIdOrIndex)}"]`
      : `[data-cell-index="${cellIdOrIndex}"]`
  return root.querySelector(selector) as HTMLElement | null
}

let highlighted: HTMLElement | null = null
let highlightTimer: number | null = null

function markInsertedCell(target: HTMLElement) {
  if (highlighted && highlighted !== target) {
    highlighted.style.outline = ''
    highlighted.style.outlineOffset = ''
  }
  highlighted = target
  target.style.outline = '2px solid #3b82f6'
  target.style.outlineOffset = '2px'
  if (highlightTimer != null) window.clearTimeout(highlightTimer)
  highlightTimer = window.setTimeout(() => {
    target.style.outline = ''
    target.style.outlineOffset = ''
    if (highlighted === target) highlighted = null
    highlightTimer = null
  }, 2000)
}

/** 立刻滚到插入的单元并描边，返回是否找到了目标。 */
export function scrollToInsertedCell(
  cellIdOrIndex: string | number,
  root: ParentNode = document
): boolean {
  const target = findInsertedCellElement(cellIdOrIndex, root)
  if (!target) return false
  target.scrollIntoView({ behavior: 'auto', block: 'center', inline: 'nearest' })
  markInsertedCell(target)
  return true
}
