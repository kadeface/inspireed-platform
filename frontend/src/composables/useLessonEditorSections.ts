/**
 * 教案编辑器 - 大环节（Sections）与 content 双向同步、标签 Sortable、增删改
 */

import { ref, watch, nextTick, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import Sortable from 'sortablejs'
import {
  normalizeContentToSections,
  renumberCellsGloballyInSections,
  sectionsToContent,
} from '../utils/lessonContent'
import type { SectionInContent } from '../types/section'
import { useLessonStore } from '../store/lesson'

export function useLessonEditorSections(
  tabsContainerRef: Ref<HTMLElement | undefined>
) {
  const route = useRoute()
  const lessonStore = useLessonStore()

  const sections = ref<SectionInContent[]>([])
  const activeSectionIndex = ref(0)
  const editingTabId = ref<string | null>(null)
  const editingTabNameRef = ref<HTMLInputElement | HTMLInputElement[] | null>(null)

  let tabsSortableInstance: ReturnType<typeof Sortable.create> | null = null

  // 从 lesson 加载后同步到 sections
  watch(
    [
      () => Number(route.params.id),
      () => {
        const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
        return cur?.id
      },
    ],
    ([routeId, lessonId]) => {
      const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
      if (routeId && lessonId && cur && Number(routeId) === Number(lessonId)) {
        sections.value = normalizeContentToSections(cur.content)
      }
    },
    { immediate: true }
  )

  // sections 变化时同步回 currentLesson.content
  watch(
    sections,
    () => {
      const cur = (lessonStore as any).currentLesson?.value ?? (lessonStore as any).currentLesson
      if (cur) (cur as any).content = sectionsToContent(sections.value)
    },
    { deep: true }
  )

  function handleSectionUpdate(sectionIndex: number, payload: Partial<SectionInContent>) {
    const s = sections.value[sectionIndex]
    if (s) Object.assign(s, payload)
  }

  function handleSectionDelete(sectionIndex: number) {
    const s = sections.value[sectionIndex]
    if (!s || s.type === 'default') return
    const teaching = sections.value.find((sec) => sec.order === 1)
    if (s.cells?.length && teaching) {
      teaching.cells = teaching.cells ?? []
      teaching.cells.push(...s.cells)
      renumberCellsGloballyInSections(sections.value)
    }
    sections.value.splice(sectionIndex, 1)
    if (activeSectionIndex.value >= sections.value.length) {
      activeSectionIndex.value = Math.max(0, sections.value.length - 1)
    }
  }

  function handleAddSection(showToast: (t: 'success' | 'error' | 'warning', m: string) => void) {
    const maxOrder = sections.value.length
      ? Math.max(...sections.value.map((s) => s.order), -1) + 1
      : 0
    sections.value.push({
      id: `sec-custom-${Date.now()}`,
      name: '新增大环节',
      type: 'custom',
      order: maxOrder,
      is_collapsed: false,
      cells: [],
    })
    showToast('success', '已添加大环节，双击标题可重命名')
    activeSectionIndex.value = sections.value.length - 1
  }

  function handleTabDblClick(sec: SectionInContent) {
    if (sec.type === 'custom') {
      editingTabId.value = sec.id
      nextTick(() => {
        const r = editingTabNameRef.value
        if (Array.isArray(r) && r.length > 0) {
          r[0]?.focus()
        } else if (r && typeof (r as any).focus === 'function') {
          (r as any).focus()
        }
      })
    }
  }

  function initTabsSortable() {
    if (!tabsContainerRef.value) return
    if (tabsSortableInstance) {
      tabsSortableInstance.destroy()
      tabsSortableInstance = null
    }
    tabsSortableInstance = Sortable.create(tabsContainerRef.value, {
      animation: 200,
      handle: '.drag-handle',
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      onEnd(evt) {
        const { oldIndex, newIndex } = evt
        if (oldIndex != null && newIndex != null && oldIndex !== newIndex) {
          const item = sections.value.splice(oldIndex, 1)[0]
          sections.value.splice(newIndex, 0, item)
          if (activeSectionIndex.value === oldIndex) {
            activeSectionIndex.value = newIndex
          } else if (activeSectionIndex.value > oldIndex && activeSectionIndex.value <= newIndex) {
            activeSectionIndex.value--
          } else if (activeSectionIndex.value < oldIndex && activeSectionIndex.value >= newIndex) {
            activeSectionIndex.value++
          }
        }
      },
    })
  }

  function destroySortable() {
    if (tabsSortableInstance) {
      tabsSortableInstance.destroy()
      tabsSortableInstance = null
    }
  }

  return {
    sections,
    activeSectionIndex,
    editingTabId,
    editingTabNameRef,
    handleSectionUpdate,
    handleSectionDelete,
    handleAddSection,
    handleTabDblClick,
    initTabsSortable,
    destroySortable,
  }
}
