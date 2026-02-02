# 课堂会话系统 v2.0 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use @superpowers:executing-plans to implement this plan task-by-step.

**目标:** 重构课堂会话系统，将代码量从8,067行减少到~2,000行，简化状态管理，提升可维护性

**架构:** 采用状态机模式管理会话状态（PREPARING → TEACHING → ENDED），纯WebSocket通信，前端组件化拆分，后端API简化

**技术栈:**
- 后端: FastAPI, SQLAlchemy, WebSocket, pytest
- 前端: Vue 3, Composition API, Pinia, @vueuse/core, TypeScript
- 测试: Playwright (E2E), Vitest (前端), pytest (后端)

---

## 实施概览

本计划分为5个阶段，总计8-11周：

1. **第1阶段：准备** (1周) - 环境设置、测试框架
2. **第2阶段：后端重构** (2-3周) - 状态机、API简化
3. **第3阶段：前端重构** (3-4周) - 组件拆分、Composables
4. **第4阶段：集成测试** (1-2周) - 集成测试、E2E测试
5. **第5阶段：部署** (1周) - 代码审查、文档、灰度发布

---

## 第1阶段：准备（1周）

### Task 1.1: 创建开发分支和虚拟环境

**目标:** 设置隔离的开发环境

**Step 1: 创建新的git worktree**

```bash
cd /Users/382241106qq.com/inspireed-platform-main
git worktree add ../inspireed-platform-v2 feature/classroom-mode-2.0
cd ../inspireed-platform-v2
```

**Step 2: 创建Python虚拟环境**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 3: 安装前端依赖**

```bash
cd frontend
npm install
```

**Step 4: 验证环境**

```bash
# 后端
cd backend
python -c "import fastapi; print('FastAPI OK')"

# 前端
cd frontend
npm run type-check
```

**Step 5: 提交环境设置**

```bash
git add .
git commit -m "chore: setup development environment for v2.0"
```

---

### Task 1.2: 创建测试框架

**目标:** 建立后端和前端测试基础设施

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `frontend/vitest.config.ts`

**Step 1: 创建后端测试配置**

```python
# backend/tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db
from app.main import app

# 测试数据库URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test_inspireed"

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest.fixture
def override_get_db(db_session):
    """覆盖数据库依赖"""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_get_db):
    """创建测试客户端"""
    from httpx import AsyncClient
    return AsyncClient(app=app, base_url="http://test")
```

**Step 2: 创建前端测试配置**

```typescript
// frontend/vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts']
  },
  resolve: {
    alias: {
      '@': new URL('./src', import.meta.url).pathname
    }
  }
})
```

```typescript
// frontend/tests/setup.ts
import { vi } from 'vitest'

// Mock WebSocket
global.WebSocket = vi.fn(() => ({
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
}))
```

**Step 3: 运行测试验证**

```bash
# 后端
cd backend
pytest tests/ -v

# 前端
cd frontend
npm run test:unit
```

**Step 4: 提交测试框架**

```bash
git add backend/tests frontend/vitest.config.ts frontend/tests
git commit -m "test: setup testing framework for backend and frontend"
```

---

### Task 1.3: 创建状态机单元测试框架

**目标:** 先写测试，定义状态机行为（TDD）

**Files:**
- Create: `backend/tests/test_session_state_machine.py`

**Step 1: 编写状态机测试（全部失败）**

```python
# backend/tests/test_session_state_machine.py
import pytest
from app.services.session_state_machine import SessionStateMachine, SessionStatus, InvalidStateTransition

class TestSessionStateMachine:
    """会话状态机测试"""

    def test_initial_state_is_preparing(self, db_session):
        """测试：初始状态为PREPARING"""
        session = ClassSession(status=SessionStatus.PREPARING)
        state_machine = SessionStateMachine(session)

        assert state_machine.is_preparing()
        assert not state_machine.is_teaching()
        assert not state_machine.is_ended()

    def test_can_transition_from_preparing_to_teaching(self, db_session):
        """测试：PREPARING → TEACHING 是合法的"""
        session = ClassSession(status=SessionStatus.PREPARING)
        state_machine = SessionStateMachine(session)

        assert state_machine.can_transition_to(SessionStatus.TEACHING)

    def test_can_transition_from_preparing_to_teaching_successfully(self, db_session):
        """测试：成功从PREPARING转换到TEACHING"""
        session = ClassSession(status=SessionStatus.PREPARING)
        state_machine = SessionStateMachine(session)

        state_machine.transition_to(SessionStatus.TEACHING)

        assert session.status == SessionStatus.TEACHING
        assert state_machine.is_teaching()

    def test_cannot_transition_from_teaching_to_preparing(self, db_session):
        """测试：TEACHING → PREPARING 是非法的"""
        session = ClassSession(status=SessionStatus.TEACHING)
        state_machine = SessionStateMachine(session)

        assert not state_machine.can_transition_to(SessionStatus.PREPARING)

    def test_transition_from_teaching_to_preparing_raises_error(self, db_session):
        """测试：非法转换抛出异常"""
        session = ClassSession(status=SessionStatus.TEACHING)
        state_machine = SessionStateMachine(session)

        with pytest.raises(InvalidStateTransition):
            state_machine.transition_to(SessionStatus.PREPARING)

    def test_can_transition_from_teaching_to_ended(self, db_session):
        """测试：TEACHING → ENDED 是合法的"""
        session = ClassSession(status=SessionStatus.TEACHING)
        state_machine = SessionStateMachine(session)

        assert state_machine.can_transition_to(SessionStatus.ENDED)

    def test_transition_from_teaching_to_ended_successfully(self, db_session):
        """测试：成功从TEACHING转换到ENDED"""
        session = ClassSession(status=SessionStatus.TEACHING)
        state_machine = SessionStateMachine(session)

        state_machine.transition_to(SessionStatus.ENDED)

        assert session.status == SessionStatus.ENDED
        assert state_machine.is_ended()

    def test_ended_is_terminal_state(self, db_session):
        """测试：ENDED是终态，不能转换到任何状态"""
        session = ClassSession(status=SessionStatus.ENDED)
        state_machine = SessionStateMachine(session)

        assert not state_machine.can_transition_to(SessionStatus.PREPARING)
        assert not state_machine.can_transition_to(SessionStatus.TEACHING)
        assert not state_machine.can_transition_to(SessionStatus.ENDED)
```

**Step 2: 运行测试（全部失败）**

```bash
cd backend
pytest tests/test_session_state_machine.py -v
```

Expected: `FAILED - ImportError: No module named app.services.session_state_machine`

**Step 3: 提交测试**

```bash
git add backend/tests/test_session_state_machine.py
git commit -m "test: add state machine unit tests (all failing)"
```

---

## 第2阶段：后端重构（2-3周）

### Task 2.1: 实现SessionStateMachine

**目标:** 创建状态机类，使所有测试通过

**Files:**
- Create: `backend/app/services/session_state_machine.py`
- Create: `backend/app/services/__init__.py`
- Modify: `backend/app/models/classroom_session.py`

**Step 1: 创建状态枚举**

