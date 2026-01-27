/**
 * Cell ID 工具函数
 * 
 * 用于统一处理前端临时 ID（UUID）和后端持久 ID（数字）的转换和检测
 * 
 * @see docs/design/CELL_ID_MANAGEMENT.md
 */

/**
 * UUID v4 格式的正则表达式
 */
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/**
 * 检查字符串是否为 UUID 格式
 * 
 * @param value - 要检查的值
 * @returns 如果是 UUID 格式返回 true，否则返回 false
 */
export function isUUID(value: string | number | null | undefined): boolean {
  if (typeof value !== 'string') {
    return false
  }
  return UUID_PATTERN.test(value)
}

/**
 * 检查值是否为有效的数字 ID
 * 
 * @param value - 要检查的值
 * @returns 如果是有效的数字 ID（正整数）返回 true，否则返回 false
 */
export function isValidNumericId(value: string | number | null | undefined): boolean {
  if (typeof value === 'number') {
    return value > 0 && Number.isInteger(value)
  }
  
  if (typeof value === 'string') {
    // 如果是 UUID 格式，不是数字 ID
    if (isUUID(value)) {
      return false
    }
    
    // 尝试解析为数字
    const parsed = parseInt(value, 10)
    // 严格检查：必须是纯数字字符串才能当作数字 ID
    return !isNaN(parsed) && parsed > 0 && value.trim() === parsed.toString()
  }
  
  return false
}

/**
 * 将值转换为数字 ID（如果不是 UUID）
 * 
 * @param value - 要转换的值
 * @returns 如果是数字或数字字符串返回数字，否则返回 null
 */
export function toNumericId(value: string | number | null | undefined): number | null {
  if (typeof value === 'number') {
    return value > 0 && Number.isInteger(value) ? value : null
  }
  
  if (typeof value === 'string') {
    // 如果是 UUID，返回 null
    if (isUUID(value)) {
      return null
    }
    
    // 尝试解析为数字
    const parsed = parseInt(value, 10)
    if (!isNaN(parsed) && parsed > 0 && value.trim() === parsed.toString()) {
      return parsed
    }
  }
  
  return null
}

/**
 * 获取 Cell ID（提取 cell.id 或 cell._dbId）
 * 
 * @param cell - Cell 对象
 * @returns Cell ID（可能是数字或 UUID 字符串）
 */
export function getCellId(cell: { id?: string | number; _dbId?: number }): string | number | null {
  if (cell._dbId) {
    return cell._dbId
  }
  return cell.id ?? null
}

/**
 * 构建导航请求数据
 * 
 * 根据 cellId 和 cellOrder 构建适合后端 API 的请求数据
 * 
 * @param cellId - Cell ID（可能是数字或 UUID）
 * @param cellOrder - Cell 的 order（索引）
 * @returns 请求数据对象，包含 cellId（数字）或 cellOrder
 * @throws 如果无法确定导航目标抛出错误
 */
export function buildNavigateRequest(
  cellId: string | number | null | undefined,
  cellOrder: number | null | undefined
): { cellId?: number; cellOrder?: number } {
  // cellId 为 0 或都为 null，隐藏所有内容
  if (cellId === 0 || (cellId === null && cellOrder === null)) {
    return { cellId: 0 }
  }
  
  // 尝试转换为数字 ID
  const numericId = toNumericId(cellId)
  if (numericId) {
    // 有有效的数字 ID，使用 ID
    return { cellId: numericId }
  }
  
  // 如果是 UUID 或无效 ID，使用 cellOrder
  if (cellOrder !== null && cellOrder !== undefined && cellOrder >= 0) {
    return { cellOrder }
  }
  
  // 无法确定导航目标
  throw new Error(
    `无法确定导航目标：cellId=${cellId} (类型: ${typeof cellId}), cellOrder=${cellOrder}`
  )
}

/**
 * 判断是否应该使用 cellOrder 进行导航
 * 
 * @param cellId - Cell ID（可能是数字或 UUID）
 * @returns 如果应该使用 cellOrder 返回 true
 */
export function shouldUseCellOrder(cellId: string | number | null | undefined): boolean {
  // 如果是 UUID，应该使用 cellOrder
  if (typeof cellId === 'string' && isUUID(cellId)) {
    return true
  }
  
  // 如果是 null 或 undefined，应该使用 cellOrder
  if (cellId === null || cellId === undefined) {
    return true
  }
  
  // 如果是 0，表示隐藏，不使用 cellOrder
  if (cellId === 0) {
    return false
  }
  
  // 如果是有效的数字 ID，不使用 cellOrder
  if (isValidNumericId(cellId)) {
    return false
  }
  
  // 其他情况，使用 cellOrder
  return true
}

