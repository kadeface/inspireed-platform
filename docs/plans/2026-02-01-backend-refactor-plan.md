# 课堂会话后端重构计划

**创建时间**: 2026-02-01
**阶段**: 第2阶段 - 后端重构
**目标**: 从2017行简化到~800行（减少60%）

---

## 📋 当前文件分析

### 文件大小
- `backend/app/api/v1/classroom_sessions.py`: 2017行
- 需要减少到: ~800行

### API端点统计（共18个）
1. `POST /lessons/{lesson_id}/sessions` - 创建会话
2. `GET /sessions/{session_id}` - 获取会话详情
3. `GET /lessons/{lesson_id}/sessions` - 获取教案的所有会话
4. `POST /sessions/{session_id}/start` - 开始上课
5. `POST /sessions/{session_id}/pause` - **暂停会话（需移除）**
6. `POST /sessions/{session_id}/resume` - **恢复会话（需移除）**
7. `POST /sessions/{session_id}/end` - 结束课程
8. `POST /sessions/{session_id}/navigate` - 切换内容
9. `POST /sessions/{session_id}/display-mode` - **更新显示模式（需移除）**
10. `POST /sessions/{session_id}/start-activity` - 开始活动
11. `POST /sessions/{session_id}/end-activity` - 结束活动
12. `GET /sessions/{session_id}/participants` - 获取参与者列表
13. `POST /sessions/{session_id}/join` - 学生加入
14. `POST /sessions/{session_id}/leave` - 学生离开
15. `GET /student/pending-sessions` - 学生待加入会话
16. `GET /student/active-sessions` - 学生活跃会话
17. `GET /sessions/{session_id}/statistics` - 统计信息
18. `POST /sessions/{session_id}/check-teacher-status` - 检查教师状态
19. `WS /sessions/{session_id}/ws` - 学生WebSocket
20. `WS /sessions/{session_id}/ws/teacher` - 教师WebSocket
21. `WS /lessons/{lesson_id}/ws/teacher` - 教师WebSocket（by lesson）

### PAUSED状态使用位置
- 第125行: 查询过滤（PENDING, ACTIVE, PAUSED）
- 第403行: `pause_session` 端点
- 第423行: 设置状态为PAUSED
- 第461行: resume检查PAUSED状态
- 第480行: PAUSED → ACTIVE广播
- 第1332行: 教师状态检查
- 第1787行: 教师WebSocket连接检查

---

## 🎯 重构任务

### 任务1: 更新状态枚举（优先级：高）

**文件**: `backend/app/models/classroom_session.py`

**修改前**:
```python
class ClassSessionStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"  # ❌ 移除
    ENDED = "ENDED"
```

**修改后**:
```python
class ClassSessionStatus(str, Enum):
    PREPARING = "PREPARING"  # 准备中（原PENDING）
    TEACHING = "TEACHING"    # 上课中（原ACTIVE）
    ENDED = "ENDED"          # 已结束
```

**影响范围**: 全局

---

### 任务2: 移除PAUSE/RESUME端点（优先级：高）

**文件**: `backend/app/api/v1/classroom_sessions.py`

**移除端点**:
- `POST /sessions/{session_id}/pause` (第403行)
- `POST /sessions/{session_id}/resume` (第444行)

**代码行数**: ~80行

---

### 任务3: 移除显示模式相关代码（优先级：中）

**文件**: `backend/app/api/v1/classroom_sessions.py`

**移除端点**:
- `POST /sessions/{session_id}/display-mode` (第692行)

**移除模型字段**:
- `ClassSession.display_mode`

**代码行数**: ~100行

---

### 任务4: 集成SessionStateMachine（优先级：高）

**文件**: `backend/app/api/v1/classroom_sessions.py`

**修改内容**:
1. 导入SessionStateMachine
2. 在状态转换处使用状态机验证
3. 替换直接状态赋值为状态机转换

