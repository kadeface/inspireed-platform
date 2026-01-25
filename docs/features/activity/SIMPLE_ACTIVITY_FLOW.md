# 活动模块最简单实现方案（极简版）

## 概述

这是一个**极简化的活动模块实现方案**：
- ✅ **不保存草稿** - 学生答案只在本地内存中保存
- ✅ **不自动保存** - 只在点击"提交"按钮时一次性提交
- ✅ **直接提交** - 点击提交按钮后，创建提交记录并立即提交

从教师显示活动到学生提交、教师查看统计的完整流程。

## 核心流程

```
教师端显示活动 → 学生端看到题目 → 学生完成并提交 → 教师端实时更新统计和列表
```

## 数据流

### 1. 教师端显示活动模块

**组件位置：** `frontend/src/components/Classroom/TeacherControlPanel.vue`

**关键代码：**
```vue
<!-- 活动统计面板 -->
<SubmissionStatistics
  :cell-id="currentActivityDbCell.id"
  :lesson-id="lesson?.id || lessonId"
  :session-id="session.id"
/>

<!-- 学生提交列表 -->
<SubmissionList
  :cell-id="currentActivityDbCell.id"
  :activity="currentCell.content"
  :session-id="session.id"
  :lesson-id="lesson?.id || lessonId"
/>
```

**初始化时：**
1. `SubmissionStatistics` 组件挂载
2. 调用 `activityService.getStatistics(cellId)` 获取统计
3. 连接 WebSocket 监听实时更新
4. `SubmissionList` 组件挂载
5. 调用 `activityService.getCellSubmissions(cellId, status, sessionId, lessonId)` 获取提交列表

### 2. 学生端看到题目并完成

**组件位置：** `frontend/src/components/Activity/ActivityViewer.vue`

**关键步骤（极简版）：**
```typescript
// 学生点击"提交"按钮时，一次性完成：
// 1. 创建提交记录（状态为DRAFT）
const submission = await activityService.createSubmission({
  cellId: cellId,
  lessonId: lessonId,
  sessionId: sessionId,  // 课堂会话ID（如果有）
  responses: answers,    // 所有答案
  startedAt: startTime.toISOString(),
})

// 2. 立即提交（状态改为SUBMITTED）
await activityService.submitActivity(submission.id, {
  responses: answers,
  timeSpent: 120,       // 用时（秒）
  sessionId: sessionId,
})

// 注意：不保存草稿，不自动保存，答案只在本地内存中保存
```

### 3. 学生提交 → 后端处理

**API端点：** `POST /api/v1/activities/submissions/{submission_id}/submit`

**后端逻辑（`backend/app/api/v1/activities.py`）：**
```python
async def submit_activity(submission_id, data):
    # 1. 更新提交状态为 SUBMITTED
    submission.status = ActivitySubmissionStatus.SUBMITTED
    submission.submitted_at = datetime.utcnow()
    submission.responses = data.responses
    
    # 2. 自动评分（如果是选择题）
    auto_graded, total_score, max_score, graded_responses = _auto_grade_submission(
        data.responses,
        cell_content
    )
    
    # 3. 更新统计数据
    await _update_statistics(db, cell_id, lesson_id)
    
    # 4. WebSocket 实时通知教师
    # - 发送新提交通知（new_submission）
    # - 发送统计更新通知（submission_statistics_updated）
```

### 4. 教师端实时更新

**统计更新（`SubmissionStatistics.vue`）：**
```typescript
// 监听 WebSocket 消息
registerListener('submission_statistics_updated', (message) => {
  statistics.value = {
    totalStudents: message.data.total_students,
    submittedCount: message.data.submitted_count,
    draftCount: message.data.draft_count,
    averageScore: message.data.average_score,
    // ...
  }
})

// 如果 WebSocket 未连接，使用轮询（每5秒）
setInterval(() => {
  loadStatisticsFromAPI()
}, 5000)
```

**列表更新（`SubmissionList.vue`）：**
```typescript
// 手动刷新或监听 WebSocket 后刷新
async function loadSubmissions() {
  const data = await activityService.getCellSubmissions(
    cellId,
    statusFilter.value,
    sessionId,
    lessonId
  )
  submissions.value = data
}
```

## 关键API

### 学生端API

1. **创建提交（草稿）**
   ```
   POST /api/v1/activities/submissions
   Body: { cell_id, lesson_id, session_id?, responses, started_at }
   ```

2. **更新草稿**
   ```
   PATCH /api/v1/activities/submissions/{id}
   Body: { responses, session_id? }
   ```

3. **正式提交**
   ```
   POST /api/v1/activities/submissions/{id}/submit
   Body: { responses, time_spent, session_id? }
   ```

### 教师端API

1. **获取统计**
   ```
   GET /api/v1/activities/cells/{cell_id}/statistics
   Response: { total_students, submitted_count, draft_count, average_score, ... }
   ```

2. **获取提交列表**
   ```
   GET /api/v1/activities/cells/{cell_id}/submissions?status=&session_id=&lesson_id=
   Response: [{ id, student_name, status, score, submitted_at, ... }, ...]
   ```

