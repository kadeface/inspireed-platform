# 进度日志：理清学生如何加入课堂

## 2025-01-XX 开始任务

### Phase 1: 前端流程分析 [completed]

#### 已完成
1. ✅ 分析学生端触发入口（LessonView.vue）
2. ✅ 分析 `useClassroomSession` composable
3. ✅ 分析 `findAndJoinSession` 函数逻辑
4. ✅ 分析会话查找和选择策略
5. ✅ 分析前端错误处理和重试机制

#### 关键发现
- 学生打开教案页面时自动调用 `findAndJoinSession()`
- 优先查找 `active` 状态的会话，其次 `pending` 状态
- 按 ID 降序排序选择最新会话
- 支持最多 3 次重试，特殊错误（403、400）不重试
- WebSocket 连接延迟 500ms，失败时降级到轮询模式

### Phase 2: API 接口分析 [completed]

#### 已完成
1. ✅ 分析 `/sessions/{session_id}/join` 接口
2. ✅ 分析权限验证逻辑（`check_user_in_classroom`）
3. ✅ 分析班级成员关系检查（`ClassroomMembership`）
4. ✅ 分析参与记录创建/更新逻辑（`StudentSessionParticipation`）
5. ✅ 分析会话状态检查
6. ✅ 分析会话列表查询 API

#### 关键发现
- 权限检查包括：角色检查、会话存在性、会话状态、班级成员关系
- 使用统一的 `check_user_in_classroom()` 函数检查班级成员关系
- 支持多班级（通过 `ClassroomMembership`）和向后兼容（`User.classroom_id`）
- 已加入的学生会更新状态，未加入的创建新记录
- 更新会话统计（`total_students`、`active_students`）

### Phase 3: 数据模型分析 [completed]

#### 已完成
1. ✅ 分析 `ClassSession` 模型
2. ✅ 分析 `StudentSessionParticipation` 模型
3. ✅ 分析 `ClassroomMembership` 模型
4. ✅ 分析模型之间的关系

#### 关键发现
- `ClassSession`: 课堂会话，包含状态、当前Cell、学生统计等
- `StudentSessionParticipation`: 学生参与记录，包含加入时间、活跃状态、进度等
- `ClassroomMembership`: 班级成员关系，支持多班级和角色管理
- 使用数据库唯一约束防止重复加入

### Phase 4: WebSocket 连接分析 [completed]

#### 已完成
1. ✅ 分析 WebSocket 连接建立流程
2. ✅ 分析实时同步机制
3. ✅ 分析降级方案（轮询）

#### 关键发现
- WebSocket URL: `/api/v1/classroom-sessions/sessions/{session_id}/ws?token={jwt}`
- 连接流程：CORS 验证 → 接受连接 → Token 验证 → 权限检查 → 绑定学生
- 降级方案：WebSocket 失败时使用 5 秒轮询间隔
- 延迟 500ms 建立连接，避免资源竞争

### Phase 5: 完整流程图绘制 [completed]

#### 已完成
1. ✅ 绘制端到端的流程图
2. ✅ 标注关键决策点
3. ✅ 标注错误处理路径
4. ✅ 标注数据流转

#### 关键发现
- 完整流程：页面加载 → 查找会话 → 选择会话 → 加入会话 → 建立 WebSocket
- 错误处理：特殊错误不重试，其他错误最多重试 3 次
- 数据一致性：使用数据库唯一约束，支持重新加入场景

## 总结

已全面理清学生加入课堂的完整流程，包括：
- 前端触发和流程控制
- API 接口和权限验证
- 数据模型和关系
- WebSocket 连接和降级方案
- 错误处理和数据一致性

所有发现已记录在 `findings_student_join.md` 中。
