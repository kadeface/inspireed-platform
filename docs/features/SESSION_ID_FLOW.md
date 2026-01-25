# SessionId 创建与传递流程说明

## 一、SessionId 的创建

### 1.1 创建位置

**后端 API：**
- 路径：`POST /classroom-sessions/lessons/{lesson_id}/sessions`
- 文件：`backend/app/api/v1/classroom_sessions.py` (第46-119行)
- 创建者：教师（只有教师角色可以创建）

**前端调用：**
- 服务：`classroomSessionService.createSession()`
- 文件：`frontend/src/services/classroomSession.ts` (第22-75行)
- 调用位置：`TeacherControlPanel.vue` 的 `handleCreateSession()` 函数 (第1362行)

### 1.2 创建流程

```typescript
// 1. 教师点击"创建课堂"按钮
handleCreateSession() {
  // 2. 调用 API 创建会话
  const newSession = await classroomSessionService.createSession(lessonId, {
    classroom_id: classroomId
  })
  
  // 3. 会话创建成功，返回的 newSession.id 就是 sessionId
  // 4. 存储在 session.value 中
  session.value = newSession  // session.value.id 就是 sessionId
}
```

### 1.3 会话状态

创建后的会话状态：
- **初始状态**：`PENDING`（等待学生加入）
- **开始后**：`ACTIVE`（进行中）
- **暂停**：`PAUSED`
- **结束**：`ENDED`

## 二、SessionId 的传递

### 2.1 传递路径

```
TeacherControlPanel (创建 session)
  ↓ provide('classroomSessionId', session.value.id)
  ↓ provide('classroomSession', session)
  ↓
LessonEditor (渲染 CellContainer)
  ↓ inject('classroomSessionId')
  ↓ inject('classroomSession')
  ↓
CellContainer (接收 props 或 inject)
  ↓ :session-id="finalSessionId"
  ↓ :lesson-id="finalLessonId"
  ↓
ActivityCell (接收 props)
  ↓ :session-id="sessionId"
  ↓
SubmissionList (接收 props)
  ↓ :session-id="sessionId"
  ↓
API 调用: GET /activities/cells/{cell_id}/submissions?session_id={sessionId}
```

### 2.2 传递机制

#### 方式1：Props 传递（显式传递）

```vue
<!-- LessonEditor.vue -->
<CellContainer
  :cell="cell"
  :session-id="sessionId"  <!-- 如果知道 sessionId -->
  :lesson-id="lessonId"
/>
```

#### 方式2：Provide/Inject（自动注入）

```typescript
// TeacherControlPanel.vue
provide('classroomSessionId', computed(() => session.value?.id))
provide('classroomSession', session)

// CellContainer.vue
const injectedSessionId = inject('classroomSessionId')
const injectedSession = inject('classroomSession')

// 优先使用 props，否则使用注入的值
const finalSessionId = computed(() => {
  return props.sessionId ?? injectedSessionId?.value ?? injectedSession?.value?.id
})
```

### 2.3 优先级

1. **Props 传递**（最高优先级）
2. **Inject 的 computed sessionId**
3. **Inject 的 session 对象的 id**
4. **undefined**（如果没有提供）

## 三、SessionId 的使用

### 3.1 在提交列表查询中使用

```typescript
// SubmissionList.vue
async function loadSubmissions() {
  const data = await activityService.getCellSubmissions(
    props.cellId,
    statusFilter.value || undefined,
    props.sessionId,  // ⚠️ 关键：用于过滤特定会话的提交
    props.lessonId
  )
}
```

### 3.2 在后端 API 中的过滤

```python
# backend/app/api/v1/activities.py
@router.get("/cells/{cell_id}/submissions")
async def get_cell_submissions(
    cell_id: int,
    session_id: Optional[int] = Query(None),  # ⚠️ 关键参数
    ...
):
    if session_id:
        # 严格过滤：只返回该会话的提交
        query = query.where(ActivitySubmission.session_id == session_id)
```

### 3.3 为什么需要 SessionId？

1. **区分不同课堂会话**：
   - 同一课程可能被多个班级上
   - 每个班级的会话有独立的 sessionId
   - 不传递 sessionId 会导致所有会话的提交混在一起

2. **实时统计准确性**：
   - 教师需要看到当前课堂的实时提交
   - 不应该看到其他课堂或课后提交

3. **数据隔离**：
   - 确保提交数据正确关联到对应的课堂会话
   - 避免统计混乱

## 四、常见问题

### Q1: 为什么 sessionId 是 undefined？

**可能原因：**
1. 还没有创建课堂会话（需要点击"创建课堂"按钮）
2. `TeacherControlPanel` 组件未加载（不在预览模式）
3. Provide/Inject 未正确设置（已修复）

**解决方案：**
- 确保在预览模式下打开课堂控制面板
- 点击"创建课堂"按钮创建会话
- 检查控制台日志，确认 sessionId 是否正确传递

### Q2: 为什么使用数字 ID 而不是 UUID？

**原因：**
- 后端数据库使用数字主键（`Integer`）
- UUID 主要用于前端临时标识（lesson.content 中的 cell）
- 提交时，后端会将 UUID 映射到数字 ID

**流程：**
```
前端 cell.id (UUID) 
  → 后端查找/创建 Cell 记录 
  → 返回数字 ID 
  → 用于后续 API 调用
```

### Q3: 如何调试 sessionId 传递问题？

**添加调试日志：**
```typescript
// ActivityCell.vue
console.log('🔍 ActivityCell Props:', {
  sessionId: props.sessionId,
  lessonId: props.lessonId,
})

// SubmissionList.vue
console.log('🔍 加载提交列表:', {
  cellId: props.cellId,
  sessionId: props.sessionId,  // 检查这个值
  lessonId: props.lessonId,
})
```

## 五、相关文件

- **创建会话**：`backend/app/api/v1/classroom_sessions.py`
- **前端服务**：`frontend/src/services/classroomSession.ts`
- **教师控制面板**：`frontend/src/components/Classroom/TeacherControlPanel.vue`
- **Cell 容器**：`frontend/src/components/Cell/CellContainer.vue`
- **活动 Cell**：`frontend/src/components/Cell/ActivityCell.vue`
- **提交列表**：`frontend/src/components/Activity/Teacher/SubmissionList.vue`

## 六、修复历史

### 2024-01-XX 修复

1. **添加 Provide/Inject 机制**：
   - `TeacherControlPanel` 提供 `sessionId` 和 `session`
   - `CellContainer` 自动注入并使用

2. **增强 ActivityCell**：
   - 支持从路由参数获取 sessionId（备用方案）
   - 添加警告提示，当 sessionId 缺失时显示

3. **修复 CellContainer**：
   - 添加 `sessionId` 和 `lessonId` props
   - 支持自动注入机制

