/**
 * 课堂同步调试工具
 * 用于诊断教师端导播台和学生端显示不一致的问题
 */

export function debugCellMapping(config: {
  lessonContent: any[]
  dbCells: Array<{ id: number; order: number; cell_type: string }>
  displayCellIds: number[]
  source: 'teacher' | 'student'
}) {
  const { lessonContent, dbCells, displayCellIds, source } = config
  
  console.group(`🔍 [${source.toUpperCase()}] Cell 映射调试`)
  
  // 1. 基本信息
  console.log('📊 基本信息:')
  console.log('  - lessonContent 数量:', lessonContent.length)
  console.log('  - dbCells 数量:', dbCells.length)
  console.log('  - displayCellIds:', displayCellIds)
  
  // 2. lessonContent 详情
  console.log('\n📋 lessonContent 详情:')
  lessonContent.forEach((cell, index) => {
    console.log(`  [${index}]`, {
      id: cell.id,
      order: cell.order !== undefined ? cell.order : index,
      type: cell.type,
      title: cell.title || '(无标题)',
    })
  })
  
  // 3. dbCells 详情
  console.log('\n📦 dbCells 详情:')
  if (dbCells.length === 0) {
    console.error('  ❌ dbCells 为空！')
  } else {
    dbCells.forEach((dbCell) => {
      console.log(`  [ID ${dbCell.id}]`, {
        order: dbCell.order,
        cell_type: dbCell.cell_type,
      })
    })
  }
  
  // 4. ID 到 order 的映射
  console.log('\n🗺️  ID → order 映射:')
  const idToOrderMap = new Map<number, number>()
  dbCells.forEach((dbCell) => {
    if (dbCell.id && dbCell.order !== undefined) {
      idToOrderMap.set(dbCell.id, dbCell.order)
      console.log(`  ${dbCell.id} → order ${dbCell.order}`)
    }
  })
  
  // 5. order 到 index 的映射
  console.log('\n🗺️  order → lessonContent index 映射:')
  const orderToIndexMap = new Map<number, number>()
  lessonContent.forEach((cell, index) => {
    const order = cell.order !== undefined ? cell.order : index
    orderToIndexMap.set(order, index)
    const dbCell = dbCells.find(c => c.order === order)
    console.log(`  order ${order} → index ${index}`, {
      cellId: cell.id,
      dbCellId: dbCell?.id || null,
    })
  })
  
  // 6. 显示的 Cell IDs 映射
  console.log('\n🎯 displayCellIds 映射到 lessonContent:')
  if (displayCellIds.length === 0) {
    console.log('  (无选中的模块)')
  } else {
    displayCellIds.forEach((id) => {
      const order = idToOrderMap.get(id)
      const index = order !== undefined ? orderToIndexMap.get(order) : undefined
      const cell = index !== undefined ? lessonContent[index] : null
      
      if (cell) {
        console.log(`  ✅ ID ${id} → order ${order} → index ${index}`, {
          cellTitle: cell.title || '(无标题)',
          cellType: cell.type,
        })
      } else {
        console.error(`  ❌ ID ${id} → order ${order} → 无法找到对应的 Cell!`)
        console.error(`     - order: ${order}`)
        console.error(`     - index: ${index}`)
        console.error(`     - orderToIndexMap has order ${order}:`, orderToIndexMap.has(order || -1))
      }
    })
  }
  
  // 7. 诊断建议
  console.log('\n💡 诊断建议:')
  
  if (dbCells.length === 0) {
    console.error('  ⚠️  dbCells 为空，这会导致 ID 映射失败')
    console.error('     建议：检查 API /cells/lesson/{lesson_id} 是否正常返回数据')
  } else if (dbCells.length !== lessonContent.length) {
    console.warn(`  ⚠️  dbCells (${dbCells.length}) 与 lessonContent (${lessonContent.length}) 数量不一致`)
    console.warn('     可能原因：')
    console.warn('     - 教案 content 中有些 Cell 还未保存到数据库')
    console.warn('     - 数据库中有已删除但 lessonContent 中不存在的 Cell')
  }
  
  const unmappedIds = displayCellIds.filter((id) => {
    const order = idToOrderMap.get(id)
    const index = order !== undefined ? orderToIndexMap.get(order) : undefined
    return index === undefined
  })
  
  if (unmappedIds.length > 0) {
    console.error(`  ⚠️  ${unmappedIds.length} 个 Cell ID 无法映射到 lessonContent:`, unmappedIds)
    console.error('     建议：')
    console.error('     - 检查这些 ID 对应的 Cell 是否存在于数据库中')
    console.error('     - 检查 order 值是否一致')
  }
  
  console.groupEnd()
  
  return {
    summary: {
      lessonContentCount: lessonContent.length,
      dbCellsCount: dbCells.length,
      displayCellIdsCount: displayCellIds.length,
      unmappedIdsCount: unmappedIds.length,
      isHealthy: dbCells.length > 0 && unmappedIds.length === 0,
    },
    maps: {
      idToOrder: Object.fromEntries(idToOrderMap),
      orderToIndex: Object.fromEntries(orderToIndexMap),
    },
    unmappedIds,
  }
}

