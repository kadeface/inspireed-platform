# 发现记录：学生加入课堂流程分析

## 初步发现

### 1. 前端入口点

#### 1.1 页面组件
- **位置**: `frontend/src/pages/Student/LessonView.vue`
- **触发**: 学生打开教案页面时自动调用 `findAndJoinSession()`

#### 1.2 Composable
- **位置**: `frontend/src/composables/useClassroomSession.ts`
- **主要函数**: `findAndJoinSession()`
- **功能**: 查找并加入课堂会话

### 2. 前端流程（findAndJoinSession）

#### 步骤 1: 查找会话
```typescript
// 1. 先查找 active 状态的会话
let sessions = await classroomSessionService.listSessions(lessonId, 'active')

// 2. 如果没有 active，查找 pending 状态的会话
if (sessions.length === 0) {
  const allSessions = await classroomSessionService.listSessions(lessonId)
  sessions = allSessions.filter(s => s.status === 'pending' || s.status === 'active')
}
```

#### 步骤 2: 选择会话
- 按 ID 降序排序（ID 越大越新）
- 优先选择 `active` 状态的会话
- 如果没有 `active`，选择 `pending` 状态的会话

#### 步骤 3: 加入会话
```typescript
participation.value = await classroomSessionService.joinSession(session.value.id)
```

#### 步骤 4: 建立 WebSocket 连接
- 延迟 500ms 后建立连接（避免资源竞争）
- 如果 WebSocket 失败，降级到轮询模式

#### 错误处理
- 支持最多 3 次重试
- 重试延迟 2 秒
- 特殊处理：
  - 403 权限错误：不重试，直接返回 null
  - 400 会话已结束：不重试，直接返回 null

### 3. API 服务层

#### 3.1 服务位置
- **文件**: `frontend/src/services/classroomSession.ts`
- **函数**: `joinSession(sessionId: number)`

#### 3.2 API 调用
```typescript
const response = await api.post(`/classroom-sessions/sessions/${sessionId}/join`)
```

#### 3.3 响应处理
- 字段映射：将后端 snake_case 转换为前端 camelCase
- 返回 `StudentParticipation` 对象

### 4. 后端 API

#### 4.1 接口位置
- **文件**: `backend/app/api/v1/classroom_sessions.py`
- **路由**: `POST /sessions/{session_id}/join`
- **函数**: `join_session()`

#### 4.2 权限验证流程

**步骤 1: 角色检查**
```python
if current_role != UserRole.STUDENT:
    raise HTTPException(status_code=403, detail="只有学生可以加入会话")
```

**步骤 2: 会话存在性检查**
```python
session = await db.get(ClassSession, session_id)
if not session:
    raise HTTPException(status_code=404, detail="会话不存在")
```

**步骤 3: 会话状态检查**
```python
if session.status == ClassSessionStatus.ENDED:
    raise HTTPException(status_code=400, detail="会话已结束")
```

**步骤 4: 班级成员关系检查**
```python
classroom_id = cast(int, session.classroom_id)
has_access = await check_user_in_classroom(db, current_user, classroom_id)

if not has_access:
    raise HTTPException(
        status_code=403, 
        detail=f"无权加入该会话：学生不属于该班级（classroom_id={classroom_id}）"
    )
```

#### 4.3 参与记录处理

**情况 1: 已存在参与记录**
- 更新 `is_active = True`
- 更新 `last_active_at = datetime.utcnow()`
- 同步 `current_cell_id`
- 如果之前是离线状态，增加 `active_students` 计数

**情况 2: 新建参与记录**
- 创建 `StudentSessionParticipation` 记录
- 设置 `is_active = True`
- 设置 `current_cell_id = session.current_cell_id`
- 增加 `total_students` 和 `active_students` 计数

### 5. 权限检查函数

#### 5.1 函数位置
- **文件**: `backend/app/core/classroom_utils.py`
- **函数**: `check_user_in_classroom()`

#### 5.2 检查逻辑
```python
async def check_user_in_classroom(
    db: AsyncSession,
    user: User,
    classroom_id: int,
    include_inactive: bool = False
) -> bool:
    classroom_ids = await get_user_classroom_ids(db, user, include_inactive)
    return classroom_id in classroom_ids
```

#### 5.3 获取用户班级ID
```python
async def get_user_classroom_ids(
    db: AsyncSession,
    user: User,
    include_inactive: bool = False
) -> Set[int]:
    # 优先从 ClassroomMembership 获取（支持多班级）
    # 如果没有，则从 User.classroom_id 获取（向后兼容）
```

### 6. 数据模型

#### 6.1 ClassSession（课堂会话）
- `id`: 会话ID
- `lesson_id`: 教案ID
- `classroom_id`: 班级ID
- `status`: 状态（pending/active/ended）
- `current_cell_id`: 当前Cell ID
- `total_students`: 总学生数
- `active_students`: 活跃学生数

#### 6.2 StudentSessionParticipation（学生参与记录）
- `id`: 参与记录ID
- `session_id`: 会话ID
- `student_id`: 学生ID
- `joined_at`: 加入时间
- `last_active_at`: 最后活跃时间
- `left_at`: 离开时间
- `is_active`: 是否在线
- `current_cell_id`: 当前Cell ID
- `completed_cells`: 已完成的Cell列表
- `progress_percentage`: 完成百分比

#### 6.3 ClassroomMembership（班级成员关系）
- `id`: 成员关系ID
- `classroom_id`: 班级ID
- `user_id`: 用户ID
- `role_in_class`: 班级内角色
- `is_active`: 是否活跃
- `is_primary_class`: 是否为主班级

