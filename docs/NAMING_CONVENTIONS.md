# InspireEd 命名规范

> **状态**：已采纳（Adopted）  
> **版本**：1.0  
> **日期**：2026-07-18  
> **适用范围**：前端（Vue/TS）、后端（Python/FastAPI）、数据库（PostgreSQL）、HTTP API  
> **相关文档**：[前端命名迁移方案](./design/FRONTEND_NAMING_CONVENTION_MIGRATION.md) · [新项目命名脚手架](./templates/naming-scaffold/README.md)

---

## 1. 总原则

1. **数据字段一贯**：库表列名 → 后端模型/Schema → API JSON → 前端类型/DTO，默认全部使用 `snake_case`。
2. **语言本地惯例**：各层「非数据字段」的标识符，遵循该语言社区惯例（见下表）。
3. **新代码必须合规**：新增接口、表、类型一律按本规范；存量混用允许暂时存在，按迁移清单逐步收口。
4. **禁止双风格并存于同一边界**：同一 API、同一 TypeScript 接口、同一表内，字段风格必须一致。
5. **不做无必要转换**：不要在服务层手写零散的 `camelCase ↔ snake_case` 映射；若确需兼容，集中在适配层并标注废弃期限。

### 1.1 分层速查

| 层 | 数据字段 / JSON 键 | 本地变量与函数 | 类型 / 类 / 组件 | 文件名 |
|----|-------------------|----------------|------------------|--------|
| 数据库 | `snake_case` | — | — | 迁移文件见 §4 |
| 后端 Python | `snake_case` | `snake_case` | `PascalCase` | `snake_case.py` |
| HTTP API | `snake_case` | — | — | URL 见 §3.4 |
| 前端 TypeScript | 接口字段 `snake_case` | `camelCase` | `PascalCase` | `camelCase.ts` / `PascalCase.vue` |

### 1.2 冻结（新代码硬约束）

自 1.0 起，新增与增量改动必须遵守：

1. 新 API / Schema / 前端 DTO 字段禁止使用 camelCase（一律 `snake_case`）。
2. 禁止新增将响应当成 camelCase 的 `serialization_alias`（或同等别名）。
3. 禁止扩大 `lesson_id || lessonId` 这类双读兼容，禁止新增零散字段映射；遗留转换须集中并标注拆除条件。

---

## 2. 后端（Python / FastAPI）

### 2.1 标识符

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 / 文件 | `snake_case` | `classroom_session.py` |
| 包目录 | `snake_case` | `app/services/` |
| 类 / Pydantic Model | `PascalCase` | `ClassSession`, `ActivitySubmissionCreate` |
| 函数 / 方法 / 变量 | `snake_case` | `get_active_sessions`, `student_id` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Enum 成员名 | `UPPER_SNAKE_CASE` | `DISTRICT_ADMIN` |
| Enum 存储值（新） | `snake_case` 小写字符串 | `"district_admin"` |

> **存量例外**：部分会话状态等 Enum 值为全大写（如 `"PREPARING"`）。新 Enum 一律用小写 `snake_case`；旧值勿擅自改库，需迁移脚本时再统一。

### 2.2 SQLAlchemy 模型

- 类名：`PascalCase` 单数实体名，如 `ClassSession`。
- `__tablename__`：`snake_case` **复数**，如 `class_sessions`、`users`。
- 列名：`snake_case`，如 `teacher_id`、`created_at`。
- 外键列：`{referenced_table_singular}_id`，如 `lesson_id` → `lessons.id`。
- 布尔列：`is_` / `has_` 前缀，如 `is_active`、`has_guest_access`。
- 时间列：`*_at`（时刻）、`*_date`（日期）、`duration_*`（时长）。

### 2.3 Pydantic Schema

- 请求/响应模型字段与数据库、API 一致，使用 `snake_case`。
- **默认禁止**为字段添加 `serialization_alias` 把响应当成 camelCase。
- 存量个别别名（如 `studentEmail`）视为技术债：新接口不得新增；修复时改回 `snake_case` 并同步前端。

