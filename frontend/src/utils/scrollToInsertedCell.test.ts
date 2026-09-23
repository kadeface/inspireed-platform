import { afterEach, describe, expect, it, vi } from 'vitest'
import { findInsertedCellElement, scrollToInsertedCell } from './scrollToInsertedCell'

describe('scrollToInsertedCell', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('scrolls to the inserted cell by id when no list ref is available', () => {
    document.body.innerHTML = `
      <div data-cell-id="cell-new" data-cell-index="12">新单元</div>
    `
    const target = document.querySelector('[data-cell-id="cell-new"]') as HTMLElement
    const scrollIntoView = vi.fn()
    target.scrollIntoView = scrollIntoView

    expect(scrollToInsertedCell('cell-new')).toBe(true)
    expect(scrollIntoView).toHaveBeenCalledWith({
      behavior: 'auto',
      block: 'center',
      inline: 'nearest',
    })
    expect(target.style.outline).toBe('2px solid #3b82f6')
  })

  it('falls back to the flat cell index', () => {
    document.body.innerHTML = `<div data-cell-index="3"></div>`
    expect(findInsertedCellElement(3)?.getAttribute('data-cell-index')).toBe('3')
  })
})