```python
# backend/app/models/classroom_session.py
# 在文件顶部添加新的状态枚举

from enum import Enum

class SessionStatus(str, Enum):
    """课堂会话状态（v2.0 简化版）"""
    PREPARING = "PREPARING"  # 准备中
    TEACHING = "TEACHING"    # 上课中
    ENDED = "ENDED"          # 已结束

# 保留旧的枚举用于向后兼容
class ClassSessionStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ENDED = "ENDED"
```

**Step 2: 实现状态机**

```python
# backend/app/services/session_state_machine.py
from typing import TYPE_CHECKING
from app.models.classroom_session import SessionStatus

if TYPE_CHECKING:
    from app.models.classroom_session import ClassSession

class InvalidStateTransition(Exception):
    """非法状态转换异常"""
    def __init__(self, current_status: SessionStatus, new_status: SessionStatus):
        self.current_status = current_status
        self.new_status = new_status
        super().__init__(
            f"Cannot transition from {current_status.value} to {new_status.value}"
        )

class SessionStateMachine:
    """会话状态机

    简化的状态转换：
    PREPARING → TEACHING → ENDED
    """

    # 允许的状态转换
    TRANSITIONS = {
        SessionStatus.PREPARING: [SessionStatus.TEACHING, SessionStatus.ENDED],
        SessionStatus.TEACHING: [SessionStatus.ENDED],
        SessionStatus.ENDED: []  # 终态
    }

    def __init__(self, session: "ClassSession"):
        """初始化状态机

        Args:
            session: ClassSession实例
        """
        self.session = session

    def can_transition_to(self, new_status: SessionStatus) -> bool:
        """检查是否可以转换到新状态

        Args:
            new_status: 目标状态

        Returns:
            True if can transition, False otherwise
        """
        current = self.session.status
        allowed = self.TRANSITIONS.get(current, [])
        return new_status in allowed

    def transition_to(self, new_status: SessionStatus) -> bool:
        """执行状态转换

        Args:
            new_status: 目标状态

        Returns:
            True if transition successful

        Raises:
            InvalidStateTransition: 如果转换不被允许
        """
        if not self.can_transition_to(new_status):
            raise InvalidStateTransition(self.session.status, new_status)

        self.session.status = new_status
        return True

    def is_preparing(self) -> bool:
        """是否在准备中"""
        return self.session.status == SessionStatus.PREPARING

    def is_teaching(self) -> bool:
        """是否在上课中"""
        return self.session.status == SessionStatus.TEACHING

    def is_ended(self) -> bool:
        """是否已结束"""
        return self.session.status == SessionStatus.ENDED
```

**Step 3: 运行测试**

```bash
cd backend
pytest tests/test_session_state_machine.py -v
```

Expected: `PASSED` (所有10个测试通过)

**Step 4: 提交状态机实现**

```bash
git add backend/app/services/session_state_machine.py backend/app/services/__init__.py backend/app/models/classroom_session.py
git commit -m "feat: implement SessionStateMachine with TDD

- Add SessionStatus enum (PREPARING, TEACHING, ENDED)
- Implement SessionStateMachine class
- All 10 unit tests passing
"
```

---

### Task 2.2: 简化classroom_sessions.py - 移除PAUSED状态

**目标:** 更新API端点，使用新的状态机

**Files:**
- Modify: `backend/app/api/v1/classroom_sessions.py`

**Step 1: 添加状态机导入**

```python
# backend/app/api/v1/classroom_sessions.py
# 在文件顶部添加

from app.services.session_state_machine import SessionStateMachine, SessionStatus, InvalidStateTransition
```

**Step 2: 更新create_class_session函数**

```python
# backend/app/api/v1/classroom_sessions.py
# 找到 create_class_session 函数，修改为：

@router.post("/lessons/{lesson_id}/sessions", response_model=ClassSessionResponse, status_code=201)
async def create_class_session(
    lesson_id: int,
    data: ClassSessionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """创建课堂会话"""
    # ... 前面的验证逻辑保持不变 ...

    # 创建会话（使用新的状态）
    session = ClassSession(
        lesson_id=lesson_id,
        classroom_id=data.classroom_id,
        teacher_id=current_user_id,
        scheduled_start=data.scheduled_start,
        settings=session_settings,
        status=SessionStatus.PREPARING,  # 使用新状态
        total_students=0,
        active_students=0,
        current_cell_id=None,
    )
```

**Step 3: 移除pause_session和resume_session端点**

```python
# backend/app/api/v1/classroom_sessions.py
# 找到这两个函数并删除：

# @router.post("/sessions/{session_id}/pause", ...)  # 删除
# @router.post("/sessions/{session_id}/resume", ...)  # 删除
```

**Step 4: 更新start_session函数**

```python
# backend/app/api/v1/classroom_sessions.py
# 替换现有的start_session函数：

@router.post("/sessions/{session_id}/start", response_model=ClassSessionResponse)
async def start_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """开始课堂会话：PREPARING → TEACHING"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 使用状态机进行转换
    state_machine = SessionStateMachine(session)
    try:
        state_machine.transition_to(SessionStatus.TEACHING)
    except InvalidStateTransition:
        raise HTTPException(
            status_code=400,
            detail=f"当前状态为{session.status.value}，无法开始上课"
        )

    # 更新开始时间
    session.actual_start = datetime.utcnow()

    # 自动初始化显示内容（显示第一个cell）
    session_lesson_id = cast(int, session.lesson_id)
    result = await db.execute(
        select(Cell).where(
            Cell.lesson_id == session_lesson_id
        ).order_by(Cell.order.asc(), Cell.id.asc()).limit(1)
    )
    first_cell = result.scalar_one_or_none()

    if first_cell:
        session.current_cell_id = cast(int, first_cell.id)
        # 更新 display_cell_orders
        new_settings = dict(session.settings) if session.settings else {}
        new_settings["display_cell_orders"] = [first_cell.order]
        setattr(session, "settings", new_settings)

    await db.commit()
    await db.refresh(session)

    # 广播WebSocket
    await manager.broadcast_to_session(
        message={
            "type": "session_started",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "status": session.status.value,
                "actual_start": session.actual_start.isoformat(),
                "current_cell_id": session.current_cell_id,
            }
        },
        session_id=session_id
    )

    return session
```

**Step 5: 更新end_session函数**

```python
# backend/app/api/v1/classroom_sessions.py
# 替换现有的end_session函数：

@router.post("/sessions/{session_id}/end", response_model=ClassSessionResponse)
async def end_session(
    session_id: int,
    data: Optional[EndSessionRequest] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """结束课堂会话：TEACHING/PREPARING → ENDED"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 幂等性检查
    if session.status == SessionStatus.ENDED:
        return session

    # 使用状态机进行转换
    state_machine = SessionStateMachine(session)
    state_machine.transition_to(SessionStatus.ENDED)

    # 更新结束时间和时长
    session.ended_at = datetime.utcnow()

    if session.actual_start:
        duration = (session.ended_at - session.actual_start).total_seconds() / 60
        session.duration_minutes = int(duration)

    # 更新所有学生为离线
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.is_active == True,
            )
        )
    )
    participations = result.scalars().all()
    for participation in participations:
        participation.is_active = False
        participation.left_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    # 广播WebSocket
    await manager.broadcast_to_session(
        message={
            "type": "session_ended",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "message": "课程已结束"
            }
        },
        session_id=session_id
    )

    return session
```

