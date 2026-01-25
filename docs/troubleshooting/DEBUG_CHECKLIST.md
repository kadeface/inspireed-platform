# 学生端内容不显示问题调试清单

## 请在浏览器控制台查看以下日志

### 1️⃣ 收到 WebSocket 消息
应该看到：
```
🔄 收到内容切换消息: { display_cell_orders: [X], ... }
```

**检查项**：
- [ ] 是否收到了这条消息？
- [ ] `display_cell_orders` 的值是什么？（例如 `[0]` 或 `[1]`）

---

### 2️⃣ 内容已同步
应该看到：
```
✅ 内容已同步: { displayCellOrders: [X], currentCellId: ... }
```

**检查项**：
- [ ] `displayCellOrders` 是否有值？
- [ ] 值是否和上一步一致？

---

### 3️⃣ 初始状态更新（如果刚连接）
应该看到：
```
🔧 初始状态已更新: { status: "active", displayCellOrders: [X], ... }
```

**检查项**：
- [ ] `displayCellOrders` 是否有值？

---

### 4️⃣ 过滤 Cells 检查
**最关键的日志**，应该看到：
```
🔍 shouldSyncDisplay = true, 检查 settings: {
  hasSettings: true,
  settings: {...},
  display_cell_orders: [X],
  isArray: true,
  length: 1
}
```

**检查项**：
- [ ] `hasSettings` 是 `true` 还是 `false`？
- [ ] `display_cell_orders` 是什么值？
- [ ] `isArray` 是 `true` 还是 `false`？
- [ ] `length` 是多少？

---

### 5️⃣ 使用新方式过滤
如果上一步都正常，应该看到：
```
✅ 学生端使用新方式 display_cell_orders: [X]
```

**如果看不到这条日志**，说明条件判断失败了。

---

### 6️⃣ 过滤结果
应该看到：
```
✅ 过滤结果（新方式）: {
  totalCells: 10,
  displayOrders: [X],
  filteredCount: 1,
  firstCellOrder: 0
}
```

**检查项**：
- [ ] `totalCells` 是多少？（应该 > 0）
- [ ] `displayOrders` 的值是什么？
- [ ] `filteredCount` 是多少？（如果是 0，说明没有匹配的 Cell）
- [ ] `firstCellOrder` 是什么？（可能是 0 或 1 或 undefined）

---

## 常见问题诊断

### 问题 A：看不到步骤 4 的日志
**原因**：`filteredCells` computed 没有被触发
**解决方案**：检查是否真的在课堂模式下

### 问题 B：步骤 4 显示 `hasSettings: false` 或 `display_cell_orders: undefined`
**原因**：session.settings 没有正确更新
**解决方案**：检查步骤 2 和步骤 3 的日志

### 问题 C：步骤 6 显示 `filteredCount: 0`
**原因**：Cell 的 order 值和 display_cell_orders 不匹配

**可能的情况**：
1. Cell 的 order 是 1，但 display_cell_orders 是 [0]
2. Cell 没有 order 属性（firstCellOrder 是 undefined）

**解决方案**：
- 检查 `firstCellOrder` 的值
- 检查 `displayOrders` 的值
- 两者应该能匹配上

---

## 请提供以下信息

复制以下内容到聊天框：

```
### 控制台日志
步骤1 - 收到消息：[粘贴日志]
步骤2 - 内容同步：[粘贴日志]
步骤4 - 过滤检查：[粘贴日志]
步骤5 - 使用新方式：[有/无此日志]
步骤6 - 过滤结果：[粘贴日志]

### 关键数据
- display_cell_orders 的值：
- firstCellOrder 的值：
- filteredCount 的值：
- totalCells 的值：
```

---

## 如果还是找不到问题

请在控制台执行以下代码，然后把结果发给我：

```javascript
// 检查 classroomSession 状态
console.log('=== 调试信息 ===')
console.log('lesson.content 数量:', document.__VUE__?.lesson?.content?.length)
console.log('lesson.content[0]:', document.__VUE__?.lesson?.content?.[0])
console.log('classroomSession:', document.__VUE__?.classroomSession)
console.log('isInClassroomMode:', document.__VUE__?.isInClassroomMode)
console.log('shouldSyncDisplay:', document.__VUE__?.shouldSyncDisplay)
```

**注意**：上述代码可能不工作，因为 Vue 3 的调试方式不同。

## 临时解决方案

如果调试困难，可以临时关闭严格同步模式：

1. 在 `useClassroomSession.ts` 中找到：
```typescript
const shouldSyncDisplay = computed(() => {
  if (!isInClassroomMode.value) {
    return false
  }
  const syncMode = session.value?.settings?.sync_mode
  return syncMode === 'strict' || syncMode === undefined || syncMode === null
})
```

2. 临时改为：
```typescript
const shouldSyncDisplay = computed(() => {
  return false  // 临时禁用严格同步，显示所有内容
})
```

这样学生端就会显示所有内容，虽然不会严格同步，但至少能看到内容。

