# 前端命名规范统一方案

## 📋 目录

1. [现状分析](#现状分析)
2. [统一规范](#统一规范)
3. [迁移计划](#迁移计划)
4. [具体操作步骤](#具体操作步骤)
5. [需要修改的文件清单](#需要修改的文件清单)
6. [注意事项](#注意事项)
7. [验证检查清单](#验证检查清单)

---

## 🔍 现状分析

### 当前命名情况

#### 使用 camelCase 的文件
- `frontend/src/types/activity.ts` - 活动相关接口
  - `cellId`, `lessonId`, `studentId`, `maxScore`, `teacherFeedback`
  - `createdAt`, `updatedAt`, `startedAt`, `submittedAt`, `gradedAt`
  - `processTrace`, `activityPhase`, `attemptNo`, `timeSpent`, `isLate`

- `frontend/src/services/classroomSession.ts` - 课堂会话服务
  - 部分接口使用 `camelCase`，并在响应时手动转换

#### 使用 snake_case 的文件
- `frontend/src/types/lesson.ts` - 教案相关接口
  - `creator_id`, `course_id`, `chapter_id`, `created_at`, `updated_at`
  - `cover_image_url`, `reference_resource_id`, `cell_count`

- `frontend/src/types/user.ts` - 用户相关接口
  - `full_name`, `is_active`, `region_id`, `school_id`, `created_at`

- `frontend/src/types/curriculum.ts` - 课程体系接口
  - 大部分使用 `snake_case`

### 存在的问题

1. **命名不一致**：同一项目中混用两种命名风格
2. **手动转换开销**：API服务层需要手动转换字段名
3. **容易出错**：转换逻辑分散，容易遗漏或出错
4. **维护困难**：新开发者不知道应该使用哪种命名
5. **类型安全降低**：手动转换可能丢失类型检查

### 手动转换示例

**activity.ts 中的转换：**
```typescript
// 发送请求时：camelCase -> snake_case
const requestData: any = {
  cell_id: data.cellId,
  lesson_id: data.lessonId,
  session_id: data.sessionId,
  started_at: data.startedAt,
  // ...
}
```

**classroomSession.ts 中的转换：**
```typescript
// 接收响应时：snake_case -> camelCase
return sessions.map((s: any) => ({
  lessonId: s.lesson_id || s.lessonId,
  teacherId: s.teacher_id || s.teacherId,
  // ...
}))
```

---

## ✅ 统一规范

### 规范选择：统一使用 snake_case

**理由：**
1. ✅ **与后端一致**：后端数据库模型和API响应都使用 `snake_case`
2. ✅ **减少转换**：无需在API层进行字段名转换
3. ✅ **符合Python惯例**：后端使用Python，snake_case是标准
4. ✅ **数据库一致性**：PostgreSQL等数据库使用snake_case
5. ✅ **RESTful API惯例**：大多数REST API使用snake_case

### 命名规范细则

#### 1. TypeScript接口定义

```typescript
// ✅ 正确：使用 snake_case
export interface ActivitySubmission {
  id: number
  cell_id: number
  lesson_id: number
  student_id: number
  session_id?: number
  max_score?: number
  teacher_feedback?: string
  created_at: string
  updated_at: string
}

// ❌ 错误：使用 camelCase
export interface ActivitySubmission {
  cellId: number
  lessonId: number
  studentId: number
  maxScore?: number
  teacherFeedback?: string
  createdAt: string
}
```

#### 2. Vue组件中的使用

```typescript
// ✅ 正确：使用 snake_case
const gradeRecord = ref<GradeRecord>({
  student_id: 123,
  course_id: 456,
  max_score: 100,
  created_at: new Date().toISOString()
})

// 访问字段
console.log(gradeRecord.value.student_id)
console.log(gradeRecord.value.max_score)

// ❌ 错误：使用 camelCase
const gradeRecord = ref<GradeRecord>({
  studentId: 123,  // ❌
  courseId: 456,   // ❌
  maxScore: 100    // ❌
})
```

#### 3. API服务层

```typescript
// ✅ 正确：直接使用 snake_case，无需转换
async createSubmission(
  data: CreateActivitySubmissionRequest
): Promise<ActivitySubmission> {
  // 直接使用，无需转换
  const response = await api.post<ActivitySubmission>(
    '/activities/submissions',
    {
      cell_id: data.cell_id,
      lesson_id: data.lesson_id,
      session_id: data.session_id,
      started_at: data.started_at,
      // ...
    }
  )
  return response  // 响应也是 snake_case，无需转换
}

// ❌ 错误：手动转换
const requestData: any = {
  cell_id: data.cellId,      // ❌ 不需要转换
  lesson_id: data.lessonId,   // ❌ 不需要转换
}
```

#### 4. 函数和变量命名

```typescript
// ✅ 正确：函数名使用 camelCase（JavaScript惯例）
function calculateTotalScore(gradeRecords: GradeRecord[]): number {
  return gradeRecords.reduce((sum, record) => sum + record.score, 0)
}

// ✅ 正确：变量名使用 camelCase（JavaScript惯例）
const gradeRecord = ref<GradeRecord>()
const totalScore = computed(() => calculateTotalScore(records.value))

// ✅ 正确：常量使用 UPPER_SNAKE_CASE
const MAX_SCORE = 100
const DEFAULT_WEIGHT = 0.3
```

#### 5. 命名规范总结

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| TypeScript接口字段 | `snake_case` | `student_id`, `max_score`, `created_at` |
| API请求/响应字段 | `snake_case` | `cell_id`, `lesson_id`, `session_id` |
| Vue组件变量 | `camelCase` | `gradeRecord`, `totalScore` |
| 函数名 | `camelCase` | `calculateTotalScore`, `syncFromActivities` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_SCORE`, `DEFAULT_WEIGHT` |
| 类名/接口名 | `PascalCase` | `GradeRecord`, `ActivitySubmission` |

---

## 📅 迁移计划

### 阶段一：类型定义迁移（优先级：高）

**目标**：统一所有 TypeScript 接口定义使用 `snake_case`

**预计时间**：2-3天

**文件清单**：
1. `frontend/src/types/activity.ts` - 活动相关接口（大量camelCase）
2. `frontend/src/types/classroomSession.ts` - 课堂会话接口
3. 其他类型文件检查（确保一致性）

### 阶段二：API服务层清理（优先级：高）

**目标**：移除所有手动转换逻辑，直接使用 `snake_case`

**预计时间**：1-2天

**文件清单**：
1. `frontend/src/services/activity.ts` - 移除请求转换逻辑
2. `frontend/src/services/classroomSession.ts` - 移除响应转换逻辑
3. 其他服务文件检查

### 阶段三：组件代码迁移（优先级：中）

**目标**：更新所有Vue组件中的字段访问

**预计时间**：3-5天

**文件清单**（基于grep结果，约20个文件）：
1. `frontend/src/components/Activity/ActivityViewer.vue`
2. `frontend/src/components/Activity/Teacher/SubmissionList.vue`
3. `frontend/src/components/Activity/Teacher/UnifiedSubmissionPanel.vue`
4. `frontend/src/components/Cell/ActivityCell.vue`
5. `frontend/src/components/Classroom/TeacherControlPanel.vue`
6. `frontend/src/pages/Student/Dashboard.vue`
7. `frontend/src/pages/Student/Profile.vue`
8. 其他使用camelCase字段的组件...

### 阶段四：测试和验证（优先级：高）

**目标**：确保所有功能正常工作

**预计时间**：2-3天

**任务**：
1. 单元测试
2. 集成测试
3. 手动功能测试
4. 代码审查

---

## 🔧 具体操作步骤

### 步骤1：类型定义迁移

#### 1.1 修改 `activity.ts`

**修改前：**
```typescript
export interface ActivitySubmission {
  id: number
  cellId: number           // ❌ camelCase
  lessonId: number         // ❌ camelCase
  studentId: number        // ❌ camelCase
  maxScore?: number        // ❌ camelCase
  teacherFeedback?: string // ❌ camelCase
  createdAt: string        // ❌ camelCase
  updatedAt: string        // ❌ camelCase
}
```

**修改后：**
```typescript
export interface ActivitySubmission {
  id: number
  cell_id: number           // ✅ snake_case
  lesson_id: number         // ✅ snake_case
  student_id: number        // ✅ snake_case
  max_score?: number        // ✅ snake_case
  teacher_feedback?: string // ✅ snake_case
  created_at: string        // ✅ snake_case
  updated_at: string        // ✅ snake_case
}
```

#### 1.2 批量替换规则

使用VS Code的查找替换功能（支持正则表达式）：

**查找模式：**
```regex
(cellId|lessonId|studentId|sessionId|maxScore|teacherFeedback|createdAt|updatedAt|startedAt|submittedAt|gradedAt|processTrace|activityPhase|attemptNo|timeSpent|isLate|submissionCount|autoGraded|gradedBy)
```

**替换规则表：**
| 查找 | 替换 |
|------|------|
| `cellId` | `cell_id` |
| `lessonId` | `lesson_id` |
| `studentId` | `student_id` |
| `sessionId` | `session_id` |
| `maxScore` | `max_score` |
| `teacherFeedback` | `teacher_feedback` |
| `createdAt` | `created_at` |
| `updatedAt` | `updated_at` |
| `startedAt` | `started_at` |
| `submittedAt` | `submitted_at` |
| `gradedAt` | `graded_at` |
| `processTrace` | `process_trace` |
| `activityPhase` | `activity_phase` |
| `attemptNo` | `attempt_no` |
| `timeSpent` | `time_spent` |
| `isLate` | `is_late` |
| `submissionCount` | `submission_count` |
| `autoGraded` | `auto_graded` |
| `gradedBy` | `graded_by` |

### 步骤2：API服务层清理

#### 2.1 修改 `activity.ts` 服务

**修改前：**
```typescript
async createSubmission(
  data: CreateActivitySubmissionRequest
): Promise<ActivitySubmission> {
  // ❌ 手动转换
  const requestData: any = {
    cell_id: data.cellId,
    lesson_id: data.lessonId,
    session_id: data.sessionId,
    started_at: data.startedAt,
    process_trace: data.processTrace,
    activity_phase: data.activityPhase,
    attempt_no: data.attemptNo,
  }
  
  const response = await api.post<ActivitySubmission>(
    '/activities/submissions',
    requestData
  )
  return response
}
```

**修改后：**
```typescript
async createSubmission(
  data: CreateActivitySubmissionRequest
): Promise<ActivitySubmission> {
  // ✅ 直接使用，无需转换
  const response = await api.post<ActivitySubmission>(
    '/activities/submissions',
    data  // 直接传递，字段名已统一
  )
  return response
}
```

#### 2.2 修改 `classroomSession.ts` 服务

**修改前：**
```typescript
// ❌ 手动转换响应
return sessions.map((s: any) => ({
  lessonId: s.lesson_id || s.lessonId,
  teacherId: s.teacher_id || s.teacherId,
  classroomId: s.classroom_id || s.classroomId,
  // ...
}))
```

**修改后：**
```typescript
// ✅ 直接返回，无需转换
return sessions  // 响应字段名已统一为 snake_case
```

### 步骤3：组件代码迁移

#### 3.1 查找和替换

在Vue组件中，使用查找替换功能：

**查找：** `.cellId` → **替换：** `.cell_id`
**查找：** `.lessonId` → **替换：** `.lesson_id`
**查找：** `.studentId` → **替换：** `.student_id`
**查找：** `.maxScore` → **替换：** `.max_score`
**查找：** `.createdAt` → **替换：** `.created_at`

#### 3.2 模板中的使用

**修改前：**
```vue
<template>
  <div>
    <p>学生ID: {{ submission.studentId }}</p>
    <p>最高分: {{ submission.maxScore }}</p>
    <p>创建时间: {{ submission.createdAt }}</p>
  </div>
</template>
```

**修改后：**
```vue
<template>
  <div>
    <p>学生ID: {{ submission.student_id }}</p>
    <p>最高分: {{ submission.max_score }}</p>
    <p>创建时间: {{ submission.created_at }}</p>
  </div>
</template>
```

---

## 📝 需要修改的文件清单

### 类型定义文件（必须修改）

1. ✅ `frontend/src/types/activity.ts` - **高优先级**
   - 包含大量camelCase字段
   - 影响范围：所有活动相关功能

2. ✅ `frontend/src/types/classroomSession.ts` - **高优先级**
   - 检查是否有camelCase字段

3. ⚠️ `frontend/src/types/lesson.ts` - **检查**
   - 已使用snake_case，确认一致性

4. ⚠️ `frontend/src/types/user.ts` - **检查**
   - 已使用snake_case，确认一致性

5. ⚠️ `frontend/src/types/curriculum.ts` - **检查**
   - 确认是否全部使用snake_case

### API服务文件（必须修改）

1. ✅ `frontend/src/services/activity.ts` - **高优先级**
   - 移除所有手动转换逻辑
   - 约10+处需要修改

2. ✅ `frontend/src/services/classroomSession.ts` - **高优先级**
   - 移除响应转换逻辑
   - 约5+处需要修改

3. ⚠️ 其他服务文件 - **检查**
   - `frontend/src/services/lesson.ts`
   - `frontend/src/services/user.ts`
   - 确认是否有转换逻辑

### Vue组件文件（需要修改）

基于grep结果，以下文件使用了camelCase字段：

1. ✅ `frontend/src/components/Activity/ActivityViewer.vue`
2. ✅ `frontend/src/components/Activity/Teacher/SubmissionList.vue`
3. ✅ `frontend/src/components/Activity/Teacher/UnifiedSubmissionPanel.vue`
4. ✅ `frontend/src/components/Activity/Teacher/ActivityStatistics.vue`
5. ✅ `frontend/src/components/Activity/SubmissionStatistics.vue`
6. ✅ `frontend/src/components/Activity/PeerReview/PeerReviewTask.vue`
7. ✅ `frontend/src/components/Activity/PeerReview/PeerReviewResults.vue`
8. ✅ `frontend/src/components/Activity/PeerReview/PeerReviewAssign.vue`
9. ✅ `frontend/src/components/Cell/ActivityCell.vue`
10. ✅ `frontend/src/components/Cell/CellContainer.vue`
11. ✅ `frontend/src/components/Cell/FlowchartStudentCell.vue`
12. ✅ `frontend/src/components/Classroom/TeacherControlPanel.vue`
13. ✅ `frontend/src/components/Student/StudentAiAssistantPanel.vue`
14. ✅ `frontend/src/components/Resource/ReviewSection.vue`
15. ✅ `frontend/src/pages/Student/Dashboard.vue`
16. ✅ `frontend/src/pages/Student/Profile.vue`
17. ✅ `frontend/src/pages/Teacher/Questions.vue`
18. ✅ `frontend/src/composables/useClassroomSession.ts`

### 其他文件（检查）

1. ⚠️ `frontend/src/composables/*.ts` - 检查所有composables
2. ⚠️ `frontend/src/utils/*.ts` - 检查工具函数
3. ⚠️ `frontend/src/stores/*.ts` - 检查Pinia stores

---

## ⚠️ 注意事项

### 1. 向后兼容性

**问题**：如果后端API同时支持两种命名，需要确认后端是否已统一。

**解决方案**：
- 确认后端API响应统一使用 `snake_case`
- 如果后端还在返回 `camelCase`，需要先更新后端

### 2. 渐进式迁移

**建议**：不要一次性修改所有文件，按模块逐步迁移：

1. **先迁移类型定义** - 确保类型系统正确
2. **再迁移API服务** - 确保数据流正确
3. **最后迁移组件** - 确保UI正常显示

### 3. 测试覆盖

**重要**：每个阶段完成后都要进行测试：

- ✅ 类型检查（TypeScript编译）
- ✅ 单元测试
- ✅ 集成测试
- ✅ 手动功能测试

### 4. Git提交策略

**建议**：按阶段提交，便于回滚：

```bash
# 阶段一：类型定义
git commit -m "refactor: 统一类型定义使用snake_case"

# 阶段二：API服务
git commit -m "refactor: 移除API服务层手动转换逻辑"

# 阶段三：组件迁移
git commit -m "refactor: 更新组件使用snake_case字段"
```

### 5. 代码审查要点

审查时重点关注：

1. ✅ 是否所有接口定义都使用 `snake_case`
2. ✅ 是否移除了所有手动转换逻辑
3. ✅ 组件中字段访问是否正确更新
4. ✅ 是否有遗漏的字段未更新
5. ✅ 类型检查是否通过

### 6. 常见错误

**错误1：** 忘记更新模板中的字段访问
```vue
<!-- ❌ 错误 -->
<p>{{ submission.studentId }}</p>

<!-- ✅ 正确 -->
<p>{{ submission.student_id }}</p>
```

**错误2：** 在计算属性中使用旧字段名
```typescript
// ❌ 错误
const total = computed(() => records.value.reduce((sum, r) => sum + r.maxScore, 0))

// ✅ 正确
const total = computed(() => records.value.reduce((sum, r) => sum + r.max_score, 0))
```

**错误3：** 在解构时使用旧字段名
```typescript
// ❌ 错误
const { studentId, maxScore } = submission.value

// ✅ 正确
const { student_id, max_score } = submission.value
```

---

## ✅ 验证检查清单

### 类型定义检查

- [ ] 所有 `frontend/src/types/*.ts` 文件中的接口字段都使用 `snake_case`
- [ ] TypeScript编译无错误
- [ ] 没有类型警告

### API服务检查

- [ ] 所有 `frontend/src/services/*.ts` 文件中没有手动转换逻辑
- [ ] 请求数据直接使用接口定义，无需转换
- [ ] 响应数据直接使用，无需转换

### 组件检查

- [ ] 所有Vue组件中的字段访问都使用 `snake_case`
- [ ] 模板中的字段访问正确
- [ ] 脚本中的字段访问正确
- [ ] 计算属性中的字段访问正确

### 功能测试

- [ ] 活动提交功能正常
- [ ] 成绩查看功能正常
- [ ] 课堂会话功能正常
- [ ] 数据列表显示正常
- [ ] 表单提交正常

### 代码质量

- [ ] ESLint检查通过
- [ ] Prettier格式化通过
- [ ] 没有console.log调试代码
- [ ] 代码审查通过

---

## 🛠️ 迁移工具和脚本

### VS Code查找替换

使用VS Code的批量查找替换功能：

1. 打开查找替换（`Cmd+Shift+H` / `Ctrl+Shift+H`）
2. 启用正则表达式模式（`.*` 按钮）
3. 使用上面的替换规则表

### 自动化脚本（可选）

可以编写Node.js脚本自动替换：

```javascript
// scripts/migrate-naming.js
const fs = require('fs')
const path = require('path')

const replacements = {
  'cellId': 'cell_id',
  'lessonId': 'lesson_id',
  'studentId': 'student_id',
  // ... 更多替换规则
}

function migrateFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8')
  
  for (const [old, new_] of Object.entries(replacements)) {
    const regex = new RegExp(old, 'g')
    content = content.replace(regex, new_)
  }
  
  fs.writeFileSync(filePath, content, 'utf8')
  console.log(`✅ Migrated: ${filePath}`)
}

// 遍历文件并迁移
// ...
```

### ESLint规则（未来）

可以添加ESLint规则防止使用camelCase字段：

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    // 自定义规则：禁止在接口字段中使用camelCase
    'no-camelcase-in-interface': 'error'
  }
}
```

---

## 📊 迁移进度跟踪

### 阶段一：类型定义（0%）

- [ ] `activity.ts`
- [ ] `classroomSession.ts`
- [ ] 其他类型文件检查

### 阶段二：API服务（0%）

- [ ] `activity.ts`
- [ ] `classroomSession.ts`
- [ ] 其他服务文件检查

### 阶段三：组件迁移（0%）

- [ ] Activity相关组件（8个文件）
- [ ] Cell相关组件（3个文件）
- [ ] 页面组件（3个文件）
- [ ] 其他组件（4个文件）

### 阶段四：测试验证（0%）

- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试
- [ ] 代码审查

---

## 🎯 预期收益

完成迁移后，将获得：

1. ✅ **代码一致性**：前后端命名完全一致
2. ✅ **减少错误**：无需手动转换，减少出错可能
3. ✅ **提高效率**：开发时无需考虑命名转换
4. ✅ **类型安全**：TypeScript类型检查更准确
5. ✅ **易于维护**：新开发者无需学习转换规则
6. ✅ **减少代码量**：移除所有转换逻辑

---

## 📚 参考资料

- [Python PEP 8 - 命名规范](https://pep8.org/#naming-conventions)
- [TypeScript 命名规范](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [RESTful API 设计最佳实践](https://restfulapi.net/resource-naming/)

---

## 📝 更新日志

- **2025-01-XX**：创建迁移方案文档
- **待更新**：记录实际迁移进度和遇到的问题