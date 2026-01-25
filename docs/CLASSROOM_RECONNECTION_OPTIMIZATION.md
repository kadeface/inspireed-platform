# 教室重连优化方案

## 问题描述

1. **教师开始上课后，学生无法进入教室**：学生可能在教师开始上课后才尝试加入，或者之前加入过但异常退出
2. **学生异常退出后无法重新进入**：学生端异常退出（网络断开、浏览器崩溃等）后，无法重新加入正在进行的课堂会话

## 优化方案

### 1. 后端优化 (`backend/app/api/v1/classroom_sessions.py`)

#### 改进 `join_session` API
- **问题**：学生异常退出后，数据库中的 `is_active` 可能还是 `True`，但实际已经离线。重新加入时，活跃学生数统计不准确
- **优化**：
  - 检测学生是否之前是离线状态（`is_active = False`），如果是，重新加入时更新活跃学生数
  - 确保在 `ACTIVE` 和 `PENDING` 状态下都可以重新加入会话
  - 自动同步当前会话的 `current_cell_id` 到学生参与记录

```python
# 如果之前是离线状态，现在重新加入，需要更新活跃学生数
if was_inactive:
    session.active_students = (session.active_students or 0) + 1
```

### 2. 前端优化 (`frontend/src/composables/useClassroomSession.ts`)

#### 改进 `findAndJoinSession` 函数
- **问题**：查找会话失败时没有重试机制，网络波动可能导致无法加入
- **优化**：
  - 添加自动重试机制（最多3次，每次间隔2秒）
  - 优先查找 `active` 状态的会话，如果没有再查找 `pending` 状态的会话
  - 改进错误处理，区分不同类型的错误（会话已结束、权限不足等）
  - 对于可恢复的错误（网络错误等），自动重试
  - 对于不可恢复的错误（会话已结束、权限不足），立即返回，不重试

```typescript
async function findAndJoinSession(retryCount: number = 0): Promise<ClassSession | null> {
  const MAX_RETRIES = 3
  const RETRY_DELAY = 2000 // 2秒
  
  // ... 查找和加入逻辑
  
  // 如果失败且有重试次数，自动重试
  if (retryCount < MAX_RETRIES) {
    await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
    return findAndJoinSession(retryCount + 1)
  }
}
```

#### 增强 WebSocket 重连处理
- **问题**：WebSocket 重连失败时，没有降级到轮询模式
- **优化**：
  - 监听 `reconnect_failed` 事件，自动降级到轮询模式
  - 监听 `connection_closed` 事件，区分服务器主动关闭的原因
  - 如果是因为会话已结束，停止轮询；如果是其他原因，降级到轮询模式

### 3. WebSocket 服务优化 (`frontend/src/services/websocket.ts`)

#### 改进重连机制
- **问题**：重连失败时没有足够的重试次数和错误处理
- **优化**：
  - 使用指数退避策略（但最大延迟不超过30秒）
  - 增加重连次数上限（5次）
  - 区分不同类型的连接关闭原因（1008 代码表示服务器主动关闭）
  - 触发重连失败事件，让调用方知道需要降级到轮询模式

```typescript
// 使用指数退避策略
const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)

// 检查关闭代码，某些代码不应该重连（如会话已结束）
if (event.code === 1008) {
  // 1008: Policy Violation，通常是服务器主动关闭
  console.warn('⚠️ 服务器主动关闭连接，可能原因:', event.reason)
}
```

### 4. 用户体验优化

#### 改进错误提示
- **问题**：错误提示不够清晰，用户不知道发生了什么
- **优化**：
  - 区分不同类型的错误，给出相应的提示
  - 对于可恢复的错误，不显示错误提示（后台自动重试）
  - 对于不可恢复的错误，给出清晰的错误信息

## 使用场景

### 场景1：教师开始上课后，学生加入
1. 学生点击"进入课堂"
2. 前端查找 `active` 状态的会话
3. 如果找到，调用 `join_session` API 加入
4. 建立 WebSocket 连接
5. 如果 WebSocket 连接失败，降级到轮询模式

### 场景2：学生异常退出后重新加入
1. 学生重新打开页面或刷新页面
2. 前端查找 `active` 或 `pending` 状态的会话
3. 调用 `join_session` API，后端检测到之前已加入但离线，更新状态
4. 建立 WebSocket 连接
5. 如果 WebSocket 连接失败，降级到轮询模式

### 场景3：网络波动导致连接断开
1. WebSocket 连接断开
2. 自动尝试重连（最多5次，使用指数退避）
3. 如果重连成功，恢复正常
4. 如果重连失败，降级到轮询模式（每5秒轮询一次）

## 技术细节

### 重试策略
- **查找会话**：最多3次，每次间隔2秒
- **WebSocket 重连**：最多5次，使用指数退避（最大延迟30秒）

### 降级机制
- WebSocket 连接失败 → 降级到轮询模式（每5秒轮询一次）
- 轮询模式可以保证学生能够接收到教师的内容切换，但实时性稍差

### 状态同步
- 后端自动同步会话的 `current_cell_id` 到学生参与记录
- 学生重新加入时，自动同步到当前教师显示的内容

## 测试建议

1. **测试场景1**：教师开始上课后，学生尝试加入
2. **测试场景2**：学生加入后，关闭浏览器，重新打开并加入
3. **测试场景3**：学生加入后，断开网络，重新连接
4. **测试场景4**：学生加入后，教师结束会话，学生尝试加入（应该失败并提示）

## 注意事项

1. 轮询模式会增加服务器负载，但可以保证在 WebSocket 不可用时仍能正常工作
2. 重试机制可能会增加请求次数，但可以处理网络波动等临时问题
3. 学生重新加入时，会自动同步到当前教师显示的内容，不会丢失进度

