/**
 * 导航管理 Composable
 *
 * 管理课堂模块导航、选择和切换功能
 */

import { ref, type Ref, computed, nextTick } from 'vue'
import { CellType, type Cell } from '@/types/cell'
import classroomSessionService from '@/services/classroomSession'
import { getCellId as getCellIdUtil, toNumericId, isUUID } from '@/utils/cellId'
import { findFlatCellIndexByOrder } from '@/components/Classroom/cellUtils'

function isActivityCell(cell: Cell): boolean {
  const t = cell.type as string
  return t === CellType.ACTIVITY || t.toLowerCase() === 'activity'
}

export interface UseNavigationOptions {
  /**
   * 会话对象
   */
  session: Ref<any | null>

  /**
   * 加载状态
   */
  loading: Ref<boolean>

  /**
   * 选中的Cell索引
   */
  selectedCellIndex: Ref<number>

  /**
   * 课程内容Cells数组
   */
  lessonContentCells: Ref<Cell[]>

  /**
   * 是否为多选模式
   */
  isMultiSelectMode: Ref<boolean>

  /**
   * 规范化的会话状态
   */
  normalizedSessionStatus: Ref<string | null>

  /**
   * 当前模块索引
   */
  currentModuleIndex: Ref<number>

  /**
   * 判断模块是否激活
   */
  isModuleActive: (cell: Cell, index: number) => boolean

  /**
   * 滚动到选中的模块
   */
  scrollToSelectedModule: () => void

  /**
   * 加载参与者列表
   */
  loadParticipants: () => void | Promise<void>

  /**
   * 确保活动模块的数据库记录存在
   */
  ensureActivityCellExists: (cell: Cell, order: number) => Promise<number | null>

  /**
   * 加载数据库 Cell 记录
   */
  loadDbCells: () => Promise<void>

  /**
   * 数据库 Cell 记录
   */
  dbCells: Ref<Array<{ id: number | string; order: number; cell_type: string }>>
}

