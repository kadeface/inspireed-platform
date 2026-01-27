# 活动模块极简实现方案

## 概述

这是**极简版**的活动模块实现方案，移除了所有复杂功能，只保留核心流程：

✅ **点击提交才提交** - 不保存草稿，不自动保存  
✅ **实时统计** - 教师端实时查看学生提交和统计  
✅ **一步完成** - 学生点击提交按钮后，创建并立即提交

## 核心流程

```
学生打开活动 → 答题（答案只在内存中） → 点击"提交"按钮 → 后端保存 → 教师端实时更新
```

## 已移除的功能

- ❌ **草稿保存** - 不创建草稿记录
- ❌ **自动保存** - 不自动保存答案到服务器
- ❌ **保存草稿按钮** - UI中移除草稿保存按钮
- ❌ **离线支持** - 简化版不处理离线场景
- ❌ **草稿加载** - 不加载之前的草稿（只加载已提交的内容）

## 实现细节

### 学生端（ActivityViewer.vue）

**提交逻辑：**
```typescript
async function handleSubmit() {
  // 1. 创建提交记录（状态为DRAFT）
  const submission = await activityService.createSubmission({
    cellId: cellId,
    lessonId: lessonId,
    sessionId: sessionId,
    responses: answers.value,  // 所有答案
    startedAt: startTime.value.toISOString(),
  })
  
  // 2. 立即提交（状态改为SUBMITTED）
  const submittedSubmission = await activityService.submitActivity(submission.id, {
    responses: answers.value,
    timeSpent: timeSpent,
    sessionId: sessionId,
  })
  
  // 3. 更新UI，显示已提交状态
  isSubmitted.value = true
  submissionData.value = submittedSubmission
}
```

**关键点：**
- 答案只在 `answers.value` 中保存（内存）
- 不调用自动保存函数
- 不监听答案变化
- 只检查是否已提交过（不加载草稿）

### 教师端

**统计显示（SubmissionStatistics.vue）：**
- 组件挂载时获取初始统计
- 监听 WebSocket 实时更新
- WebSocket 断开时降级到轮询（每5秒）

**提交列表（SubmissionList.vue）：**
- 组件挂载时获取提交列表
- 可以手动刷新

### 后端（activities.py）

**提交处理：**
```python
async def submit_activity(submission_id, data):
    # 1. 更新状态为 SUBMITTED
    submission.status = ActivitySubmissionStatus.SUBMITTED
    submission.submitted_at = datetime.utcnow()
    
    # 2. 自动评分（如果是选择题）
    auto_graded, total_score, max_score, graded_responses = _auto_grade_submission(...)
    
    # 3. 更新统计数据
    await _update_statistics(db, cell_id, lesson_id)
    
    # 4. WebSocket 推送通知
    # - new_submission（新提交通知）
    # - submission_statistics_updated（统计更新）
```

## API调用流程

```
学生点击提交
  ↓
POST /api/v1/activities/submissions
  Body: { cell_id, lesson_id, session_id, responses, started_at }
  ↓
创建提交记录（status=DRAFT）
  ↓
POST /api/v1/activities/submissions/{id}/submit
  Body: { responses, time_spent, session_id }
  ↓
更新状态为 SUBMITTED
自动评分
更新统计
WebSocket 推送
  ↓
教师端接收通知并更新UI
```

## 数据流图

```
┌─────────────────┐
│  学生端         │
│  ActivityViewer │
└────────┬────────┘
         │
         │ 1. 学生答题（答案在内存中）
         │
         │ 2. 点击"提交"按钮
         │
         ├─→ POST /submissions (创建)
         │   └─→ 创建提交记录（DRAFT）
         │
         ├─→ POST /submissions/{id}/submit (提交)
         │   └─→ 更新状态为 SUBMITTED
         │       ├─→ 自动评分
         │       ├─→ 更新统计
         │       └─→ WebSocket 推送
         │
         └─→ 显示"已提交"状态

┌─────────────────┐
│  教师端         │
│  TeacherControl │
│  Panel          │
└────────┬────────┘
         │
         ├─→ SubmissionStatistics
         │   ├─→ GET /statistics（初始化）
         │   ├─→ WebSocket 监听（实时）
         │   └─→ 轮询降级（每5秒）
         │
         └─→ SubmissionList
             ├─→ GET /submissions（初始化）
             └─→ 手动刷新
```

## 关键代码位置

### 前端
- `frontend/src/components/Activity/ActivityViewer.vue` - 学生答题界面（已简化）
- `frontend/src/components/Activity/SubmissionStatistics.vue` - 统计面板
- `frontend/src/components/Activity/Teacher/SubmissionList.vue` - 提交列表
- `frontend/src/services/activity.ts` - API服务

### 后端
- `backend/app/api/v1/activities.py` - 活动API
  - `create_submission()` - 创建提交
  - `submit_activity()` - 提交活动
  - `_update_statistics()` - 更新统计
- `backend/app/services/realtime.py` - WebSocket推送

## 优点

1. **简单** - 代码逻辑清晰，易于维护
2. **可靠** - 减少中间状态，降低出错概率
3. **快速** - 不频繁保存，减少服务器负载
4. **实时** - WebSocket推送保证实时性

## 注意事项

1. **答案丢失风险** - 刷新页面会丢失未提交的答案（简化版的权衡）
2. **网络要求** - 提交时需要网络连接
3. **不适合长时间答题** - 建议用于短时间的课堂测验

## 如果需要更复杂的功能

如果需要添加：
- 草稿保存
- 自动保存
- 离线支持

请参考 `SIMPLE_ACTIVITY_FLOW.md` 中的完整实现方案。