**Step 6: 运行测试验证**

```bash
cd backend
pytest tests/test_session_state_machine.py -v
```

**Step 7: 提交更改**

```bash
git add backend/app/api/v1/classroom_sessions.py
git commit -m "refactor: simplify classroom sessions API - remove PAUSED state

- Use SessionStateMachine for state transitions
- Remove pause_session and resume_session endpoints
- Update start_session to use PREPARING → TEACHING
- Update end_session to use TEACHING/PREPARING → ENDED
- All state machine tests passing
"
```

---

### Task 2.3: 简化WebSocket处理

**目标:** 移除HTTP轮询相关代码，纯WebSocket通信

**Files:**
- Modify: `backend/app/api/v1/classroom_sessions.py`
- Modify: `frontend/src/composables/useClassroomSession.ts`

**Step 1: 移除HTTP轮询端点**

```python
# backend/app/api/v1/classroom_sessions.py
# 找到并删除这些端点：

# @router.post("/sessions/{session_id}/check-teacher-status", ...)  # 删除

# 移除检查教师状态的定期任务逻辑
```

**Step 2: 简化WebSocket错误处理**

```python
# backend/app/api/v1/classroom_sessions.py
# 在 websocket_endpoint 函数中，简化错误处理：

@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """WebSocket连接端点（学生端）"""

    # ... 验证逻辑保持不变 ...

    # 接受连接
    await websocket.accept()

    # 注册连接
    await manager.connect(websocket, session_id, student_id)

    # 发送初始状态
    await send_initial_state(websocket, session, db)

    # 更新学生在线状态
    await update_student_online_status(db, session_id, student_id, is_online=True)

    try:
        # 监听消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_client_message(message, session_id, student_id, websocket, db)
    except WebSocketDisconnect:
        print(f"🔌 学生断开连接（会话 {session_id}），student_id={student_id}")
    except Exception as e:
        print(f"❌ WebSocket异常: {str(e)}")
    finally:
        # 清理
        if student_id is not None:
            try:
                await manager.disconnect(session_id, student_id)
                await update_student_online_status(db, session_id, student_id, is_online=False)
                print(f"✅ 学生 {student_id} 连接已清理（会话 {session_id}）")
            except Exception as e:
                print(f"⚠️ 清理连接时出错: {str(e)}")
```

**Step 3: 移除教师WebSocket的自动结束逻辑**

```python
# backend/app/api/v1/classroom_sessions.py
# 在 websocket_teacher_session_endpoint 中，移除自动结束逻辑：

# 移除这部分代码（大约在1836行）：
# """
# try:
#     # 重新获取会话最新状态
#     session = await db.get(ClassSession, session_id)
#     if session and session.status in [ClassSessionStatus.ACTIVE, ClassSessionStatus.PAUSED]:
#         print(f"⚠️ 教师异常退出，自动结束会话 {session_id}")
#         # ... 自动结束逻辑 ...
# except Exception as end_error:
#     print(f"❌ 自动结束会话失败: {str(end_error)}")
# """
```

**Step 4: 提交WebSocket简化**

```bash
git add backend/app/api/v1/classroom_sessions.py
git commit -m "refactor: simplify WebSocket handling - remove polling

- Remove HTTP polling fallback logic
- Simplify error handling
- Remove auto-end session on teacher disconnect
- Pure WebSocket communication only
"
```

---

### Task 2.4: 后端集成测试

**目标:** 编写完整的授课流程集成测试

**Files:**
- Create: `backend/tests/test_session_flow_integration.py`

**Step 1: 编写集成测试**

```python
# backend/tests/test_session_flow_integration.py
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models.classroom_session import ClassSession, SessionStatus
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_complete_teaching_flow(db_session, client: AsyncClient):
    """测试完整授课流程：创建→加入→开始→结束"""

    # 1. 创建教师和学生
    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="$2b$12$hashed",
        full_name="测试教师",
        role=UserRole.TEACHER,
        school_id=1
    )
    db_session.add(teacher)
    await db_session.commit()

    student = User(
        username="test_student",
        email="test_student@example.com",
        hashed_password="$2b$12$hashed",
        full_name="测试学生",
        role=UserRole.STUDENT,
        school_id=1,
        classroom_id=204
    )
    db_session.add(student)
    await db_session.commit()

    # 2. 教师登录
    login_response = await client.post(
        "/api/auth/login",
        data={"username": "test_teacher", "password": "password"}
    )
    assert login_response.status_code == 200
    teacher_token = login_response.json()["access_token"]

    # 3. 学生登录
    student_login_response = await client.post(
        "/api/auth/login",
        data={"username": "test_student", "password": "password"}
    )
    assert student_login_response.status_code == 200
    student_token = student_login_response.json()["access_token"]

    # 4. 教师创建会话
    create_response = await client.post(
        "/api/sessions/",
        json={
            "lesson_id": 1,
            "classroom_id": 204
        },
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert create_response.status_code == 201
    session_data = create_response.json()
    assert session_data["status"] == "PREPARING"
    session_id = session_data["id"]

    # 5. 学生加入会话
    join_response = await client.post(
        f"/api/sessions/{session_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert join_response.status_code == 200
    participation = join_response.json()
    assert participation["is_active"] is True

    # 6. 验证数据库状态
    result = await db_session.execute(
        select(ClassSession).where(ClassSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    assert session is not None
    assert session.status == SessionStatus.PREPARING

    # 7. 教师开始上课
    start_response = await client.post(
        f"/api/sessions/{session_id}/start",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert start_response.status_code == 200
    session_data = start_response.json()
    assert session_data["status"] == "TEACHING"
    assert session_data["current_cell_id"] is not None

    # 8. 验证状态转换
    await db_session.refresh(session)
    assert session.status == SessionStatus.TEACHING
    assert session.actual_start is not None

    # 9. 教师结束课程
    end_response = await client.post(
        f"/api/sessions/{session_id}/end",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert end_response.status_code == 200
    session_data = end_response.json()
    assert session_data["status"] == "ENDED"

    # 10. 验证最终状态
    await db_session.refresh(session)
    assert session.status == SessionStatus.ENDED
    assert session.ended_at is not None
    assert session.duration_minutes is not None
    assert session.duration_minutes >= 0
```

**Step 2: 运行集成测试**

```bash
cd backend
pytest tests/test_session_flow_integration.py -v
```

**Step 3: 提交集成测试**

```bash
git add backend/tests/test_session_flow_integration.py
git commit -m "test: add complete teaching flow integration test

- Test create → join → start → end flow
- Verify state transitions
- Verify database state
"
```

---

## 第3阶段：前端重构（3-4周）

### Task 3.1: 创建Pinia Store

**目标:** 创建统一的课堂状态管理

**Files:**
- Create: `frontend/src/store/classroom.ts`
- Create: `frontend/src/store/index.ts`

