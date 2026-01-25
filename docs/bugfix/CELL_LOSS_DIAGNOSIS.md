# Cell 丢失问题诊断和修复

## 问题现象

用户新增模块并手动保存，前端显示保存成功（23个cells），但重新加载后只有22个cells。

## 已实施的修复

### 1. 移除前端"智能恢复"逻辑 (`frontend/src/store/lesson.ts`)

**问题：** 前端在保存后会用本地数据覆盖服务器返回的数据，导致保存死循环。

**修复：** 始终信任服务器返回的数据，不再用本地数据覆盖。

```typescript
// 修改前：
if (localContentLength > savedContentLength) {
  savedLesson.content = localContent  // 用本地数据覆盖
}

// 修改后：
if (localContentLength !== savedContentLength) {
  // 只记录警告，不覆盖数据
  console.warn('数据数量有差异，但信任服务器数据')
}
```

### 2. 优化前端 Watch 监听逻辑 (`frontend/src/pages/Teacher/LessonEditor.vue`)

**问题：** 保存过程中的状态更新也被监听为"未保存的更改"。

**修复：** 在保存过程中（`saveStatus === 'saving'`）忽略状态更新。

```typescript
watch(
  [() => currentLesson.value?.content, () => lessonTitle.value],
  () => {
    // 在保存过程中不触发此标记
    if (currentLesson.value && !isPreviewMode.value && saveStatus.value !== 'saving') {
      hasUnsavedChanges.value = true
    }
  },
  { deep: true }
)
```

### 3. 优化返回前的保存逻辑 (`frontend/src/pages/Teacher/LessonEditor.vue`)

**问题：** 即使没有变化也会触发保存。

**修复：** 只在真正有变化时保存。

```typescript
// 修改前：
if (hasActualChanges || currentCellsCount > 0) {
  // 总是保存
}

// 修改后：
if (hasActualChanges) {
  // 只在真正有变化时保存
} else {
  console.log('✅ 无未保存的更改，直接返回')
}
```

### 4. 增强后端日志 (`backend/app/api/v1/lessons.py`)

**问题：** 无法确定哪个 cell 被后端过滤了。

**修复：** 记录每个被移除的 cell 的详细信息。

```python
# 移除无效的 cell（如果无法修复）
if invalid_cells:
    logger.error(f"❌ 发现 {len(invalid_cells)} 个无法修复的无效 cell")
    # 记录每个被移除的 cell 的详细信息
    for idx in invalid_cells:
        if idx < len(new_content):
            invalid_cell = new_content[idx]
            logger.error(
                f"  被移除的 Cell[{idx}]: type={type(invalid_cell)}, "
                f"value={invalid_cell if not isinstance(invalid_cell, dict) else f'dict with keys: {list(invalid_cell.keys())}'}"
            )
```

### 5. 添加 Pydantic 验证日志 (`backend/app/schemas/lesson.py`)

**问题：** 无法确定 Pydantic 验证是否过滤了某些 cell。

**修复：** 为 `LessonCreate`、`LessonUpdate` 和 `LessonResponse` 添加 content 字段验证器。

```python
@field_validator("content", mode="before")
@classmethod
def validate_content(cls, v):
    """验证 content 字段，确保所有 cell 都是有效的字典"""
    import logging
    logger = logging.getLogger(__name__)
    
    if v is None:
        return []
    
    if not isinstance(v, list):
        logger.warning(f"Content 不是列表类型: {type(v)}")
        return []
    
    # 记录原始长度
    original_length = len(v)
    
    # 验证每个 cell
    valid_cells = []
    for idx, cell in enumerate(v):
        if cell is None:
            logger.warning(f"Cell[{idx}] 是 None，将被跳过")
            continue
        
        if not isinstance(cell, dict):
            logger.warning(
                f"Cell[{idx}] 不是字典类型: type={type(cell)}, value={cell}"
            )
            continue
        
        valid_cells.append(cell)
    
    # 如果有 cell 被过滤，记录警告
    if len(valid_cells) != original_length:
        logger.warning(
            f"⚠️ Content 验证时过滤了 {original_length - len(valid_cells)} 个无效 cell: "
            f"{original_length} -> {len(valid_cells)}"
        )
    
    return valid_cells
```

