# 活动实时互动方案设计

## 概述

本文档设计 ActivityCell 模块下学生上传结果和教师端接收结果的实时互动方案。目标是实现：
- 学生提交后，教师实时收到通知
- 教师评分后，学生实时收到通知
- 实时显示提交进度和统计信息
- 支持课堂模式下的实时互动

## 当前状态分析

### 已有功能
1. **学生端（ActivityViewer.vue）**
   - ✅ 支持多种题型答题
   - ✅ 自动保存草稿（每3秒）
   - ✅ 离线支持（IndexedDB）
   - ✅ 提交后显示正确答案和得分
   - ❌ 缺少实时通知（教师评分后）

2. **教师端（SubmissionList.vue）**
   - ✅ 显示学生提交列表
   - ✅ 支持状态过滤
   - ✅ 支持评分和批量操作
   - ❌ 缺少实时通知（学生提交后）
   - ❌ 需要手动刷新才能看到新提交

3. **WebSocket 基础设施**
   - ✅ 已有 WebSocket 服务（websocket.ts）
   - ✅ 已有后端连接管理器（websocket_manager.py）
   - ✅ 课堂会话已集成 WebSocket
   - ❌ 活动提交尚未集成实时通知

## 设计方案

### 1. WebSocket 消息类型扩展

#### 1.1 学生端发送的消息

```typescript
// 学生提交活动
{
  type: 'activity_submitted',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    submission_id: 123,
    cell_id: 456,
    lesson_id: 789,
    student_id: 1,
    status: 'submitted',
    score: null,  // 如果自动评分，可能已有分数
    submitted_at: '2024-01-01T12:00:00Z'
  }
}

// 学生保存草稿（可选，用于实时进度显示）
{
  type: 'activity_draft_saved',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    cell_id: 456,
    lesson_id: 789,
    student_id: 1,
    progress: 60,  // 完成进度百分比
    answered_count: 6,
    total_count: 10
  }
}
```

#### 1.2 教师端接收的消息

```typescript
// 新提交通知
{
  type: 'new_submission',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    submission_id: 123,
    cell_id: 456,
    lesson_id: 789,
    student_id: 1,
    student_name: '张三',
    student_email: 'zhangsan@example.com',
    status: 'submitted',
    score: null,
    submitted_at: '2024-01-01T12:00:00Z',
    time_spent: 300  // 秒
  }
}

// 提交统计更新
{
  type: 'submission_statistics_updated',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    cell_id: 456,
    lesson_id: 789,
    total_students: 30,
    submitted_count: 15,
    draft_count: 10,
    not_started_count: 5,
    average_score: 85.5,
    average_time_spent: 450
  }
}

// 学生答题进度更新（实时显示谁在答题）
{
  type: 'student_progress_updated',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    cell_id: 456,
    lesson_id: 789,
    student_id: 1,
    student_name: '张三',
    progress: 60,
    answered_count: 6,
    total_count: 10,
    last_active_at: '2024-01-01T12:00:00Z'
  }
}
```

#### 1.3 学生端接收的消息

```typescript
// 教师评分通知
{
  type: 'submission_graded',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    submission_id: 123,
    cell_id: 456,
    lesson_id: 789,
    score: 90,
    max_score: 100,
    teacher_feedback: '回答得很好！',
    graded_at: '2024-01-01T12:05:00Z',
    graded_by: 2,  // 教师ID
    graded_by_name: '李老师'
  }
}

// 提交被退回
{
  type: 'submission_returned',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    submission_id: 123,
    cell_id: 456,
    lesson_id: 789,
    teacher_feedback: '请重新检查第3题',
    returned_at: '2024-01-01T12:05:00Z'
  }
}
```

#### 1.4 消息通用字段与幂等策略

所有 WebSocket 事件统一采用 Envelope 结构：

```json
{
  "event_id": "uuid",          // 由后端生成，保证全局唯一，便于幂等
  "version": 1,                // 消息结构版本，方便后续 schema 兼容
  "type": "new_submission",    // 业务事件类型
  "timestamp": "ISO8601",
  "channel": {
    "scope": "session|lesson",
    "id": 123,                 // session_id 或 lesson_id
    "lesson_id": 456           // 便于前端二次过滤
  },
  "delivery_mode": "cast|unicast",
  "data": { ... },
  "ack_token": "optional"      // 需要客户端确认时返回
}
```

- **event_id**：前端用 `Set` 或 `Map` 记录最近 100 条，以避免重复插入。
- **channel.scope**：课堂实时场景使用 `session`，课后异步使用 `lesson`，便于统一监听。
- **delivery_mode**：`unicast` 用于个人通知（评分/退回），`cast` 用于广播（统计/进度）。
- **ack_token**：仅在需要双向确认（例如“大屏点名”等）时下发；普通消息无需 ack，失败自动重发。

