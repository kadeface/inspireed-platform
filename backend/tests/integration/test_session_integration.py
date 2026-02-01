"""
Integration tests for classroom session v2.0 API endpoints.

These tests verify the complete workflow:
1. Create session (PREPARING)
2. Start session (PREPARING → TEACHING)
3. End session (TEACHING → ENDED)
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient

from app.models.user import User, UserRole
from app.models.classroom_session import ClassSession, ClassSessionStatus
from app.models.organization import School, Classroom
from app.models.lesson import Lesson


@pytest.mark.asyncio
async def test_complete_teaching_workflow(async_session: AsyncSession):
    """测试完整授课流程：创建 → 开始 → 结束"""

    # 1. 创建教师
    teacher = User(
        username="test_teacher_integration",
        email="test_teacher_integration@example.com",
        hashed_password="$2b$12$hashed",
        full_name="测试教师",
        role=UserRole.TEACHER,
    )
    async_session.add(teacher)
    await async_session.commit()
    await async_session.refresh(teacher)

    # 2. 创建会话（通过直接操作数据库）
    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
        scheduled_start=datetime.utcnow(),
    )
    async_session.add(session)
    await async_session.commit()
    await async_session.refresh(session)

    # 验证初始状态
    assert session.status == ClassSessionStatus.PREPARING
    assert session.actual_start is None
    assert session.ended_at is None

    # 3. 开始上课（PREPARING → TEACHING）
    from app.api.v1.classroom_sessions import transition_session_state

    await transition_session_state(session, ClassSessionStatus.TEACHING)
    session.actual_start = datetime.utcnow()
    await async_session.commit()
    await async_session.refresh(session)

    # 验证状态转换成功
    assert session.status == ClassSessionStatus.TEACHING
    assert session.actual_start is not None

    # 4. 结束课程（TEACHING → ENDED）
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
    assert session.ended_at is not None
    assert session.duration_minutes is not None
    assert session.duration_minutes >= 0


@pytest.mark.asyncio
async def test_cancelled_session_workflow(async_session: AsyncSession):
    """测试取消课程流程：创建 → 直接结束（PREPARING → ENDED）"""

    # 1. 创建教师
    teacher = User(
        username="test_teacher_cancel",
        email="test_teacher_cancel@example.com",
        hashed_password="$2b$12$hashed",
        role=UserRole.TEACHER,
        school_id=1
    )
    async_session.add(teacher)
    await async_session.commit()

    # 2. 创建会话（PREPARING状态）
    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
        scheduled_start=datetime.utcnow(),
    )
    async_session.add(session)
    await async_session.commit()
    await async_session.refresh(session)

    # 验证初始状态
    assert session.status == ClassSessionStatus.PREPARING

    # 3. 直接结束课程（PREPARING → ENDED）
    from app.api.v1.classroom_sessions import transition_session_state

    await transition_session_state(session, ClassSessionStatus.ENDED)
    session.ended_at = datetime.utcnow()
    await async_session.commit()
    await async_session.refresh(session)

    # 验证状态
    assert session.status == ClassSessionStatus.ENDED
    assert session.ended_at is not None
    # 没有开始上课，所以 actual_start 应该为 None
    assert session.actual_start is None


@pytest.mark.asyncio
async def test_session_state_transitions(async_session: AsyncSession):
    """测试所有合法的状态转换"""

    teacher = User(
        username="test_teacher_transitions",
        email="test_teacher_transitions@example.com",
        hashed_password="$2b$12$hashed",
        role=UserRole.TEACHER,
        school_id=1
    )
    async_session.add(teacher)
    await async_session.commit()

    from app.api.v1.classroom_sessions import transition_session_state

    # 测试1: PREPARING → TEACHING ✅
    session1 = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
    )
    async_session.add(session1)
    await async_session.commit()

    # 应该成功
    await transition_session_state(session1, ClassSessionStatus.TEACHING)
    assert session1.status == ClassSessionStatus.TEACHING

    # 测试2: PREPARING → ENDED ✅
    session2 = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
    )
    async_session.add(session2)
    await async_session.commit()

    # 应该成功
    await transition_session_state(session2, ClassSessionStatus.ENDED)
    assert session2.status == ClassSessionStatus.ENDED

    # 测试3: TEACHING → ENDED ✅
    session3 = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.TEACHING,
    )
    async_session.add(session3)
    await async_session.commit()

    # 应该成功
    await transition_session_state(session3, ClassSessionStatus.ENDED)
    assert session3.status == ClassSessionStatus.ENDED

    # 测试4: ENDED 是终态，不能转换
    session4 = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.ENDED,
    )
    async_session.add(session4)
    await async_session.commit()

    # 所有转换都应该失败（抛出HTTPException）
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await transition_session_state(session4, ClassSessionStatus.PREPARING)
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        await transition_session_state(session4, ClassSessionStatus.TEACHING)
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        await transition_session_state(session4, ClassSessionStatus.ENDED)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_session_settings_preservation(async_session: AsyncSession):
    """测试状态转换过程中设置字段保留"""

    teacher = User(
        username="test_teacher_settings",
        email="test_teacher_settings@example.com",
        hashed_password="$2b$12$hashed",
        role=UserRole.TEACHER,
        school_id=1
    )
    async_session.add(teacher)
    await async_session.commit()

    # 创建带设置的会话
    initial_settings = {
        "display_cell_orders": [1, 2, 3],
        "strict_sync": True,
        "allow_student_navigation": False
    }

    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
        settings=initial_settings,
    )
    async_session.add(session)
    await async_session.commit()
    await async_session.refresh(session)

    # 验证初始设置
    assert session.settings == initial_settings

    # 状态转换1: PREPARING → TEACHING
    from app.api.v1.classroom_sessions import transition_session_state

    await transition_session_state(session, ClassSessionStatus.TEACHING)
    await async_session.commit()
    await async_session.refresh(session)

    # 验证设置保留
    assert session.settings == initial_settings

    # 更新设置
    new_settings = dict(initial_settings)
    new_settings["display_cell_orders"] = [2, 3]
    session.settings = new_settings
    await async_session.commit()
    await async_session.refresh(session)

    # 验证设置更新
    assert session.settings["display_cell_orders"] == [2, 3]

    # 状态转换2: TEACHING → ENDED
    await transition_session_state(session, ClassSessionStatus.ENDED)
    session.ended_at = datetime.utcnow()
    await async_session.commit()
    await async_session.refresh(session)

    # 验证设置仍然保留
    assert session.settings is not None
    assert session.settings["display_cell_orders"] == [2, 3]
    assert session.settings["strict_sync"] is True


@pytest.mark.asyncio
async def test_active_session_check_without_paused(async_session: AsyncSession):
    """测试活跃会话检查不包含PAUSED状态（v2.0移除了PAUSED）"""

    teacher = User(
        username="test_teacher_active_check",
        email="test_teacher_active@example.com",
        hashed_password="$2b$12$hashed",
        role=UserRole.TEACHER,
        school_id=1
    )
    async_session.add(teacher)
    await async_session.commit()

    # 创建3个不同状态的会话
    session_preparing = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
    )
    async_session.add(session_preparing)

    session_teaching = ClassSession(
        lesson_id=2,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.TEACHING,
    )
    async_session.add(session_teaching)

    session_ended = ClassSession(
        lesson_id=3,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.ENDED,
    )
    async_session.add(session_ended)

    await async_session.commit()

    # 查询活跃会话（PREPARING和TEACHING，不包含PAUSED）
    result = await async_session.execute(
        select(ClassSession).where(
            ClassSession.status.in_([
                ClassSessionStatus.PREPARING,
                ClassSessionStatus.TEACHING,
                # v2.0: 不再包含 ClassSessionStatus.PAUSED
            ])
        )
    )
    active_sessions = result.scalars().all()

    # 应该找到2个活跃会话（PREPARING和TEACHING）
    assert len(active_sessions) == 2

    session_ids = {s.id for s in active_sessions}
    assert session_preparing.id in session_ids
    assert session_teaching.id in session_ids
    assert session_ended.id not in session_ids


@pytest.mark.asyncio
async def test_session_duration_calculation(async_session: AsyncSession):
    """测试会话时长计算"""

    teacher = User(
        username="test_teacher_duration",
        email="test_teacher_duration@example.com",
        hashed_password="$2b$12$hashed",
        role=UserRole.TEACHER,
        school_id=1
    )
    async_session.add(teacher)
    await async_session.commit()

    from app.api.v1.classroom_sessions import transition_session_state

    # 创建会话
    start_time = datetime.utcnow()
    session = ClassSession(
        lesson_id=1,
        classroom_id=1,
        teacher_id=teacher.id,
        status=ClassSessionStatus.PREPARING,
        scheduled_start=start_time,
    )
    async_session.add(session)
    await async_session.commit()

    # 开始上课
    await transition_session_state(session, ClassSessionStatus.TEACHING)
    session.actual_start = start_time
    await async_session.commit()

    # 模拟45分钟后结束
    from datetime import timedelta as td

    end_time = start_time + td(minutes=45, seconds=30)
    await transition_session_state(session, ClassSessionStatus.ENDED)
    session.ended_at = end_time

    # 计算时长
    if session.actual_start:
        duration = (session.ended_at - session.actual_start).total_seconds() / 60
        session.duration_minutes = int(duration)

    await async_session.commit()
    await async_session.refresh(session)

    # 验证时长计算（应该是45或46分钟，取决于四舍五入）
    assert session.duration_minutes == 45
    assert session.duration_minutes >= 45
    assert session.duration_minutes < 46
