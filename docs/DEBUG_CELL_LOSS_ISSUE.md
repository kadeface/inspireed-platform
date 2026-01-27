# 调试 Cell 丢失问题

## 问题描述

用户新增模块并手动保存，前端显示保存成功（23个cells），但重新加载后只有22个cells。

## 调试步骤

### 1. 检查前端保存时的数据

在浏览器控制台中，在保存**之前**执行以下命令：

```javascript
// 获取当前 lesson store
const lessonStore = window.__VUE_DEVTOOLS_GLOBAL_HOOK__.apps[0]._instance.proxy.$pinia._s.get('lesson')

// 检查 cells 和 content 是否一致
console.log('=== 保存前检查 ===')
console.log('cells.length:', lessonStore.cells.length)
console.log('currentLesson.content.length:', lessonStore.currentLesson.content.length)
console.log('是否一致:', lessonStore.cells.length === lessonStore.currentLesson.content.length)

// 检查最后一个 cell 的结构
const lastCell = lessonStore.cells[lessonStore.cells.length - 1]
console.log('最后一个 cell:', lastCell)
console.log('最后一个 cell 的类型:', typeof lastCell)
console.log('最后一个 cell 是否为对象:', lastCell !== null && typeof lastCell === 'object')
console.log('最后一个 cell 的字段:', Object.keys(lastCell))

// 检查所有 cells 的类型
console.log('所有 cells 类型检查:')
lessonStore.cells.forEach((cell, idx) => {
  const isDict = cell !== null && typeof cell === 'object' && !Array.isArray(cell)
  console.log(`  Cell[${idx}]: type=${typeof cell}, isDict=${isDict}, id=${cell?.id}, type=${cell?.type}`)
})
```

### 2. 检查保存请求的数据

在 Network 面板中：
1. 找到 `PUT /api/v1/lessons/76` 请求
2. 查看 Request Payload
3. 检查 `content` 字段的长度
4. 检查 `content` 数组中每个元素是否都是对象

### 3. 检查保存响应的数据

在 Network 面板中：
1. 查看同一个请求的 Response
2. 检查返回的 `content` 字段的长度
3. 对比请求和响应的 `content` 长度是否一致

### 4. 检查后端日志

在后端日志中搜索关键信息：

```bash
# 查找教案 76 的详细保存日志
tail -200 logs/backend.log | grep -A 10 -B 10 "教案 76"

# 查找被过滤的 cell
tail -200 logs/backend.log | grep -E "(无效|invalid|移除)"

# 查找 Pydantic 验证错误
tail -200 logs/backend.log | grep -E "(ValidationError|validation error)"
```

## 可能的原因

### 原因 1: 前端 cells 和 content 不同步

**症状：** `cells.length !== currentLesson.content.length`

**解决方案：** 在保存前确保同步：
```typescript
currentLesson.value.content = [...cells.value]
```

### 原因 2: 某个 cell 不是有效的对象

**症状：** 某个 cell 是 `null`、`undefined` 或其他类型

**解决方案：** 在添加 cell 时验证数据结构：
```typescript
function addCell(cell: Cell) {
  if (!cell || typeof cell !== 'object') {
    console.error('Invalid cell:', cell)
    return
  }
  if (!cell.id || !cell.type) {
    console.error('Cell missing required fields:', cell)
    return
  }
  currentLesson.value.content.push(cell)
}
```

### 原因 3: Pydantic 验证时过滤了某个 cell

**症状：** 后端日志中有 "ValidationError" 或 "validation error"

**解决方案：** 修改 Pydantic schema，使用更宽松的验证：
```python
from pydantic import field_validator

class LessonResponse(LessonBase):
    content: List[dict]
    
    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v):
        """确保 content 中每个元素都是字典"""
        if not isinstance(v, list):
            return []
        
        valid_cells = []
        for idx, cell in enumerate(v):
            if not isinstance(cell, dict):
                logger.warning(f"Cell[{idx}] 不是字典类型: {type(cell)}")
                continue
            valid_cells.append(cell)
        
        return valid_cells
```

### 原因 4: 并发保存导致数据覆盖

**症状：** 多次保存请求几乎同时发送

**解决方案：** 已实现保存锁机制（`isSavingInProgress`），应该不是这个问题

### 原因 5: 数据库 JSONB 字段的序列化问题

**症状：** 保存时是 23 个，但数据库中只有 22 个

**解决方案：** 在数据库层面检查：
```sql
SELECT 
  id, 
  title, 
  jsonb_array_length(content) as content_length,
  content
FROM lessons 
WHERE id = 76;
```

## 下一步

1. 先在浏览器控制台执行步骤 1 的代码
2. 记录所有输出
3. 查看 Network 请求/响应
4. 查看后端日志
5. 根据线索确定根本原因