该 Envelope 由 WebSocket 服务统一注入，业务代码只负责填充 `type` 和 `data`，减少重复实现。

### 2. 后端实现方案

#### 2.1 在活动提交 API 中发送 WebSocket 通知

**位置：** `backend/app/api/v1/activities.py`

```python
# 在 submit_activity 函数中
@router.post("/submissions/{submission_id}/submit", ...)
async def submit_activity(...):
    # ... 现有提交逻辑 ...

    from app.services.realtime import build_event, resolve_teacher_targets
    from app.services.websocket_manager import manager

    teacher_targets = await resolve_teacher_targets(db, submission)
    if teacher_targets:
        event = build_event(
            type="new_submission",
            channel=teacher_targets.channel,
            delivery_mode="cast" if teacher_targets.is_broadcast else "unicast",
            data={
                "submission_id": submission.id,
                "cell_id": submission.cell_id,
                "lesson_id": submission.lesson_id,
                "student_id": submission.student_id,
                "student_name": submission.student.username,
                "student_email": submission.student.email,
                "status": submission.status.value,
                "score": submission.score,
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "time_spent": submission.time_spent,
            },
        )
        await manager.send_to_teacher(event, teacher_targets)

    stats = await _get_submission_statistics(
        db,
        submission.cell_id,
        submission.lesson_id,
        session_id=submission.session_id,
        lesson_id=submission.lesson_id,
    )

    stats_channel = teacher_targets.channel if teacher_targets else Channel(scope="lesson", id=submission.lesson_id)

    await manager.broadcast(
        event=build_event(
            type="submission_statistics_updated",
            channel=stats_channel,
            delivery_mode="cast",
            data=stats,
        ),
        channel=stats_channel,
    )
```

```python
async def resolve_teacher_targets(db: AsyncSession, submission: ActivitySubmission) -> RealtimeTarget:
    """
    课堂模式：channel.scope = session，绑定 session_id
    课后模式：channel.scope = lesson，同时附带 classroom_ids，支持多名教师协作。
    """
    if submission.session_id:
        session = await db.get(ClassSession, submission.session_id)
        return RealtimeTarget.session(session_id=submission.session_id, teacher_ids=[session.teacher_id])

    # 课后模式：根据 lesson -> classroom -> teacher 多对多建立映射
    lesson = await db.get(Lesson, submission.lesson_id)
    teacher_ids = await fetch_teachers_by_lesson(db, lesson)
    return RealtimeTarget.lesson(lesson_id=lesson.id, teacher_ids=teacher_ids)
```

- `resolve_teacher_targets()` 返回 `RealtimeTarget`，内部封装 `channel` 和接收者列表，可扩展到助教、多教师协同。
- `resolve_student_target()`（未展开）遵循相同模式：课堂模式走 session channel，课后模式走 lesson channel + 学生 ID。
- `build_event()` 统一注入 `event_id`、`timestamp`、`channel` 等 envelope 字段，保证消息格式一致。

#### 2.2 在评分 API 中发送 WebSocket 通知

**位置：** `backend/app/api/v1/activities.py`

```python
# 在 grade_submission 函数中
@router.post("/submissions/{submission_id}/grade", ...)
async def grade_submission(...):
    # ... 现有评分逻辑 ...
    
    # 发送 WebSocket 通知给学生（课堂 / 课后统一）
    from app.services.realtime import build_event, resolve_student_target
    from app.services.websocket_manager import manager

    student_target = resolve_student_target(submission)
    await manager.send_to_student(
        build_event(
            type="submission_graded",
            channel=student_target.channel,
            delivery_mode="unicast",
            data={
                "submission_id": submission.id,
                "cell_id": submission.cell_id,
                "lesson_id": submission.lesson_id,
                "score": submission.score,
                "max_score": submission.max_score,
                "teacher_feedback": submission.teacher_feedback,
                "graded_at": submission.graded_at.isoformat() if submission.graded_at else None,
                "graded_by": submission.graded_by,
            },
        ),
        student_target,
    )
```

#### 2.3 扩展 WebSocket 连接管理器支持教师

**位置：** `backend/app/services/websocket_manager.py`

当前管理器只支持学生连接。需要扩展：

