/**
 * 教案编辑器 - Cell 相关逻辑：添加、更新、删除、移动、默认结构、滚动定位
 */

import { nextTick, type Ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { Cell, ReferenceMaterialCell } from '../types/cell'
import { CellType } from '../types/cell'
import type { LessonRelatedMaterial } from '../types/lesson'
import type { SectionInContent } from '../types/section'
import { getCellTypeName } from '../utils/lessonEditorHelpers'
import { renumberCellsGloballyInSections } from '../utils/lessonContent'
import { useLessonStore } from '../store/lesson'

export function getDefaultCell(cellType: (typeof CellType)[keyof typeof CellType], order: number): Cell {
  const baseCell = {
    id: uuidv4(),
    type: cellType,
    order,
    editable: true,
  }

  switch (cellType) {
    case CellType.TEXT:
      return { ...baseCell, type: CellType.TEXT, content: { html: '<p>在此输入文本内容...</p>' } } as Cell
    case CellType.CODE:
      return {
        ...baseCell,
        type: CellType.CODE,
        content: { code: '# 在此编写代码\nprint("Hello, World!")', language: 'python' as const },
        config: { environment: 'jupyterlite' as const },
      } as Cell
    case CellType.SIM:
      return {
        ...baseCell,
        type: CellType.SIM,
        content: {
          type: 'phet' as const,
          config: { width: 800, height: 600, autoplay: false, locale: 'zh_CN' },
        },
      } as Cell
    case CellType.CHART:
      return { ...baseCell, type: CellType.CHART, content: { chartType: 'bar' as const, data: {}, options: {} } } as Cell
    case CellType.CONTEST:
      return {
        ...baseCell,
        type: CellType.CONTEST,
        content: { title: '竞赛任务', description: '在此输入竞赛说明...', rules: {} },
      } as Cell
    case CellType.VIDEO:
      return {
        ...baseCell,
        type: CellType.VIDEO,
        content: { videoUrl: '', title: '', description: '' },
        config: { autoplay: false, controls: true, loop: false, muted: false },
      } as Cell
    case CellType.IMAGE:
      return {
        ...baseCell,
        type: CellType.IMAGE,
        content: { src: '', alt: '', caption: '' },
        config: { align: 'center' as const, maxWidth: '100%' },
      } as Cell
    case CellType.ACTIVITY:
      return {
        ...baseCell,
        type: CellType.ACTIVITY,
        content: {
          title: '新活动',
          description: '',
          activityType: 'quiz' as const,
          timing: { phase: 'in-class' as const },
          items: [],
          grading: { enabled: true, totalPoints: 100, autoGrade: false },
          submission: { allowMultiple: false, showFeedback: 'immediate' as const },
          display: { showProgress: true },
        },
        config: { allowOffline: true },
      } as Cell
    case CellType.FLOWCHART:
      return {
        ...baseCell,
        type: CellType.FLOWCHART,
        content: { nodes: [], edges: [], style: { theme: 'light' as const, layoutDirection: 'TB' as const } },
        config: { editable: true, showMinimap: false },
      } as Cell
    case CellType.BROWSER:
      return {
        ...baseCell,
        type: CellType.BROWSER,
        content: { url: '', title: '', description: '' },
        config: { allowFullscreen: true, allowNavigation: true, showToolbar: false, height: '600px' },
      } as Cell
    case CellType.INTERACTIVE:
      return {
        ...baseCell,
        type: CellType.INTERACTIVE,
        content: {
          url: '',
          html_code: undefined,
          teacher_html_code: undefined,
          student_html_code: undefined,
          title: '',
          description: '',
        },
        config: { allowFullscreen: true, height: '800px' },
      } as Cell
    default:
      throw new Error(`Unknown cell type: ${cellType}`)
  }
}

export function createReferenceMaterialCell(
  material: LessonRelatedMaterial,
  order: number
): ReferenceMaterialCell {
  return {
    id: uuidv4(),
    type: CellType.REFERENCE_MATERIAL,
    order,
    editable: true,
    content: {
      material_id: material.id,
      title: material.title,
      summary: material.summary,
      resource_type: material.resource_type,
      source_lesson_id: material.source_lesson_id,
      source_lesson_title: material.source_lesson_title,
      preview_url: material.preview_url,
      download_url: material.download_url,
      tags: material.tags ?? [],
      updated_at: material.updated_at,
      is_accessible: material.is_accessible,
    },
  }
}

export type CellTypeValue = (typeof CellType)[keyof typeof CellType]

export function useLessonEditorCells(
  sections: Ref<SectionInContent[]>,
  activeSectionIndex: Ref<number>,
  cellListRef: Ref<HTMLElement | undefined>,
  showToast: (type: 'success' | 'error' | 'warning', message: string) => void
) {
  const lessonStore = useLessonStore()

  function scrollToNewCell(index: number) {
    const el = cellListRef.value
    if (!el) return
    const target = el.querySelector(`[data-cell-index="${index}"]`) as HTMLElement | null
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
      target.classList.add('ring-2', 'ring-blue-400', 'ring-opacity-75')
      setTimeout(() => target.classList?.remove('ring-2', 'ring-blue-400', 'ring-opacity-75'), 2000)
    }
  }

  function handleAddCellToEnd(cellType: CellTypeValue) {
    // 如果 sections 为空，创建一个默认的 section
    if (sections.value.length === 0) {
      sections.value.push({
        id: 'sec-default-1',
        name: '教学过程',
        type: 'default',
        order: 1,
        is_collapsed: false,
        cells: [],
      })
      activeSectionIndex.value = 0
    }

    // 确保 activeSectionIndex 有效
    if (activeSectionIndex.value < 0 || activeSectionIndex.value >= sections.value.length) {
      activeSectionIndex.value = Math.max(0, sections.value.length - 1)
    }

    const activeSec = sections.value[activeSectionIndex.value]
    if (!activeSec) {
      console.error('无法添加模块：找不到活动的大环节', {
        sectionsCount: sections.value.length,
        activeSectionIndex: activeSectionIndex.value,
        sections: sections.value,
      })
      showToast('error', '无法添加模块：请先选择或创建一个大环节')
      return
    }

    const idx = (activeSec.cells?.length ?? 0)
    const newCell = getDefaultCell(cellType, idx)
    if (!activeSec.cells) activeSec.cells = []
    activeSec.cells.push(newCell)
    renumberCellsGloballyInSections(sections.value)
    showToast('success', `已添加${getCellTypeName(cellType)}`)
    const previousCellsCount = sections.value
      .slice(0, activeSectionIndex.value)
      .reduce((c, s) => c + (s.cells?.length || 0), 0)
    nextTick(() => scrollToNewCell(previousCellsCount + idx))
  }

  function handleAddCellInSection(sectionIndex: number, indexInSection: number, cellType: CellTypeValue) {
    // 验证参数
    if (sectionIndex === undefined || sectionIndex === null || typeof sectionIndex !== 'number') {
      console.error('无法添加模块：sectionIndex 参数无效', {
        sectionIndex,
        indexInSection,
        cellType,
        sectionsCount: sections.value.length,
      })
      showToast('error', '无法添加模块：参数错误，请刷新页面重试')
      return
    }

    if (indexInSection === undefined || indexInSection === null || typeof indexInSection !== 'number') {
      console.error('无法添加模块：indexInSection 参数无效', {
        sectionIndex,
        indexInSection,
        cellType,
      })
      showToast('error', '无法添加模块：参数错误，请刷新页面重试')
      return
    }

    // 如果 sections 为空，创建一个默认的 section
    if (sections.value.length === 0) {
      sections.value.push({
        id: 'sec-default-1',
        name: '教学过程',
        type: 'default',
        order: 1,
        is_collapsed: false,
        cells: [],
      })
      activeSectionIndex.value = 0
    }

    // 确保 sectionIndex 有效
    if (sectionIndex < 0 || sectionIndex >= sections.value.length) {
      console.error('无法添加模块：无效的大环节索引', {
        sectionIndex,
        sectionsCount: sections.value.length,
        sections: sections.value.map((s, i) => ({ index: i, id: s.id, name: s.name })),
      })
      showToast('error', '无法添加模块：无效的大环节索引')
      return
    }

    const sec = sections.value[sectionIndex]
    if (!sec) {
      console.error('无法添加模块：找不到指定的大环节', {
        sectionIndex,
        sectionsCount: sections.value.length,
      })
      showToast('error', '无法添加模块：找不到指定的大环节')
      return
    }

    // 确保 cells 数组存在且是响应式的
    if (!sec.cells) {
      sec.cells = []
    }
    
    // 确保 indexInSection 在有效范围内
    const maxIndex = sec.cells.length
    const safeIndex = Math.max(0, Math.min(indexInSection, maxIndex))
    
    try {
      const newCell = getDefaultCell(cellType, safeIndex)
      
      // 验证新创建的 cell 对象
      if (!newCell || !newCell.id || !newCell.type) {
        throw new Error('创建的 cell 对象无效')
      }
      
      // 确保 cells 数组是响应式的（通过重新赋值触发响应式更新）
      const currentCells = [...(sec.cells || [])]
      
      // 使用更安全的方式添加 cell
      if (safeIndex === maxIndex) {
        // 添加到末尾
        currentCells.push(newCell)
      } else {
        // 插入到指定位置
        currentCells.splice(safeIndex, 0, newCell)
      }
      
      // 重新赋值以触发响应式更新
      sec.cells = currentCells
      renumberCellsGloballyInSections(sections.value)
      
      showToast('success', `已添加${getCellTypeName(cellType)}`)
      const globalIndex =
        sections.value.slice(0, sectionIndex).reduce((a, s) => a + (s.cells?.length || 0), 0) + safeIndex
      nextTick(() => scrollToNewCell(globalIndex))
    } catch (error) {
      console.error('添加模块时出错:', error, {
        sectionIndex,
        indexInSection: safeIndex,
        cellType,
        cellsLength: sec.cells?.length || 0,
        section: {
          id: sec.id,
          name: sec.name,
          cellsCount: sec.cells?.length || 0,
        },
        errorStack: error instanceof Error ? error.stack : undefined,
      })
      showToast('error', `添加模块失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  function handleAddCellAt(cellType: CellTypeValue, index: number) {
    const teaching = sections.value.find((s) => s.order === 1)
    const idx = teaching ? Math.min(index, teaching.cells?.length ?? 0) : 0
    const si = sections.value.findIndex((s) => s.order === 1)
    if (si >= 0) handleAddCellInSection(si, idx, cellType)
  }

  function insertReferenceMaterial(material: LessonRelatedMaterial): number | null {
    const teaching = sections.value.find((s) => s.order === 1)
    if (!teaching || !lessonStore.currentLesson?.value) return null
    if (!teaching.cells) teaching.cells = []
    const indexInSection = teaching.cells.length
    const newCell = createReferenceMaterialCell(material, indexInSection)
    teaching.cells.push(newCell)
    return sections.value.reduce((a, s) => a + (s.cells?.length || 0), 0) - 1
  }

  function handleCellUpdate(updatedCell: Cell) {
    for (let i = 0; i < sections.value.length; i++) {
      const arr = sections.value[i].cells ?? []
      const idx = arr.findIndex((c) => String(c.id) === String(updatedCell.id))
      if (idx >= 0) {
        arr[idx] = updatedCell
        return
      }
    }
  }

  function handleDeleteCell(cellId: string) {
    if (!confirm('确定要删除这个单元吗？')) return
    for (let i = 0; i < sections.value.length; i++) {
      const arr = sections.value[i].cells ?? []
      const idx = arr.findIndex((c) => String(c.id) === String(cellId))
      if (idx >= 0) {
        arr.splice(idx, 1)
        renumberCellsGloballyInSections(sections.value)
        showToast('success', '单元已删除')
        return
      }
    }
  }

  function handleMoveUp(cellId: string) {
    for (let i = 0; i < sections.value.length; i++) {
      const arr = sections.value[i].cells ?? []
      const idx = arr.findIndex((c) => String(c.id) === String(cellId))
      if (idx > 0) {
        [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]
        renumberCellsGloballyInSections(sections.value)
        return
      }
    }
  }

  function handleMoveDown(cellId: string) {
    for (let i = 0; i < sections.value.length; i++) {
      const arr = sections.value[i].cells ?? []
      const idx = arr.findIndex((c) => String(c.id) === String(cellId))
      if (idx >= 0 && idx < arr.length - 1) {
        [arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]
        renumberCellsGloballyInSections(sections.value)
        return
      }
    }
  }

  return {
    getDefaultCell,
    createReferenceMaterialCell,
    scrollToNewCell,
    handleAddCellToEnd,
    handleAddCellInSection,
    handleAddCellAt,
    insertReferenceMaterial,
    handleCellUpdate,
    handleDeleteCell,
    handleMoveUp,
    handleMoveDown,
  }
}
