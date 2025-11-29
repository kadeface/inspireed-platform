/**
 * CellId 解析 Composable
 * 统一处理 cellId 的解析逻辑（支持数字 ID 和 UUID）
 */

import { ref, computed } from 'vue'
import type { ActivityCell } from '../types/cell'

interface UseCellIdResolverOptions {
  cell: ActivityCell
  lessonId: number
}

export function useCellIdResolver(options: UseCellIdResolverOptions) {
  const { cell, lessonId } = options
  
  // 存储 UUID 到数字 ID 的映射
  const cellIdMap = ref<Map<string, number>>(new Map())
  const resolvingCellId = ref(false)
  
  // 解析后的 cellId（可能是数字或 UUID 字符串）
  const cellId = ref<number | string>(0)
  const cellIdUuid = ref<string | null>(null)
  
  /**
   * 初始化 cellId
   */
  async function initCellId(): Promise<void> {
    const id = cell.id
    console.log('🔍 Initializing cellId, input:', id, 'type:', typeof id)
    
    if (typeof id === 'number') {
      if (!isNaN(id)) {
        cellId.value = id
        console.log('✅ Using numeric cellId:', id)
        return
      }
    }
    
    if (typeof id === 'string') {
      const parsed = parseInt(id, 10)
      if (!isNaN(parsed)) {
        cellId.value = parsed
        console.log('✅ Parsed string cellId to number:', parsed)
        return
      }
      
      // 如果是 UUID，后端现在支持直接使用 UUID
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
      if (uuidPattern.test(id)) {
        console.log('🔍 Detected UUID, backend will handle it. Using UUID directly.')
        cellId.value = 0  // 使用 0 作为标记
        cellIdUuid.value = id  // 存储原始 UUID
        console.log('✅ Will use UUID string for API calls:', id)
        return
      }
      
      console.error('❌ Invalid cellId string (not UUID and not numeric):', id)
    }
    
    console.error('❌ Invalid cellId:', id)
    cellId.value = 0
  }
  
  /**
   * 获取实际的 cellId（可能是数字或 UUID 字符串）
   */
  function getActualCellId(): number | string {
    if (cellId.value === 0 && cellIdUuid.value) {
      return cellIdUuid.value
    }
    return cellId.value
  }
  
  /**
   * 通过 API 解析 UUID 到数字 ID（如果需要）
   */
  async function resolveCellIdFromApi(uuid: string): Promise<number | null> {
    if (cellIdMap.value.has(uuid)) {
      return cellIdMap.value.get(uuid) || null
    }

    if (resolvingCellId.value) {
      // 如果正在解析，等待一下
      await new Promise(resolve => setTimeout(resolve, 100))
      return cellIdMap.value.get(uuid) || null
    }

    try {
      resolvingCellId.value = true
      console.log('🔍 Resolving UUID to numeric ID:', uuid, 'for lesson:', lessonId)
      
      // 首先尝试从 API 获取 lesson 的所有 cells
      const { api } = await import('../services/api')
      let response: any
      try {
        response = await api.get(`/cells/lesson/${lessonId}`)
      } catch (error: any) {
        console.warn('⚠️ Failed to fetch cells from API, will try to create cell:', error)
        response = { data: [] }
      }
      
      const cells = response?.data || []
      console.log('📦 Fetched cells from API:', cells.length, 'cells')
      
      // 尝试通过 order 和 type 匹配 cell
      const currentCellOrder = cell.order
      const currentCellType = cell.type
      
      // 首先尝试精确匹配：order 和 type 都匹配
      let matchedCell = cells.find((c: any) => {
        return c.order === currentCellOrder && c.cell_type === currentCellType
      })
      
      // 如果精确匹配失败，尝试只匹配 order
      if (!matchedCell) {
        matchedCell = cells.find((c: any) => {
          return c.order === currentCellOrder
        })
      }
      
      // 如果还是找不到，尝试通过 title 匹配
      if (!matchedCell && cell.title) {
        matchedCell = cells.find((c: any) => {
          return c.title === cell.title && c.cell_type === currentCellType
        })
      }
      
      if (matchedCell && matchedCell.id) {
        const numericId = typeof matchedCell.id === 'number' ? matchedCell.id : parseInt(matchedCell.id, 10)
        if (!isNaN(numericId)) {
          cellIdMap.value.set(uuid, numericId)
          console.log('✅ Resolved UUID to numeric ID:', uuid, '->', numericId)
          return numericId
        }
      }
      
      // 如果找不到匹配的 cell，尝试创建一个新的 cell 记录
      console.log('⚠️ No matching cell found, attempting to create cell record...')
      try {
        const cellCreateData = {
          lesson_id: lessonId,
          cell_type: currentCellType,
          title: cell.title || '',
          content: cell.content || {},
          config: cell.config || {},
          order: currentCellOrder,
          editable: cell.editable ?? false,
        }
        
        console.log('📤 Creating cell:', cellCreateData)
        const createResponse = await api.post('/cells', cellCreateData) as any
        const newCell = createResponse.data
        
        if (newCell && newCell.id) {
          const numericId = typeof newCell.id === 'number' ? newCell.id : parseInt(newCell.id, 10)
          if (!isNaN(numericId)) {
            cellIdMap.value.set(uuid, numericId)
            console.log('✅ Created new cell and resolved UUID to numeric ID:', uuid, '->', numericId)
            return numericId
          }
        }
      } catch (createError: any) {
        console.error('❌ Failed to create cell:', createError)
      }
      
      console.warn('⚠️ Could not resolve or create cell for UUID:', uuid)
      return null
    } catch (error: any) {
      console.error('❌ Failed to resolve cell ID from API:', error)
      return null
    } finally {
      resolvingCellId.value = false
    }
  }
  
  /**
   * 验证 cellId 是否有效
   */
  function isValidCellId(): boolean {
    const actualId = getActualCellId()
    return actualId !== 0 && actualId !== null && actualId !== undefined
  }
  
  /**
   * 获取用于存储的 cellId（对于 UUID，使用哈希值）
   */
  function getCellIdForStorage(): number {
    const actualId = getActualCellId()
    if (typeof actualId === 'string') {
      // 使用 UUID 的前 8 个字符的哈希值作为临时数字 ID
      const hash = actualId.split('-')[0]
      return parseInt(hash, 16) % 1000000  // 转换为 0-999999 的数字
    }
    return actualId as number
  }
  
  return {
    // 状态
    cellId: computed(() => cellId.value),
    cellIdUuid: computed(() => cellIdUuid.value),
    isResolving: computed(() => resolvingCellId.value),
    
    // 方法
    initCellId,
    getActualCellId,
    resolveCellIdFromApi,
    isValidCellId,
    getCellIdForStorage,
  }
}