```python
from typing import Literal, Optional
from uuid import uuid4
from datetime import datetime

@dataclass(frozen=True)
class Channel:
    scope: Literal["session", "lesson"]
    id: int

@dataclass
class RealtimeTarget:
    channel: Channel
    recipient_ids: list[int]

    @property
    def is_broadcast(self) -> bool:
        return len(self.recipient_ids) == 0

    @classmethod
    def session(cls, session_id: int, teacher_ids: Optional[list[int]] = None):
        return cls(channel=Channel(scope="session", id=session_id), recipient_ids=teacher_ids or [])

    @classmethod
    def lesson(cls, lesson_id: int, teacher_ids: Optional[list[int]] = None):
        return cls(channel=Channel(scope="lesson", id=lesson_id), recipient_ids=teacher_ids or [])


class ConnectionManager:
    def __init__(self):
        # {Channel -> {user_id -> WebSocket}}
        self.student_connections: dict[Channel, dict[int, WebSocket]] = {}
        self.teacher_connections: dict[Channel, dict[int, WebSocket]] = {}

    async def connect(self, *, websocket: WebSocket, channel: Channel, user_id: int, role: UserRole):
        store = self.teacher_connections if role == UserRole.TEACHER else self.student_connections
        store.setdefault(channel, {})

        old_ws = store[channel].get(user_id)
        if old_ws and old_ws.client_state == WebSocketState.CONNECTED:
            await old_ws.close(code=status.WS_1011_INTERNAL_ERROR)

        store[channel][user_id] = websocket

    async def disconnect(self, *, channel: Channel, user_id: int, role: UserRole):
        store = self.teacher_connections if role == UserRole.TEACHER else self.student_connections
        store.get(channel, {}).pop(user_id, None)

    async def send_to_teacher(self, event: dict, target: RealtimeTarget):
        await self._send(event, target, store=self.teacher_connections)

    async def send_to_student(self, event: dict, target: RealtimeTarget):
        await self._send(event, target, store=self.student_connections)

    async def broadcast(self, event: dict, *, channel: Channel):
        await self._send(event, RealtimeTarget(channel=channel, recipient_ids=[]), store=self.teacher_connections)
        await self._send(event, RealtimeTarget(channel=channel, recipient_ids=[]), store=self.student_connections)

    async def _send(self, event: dict, target: RealtimeTarget, store: dict[Channel, dict[int, WebSocket]]):
        if target.channel not in store:
            return
        recipients = store[target.channel]
        delivery_list = target.recipient_ids or list(recipients.keys())
        for recipient_id in delivery_list:
            websocket = recipients.get(recipient_id)
            if not websocket:
                continue
            try:
                await websocket.send_text(json.dumps(event))
            except Exception:
                await websocket.close()
                recipients.pop(recipient_id, None)
```

```python
def build_event(*, type: str, channel: Channel, delivery_mode: Literal["cast", "unicast"], data: dict, ack_token: str | None = None) -> dict:
    return {
        "event_id": str(uuid4()),
        "version": 1,
        "type": type,
        "timestamp": datetime.utcnow().isoformat(),
        "channel": {"scope": channel.scope, "id": channel.id},
        "delivery_mode": delivery_mode,
        "data": data,
        "ack_token": ack_token,
    }
```

### 3. 前端实现方案

#### 3.1 学生端：监听评分通知

**位置：** `frontend/src/components/Activity/ActivityViewer.vue`

```typescript
const channelScope = computed(() =>
  isInClassroomMode.value ? { scope: 'session', id: session.value!.id } : { scope: 'lesson', id: lessonId.value }
)

const { registerListener, unregisterAll, processedMessages } = useRealtimeChannel(channelScope)
const toast = useToast()

function handleGraded(message: WebSocketMessage) {
  if (processedMessages.has(message.event_id)) return
  processedMessages.add(message.event_id)

  if (message.data.submission_id !== submissionId.value) return

  submissionData.value = {
    ...submissionData.value,
    score: message.data.score,
    maxScore: message.data.max_score,
    teacherFeedback: message.data.teacher_feedback,
    gradedAt: message.data.graded_at,
  }

  toast.show({
    type: 'success',
    title: '老师已评分',
    message: `${message.data.score} / ${message.data.max_score} 分`,
  })

  if (isSubmitted.value) {
    loadSubmissionDetails()
  }
}

function handleReturned(message: WebSocketMessage) {
  if (message.data.submission_id !== submissionId.value) return
  isSubmitted.value = false
  toast.show({
    type: 'warning',
    title: '提交被退回',
    message: message.data.teacher_feedback,
  })
}

onMounted(() => {
  registerListener('submission_graded', handleGraded)
  registerListener('submission_returned', handleReturned)
})

onUnmounted(unregisterAll)
```

#### 3.2 教师端：实时更新提交列表

**位置：** `frontend/src/components/Activity/Teacher/SubmissionList.vue`