```python
# ✅
class ActivitySubmissionResponse(BaseModel):
    student_id: int
    created_at: datetime

# ❌ 新代码不要再引入
student_name: str = Field(..., serialization_alias="studentName")
```

### 2.4 路由与依赖

- 路径参数、查询参数名：`snake_case`（与 OpenAPI 一致）。
- 路由函数名：`snake_case` 动词短语，如 `list_class_sessions`。

---

## 3. HTTP API

### 3.1 JSON 字段

- 请求体、响应体字段名：**一律 `snake_case`**。
- 与后端 Schema、前端 `types/*` 对齐，避免前端再做字段重命名。

### 3.2 成功 / 错误结构

沿用项目既有响应包装；其中业务对象内部字段仍遵守 `snake_case`。勿在错误详情里混用 camelCase。

### 3.3 WebSocket / 实时消息

- 事件名：`snake_case` 或已有点分层风格保持模块内一致（如 `session.cell_changed`）；**同一频道内不得混用**。
- payload 字段：`snake_case`。

### 3.4 URL

| 元素 | 规范 | 示例 |
|------|------|------|
| 路径段 | 小写，多词用连字符或与现有资源复数名一致 | `/api/v1/class-sessions` 或既有 `/class_sessions` |
| 路径参数 | 花括号 + `snake_case` | `/{session_id}` |
| 查询参数 | `snake_case` | `?teacher_id=1&is_active=true` |

> **存量**：若线上已有 camelCase 查询参数或路径，新端点不要模仿；变更旧端点需兼容期。

**推荐**：新路由优先与现有主风格保持一致（资源名复数 + `snake_case` 参数），不要为「更 REST」而引入第三种风格。

---

## 4. 数据库（PostgreSQL）

### 4.1 表与列

| 对象 | 规范 | 示例 |
|------|------|------|
| 表名 | `snake_case` 复数 | `class_sessions`, `exam_subjects` |
| 列名 | `snake_case` | `student_id`, `ended_at` |
| 主键 | 优先 `id` | `id` |
| 外键列 | `{entity}_id` | `classroom_id` |
| 关联表 | 两表名排序或语义名 | `exam_number_mappings` |

### 4.2 约束与索引命名

| 类型 | 推荐前缀 | 格式 | 示例 |
|------|----------|------|------|
| 普通索引 | `ix_` 或 `idx_` | `{prefix}_{table}_{column(s)}` | `ix_class_sessions_teacher_id` |
| 唯一约束 | `uq_` | `uq_{table}_{column(s)}` | `uq_exam_subject` |
| 主键 | `pk_` | `pk_{table}` | `pk_users` |
| 外键 | `fk_` | `fk_{table}_{column}` | `fk_scores_exam_id` |
| Check | `ck_` | `ck_{table}_{rule}` | `ck_users_role` |

**约定**：

- 新迁移优先使用 Alembic `op.f("ix_...")` 生成的 `ix_` 形式，与学习指南一致。
- 存量 `idx_` 索引可保留，不必仅为改名而迁移。
- 同一仓库内新建索引不要再发明第四种前缀。

### 4.3 枚举类型（DB）

- PostgreSQL 枚举类型名：`snake_case`，如 `user_role`、`class_session_status`。
- 枚举标签：与后端 Enum **存储值**一致（新值为小写 `snake_case`）。

### 4.4 迁移文件

- 文件名：Alembic revision 惯例 + 简短 `snake_case` 说明，如 `002_add_guest_access_to_sessions.py`。
- 说明文字可用中文，但标识符（表/列/索引名）必须英文 `snake_case`。

---

## 5. 前端（Vue 3 / TypeScript）

### 5.1 数据字段 vs 本地标识符（关键）

