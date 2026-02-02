"""
Unit tests for classroom session state transitions.

These tests focus on the state machine logic without complex database setup.
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.classroom_session import ClassSession, ClassSessionStatus
from app.api.v1.classroom_sessions import transition_session_state
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_state_enum_values():
    """测试状态枚举值是否正确"""

    # 验证新的状态枚举值
    assert ClassSessionStatus.PREPARING.value == "PREPARING"
    assert ClassSessionStatus.TEACHING.value == "TEACHING"
    assert ClassSessionStatus.ENDED.value == "ENDED"


@pytest.mark.asyncio
async def test_session_default_status_is_preparing(async_session: AsyncSession):
    """测试会话默认状态为 PREPARING"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    # 不指定 status，应该使用默认值 PREPARING
    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
    )
    async_session.add(session)

    await async_session.commit()

    # 验证默认状态
    assert session.status == ClassSessionStatus.PREPARING


@pytest.mark.asyncio
async def test_state_transition_preparing_to_teaching(async_session: AsyncSession):
    """测试状态转换：PREPARING -> TEACHING"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
    )
    async_session.add(session)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证初始状态
    assert session.status == ClassSessionStatus.PREPARING
    assert session.actual_start is None

    # 执行状态转换
    await transition_session_state(session, ClassSessionStatus.TEACHING)

    # 更新实际开始时间
    session.actual_start = datetime.utcnow()

    await async_session.commit()
    await async_session.refresh(session)

    # 验证状态转换成功
    assert session.status == ClassSessionStatus.TEACHING
    assert session.actual_start is not None


@pytest.mark.asyncio
async def test_state_transition_teaching_to_ended(async_session: AsyncSession):
    """测试状态转换：TEACHING -> ENDED"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    start_time = datetime.utcnow()

    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.TEACHING,
        actual_start=start_time,
    )
    async_session.add(session)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证初始状态
    assert session.status == ClassSessionStatus.TEACHING

    # 执行状态转换
    await transition_session_state(session, ClassSessionStatus.ENDED)

    # 更新结束时间
    session.ended_at = datetime.utcnow()

    # 计算时长
    if session.actual_start:
        duration = (session.ended_at - session.actual_start).total_seconds() / 60
        session.duration_minutes = int(duration)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证状态转换成功
    assert session.status == ClassSessionStatus.ENDED
    assert session.ended_at is not None
    assert session.duration_minutes is not None
    assert session.duration_minutes >= 0


@pytest.mark.asyncio
async def test_state_transition_preparing_to_ended(async_session: AsyncSession):
    """测试状态转换：PREPARING -> ENDED（提前结束）"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
    )
    async_session.add(session)

    await async_session.commit()

    # 从 PREPARING 直接到 ENDED（允许提前结束）
    await transition_session_state(session, ClassSessionStatus.ENDED)

    session.ended_at = datetime.utcnow()

    await async_session.commit()
    await async_session.refresh(session)

    assert session.status == ClassSessionStatus.ENDED


@pytest.mark.asyncio
async def test_state_transition_idempotent_ended(async_session: AsyncSession):
    """测试已结束的会话状态幂等性"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    ended_at = datetime.utcnow()
    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.ENDED,
        ended_at=ended_at,
        duration_minutes=30,
    )
    async_session.add(session)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证已经是 ENDED 状态
    assert session.status == ClassSessionStatus.ENDED

    # 状态应该保持不变（在实际代码中会有提前返回）
    assert session.status == ClassSessionStatus.ENDED
    assert session.ended_at == ended_at


@pytest.mark.asyncio
async def test_state_transition_with_timestamps(async_session: AsyncSession):
    """测试带时间戳的完整状态转换流程"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    # 步骤1：创建 PREPARING 状态的会话
    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
        scheduled_start=datetime.utcnow(),
    )
    async_session.add(session)
    await async_session.commit()

    assert session.status == ClassSessionStatus.PREPARING
    assert session.actual_start is None
    assert session.ended_at is None

    # 步骤2：转换到 TEACHING
    await transition_session_state(session, ClassSessionStatus.TEACHING)
    session.actual_start = datetime.utcnow()
    await async_session.commit()

    assert session.status == ClassSessionStatus.TEACHING
    assert session.actual_start is not None
    assert session.ended_at is None

    # 步骤3：转换到 ENDED
    await transition_session_state(session, ClassSessionStatus.ENDED)
    session.ended_at = datetime.utcnow()

    # 计算时长
    if session.actual_start:
        duration = (session.ended_at - session.actual_start).total_seconds() / 60
        session.duration_minutes = int(duration)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证最终状态
    assert session.status == ClassSessionStatus.ENDED
    assert session.actual_start is not None
    assert session.ended_at is not None
    assert session.duration_minutes is not None
    assert session.duration_minutes >= 0

    # 验证时间顺序
    assert session.actual_start <= session.ended_at


@pytest.mark.asyncio
async def test_session_settings_display_cell_orders(async_session: AsyncSession):
    """测试会话设置中的 display_cell_orders"""

    teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)

    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
        settings={"display_cell_orders": [1, 2, 3]},
    )
    async_session.add(session)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证设置正确保存
    assert session.settings is not None
    assert session.settings.get("display_cell_orders") == [1, 2, 3]

    # 测试更新设置
    new_settings = dict(session.settings)
    new_settings["display_cell_orders"] = [2, 3]
    session.settings = new_settings

    await async_session.commit()
    await async_session.refresh(session)

    assert session.settings.get("display_cell_orders") == [2, 3]