## 数据模型

### ActivitySubmission（活动提交）

```python
class ActivitySubmission:
    id: int
    cell_id: int              # 活动Cell ID
    lesson_id: int            # 教案ID
    student_id: int           # 学生ID
    session_id: int?          # 课堂会话ID（可选）
    responses: dict           # 答案 {item_id: answer}
    status: enum              # draft | submitted | graded | returned
    score: float?             # 得分
    submitted_at: datetime?   # 提交时间
```

### ActivityStatistics（统计）

```python
class ActivityStatistics:
    cell_id: int
    total_students: int       # 总学生数
    submitted_count: int      # 已提交数
    draft_count: int          # 草稿数
    average_score: float?     # 平均分
```

## 最简单的实现方式

### 方案1：纯API轮询（最简单，无需WebSocket）

**教师端：**
```typescript
// 每5秒刷新一次统计和列表
setInterval(async () => {
  const stats = await activityService.getStatistics(cellId)
  const submissions = await activityService.getCellSubmissions(cellId, status, sessionId, lessonId)
  // 更新UI
}, 5000)
```

**优点：**
- 实现简单，不需要WebSocket
- 可靠性高，不依赖连接状态

**缺点：**
- 有延迟（最多5秒）
- 增加服务器负载

### 方案2：WebSocket + 轮询降级（推荐）

**当前实现方式：**
- 优先使用 WebSocket 实时推送
- 如果 WebSocket 断开，降级到轮询

**实现：**
```typescript
// 1. 尝试连接 WebSocket
connectRealtime()
registerListener('submission_statistics_updated', handleUpdate)

// 2. 如果连接失败，使用轮询
if (!isConnected.value) {
  setInterval(() => loadStatisticsFromAPI(), 5000)
}
```

**优点：**
- 实时性好（WebSocket推送）
- 有降级方案（轮询）
- 用户体验好

## 关键代码文件

### 后端
- `backend/app/api/v1/activities.py` - 活动API
- `backend/app/services/realtime.py` - WebSocket推送逻辑
- `backend/app/models/activity.py` - 数据模型

### 前端
- `frontend/src/components/Activity/ActivityViewer.vue` - 学生答题界面
- `frontend/src/components/Activity/SubmissionStatistics.vue` - 统计面板
- `frontend/src/components/Activity/Teacher/SubmissionList.vue` - 提交列表
- `frontend/src/services/activity.ts` - API服务
- `frontend/src/composables/useActivitySubmission.ts` - 提交逻辑

## 流程图

```
┌─────────────────┐
│  教师端启动活动  │
│  (TeacherControl│
│   Panel)        │
└────────┬────────┘
         │
         ├─→ 显示统计面板 (SubmissionStatistics)
         │   └─→ GET /statistics → 显示统计
         │
         └─→ 显示提交列表 (SubmissionList)
             └─→ GET /submissions → 显示列表

┌─────────────────┐
│  学生端查看活动  │
│  (ActivityViewer)│
└────────┬────────┘
         │
         ├─→ POST /submissions (创建草稿)
         │
         ├─→ PATCH /submissions/{id} (自动保存)
         │
         └─→ POST /submissions/{id}/submit (正式提交)
             │
             └─→ 后端处理:
                 ├─ 更新状态为 SUBMITTED
                 ├─ 自动评分（如适用）
                 ├─ 更新统计 (_update_statistics)
                 └─ WebSocket 推送通知
                     ├─ new_submission (新提交通知)
                     └─ submission_statistics_updated (统计更新)

┌─────────────────┐
│  教师端接收更新  │
│  (实时/轮询)     │
└─────────────────┘
         │
         ├─→ WebSocket 消息 → 更新UI
         │
         └─→ 轮询 (每5秒) → GET /statistics → 更新UI
```

## 极简版实现特点

### ✅ 已移除的功能
- ❌ **草稿保存** - 不保存草稿，答案只在内存中
- ❌ **自动保存** - 不移除自动保存逻辑
- ❌ **离线支持** - 简化版不支持离线模式
- ❌ **草稿加载** - 不加载之前的草稿（只加载已提交的内容）

### ✅ 保留的核心功能
- ✅ **点击提交** - 学生点击"提交"按钮时一次性提交
- ✅ **实时统计** - 教师端实时查看统计和提交列表
- ✅ **WebSocket推送** - 学生提交后立即通知教师端

## 总结

**极简版实现方式：**

1. **学生提交**：
   - 答案只在本地内存中保存（不保存草稿）
   - 点击"提交"按钮时：创建提交记录 → 立即提交 → 后端更新统计 → WebSocket推送

2. **教师查看**：
   - 组件挂载时调用 API 获取初始数据
   - 监听 WebSocket 更新
   - WebSocket 断开时降级到轮询

**关键点：**
- ✅ **不保存草稿** - 简化流程，只在提交时创建记录
- ✅ 提交时传递 `sessionId`（课堂模式）
- ✅ 后端自动更新统计（`_update_statistics`）
- ✅ 前端优先使用 WebSocket，失败时降级到轮询
- ✅ 统计和列表可以独立刷新

