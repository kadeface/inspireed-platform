# 活动模块数据提交与展示结构说明

## 一、学生端提交的数据包结构

### 1.1 创建提交（草稿）阶段

学生开始答题时，前端会调用 `POST /activities/submissions` 创建草稿，请求数据结构如下：

```typescript
interface ActivitySubmissionCreate {
  cellId: number | string  // 支持数字 ID 或 UUID 字符串
  lessonId: number
  sessionId?: number  // 课堂会话ID（课堂模式必须提供）
  responses?: Record<string, ItemAnswer>  // 初始答案（可能为空）
  startedAt?: string  // ISO 8601 格式的时间戳
  processTrace?: ProcessTraceEvent[]  // 过程追踪数据（可选）
  context?: Record<string, any>  // 上下文数据（可选）
  activityPhase?: string  // 活动阶段（可选）
  attemptNo?: number  // 尝试次数（默认1）
}
```

**实际发送的 HTTP 请求体（snake_case）：**
```json
{
  "cell_id": 123,  // 或 UUID 字符串
  "lesson_id": 456,
  "session_id": 789,  // 可选，课堂模式必须有
  "responses": {
    "item-uuid-1": {
      "answer": "A"  // 单选题答案：选项ID
    },
    "item-uuid-2": {
      "answer": ["A", "C"]  // 多选题答案：选项ID数组
    },
    "item-uuid-3": {
      "text": "这是简答题答案..."
    },
    "item-uuid-4": {
      "value": 4  // 量表题答案：数值
    }
  },
  "started_at": "2024-01-15T10:30:00Z"
}
```

### 1.2 正式提交阶段

学生点击提交按钮时，前端会调用：
1. 先创建/更新提交：`POST /activities/submissions` 或 `PATCH /activities/submissions/{id}`
2. 然后正式提交：`POST /activities/submissions/{submission_id}/submit`

**正式提交请求数据结构：**
```typescript
interface ActivitySubmissionSubmit {
  responses: Record<string, ItemAnswer>  // 完整的答案字典
  sessionId?: number  // 课堂会话ID（课堂模式必须提供）
  timeSpent?: number  // 用时（秒）
  processTrace?: ProcessTraceEvent[]
  context?: Record<string, any>
  activityPhase?: string
  attemptNo?: number
}
```

**实际发送的 HTTP 请求体：**
```json
{
  "responses": {
    "item-uuid-1": {
      "answer": "A"
    },
    "item-uuid-2": {
      "answer": ["A", "C"]
    },
    "item-uuid-3": {
      "text": "这是简答题答案..."
    }
  },
  "session_id": 789,
  "time_spent": 1250  // 秒
}
```

### 1.3 答案数据结构（ItemAnswer）

根据题目类型，答案格式不同：

#### 单选题（single-choice）
```json
{
  "answer": "option-id-A"  // 选项ID
}
```

#### 多选题（multiple-choice）
```json
{
  "answer": ["option-id-A", "option-id-C"]  // 选项ID数组
}
```

#### 判断题（true-false）
```json
{
  "answer": true  // 或 false
}
```

#### 简答题/论述题（short-answer / long-answer）
```json
{
  "text": "学生的文本答案..."
}
```

#### 文件上传（file-upload）
```json
{
  "files": ["https://example.com/file1.pdf", "https://example.com/file2.docx"]
}
```

#### 代码提交（code-submission）
```json
{
  "code": "def hello():\n    print('Hello')",
  "testResults": [...]  // 可选
}
```

#### 量表题（scale）
```json
{
  "value": 4  // 1-5 的数值
}
```

---

## 二、后端处理与存储

### 2.1 后端接收与验证

后端接收到提交后：

1. **验证数据格式**：使用 Pydantic Schema (`ActivitySubmissionCreate` / `ActivitySubmissionSubmit`)
2. **处理 cell_id**：如果是 UUID，从 `lesson.content` 中查找并创建/映射到数据库 Cell 记录
3. **自动评分**：对于选择题和判断题，后端会自动评分并更新 `responses`：
   ```json
   {
     "item-uuid-1": {
       "answer": "A",
       "correct": true,  // 后端添加
       "correctAnswer": "A",  // 后端添加
       "correctAnswerId": "A",  // 后端添加
       "score": 10  // 后端计算（如果正确）
     }
   }
   ```

### 2.2 数据库存储结构

提交数据存储在 `activity_submissions` 表中：

