# 活动模块信息提交工作流文档

## 📋 概述

本文档详细说明活动模块（Activity）的信息提交工作流，包括学生提交、教师查看评分，以及结果展示机制。

---

## 🔄 完整工作流程

### 1. 学生端：答题与提交流程

#### 1.1 答题界面（ActivityViewer.vue）

**位置**: `frontend/src/components/Activity/ActivityViewer.vue`

**功能特性**:
- ✅ 支持多种题型：单选题、多选题、判断题、简答题、论述题、量表评分等
- ✅ 实时保存草稿（每3秒自动保存）
- ✅ 离线支持：使用 IndexedDB 本地存储，联网后自动同步
- ✅ 进度显示：显示已完成题目数和百分比
- ✅ 必答题验证：提交前检查所有必答题是否完成

**关键代码流程**:

```typescript
// 1. 初始化时加载已保存的答案
onMounted(async () => {
  // 从 IndexedDB 加载离线数据
  const offlineData = await loadFromIndexedDB()
  if (offlineData) {
    answers.value = offlineData
  }
  
  // 如果在线，从服务器加载最新数据
  if (isOnline.value) {
    const submission = await activityService.getMyCellSubmission(cellId)
    if (submission) {
      answers.value = submission.responses || {}
      if (submission.status === 'submitted') {
        isSubmitted.value = true
        submissionData.value = submission  // 包含正确答案
      }
    }
  }
})

// 2. 自动保存答案（防抖）
watch(answers, () => {
  saveTimeout = window.setTimeout(() => {
    syncToServer(answers.value, 'draft').catch(() => {
      // 离线时保存到 IndexedDB
    })
  }, 3000)
}, { deep: true })

// 3. 正式提交
async function handleSubmit() {
  // 创建或更新提交记录
  const submission = await activityService.createSubmission({
    cellId: getActualCellId(),
    lessonId: lessonId.value,
    responses: answers.value,
    startedAt: startTime.value.toISOString(),
  })
  
  // 正式提交（触发自动评分）
  const submittedSubmission = await activityService.submitActivity(submission.id, {
    responses: answers.value,
    timeSpent: Math.floor((Date.now() - startTime.value.getTime()) / 1000),
  })
  
  // 保存包含正确答案的完整数据
  submissionData.value = submittedSubmission
  isSubmitted.value = true
}
```

#### 1.2 提交状态流转

```
草稿 (draft) 
  ↓ [学生点击"提交答案"]
已提交 (submitted) 
  ↓ [自动评分或教师评分]
已评分 (graded)
  ↓ [可选：教师退回]
已退回 (returned)
```

#### 1.3 离线支持机制

**实现位置**: `frontend/src/composables/useOfflineActivity.ts`

**特性**:
- 使用 IndexedDB 存储答案
- 自动检测网络状态
- 联网后自动同步到服务器
- 支持版本冲突检测

---

### 2. 教师端：查看与评分流程

#### 2.1 提交列表（SubmissionList.vue）

**位置**: `frontend/src/components/Activity/Teacher/SubmissionList.vue`

**功能特性**:
- ✅ 显示所有学生的提交记录
- ✅ 按状态筛选（草稿/已提交/已评分/已退回）
- ✅ 显示学生信息、分数、提交时间、用时
- ✅ 批量操作：批量评分、批量退回
- ✅ 实时刷新

**关键代码**:

```typescript
// 加载提交列表
async function loadSubmissions() {
  const data = await activityService.getCellSubmissions(
    props.cellId,
    statusFilter.value || undefined
  )
  submissions.value = data
}

// 后端 API: GET /activities/cells/{cell_id}/submissions
// 返回格式：
[
  {
    id: 1,
    student_id: 123,
    student_name: "张三",
    student_email: "zhangsan@example.com",
    status: "submitted",
    score: 85,
    max_score: 100,
    submitted_at: "2024-01-15T10:30:00Z",
    time_spent: 1800,
    is_late: false,
    responses: { ... }
  },
  ...
]
```

#### 2.2 评分界面（GradingModal.vue）

**位置**: `frontend/src/components/Activity/Teacher/GradingModal.vue`

**功能特性**:
- ✅ 查看学生完整答案
- ✅ 逐题评分（支持分项打分）
- ✅ 总体评分和反馈
- ✅ 显示提交时间和用时
- ✅ 标记迟交

**评分流程**:

```typescript
// 保存评分
async function handleSaveGrade() {
  await activityService.gradeSubmission(props.submission.id, {
    score: totalScore.value,
    teacherFeedback: feedback.value,
    itemScores: itemScores.value,  // 每题的分数
  })
  emit('graded')  // 触发列表刷新
}

// 后端 API: POST /activities/submissions/{submission_id}/grade
```

#### 2.3 结果展示机制

**在 ActivityCell.vue 中的展示逻辑**:

```vue
<!-- 教师查看学生提交模式 -->
<div v-else-if="isTeacher" class="activity-teacher-view">
  <div class="teacher-view-header">
    <h3>{{ cell.content.title }}</h3>
    <p>{{ cell.content.description }}</p>
  </div>
  
  <!-- 学生提交列表 -->
  <SubmissionList
    :cell-id="actualCellId"
    :activity="cell.content"
  />
</div>
```

**展示内容**:
- 活动标题和描述
- 所有学生的提交列表（表格形式）
- 每个提交的状态、分数、时间等信息
- 操作按钮（查看、评分）

---

### 3. 后端 API 流程

#### 3.1 提交相关 API

| API | 方法 | 说明 |
|-----|------|------|
| `/activities/submissions` | POST | 创建提交（草稿） |
| `/activities/submissions/{id}` | GET | 获取提交详情 |
| `/activities/submissions/{id}` | PATCH | 更新提交（保存草稿） |
| `/activities/submissions/{id}/submit` | POST | 正式提交（触发自动评分） |
| `/activities/submissions/{id}/grade` | POST | 教师评分 |
| `/activities/cells/{cell_id}/submissions` | GET | 获取所有提交（教师端） |
| `/activities/cells/{cell_id}/my-submission` | GET | 获取我的提交（学生端） |

#### 3.2 自动评分机制

**位置**: `backend/app/api/v1/activities.py`

**流程**:
1. 学生提交时，后端调用 `_auto_grade_submission()` 函数
2. 对于选择题、判断题等客观题，自动判断正确性并计算分数
3. 更新 `responses` 字段，添加 `correct`、`score`、`correctAnswer` 等信息
4. 如果所有题目都是客观题且启用了自动评分，直接标记为 `graded`

**关键代码**:

```python
# 提交时自动评分
auto_graded, total_score, max_score, graded_responses = _auto_grade_submission(
    data.responses,
    cell_content
)

# 更新 responses（包含正确性判断）
submission.responses = graded_responses
submission.score = total_score
submission.max_score = max_score
submission.auto_graded = auto_graded

if auto_graded and all_auto_gradable:
    submission.status = ActivitySubmissionStatus.GRADED
```

#### 3.3 WebSocket 实时通知

**位置**: `backend/app/api/v1/activities.py` (submit_activity 函数)

**功能**:
- 学生提交后，通过 WebSocket 实时通知教师
- 发送新提交通知，包含学生信息、状态、分数等

---

## ✅ 当前实现状态

### 已实现功能

1. ✅ **学生提交流程**
   - 答题界面完整
   - 草稿自动保存
   - 离线支持
   - 正式提交
   - 查看提交结果（包含正确答案）

2. ✅ **教师查看流程**
   - 查看所有学生提交列表
   - 按状态筛选
   - 查看单个提交详情
   - 评分功能
   - 批量操作

3. ✅ **结果展示**
   - 学生端：提交后显示正确答案和得分
   - 教师端：清晰的表格展示所有提交
   - 状态标识（草稿/已提交/已评分/已退回）

4. ✅ **自动评分**
   - 选择题自动判断
   - 自动计算分数
   - 支持混合评分（部分自动+部分手动）

---

## ❌ 缺失功能：范例推送

### 问题描述

**目前系统中没有实现"教师推送范例答案给学生"的功能。**

### 功能需求

教师应该能够：
1. 选择一个优秀的学生提交作为范例
2. 或者手动创建范例答案
3. 将范例推送给所有学生或特定学生
4. 学生可以在答题后查看范例答案

### 建议实现方案

#### 方案 1：基于现有提交的范例推送

**数据结构扩展**:

```typescript
// 在 ActivityCellContent 中添加
export interface ActivityCellContent {
  // ... 现有字段
  exampleSubmission?: {
    enabled: boolean
    submissionId?: number  // 引用某个学生提交作为范例
    customAnswers?: Record<string, ItemAnswer>  // 或自定义范例答案
    publishedAt?: string
    visibleTo?: 'all' | 'submitted' | 'graded'
  }
}
```