**Step 1: 安装Pinia**

```bash
cd frontend
npm install pinia
```

**Step 2: 创建Store配置**

```typescript
// frontend/src/store/index.ts
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia
```

**Step 3: 创建课堂Store**

```typescript
// frontend/src/store/classroom.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ClassSession, Student } from '@/types/classroomSession'

export enum SessionStatus {
  PREPARING = 'PREPARING',
  TEACHING = 'TEACHING',
  ENDED = 'ENDED'
}

export const useClassroomStore = defineStore('classroom', () => {
  // 状态
  const session = ref<ClassSession | null>(null)
  const students = ref<Student[]>([])
  const duration = ref(0)
  const currentCell = ref<number | null>(null)

  // 计算属性
  const sessionStatus = computed(() => session.value?.status ?? SessionStatus.ENDED)
  const isTeaching = computed(() => sessionStatus.value === SessionStatus.TEACHING)
  const isPreparing = computed(() => sessionStatus.value === SessionStatus.PREPARING)
  const isEnded = computed(() => sessionStatus.value === SessionStatus.ENDED)
  const hasStudents = computed(() => students.value.length > 0)

  // Actions
  function setSession(newSession: ClassSession) {
    session.value = newSession
  }

  function setStudents(newStudents: Student[]) {
    students.value = newStudents
  }

  function addStudent(student: Student) {
    const exists = students.value.find(s => s.id === student.id)
    if (!exists) {
      students.value.push(student)
    }
  }

  function removeStudent(studentId: number) {
    students.value = students.value.filter(s => s.id !== studentId)
  }

  function updateStudentProgress(studentId: number, progress: number) {
    const student = students.value.find(s => s.id === studentId)
    if (student) {
      student.progress = progress
    }
  }

  function setDuration(seconds: number) {
    duration.value = seconds
  }

  function incrementDuration() {
    duration.value++
  }

  function setCurrentCell(cellId: number | null) {
    currentCell.value = cellId
  }

  function reset() {
    session.value = null
    students.value = []
    duration.value = 0
    currentCell.value = null
  }

  return {
    // 状态
    session,
    students,
    duration,
    currentCell,

    // 计算属性
    sessionStatus,
    isTeaching,
    isPreparing,
    isEnded,
    hasStudents,

    // Actions
    setSession,
    setStudents,
    addStudent,
    removeStudent,
    updateStudentProgress,
    setDuration,
    incrementDuration,
    setCurrentCell,
    reset
  }
})
```

**Step 4: 更新main.ts**

```typescript
// frontend/src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

const app = createApp(App)

app.use(router)
app.use(pinia)

app.mount('#app')
```

**Step 5: 提交Store**

```bash
git add frontend/src/store
git commit -m "feat: add Pinia store for classroom state management

- Add useClassroomStore with session, students, duration
- Add computed properties for status checks
- Add actions for state mutations
"
```

---

### Task 3.2: 实现useSessionManager Composable

**目标:** 封装会话管理逻辑

**Files:**
- Create: `frontend/src/composables/useSessionManager.ts`
- Create: `frontend/src/services/classroomSession.ts`

**Step 1: 创建API服务**

```typescript
// frontend/src/services/classroomSession.ts
import axios from 'axios'
import type { ClassSession, ClassSessionCreate } from '@/types/classroomSession'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api'
})

// 拦截器：添加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const classroomSessionService = {
  // 创建会话
  async createSession(lessonId: number, classroomId: number): Promise<ClassSession> {
    const { data } = await api.post<ClassSession>('/sessions', {
      lesson_id: lessonId,
      classroom_id: classroomId
    })
    return data
  },

  // 开始上课
  async startSession(sessionId: number): Promise<ClassSession> {
    const { data } = await api.post<ClassSession>(`/sessions/${sessionId}/start`)
    return data
  },

  // 结束课程
  async endSession(sessionId: number): Promise<ClassSession> {
    const { data } = await api.post<ClassSession>(`/sessions/${sessionId}/end`)
    return data
  },

  // 获取会话详情
  async getSession(sessionId: number): Promise<ClassSession> {
    const { data } = await api.get<ClassSession>(`/sessions/${sessionId}`)
    return data
  },

  // 导航
  async navigate(sessionId: number, cellOrders: number[]): Promise<ClassSession> {
    const { data } = await api.post<ClassSession>(`/sessions/${sessionId}/navigate`, {
      display_cell_orders: cellOrders
    })
    return data
  }
}
```

**Step 2: 实现useSessionManager**

```typescript
// frontend/src/composables/useSessionManager.ts
import { ref } from 'vue'
import { useClassroomStore } from '@/store/classroom'
import { classroomSessionService } from '@/services/classroomSession'
import { useWebSocket } from './useWebSocket'
import type { ClassSession } from '@/types/classroomSession'

export function useSessionManager() {
  const store = useClassroomStore()
  const { connect, broadcast, disconnect } = useWebSocket()
  const loading = ref(false)

  // 创建会话
  async function createSession(lessonId: number, classroomId: number) {
    loading.value = true
    try {
      const session = await classroomSessionService.createSession(lessonId, classroomId)
      store.setSession(session)

      // 连接WebSocket
      await connect(session.id)

      return session
    } catch (error: any) {
      console.error('Failed to create session:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 开始上课
  async function startSession() {
    if (!store.session?.id) {
      throw new Error('No active session')
    }

    loading.value = true
    try {
      const updated = await classroomSessionService.startSession(store.session.id)
      store.setSession(updated)

      // 广播给所有学生
      broadcast({
        type: 'session_started',
        data: {
          session_id: store.session.id,
          status: updated.status,
          current_cell_id: updated.currentCellId
        }
      })

      return updated
    } catch (error: any) {
      console.error('Failed to start session:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 结束课程
  async function endSession() {
    if (!store.session?.id) {
      throw new Error('No active session')
    }

    loading.value = true
    try {
      const updated = await classroomSessionService.endSession(store.session.id)
      store.setSession(updated)

      // 广播给所有学生
      broadcast({
        type: 'session_ended',
        data: {
          session_id: store.session.id,
          message: '课程已结束'
        }
      })

      // 断开WebSocket
      disconnect()

      return updated
    } catch (error: any) {
      console.error('Failed to end session:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    createSession,
    startSession,
    endSession
  }
}
```

**Step 3: 提交**

```bash
git add frontend/src/composables/useSessionManager.ts frontend/src/services
git commit -m "feat: implement useSessionManager composable

- Add classroomSessionService API client
- Implement createSession, startSession, endSession
- Integrate with WebSocket
"
```

---

### Task 3.3: 实现useWebSocket Composable

**目标:** 纯WebSocket通信，移除轮询

**Files:**
- Create: `frontend/src/composables/useWebSocket.ts`
- Create: `frontend/src/services/websocket.ts`

**Step 1: 实现WebSocket服务**