```typescript
import { useRealtimeChannel } from '@/composables/useRealtimeChannel'
import { useToast } from '@/components/NotificationToast'

const sessionChannel = computed(() =>
  props.sessionId ? { scope: 'session', id: props.sessionId } : { scope: 'lesson', id: props.lessonId }
)

const { registerListener, unregisterAll } = useRealtimeChannel(sessionChannel)
const toast = useToast()

function handleNewSubmission(message: WebSocketMessage) {
  if (message.data.cell_id !== props.cellId) return
  const newSubmission = normalizeSubmission(message.data)
  insertSubmission(newSubmission)
  toast.show({ type: 'info', title: '新提交', message: newSubmission.studentName })
}

function handleStatistics(message: WebSocketMessage) {
  if (message.data.cell_id !== props.cellId) return
  statistics.value = normalizeStatistics(message.data)
}

onMounted(() => {
  registerListener('new_submission', handleNewSubmission)
  registerListener('submission_statistics_updated', handleStatistics)
})

onUnmounted(unregisterAll)
```

#### 3.3 教师端：实时统计面板

可以创建一个新的组件 `SubmissionStatistics.vue`：

```vue
<template>
  <div class="statistics-panel">
    <h3 class="panel-title">📊 实时统计</h3>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总学生数</div>
        <div class="stat-value">{{ statistics.totalStudents }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">已提交</div>
        <div class="stat-value text-green-600">{{ statistics.submittedCount }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">草稿中</div>
        <div class="stat-value text-yellow-600">{{ statistics.draftCount }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">未开始</div>
        <div class="stat-value text-gray-600">{{ statistics.notStartedCount }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">平均分</div>
        <div class="stat-value text-blue-600">{{ statistics.averageScore?.toFixed(1) || '-' }}</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">平均用时</div>
        <div class="stat-value text-purple-600">{{ formatTime(statistics.averageTimeSpent) }}</div>
      </div>
    </div>
    
    <!-- 进度条 -->
    <div class="progress-section">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${(statistics.submittedCount / statistics.totalStudents) * 100}%` }"
        ></div>
      </div>
      <p class="progress-text">
        提交进度：{{ statistics.submittedCount }} / {{ statistics.totalStudents }} 
        ({{ Math.round((statistics.submittedCount / statistics.totalStudents) * 100) }}%)
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRealtimeChannel } from '@/composables/useRealtimeChannel'
import type { WebSocketMessage } from '@/services/websocket'

interface Props {
  cellId: number
  lessonId: number
  sessionId?: number
}

const props = defineProps<Props>()
const statistics = ref({
  totalStudents: 0,
  submittedCount: 0,
  draftCount: 0,
  notStartedCount: 0,
  averageScore: null as number | null,
  averageTimeSpent: 0,
})

