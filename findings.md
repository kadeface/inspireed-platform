# Findings: 学生端不随教师端模块切换而更新

## 问题描述
教师端开始上课并切换模块后，学生端界面不自动跟随切换，必须手动刷新页面才更新。

## 根本原因（Root Cause）

**网络配置错误**：教师端和学生端使用不同的地址访问系统，导致 WebSocket 连接失败。

### 问题场景：
- 教师端使用：`http://localhost:5173` → WebSocket 连接到 `ws://localhost:8000` ✓
- 学生端使用：`http://192.168.1.102:5173` → WebSocket 连接到 `ws://192.168.1.102:8000` ✗
- 后端运行在教师机器上，学生机器的 192.168.1.102:8000 没有服务运行
- 结果：学生端无法建立 WebSocket 连接，`broadcast_to_session` 找不到学生连接

### 解决方案：
**所有用户（教师和学生）必须使用相同的服务器地址访问系统：**

**选项 1：全部使用 IP 地址（局域网环境推荐）**
```
教师端：http://192.168.1.102:5173
学生端：http://192.168.1.102:5173
```

**选项 2：全部使用域名（生产环境推荐）**
```
教师端：http://inspireed.local:5173
学生端：http://inspireed.local:5173
```

**选项 3：全部使用 localhost（仅单机测试）**
```
教师端：http://localhost:5173
学生端：http://localhost:5173（同一机器不同浏览器）
```

## 链路梳理

### 教师端
- 切换模块：`ModuleList` / 上一页/下一页 → `useNavigation.handleModuleItemClick` / `handlePrevModule` / `handleNextModule` → `handleControlBoardNavigate` → `classroomSessionService.navigateToCell(sessionId, { displayCellOrders })` → HTTP POST `/api/v1/classroom-sessions/sessions/{id}/navigate`。
- 后端 `navigate_to_cell` 会更新 `session.settings["display_cell_orders"]` 和 `session.current_cell_id`，并调用 `manager.broadcast_to_session(message, session_id)`，消息类型为 `cell_changed`，payload 含 `display_cell_orders`、`current_cell_id`。

### 后端
- `broadcast_to_session(session_id)` 向 `active_connections[session_id]` 内所有学生 WebSocket 发送该消息。
- 学生只有在已连接 `/sessions/{session_id}/ws` 并成功 `manager.connect()` 后才会出现在 `active_connections` 中。

### 学生端
- `LessonView` 使用 `useClassroomSession(lessonId)`，得到 `session`（即 `classroomSession`）。
- 加入流程：`findAndJoinSession()` → 加入后延迟 500ms → `connectWebSocket(sessionId)` → 先 `setupWebSocketListeners()` 再 `websocketService.connect()`。
- `setupWebSocketListeners()` 注册 `cell_changed`：收到后 `session.value = newSession`（含新 `settings.display_cell_orders`），`currentCellId.value = message.data.current_cell_id`。
- `filteredCells` 依赖 `classroomSession.value?.settings?.display_cell_orders`，理论上 `session` 更新后应重新计算并驱动视图。

## 可能原因归纳

1. **WebSocket 未连接或已断开**
   - 学生未打开本课页、连接失败或中途断开，则收不到 `cell_changed`；若未降级到轮询或轮询未拉取 `display_cell_orders`，则只能通过刷新拿到最新状态。

2. **连接/监听时序**
   - 监听器在 `connectWebSocket` 内、在 `connect()` 之前注册，理论上不会漏首条消息；若存在重复进入教室或重复调用 `findAndJoinSession` 的路径，需确认不会重复注册或清空监听器导致漏消息。

3. **后端未把该学生加入广播列表**
   - 仅当学生已成功连接 `/sessions/{session_id}/ws` 且 `manager.connect()` 完成时才会在 `active_connections[session_id]` 中；若学生用错 `session_id` 或连接未完成就收到教师切换，则不会收到广播。

4. **页面不可见时未再同步**
   - 若浏览器后台/切页时 WebSocket 断连或漏消息，再切回页面时若没有用 API 拉一次最新会话，界面会一直停留在旧状态直到用户手动刷新。

## 技术结论
- 教师端会正确调用 navigate API 并触发后端广播。
- 后端会向该 session 下所有已注册学生发送 `cell_changed`。
- 学生端有 `cell_changed` 监听且会更新 `session` 与 `currentCellId`，依赖的 `filteredCells` 会随 `classroomSession` 变化而更新。
- 最可能的问题是：**学生未通过 WebSocket 收到 `cell_changed`**（未连接、断连、或未在 `active_connections` 中），且**没有其它机制在未收到时或页面重新可见时拉取最新会话**。

## 建议修复

### ✅ 已修复：网络配置问题

**问题：** 教师端使用 `localhost`，学生端使用 `192.168.1.102`，导致 WebSocket 连接失败。

**解决方案：**
1. 确保所有用户（教师和学生）使用相同的服务器地址访问系统
2. 局域网环境推荐使用服务器的 IP 地址（如 `http://192.168.1.102:5173`）
3. 生产环境推荐使用域名（如 `http://inspireed.example.com`）

**详细配置指南：** 参见 `NETWORK_CONFIGURATION.md`

### 2. 可选增强：页面可见时刷新会话（已实现）

在课堂模式下，监听 `document.visibilitychange`，当页面从隐藏变为可见时调用 `refreshSession()`，用 API 拉取最新 `display_cell_orders` 等，避免因 WebSocket 临时断开导致必须手动刷新。

**实现位置：** `frontend/src/composables/useClassroomSession.ts:onVisibilityChange()`
