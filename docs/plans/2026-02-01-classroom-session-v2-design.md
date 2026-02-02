# 课堂会话模式 v2.0 设计文档

**创建时间**: 2026-02-01
**版本**: 2.0
**作者**: Claude (AI Assistant)
**状态**: 设计阶段，待实施

---

## 📋 文档概述

本文档描述了课堂会话系统的全面重构设计，旨在解决当前系统存在的复杂度高、可维护性差、性能问题等。

### 当前问题

- **代码量巨大**: 4个核心文件共8,067行代码
  - `TeacherControlPanel.vue`: 5,047行
  - `classroom_sessions.py`: 2,017行
  - `useClassroomSession.ts`: 732行
  - `StudentClassroomSync.vue`: 271行

- **状态管理复杂**: 4种状态（PENDING, ACTIVE, PAUSED, ENDED）
- **实时通信双重机制**: WebSocket + HTTP轮询
- **班级双重关联**: User.classroom_id + ClassroomMembership
- **状态不一致**: 前后端大小写混乱（刚修复）

### 重构目标

- **代码量**: 从8,067行 → ~2,000行（减少75%）
- **单文件限制**: 所有文件 < 400行
- **状态管理**: 简化为3个状态
- **实时通信**: 纯WebSocket，移除轮询
- **可维护性**: 职责清晰，易于测试

---

## 🎯 核心功能

### 必须保留的功能

✅ **基础课堂流程**
- 教师创建课堂 → 学生加入 → 教师开始上课 → 结束课程

✅ **实时同步**
- 教师切换内容，学生端自动同步显示
- WebSocket推送

✅ **多班级支持**
- 一个教师可以管理多个班级
- 一个学生可以属于多个班级

✅ **学生进度追踪**
- 实时显示学生的答题进度
- 统计数据

✅ **课后模式**
- 课后学生仍可查看课程内容

### 简化的功能

⚠️ **暂停/继续功能**
- 移除PAUSED状态
- 如需暂停，直接结束课程，稍后重新开始

⚠️ **显示模式控制**
- 移除全屏/窗口切换功能
- 简化教师操作

---

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────┐
│                    前端层                        │
├─────────────────────────────────────────────────┤
│  TeacherControlPanel.vue (200行)               │
│    ├─ SessionHeader.vue (150行)                │
│    ├─ StudentList.vue (200行)                  │
│    ├─ ContentNavigator.vue (300行)             │
│    ├─ SessionTimer.vue (150行)                  │
│    └─ ActionButtons.vue (100行)                │
│                                                 │
│  Composables:                                   │
│    ├─ useSessionManager.ts (200行)             │
│    ├─ useWebSocket.ts (150行)                  │
│    ├─ useStudentTracking.ts (200行)            │
│    └─ useClassroomStore.ts (150行)             │
└─────────────────────────────────────────────────┘
                    ↓ WebSocket
┌─────────────────────────────────────────────────┐
│                   后端层                        │
├─────────────────────────────────────────────────┤
│  classroom_sessions.py (800行) ← 从2017行简化   │
│    ├─ 会话CRUD (200行)                          │
│    ├─ 状态管理 (150行)                          │
│    ├─ WebSocket处理 (250行)                     │
│    └─ 学生参与追踪 (200行)                      │
│                                                 │
│  Services:                                      │
│    ├─ session_state_machine.py (新增, 150行)   │
│    └─ websocket_manager.py (简化)              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│                  数据层                         │
├─────────────────────────────────────────────────┤
│  简化后的数据模型：                             │
│    - ClassSession (3个状态)                     │
│    - ClassroomMembership (统一班级关联)         │
│    - StudentSessionParticipation (进度追踪)     │
└─────────────────────────────────────────────────┘
```

---

## 🎨 前端设计

### 状态机设计

**简化后的状态流：**

```
PREPARING (准备中)
    ↓ 教师点击"开始上课"
TEACHING (上课中)
    ↓ 教师点击"结束课程"
