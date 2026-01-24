/**
 * Lesson.content 与 Sections 互转
 * - 旧格式：Cell[] 平铺
 * - 新格式：{ sections: [ { id, name, type, order, is_collapsed?, cells } ] }
 */

import type { Cell } from '../types/cell'
import type { LessonContentWithSections, SectionInContent } from '../types/section'

const DEFAULT_SECTION_NAMES = [
  '教学目标、教学重点难点、学生学情分析',
  '教学过程',
  '课堂练习',
  '课程资源',
  '反思总结',
] as const

const TEACHING_PROCESS_ORDER = 1

/**
 * 将 Lesson.content 标准化为 sections 数组
 * - 若为 { sections }：直接使用，并补齐 5 个默认大环节（若缺失）
 * - 若为 Cell[]：生成 5 个默认大环节，把所有 cell 放入「教学过程」
 */
export function normalizeContentToSections(
  content: Cell[] | LessonContentWithSections | undefined | null
): SectionInContent[] {
  if (!content) {
    return getEmptyDefaultSections()
  }

  if (isContentWithSections(content)) {
    const sections = content.sections || []
    // 确保至少有 5 个默认大环节
    const defaultMap = new Map(
      DEFAULT_SECTION_NAMES.map((name, i) => [name, { order: i, filled: false }])
    )
    const result: SectionInContent[] = []
    const seen = new Set<string>()

    for (const s of sections) {
      const sec = { ...s, cells: s.cells || [] }
      if (sec.id) seen.add(String(sec.id))
      result.push(sec)
      if (DEFAULT_SECTION_NAMES.includes(s.name as any)) {
        defaultMap.set(s.name, { ...defaultMap.get(s.name)!, filled: true })
      }
    }

    // 补缺失的默认大环节（按 order 插入）
    for (let i = 0; i < DEFAULT_SECTION_NAMES.length; i++) {
      const name = DEFAULT_SECTION_NAMES[i]
      if (defaultMap.get(name)?.filled) continue
      const id = `sec-default-${i}`
      if (seen.has(id)) continue
      result.push({
        id,
        name,
        type: 'default',
        order: i,
        is_collapsed: false,
        cells: [],
      })
    }
    result.sort((a, b) => a.order - b.order)
    return result
  }

  // 旧格式：Cell[]
  const cells = Array.isArray(content) ? content : []
  const sections = getEmptyDefaultSections()
  const teaching = sections.find((s) => s.order === TEACHING_PROCESS_ORDER)
  if (teaching) {
    teaching.cells = cells.map((c, i) => ({ ...c, order: i }))
  }
  return sections
}

function getEmptyDefaultSections(): SectionInContent[] {
  return DEFAULT_SECTION_NAMES.map((name, i) => ({
    id: `sec-default-${i}`,
    name,
    type: 'default' as const,
    order: i,
    is_collapsed: false,
    cells: [],
  }))
}

export function isContentWithSections(
  c: Cell[] | LessonContentWithSections | null | undefined
): c is LessonContentWithSections {
  return !!c && typeof c === 'object' && 'sections' in c && Array.isArray((c as any).sections)
}

/**
 * 将 sections 转为 Lesson.content 新格式（用于保存）
 */
export function sectionsToContent(sections: SectionInContent[]): LessonContentWithSections {
  return {
    sections: sections.map((s) => ({
      ...s,
      cells: s.cells || [],
    })),
  }
}

/**
 * 从 sections 扁平出所有 cells（兼容需要平铺的逻辑，如幻灯片、cell 数统计）
 */
export function sectionsToFlatCells(sections: SectionInContent[]): Cell[] {
  return sections.flatMap((s) => s.cells || [])
}
