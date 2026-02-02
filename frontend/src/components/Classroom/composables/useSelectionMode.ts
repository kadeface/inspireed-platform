/**
 * 选择模式管理 Composable
 *
 * 管理单选/多选模式的切换和状态
 */

import { ref, watch, type Ref } from 'vue'
import type { Cell } from '@/types/cell'

export interface UseSelectionModeOptions {
  /**
   * 加载状态
   */
  loading: Ref<boolean>

  /**
   * 会话对象
   */
  session: Ref<any | null>

  /**
   * 选中的Cell订单号列表
   */
  displayCellOrders: Ref<number[]>

  /**
   * 课程内容Cells数组
   */
  lessonContentCells: Ref<Cell[]>

  /**
   * 导航控制函数（可选，用于在模式切换时更新选中状态）
   */
  handleControlBoardNavigate?: (
    cellId: number | string | null,
    cellOrder: number | null,
    action: 'toggle' | 'add' | 'remove',
    multiSelect: boolean
  ) => void | Promise<void>
}

export function useSelectionMode(options: UseSelectionModeOptions) {
  const {
    loading,
    session,
    displayCellOrders,
    lessonContentCells,
    handleControlBoardNavigate,
  } = options

  // 多选模式：false=单选，true=多选
  const isMultiSelectMode = ref(false)

  /**
   * 切换选择模式（单选/多选）
   */
  async function toggleSelectionMode() {
    if (loading.value || !session.value) return

    const wasMultiSelect = isMultiSelectMode.value
    isMultiSelectMode.value = !isMultiSelectMode.value

    // 如果从多选切换到单选，且当前有多个选中项，只保留第一个
    if (!isMultiSelectMode.value && wasMultiSelect && displayCellOrders.value.length > 1) {
      // 只有在有 handleControlBoardNavigate 函数时才调用
      if (!handleControlBoardNavigate) {
        console.warn('handleControlBoardNavigate 未提供，跳过导航更新')
        return
      }

      const firstOrder = displayCellOrders.value[0]
      const cell = lessonContentCells.value.find((cell, idx) => {
        const cellOrder = cell.order !== undefined ? cell.order : idx
        return cellOrder === firstOrder
      })
      if (cell) {
        const id = getCellId(cell)
        const cellIndex = lessonContentCells.value.indexOf(cell)
        const order = cell.order !== undefined ? cell.order : cellIndex
        // 切换到单选模式，只显示第一个选中的项
        await handleControlBoardNavigate(id, order, 'toggle', false)
      }
    }
    // 如果从单选切换到多选，且当前有选中项，保持选中状态（已经是多选模式，可以继续添加）
  }

  /**
   * 获取 Cell ID
   */
  function getCellId(cell: Cell): number | string | null {
    if (cell.id !== undefined) {
      return cell.id
    }
    if (cell.order !== undefined) {
      return cell.order
    }
    return null
  }

  /**
   * 监听 displayCellOrders 变化，自动同步多选模式状态
   */
  watch(displayCellOrders, (orders) => {
    if (Array.isArray(orders) && orders.length > 1) {
      // 如果有多个选中项，自动切换到多选模式
      if (!isMultiSelectMode.value) {
        isMultiSelectMode.value = true
      }
    } else if (Array.isArray(orders) && orders.length <= 1) {
      // 如果只有一个或没有选中项，可以保持当前模式（不强制切换）
      // 这样用户可以手动选择模式
    }
  }, { immediate: true })

  return {
    // 状态
    isMultiSelectMode,

    // 方法
    toggleSelectionMode,
  }
}