ENDED (已结束)
```

**移除的状态：**
- ~~PAUSED~~ (使用频率低)

### 组件拆分

#### 主容器: TeacherControlPanel.vue (~200行)

**职责：** 组装和协调子组件

```vue
<template>
  <div class="teacher-control-panel">
    <SessionHeader :session="session" :status="sessionStatus" />
    <StudentList :students="activeStudents" :total="totalStudents" />
    <ContentNavigator :cells="lessonCells" :current-cell="currentCellId" />
    <SessionTimer :duration="sessionDuration" />
    <ActionButtons :status="sessionStatus" @start="handleStart" @end="handleEnd" />
  </div>
</template>
```

#### 子组件职责

| 组件 | 行数 | 职责 |
|------|------|------|
| SessionHeader.vue | 150 | 显示课程标题、状态、时间 |
| StudentList.vue | 200 | 显示在线学生、进度、踢出功能 |
| ContentNavigator.vue | 300 | 内容选择和导航 |
| SessionTimer.vue | 150 | 课程计时器 |
| ActionButtons.vue | 100 | 开始上课、结束课程按钮 |

### Composables设计

#### useSessionManager.ts (~200行)

核心会话管理逻辑：

```typescript
interface SessionManagerState {
  session: Ref<ClassSession | null>
  sessionStatus: Ref<SessionStatus>
  sessionDuration: Ref<number>
  activeStudents: Ref<Student[]>

  createSession(lessonId, classroomId): Promise<void>
  startSession(): Promise<void>
  endSession(): Promise<void>
}
```

#### useWebSocket.ts (~150行)

纯WebSocket通信，移除轮询：

```typescript
function connect(sessionId: number)
function broadcast(message: WSMessage)
function handleMessage(message: WSMessage)
```

**关键改进：**
- 使用@vueuse/core的useWebSocket
- 自动重连（最多3次）
- 失败后提示用户刷新

#### useStudentTracking.ts (~200行)

学生进度追踪和统计：

```typescript
function loadStudents(): Promise<void>
function updateStudentProgress(studentId, progress): void
function kickStudent(studentId): Promise<void>
```

#### useClassroomStore.ts (~150行)

Pinia状态管理，单一数据源：

```typescript
const session = ref<ClassSession | null>(null)
const students = ref<Student[]>([])
const duration = ref(0)
const currentCell = ref<number | null>(null)

const isTeaching = computed(() => session.value?.status === 'TEACHING')
```

---

## 🔧 后端设计

### 状态机实现

```python
class SessionStatus(str, Enum):
    PREPARING = "PREPARING"  # 准备中
    TEACHING = "TEACHING"    # 上课中
    ENDED = "ENDED"          # 已结束

class SessionStateMachine:
    """会话状态机"""

    TRANSITIONS = {
        SessionStatus.PREPARING: [SessionStatus.TEACHING, SessionStatus.ENDED],
        SessionStatus.TEACHING: [SessionStatus.ENDED],
        SessionStatus.ENDED: []  # 终态
    }

    def can_transition_to(self, new_status: SessionStatus) -> bool:
        """检查是否可以转换到新状态"""
        current = self.session.status
        allowed = self.TRANSITIONS.get(current, [])
        return new_status in allowed

    def transition_to(self, new_status: SessionStatus) -> bool:
        """执行状态转换"""
        if not self.can_transition_to(new_status):
            raise InvalidStateTransition(...)
        self.session.status = new_status
        return True
```

### API端点简化

| 端点 | 方法 | 说明 | 代码行数 |
|------|------|------|---------|
| `/sessions` | POST | 创建会话 | 50 |
| `/sessions/{id}/start` | POST | 开始上课 | 80 |
| `/sessions/{id}/end` | POST | 结束课程 | 80 |
| `/sessions/{id}/navigate` | POST | 切换内容 | 100 |
| `/sessions/{id}/join` | POST | 学生加入 | 80 |
| `/sessions/{id}/ws` | WebSocket | 实时通信 | 150 |

**总计**: ~800行（从2017行减少60%）

### WebSocket简化

**移除降级逻辑：**
- ~~HTTP轮询降级~~
- 纯WebSocket + 自动重连

**关键改进：**
```python
@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(...):
    # 1. 验证Token
    # 2. 验证会话存在
    # 3. 验证班级权限
    # 4. 接受连接
    # 5. 注册到管理器
    # 6. 发送初始状态
    # 7. 监听消息循环
