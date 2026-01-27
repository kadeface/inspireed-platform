# Cell ID 生成与管理策略

## 概述

本系统采用**双重 ID 体系**来管理 Cell（教学单元）：
- **前端临时 ID**：使用 UUID v4 作为临时标识符，用于前端编辑时的唯一性
- **后端持久 ID**：使用数据库自增整数作为持久标识符

## ID 体系说明

### 1. 前端临时 ID（UUID）

**用途**：
- 在编辑教案时，为新创建的 Cell 提供唯一标识
- 存储在 `lesson.content` JSON 数组中
- 在保存到数据库之前使用

**格式**：
- UUID v4 格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- 示例：`a6121660-02ea-4c80-8fe0-8002928b31e5`

**生成位置**：
- `frontend/src/pages/Teacher/LessonEditor.vue`: `getDefaultCell()` 函数
- `frontend/src/components/Lesson/CreateLessonModal.vue`: 创建新 Cell 时
- `frontend/src/components/Activity/ActivityItemModal.vue`: 创建活动选项时

### 2. 后端持久 ID（Integer）

**用途**：
- 数据库主键
- API 接口标识符
- 关联关系外键

**格式**：
- 整数，自增
- 示例：`1`, `2`, `123`

**存储位置**：
- `cells` 表的 `id` 字段（主键）

## ID 映射机制

### 问题场景

1. **编辑阶段**：Cell 只有 UUID，尚未保存到数据库
2. **导航阶段**：需要根据 UUID 或 `order` 找到对应的数据库 ID
3. **课堂控制**：导播台点击时，Cell ID 可能是 UUID

### 解决方案

#### 方案 A：通过 `cell_order` 映射（推荐）

当 Cell ID 是 UUID 时，使用 `order`（索引）进行导航：

```typescript
// 前端：检测 UUID
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
if (uuidPattern.test(cellId)) {
  // 使用 cellOrder 进行导航
  await navigateToCell({ cellOrder: cell.order })
}
```

后端导航 API 会：
1. 首先尝试通过 `cell_id`（数字 ID）查找
2. 如果找不到，通过 `cell_order` 和 `lesson_id` 查找
3. 如果仍然找不到，从 `lesson.content[cell_order]` 中读取并创建 Cell 记录

#### 方案 B：提前创建 Cell 记录

在保存教案时，同步创建所有 Cell 的记录：

```python
# 后端：保存教案时
for index, cell_data in enumerate(lesson_content):
    cell_uuid = cell_data.get('id')
    # 通过 UUID 或 order 查找已存在的 Cell
    existing_cell = await find_cell_by_uuid_or_order(lesson_id, cell_uuid, index)
    if not existing_cell:
        # 创建新 Cell
        new_cell = Cell(
            lesson_id=lesson_id,
            cell_type=cell_data.get('type'),
            order=index,
            ...
        )
        db.add(new_cell)
```

**优点**：
- 导航时总能在数据库中找到 Cell
- 避免动态创建带来的延迟

**缺点**：
- 草稿状态的 Cell 也会创建记录
- 需要额外的 UUID 映射表（或使用 `order` 匹配）

## 当前实现状态

### 前端

1. **LessonEditor.vue**：
   - ✅ 使用 `uuidv4()` 生成临时 ID
   - ✅ 保存时将 `lesson.content` 发送到后端
   - ❌ 未同步创建 Cell 记录（仅保存到 `lesson.content`）

2. **TeacherControlPanel.vue**：
   - ✅ 检测 UUID 格式
   - ✅ 使用 `cellOrder` 进行导航
   - ✅ 处理 `order` 到数据库 ID 的映射

3. **ClassroomControlBoard.vue**：
   - ✅ 传递 `cellOrder` 给父组件
   - ✅ 正确处理 UUID `cellId`

### 后端

1. **navigate_to_cell API** (`backend/app/api/v1/classroom_sessions.py:346`)：
   - ✅ 支持 `cell_id`（数字 ID）
   - ✅ 支持 `cell_order`（索引）
   - ✅ 从 `lesson.content` 创建缺失的 Cell 记录

2. **Cell 模型** (`backend/app/models/cell.py`)：
   - ✅ 使用 `Integer` 主键
   - ✅ `order` 字段用于排序和查找

## 推荐的最佳实践

### 1. 统一使用 `order` 进行导航

**原因**：
- `order` 是稳定的（即使 Cell ID 变化也不会改变）
- 前端总是知道 Cell 的 `order`（数组索引）
- 后端可以通过 `order + lesson_id` 快速查找

**实现**：
```typescript
// 前端导航时
const cellOrder = cells.findIndex(cell => cell.id === cellId)
await navigateToCell({ cellOrder })
```

### 2. 在保存教案时同步 Cell 记录

**建议流程**：
1. 用户编辑教案（使用 UUID）
2. 保存教案时：
   - 保存 `lesson.content`
   - 同步创建/更新 `cells` 表记录（通过 `order` 匹配）
3. 导航时：
   - 优先使用 `cell_id`（如果已存在）
   - 否则使用 `cell_order`（自动查找或创建）

### 3. UUID 仅用于前端临时标识

**规则**：
- UUID **不**传递到后端 API（除非作为元数据）
- 导航时转换为 `cellOrder`
- 创建 Cell 时使用数据库返回的数字 ID

## 需要改进的地方

### 高优先级

1. **统一导航逻辑**：
   - ✅ 已完成：`TeacherControlPanel.vue` 和 `ClassroomControlBoard.vue` 已正确处理 UUID
   - ⚠️ 待确认：其他组件是否也需要类似处理

2. **清理临时 UUID 处理**：
   - `ActivityViewer.vue` 中的 `resolveCellIdFromApi()` 函数比较复杂
   - 建议简化为统一的 `order` 映射逻辑

### 中优先级

1. **保存时同步 Cell**：
   - 在保存教案 API 中添加逻辑，自动创建/更新 Cell 记录
   - 这样导航时总能找到 Cell

2. **类型定义优化**：
   - 明确区分临时 ID（UUID）和持久 ID（number）
   - TypeScript 类型定义更加严格

### 低优先级

1. **性能优化**：
   - 批量创建 Cell 记录（减少数据库查询）
   - 缓存 UUID 到数字 ID 的映射

## 相关文件

### 前端
- `frontend/src/pages/Teacher/LessonEditor.vue` - 生成 UUID
- `frontend/src/components/Classroom/TeacherControlPanel.vue` - UUID 检测和导航
- `frontend/src/components/Classroom/ClassroomControlBoard.vue` - 传递 cellOrder
- `frontend/src/components/Activity/ActivityViewer.vue` - UUID 解析逻辑

### 后端
- `backend/app/models/cell.py` - Cell 模型定义
- `backend/app/api/v1/classroom_sessions.py` - 导航 API
- `backend/app/api/v1/cells.py` - Cell CRUD API

## 参考资料

- [UUID v4 规范](https://tools.ietf.org/html/rfc4122)
- [SQLAlchemy Integer 主键](https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.Integer)