```python
class ActivitySubmission(Base):
    id: int  # 主键
    cell_id: int  # 关联的 Cell ID
    lesson_id: int  # 关联的教案 ID
    student_id: int  # 学生 ID
    session_id: int | None  # 课堂会话ID（NULL表示课后提交）
    
    # JSON 字段
    responses: dict  # 答案字典（包含评分后的完整信息）
    process_trace: list  # 过程追踪
    context: dict  # 上下文数据
    
    # 评分字段
    score: float | None  # 实际得分
    max_score: float | None  # 满分
    auto_graded: bool  # 是否自动评分
    
    # 状态
    status: ActivitySubmissionStatus  # draft, submitted, graded, returned
    
    # 时间戳
    started_at: datetime | None
    submitted_at: datetime | None
    graded_at: datetime | None
    
    # 元数据
    time_spent: int | None  # 用时（秒）
    teacher_feedback: str | None
    graded_by: int | None
    is_late: bool
```

---

## 三、教师端接收的提交数据结构

**✅ 回答：教师端接收的信息包括所有关键字段！**

教师端接收到的数据**包含**以下所有字段：
- ✅ `cell_id`：活动ID（支持数字或UUID）
- ✅ `lesson_id`：教案ID  
- ✅ `session_id`：课堂会话ID（**关键字段**，NULL表示课后提交）

**⚠️ 关于 `session_id` 的重要性：**
如果不包括 `session_id` 或查询时不传递 `session_id` 参数，确实会导致问题：
- 同一课程被多个班级上时，所有班级的提交都会统计在一起
- 无法区分是哪个课堂会话的提交
- 统计会包含所有历史提交（包括其他课堂和课后提交）

**解决方案：**
- 后端API调用时**必须传递 `session_id` 参数**：`GET /activities/cells/{cell_id}/submissions?session_id={session_id}`
- 后端会严格过滤，只返回该会话的提交（第538-539行）
- 前端也会进行客户端过滤（双重保险）

### 3.1 API 返回结构

教师端调用 `GET /activities/cells/{cell_id}/submissions` 获取提交列表，返回：

```typescript
interface ActivitySubmissionWithStudent {
  // 基础信息（重要：这些字段都会返回）
  id: number
  cellId: number              // ✅ 活动ID（支持数字或UUID）
  lessonId: number            // ✅ 教案ID
  studentId: number
  sessionId?: number          // ✅ 课堂会话ID（关键字段，NULL表示课后提交）
  
  // 学生信息（教师端特有）
  studentName: string
  studentEmail: string
  
  // 答案数据
  responses: Record<string, ItemAnswer>  // 已包含自动评分信息
  
  // 评分信息
  score?: number
  maxScore?: number
  autoGraded: boolean
  teacherFeedback?: string
  gradedBy?: number
  
  // 状态
  status: 'draft' | 'submitted' | 'graded' | 'returned'
  
  // 时间信息
  startedAt?: string
  submittedAt?: string
  gradedAt?: string
  timeSpent?: number  // 秒
  
  // 元数据
  isLate: boolean
  attemptNo: number
  submissionCount: number
}
```

**实际 API 返回示例（JSON）：**
```json
{
  "id": 1001,
  "cell_id": 123,              // ✅ 活动ID
  "lesson_id": 456,            // ✅ 教案ID
  "student_id": 789,
  "session_id": 101,           // ✅ 课堂会话ID（关键！）
  "student_name": "张三",
  "student_email": "zhangsan@example.com",
  "responses": {
    "item-uuid-1": {
      "answer": "A",
      "correct": true,
      "correctAnswer": "A",
      "correctAnswerId": "A",
      "score": 10
    },
    "item-uuid-2": {
      "answer": ["A", "C"],
      "correct": false,
      "correctAnswer": "A, B",
      "score": 0
    },
    "item-uuid-3": {
      "text": "这是学生的简答题答案..."
    }
  },
  "score": 10,
  "max_score": 100,
  "auto_graded": true,
  "status": "submitted",
  "submitted_at": "2024-01-15T10:52:30Z",
  "time_spent": 1250,
  "is_late": false
}
```

**⚠️ 重要说明：**
- **`cell_id`**：会返回，用于标识是哪个活动的提交
- **`lesson_id`**：会返回，用于标识是哪个教案的提交
- **`session_id`**：会返回，这是**关键字段**，用于区分不同课堂会话的提交
  - 如果 `session_id` 为 `null` 或 `undefined`，表示是课后提交
  - 如果 `session_id` 有值（如 `101`），表示是该课堂会话的提交
  - **后端API会严格按 `session_id` 过滤**（如果提供了 `session_id` 参数）
  - **前端也会进行客户端过滤**（双重保险，确保只显示当前会话的提交）

### 3.2 提交列表数据过滤

教师端获取提交列表时，支持以下过滤：