## 测试步骤

### 步骤 1: 重启服务

```bash
cd /Users/382241106qq.com/inspireed-platform-main
./restart.sh
```

### 步骤 2: 复现问题

1. 登录教师端
2. 打开教案 76（或创建新教案）
3. 新增一个模块
4. 点击保存按钮
5. 打开浏览器控制台（F12）
6. 查看保存日志：
   ```
   💾 保存教案:
   ✅ 保存成功，返回数据:
   ```
7. 记录保存前后的 `contentLength`

### 步骤 3: 检查后端日志

```bash
tail -100 /Users/382241106qq.com/inspireed-platform-main/logs/backend.log
```

查找以下关键信息：

1. **被后端过滤的 cell：**
   ```
   ❌ 教案 XX 发现 N 个无法修复的无效 cell
   被移除的 Cell[X]: type=...
   ```

2. **被 Pydantic 验证过滤的 cell：**
   ```
   ⚠️ Content 验证时过滤了 N 个无效 cell
   Cell[X] 不是字典类型: type=...
   Cell[X] 是 None，将被跳过
   ```

3. **Pydantic 验证前后数量变化：**
   ```
   ⚠️ 教案 XX 在 _lesson_to_response 验证时 content 数量变化: X -> Y
   ```

### 步骤 4: 返回首页并重新加载

1. 点击返回按钮
2. 查看控制台日志：
   ```
   💾 返回前保存未保存的更改...
   ✅ 返回前已保存更改
   ```
   或
   ```
   ✅ 无未保存的更改，直接返回
   ```
3. 重新进入教案编辑器
4. 检查模块数量是否正确

### 步骤 5: 数据库验证（可选）

```sql
-- 连接到数据库
docker exec -it inspireed-postgres psql -U inspireed -d inspireed

-- 查询教案 76 的 content 数量
SELECT 
  id, 
  title, 
  jsonb_array_length(content) as content_length
FROM lessons 
WHERE id = 76;

-- 查看完整的 content（如果需要）
SELECT content FROM lessons WHERE id = 76;
```

## 预期结果

### 如果问题在前端（已修复）

**症状：**
- 不再出现反复保存的日志（`22 -> 23 -> 22 -> 23...`）
- 返回前只保存一次（如果有未保存的更改）

**日志：**
```
✅ 返回前已保存更改 { savedContentLength: 23, expectedLength: 23, match: true }
✅ 无未保存的更改，直接返回
```

### 如果问题在后端验证层

**症状：**
- 某个 cell 被后端或 Pydantic 验证过滤

**日志：**
```
⚠️ Content 验证时过滤了 1 个无效 cell: 23 -> 22
Cell[X] 不是字典类型: type=<class 'NoneType'>, value=None
```

**解决方案：**
- 检查前端新增 cell 时的数据结构
- 确保 cell 不是 `null` 或 `undefined`
- 确保 cell 包含必需的字段（`id`、`type`）

### 如果问题在数据库层

**症状：**
- 前端和后端日志都显示 23 个
- 但数据库实际只有 22 个

**日志：**
```sql
content_length
--------------
22
```

**解决方案：**
- 检查 PostgreSQL JSONB 字段的大小限制
- 检查 SQLAlchemy 的 JSON 序列化配置
- 可能需要升级数据库或修改字段类型

## 下一步

1. 执行上述测试步骤
2. 记录所有日志输出
3. 根据日志确定问题根源
4. 如果问题仍然存在，请提供：
   - 浏览器控制台完整日志
   - 后端日志完整输出
   - 数据库查询结果
   - 被新增的 cell 的类型和内容

## 相关文档

- [保存死循环修复文档](./SAVE_LOOP_FIX.md)
- [Cell 丢失调试指南](../DEBUG_CELL_LOSS_ISSUE.md)
- [教案存储工作流](../features/lesson/LESSON_STORAGE_WORKFLOW.md)