```

---

## 📊 数据流设计

### 1. 教师创建课堂流程

```
TeacherControlPanel.vue
  ↓ 点击"创建课堂"
useSessionManager.createSession()
  ↓ POST /api/sessions
后端: 创建会话 (status=PREPARING)
  ↓ 返回会话对象
前端: setSession(session)
  ↓ 连接WebSocket
  ↓ 显示"等待学生加入"
```

### 2. 学生加入课堂流程

```
LessonView.vue
  ↓ 自动调用
useClassroomSession.findAndJoinSession()
  ↓ GET /api/lessons/{id}/sessions
  ↓ 过滤PREPARING/TEACHING状态
  ↓ POST /api/sessions/{id}/join
后端: 验证权限 + 创建参与记录
  ↓ 返回参与信息
前端: 连接WebSocket
  ↓ 显示"等待教师开始上课"
```

### 3. 教师开始上课流程

```
TeacherControlPanel.vue
  ↓ 点击"开始上课"
useSessionManager.startSession()
  ↓ POST /api/sessions/{id}/start
后端: 状态转换 PREPARING → TEACHING
  ↓ 初始化current_cell_id
  ↓ 广播WebSocket: session_started
前端: 所有学生收到消息
  ↓ 更新状态为TEACHING
  ↓ 显示课程内容
```

### 4. 内容导航流程

```
ContentNavigator.vue
  ↓ 教师勾选模块
handleNavigate([1, 2, 3])
  ↓ POST /api/sessions/{id}/navigate
后端: 更新display_cell_orders
  ↓ 广播WebSocket: cell_changed
前端: 所有学生收到
  ↓ 更新displayCellId
  ↓ 只显示选中的模块
```

---

## ⚠️ 错误处理设计

### 前端统一错误处理

```typescript
enum ErrorCode {
  NETWORK_ERROR = "NETWORK_ERROR",
  UNAUTHORIZED = "UNAUTHORIZED",
  FORBIDDEN = "FORBIDDEN",
  SESSION_NOT_FOUND = "SESSION_NOT_FOUND",
  INVALID_STATE = "INVALID_STATE",
  WEBSOCKET_FAILED = "WEBSOCKET_FAILED"
}

function handleApiError(error: any): string {
  if (error.response) {
    const { status, data } = error.response
    switch (status) {
      case 401: return "登录已过期，请重新登录"
      case 403: return data.detail || "您没有权限执行此操作"
      case 404: return "会话不存在或已被删除"
      case 400: return "请求参数错误"
      default: return "网络错误，请稍后重试"
    }
  }
  return "未知错误"
}
```

### WebSocket错误处理

```typescript
ws.value.onclose = (event) => {
  switch (event.code) {
    case 1000:  // 正常关闭
      break
    case 1008:  // 策略错误
      ElMessage.error('您无权连接或会话已结束')
      break
    case 1006:  // 异常关闭
      if (reconnectAttempts < 3) {
        reconnect()
      } else {
        ElMessage.error('连接失败，请刷新页面')
      }
      break
  }
}
```

### 后端异常类

```python
class TeachingException(HTTPException):
    """课堂相关异常基类"""

class InvalidStateTransition(TeachingException):
    """非法状态转换"""

class SessionNotFound(TeachingException):
    """会话不存在"""

class NotInClassroom(TeachingException):
    """用户不在班级中"""