- **按状态筛选**：`?status=submitted` （draft, submitted, graded, returned, not_started）
- **按会话筛选**：`?session_id=101` ⚠️ **关键参数**（只显示该会话的提交）
- **包含未开始学生**：`?include_not_started=true` （显示所有学生，包括未提交的）

**⚠️ 关于 `session_id` 的重要性：**

1. **如果不传递 `session_id`**：
   - 后端会返回该 `cell_id` 的所有提交（包括所有课堂会话和课后提交）
   - 这会导致统计混淆：同一个课程被多个班级上时，会统计所有班级的提交
   - **不推荐在课堂模式下不传递 `session_id`**

2. **如果传递了 `session_id`**：
   - 后端会严格过滤，只返回该会话的提交（第538-539行）
   - 确保只显示当前课堂会话的提交，不会混入其他会话的提交
   - **这是推荐的用法，特别是在课堂模式下**

3. **双重过滤机制**：
   - 后端过滤：SQL查询时添加 `WHERE session_id = {session_id}` 条件
   - 前端过滤：前端收到数据后，再次检查 `sessionId` 字段（第560-577行）
   - 这样可以确保即使后端过滤失效，前端也能正确过滤

**示例 API 调用：**
```typescript
// ✅ 正确：传递 session_id，只获取该会话的提交
GET /activities/cells/123/submissions?session_id=101&lesson_id=456

// ❌ 错误（课堂模式下）：不传递 session_id，会获取所有提交
GET /activities/cells/123/submissions?lesson_id=456
```

---

## 四、教师端数据展示

### 4.1 提交列表视图（SubmissionList.vue）

#### 4.1.1 统计卡片

显示总体统计信息：

```typescript
interface SubmissionStatistics {
  totalStudents: number      // 总学生数
  submittedCount: number     // 已提交数
  submittedPercent: number   // 已提交百分比
  draftCount: number         // 草稿数
  draftPercent: number       // 草稿百分比
  gradedCount: number        // 已评分数
  gradedPercent: number      // 已评分百分比
}
```

**显示位置：** 列表顶部统计卡片区域

#### 4.1.2 提交列表表格

表格列包括：

| 列名 | 数据来源 | 说明 |
|------|---------|------|
| 学生 | `studentName` / `studentEmail` | 学生姓名和邮箱 |
| 状态 | `status` | 草稿/已提交/已评分/已退回 |
| 分数 | `score` / `maxScore` | 得分/满分 |
| 提交时间 | `submittedAt` | 格式化显示（如：01/15 10:52） |
| 用时 | `timeSpent` | 格式化显示（如：20分钟） |
| 操作 | - | 查看/评分按钮 |

**显示位置：** `frontend/src/components/Activity/Teacher/SubmissionList.vue` (第83-169行)

#### 4.1.3 选择题选项统计

对于选择题（单选题、多选题、判断题），显示选项分布统计：

```typescript
interface ChoiceItemStatistics {
  itemId: string
  order: number
  type: 'single-choice' | 'multiple-choice' | 'true-false'
  question: string
  options: Array<{
    id: string
    label: string
    isCorrect: boolean  // 是否为正确答案
    count: number       // 选择该选项的学生数
    percentage: number  // 选择该选项的百分比
  }>
}
```

**显示位置：** 列表底部，单独的区域展示（第179-214行）

**示例显示：**
```
📊 选择题选项分布

第 1 题 [单选题]
问题：以下哪个是正确的？

选项A [✓ 正确答案]    15人  75%  ████████████████
选项B                 3人  15%  ███
选项C                 2人  10%  ██
```

### 4.2 评分模态框视图（GradingModal.vue）

当教师点击"查看"或"评分"按钮时，打开评分模态框，显示：

#### 4.2.1 提交信息区域

- **提交时间**：`submittedAt`
- **用时**：`timeSpent`（格式化显示）
- **迟交标记**：`isLate`（如果有）

#### 4.2.2 学生答案区域

按题目顺序显示每道题的答案：

**选择题（单选题/多选题）**
- 显示学生选择的选项文本
- 显示正确性判断（✓ 正确 / ✗ 错误）
- 显示正确答案（如果有）

**文本题（简答题/论述题）**
- 显示学生的文本答案（可滚动查看）

**量表题**
- 显示学生评分的数值

**其他类型**
- 以 JSON 格式显示答案内容

#### 4.2.3 评分输入区域

- **分项评分**：每道题可以单独输入得分（如果题目有分值）
- **总分输入**：输入总体得分（0 - 满分）
- **教师反馈**：多行文本输入框

**显示位置：** `frontend/src/components/Activity/Teacher/GradingModal.vue`

---

## 五、数据流转完整流程

