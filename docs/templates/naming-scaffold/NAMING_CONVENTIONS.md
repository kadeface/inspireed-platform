# 命名规范（新项目模板）

> **状态**：模板 — 复制到新项目后改为「已采纳」并填版本/日期  
> **适用范围**：前端（TS/Vue 等）、后端（Python/FastAPI）、数据库（PostgreSQL）、HTTP API

---

## 1. 总原则

1. **数据字段一贯**：库表列 → 后端模型/Schema → API JSON → 前端 DTO/接口字段，一律 `snake_case`。
2. **语言本地惯例**：非数据字段的标识符跟语言社区走（见下表）。
3. **禁止双风格**：同一 API、同一 TS 接口、同一表内字段风格必须一致。
4. **禁止无必要转换**：不要在服务层散落 `camelCase ↔ snake_case` 映射。
5. **决策表优先**：作者字段、布尔、枚举、索引等，查 [`DECISION_DEFAULTS.md`](./DECISION_DEFAULTS.md)，禁止现场发明同义词。

### 1.1 分层速查

| 层 | 数据字段 / JSON 键 | 本地变量与函数 | 类型 / 类 / 组件 |
|----|-------------------|----------------|------------------|
| 数据库 | `snake_case`；表名复数 | — | — |
| 后端 Python | `snake_case` | `snake_case` | `PascalCase` |
| HTTP API | `snake_case` | — | — |
| 前端 TypeScript | 接口字段 `snake_case` | `camelCase` | `PascalCase` |

常量：`UPPER_SNAKE_CASE`。

### 1.2 冻结（新代码硬约束）

1. 禁止 camelCase 的 API / Schema / 前端 DTO 字段。
2. 禁止 `serialization_alias`（或同等）把 JSON 输出成 camelCase。
3. 禁止 `lesson_id || lessonId` 双读；禁止散落 mapper。临时适配必须集中且标注拆除条件。

---

## 2. 后端

- 文件/函数/变量：`snake_case`；类与 Pydantic 模型：`PascalCase`。
- Enum **成员名**：`UPPER_SNAKE_CASE`；**存库值**：小写 `snake_case`（如 `"in_progress"`）。
- 外键列：`{entity}_id`；布尔：`is_` / `has_` / `*_enabled`；时间：`*_at` / `*_date`。

---

## 3. HTTP API

- 请求/响应 JSON 键：`snake_case`。
- 查询参数、路径参数：`snake_case`。
- WebSocket payload 字段：`snake_case`。

---

## 4. 数据库

| 对象 | 规范 | 示例 |
|------|------|------|
| 表名 | 复数 `snake_case` | `class_sessions` |
| 列名 | `snake_case` | `teacher_id` |
| 普通索引 | `ix_{table}_{columns}` | `ix_class_sessions_teacher_id` |
| 唯一约束 | `uq_{table}_{columns}` | `uq_exam_subject` |
| 外键约束 | `fk_{table}_{column}` | `fk_scores_exam_id` |
| 主键 | `pk_{table}` | `pk_users` |
| PG 枚举类型名 | `snake_case`（带下划线） | `class_session_status` |
| 枚举标签 | 与后端存库值一致 | `preparing` |

---

## 5. 前端

```typescript
// DTO / API：snake_case
interface ClassSession {
  lesson_id: number
  created_at: string
}

// 本地标识符：camelCase
const currentSession = ref<ClassSession>()
function loadSessionById(sessionId: number) { /* ... */ }
console.log(currentSession.value?.lesson_id)
```

- `types/**`、`services/**` 的请求/响应类型字段必须 `snake_case`。
- 组件名：`PascalCase.vue`；composable：`useXxx`。

---

## 6. PR 检查清单

- [ ] 新表/列/索引符合 §4 与决策表  
- [ ] 新 Schema / API 字段为 `snake_case`，无 camelCase alias  
- [ ] 新前端类型字段与 API 一致  
- [ ] 局部变量仍为 `camelCase`  
- [ ] 未新增双读或散落转换  

---

## 7. 生效

本文件为项目命名单一事实来源。与代码冲突时：新代码按本文件；无关 PR 不做大规模重命名。