**后端 API**:

```python
# 标记某个提交为范例
POST /activities/submissions/{submission_id}/set-as-example

# 发布范例给学生
POST /activities/cells/{cell_id}/publish-example
{
  "submission_id": 123,  # 或
  "custom_answers": {...}
}

# 学生获取范例
GET /activities/cells/{cell_id}/example
```

**前端实现**:

1. **教师端**（在 SubmissionList 或 GradingModal 中）:
   - 添加"设为范例"按钮
   - 添加"发布范例"功能

2. **学生端**（在 ActivityViewer 中）:
   - 提交后显示"查看范例答案"按钮
   - 显示范例答案（与自己的答案对比）

#### 方案 2：在活动配置中预设范例答案

**数据结构扩展**:

```typescript
// 在 ActivityItem 中添加
export interface ActivityItemBase {
  // ... 现有字段
  exampleAnswer?: ItemAnswer  // 范例答案
  showExampleAfter?: 'submit' | 'deadline' | 'manual'  // 何时显示范例
}
```

**实现位置**:
- 编辑器中：教师可以为每道题设置范例答案
- 查看器中：根据配置显示范例答案

---

## 📊 数据流图

```
学生答题
  ↓
[ActivityViewer]
  ↓ 自动保存
草稿 (IndexedDB + 服务器)
  ↓ 学生提交
[POST /activities/submissions/{id}/submit]
  ↓
已提交 + 自动评分
  ↓
[WebSocket 通知]
  ↓
教师收到通知
  ↓
[SubmissionList] 显示新提交
  ↓ 教师点击"评分"
[GradingModal] 查看详情
  ↓ 教师评分
[POST /activities/submissions/{id}/grade]
  ↓
已评分
  ↓
学生可查看评分结果
```

---

## 🔍 关键文件清单

### 前端文件

- `frontend/src/components/Cell/ActivityCell.vue` - 活动 Cell 主组件
- `frontend/src/components/Activity/ActivityViewer.vue` - 学生答题界面
- `frontend/src/components/Activity/Teacher/SubmissionList.vue` - 教师提交列表
- `frontend/src/components/Activity/Teacher/GradingModal.vue` - 教师评分界面
- `frontend/src/services/activity.ts` - 活动 API 服务
- `frontend/src/composables/useOfflineActivity.ts` - 离线支持

### 后端文件

- `backend/app/api/v1/activities.py` - 活动 API 端点
- `backend/app/models/activity.py` - 活动数据模型
- `backend/app/schemas/activity.py` - 活动数据模式

---

## 🎯 最佳实践建议

### 1. 确保教师能看到所有提交

- ✅ 已实现：`get_cell_submissions` API 返回所有学生的提交
- ✅ 已实现：按状态筛选功能
- ✅ 已实现：实时刷新按钮

**建议增强**:
- 添加搜索功能（按学生姓名/邮箱）
- 添加排序功能（按分数/时间）
- 添加导出功能（Excel/CSV）

### 2. 结果清晰展示

- ✅ 已实现：表格形式展示，包含关键信息
- ✅ 已实现：状态徽章（颜色区分）
- ✅ 已实现：分数显示

**建议增强**:
- 添加统计图表（分数分布、完成率等）
- 添加题目级统计（每题的答对率）
- 添加对比视图（学生答案 vs 正确答案）

### 3. 范例推送功能（待实现）

**优先级**: 高

**实现步骤**:
1. 扩展数据模型，添加范例相关字段
2. 实现后端 API（设置范例、发布范例、获取范例）
3. 前端教师端：添加"设为范例"和"发布范例"功能
4. 前端学生端：添加"查看范例答案"功能
5. 添加权限控制（只有教师可以设置范例）

---

## 📝 总结

当前活动模块的提交工作流已经**基本完整**，包括：

✅ **学生端**：答题、保存、提交、查看结果  
✅ **教师端**：查看列表、评分、批量操作  
✅ **数据流**：离线支持、自动同步、实时通知  
✅ **评分机制**：自动评分 + 手动评分

**缺失功能**：
❌ **范例推送**：教师无法将优秀答案或范例推送给学生观摩

建议优先实现范例推送功能，以完善教学活动闭环。