```
学生端答题
  ↓
[ActivityViewer.vue]
  ↓ 收集答案到 answers.value (Record<itemId, ItemAnswer>)
  ↓
点击提交按钮
  ↓
调用 activityService.createSubmission() 
  → POST /activities/submissions
  → 创建草稿（status: DRAFT）
  ↓
调用 activityService.submitActivity()
  → POST /activities/submissions/{id}/submit
  → 更新状态为 SUBMITTED
  → 后端自动评分（选择题）
  → 更新 responses（添加 correct, score 等字段）
  ↓
后端 WebSocket 通知教师端
  → new_submission 事件
  → submission_statistics_updated 事件
  ↓
教师端 [SubmissionList.vue]
  ↓ 监听 WebSocket 事件或轮询
  ↓ 调用 activityService.getCellSubmissions()
  → GET /activities/cells/{cell_id}/submissions?session_id={id}
  ↓
后端返回 ActivitySubmissionWithStudent[]
  ↓
前端展示：
  1. 统计卡片（计算得出）
  2. 提交列表表格
  3. 选择题选项统计（从 responses 中计算）
  ↓
教师点击"查看"/"评分"
  ↓
打开 [GradingModal.vue]
  ↓ 显示详细答案
  ↓ 教师输入评分和反馈
  ↓
调用 activityService.gradeSubmission()
  → POST /activities/submissions/{id}/grade
  ↓
后端更新：
  - score, teacher_feedback, graded_by, graded_at
  - status: GRADED
  ↓
前端刷新列表
```

---

## 六、关键数据结构总结

### 6.1 学生提交时的 `responses` 结构

```typescript
{
  "item-uuid-1": { "answer": "A" },           // 单选题
  "item-uuid-2": { "answer": ["A", "C"] },    // 多选题
  "item-uuid-3": { "text": "答案..." },       // 简答题
  "item-uuid-4": { "value": 4 }               // 量表题
}
```

### 6.2 后端处理后（自动评分）的 `responses` 结构

```typescript
{
  "item-uuid-1": {
    "answer": "A",
    "correct": true,
    "correctAnswer": "A",
    "correctAnswerId": "A",
    "score": 10
  },
  "item-uuid-2": {
    "answer": ["A", "C"],
    "correct": false,
    "correctAnswer": "A, B",
    "score": 0
  },
  "item-uuid-3": {
    "text": "答案..."  // 简答题不自动评分
  }
}
```

### 6.3 教师端看到的完整提交对象

```typescript
{
  id: 1001,
  studentName: "张三",
  studentEmail: "zhangsan@example.com",
  status: "submitted",
  score: 10,
  maxScore: 100,
  submittedAt: "2024-01-15T10:52:30Z",
  timeSpent: 1250,
  responses: { /* 如上所示 */ },
  // ... 其他字段
}
```

---

## 七、注意事项

1. **cell_id 支持 UUID**：前端可能传递 UUID 字符串，后端会自动映射到数据库的数字 ID
2. **session_id 的重要性**：⚠️ **关键字段**
   - 课堂模式下**必须传递 `session_id`**，用于区分不同课堂会话的提交
   - 如果不传递 `session_id`，会导致统计混淆：同一课程被多个班级上时，会统计所有班级的提交
   - 后端API会严格按 `session_id` 过滤（如果提供了该参数）
   - 前端也会进行客户端过滤（双重保险）
3. **教师端接收的数据包含完整字段**：
   - ✅ `cell_id`：活动ID（支持数字或UUID）
   - ✅ `lesson_id`：教案ID
   - ✅ `session_id`：课堂会话ID（NULL表示课后提交）⚠️ **关键字段**
4. **自动评分**：只有选择题和判断题会进行自动评分，简答题需要教师手动评分
5. **实时更新**：教师端通过 WebSocket 实时接收新提交通知，同时使用轮询作为备用
6. **数据格式转换**：后端 API 返回 snake_case，前端自动转换为 camelCase
7. **未开始学生**：教师端可以显示未开始的学生（`id: 0`, `status: DRAFT`），作为占位符

---

## 八、相关文件位置

- **学生端提交组件**：`frontend/src/components/Activity/ActivityViewer.vue`
- **教师端列表组件**：`frontend/src/components/Activity/Teacher/SubmissionList.vue`
- **教师端评分组件**：`frontend/src/components/Activity/Teacher/GradingModal.vue`
- **API 服务**：`frontend/src/services/activity.ts`
- **后端 API**：`backend/app/api/v1/activities.py`
- **数据模型**：`backend/app/models/activity.py`
- **Schema 定义**：`backend/app/schemas/activity.py`
- **类型定义**：`frontend/src/types/activity.ts`