export function useNavigation(options: UseNavigationOptions) {
  const {
    session,
    loading,
    selectedCellIndex,
    lessonContentCells,
    isMultiSelectMode,
    normalizedSessionStatus,
    currentModuleIndex,
    isModuleActive,
    scrollToSelectedModule,
    loadParticipants,
    ensureActivityCellExists,
    loadDbCells,
    dbCells,
  } = options

  /**
   * 判断是否可以上一模块
   */
  const canGoPrev = computed(() => {
    return currentModuleIndex.value > 0
  })

  /**
   * 判断是否可以下一模块
   */
  const canGoNext = computed(() => {
    if (!lessonContentCells.value.length) return false
    return currentModuleIndex.value >= 0 && currentModuleIndex.value < lessonContentCells.value.length - 1
  })

  /**
   * 获取 Cell ID
   */
  function getCellId(cell: Cell): number | string | null {
    return getCellIdUtil(cell)
  }

  /**
   * 验证会话状态是否允许导航
   */
  function validateSessionStateForNavigation(): boolean {
    if (!session.value) {
      console.warn('无法导航：会话不存在')
      return false
    }

    const status = normalizedSessionStatus.value
    if (status !== 'active' && status !== 'teaching') {
      const statusMessages: Record<string, string> = {
        'pending': '请先点击"开始上课"按钮，等待教师开始上课',
        'preparing': '请先点击"开始上课"按钮，等待教师开始上课',
        'paused': '会话已暂停，请先继续会话',
        'ended': '会话已结束，无法导航'
      }
      const message = statusMessages[status!] || '会话状态不正确，无法导航'
      alert(message)
      return false
    }

    return true
  }

  /**
   * 核心：导航控制（切换显示的模块）
   */
  async function handleControlBoardNavigate(
    cellId: number | string | null,
    cellOrder: number | null,
    action: 'toggle' | 'add' | 'remove' = 'toggle',
    multiSelect: boolean = false
  ) {
    if (!validateSessionStateForNavigation()) {
      return
    }

    loading.value = true
    try {
      // 获取当前选中的 orders（从 settings 中获取，如果有的话）
      let displayOrders: number[] = []
      const currentSettings = session.value.settings as any
      if (currentSettings?.display_cell_orders) {
        displayOrders = [...currentSettings.display_cell_orders]
      } else if (currentSettings?.display_cell_ids && lessonContentCells.value.length > 0) {
        // 向后兼容：如果只有 display_cell_ids，转换成 orders
        displayOrders = currentSettings.display_cell_ids
          .map((id: number) => {
            const cell = lessonContentCells.value.find((c: any) => getCellId(c) === id)
            if (cell) {
              const cellIndex = lessonContentCells.value.indexOf(cell)
              return cell.order !== undefined ? cell.order : cellIndex
            }
            return -1
          })
          .filter((order: number) => order >= 0)
      }

      // 如果是隐藏所有（cellId === 0、"0" 或 null）且不是多选模式
      const isHideAll = (cellId === 0 || cellId === "0" || cellId === null) && cellOrder === null && !multiSelect
      if (isHideAll) {
        displayOrders = []
      } else if (cellOrder !== null) {
        // 根据 action 更新 displayOrders
        if (action === 'add') {
          if (multiSelect) {
            if (!displayOrders.includes(cellOrder)) {
              displayOrders.push(cellOrder)
            }
          } else {
            // 单选模式：活动模块等走 add 时也应只播当前格，避免与 displayOrders 叠加多条
            displayOrders = [cellOrder]
          }
        } else if (action === 'remove') {
          displayOrders = displayOrders.filter(o => o !== cellOrder)
        } else if (action === 'toggle') {
          if (displayOrders.includes(cellOrder)) {
            displayOrders = displayOrders.filter(o => o !== cellOrder)
          } else {
            displayOrders = multiSelect ? [...displayOrders, cellOrder] : [cellOrder]
          }
        }
      }

      // 发送请求
      const requestData = {
        displayCellOrders: displayOrders,
        action,
      }

      const updatedSession = await classroomSessionService.navigateToCell(session.value.id, requestData)

      // 确保更新后的会话状态正确（不要丢失状态）
      if (updatedSession) {
        const upd = updatedSession as Record<string, unknown>
        session.value = {
          ...session.value,
          ...updatedSession,
          status: session.value.status, // 保持原有状态，导航不应该改变会话状态
          id: session.value.id,
          // navigate API 映射为 currentCellId；导播台与授课滚动监听仍读 current_cell_id
          current_cell_id:
            (upd.current_cell_id as number | undefined) ??
            (upd.currentCellId as number | undefined) ??
            (session.value as any).current_cell_id,
        }
      }

      // 导航后立即刷新学生列表
      await loadParticipants()

      // 如果点击的是活动模块，确保数据库记录存在
      if (cellOrder !== null && lessonContentCells.value.length > 0) {
        const clickedIndex = findFlatCellIndexByOrder(
          lessonContentCells.value,
          cellOrder,
          selectedCellIndex.value
        )
        const clickedCell =
          clickedIndex >= 0 ? lessonContentCells.value[clickedIndex] : undefined

        if (clickedCell && isActivityCell(clickedCell)) {
          const createdCellId = await ensureActivityCellExists(clickedCell, cellOrder)
          // 重新加载 dbCells 以获取最新数据
          await loadDbCells()

          // 如果创建成功，等待一小段时间让数据库记录生效
          if (createdCellId) {
            await new Promise(resolve => setTimeout(resolve, 500))
            // 再次加载确保获取到最新数据
            await loadDbCells()
          }
        }
      }

      // 如果 dbCells 为空，重新加载（可能活动模块刚创建）
      if (dbCells.value.length === 0) {
        await loadDbCells()
      }

      // 更新selectedCellIndex
      if (cellId === 0) {
        selectedCellIndex.value = -1
      } else if (cellOrder !== null && cellOrder !== undefined && lessonContentCells.value.length > 0) {
        const hint =
          selectedCellIndex.value >= 0
            ? selectedCellIndex.value
            : currentModuleIndex.value
        const index = findFlatCellIndexByOrder(lessonContentCells.value, cellOrder, hint)
        if (index >= 0) {
          selectedCellIndex.value = index
        } else {
          selectedCellIndex.value = cellOrder < lessonContentCells.value.length ? cellOrder : -1
        }
      } else if (cellId && lessonContentCells.value.length > 0) {
        // 通过 cellId 查找索引
        const index = lessonContentCells.value.findIndex((cell) => {
          const id = getCellId(cell)
          if (typeof id === 'number' && id === cellId) return true
          if (typeof id === 'string') {
            const numId = parseInt(id, 10)
            if (!isNaN(numId) && numId === cellId) return true
          }
          return false
        })
        if (index >= 0) {
          selectedCellIndex.value = index
        } else {
          // 如果找不到，尝试使用返回的 currentCellId 对应的索引
          if (updatedSession?.currentCellId) {
            const currentId = updatedSession.currentCellId
            const foundIndex = lessonContentCells.value.findIndex((cell) => {
              const id = getCellId(cell)
              return id === currentId || (typeof id === 'string' && String(id) === String(currentId))
            })
            if (foundIndex >= 0) {
              selectedCellIndex.value = foundIndex
            }
          }
        }
      }

      // 滚动到选中的模块
      await nextTick()
      setTimeout(() => {
        scrollToSelectedModule()
      }, 100)
    } catch (error: any) {
      console.error('Failed to navigate from control board:', error)
      const errorMessage = error.response?.data?.detail || error.message || '切换内容失败'
      alert(errorMessage)
    } finally {
      loading.value = false
    }
  }

  /**
   * 处理模块项点击
   */
  function handleModuleItemClick(cell: Cell, index: number) {
    if (loading.value) return

    // 立即更新 selectedCellIndex，确保按钮状态及时更新
    selectedCellIndex.value = index

    const cellId = getCellId(cell)
    const cellOrder = cell.order !== undefined ? cell.order : index

    // 活动用 add：多选时叠加且不重复；单选时在 navigate 内归一为仅 [cellOrder]（再次点击同一活动仍为单格，不触发 toggle 取消）
    const actionItem: 'toggle' | 'add' | 'remove' = isActivityCell(cell) ? 'add' : 'toggle'

    handleControlBoardNavigate(cellId, cellOrder, actionItem, isMultiSelectMode.value)
  }

  /**
   * 导航到上一模块
   */
  function handlePrevModule() {
    if (!canGoPrev.value || !lessonContentCells.value.length) return
    const prevIndex = currentModuleIndex.value - 1
    const prevCell = lessonContentCells.value[prevIndex]
    if (prevCell) {
      handleModuleItemClick(prevCell, prevIndex)
    }
  }

  /**
   * 导航到下一模块
   */
  function handleNextModule() {
    if (!canGoNext.value || !lessonContentCells.value.length) return
    const nextIndex = currentModuleIndex.value + 1
    const nextCell = lessonContentCells.value[nextIndex]
    if (nextCell) {
      handleModuleItemClick(nextCell, nextIndex)
    }
  }

  /**
   * 处理单选框/复选框点击（防止事件冒泡，并处理取消选中）
   */
  function handleModuleCheckboxClick(cell: Cell, index: number, event: Event) {
    event.stopPropagation()

    if (loading.value) {
      return
    }

    const isCurrentlyActive = isModuleActive(cell, index)
    const cellId = getCellId(cell)
    const cellOrder = cell.order !== undefined ? cell.order : index

    if (isMultiSelectMode.value) {
      // 多选模式：复选框逻辑
      if (isCurrentlyActive) {
        // 取消选中：从选中列表中移除
        handleControlBoardNavigate(cellId, cellOrder, 'remove', true)
      } else {
        // 选中：添加到选中列表
        handleControlBoardNavigate(cellId, cellOrder, 'add', true)
      }
    } else {
      // 单选模式：单选框逻辑
      if (isCurrentlyActive) {
        // 如果点击已选中的单选框，取消选中（隐藏所有内容）
        const target = event.target as HTMLElement
        const checkboxWrapper = target.closest('.module-item-checkbox, .module-card-checkbox')
        const radioInput = checkboxWrapper?.querySelector('input[type="radio"]') as HTMLInputElement | undefined
        if (radioInput) {
          event.preventDefault()
          radioInput.checked = false
          // 隐藏所有内容
          handleControlBoardNavigate(null, null, 'toggle', false)
        }
      }
    }
  }

  /**
   * 处理单选框/复选框变化
   */
  function handleModuleCheckboxChange(cell: Cell, index: number, event: Event) {
    if (loading.value) {
      return
    }

    const target = event.target as HTMLInputElement
    const isChecked = target.checked
    const cellId = getCellId(cell)
    const cellOrder = cell.order !== undefined ? cell.order : index

    if (isMultiSelectMode.value) {
      // 多选模式：复选框逻辑（已在 handleModuleCheckboxClick 中处理，这里作为备用）
      if (isChecked) {
        handleControlBoardNavigate(cellId, cellOrder, 'add', true)
      } else {
        handleControlBoardNavigate(cellId, cellOrder, 'remove', true)
      }
    } else {
      // 单选模式：单选框逻辑
      // 只处理选中新项的情况（取消选中已在 handleModuleCheckboxClick 中处理）
      if (!isChecked) {
        return
      }

      // 选中新项（单选模式，multiSelect = false，会自动清除其他选中项）
      if (cellId && typeof cellId === 'string' && isUUID(cellId)) {
        handleControlBoardNavigate(null, cellOrder, 'toggle', false)
      } else {
        const numericId = toNumericId(cellId)
        if (numericId) {
          handleControlBoardNavigate(numericId, null, 'toggle', false)
        } else {
          handleControlBoardNavigate(null, cellOrder, 'toggle', false)
        }
      }
    }
  }

  /**
   * 隐藏所有内容
   */
  async function handleHideAll() {
    if (!validateSessionStateForNavigation()) {
      return
    }

    loading.value = true
    try {
      // 使用 displayCellOrders: [] 来隐藏所有内容
      session.value = await classroomSessionService.navigateToCell(session.value.id, {
        displayCellOrders: [],
      })
      selectedCellIndex.value = -1
    } catch (error: any) {
      console.error('Failed to hide content:', error)
      const errorMessage = error.response?.data?.detail || error.message || '隐藏内容失败'
      alert(errorMessage)
    } finally {
      loading.value = false
    }
  }

  return {
    // 计算属性
    canGoPrev,
    canGoNext,

    // 导航方法
    handleControlBoardNavigate,
    handleModuleItemClick,
    handlePrevModule,
    handleNextModule,
    handleModuleCheckboxClick,
    handleModuleCheckboxChange,
    handleHideAll,
  }
}