function formatTime(seconds: number): string {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟`
}

const channel = computed(() =>
  props.sessionId ? { scope: 'session', id: props.sessionId } : { scope: 'lesson', id: props.lessonId }
)

const { registerListener, unregisterAll } = useRealtimeChannel(channel)

function handleStatisticsUpdate(message: WebSocketMessage) {
  if (message.data.cell_id !== props.cellId) return
  statistics.value = {
    totalStudents: message.data.total_students,
    submittedCount: message.data.submitted_count,
    draftCount: message.data.draft_count,
    notStartedCount: message.data.not_started_count,
    averageScore: message.data.average_score,
    averageTimeSpent: message.data.average_time_spent,
  }
}

onMounted(() => registerListener('submission_statistics_updated', handleStatisticsUpdate))
onUnmounted(unregisterAll)
</script>

<style scoped>
.statistics-panel {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.panel-title {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.stats-grid {
  @apply grid grid-cols-3 gap-4 mb-6;
}

.stat-card {
  @apply bg-gray-50 rounded-lg p-4 text-center;
}

.stat-label {
  @apply text-sm text-gray-600 mb-2;
}

.stat-value {
  @apply text-2xl font-bold;
}

.progress-section {
  @apply mt-4;
}

.progress-bar {
  @apply w-full h-3 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-600 transition-all duration-300;
}

.progress-text {
  @apply text-sm text-gray-600 mt-2 text-center;
}
</style>
```

#### 3.4 学生端：实时进度提示

在 `ActivityViewer.vue` 中添加实时进度提示组件：

```vue
<!-- 在活动标题下方添加 -->
<div v-if="isInClassroomMode && realtimeStats" class="realtime-stats-banner">
  <div class="stats-info">
    <span>📊 实时进度：</span>
    <span class="text-blue-600 font-semibold">{{ realtimeStats.submittedCount }}</span>
    <span>/ {{ realtimeStats.totalStudents }} 人已提交</span>
  </div>
</div>
```

### 4. 实现步骤

#### 阶段一：后端 WebSocket 扩展（优先级：高）

1. **扩展 ConnectionManager + Realtime Service**
   - [ ] 引入 `Channel`、`RealtimeTarget`、`build_event()`、`resolve_*_target()` 等统一模型
   - [ ] 将 `connect`/`disconnect`/`send_to_teacher`/`send_to_student`/`broadcast` 收敛到单入口
   - [ ] 支持 `session` + `lesson` 双通道，覆盖课堂与课后
   - [ ] 添加 lesson 级教师端点（课后模式）与 session 端点鉴权改为 Header

2. **在提交 API 中集成通知**
   - [ ] 使用 `resolve_teacher_targets()` 发送 `new_submission`
   - [ ] `_get_submission_statistics()` 根据 session/lesson 精确统计
   - [ ] `broadcast()` 统一向教师与统计组件广播

3. **在评分 / 退回 API 中集成通知**
   - [ ] `grade_submission()` + `bulk_grade_submissions()` 使用 `resolve_student_target()`
   - [ ] `bulk_return_submissions()` 发送 `submission_returned`
   - [ ] 引入 `event_id` / `ack_token` 以支持重试与审计

#### 阶段二：前端学生端集成（优先级：高）

1. **ActivityViewer.vue 增强**
   - [ ] 接入 `useRealtimeChannel`，统一 session/lesson 监听
   - [ ] 使用 `NotificationToast` 展示评分/退回提醒
   - [ ] 同步 `submissionData` 并触发 `loadSubmissionDetails()`
   - [ ] 添加实时统计横幅（可选）

2. **通知提示优化**
   - [ ] 引入 `NotificationToast` + 声音提示（可选）
   - [ ] 支持浏览器原生通知（可选）

#### 阶段三：前端教师端集成（优先级：高）

1. **SubmissionList.vue 增强**
   - [ ] 基于 `useRealtimeChannel` 注册 `new_submission` / `submission_statistics_updated`
   - [ ] `normalizeSubmission` + 批量插入，防重复
   - [ ] 与 `NotificationToast` 联动提示
   - [ ] 新提交视觉高亮（闪烁/动画）

2. **创建 SubmissionStatistics.vue**
   - [ ] 集成 `registerListener` + 防抖
   - [ ] 在 ActivityCell.vue 教师视图复用
   - [ ] 与课堂大屏布局一致

#### 阶段四：优化和测试（优先级：中）

1. **性能优化**
   - [ ] 防抖处理频繁的统计更新
   - [ ] 优化 WebSocket 消息大小
   - [ ] 添加消息队列处理

2. **错误处理**
   - [ ] WebSocket 断开重连
   - [ ] 消息发送失败重试
   - [ ] 降级到轮询模式

3. **测试**
   - [ ] 单元测试：WebSocket 消息处理
   - [ ] 集成测试：端到端实时通知
   - [ ] 压力测试：多学生同时提交

### 5. 技术细节

#### 5.1 WebSocket 连接管理

**教师连接端点：**
```python
@router.websocket("/sessions/{session_id}/ws/teacher")
async def websocket_teacher_endpoint(
    websocket: WebSocket,
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """教师 WebSocket 连接端点"""
    token = await extract_ws_token(websocket)  # 从 Cookie / Authorization Header 解析
    user = await verify_token(token, db)
    if user.role != UserRole.TEACHER:
        await websocket.close(code=CloseCode.FORBIDDEN, reason="Only teachers can connect")
        return
    
    session = await db.get(ClassSession, session_id)
    if not session or session.teacher_id != user.id:
        await websocket.close(code=CloseCode.FORBIDDEN, reason="Unauthorized")
        return
    
    channel = Channel(scope="session", id=session_id)
    await manager.connect(
        websocket=websocket,
        channel=channel,
        user_id=user.id,
        role=UserRole.TEACHER,
    )
    
    try:
        while True:
            payload = await websocket.receive_json()
            if payload.get("type") == "request_statistics":
                stats = await _get_submission_statistics(
                    db,
                    payload["cell_id"],
                    payload["lesson_id"],
                    session_id=session_id,
                )
                await manager.send_to_teacher(
                    build_event(
                        type="submission_statistics_updated",
                        channel=channel,
                        delivery_mode="unicast",
                        data=stats,
                    ),
                    RealtimeTarget(channel=channel, recipient_ids=[user.id]),
                )
    except WebSocketDisconnect:
        await manager.disconnect(channel=channel, user_id=user.id, role=UserRole.TEACHER)
```

```python
@router.websocket("/lessons/{lesson_id}/ws/teacher")
async def websocket_teacher_lesson_endpoint(
    websocket: WebSocket,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
):
    """课后（lesson 范围）教师端点"""
    token = await extract_ws_token(websocket)
    user = await verify_token(token, db)
    await ensure_teacher_has_lesson_access(db, user, lesson_id)

    channel = Channel(scope="lesson", id=lesson_id)
    await manager.connect(websocket=websocket, channel=channel, user_id=user.id, role=UserRole.TEACHER)

    try:
        while True:
            await websocket.receive_text()  # keepalive, 支持心跳/subscribe
    except WebSocketDisconnect:
        await manager.disconnect(channel=channel, user_id=user.id, role=UserRole.TEACHER)
```

#### 5.2 统计计算函数

```python
async def _get_submission_statistics(
    db: AsyncSession,
    cell_id: int,
    lesson_id: int,
    session_id: Optional[int] = None,
) -> dict:
    """获取提交统计信息，课堂 / 课后共用"""
    from sqlalchemy import func, select
    from app.models.activity import ActivitySubmission, ActivitySubmissionStatus
    from app.models.classroom_session import StudentParticipation
    from app.models.classroom import Classroom, ClassroomEnrollment

    if session_id:
        total_students = await db.scalar(
            select(func.count(StudentParticipation.id)).where(
                StudentParticipation.session_id == session_id
            )
        )
    else:
        total_students = await db.scalar(
            select(func.count(ClassroomEnrollment.id)).where(
                ClassroomEnrollment.classroom_id.in_(
                    select(Classroom.id).where(Classroom.lesson_id == lesson_id)
                )
            )
        )

    status_counts = await db.execute(
        select(
            ActivitySubmission.status,
            func.count(ActivitySubmission.id).label("count"),
        )
        .where(ActivitySubmission.cell_id == cell_id)
        .where(ActivitySubmission.lesson_id == lesson_id)
        .group_by(ActivitySubmission.status)
    )

    status_dict = {row.status.value: row.count for row in status_counts}

    avg_result = await db.execute(
        select(
            func.avg(ActivitySubmission.score).label("avg_score"),
            func.avg(ActivitySubmission.time_spent).label("avg_time"),
        )
        .where(ActivitySubmission.cell_id == cell_id)
        .where(ActivitySubmission.lesson_id == lesson_id)
        .where(
            ActivitySubmission.status.in_(
                [ActivitySubmissionStatus.SUBMITTED, ActivitySubmissionStatus.GRADED]
            )
        )
    )

    avg_row = avg_result.first()
    processed = status_dict.get("submitted", 0) + status_dict.get("graded", 0) + status_dict.get("returned", 0)

    return {
        "cell_id": cell_id,
        "lesson_id": lesson_id,
        "total_students": total_students or 0,
        "submitted_count": status_dict.get("submitted", 0) + status_dict.get("graded", 0),
        "draft_count": status_dict.get("draft", 0),
        "not_started_count": max(0, (total_students or 0) - processed),
        "average_score": float(avg_row.avg_score) if avg_row.avg_score else None,
        "average_time_spent": int(avg_row.avg_time) if avg_row.avg_time else 0,
    }
```

#### 5.3 前端通知组件

创建一个通用的通知组件 `NotificationToast.vue`：

```vue
<template>
  <Transition name="toast">
    <div v-if="visible" :class="toastClass">
      <div class="toast-icon">{{ icon }}</div>
      <div class="toast-content">
        <div class="toast-title">{{ title }}</div>
        <div v-if="message" class="toast-message">{{ message }}</div>
      </div>
      <button @click="close" class="toast-close">×</button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Props {
  type?: 'success' | 'info' | 'warning' | 'error'
  title: string
  message?: string
  duration?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  duration: 5000,
})

const visible = ref(true)

const icon = computed(() => {
  const icons = {
    success: '✓',
    info: 'ℹ',
    warning: '⚠',
    error: '✗',
  }
  return icons[props.type]
})

const toastClass = computed(() => {
  return [
    'toast',
    `toast-${props.type}`,
  ]
})

function close() {
  visible.value = false
}

onMounted(() => {
  if (props.duration > 0) {
    setTimeout(close, props.duration)
  }
})
</script>

<style scoped>
.toast {
  @apply fixed top-4 right-4 z-50 flex items-start gap-3 p-4 rounded-lg shadow-lg min-w-[300px] max-w-[500px];
}

.toast-success {
  @apply bg-green-50 border border-green-200 text-green-800;
}

.toast-info {
  @apply bg-blue-50 border border-blue-200 text-blue-800;
}

.toast-warning {
  @apply bg-yellow-50 border border-yellow-200 text-yellow-800;
}

.toast-error {
  @apply bg-red-50 border border-red-200 text-red-800;
}

.toast-icon {
  @apply text-2xl font-bold;
}

.toast-content {
  @apply flex-1;
}

.toast-title {
  @apply font-semibold mb-1;
}

.toast-message {
  @apply text-sm opacity-90;
}

.toast-close {
  @apply text-xl font-bold opacity-50 hover:opacity-100 cursor-pointer;
}

.toast-enter-active,
.toast-leave-active {
  @apply transition-all duration-300;
}

.toast-enter-from {
  @apply opacity-0 translate-x-full;
}

.toast-leave-to {
  @apply opacity-0 translate-x-full;
}
</style>
```

#### 5.4 前端通用实时订阅（`useRealtimeChannel`）

```typescript
import { onUnmounted, shallowRef } from 'vue'
import type { Ref } from 'vue'
import { websocketService, type WebSocketMessage } from '@/services/websocket'

interface ChannelDescriptor {
  scope: 'session' | 'lesson'
  id: number
}

export function useRealtimeChannel(channelRef: Ref<ChannelDescriptor>) {
  const offFns = new Map<string, () => void>()
  const processedMessages = shallowRef<Set<string>>(new Set())

  function registerListener(type: string, handler: (message: WebSocketMessage) => void) {
    const off = websocketService.subscribe(channelRef.value, type, handler)
    offFns.set(type, off)
  }

  function unregisterAll() {
    offFns.forEach((off) => off())
    offFns.clear()
  }

  onUnmounted(unregisterAll)

  return {
    registerListener,
    unregisterAll,
    processedMessages,
  }
}
```

`websocketService.subscribe` 负责根据 `ChannelDescriptor` 动态选择 session/lesson 通道，内部已处理重连、心跳和降级轮询（接入 6.2 的策略）。组件层不必关心底层连接细节。

### 6. 注意事项和最佳实践

#### 6.1 消息去重

避免重复处理相同的消息：

```typescript
const processedMessages = shallowRef<Set<string>>(new Set())

function handleEvent(message: WebSocketMessage) {
  if (processedMessages.value.has(message.event_id)) return
  processedMessages.value.add(message.event_id)

  // ... 处理消息

  if (processedMessages.value.size > 100) {
    const oldest = processedMessages.value.values().next().value
    processedMessages.value.delete(oldest)
  }
}

registerListener('new_submission', handleEvent)
```

#### 6.2 降级策略

当 WebSocket 不可用时，降级到轮询：

```typescript
const pollingInterval = ref<ReturnType<typeof setInterval> | null>(null)

watch(
  () => websocketService.channelState(sessionChannel.value),
  (state) => {
    if (state === 'connected') {
      clearInterval(pollingInterval.value!)
      pollingInterval.value = null
      return
    }

    if (!pollingInterval.value) {
      pollingInterval.value = setInterval(loadSubmissions, 5000)
    }
  },
  { immediate: true }
)

onUnmounted(() => pollingInterval.value && clearInterval(pollingInterval.value))
```

#### 6.3 性能优化

**防抖处理频繁更新：**

```typescript
import { debounce } from 'lodash-es'

// 防抖统计更新（500ms）
const debouncedUpdateStatistics = debounce((data: any) => {
  statistics.value = data
}, 500)

registerListener('submission_statistics_updated', (message: WebSocketMessage) => {
  debouncedUpdateStatistics(message.data)
})
```

**批量更新列表：**

```typescript
// 收集一段时间内的新提交，批量更新
const pendingSubmissions = ref<any[]>([])
const updateTimer = ref<ReturnType<typeof setTimeout> | null>(null)

function handleNewSubmission(submission: any) {
  pendingSubmissions.value.push(submission)
  
  // 清除之前的定时器
  if (updateTimer.value) {
    clearTimeout(updateTimer.value)
  }
  
  // 500ms 后批量更新
  updateTimer.value = setTimeout(() => {
    submissions.value.unshift(...pendingSubmissions.value)
    pendingSubmissions.value = []
  }, 500)
}
```

#### 6.4 错误处理

**WebSocket 重连机制：**

```typescript
// 在 websocket.ts 中已有重连机制，但需要处理活动相关的重连
websocketService.on('error', (message: WebSocketMessage) => {
  console.error('WebSocket 错误:', message.data)
  // 显示错误提示
  showNotification({
    type: 'error',
    title: '连接错误',
    message: '实时更新已断开，正在尝试重连...',
  })
})

// 重连成功后重新订阅
websocketService.on('connected', () => {
  // 重新设置监听器
  setupWebSocketListeners()
})
```

**消息发送失败处理：**

```python
# 后端：如果 WebSocket 发送失败，记录日志但不影响主流程
try:
    await manager.send_to_teacher(message, session_id, teacher_id)
except Exception as e:
    logger.error(f"Failed to send WebSocket message: {e}")
    # 不抛出异常，允许 API 正常返回
```

### 7. 测试方案

#### 7.1 单元测试

**后端测试：**

```python
# tests/test_activity_websocket.py
import pytest
from app.services.websocket_manager import manager

@pytest.mark.asyncio
async def test_submission_notification():
    """测试提交通知"""
    # 模拟 WebSocket 连接
    # 创建测试提交
    # 验证通知是否发送
    pass

@pytest.mark.asyncio
async def test_grade_notification():
    """测试评分通知"""
    pass
```

**前端测试：**

```typescript
// tests/ActivityViewer.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ActivityViewer from '@/components/Activity/ActivityViewer.vue'

describe('ActivityViewer WebSocket', () => {
  it('should handle grade notification', async () => {
    // 模拟 WebSocket 消息
    // 验证 UI 更新
  })
})
```

#### 7.2 集成测试

**端到端测试场景：**

1. **学生提交 → 教师收到通知**
   - 学生提交活动
   - 验证教师端实时显示新提交
   - 验证统计信息更新

2. **教师评分 → 学生收到通知**
   - 教师评分
   - 验证学生端实时显示分数
   - 验证反馈信息显示

3. **批量操作通知**
   - 教师批量评分
   - 验证所有相关学生收到通知

4. **WebSocket 断开重连**
   - 模拟网络断开
   - 验证自动重连
   - 验证消息不丢失

#### 7.3 压力测试

**多学生同时提交：**

```python
# 模拟 50 个学生同时提交
async def test_concurrent_submissions():
    tasks = []
    for i in range(50):
        task = create_submission(student_id=i)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    # 验证所有通知都正确发送
```

### 8. 部署和监控

#### 8.1 监控指标

**需要监控的指标：**

1. WebSocket 连接数
2. 消息发送成功率
3. 消息延迟
4. 重连次数
5. 错误率

**实现示例：**

```python
# 在 websocket_manager.py 中添加指标收集
class ConnectionManager:
    def __init__(self):
        self.metrics = {
            'total_messages_sent': 0,
            'total_messages_failed': 0,
            'active_connections': 0,
        }
    
    async def send_personal_message(self, ...):
        try:
            await websocket.send_text(json.dumps(message))
            self.metrics['total_messages_sent'] += 1
        except Exception as e:
            self.metrics['total_messages_failed'] += 1
            raise
```

#### 8.2 日志记录

**关键日志点：**

```python
# 提交通知
logger.info(f"Submission notification sent: submission_id={submission.id}, teacher_id={teacher_id}")

# 评分通知
logger.info(f"Grade notification sent: submission_id={submission.id}, student_id={student_id}")

# WebSocket 连接
logger.info(f"Teacher connected: teacher_id={teacher_id}, session_id={session_id}")

# 错误日志
logger.error(f"WebSocket send failed: {error}", exc_info=True)
```

### 9. 后续优化方向

#### 9.1 功能增强

1. **实时答题进度显示**
   - 显示每个学生的答题进度（已完成几题）
   - 显示最后活跃时间
   - 帮助教师了解课堂状态

2. **实时排行榜**
   - 显示提交速度排行榜
   - 显示分数排行榜（可选）
   - 激励学生积极参与

3. **实时讨论区**
   - 学生可以提问
   - 教师可以回答
   - 支持匿名提问

4. **智能提醒**
   - 提醒未提交的学生
   - 提醒教师有新的提交需要评分
   - 基于时间的智能提醒

#### 9.2 性能优化

1. **消息压缩**
   - 对于大量数据，使用压缩算法
   - 减少网络传输量

2. **消息队列**
   - 使用消息队列处理高并发
   - 确保消息顺序和可靠性

3. **缓存优化**
   - 缓存统计信息
   - 减少数据库查询

#### 9.3 用户体验优化

1. **动画效果**
   - 新提交的动画提示
   - 统计数字的动画更新
   - 平滑的过渡效果

2. **声音提示**
   - 可选的提示音
   - 不同事件不同音效

3. **浏览器通知**
   - 使用浏览器原生通知 API
   - 即使页面不在前台也能收到通知

### 10. 总结

本方案通过 WebSocket 实现了活动提交和评分的实时互动，主要特点：

1. **实时性**：学生提交后教师立即收到通知，教师评分后学生立即收到通知
2. **可靠性**：支持重连机制和降级策略，确保在各种网络环境下都能正常工作
3. **可扩展性**：架构设计支持后续功能扩展，如实时进度、排行榜等
4. **用户体验**：通过实时统计、通知提示等提升用户体验

**实施优先级：**
- **高优先级**：基础实时通知功能（阶段一、二、三）
- **中优先级**：优化和测试（阶段四）
- **低优先级**：后续功能增强（9.1）

**预计工作量：**
- 后端开发：3-5 天
- 前端开发：3-5 天
- 测试和优化：2-3 天
- **总计：8-13 天**

### 11. 参考资料

- [WebSocket API 文档](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [FastAPI WebSocket 文档](https://fastapi.tiangolo.com/advanced/websockets/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [课堂同步架构文档](./CLASSROOM_SYNC_ARCHITECTURE.md)

---

**文档版本：** v1.0  
**最后更新：** 2024-01-01  
**维护者：** 开发团队