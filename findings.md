# Findings: 教师端教案加载慢

## 场景区分
- **工作台教案列表**（`/teacher` Dashboard）：进入后加载「我的教案」列表 + PDCA 区统计。
- **教案编辑页**（`LessonEditor`）：打开单篇教案，拉取完整 `content` JSON。

## 主要成因（代码级）

### 1. 首屏并发多路 `/lessons/` + 先阻塞拉用户信息
`Dashboard.vue` 的 `onMounted` 会先 `await authService.getCurrentUser()`，再同时触发：
- `loadLessons()` → 一页列表（默认 `page_size` 20）
- `refreshPdcaOverview()` → 内含 `loadLessonStatusStats()`，对 **草稿 / 已发布 / 已归档** 各发 **1 次** `fetchLessons`（`page_size: 1`）

因此首屏至少 **4 次** 教案列表类请求与其它统计请求并行，数据库与连接池压力大时体感明显变慢。

### 2. 列表接口在 DB 层仍可能读出整份 `content`
`Lesson.content` 为 JSON 列，模型未做 `deferred`；`list_lessons` 使用 `select(Lesson)` 会按行加载全部列（含大 JSON）。  
API 虽用 `include_content=False` 不把正文返回给前端（见 `lessons.py` 注释），但 **IO/反序列化开销仍在**。

### 3. 每条列表记录仍做较重序列化与关联加载
列表查询 `options` 包含 `course→subject/grade`、`creator`、`lesson_classrooms→classroom` 等 `selectinload`。  
`_lesson_to_response` 还会从 `lesson.__dict__` 组装字段；若 `cell_count` 为 0，仍会 **遍历 `lesson.content`** 计算 cell 数。

### 4. 列表 COUNT 查询成本高
教师在「共享」语义下使用 `or_(本人, 已发布)` 等条件，COUNT 通过 `distinct` 子查询实现；数据量大时每次列表（含那 3 次「只取 1 条」的统计请求）都要跑一遍计数。

### 5. 前端禁用 GET 缓存
`api.get` 统一加 `Cache-Control: no-cache`（教案数据），避免脏读但 **无法利用浏览器缓存**，重复进入页面都会全量重拉。

### 6. 编辑单篇教案时
`GET /lessons/{id}` 返回完整 content，且会做 `_convert_content_urls`（递归 + 正则处理 HTML），教案越大 CPU 与响应时间越长；若还有 `getReferenceResource` 等串行请求，首屏会更慢。

## 建议验证方式（非改代码）
- 浏览器 Network：登录进工作台，数 `/api/v1/lessons/` 并发次数与各自 TTFB/体积。
- 后端日志/SQL：对 `list_lessons` 的 COUNT 与主查询做 `EXPLAIN ANALYZE`（或等价分析）。
