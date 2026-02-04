# Task Plan: 学生端不随教师端模块切换而更新

## Goal
查明教师端开始上课并切换模块后，学生端不自动跟随切换、必须手动刷新才更新的原因，并定位修复点。

## Current Phase
Phase 4: 验证

## Phases

### Phase 1: Requirements & Discovery
- [x] 理解问题：教师切换模块 → 学生端应自动切到同一模块，目前不生效
- [x] 梳理教师端：切换模块时是否调用 API / 发 WebSocket
- [x] 梳理后端：是否广播 current_cell_id / 导航消息
- [x] 梳理学生端：是否订阅并处理该广播、是否用 currentCellId 驱动视图
- **Status:** complete

### Phase 2: 根因定位
- [x] 确定断点：教师未发 / 后端未广播 / 学生未收 / 学生收但未更新 UI
- [x] 记录到 findings.md
- **Status:** complete

### Phase 3: 修复实现
- [x] 按根因修改代码：学生端页面可见时刷新会话（避免 WebSocket 漏消息）
- [x] 保证教师切换模块后学生端能通过 WebSocket 或可见时刷新得到最新状态
- **Status:** complete

### Phase 4: 验证
- [ ] 本地或联调验证：教师切换 → 学生跟随；切 tab 再回来 → 学生端自动对齐
- **Status:** in_progress

## Key Questions
1. 教师点击模块/上一页/下一页时，是否调用了 navigate_to_cell 或等效 API？**是**：`handleControlBoardNavigate` → `navigateToCell` → POST `/navigate`。
2. 后端 broadcast_to_session 的消息格式是什么？学生端 WebSocket 期望的 type 与 payload 是什么？**type: `cell_changed`，data: display_cell_orders, current_cell_id**；学生端已监听 `cell_changed` 并更新 session 与 currentCellId。
3. 学生 LessonView 的 currentCellId 来源是 session 拉取还是 WebSocket？是否在收到广播时更新？**两者都有**：加入时从 API 拉取，之后由 WebSocket `cell_changed` 更新；filteredCells 依赖 `classroomSession.settings.display_cell_orders`。

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 页面可见时刷新会话 | 若 WebSocket 漏收 cell_changed（断连/未连接），切回标签页时通过 API 拉取最新 display_cell_orders，避免必须手动刷新 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|  | 1       |            |

## Notes
- 已从 grep 得知：useClassroomSession 有 currentCellId，会在 message.data.current_cell_id 时更新；后端 navigate_to_cell 会 broadcast_to_session；需确认教师端是否触发 navigate、学生端是否正确监听并驱动 UI。
