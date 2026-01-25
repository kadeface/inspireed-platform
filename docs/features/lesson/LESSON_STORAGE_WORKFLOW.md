# 教案存储工作流

本文档详细说明教案（Lesson）在平台中的存储工作流程，包括前端编辑、自动保存、API调用和数据库存储的完整链路。

## 目录

1. [架构概览](#架构概览)
2. [数据模型](#数据模型)
3. [前端工作流](#前端工作流)
4. [后端工作流](#后端工作流)
5. [自动保存机制](#自动保存机制)
6. [版本控制](#版本控制)
7. [关键代码位置](#关键代码位置)

---

## 架构概览

```
┌─────────────────┐
│  LessonEditor   │  (前端组件)
│   (Vue组件)     │
└────────┬────────┘
         │
         │ 编辑操作 (添加/修改/删除Cell)
         ▼
┌─────────────────┐
│  useLessonStore │  (Pinia状态管理)
│   (lesson.ts)   │
└────────┬────────┘
         │
         │ 状态变化触发
         ▼
┌─────────────────┐
│  useAutoSave    │  (自动保存Composable)
│  (useAutoSave)  │  - 防抖延迟: 60秒
└────────┬────────┘
         │
         │ 调用 saveCurrentLesson()
         ▼
┌─────────────────┐
│  lessonService  │  (API服务层)
│   (lesson.ts)   │
└────────┬────────┘
         │
         │ HTTP PUT /lessons/{id}
         ▼
┌─────────────────┐
│  update_lesson  │  (后端API)
│  (lessons.py)   │
└────────┬────────┘
         │
         │ SQLAlchemy ORM
         ▼
┌─────────────────┐
│   PostgreSQL    │  (数据库)
│   lessons表     │
└─────────────────┘
```

---

## 数据模型

### 数据库表结构

**表名**: `lessons`

**核心字段**:

```python
class Lesson(Base):
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    
    # 状态管理
    status = Column(SQLEnum(LessonStatus), default=LessonStatus.DRAFT)
    
    # 核心：教案内容（JSON格式存储所有Cell配置）
    content = Column(JSON, nullable=False, default=list)
    
    # 版本控制
    version = Column(Integer, default=1, nullable=False)
    parent_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
```

**关键点**:
- `content` 字段以 JSON 格式存储所有 Cell 的完整配置
- 每个 Cell 包含：`id`, `type`, `order`, `content`, `config` 等
- 版本号用于追踪已发布教案的内容更新

---

## 前端工作流

### 1. 组件层 (LessonEditor.vue)

**位置**: `frontend/src/pages/Teacher/LessonEditor.vue`

**主要功能**:
- 提供教案编辑界面
- 监听用户操作（添加/修改/删除 Cell）
- 显示保存状态

**关键代码**:

```typescript
// 自动保存配置
const { saveStatus, lastSavedAt, manualSave } = useAutoSave({
  data: computed(() => lessonStore.currentLesson),
  saveFn: async () => {
    if (currentLesson.value) {
      // 更新标题
      currentLesson.value.title = lessonTitle.value
      await lessonStore.saveCurrentLesson()
    }
  },
  delay: 60000, // 60秒自动保存
  enabled: computed(
    () => !isPreviewMode.value && !!currentLesson.value && !isFlowInteractionActive.value
  ),
})
```

### 2. 状态管理层 (lesson.ts Store)

**位置**: `frontend/src/store/lesson.ts`

**核心方法**:

#### `saveCurrentLesson()`

```typescript
async function saveCurrentLesson() {
  if (!currentLesson.value) {
    throw new Error('没有要保存的教案')
  }

  isSaving.value = true
  error.value = null

  try {
    let savedLesson: Lesson

    if (currentLesson.value.id) {
      // 更新现有教案
      savedLesson = await lessonService.updateLesson(currentLesson.value.id, {
        title: currentLesson.value.title,
        description: currentLesson.value.description,
        content: currentLesson.value.content,  // 所有Cell配置
        tags: currentLesson.value.tags,
      })
    } else {
      // 创建新教案
      savedLesson = await lessonService.createLesson({...})
    }

    // 更新本地状态
    currentLesson.value = savedLesson
    
    // 更新列表中的教案
    const index = lessons.value.findIndex((l) => l.id === savedLesson.id)
    if (index !== -1) {
      lessons.value[index] = savedLesson
    }

    return savedLesson
  } catch (err: any) {
    error.value = err.message || '保存教案失败'
    throw err
  } finally {
    isSaving.value = false
  }
}
```

**本地操作方法** (不触发保存，只更新内存状态):

- `addCell(cell)` - 添加Cell到content数组
- `updateCell(cellId, updates)` - 更新指定Cell
- `deleteCell(cellId)` - 删除指定Cell
- `reorderCells(fromIndex, toIndex)` - 重新排序Cell

### 3. API服务层 (lesson.ts Service)

**位置**: `frontend/src/services/lesson.ts`

**核心方法**:

```typescript
async updateLesson(id: number, data: LessonUpdate): Promise<Lesson> {
  try {
    const response = await api.put<Lesson>(`${this.basePath}/${id}`, data)
    return response
  } catch (error: any) {
    console.error(`Failed to update lesson ${id}:`, error)
    throw new Error(error.response?.data?.detail || '更新教案失败')
  }
}
```

---

## 后端工作流

### API端点

**位置**: `backend/app/api/v1/lessons.py`

**路由**: `PUT /api/v1/lessons/{lesson_id}`

### 更新流程

```python
@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_in: LessonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新教案"""
    
    # 1. 验证教案存在
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 2. 验证权限（只有创建者可以修改）
    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该教案")
    
    # 3. 检查内容是否更新
    content_updated = False
    if "content" in update_data:
        old_content = lesson.content
        new_content = update_data["content"]
        if old_content != new_content:
            content_updated = True
    
    # 4. 更新字段
    for field, value in update_data.items():
        setattr(lesson, field, value)
    
    # 5. 版本控制：如果更新了已发布教案的内容，自动增加版本号
    if content_updated and lesson.status == LessonStatus.PUBLISHED:
        current_version = lesson.version or 1
        lesson.version = current_version + 1
        lesson.published_at = datetime.utcnow()  # 更新时间戳
    
    # 6. 提交到数据库
    await db.commit()
    
    # 7. 重新加载关联数据并返回
    lesson = await _get_lesson_with_relations(db, lesson_id)
    return _lesson_to_response(lesson)
```

### 关键逻辑

1. **权限验证**: 只有教案创建者可以修改
2. **内容比较**: 通过比较新旧 content 判断是否真正更新
3. **版本控制**: 已发布教案内容更新时自动增加版本号
4. **时间戳**: `updated_at` 自动更新，`published_at` 在内容更新时也更新

---

## 自动保存机制

### useAutoSave Composable

**位置**: `frontend/src/composables/useAutoSave.ts`

**工作原理**:

```typescript
export function useAutoSave(options: UseAutoSaveOptions): UseAutoSaveReturn {
  const { data, saveFn, delay = 3000, enabled = ref(true) } = options

  const saveStatus = ref<SaveStatus>('idle')
  const lastSavedAt = ref<Date | null>(null)
  const errorMessage = ref<string | null>(null)

  // 执行保存
  async function performSave() {
    if (!enabled.value) return

    saveStatus.value = 'saving'
    errorMessage.value = null

    try {
      await saveFn()
      saveStatus.value = 'saved'
      lastSavedAt.value = new Date()

      // 2秒后重置为 idle
      setTimeout(() => {
        if (saveStatus.value === 'saved') {
          saveStatus.value = 'idle'
        }
      }, 2000)
    } catch (error: any) {
      saveStatus.value = 'error'
      errorMessage.value = error.message || '保存失败'
    }
  }

  // 防抖保存（使用 VueUse 的 useDebounceFn）
  const debouncedSave = useDebounceFn(performSave, delay)

  // 监听数据变化（深度监听）
  watch(
    data,
    () => {
      if (enabled.value && data.value) {
        debouncedSave()  // 触发防抖保存
      }
    },
    { deep: true }
  )

  return {
    saveStatus,
    lastSavedAt,
    errorMessage,
    manualSave,  // 手动保存方法
  }
}
```

**特性**:

1. **防抖机制**: 使用 `useDebounceFn`，默认延迟 60 秒（在 LessonEditor 中配置）
2. **深度监听**: 监听 `currentLesson` 的所有嵌套属性变化
3. **状态管理**: 提供 `idle` / `saving` / `saved` / `error` 四种状态
4. **条件启用**: 可通过 `enabled` 控制是否自动保存（例如预览模式下禁用）

**在 LessonEditor 中的配置**:

```typescript
delay: 60000,  // 60秒延迟
enabled: computed(
  () => !isPreviewMode.value && !!currentLesson.value && !isFlowInteractionActive.value
)
```

---

## 版本控制

### 版本号机制

**目的**: 追踪已发布教案的内容更新，让学生端能够检测到新版本

**触发条件**:
- 教案状态为 `published`（已发布）
- `content` 字段发生变化

**实现逻辑**:

```python
# 检查是否更新了内容
content_updated = False
if "content" in update_data:
    old_content = lesson.content
    new_content = update_data["content"]
    if old_content != new_content:
        content_updated = True

# 如果更新了已发布教案的内容，自动更新版本号
if content_updated and lesson.status == LessonStatus.PUBLISHED:
    current_version = lesson.version or 1
    lesson.version = current_version + 1
    lesson.published_at = datetime.utcnow()  # 更新时间戳
```

**版本号用途**:
- 学生端可以通过比较版本号判断教案是否有更新
- 教师端可以看到教案的版本历史

---

## 关键代码位置

### 前端

| 文件 | 路径 | 说明 |
|------|------|------|
| LessonEditor | `frontend/src/pages/Teacher/LessonEditor.vue` | 教案编辑主组件 |
| lesson Store | `frontend/src/store/lesson.ts` | Pinia状态管理 |
| lesson Service | `frontend/src/services/lesson.ts` | API服务封装 |
| useAutoSave | `frontend/src/composables/useAutoSave.ts` | 自动保存Composable |

### 后端

| 文件 | 路径 | 说明 |
|------|------|------|
| Lesson Model | `backend/app/models/lesson.py` | 数据模型定义 |
| lessons API | `backend/app/api/v1/lessons.py` | API端点实现 |

---

## 数据流转示例

### 场景：教师编辑教案标题和添加一个文本Cell

1. **用户操作**:
   - 修改标题: "我的教案" → "我的教案（更新版）"
   - 添加一个文本Cell

2. **前端状态更新**:
   ```typescript
   // LessonEditor.vue
   lessonTitle.value = "我的教案（更新版）"
   lessonStore.addCell(newTextCell)
   ```

3. **自动保存触发**:
   ```typescript
   // useAutoSave 监听到 currentLesson 变化
   // 60秒后触发 debouncedSave()
   ```

4. **保存执行**:
   ```typescript
   // lessonStore.saveCurrentLesson()
   await lessonService.updateLesson(lessonId, {
     title: "我的教案（更新版）",
     content: [...existingCells, newTextCell]  // 包含新Cell
   })
   ```

5. **API请求**:
   ```
   PUT /api/v1/lessons/123
   {
     "title": "我的教案（更新版）",
     "content": [...]
   }
   ```

6. **后端处理**:
   ```python
   # 更新数据库
   lesson.title = "我的教案（更新版）"
   lesson.content = [...]
   lesson.updated_at = datetime.utcnow()
   
   # 如果已发布，增加版本号
   if lesson.status == PUBLISHED and content_updated:
       lesson.version += 1
       lesson.published_at = datetime.utcnow()
   
   await db.commit()
   ```

7. **响应返回**:
   ```json
   {
     "id": 123,
     "title": "我的教案（更新版）",
     "content": [...],
     "version": 2,
     "updated_at": "2024-01-15T10:30:00Z"
   }
   ```

8. **前端状态同步**:
   ```typescript
   // 更新本地状态
   currentLesson.value = savedLesson
   saveStatus.value = 'saved'
   ```

---

## 注意事项

1. **内容格式**: `content` 字段存储的是完整的 Cell 配置数组，包括所有嵌套属性
2. **自动保存延迟**: 默认 60 秒，避免频繁请求
3. **版本控制**: 只有已发布教案的内容更新才会增加版本号
4. **权限控制**: 只有教案创建者可以修改
5. **状态同步**: 保存成功后会自动更新本地状态和列表中的教案

---

## 相关文档

- [教案功能文档](./README.md)
- [Cell系统文档](../cell/README.md)
- [自动保存实现](../lesson/useAutoSave.md)