```

---

## 🧪 测试策略

### 单元测试

#### 后端测试

**状态机测试：**
- ✅ PREPARING → TEACHING 转换
- ✅ TEACHING → ENDED 转换
- ❌ TEACHING → PREPARING 非法转换
- ❌ ENDED 终态转换

**班级权限测试：**
- ✅ 通过 ClassroomMembership 检查
- ✅ 多班级支持
- ❌ 不在班级中返回false

#### 前端测试

**Composables测试：**
- ✅ createSession + WebSocket连接
- ✅ startSession 状态转换
- ✅ WebSocket自动重连
- ❌ 错误处理

### 集成测试

**完整授课流程：**
1. 教师创建会话 → PREPARING
2. 学生加入 → 参与记录创建
3. 教师开始上课 → TEACHING
4. 教师结束课程 → ENDED

### E2E测试

**使用Playwright：**
```typescript
test('完整流程', async ({ page }) => {
  // 1. 教师登录
  // 2. 创建课堂
  // 3. 学生加入
  // 4. 教师开始上课
  // 5. 学生看到内容
  // 6. 教师结束课程
  // 7. 学生看到结束提示
})
```

### 测试覆盖率目标

| 模块 | 单元测试 | 集成测试 | E2E测试 |
|------|---------|---------|---------|
| 后端状态机 | 100% | - | - |
| 后端API | 80% | 60% | - |
| 前端Composables | 90% | - | - |
| 前端组件 | 70% | - | - |
| 关键流程 | - | 80% | 100% |

---

## 📦 实施计划

### 第1阶段：准备（1周）

- [x] 修复状态大小写问题
- [ ] 创建git worktree
- [ ] 设置开发环境
- [ ] 编写单元测试框架

### 第2阶段：后端重构（2-3周）

- [ ] 实现SessionStateMachine
- [ ] 简化classroom_sessions.py
- [ ] 移除PAUSED状态相关代码
- [ ] 简化WebSocket处理
- [ ] 编写单元测试

### 第3阶段：前端重构（3-4周）

- [ ] 拆分TeacherControlPanel.vue
- [ ] 实现useSessionManager.ts
- [ ] 实现useWebSocket.ts（移除轮询）
- [ ] 实现useClassroomStore.ts
- [ ] 编写单元测试

### 第4阶段：集成测试（1-2周）

- [ ] 集成测试
- [ ] E2E测试
- [ ] 性能测试
- [ ] 修复bug

### 第5阶段：部署（1周）

- [ ] 代码审查
- [ ] 文档更新
- [ ] 灰度发布
- [ ] 监控和反馈

**总计**: 8-11周

---

## 📈 预期收益

### 代码量

| 指标 | 当前 | 目标 | 改善 |
|------|------|------|------|
| 前端代码 | 6,050行 | ~1,200行 | ⬇️ 80% |
| 后端代码 | 2,017行 | ~800行 | ⬇️ 60% |
| 总计 | 8,067行 | ~2,000行 | ⬇️ 75% |

### 可维护性

- **单文件行数**: 最大5,047行 → 最大400行
- **组件职责**: 清晰分离
- **测试覆盖率**: 0% → 75%+
- **Bug修复时间**: 平均2小时 → 30分钟

### 性能

- **WebSocket重连**: 自动化，无需手动刷新
- **状态查询**: 简化状态机，减少50%检查逻辑
- **内存占用**: 减少40%（移除轮询定时器）

---

## 🔍 技术债务清理

### 已解决

- ✅ 状态大小写不一致
- ✅ 前端状态过滤错误

### 待解决

- [ ] 移除HTTP轮询降级逻辑
- [ ] 统一班级关联方式（迁移到ClassroomMembership）
- [ ] 拆分巨型组件
- [ ] 添加单元测试

---

## 📝 附录

### 相关文件

**当前版本（旧）：**
- `frontend/src/components/Classroom/TeacherControlPanel.vue` (5,047行)
- `frontend/src/composables/useClassroomSession.ts` (732行)
- `backend/app/api/v1/classroom_sessions.py` (2,017行)

**新版本（设计）：**
- `frontend/src/components/Classroom/TeacherControlPanel.vue` (~200行)
- `frontend/src/composables/useSessionManager.ts` (~200行)
- `frontend/src/composables/useWebSocket.ts` (~150行)
- `backend/app/api/v1/classroom_sessions.py` (~800行)
- `backend/app/services/session_state_machine.py` (~150行)

### 参考资料

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia State Management](https://pinia.vuejs.org/)
- [@vueuse/core](https://vueuse.org/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [Playwright E2E Testing](https://playwright.dev/)

---

**文档结束**