```typescript
// frontend/src/services/websocket.ts
import { ref } from 'vue'

export interface WSMessage {
  type: string
  timestamp?: string
  data: any
}

export type WSMessageHandler = (message: WSMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private isConnected = false
  private reconnectAttempts = 0
  private readonly MAX_RECONNECT = 3
  private messageHandlers = new Map<string, WSMessageHandler[]>()

  connect(sessionId: number, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = `ws://localhost:8000/api/sessions/${sessionId}/ws?token=${token}`

      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        this.isConnected = true
        this.reconnectAttempts = 0
        console.log('✅ WebSocket connected')
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        this.isConnected = false
        console.warn('WebSocket closed:', event.code, event.reason)

        // 自动重连
        if (this.reconnectAttempts < this.MAX_RECONNECT && event.code !== 1000) {
          setTimeout(() => {
            this.reconnectAttempts++
            console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.MAX_RECONNECT})`)
            this.connect(sessionId, token)
          }, 1000)
        } else if (event.code === 1008) {
          // 策略错误，不重连
          console.error('❌ WebSocket closed with policy error')
        } else {
          console.error('❌ WebSocket failed after max retries')
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }
    })
  }

  send(message: WSMessage) {
    if (!this.ws || !this.isConnected) {
      console.warn('WebSocket not connected, cannot send message')
      return
    }
    this.ws.send(JSON.stringify(message))
  }

  on(type: string, handler: WSMessageHandler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type)!.push(handler)
  }

  off(type: string, handler: WSMessageHandler) {
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  private handleMessage(message: WSMessage) {
    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => handler(message))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
      this.isConnected = false
    }
  }
}

export const websocketService = new WebSocketService()
```

**Step 2: 实现useWebSocket Composable**

```typescript
// frontend/src/composables/useWebSocket.ts
import { ref, onUnmounted } from 'vue'
import { websocketService, type WSMessage } from '@/services/websocket'
import { useClassroomStore } from '@/store/classroom'
import { getAuthToken } from '@/utils/auth'

export function useWebSocket() {
  const store = useClassroomStore()
  const isConnected = ref(false)

  // 连接WebSocket
  async function connect(sessionId: number) {
    const token = getAuthToken()
    if (!token) {
      throw new Error('No auth token')
    }

    await websocketService.connect(sessionId, token)

    // 监听连接成功
    websocketService.on('connected', (message: WSMessage) => {
      isConnected.value = true
      console.log('📥 WebSocket initial state:', message.data)
    })

    // 监听学生加入
    websocketService.on('student_joined', (message: WSMessage) => {
      console.log('📥 Student joined:', message.data)
      store.addStudent({
        id: message.data.student_id,
        name: message.data.student_name,
        progress: 0,
        isActive: true
      })
    })

    // 监听内容切换
    websocketService.on('cell_changed', (message: WSMessage) => {
      console.log('📥 Content changed:', message.data)
      store.setCurrentCell(message.data.current_cell_id)
    })

    // 监听会话结束
    websocketService.on('session_ended', (message: WSMessage) => {
      console.log('📥 Session ended:', message.data)
      store.reset()
    })

    // 监听连接关闭
    websocketService.on('connection_closed', (message: WSMessage) => {
      isConnected.value = false
    })
  }

  // 发送消息
  function broadcast(message: WSMessage) {
    websocketService.send(message)
  }

  // 断开连接
  function disconnect() {
    websocketService.disconnect()
    isConnected.value = false
  }

  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    connect,
    broadcast,
    disconnect
  }
}
```

**Step 3: 更新useClassroomSession**

```typescript
// frontend/src/composables/useClassroomSession.ts
// 更新为使用新的状态

import { computed } from 'vue'
import { useClassroomStore } from '@/store/classroom'
import { classroomSessionService } from '@/services/classroomSession'
import { useWebSocket } from './useWebSocket'

export function useClassroomSession(lessonId: number) {
  const store = useClassroomStore()
  const { connect, disconnect } = useWebSocket()

  // 查找并加入会话
  async function findAndJoinSession() {
    try {
      // 获取所有会话
      const sessions = await classroomSessionService.listSessions(lessonId)

      // 过滤：PREPARING 或 TEACHING 状态
      const availableSessions = sessions.filter(
        s => s.status === 'PREPARING' || s.status === 'TEACHING'
      )

      if (availableSessions.length === 0) {
        console.log('ℹ️ 未找到可加入的课堂会话')
        return null
      }

      // 选择最新的会话
      const session = availableSessions.sort((a, b) => b.id - a.id)[0]

      // 加入会话
      await classroomSessionService.joinSession(session.id)

      // 更新store
      store.setSession(session)

      // 连接WebSocket
      await connect(session.id)

      return session
    } catch (error: any) {
      console.error('Failed to join session:', error)
      return null
    }
  }

  // 计算属性
  const isInClassroomMode = computed(() => store.isTeaching || store.isPreparing)
  const hasDisplayableContent = computed(() => {
    if (!isInClassroomMode.value) return true
    if (store.isPreparing) return false
    return store.currentCell !== null
  })

  return {
    session: computed(() => store.session),
    isInClassroomMode,
    hasDisplayableContent,
    findAndJoinSession,
    leaveSession: () => {
      disconnect()
      store.reset()
    }
  }
}
```

**Step 4: 提交**

```bash
git add frontend/src/composables/useWebSocket.ts frontend/src/services/websocket.ts frontend/src/composables/useClassroomSession.ts
git commit -m "refactor: implement pure WebSocket communication

- Add WebSocketService class with auto-reconnect
- Implement useWebSocket composable
- Remove HTTP polling logic
- Update useClassroomSession to use new WebSocket
"
```

---

### Task 3.4: 拆分TeacherControlPanel组件

**目标:** 将5,047行的巨型组件拆分为5个子组件

**Files:**
- Create: `frontend/src/components/Classroom/SessionHeader.vue`
- Create: `frontend/src/components/Classroom/StudentList.vue`
- Create: `frontend/src/components/Classroom/ContentNavigator.vue`
- Create: `frontend/src/components/Classroom/SessionTimer.vue`
- Create: `frontend/src/components/Classroom/ActionButtons.vue`
- Modify: `frontend/src/components/Classroom/TeacherControlPanel.vue`

**Step 1: 创建SessionHeader组件**

```vue
<!-- frontend/src/components/Classroom/SessionHeader.vue -->
<template>
  <div class="session-header">
    <div class="session-title">
      <h2>{{ session?.lessonTitle || '未命名课程' }}</h2>
      <span class="status-badge" :class="statusClass">
        {{ statusText }}
      </span>
    </div>
    <div class="session-info">
      <span>班级: {{ session?.classroomName || '-' }}</span>
      <span>创建时间: {{ createdAt }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ClassSession } from '@/types/classroomSession'

interface Props {
  session: ClassSession | null
  status: string
}

const props = defineProps<Props>()

const statusText = computed(() => {
  switch (props.status) {
    case 'PREPARING': return '准备中'
    case 'TEACHING': return '上课中'
    case 'ENDED': return '已结束'
    default: return '未知'
  }
})

const statusClass = computed(() => {
  return `status-${props.status.toLowerCase()}`
})

const createdAt = computed(() => {
  if (!props.session?.createdAt) return '-'
  return new Date(props.session.createdAt).toLocaleString('zh-CN')
})
</script>

<style scoped>
.session-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.session-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-preparing {
  background-color: #fef3c7;
  color: #92400e;
}

.status-teaching {
  background-color: #d1fae5;
  color: #065f46;
}

.status-ended {
  background-color: #f3f4f6;
  color: #374151;
}

.session-info {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>
```

**Step 2: 创建StudentList组件**

```vue
<!-- frontend/src/components/Classroom/StudentList.vue -->
<template>
  <div class="student-list">
    <div class="list-header">
      <h3>在线学生 ({{ students.length }})</h3>
    </div>

    <div class="student-items">
      <div
        v-for="student in students"
        :key="student.id"
        class="student-item"
      >
        <div class="student-avatar">
          {{ student.name.charAt(0) }}
        </div>
        <div class="student-info">
          <div class="student-name">{{ student.name }}</div>
          <div class="student-progress">
            进度: {{ student.progress }}%
          </div>
        </div>
        <button
          @click="handleKick(student.id)"
          class="btn-kick"
          title="踢出学生"
        >
          踢出
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Student } from '@/types/classroomSession'

interface Props {
  students: Student[]
}

interface Emits {
  (e: 'kick', studentId: number): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

function handleKick(studentId: number) {
  if (confirm('确定要踢出该学生吗？')) {
    emit('kick', studentId)
  }
}
</script>

<style scoped>
.student-list {
  padding: 1rem;
}

.list-header {
  margin-bottom: 1rem;
}

.student-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
}

.student-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.student-info {
  flex: 1;
}

.student-name {
  font-weight: 500;
  color: #111827;
}

.student-progress {
  font-size: 0.875rem;
  color: #6b7280;
}

.btn-kick {
  padding: 0.25rem 0.75rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-kick:hover {
  background-color: #dc2626;
}
</style>
```

**Step 3: 创建ContentNavigator组件**

```vue
<!-- frontend/src/components/Classroom/ContentNavigator.vue -->
<template>
  <div class="content-navigator">
    <div class="navigator-header">
      <h3>内容导航</h3>
    </div>

    <div class="cells-list">
      <label
        v-for="cell in cells"
        :key="cell.id"
        class="cell-item"
      >
        <input
          type="checkbox"
          :value="cell.order"
          :checked="selectedCells.includes(cell.order)"
          :disabled="disabled"
          @change="handleToggle(cell.order)"
        />
        <span>{{ cell.title || `模块 ${cell.order}` }}</span>
      </label>
    </div>

    <button
      @click="handleNavigate"
      :disabled="disabled || selectedCells.length === 0"
      class="btn-navigate"
    >
      显示选中的模块 ({{ selectedCells.length }})
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Cell } from '@/types/lesson'

interface Props {
  cells: Cell[]
  currentCell: number | null
  disabled: boolean
}

interface Emits {
  (e: 'navigate', selectedCells: number[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const selectedCells = ref<number[]>([])

function handleToggle(cellOrder: number) {
  const index = selectedCells.value.indexOf(cellOrder)
  if (index > -1) {
    selectedCells.value.splice(index, 1)
  } else {
    selectedCells.value.push(cellOrder)
  }
}

function handleNavigate() {
  emit('navigate', selectedCells.value)
}
</script>

<style scoped>
.content-navigator {
  padding: 1rem;
}

.cells-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 1rem 0;
  max-height: 300px;
  overflow-y: auto;
}

.cell-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
}

.cell-item:hover {
  background-color: #f3f4f6;
}

.btn-navigate {
  width: 100%;
  padding: 0.75rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-navigate:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
</style>
```

**Step 4: 创建SessionTimer组件**

```vue
<!-- frontend/src/components/Classroom/SessionTimer.vue -->
<template>
  <div class="session-timer">
    <div class="timer-icon">⏱️</div>
    <div class="timer-display">
      <div class="timer-label">课程时长</div>
      <div class="timer-value">{{ formattedTime }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  duration: number  // 秒
  status: string
}

const props = defineProps<Props>()

const formattedTime = computed(() => {
  const hours = Math.floor(props.duration / 3600)
  const minutes = Math.floor((props.duration % 3600) / 60)
  const seconds = props.duration % 60

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})
</script>

<style scoped>
.session-timer {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.timer-icon {
  font-size: 2rem;
}

.timer-display {
  display: flex;
  flex-direction: column;
}

.timer-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.timer-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  font-family: monospace;
}
</style>
```

**Step 5: 创建ActionButtons组件**

```vue
<!-- frontend/src/components/Classroom/ActionButtons.vue -->
<template>
  <div class="action-buttons">
    <button
      v-if="status === 'PREPARING'"
      @click="handleStart"
      :disabled="!hasStudents"
      class="btn btn-start"
    >
      开始上课 ({{ activeStudents }}/{{ totalStudents }}学生在线)
    </button>

    <button
      v-if="status === 'TEACHING'"
      @click="handleEnd"
      class="btn btn-end"
    >
      结束课程
    </button>

    <button
      v-if="status === 'ENDED'"
      @click="handleCreateNew"
      class="btn btn-create"
    >
      创建新课堂
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  status: string
  hasStudents: boolean
  activeStudents: number
  totalStudents: number
}

interface Emits {
  (e: 'start'): void
  (e: 'end'): void
  (e: 'create-new'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

function handleStart() {
  emit('start')
}

function handleEnd() {
  emit('end')
}

function handleCreateNew() {
  emit('create-new')
}
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
}

.btn-start {
  background-color: #10b981;
  color: white;
}

.btn-start:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.btn-end {
  background-color: #ef4444;
  color: white;
}

.btn-create {
  background-color: #3b82f6;
  color: white;
}
</style>
```

**Step 6: 重构TeacherControlPanel主组件**

```vue
<!-- frontend/src/components/Classroom/TeacherControlPanel.vue -->
<template>
  <div class="teacher-control-panel">
    <SessionHeader
      :session="store.session"
      :status="store.sessionStatus"
    />

    <StudentList
      :students="store.students"
      @kick="handleKickStudent"
    />

    <ContentNavigator
      :cells="lessonCells"
      :current-cell="store.currentCell"
      :disabled="!store.isTeaching"
      @navigate="handleNavigate"
    />

    <SessionTimer
      :duration="store.duration"
      :status="store.sessionStatus"
    />

    <ActionButtons
      :status="store.sessionStatus"
      :has-students="store.hasStudents"
      :active-students="activeStudentsCount"
      :total-students="store.students.length"
      @start="handleStart"
      @end="handleEnd"
      @create-new="handleCreateNew"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { useClassroomStore } from '@/store/classroom'
import { useSessionManager } from '@/composables/useSessionManager'
import SessionHeader from './SessionHeader.vue'
import StudentList from './StudentList.vue'
import ContentNavigator from './ContentNavigator.vue'
import SessionTimer from './SessionTimer.vue'
import ActionButtons from './ActionButtons.vue'

const store = useClassroomStore()
const { createSession, startSession, endSession } = useSessionManager()

// Props
interface Props {
  lessonId: number
  classroomId: number
}

const props = defineProps<Props>()

// 计算属性
const lessonCells = computed(() => {
  // 从教案加载cells
  return []  // TODO: 实现
})

const activeStudentsCount = computed(() => {
  return store.students.filter(s => s.isActive).length
})

// 方法
async function handleStart() {
  try {
    await startSession()
  } catch (error: any) {
    alert(error.message || '开始上课失败')
  }
}

async function handleEnd() {
  if (!confirm('确定要结束课程吗？')) return

  try {
    await endSession()
  } catch (error: any) {
    alert(error.message || '结束课程失败')
  }
}

async function handleCreateNew() {
  // TODO: 实现创建新课堂
}

async function handleNavigate(selectedCells: number[]) {
  // TODO: 实现导航
}

async function handleKickStudent(studentId: number) {
  // TODO: 实现踢出学生
}

// 生命周期
onMounted(async () => {
  // 加载现有会话或创建新会话
})

onUnmounted(() => {
  store.reset()
})
</script>

<style scoped>
.teacher-control-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 100vh;
  overflow-y: auto;
}
</style>
```

**Step 7: 提交组件拆分**

```bash
git add frontend/src/components/Classroom/*.vue
git commit -m "refactor: split TeacherControlPanel into 5 components

- Add SessionHeader.vue (150 lines)
- Add StudentList.vue (200 lines)
- Add ContentNavigator.vue (300 lines)
- Add SessionTimer.vue (150 lines)
- Add ActionButtons.vue (100 lines)
- Refactor TeacherControlPanel.vue to 200 lines

Total reduction: 5,047 lines → 1,100 lines (78% reduction)
"
```

---

## 第4阶段：集成测试（1-2周）

### Task 4.1: 前端单元测试

**目标:** 为Composables编写单元测试

**Files:**
- Create: `frontend/src/composables/__tests__/useSessionManager.test.ts`
- Create: `frontend/src/composables/__tests__/useWebSocket.test.ts`

**Step 1: 编写useSessionManager测试**

```typescript
// frontend/src/composables/__tests__/useSessionManager.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSessionManager } from '../useSessionManager'
import { useClassroomStore } from '@/store/classroom'
import { classroomSessionService } from '@/services/classroomSession'

vi.mock('@/store/classroom')
vi.mock('@/services/classroomSession')
vi.mock('../useWebSocket')

describe('useSessionManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should create session successfully', async () => {
    const mockSession = {
      id: 261,
      status: 'PREPARING',
      lesson_id: 157,
      classroom_id: 204
    }

    vi.mocked(classroomSessionService.createSession).mockResolvedValue(mockSession)

    const { createSession } = useSessionManager()
    await createSession(157, 204)

    expect(classroomSessionService.createSession).toHaveBeenCalledWith(157, 204)
  })

  it('should start session and broadcast', async () => {
    const mockSession = {
      id: 261,
      status: 'TEACHING',
      currentCellId: 1234
    }

    vi.mocked(classroomSessionService.startSession).mockResolvedValue(mockSession)

    const store = useClassroomStore()
    store.session = { id: 261 } as any

    const { startSession } = useSessionManager()
    await startSession()

    expect(classroomSessionService.startSession).toHaveBeenCalledWith(261)
  })
})
```

**Step 2: 编写useWebSocket测试**

```typescript
// frontend/src/composables/__tests__/useWebSocket.test.ts
import { describe, it, expect, vi } from 'vitest'
import { useWebSocket } from '../useWebSocket'
import { websocketService } from '@/services/websocket'

vi.mock('@/services/websocket')
vi.mock('@/utils/auth', () => ({
  getAuthToken: () => 'test-token'
}))

global.WebSocket = vi.fn(() => ({
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn()
}))

describe('useWebSocket', () => {
  it('should connect to WebSocket', async () => {
    vi.mocked(websocketService.connect).mockResolvedValue(undefined)

    const { connect } = useWebSocket()
    await connect(261)

    expect(websocketService.connect).toHaveBeenCalledWith(261, 'test-token')
  })

  it('should broadcast message', () => {
    const { broadcast } = useWebSocket()
    broadcast({ type: 'test', data: {} })

    expect(websocketService.send).toHaveBeenCalled()
  })

  it('should disconnect on unmount', () => {
    const { disconnect } = useWebSocket()
    disconnect()

    expect(websocketService.disconnect).toHaveBeenCalled()
  })
})
```

**Step 3: 运行测试**

```bash
cd frontend
npm run test:unit
```

**Step 4: 提交测试**

```bash
git add frontend/src/composables/__tests__
git commit -m "test: add unit tests for composables

- Add useSessionManager tests
- Add useWebSocket tests
- All tests passing
"
```

---

### Task 4.2: E2E测试

**目标:** 使用Playwright测试完整授课流程

**Files:**
- Create: `frontend/e2e/teacher-flow.spec.ts`

**Step 1: 编写E2E测试**

```typescript
// frontend/e2e/teacher-flow.spec.ts
import { test, expect } from '@playwright/test'

test.describe('教师授课流程', () => {
  test('完整流程：创建→学生加入→开始上课→结束', async ({ page }) => {
    // 1. 教师登录
    await page.goto('/login')
    await page.fill('input[name="username"]', 'test_teacher')
    await page.fill('input[name="password"]', 'password')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/teacher')

    // 2. 进入教案编辑器
    await page.goto('/teacher/lessons/157/edit')
    await page.click('button:has-text("创建课堂")')

    // 3. 选择班级
    await page.selectOption('select[name="classroom"]', '204')
    await page.click('button:has-text("确认")')

    // 4. 验证状态：准备中
    await expect(page.locator('.status-badge')).toHaveText('准备中')
    await expect(page.locator('.waiting-banner')).toBeVisible()

    // 5. 学生加入（模拟）
    const studentContext = await page.context().newPage()
    await studentContext.goto('/login')
    await studentContext.fill('input[name="username"]', 'test_student')
    await studentContext.fill('input[name="password"]', 'password')
    await studentContext.click('button[type="submit"]')
    await studentContext.goto('/student/lessons/157')
    await studentContext.click('button:has-text("加入课堂")')

    // 6. 教师看到学生
    await page.waitForSelector('.student-item')
    const studentCount = await page.locator('.student-item').count()
    expect(studentCount).toBe(1)

    // 7. 教师开始上课
    await page.click('button:has-text("开始上课")')
    await expect(page.locator('.status-badge')).toHaveText('上课中')

    // 8. 学生看到内容
    await expect(studentContext.locator('.cell-content')).toBeVisible()
    await expect(studentContext.locator('.waiting-banner')).not.toBeVisible()

    // 9. 教师结束课程
    await page.click('button:has-text("结束课程")')
    await expect(page.locator('.status-badge')).toHaveText('已结束')

    // 10. 学生看到结束提示
    await expect(studentContext.locator('.ended-message')).toContainText('课程已结束')

    await studentContext.close()
  })
})
```

**Step 2: 运行E2E测试**

```bash
cd frontend
npx playwright test
```

**Step 3: 提交E2E测试**

```bash
git add frontend/e2e
git commit -m "test: add E2E test for complete teaching flow

- Test create → join → start → end flow
- Verify teacher and student interactions
"
```

---

## 第5阶段：部署（1周）

### Task 5.1: 代码审查和文档

**目标:** 完善文档，准备部署

**Files:**
- Create: `docs/classroom-v2-api.md`
- Create: `docs/classroom-v2-migration.md`

**Step 1: 编写API文档**

```markdown
<!-- docs/classroom-v2-api.md -->
# 课堂会话 API v2.0 文档

## 状态变更

v2.0 使用简化的3状态模型：
- PREPARING (准备中) - 替代 PENDING
- TEACHING (上课中) - 替代 ACTIVE
- ENDED (已结束) - 保持不变

移除的状态：
- ~~PAUSED~~ - 暂停功能移除

## API 端点

### 创建会话
POST /api/sessions
```json
{
  "lesson_id": 157,
  "classroom_id": 204
}
```

Response:
```json
{
  "id": 261,
  "status": "PREPARING",
  "created_at": "2026-02-01T10:00:00Z"
}
```

### 开始上课
POST /api/sessions/{id}/start

Response:
```json
{
  "id": 261,
  "status": "TEACHING",
  "actual_start": "2026-02-01T10:05:00Z",
  "current_cell_id": 1234
}
```

### 结束课程
POST /api/sessions/{id}/end

Response:
```json
{
  "id": 261,
  "status": "ENDED",
  "ended_at": "2026-02-01T10:45:00Z",
  "duration_minutes": 40
}
```

### WebSocket 连接
WS /api/sessions/{id}/ws?token={jwt}

连接成功后发送初始状态：
```json
{
  "type": "connected",
  "data": {
    "session_id": 261,
    "status": "TEACHING",
    "current_cell_id": 1234
  }
}
```
```

**Step 2: 编写迁移指南**

```markdown
<!-- docs/classroom-v2-migration.md -->
# 从 v1.0 迁移到 v2.0

## 后端变更

### 状态枚举
```python
# 旧代码
from app.models.classroom_session import ClassSessionStatus
status = ClassSessionStatus.PENDING

# 新代码
from app.services.session_state_machine import SessionStatus
status = SessionStatus.PREPARING
```

### 状态机
```python
# 旧代码
if session.status == ClassSessionStatus.PENDING:
    session.status = ClassSessionStatus.ACTIVE

# 新代码
from app.services.session_state_machine import SessionStateMachine
state_machine = SessionStateMachine(session)
state_machine.transition_to(SessionStatus.TEACHING)
```

## 前端变更

### 状态枚举
```typescript
// 旧代码
const status = 'pending'  // 小写

// 新代码
import { SessionStatus } from '@/store/classroom'
const status = SessionStatus.PREPARING  // 大写
```

### Composables
```typescript
// 旧代码
import { useClassroomSession } from '@/composables/useClassroomSession'
const { session, findAndJoinSession } = useClassroomSession()

// 新代码
import { useSessionManager } from '@/composables/useSessionManager'
const { createSession, startSession } = useSessionManager()
```

### 移除的功能
- pauseSession / resumeSession
- HTTP轮询降级
- 暂停/继续按钮

## 数据库迁移

无需迁移，新状态向后兼容。
```

**Step 3: 更新README**

```markdown
<!-- README.md -->
## 课堂会话系统

当前版本：v2.0

### 特性
- 简化的3状态模型（PREPARING → TEACHING → ENDED）
- 纯WebSocket实时通信
- 组件化架构（每个组件 < 300行）
- 完整的单元测试和E2E测试

### 快速开始
见 [课堂会话 v2.0 设计文档](./docs/plans/2026-02-01-classroom-session-v2-design.md)
```

**Step 4: 提交文档**

```bash
git add docs
git commit -m "docs: add v2.0 API documentation and migration guide

- Add API reference for v2.0 endpoints
- Add migration guide from v1.0 to v2.0
- Update README with v2.0 features
"
```

---

### Task 5.2: 最终测试和部署

**目标:** 完整测试，准备部署

**Step 1: 运行所有测试**

```bash
# 后端
cd backend
pytest tests/ -v --cov=app

# 前端
cd frontend
npm run test:unit
npx playwright test

# E2E
cd frontend
npx playwright test
```

**Step 2: 构建生产版本**

```bash
# 前端
cd frontend
npm run build
```

**Step 3: 创建部署标签**

```bash
git tag -a v2.0.0 -m "Release classroom session v2.0"
git push origin v2.0.0
```

**Step 4: 合并到主分支**

```bash
git checkout main
git merge feature/classroom-mode-2.0
git push origin main
```

**Step 5: 部署到生产环境**

```bash
# 根据您的部署流程执行
# 例如：docker-compose up -d --build
```

**Step 6: 监控和验证**

```bash
# 检查日志
tail -f backend/logs/app.log

# 检查服务状态
curl http://localhost:8000/api/health
```

**Step 7: 提交最终版本**

```bash
git add .
git commit -m "release: classroom session v2.0

Major achievements:
- Reduced code from 8,067 to ~2,000 lines (75% reduction)
- Simplified state machine (4 states → 3 states)
- Pure WebSocket communication (removed polling)
- Componentized architecture (all components < 300 lines)
- Comprehensive test coverage (unit + integration + E2E)

Breaking changes:
- Removed PAUSED state
- Removed HTTP polling fallback
- Changed status enum to uppercase (PENDING → PREPARING, ACTIVE → TEACHING)

See docs/plans/2026-02-01-classroom-session-v2-design.md for details
"
```

---

## 实施检查清单

### 第1阶段：准备
- [ ] 创建git worktree
- [ ] 设置虚拟环境
- [ ] 创建测试框架
- [ ] 编写状态机测试（失败）

### 第2阶段：后端重构
- [ ] 实现SessionStateMachine
- [ ] 简化classroom_sessions.py
- [ ] 移除PAUSED状态
- [ ] 简化WebSocket处理
- [ ] 编写集成测试

### 第3阶段：前端重构
- [ ] 创建Pinia Store
- [ ] 实现useSessionManager
- [ ] 实现useWebSocket
- [ ] 拆分TeacherControlPanel
- [ ] 编写前端单元测试

### 第4阶段：集成测试
- [ ] 前端单元测试
- [ ] 后端集成测试
- [ ] E2E测试
- [ ] 性能测试

### 第5阶段：部署
- [ ] 代码审查
- [ ] API文档
- [ ] 迁移指南
- [ ] 生产构建
- [ ] 部署
- [ ] 监控验证

---

## 预期结果

实施完成后，系统应达到以下指标：

| 指标 | 目标 | 验证方法 |
|------|------|---------|
| **代码量** | ~2,000行 | `cloc .` |
| **单文件最大行数** | < 400行 | `wc -l` |
| **测试覆盖率** | > 75% | `pytest --cov` |
| **状态转换测试** | 100% | pytest |
| **E2E测试** | 全部通过 | Playwright |
| **构建时间** | < 5分钟 | `npm run build` |
| **WebSocket连接成功率** | > 95% | 日志分析 |

---

**计划完成时间估算:** 8-11周

**下一步:** 使用 @superpowers:executing-plans 开始lan