### 7. WebSocket 连接

#### 7.1 连接建立
- 延迟 500ms 后建立连接
- 连接地址：`/ws/classroom-sessions/{session_id}`
- 携带 JWT token 进行认证

#### 7.2 降级方案
- 如果 WebSocket 连接失败，降级到轮询模式
- 轮询间隔：5 秒
- 轮询内容：获取会话状态更新

### 8. 会话列表查询 API

#### 8.1 前端调用
- **位置**: `frontend/src/services/classroomSession.ts`
- **函数**: `listSessions(lessonId: number, status?: string)`
- **API**: `GET /classroom-sessions/lessons/{lesson_id}/sessions?status={status}`

#### 8.2 后端实现
- **位置**: `backend/app/api/v1/classroom_sessions.py`
- **路由**: `GET /lessons/{lesson_id}/sessions`
- **函数**: `list_lesson_sessions()`
- **权限检查**:
  - 教师：只能查看自己创建的教案的会话
  - 学生：可以查看所有已发布到其班级的教案的会话

#### 8.3 查询逻辑
- 根据 `lesson_id` 查询所有会话
- 可选按 `status` 过滤（pending/active/ended）
- 返回会话列表，包括基本信息

### 9. WebSocket 连接详细流程

#### 9.1 连接建立
- **延迟**: 500ms 后建立连接（避免资源竞争）
- **URL**: `ws://{host}/api/v1/classroom-sessions/sessions/{session_id}/ws?token={jwt}`
- **认证**: 通过 JWT token 进行认证

#### 9.2 后端 WebSocket 端点
- **位置**: `backend/app/api/v1/classroom_sessions.py`
- **路由**: `@router.websocket("/sessions/{session_id}/ws")`
- **函数**: `websocket_endpoint()`

#### 9.3 连接流程
1. **CORS 验证**: 检查 Origin 头（允许 localhost、局域网 IP、Cloud Studio 域名）
2. **接受连接**: `await websocket.accept()`
3. **Token 验证**: 从 query 参数获取 token，验证并获取用户信息
4. **权限检查**: 
   - 验证用户角色（学生）
   - 验证会话存在
   - 验证学生是否属于该班级（使用 `check_user_in_classroom`）
5. **绑定学生**: 将 WebSocket 连接绑定到学生ID
6. **发送连接确认**: 发送 `connected` 消息

#### 9.4 降级方案
- 如果 WebSocket 连接失败，降级到轮询模式
- 轮询间隔：5 秒
- 轮询内容：调用 `getSession()` API 获取会话状态更新

### 10. 完整流程图

```
学生打开教案页面 (LessonView.vue)
    ↓
调用 findAndJoinSession() (useClassroomSession.ts)
    ↓
查询会话列表 (listSessions API)
    ├─ 先查找 active 状态的会话
    └─ 如果没有，查找 pending 状态的会话
    ↓
选择会话
    ├─ 按 ID 降序排序（ID 越大越新）
    ├─ 优先选择 active 状态
    └─ 如果没有 active，选择 pending 状态
    ↓
检查会话状态
    ├─ 如果 ended，返回 null
    └─ 否则继续
    ↓
调用 joinSession API
    ├─ 角色检查（必须是学生）
    ├─ 会话存在性检查
    ├─ 会话状态检查（不能是 ended）
    ├─ 班级成员关系检查 (check_user_in_classroom)
    │   ├─ 从 ClassroomMembership 获取用户班级ID
    │   └─ 如果没有，从 User.classroom_id 获取（向后兼容）
    ├─ 检查是否已加入
    │   ├─ 如果已加入：更新状态（is_active=True, last_active_at）
    │   └─ 如果未加入：创建新参与记录
    └─ 更新会话统计（total_students, active_students）
    ↓
建立 WebSocket 连接（延迟 500ms）
    ├─ 连接成功：实时同步
    └─ 连接失败：降级到轮询模式（5秒间隔）
    ↓
完成加入流程
```

### 11. 错误处理路径

#### 11.1 前端错误处理
- **403 权限错误**: 不重试，直接返回 null（学生不属于该班级）
- **400 会话已结束**: 不重试，直接返回 null
- **其他错误**: 最多重试 3 次，每次延迟 2 秒
- **WebSocket 失败**: 降级到轮询模式，不阻塞页面

#### 11.2 后端错误处理
- **角色错误**: 返回 403 "只有学生可以加入会话"
- **会话不存在**: 返回 404 "会话不存在"
- **会话已结束**: 返回 400 "会话已结束"
- **权限不足**: 返回 403 "无权加入该会话：学生不属于该班级"

### 12. 数据一致性

#### 12.1 并发加入场景
- 使用数据库唯一约束：`UniqueConstraint("session_id", "student_id")`
- 如果并发创建，数据库会抛出唯一约束错误
- 后端会捕获错误并更新现有记录

#### 12.2 重新加入场景
- 如果学生已加入但 `is_active=False`，会更新为 `True`
- 更新 `last_active_at` 时间戳
- 如果之前是离线状态，增加 `active_students` 计数

## 关键发现总结

1. **权限检查统一化**: 使用 `check_user_in_classroom()` 统一检查班级成员关系，支持多班级和向后兼容
2. **会话选择策略**: 优先选择 active 状态，其次 pending 状态，按 ID 降序排序选择最新会话
3. **重试机制**: 前端支持最多 3 次重试，特殊错误（403、400）不重试
4. **降级方案**: WebSocket 失败时自动降级到轮询模式，保证功能可用性
5. **数据一致性**: 使用数据库唯一约束防止重复加入，支持重新加入场景