**示例**:
```python
# 修改前
session.status = ClassSessionStatus.ACTIVE

# 修改后
from app.services.session_state_machine import SessionStateMachine, SessionStatus
state_machine = SessionStateMachine(initial_status=session.status)
state_machine.transition_to(SessionStatus.TEACHING)
session.status = state_machine.status
```

---

### 任务5: 简化WebSocket处理（优先级：中）

**文件**: `backend/app/api/v1/classroom_sessions.py`

**优化内容**:
1. 提取公共连接验证逻辑
2. 统一WebSocket消息格式
3. 简化消息广播逻辑

**代码行数**: ~400行 → ~250行

---

### 任务6: 更新状态引用（优先级：高）

**文件**: `backend/app/api/v1/classroom_sessions.py`

**需要修改的位置**:
1. 第125行: 查询过滤（移除PAUSED）
2. 第1332行: 教师状态检查（移除PAUSED）
3. 第1787行: WebSocket检查（移除PAUSED）

**修改前**:
```python
if session.status in [ClassSessionStatus.ACTIVE, ClassSessionStatus.PAUSED]:
```

**修改后**:
```python
if session.status == ClassSessionStatus.TEACHING:
```

---

## 📊 代码行数预估

| 部分 | 当前行数 | 重构后行数 | 减少 |
|------|---------|-----------|------|
| 状态枚举 | 20行 | 15行 | -5行 |
| PAUSE/RESUME端点 | ~80行 | 0行 | -80行 |
| 显示模式端点 | ~100行 | 0行 | -100行 |
| WebSocket处理 | ~400行 | ~250行 | -150行 |
| 状态检查简化 | ~50行 | ~30行 | -20行 |
| 其他端点 | ~1367行 | ~1200行 | -167行 |
| **总计** | **2017行** | **~1600行** | **~420行** |

**目标**: 通过进一步提取服务层，最终减少到~800行

---

## 🔄 执行顺序

### 第1步: 更新状态枚举
- 修改ClassSessionStatus
- 运行测试确保没有破坏性变更

### 第2步: 移除PAUSE/RESUME功能
- 删除pause_session端点
- 删除resume_session端点
- 更新schema文件

### 第3步: 移除显示模式功能
- 删除display-mode端点
- 移除display_mode字段

### 第4步: 更新状态引用
- 替换所有PENDING → PREPARING
- 替换所有ACTIVE → TEACHING
- 移除所有PAUSED引用

### 第5步: 集成SessionStateMachine
- 导入状态机
- 在状态转换处添加验证
- 添加错误处理

### 第6步: 简化WebSocket处理
- 提取公共逻辑
- 统一消息格式

### 第7步: 编写单元测试
- 状态转换测试
- API端点测试
- WebSocket测试

### 第8步: 运行完整测试
- 后端pytest
- 集成测试
- 性能测试

---

## ⚠️ 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 破坏现有功能 | 高 | 完整的单元测试和集成测试 |
| 前端兼容性 | 中 | 前端同步更新状态枚举 |
| 数据库迁移 | 中 | 需要迁移脚本更新现有数据 |
| WebSocket断开 | 中 | 保留向后兼容的降级逻辑 |

---

## 📝 注意事项

1. **数据迁移**: 需要更新数据库中现有的PAUSED状态
2. **前端同步**: 前端需要同步更新状态枚举
3. **测试覆盖**: 每个修改都需要对应的测试
4. **向后兼容**: 考虑保留API兼容性（如果需要）
5. **日志记录**: 添加详细的日志以便调试

---

## 🎯 成功标准

- [ ] 代码行数从2017行减少到~800行
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 没有PAUSED状态引用
- [ ] SessionStateMachine完全集成
- [ ] WebSocket处理简化
- [ ] 性能测试通过

---

**开始时间**: 2026-02-01 12:00
**预计完成**: 2026-02-22（3周）
