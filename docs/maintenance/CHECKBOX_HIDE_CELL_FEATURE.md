# 导播台复选框取消勾选隐藏模块功能验证

## 📋 功能描述

当教师在导播台中取消勾选某个模块的复选框时，学生端的对应模块应该被隐藏。

## 🔍 功能流程

### 1. 教师端操作

**位置**: `frontend/src/components/Classroom/ClassroomControlBoard.vue`

**触发事件**: `handleCheckboxChange` (第 342 行)

```typescript
// 当复选框被取消勾选时
if (action === 'remove') {
  displayOrders = displayOrders.filter(o => o !== cellOrder)
}
```

**发送导航请求**: `handleControlBoardNavigate` (第 848 行)

```typescript
// 根据 action 更新 displayOrders
if (action === 'remove') {
  displayOrders = displayOrders.filter(o => o !== cellOrder)
}

// 发送到后端
const requestData = {
  displayCellOrders: displayOrders,  // 已移除对应 order 的数组
  action,
}
```

### 2. 后端处理

**位置**: `backend/app/api/v1/classroom_sessions.py`

**函数**: `navigate_to_cell` (第 394 行)

```python
# 直接保存更新后的 display_cell_orders
new_settings["display_cell_orders"] = data.display_cell_orders
setattr(session, "settings", new_settings)

# 通过 WebSocket 广播变化
await ws_manager.broadcast_to_session(
    message={
        "type": "cell_changed",
        "data": {
            "display_cell_orders": data.display_cell_orders,  # 包含更新后的数组
        }
    },
    session_id=session_id,
)
```

### 3. 学生端接收

**位置**: `frontend/src/composables/useClassroomSession.ts`

**WebSocket 监听**: `setupWebSocketListeners` (第 278 行)

```typescript
websocketService.on('cell_changed', (message: WebSocketMessage) => {
  if (message.data.display_cell_orders !== undefined) {
    newSession.settings = {
      ...session.value.settings,
      display_cell_orders: message.data.display_cell_orders,  // 更新为新的数组
    }
  }
  session.value = newSession  // 触发响应式更新
})
```

### 4. 学生端显示过滤

**位置**: `frontend/src/pages/Student/LessonView.vue`

**计算属性**: `filteredCells` (第 386 行)

```typescript
const displayOrders = settings?.display_cell_orders
if (displayOrders && Array.isArray(displayOrders)) {
  // 如果 displayOrders 是空数组，返回空数组（隐藏所有Cell）
  if (displayOrders.length === 0) {
    return []
  }
  
  // 根据 order 过滤，只显示在 displayOrders 中的 Cell
  return lesson.value.content.filter((cell, index) => {
    const cellOrder = cell.order !== undefined ? cell.order : index
    return displayOrders.includes(cellOrder)  // 不在数组中的会被过滤掉
  })
}
```

## ✅ 功能验证

### 测试步骤

1. **教师端**：
   - 进入授课模式
   - 在导播台中勾选多个模块（例如：模块 1、2、3）
   - 取消勾选模块 2 的复选框

2. **预期结果**：
   - 学生端应该只显示模块 1 和 3
   - 模块 2 应该被隐藏

3. **检查点**：
   - ✅ 教师端 `displayOrders` 是否正确移除了对应的 `cellOrder`
   - ✅ 后端是否正确保存了更新后的 `display_cell_orders`
   - ✅ WebSocket 是否正确广播了更新后的数组
   - ✅ 学生端是否正确接收并更新了 `session.settings.display_cell_orders`
   - ✅ 学生端的 `filteredCells` 是否正确过滤了隐藏的模块

## 🔧 已修复的问题

### 1. 空数组处理

**问题**: 原代码在检查 `displayOrders.length > 0` 时，如果 `displayOrders` 是空数组，会走到 `return []`，但逻辑不够清晰。

**修复**: 明确处理空数组情况，添加详细日志。

```typescript
// 修复前
if (displayOrders && Array.isArray(displayOrders) && displayOrders.length > 0) {
  // ...
}
return []  // 空数组也会走到这里

// 修复后
if (displayOrders && Array.isArray(displayOrders)) {
  if (displayOrders.length === 0) {
    console.log('⚠️ display_cell_orders 为空数组，隐藏所有 Cell')
    return []
  }
  // ...
}
```

### 2. 过滤日志

**新增**: 添加了详细的过滤日志，方便调试。

```typescript
const filteredByOrders = lesson.value.content.filter((cell, index) => {
  const cellOrder = cell.order !== undefined ? cell.order : index
  const isIncluded = displayOrders.includes(cellOrder)
  if (!isIncluded) {
    console.log(`🚫 隐藏 Cell: order=${cellOrder}, title=${cell.title || cell.type}`)
  }
  return isIncluded
})
```

## 📝 相关文件

- `frontend/src/components/Classroom/ClassroomControlBoard.vue` - 导播台组件
- `frontend/src/components/Classroom/TeacherControlPanel.vue` - 教师控制面板
- `frontend/src/pages/Student/LessonView.vue` - 学生端视图
- `frontend/src/composables/useClassroomSession.ts` - 课堂会话组合式函数
- `backend/app/api/v1/classroom_sessions.py` - 课堂会话 API

## 🐛 可能的问题

### 1. WebSocket 连接问题

如果学生端没有正确连接到 WebSocket，可能无法接收到更新消息。

**检查方法**:
- 查看浏览器控制台是否有 WebSocket 连接错误
- 检查 `useClassroomSession.ts` 中的 WebSocket 连接状态

### 2. 响应式更新问题

如果 Vue 的响应式系统没有正确检测到变化，可能需要强制更新。

**已修复**: 在 `useClassroomSession.ts` 中，通过创建新对象来触发响应式更新。

### 3. Order 匹配问题

如果 Cell 的 `order` 值与 `display_cell_orders` 中的值不匹配，可能导致过滤失败。

**检查方法**:
- 查看控制台日志中的 `displayOrders` 和 `cellOrder` 值
- 确保 `cell.order` 与 `display_cell_orders` 中的值一致

## ✅ 总结

功能逻辑应该是完整的：

1. ✅ 教师端取消勾选 → 发送 `remove` action
2. ✅ 前端计算新的 `displayOrders` → 移除对应的 `cellOrder`
3. ✅ 后端保存并广播 → WebSocket 发送更新后的数组
4. ✅ 学生端接收并更新 → 更新 `session.settings.display_cell_orders`
5. ✅ 学生端过滤显示 → `filteredCells` 根据 `display_cell_orders` 过滤

如果功能仍然不工作，请检查：
- WebSocket 连接状态
- 浏览器控制台的错误日志
- `display_cell_orders` 的值是否正确传递

