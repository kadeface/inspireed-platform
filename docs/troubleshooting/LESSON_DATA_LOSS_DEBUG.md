# 教案数据丢失问题诊断指南

## 问题描述

保存后的教案，退出重新登录后，修改部分不见了。

## 诊断步骤

### 1. 检查浏览器控制台日志

打开浏览器开发者工具（F12），查看 Console 标签页，查找以下日志：

#### 保存时的日志
```
💾 保存教案: {
  lessonId: 123,
  title: "教案标题",
  contentLength: 5,  // 应该显示保存的Cell数量
  contentPreview: [...],  // 前2个Cell的预览
  tags: [...]
}
```

#### 保存成功后的日志
```
✅ 保存成功，返回数据: {
  lessonId: 123,
  title: "教案标题",
  contentLength: 5,  // 应该与保存时一致
  contentPreview: [...],
  version: 2,
  updatedAt: "2024-01-15T10:30:00Z"
}
```

#### 加载时的日志
```
📥 加载教案: {
  lessonId: 123,
  title: "教案标题",
  contentLength: 5,  // 应该与保存时一致
  contentPreview: [...],
  version: 2,
  updatedAt: "2024-01-15T10:30:00Z"
}
```

**如果发现**：
- 保存时 `contentLength` 有值，但加载时 `contentLength` 为 0 → **后端保存或读取问题**
- 保存时和保存后的 `contentLength` 不一致 → **后端处理问题**
- 保存后和加载时的 `contentLength` 不一致 → **数据库持久化或读取问题**

### 2. 检查网络请求

在浏览器开发者工具的 Network 标签页中：

#### 保存请求（PUT）
1. 找到 `PUT /api/v1/lessons/{id}` 请求
2. 查看 Request Payload，确认 `content` 字段包含所有 Cell 数据
3. 查看 Response，确认返回的 `content` 字段与发送的一致

**如果发现**：
- Request 中的 `content` 为空数组 `[]` → **前端发送数据问题**
- Request 中的 `content` 有数据，但 Response 中为空 → **后端处理问题**
- Response 中有数据，但页面显示为空 → **前端加载问题**

### 3. 检查后端日志

查看后端日志文件（通常在 `logs/backend.log`），查找：

```
更新教案 {lesson_id}: 更新字段=['title', 'content', ...], content长度=5
教案 {lesson_id} 已提交并刷新: content长度=5, version=2, content类型=<class 'list'>
教案 {lesson_id} 返回数据: content长度=5, version=2
```

**如果发现**：
- 更新字段中没有 `content` → **前端未发送 content 字段**
- content长度在提交后变为 0 → **数据库保存问题**
- content长度在返回时变为 0 → **数据序列化问题**

### 4. 直接检查数据库

如果可能，直接查询数据库：

```sql
SELECT id, title, content, version, updated_at 
FROM lessons 
WHERE id = {lesson_id};
```

检查：
- `content` 字段是否为 JSON 格式，包含所有 Cell 数据
- `updated_at` 是否为最近的保存时间
- `version` 是否已更新

**如果发现**：
- `content` 为 `[]` 或 `null` → **数据库保存失败**
- `content` 有数据但前端显示为空 → **前端读取或解析问题**

## 常见问题及解决方案

### 问题1: 前端发送的数据不完整

**症状**: 保存时控制台显示 `contentLength: 0`

**原因**: 
- 自动保存时 `currentLesson.value.content` 可能为空
- 数据被意外清空

**解决方案**:
```typescript
// 在保存前检查数据
if (!currentLesson.value.content || currentLesson.value.content.length === 0) {
  console.warn('⚠️ 警告：保存时 content 为空！')
  // 可以选择不保存或提示用户
}
```

### 问题2: 后端未正确处理 content 字段

**症状**: 后端日志显示 content 长度在提交后变为 0

**原因**:
- JSON 序列化/反序列化问题
- 数据库字段类型问题

**解决方案**:
检查数据库迁移，确保 `content` 字段类型为 JSON：
```python
content = Column(JSON, nullable=False, default=list)
```

### 问题3: 数据刷新问题

**症状**: 保存成功但立即加载时数据丢失

**原因**:
- 数据库事务未正确提交
- 对象未正确刷新

**解决方案**:
已在代码中添加 `await db.refresh(lesson)` 确保数据刷新

### 问题4: 缓存问题

**症状**: 保存成功但重新加载时显示旧数据

**原因**:
- 浏览器缓存
- API 响应缓存

**解决方案**:
1. 清除浏览器缓存
2. 检查 API 服务中的缓存控制头：
```typescript
headers: {
  'Cache-Control': 'no-cache, no-store, must-revalidate',
  'Pragma': 'no-cache',
  'Expires': '0',
}
```

### 问题5: 数据序列化问题

**症状**: 数据库中有数据，但 API 返回时丢失

**原因**:
- Pydantic 序列化问题
- JSON 编码问题

**解决方案**:
检查 `_lesson_to_response` 函数，确保正确序列化：
```python
lesson_data.setdefault("content", lesson.content or [])
```

## 调试工具

### 前端调试脚本

在浏览器控制台运行：

```javascript
// 检查当前教案数据
const lessonStore = useLessonStore()
console.log('当前教案:', {
  id: lessonStore.currentLesson?.id,
  title: lessonStore.currentLesson?.title,
  contentLength: lessonStore.currentLesson?.content?.length,
  content: lessonStore.currentLesson?.content,
})

// 手动保存并检查
lessonStore.saveCurrentLesson().then(saved => {
  console.log('保存后的数据:', saved)
}).catch(err => {
  console.error('保存失败:', err)
})
```

### 后端调试脚本

在 Python 控制台运行：

```python
from app.core.database import AsyncSessionLocal
from app.models.lesson import Lesson
from sqlalchemy import select

async def check_lesson(lesson_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        lesson = result.scalar_one_or_none()
        if lesson:
            print(f"教案 ID: {lesson.id}")
            print(f"标题: {lesson.title}")
            print(f"Content 长度: {len(lesson.content) if lesson.content else 0}")
            print(f"Content 类型: {type(lesson.content)}")
            print(f"Content 预览: {lesson.content[:2] if lesson.content else []}")
            print(f"版本: {lesson.version}")
            print(f"更新时间: {lesson.updated_at}")
        else:
            print("教案不存在")
```

## 预防措施

1. **保存前验证**: 在保存前检查数据完整性
2. **保存后验证**: 保存成功后立即验证返回的数据
3. **加载后验证**: 加载后检查数据是否完整
4. **错误处理**: 添加详细的错误提示，帮助用户了解问题
5. **数据备份**: 考虑实现自动备份机制

## 相关文件

- `frontend/src/store/lesson.ts` - 前端状态管理
- `frontend/src/services/lesson.ts` - API 服务
- `backend/app/api/v1/lessons.py` - 后端 API
- `backend/app/models/lesson.py` - 数据模型
- `backend/app/schemas/lesson.py` - 数据模式

## 下一步

如果以上步骤都无法解决问题，请：

1. 收集完整的浏览器控制台日志
2. 收集后端日志
3. 提供具体的操作步骤（何时保存、何时退出、何时重新登录）
4. 提供保存前后的数据对比

