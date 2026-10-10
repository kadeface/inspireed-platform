import { describe, expect, it } from 'vitest'
import { classroomDisplayProgress } from './classroomProgress'

const fourCells = [{ order: 0 }, { order: 1 }, { order: 2 }, { order: 3 }]

describe('classroomDisplayProgress', () => {
  it('moves with the current module instead of the number of checked modules', () => {
    expect(classroomDisplayProgress(fourCells, [0])).toBe(25)
    expect(classroomDisplayProgress(fourCells, [1])).toBe(50)
    expect(classroomDisplayProgress(fourCells, [3])).toBe(100)
  })

  it('uses the furthest displayed module when several are checked', () => {
    expect(classroomDisplayProgress(fourCells, [0, 2])).toBe(75)
  })

  it('matches cells by their order, not by array position alone', () => {
    const cells = [{ order: 10 }, { order: 20 }, { order: 30 }, { order: 40 }]
    expect(classroomDisplayProgress(cells, [30])).toBe(75)
  })

  it('returns 0 when nothing is on screen', () => {
    expect(classroomDisplayProgress(fourCells, [])).toBe(0)
    expect(classroomDisplayProgress([], [0])).toBe(0)
  })
})