```typescript
// ✅ 接口 / API DTO：snake_case（与后端一致）
export interface ClassSession {
  id: number
  lesson_id: number
  teacher_id: number
  current_cell_id?: number
  created_at: string
}

// ✅ 本地变量、函数：camelCase
const currentSession = ref<ClassSession>()
function loadSessionById(sessionId: number) { /* ... */ }

// ✅ 读取的是 snake_case 字段
console.log(currentSession.value?.lesson_id)
```

| 类型 | 规范 | 示例 |
|------|------|------|
| `types/*` 接口字段 | `snake_case` | `cell_id`, `max_score` |
| API 请求/响应类型 | `snake_case` | 同后端 |
| 组件内局部变量 / ref | `camelCase` | `gradeRecord`, `isLoading` |
| 函数 / composable | `camelCase`；composable 以 `use` 开头 | `useClassroomSession` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_SCORE` |
| 类型名 / 接口名 / 枚举类型名 | `PascalCase` | `ActivitySubmission` |
| 组件名（SFC） | `PascalCase` | `SubmissionList.vue` |
| 工具模块文件 | `camelCase.ts` 或与目录惯例一致 | `fieldConverter.ts` |
| props / emit 名（模板） | 模板里 kebab-case，脚本里 camelCase | `:lesson-id` ↔ `lessonId` |
| **props 若承载 API 实体字段** | 优先与 DTO 相同 `snake_case`，或显式映射一层 | 见 §5.3 |

### 5.2 与后端对齐的模块

以下方向为**目标态**，新代码必须遵守：

- `frontend/src/types/**`
- `frontend/src/services/**` 的请求体 / 响应类型

参考已对齐示例：`frontend/src/types/student_project.ts`（文件头注明 snake_case）。

### 5.3 禁止事项

- ❌ 在业务组件里散落 `lessonId: res.lesson_id` 式临时映射（应在类型层一次对齐，或集中适配）。
- ❌ 新增 API 类型使用 camelCase「指望后端以后改」。
- ❌ 扩大 `serialization_alias` / 双字段兼容（`lesson_id || lessonId`）的使用范围；兼容代码必须带注释与拆除条件。

### 5.4 转换工具

- `frontend/src/utils/fieldConverter.ts` 仅用于**遗留边界**的临时兼容。
- 目标态下，主路径服务不应依赖全局 camelCase 转换。
- 工具文件头注释若与本规范冲突，以**本规范**为准，后续应修订该注释。

### 5.5 CSS / 静态资源

- CSS 类名：沿用现有（建议 BEM 或项目已有工具类），小写 + 连字符。
- 不要用 CSS 类名表达业务字段语义去「对齐」API。

---

## 6. 跨层字段对照（权威示例）

| 含义 | DB 列 | Python | API JSON | TS 接口字段 | TS 局部变量 |
|------|-------|--------|----------|-------------|-------------|
| 教案 ID | `lesson_id` | `lesson_id` | `lesson_id` | `lesson_id` | `lessonId` |
| 学生 ID | `student_id` | `student_id` | `student_id` | `student_id` | `studentId` |
| 创建时间 | `created_at` | `created_at` | `created_at` | `created_at` | `createdAt` |
| 是否启用 | `is_active` | `is_active` | `is_active` | `is_active` | `isActive` |

---

## 7. 枚举与业务常量

| 场景 | 规范 | 示例 |
|------|------|------|
| 角色、状态等持久化值（新） | 小写 `snake_case` | `school_admin`, `in_progress` |
| 前端联合类型字面量（新） | 与后端存储值**完全一致** | `type Status = 'draft' \| 'submitted'` |
| 仅 UI 展示的文案 | 中文或 i18n key，不代替枚举值 | — |

**存量例外（勿在新代码扩散）**：

- 部分前端活动题型使用 kebab-case（如 `'single-choice'`）。
- 部分会话状态使用全大写（如 `'PREPARING'`）。

新模块若无新枚举，优先小写 `snake_case`；若必须对接旧值，在类型文件顶部用注释标明「legacy wire value」。

---

## 8. 环境变量与配置键

| 类型 | 规范 | 示例 |
|------|------|------|
| 环境变量 | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `CORS_ORIGINS` |
| Python settings 字段 | `snake_case`（与 pydantic-settings 一致） | `database_url` |
| 前端 `import.meta.env` | Vite 前缀 + `UPPER_SNAKE_CASE` | `VITE_API_BASE_URL` |

---

## 9. 存量债务与迁移策略

### 9.1 已知不一致

1. 前端部分 `types` / 组件使用 camelCase（如活动相关类型），与 `student_project` 等 snake_case 模块并存。
2. 服务层存在手动字段映射与 `fieldConverter` 使用点。
3. 后端极少数 Schema 使用 camelCase `serialization_alias`。
4. 索引前缀 `ix_` / `idx_` 混用。
5. Enum 存储值大小写风格不统一。

### 9.2 执行顺序

1. **冻结（已生效）**：见 §1.2；新 PR 不得引入 camelCase API/DTO 字段或新的 camelCase serialization alias。
2. **类型先行**：按 [FRONTEND_NAMING_CONVENTION_MIGRATION.md](./design/FRONTEND_NAMING_CONVENTION_MIGRATION.md) 将 `types` → `services` → 组件字段访问改为 snake_case。
3. **拆除转换**：映射逻辑删除或收拢到单一兼容层。
4. **后端清理**：去掉 camelCase alias，保证 JSON 为 snake_case。
5. **不做纯重命名 DB 迁移**，除非改名能消除真实缺陷；索引前缀不强制回溯。

### 9.3 PR 检查清单（增量）

- [ ] 新表/列/索引命名符合 §4  
- [ ] 新 Schema / API 字段为 `snake_case`，无 camelCase alias  
- [ ] 新前端类型字段与 API 一致（`snake_case`）  
- [ ] 组件局部变量仍为 `camelCase`，未把 API 字段改成「半套 camelCase」  
- [ ] 未新增散落的字段转换；若有兼容，已注明拆除条件  

---

## 10. 决策记录（简要）

| 决策 | 选择 | 理由 |
|------|------|------|
| API 字段风格 | `snake_case` | 与 Python/PostgreSQL 一致，减少双端转换；与既有迁移方案一致 |
| 前端局部变量 | `camelCase` | 符合 JS/TS 惯例，避免与「数据字段 snake_case」混淆 |
| 表名 | 复数 `snake_case` | 与现有模型一致 |
| 新 Enum 值 | 小写 `snake_case` | 与 `UserRole` 等主流一致；全大写视为遗留 |

---

## 11. 如何生效

1. 本文件为项目级命名规范的**单一事实来源**（已采纳 1.0）。
2. 与代码冲突时：新代码按本文件与 §1.2 冻结条款；旧代码按 §9 分批迁移，不在无关 PR 中大规模改革。
3. 根 `README.md`「开发规范」与 `.cursor/rules/naming-conventions.mdc` 指向本文件，作为人工与 AI 的执行入口。
4. **新项目**：复制 [templates/naming-scaffold](./templates/naming-scaffold/README.md)，不要带上本文件的存量债务章节。
5. 修订需更新版本号与日期，并在 PR 中说明变更动机。

---

## 附录 A. 快速反例

```typescript
// ❌ 同一接口混用
interface Session {
  lessonId: number
  teacher_id: number
}

// ❌ 服务层逐字段手工掰弯（新代码）
return {
  lessonId: raw.lesson_id,
  teacherId: raw.teacher_id,
}
```

```python
# ❌ 新响应用 camelCase 别名
class Foo(BaseModel):
    student_id: int = Field(serialization_alias="studentId")
```

```sql
-- ❌ 新表使用 PascalCase / 驼峰列
CREATE TABLE ClassSessions (teacherId INT);
```
