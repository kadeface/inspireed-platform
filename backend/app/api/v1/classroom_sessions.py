"""
课堂会话 API
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.api import deps
from app.models.user import User, UserRole
from app.models.classroom_session import (
    ClassSession,
    ClassSessionStatus,
    StudentSessionParticipation,
)
from app.models.lesson import Lesson, LessonClassroom, LessonStatus
from app.models.cell import Cell
from app.models.organization import Classroom
from app.models.classroom_assistant import ClassroomMembership
from app.core.classroom_utils import get_user_classroom_ids, check_user_in_classroom
from app.utils.lesson_content_flat import (
    build_json_cells_by_effective_order,
    guest_payload_from_lesson_cell_dict,
    lesson_content_to_guest_outline,
)
from app.schemas.classroom_session import (
    ClassSessionCreate,
    ClassSessionUpdate,
    ClassSessionResponse,
    ClassSessionWithDetails,
    StudentParticipationResponse,
    NavigateToCellRequest,
    StartActivityRequest,
    StartSessionRequest,
    EndSessionRequest,
    SessionStatistics,
    StudentPendingSessionResponse,
    GuestAccessToggleRequest,
    GuestSessionInfoResponse,
    DisplayModeUpdateRequest,
)
from app.services.session_state_machine import (
    SessionStateMachine,
    SessionStatus,
    InvalidStateTransitionError,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ========== 状态机辅助函数 ==========


def map_to_session_status(status: ClassSessionStatus) -> SessionStatus:
    """将ClassSessionStatus映射到SessionStatus"""
    status_map = {
        ClassSessionStatus.PREPARING: SessionStatus.PREPARING,
        ClassSessionStatus.TEACHING: SessionStatus.TEACHING,
        ClassSessionStatus.ENDED: SessionStatus.ENDED,
    }
    return status_map[status]


def map_to_class_session_status(status: SessionStatus) -> ClassSessionStatus:
    """将SessionStatus映射到ClassSessionStatus"""
    status_map = {
        SessionStatus.PREPARING: ClassSessionStatus.PREPARING,
        SessionStatus.TEACHING: ClassSessionStatus.TEACHING,
        SessionStatus.ENDED: ClassSessionStatus.ENDED,
    }
    return status_map[status]


async def transition_session_state(
    session: ClassSession,
    new_status: ClassSessionStatus,
) -> ClassSession:
    """
    使用状态机执行状态转换

    Args:
        session: 会话对象
        new_status: 新状态

    Returns:
        更新后的会话对象

    Raises:
        HTTPException: 如果状态转换不合法
    """
    try:
        # 转换为SessionStatus枚举
        current_status = map_to_session_status(session.status)  # type: ignore[arg-type]
        target_status = map_to_session_status(new_status)

        # 创建状态机并执行转换
        state_machine = SessionStateMachine(initial_status=current_status)
        state_machine.transition_to(target_status)

        # 更新会话状态
        session.status = new_status  # type: ignore[assignment]

        logger.info(
            f"状态转换成功: session_id={session.id}, "
            f"{current_status.value} → {target_status.value}"
        )

        return session

    except InvalidStateTransitionError as e:
        raise HTTPException(
            status_code=400,
            detail=f"非法状态转换: {e.current_status.value} → {e.new_status.value}"
        )


# ========== WebSocket辅助函数 ==========


async def validate_websocket_origin(websocket: WebSocket) -> bool:
    """
    验证WebSocket连接的Origin头

    Args:
        websocket: WebSocket连接对象

    Returns:
        bool: Origin是否合法
    """
    import re

    origin = websocket.headers.get("origin")
    logger.info(f"🔍 WebSocket Origin: {origin}")

    # 如果没有Origin头，允许连接
    if not origin:
        logger.info("⚠️ 没有Origin头，允许连接")
        return True

    # 验证Origin（允许localhost、局域网IP和CloudStudio域名）
    pattern = r"^https?://((localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?|.*\.cloudstudio\.club|.*\.coding\.net)$"
    if re.match(pattern, origin):
        logger.info(f"✅ Origin验证通过: {origin}")
        return True
    else:
        logger.warning(f"❌ Origin验证失败: {origin}")
        return False


async def authenticate_websocket_token(
    token: str,
    db: AsyncSession,
) -> Optional[User]:
    """
    验证WebSocket Token并返回用户信息

    Args:
        token: JWT token
        db: 数据库会话

    Returns:
        User对象，如果验证失败返回None
    """
    try:
        current_user = await deps.get_current_user_from_token(token, db)
        if current_user:
            logger.info(f"✅ Token验证成功: user_id={current_user.id}, role={current_user.role}")
        return current_user
    except Exception as e:
        logger.error(f"❌ Token验证异常: {str(e)}")
        return None


async def validate_student_websocket_access(
    user: User,
    session: ClassSession,
    db: AsyncSession,
) -> bool:
    """
    验证学生是否有权限访问WebSocket

    Args:
        user: 用户对象
        session: 会话对象
        db: 数据库会话

    Returns:
        bool: 是否有权限
    """
    # 1. 验证用户角色
    current_role = cast(UserRole, user.role)
    if current_role != UserRole.STUDENT:
        logger.warning(f"❌ 角色验证失败: 只允许学生连接，当前角色={current_role}")
        return False

    # 2. 验证会话状态
    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        logger.warning(f"❌ 会话已结束: session_id={session.id}, status={session.status}")
        return False

    # 3. 验证班级权限
    classroom_id = cast(int, session.classroom_id)
    has_access = await check_user_in_classroom(db, user, classroom_id)

    if not has_access:
        logger.warning(f"❌ 权限验证失败: 不属于班级 {classroom_id}")
        return False

    logger.info(f"✅ 学生访问验证通过: user_id={user.id}, session_id={session.id}")
    return True


async def validate_teacher_websocket_access(
    user: User,
    session: ClassSession,
) -> bool:
    """
    验证教师是否有权限访问WebSocket

    Args:
        user: 用户对象
        session: 会话对象

    Returns:
        bool: 是否有权限
    """
    # 1. 验证用户角色
    current_role = cast(UserRole, user.role)
    if current_role != UserRole.TEACHER:
        logger.warning(f"❌ 角色验证失败: 只允许教师连接，当前角色={current_role}")
        return False

    # 2. 验证是否是会话的创建者
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, user.id)
    if session_teacher_id != current_user_id:
        logger.warning(f"❌ 权限验证失败: 不是会话创建者")
        return False

    logger.info(f"✅ 教师访问验证通过: user_id={user.id}, session_id={session.id}")
    return True


async def send_initial_state(websocket: WebSocket, session: ClassSession, db: AsyncSession) -> None:
    """
    发送WebSocket初始状态

    Args:
        websocket: WebSocket连接
        session: 会话对象
        db: 数据库会话
    """
    # 获取关联对象
    session_teacher = await db.get(User, cast(int, session.teacher_id))
    session_lesson = await db.get(Lesson, cast(int, session.lesson_id))
    session_classroom = await db.get(Classroom, cast(int, session.classroom_id))

    # 构造初始状态消息
    message = {
        "type": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "session_id": session.id,
            "current_state": {
                "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
                "display_cell_orders": (session.settings or {}).get("display_cell_orders", []),
                "current_cell_id": session.current_cell_id,
                "current_activity_id": session.current_activity_id,
                "display_mode": (session.settings or {}).get("display_mode") or "window",
                # 添加教师和课程信息
                "teacher_name": session_teacher.full_name or session_teacher.username if session_teacher else None,
                "lesson_title": session_lesson.title if session_lesson else None,
                "classroom_name": session_classroom.name if session_classroom else None,
            }
        }
    }

    await websocket.send_text(json.dumps(message))
    logger.info(f"✅ 初始状态已发送: session_id={session.id}")


# ========== 课堂会话 CRUD ==========


@router.post("/lessons/{lesson_id}/sessions", response_model=ClassSessionResponse, status_code=201)
async def create_class_session(
    lesson_id: int,
    data: ClassSessionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """创建课堂会话"""

    # 验证用户角色
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="只有教师可以创建课堂会话")

    # 验证教案存在且有权限
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    lesson_creator_id = cast(Optional[int], lesson.creator_id)
    current_user_id = cast(int, current_user.id)
    if lesson_creator_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权创建该教案的课堂会话")

    # 验证班级存在
    classroom = await db.get(Classroom, data.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    if classroom.is_active is not True:
        raise HTTPException(status_code=400, detail="班级未激活，无法创建会话")

    # 检查教师是否有权限在该班级上课
    from app.services.permission_service import PermissionService
    permission_service = PermissionService()
    if not await permission_service.can_teacher_publish_to_classroom(
        db, current_user, classroom
    ):
        raise HTTPException(
            status_code=403,
            detail=f"无权在班级 {classroom.name} 上课",
        )

    # 确保教案已发布（如果还没有发布，自动发布）
    lesson_status = cast(LessonStatus, lesson.status)
    if lesson_status != LessonStatus.PUBLISHED:
        setattr(lesson, "status", LessonStatus.PUBLISHED)
        setattr(lesson, "published_at", datetime.utcnow())

    # 检查并创建 LessonClassroom 关系（如果不存在）
    # 这样学生端就能看到该教案了
    existing_relation_result = await db.execute(
        select(LessonClassroom).where(
            LessonClassroom.lesson_id == lesson_id,
            LessonClassroom.classroom_id == data.classroom_id,
        )
    )
    existing_relation = existing_relation_result.scalar_one_or_none()
    
    if not existing_relation:
        # 创建 LessonClassroom 关系
        lesson_classroom = LessonClassroom(
            lesson_id=lesson_id,
            classroom_id=data.classroom_id,
            assigned_by=current_user_id,
            assigned_at=datetime.utcnow(),
        )
        db.add(lesson_classroom)

    # 检查是否已有活跃的会话
    result = await db.execute(
        select(ClassSession).where(
            and_(
                ClassSession.lesson_id == lesson_id,
                ClassSession.classroom_id == data.classroom_id,
                # v2.0: 移除PAUSED状态，只检查PREPARING和TEACHING
                ClassSession.status.in_([ClassSessionStatus.PREPARING, ClassSessionStatus.TEACHING]),
            )
        )
    )
    existing_session = result.scalar_one_or_none()
    if existing_session:
        raise HTTPException(
            status_code=400,
            detail=f"该班级已有活跃的课堂会话（ID: {existing_session.id}），请先结束或使用现有会话",
        )

    # 创建会话
    # 默认设置：严格同步模式，不允许学生提前查看
    default_settings = {
        "sync_mode": "strict",  # 严格同步：只显示教师指定的Cell
        "allow_advance": False,  # 不允许学生提前查看
        "auto_save": True,  # 自动保存学生答案
        "show_leaderboard": False,  # 默认不显示排行榜
        "display_mode": "window",  # 学生端 / 观摩端全屏提示同步
    }
    # 合并用户自定义设置
    session_settings = {**default_settings, **(data.settings or {})}
    
    session = ClassSession(
        lesson_id=lesson_id,
        classroom_id=data.classroom_id,
        teacher_id=current_user_id,
        scheduled_start=data.scheduled_start,
        settings=session_settings,
        status=ClassSessionStatus.PREPARING,
        total_students=0,
        active_students=0,
        current_cell_id=None,  # 初始不显示任何Cell，等待教师手动切换
    )

    db.add(session)
    try:
        await db.commit()
        await db.refresh(session)
    except IntegrityError as exc:
        await db.rollback()
        logger.warning(
            "create_class_session integrity error lesson_id=%s classroom_id=%s: %s",
            lesson_id,
            data.classroom_id,
            exc,
        )
        # 与部分唯一索引 uq_active_session_lesson_classroom 或 lesson_classrooms 冲突
        raise HTTPException(
            status_code=409,
            detail="无法创建课堂：该教案与班级下已有未结束的会话，或数据冲突。请先结束现有会话后重试。",
        ) from exc
    except DBAPIError as exc:
        await db.rollback()
        err_txt = str(exc.orig) if getattr(exc, "orig", None) else str(exc)
        if "guest_access" in err_txt or "guest_count" in err_txt or "does not exist" in err_txt:
            logger.exception("create_class_session DB schema mismatch: %s", err_txt)
            raise HTTPException(
                status_code=503,
                detail=(
                    "数据库表 class_sessions 缺少访客相关字段或与当前代码不一致。"
                    "请在 backend 目录执行：alembic upgrade head"
                ),
            ) from exc
        raise

    return session


@router.get("/sessions/{session_id}", response_model=ClassSessionWithDetails)
async def get_class_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取课堂会话详情"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    current_role = cast(UserRole, current_user.role)
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)

    if current_role == UserRole.TEACHER and session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权访问该会话")

    if current_role == UserRole.STUDENT:
        # 🆕 使用统一函数检查学生是否属于该班级（支持多班级和向后兼容）
        classroom_id = cast(int, session.classroom_id)
        has_access = await check_user_in_classroom(db, current_user, classroom_id)
        if not has_access:
            raise HTTPException(status_code=403, detail="无权访问该会话")

    # 加载关联信息
    session_lesson = await db.get(Lesson, cast(int, session.lesson_id))
    session_classroom = await db.get(Classroom, cast(int, session.classroom_id))
    session_teacher = await db.get(User, session_teacher_id)

    # 确保 settings 被正确序列化
    # 直接从数据库对象获取 settings（确保是最新的）
    raw_settings = session.settings or {}
    
    # 创建 settings 的副本，确保可以被正确序列化
    settings = {}
    if isinstance(raw_settings, dict):
        settings = dict(raw_settings)
    elif hasattr(raw_settings, '__dict__'):
        settings = dict(raw_settings.__dict__)
    else:
        try:
            import json
            settings = json.loads(json.dumps(raw_settings, default=str))
        except:
            settings = {}
    
    logger.debug("Session response: session_id=%s", session_id)

    response_dict = {
        "id": session.id,
        "lesson_id": session.lesson_id,
        "classroom_id": session.classroom_id,
        "teacher_id": session.teacher_id,
        "status": session.status,
        "scheduled_start": session.scheduled_start,
        "actual_start": session.actual_start,
        "ended_at": session.ended_at,
        "duration_minutes": session.duration_minutes,
        "current_cell_id": session.current_cell_id,
        "current_activity_id": session.current_activity_id,
        "total_students": session.total_students,
        "active_students": session.active_students,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "lesson_title": session_lesson.title if session_lesson else None,
        "classroom_name": session_classroom.name if session_classroom else None,
        "teacher_name": session_teacher.full_name or session_teacher.username if session_teacher else None,
        "settings": settings,
    }

    return response_dict


@router.get("/lessons/{lesson_id}/sessions", response_model=List[ClassSessionResponse])
async def list_lesson_sessions(
    lesson_id: int,
    status: Optional[ClassSessionStatus] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取教案的所有课堂会话"""

    # 权限检查
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    current_role = cast(UserRole, current_user.role)
    lesson_creator_id = cast(Optional[int], lesson.creator_id)
    current_user_id = cast(int, current_user.id)

    if current_role == UserRole.TEACHER and lesson_creator_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权访问该教案的会话")

    # 构建查询
    query = select(ClassSession).where(ClassSession.lesson_id == lesson_id)
    
    if status:
        query = query.where(ClassSession.status == status)
    
    # 如果是教师，只返回自己创建的会话
    if current_role == UserRole.TEACHER:
        query = query.where(ClassSession.teacher_id == current_user_id)
    
    # 🆕 如果是学生，只返回学生所属班级的会话
    elif current_role == UserRole.STUDENT:
        student_classroom_ids = await get_user_classroom_ids(db, current_user)
        if not student_classroom_ids:
            # 如果学生没有分配到任何班级，返回空列表
            return []
        query = query.where(ClassSession.classroom_id.in_(list(student_classroom_ids)))

    query = query.order_by(ClassSession.created_at.desc())

    result = await db.execute(query)
    sessions = result.scalars().all()

    return sessions


# ========== 会话操作 ==========


@router.post("/sessions/{session_id}/start", response_model=ClassSessionResponse)
async def start_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """开始课堂会话"""

    result = await db.execute(
        select(ClassSession).where(ClassSession.id == session_id).with_for_update()
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")


    # 使用状态机转换状态
    await transition_session_state(session, ClassSessionStatus.TEACHING)

    # 更新开始时间
    session.actual_start = datetime.utcnow() # type: ignore[assignment]
    session.actual_start = datetime.utcnow() # type: ignore[comparison-overlap]

    # 🆕 自动初始化 display_cell_orders：显示第一个 cell
    # 这样学生端在开始上课后就能看到内容，而不是等待教师手动切换
    session_lesson_id = cast(int, session.lesson_id)
    
    # 查找第一个 cell（按 order 升序，如果 order 相同则按 id 升序）
    result = await db.execute(
        select(Cell).where(
            Cell.lesson_id == session_lesson_id
        ).order_by(Cell.order.asc(), Cell.id.asc()).limit(1)
    )
    first_cell = result.scalar_one_or_none()
    
    if first_cell:
        # 找到第一个 cell，初始化 display_cell_orders
        first_cell_order = first_cell.order if first_cell.order is not None else 0
        new_settings = dict(session.settings) if session.settings else {} # type: ignore[assignment]
        new_settings["display_cell_orders"] = [first_cell_order] # type: ignore[assignment]
        setattr(session, "settings", new_settings)
        session.current_cell_id = cast(int, first_cell.id) # type: ignore[comparison-overlap]
        logger.info("Auto-showing first cell: order=%s, cell_id=%s", first_cell_order, first_cell.id)
    else:
        # 如果没有找到 cell，保持为空（等待教师手动切换）
        session.current_cell_id = None # type: ignore[comparison-overlap]
        logger.info("Lesson %s has no cells; waiting for teacher to navigate", session_lesson_id)

    await db.commit()
    await db.refresh(session)

    # 🆕 通过 WebSocket 通知所有学生会话状态已变化
    await manager.broadcast_to_session(
        message={
            "type": "session_status_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
                "actual_start": session.actual_start.isoformat() if session.actual_start else None, # type: ignore[union-attr]
            }
        },
        session_id=session_id
    )
    logger.info("Broadcast session status change: session %s -> TEACHING", session_id)
    
    # 🆕 如果初始化了 display_cell_orders，也广播内容变化消息
    if first_cell:
        # 安全地获取 settings 和 display_cell_orders
        # 使用 getattr 和类型检查来避免 SQLAlchemy Column 类型问题
        settings_value = getattr(session, 'settings', None)
        if settings_value is not None:
            # 确保 settings 是字典类型
            if isinstance(settings_value, dict):
                settings_dict = settings_value
            else:
                # 如果是其他类型（如 SQLAlchemy Column），尝试转换
                try:
                    settings_dict = dict(settings_value) if hasattr(settings_value, '__iter__') else {}
                except (TypeError, ValueError):
                    settings_dict = {}
        else:
            settings_dict = {}
        
        display_cell_orders = settings_dict.get("display_cell_orders", []) if isinstance(settings_dict, dict) else []
        
        if display_cell_orders:
            broadcast_message = {
                "type": "cell_changed",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "action": "navigate",
                    "display_cell_orders": display_cell_orders,
                    "current_cell_id": session.current_cell_id,
                    "changed_by": {
                        "user_id": current_user.id,
                        "user_name": current_user.full_name or current_user.username,
                    }
                }
            }
            await manager.broadcast_to_session(
                message=broadcast_message,
                session_id=session_id,
            )
            logger.info("Broadcast initial cell for session %s", session_id)

    return session


@router.post("/sessions/{session_id}/end", response_model=ClassSessionResponse)
async def end_session(
    session_id: int,
    data: Optional[EndSessionRequest] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """结束课堂会话"""

    result = await db.execute(
        select(ClassSession).where(ClassSession.id == session_id).with_for_update()
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        logger.info("Session %s already ENDED (idempotent)", session_id)
        return session

    try:
        old_status = session.status
        await transition_session_state(session, ClassSessionStatus.ENDED)
    except HTTPException as e:
        if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
            logger.info("Session %s already ENDED (idempotent)", session_id)
            return session
        raise e

    # 更新结束时间
    session.ended_at = datetime.utcnow() # type: ignore[assignment]

    # 计算时长
    if session.actual_start: # type: ignore[comparison-overlap]
        duration = (session.ended_at - session.actual_start).total_seconds() / 60 # type: ignore[comparison-overlap]
        session.duration_minutes = int(duration) # type: ignore[comparison-overlap]

    # 更新所有学生参与记录为离线
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
        participation.is_active = False # type: ignore[comparison-overlap]
        participation.left_at = datetime.utcnow() # type: ignore[comparison-overlap]

    try:
        await db.commit()
        logger.info("Session %s committed as ENDED", session_id)
    except Exception as commit_error:
        logger.error("DB commit failed for session %s: %s", session_id, commit_error)
        await db.rollback()
        raise HTTPException(status_code=500, detail="结束会话失败")

    await db.refresh(session)

    if session.status != ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        logger.error("Session %s status verification failed: expected ENDED, got %s", session_id, session.status)
        raise HTTPException(status_code=500, detail="结束会话失败：状态更新验证失败")

    logger.info("Session %s ended: %s -> ENDED", session_id, old_status)

    try:
        await manager.broadcast_to_session(
            message={
                "type": "session_ended",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "session_id": session_id,
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None,  # type: ignore[union-attr]
                    "message": "课程已结束",
                },
            },
            session_id=session_id,
        )
        logger.info("Broadcast session_ended for session %s", session_id)
    except Exception as ws_error:
        logger.warning("WS broadcast failed for session %s (DB committed): %s", session_id, ws_error)

    return session


# ========== 内容导航 ==========


@router.post("/sessions/{session_id}/navigate", response_model=ClassSessionResponse)
async def navigate_to_cell(
    session_id: int,
    data: NavigateToCellRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """切换当前显示的Cell（使用 display_cell_orders 数组）"""
    
    try:
        session = await db.get(ClassSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        session_teacher_id = cast(int, session.teacher_id)
        current_user_id = cast(int, current_user.id)
        if session_teacher_id != current_user_id:
            raise HTTPException(status_code=403, detail="无权操作")

        if session.status != ClassSessionStatus.TEACHING:  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=400, 
                detail=f"请先点击“开始上课”按钮，等待教师开始上课"
            )

        # 使用 display_cell_orders（直接传递 order 数组）
        if data.display_cell_orders is None:
            raise HTTPException(status_code=400, detail="必须提供 display_cell_orders 参数")
        
        # 🆕 记录原始状态，确保导航不会改变会话状态
        original_status = session.status
        logger.debug("Navigate: session %s pre-status=%s", session_id, original_status)
        
        # 保存 display_cell_orders 到 settings
        new_settings = dict(session.settings) if session.settings else {} # type: ignore[assignment]
        new_settings["display_cell_orders"] = data.display_cell_orders # type: ignore[assignment]
        setattr(session, "settings", new_settings)
        
        # 设置 current_cell_id（用于兼容性，可选）
        if len(data.display_cell_orders) > 0:
            # 尝试根据第一个 order 查找对应的 cell_id
            # 注意：如果存在多个相同 order 的 Cell，取最新的（按 id 降序）
            session_lesson_id = cast(int, session.lesson_id)
            result = await db.execute(
                select(Cell).where(
                    and_(
                        Cell.lesson_id == session_lesson_id,
                        Cell.order == data.display_cell_orders[0],
                    )
                ).order_by(Cell.id.desc())
            )
            # 使用 first() 而不是 scalar_one_or_none()，避免多行数据报错
            first_cell = result.scalars().first()
            session.current_cell_id = cast(int, first_cell.id) if first_cell else None  # type: ignore[comparison-overlap]
        else:
            session.current_cell_id = None  # type: ignore[comparison-overlap]
        
        await db.commit()
        await db.refresh(session)
        
        # 验证状态未被错误修改
        # 使用 type: ignore 避免 SQLAlchemy ColumnElement 的 linter 警告
        if session.status != original_status:  # type: ignore[comparison-overlap]
            logger.warning(f"导航过程中会话状态发生了变化! 原始={original_status}, 当前={session.status}")
            # 这不应该发生，记录错误但继续执行
        
        # 通过 WebSocket 广播变化
        from app.services.websocket_manager import manager as ws_manager
        
        broadcast_message = {
            "type": "cell_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "action": "navigate",
                "display_cell_orders": data.display_cell_orders,
                "current_cell_id": session.current_cell_id,
                "changed_by": {
                    "user_id": current_user.id,
                    "user_name": current_user.full_name or current_user.username,
                }
            }
        }
        
        await ws_manager.broadcast_to_session(
            message=broadcast_message,
            session_id=session_id,
        )
        
        return session
    
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 捕获其他异常
        import traceback
        logger.error(f"导航异常: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"导航失败: {str(e)}"
        )


@router.post("/sessions/{session_id}/display-mode", response_model=ClassSessionResponse)
async def update_session_display_mode(
    session_id: int,
    data: DisplayModeUpdateRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """更新课堂展示模式（窗口/全屏），并广播给学生与访客 WebSocket。"""

    result = await db.execute(
        select(ClassSession).where(ClassSession.id == session_id).with_for_update()
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="课堂已结束")

    new_settings = dict(session.settings) if session.settings else {}
    new_settings["display_mode"] = data.display_mode
    setattr(session, "settings", new_settings)

    await db.commit()
    await db.refresh(session)

    from app.services.websocket_manager import manager as ws_manager

    await ws_manager.broadcast_to_session(
        message={
            "type": "display_mode_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "display_mode": data.display_mode,
            },
        },
        session_id=session_id,
    )

    return session


# ========== 旧代码（已废弃，保留用于参考）==========
# 以下代码在新架构中已废弃，使用 display_cell_orders 替代
# 
#        # 初始化 settings 和 display_cell_ids
#        # 重要：确保从刷新后的 session.settings 中获取最新的 display_cell_ids
#        if session.settings is None:

@router.post("/sessions/{session_id}/start-activity", response_model=ClassSessionResponse)
async def start_activity(
    session_id: int,
    data: StartActivityRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """开始活动"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status != ClassSessionStatus.TEACHING:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="只能在活跃会话中开始活动")

    # 验证Cell存在且是活动类型
    cell = await db.get(Cell, data.cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell不存在")

    from app.models.cell import CellType
    cell_type = cast(CellType, cell.cell_type)
    if cell_type != CellType.ACTIVITY:
        raise HTTPException(status_code=400, detail="该Cell不是活动类型")

    session.current_activity_id = data.cell_id # type: ignore[comparison-overlap]
    session.current_cell_id = data.cell_id # type: ignore[comparison-overlap]  # 同时设置为当前Cell
    await db.commit()
    await db.refresh(session)

    return session


@router.post("/sessions/{session_id}/end-activity", response_model=ClassSessionResponse)
async def end_activity(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """结束活动"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    session.current_activity_id = None # type: ignore[assignment]
    await db.commit()
    await db.refresh(session)

    return session


# ========== 学生参与 ==========


@router.get("/sessions/{session_id}/participants", response_model=List[StudentParticipationResponse])
async def get_session_participants(
    session_id: int,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取会话参与者列表"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    current_role = cast(UserRole, current_user.role)
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)

    if current_role == UserRole.TEACHER and session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权访问")

    # 构建查询
    query = (
        select(StudentSessionParticipation, User)
        .join(User, StudentSessionParticipation.student_id == User.id)
        .where(StudentSessionParticipation.session_id == session_id)
    )

    if is_active is not None:
        query = query.where(StudentSessionParticipation.is_active == is_active)

    query = query.order_by(StudentSessionParticipation.joined_at)

    result = await db.execute(query)
    rows = result.all()

    participants = []
    for participation, user in rows:
        participant_dict = {
            **participation.__dict__,
            "student_name": user.full_name or user.username,
            "student_email": user.email,
        }
        participants.append(participant_dict)

    return participants


@router.post("/sessions/{session_id}/join", response_model=StudentParticipationResponse)
async def join_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """加入课堂会话（学生）"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="只有学生可以加入会话")

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="会话已结束")

    # 🆕 使用统一函数检查学生是否属于该班级
    classroom_id = cast(int, session.classroom_id)
    has_access = await check_user_in_classroom(db, current_user, classroom_id)
    
    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail=f"无权加入该会话：学生不属于该班级（classroom_id={classroom_id}）"
        )

    # 检查是否已加入
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.student_id == current_user.id,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 如果已加入，更新状态（支持重新加入，例如异常退出后重新进入）
        was_inactive = not existing.is_active  # type: ignore[comparison-overlap]
        existing.is_active = True # type: ignore[comparison-overlap]
        existing.last_active_at = datetime.utcnow() # type: ignore[comparison-overlap]
        if session.current_cell_id: # type: ignore[comparison-overlap]
            existing.current_cell_id = session.current_cell_id # type: ignore[comparison-overlap]
        
        # 如果之前是离线状态，现在重新加入，需要更新活跃学生数
        if was_inactive:
            session.active_students = (session.active_students or 0) + 1 # type: ignore[comparison-overlap]
        
        await db.commit()
        await db.refresh(existing)

        # 🆕 如果学生重新加入（从离线变为在线），通知教师
        if was_inactive:
            try:
                from app.api.v1.classroom_sessions import manager
                msg = {
                    "type": "participant_joined",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "session_id": session_id,
                        "student_id": current_user.id,
                        "student_name": current_user.full_name or current_user.username,
                        "active_students": session.active_students,
                        "total_students": session.total_students,
                    },
                }
                await manager.broadcast_to_session(message=msg, session_id=session_id)
                await manager.send_to_teacher(event=msg, scope="session", channel_id=session_id)
                logger.info(f"📢 已广播学生重新加入消息（会话 {session_id}，学生 {current_user.id}）")
            except Exception as ws_error:
                logger.warning(f"⚠️ 广播学生重新加入消息失败: {ws_error}")

        return {
            **existing.__dict__,
            "student_name": current_user.full_name or current_user.username,
            "student_email": current_user.email,
        }

    # 创建新的参与记录
    participation = StudentSessionParticipation(
        session_id=session_id,
        student_id=cast(int, current_user.id),
        is_active=True,
        current_cell_id=session.current_cell_id,
    )

    db.add(participation)

    # 更新会话统计
    session.total_students = (session.total_students or 0) + 1 # type: ignore[comparison-overlap]
    session.active_students = (session.active_students or 0) + 1 # type: ignore[comparison-overlap]

    await db.commit()
    await db.refresh(participation)

    # 🆕 通过 WebSocket 通知教师有学生加入（broadcast_to_session 只发给学生，教师需单独 send_to_teacher）
    try:
        from app.api.v1.classroom_sessions import manager
        msg = {
            "type": "participant_joined",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "student_id": current_user.id,
                "student_name": current_user.full_name or current_user.username,
                "active_students": session.active_students,
                "total_students": session.total_students,
            },
        }
        await manager.broadcast_to_session(message=msg, session_id=session_id)
        await manager.send_to_teacher(event=msg, scope="session", channel_id=session_id)
        logger.info(f"📢 已广播学生加入消息（会话 {session_id}，学生 {current_user.id}）")
    except Exception as ws_error:
        # WebSocket 通知失败不影响加入流程
        logger.warning(f"⚠️ 广播学生加入消息失败: {ws_error}")

    return {
        **participation.__dict__,
        "student_name": current_user.full_name or current_user.username,
        "student_email": current_user.email,
    }


@router.post("/sessions/{session_id}/leave", response_model=dict)
async def leave_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """离开课堂会话"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="只有学生可以离开会话")

    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.student_id == current_user.id,
            )
        )
    )
    participation = result.scalar_one_or_none()

    if not participation:
        raise HTTPException(status_code=404, detail="未参与该会话")

    participation.is_active = False # type: ignore[comparison-overlap]
    participation.left_at = datetime.utcnow() # type: ignore[comparison-overlap]

    # 更新会话统计
    session = await db.get(ClassSession, session_id)
    if session:
        session.active_students = max((session.active_students or 0) - 1, 0) # type: ignore[comparison-overlap]

    await db.commit()

    return {"message": "已离开会话"}


# ========== 学生待开始课堂 ==========


@router.get("/student/pending-sessions", response_model=List[StudentPendingSessionResponse])
async def get_student_pending_sessions(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取学生待开始的课堂列表（pending状态的会话）
    
    只返回最近48小时内创建的pending会话，避免显示过期的课程
    """

    # 权限检查：仅学生可访问
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="仅学生可访问此接口")

    # 🆕 使用统一函数获取学生所在班级ID（支持多班级）
    student_classroom_ids = await get_user_classroom_ids(db, current_user)
    
    if not student_classroom_ids:
        # 如果学生没有分配班级，返回空列表
        logger.info(f"学生 {current_user.id} 没有分配到任何班级，返回空列表")
        return []

    # 计算48小时前的时间点
    cutoff_time = datetime.utcnow() - timedelta(hours=48)

    # 查询学生所在班级的最近48小时内的pending状态会话
    query = (
        select(ClassSession)
        .where(ClassSession.classroom_id.in_(list(student_classroom_ids)))
        .where(ClassSession.status == ClassSessionStatus.PREPARING)
        .where(ClassSession.created_at >= cutoff_time)  # 只返回最近48小时内的会话
        .options(
            selectinload(ClassSession.lesson),
            selectinload(ClassSession.teacher),
            selectinload(ClassSession.classroom),
        )
        .order_by(ClassSession.created_at.desc())
    )

    result = await db.execute(query)
    sessions = result.scalars().all()

    # 构建响应数据
    pending_sessions = []
    for session in sessions:
        # 获取关联信息
        lesson = session.lesson
        teacher = session.teacher
        classroom = session.classroom

        session_dict = {
            "id": session.id,
            "lesson_id": session.lesson_id,
            "lesson_title": lesson.title if lesson else None,
            "teacher_id": session.teacher_id,
            "teacher_name": teacher.full_name or teacher.username if teacher else None,
            "classroom_id": session.classroom_id,
            "classroom_name": classroom.name if classroom else None,
            "status": session.status,
            "created_at": session.created_at,
            "scheduled_start": session.scheduled_start,
            "total_students": session.total_students,
            "active_students": session.active_students,
        }
        pending_sessions.append(StudentPendingSessionResponse(**session_dict))

    return pending_sessions


@router.get("/student/active-sessions", response_model=List[StudentPendingSessionResponse])
async def get_student_active_sessions(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取学生正在上课的课堂列表（active状态的会话）
    
    只返回最近40分钟内开始的active会话，确保只显示真正正在进行的课程
    """

    # 权限检查：仅学生可访问
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="仅学生可访问此接口")

    # 🆕 使用统一函数获取学生所在班级ID
    student_classroom_ids = await get_user_classroom_ids(db, current_user)
    
    if not student_classroom_ids:
        # 如果学生没有分配班级，返回空列表
        return []

    # 计算40分钟前的时间点（一节课的标准时长）
    cutoff_time = datetime.utcnow() - timedelta(minutes=40)

    # 查询学生所在班级的active状态会话
    # 只返回最近40分钟内开始的会话
    # 使用COALESCE：优先使用actual_start，如果没有则使用created_at
    query = (
        select(ClassSession)
        .where(ClassSession.classroom_id.in_(list(student_classroom_ids)))
        .where(ClassSession.status == ClassSessionStatus.TEACHING)
        .where(
            # 使用actual_start或created_at，只要有一个在40分钟内即可
            or_(
                # 如果有actual_start，检查它是否在40分钟内
                and_(
                    ClassSession.actual_start.isnot(None),
                    ClassSession.actual_start >= cutoff_time
                ),
                # 如果没有actual_start，检查created_at是否在40分钟内
                and_(
                    ClassSession.actual_start.is_(None),
                    ClassSession.created_at >= cutoff_time
                )
            )
        )
        .options(
            selectinload(ClassSession.lesson),
            selectinload(ClassSession.teacher),
            selectinload(ClassSession.classroom),
        )
        .order_by(ClassSession.actual_start.desc().nulls_last(), ClassSession.created_at.desc())
    )

    result = await db.execute(query)
    sessions = result.scalars().all()

    # 构建响应数据
    active_sessions = []
    for session in sessions:
        
        # 获取关联信息
        lesson = session.lesson
        teacher = session.teacher
        classroom = session.classroom

        session_dict = {
            "id": session.id,
            "lesson_id": session.lesson_id,
            "lesson_title": lesson.title if lesson else None,
            "teacher_id": session.teacher_id,
            "teacher_name": teacher.full_name or teacher.username if teacher else None,
            "classroom_id": session.classroom_id,
            "classroom_name": classroom.name if classroom else None,
            "status": session.status,
            "created_at": session.created_at,
            "scheduled_start": session.scheduled_start,
            "total_students": session.total_students,
            "active_students": session.active_students,
        }
        active_sessions.append(StudentPendingSessionResponse(**session_dict))

    return active_sessions


# ========== 统计数据 ==========


@router.get("/sessions/{session_id}/statistics", response_model=SessionStatistics)
async def get_session_statistics(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取会话统计数据"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    current_role = cast(UserRole, current_user.role)
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)

    if current_role == UserRole.TEACHER and session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权访问")

    # 获取所有参与者
    result = await db.execute(
        select(StudentSessionParticipation).where(
            StudentSessionParticipation.session_id == session_id
        )
    )
    participations = result.scalars().all()

    total_students = len(participations)
    active_students = sum(1 for p in participations if p.is_active) # type: ignore[operator]
    
    # 计算平均进度
    progress_sum = sum(cast(float, p.progress_percentage) for p in participations)
    average_progress = progress_sum / total_students if total_students > 0 else 0.0

    # 按进度分组
    students_by_progress = {
        "0-25%": 0,
        "25-50%": 0,
        "50-75%": 0,
        "75-100%": 0,
        "100%": 0,
    }

    for p in participations:
        progress = cast(float, p.progress_percentage)
        if progress >= 100:
            students_by_progress["100%"] += 1
        elif progress >= 75:
            students_by_progress["75-100%"] += 1
        elif progress >= 50:
            students_by_progress["50-75%"] += 1
        elif progress >= 25:
            students_by_progress["25-50%"] += 1
        else:
            students_by_progress["0-25%"] += 1

    completed_students = students_by_progress["100%"]

    return SessionStatistics(
        total_students=total_students,
        active_students=active_students,
        completed_students=completed_students,
        average_progress=average_progress,
        students_by_progress=students_by_progress,
    )


# ========== 访客模式 ==========


def _generate_guest_code() -> str:
    """生成6位数字+字母混合接入码"""
    import secrets
    import string
    alphabet = string.ascii_uppercase + string.digits
    # 去除容易混淆的字符
    alphabet = alphabet.replace("O", "").replace("0", "").replace("I", "").replace("1", "").replace("L", "")
    return "".join(secrets.choice(alphabet) for _ in range(6))


@router.post("/sessions/{session_id}/guest-access", response_model=ClassSessionResponse)
async def toggle_guest_access(
    session_id: int,
    data: GuestAccessToggleRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师开启/关闭访客观摩模式"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    if cast(int, session.teacher_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="无权操作")

    if data.enabled:
        session.guest_access_enabled = True  # type: ignore[assignment]
        if not session.guest_access_code:
            for _ in range(10):
                code = _generate_guest_code()
                existing = await db.execute(
                    select(ClassSession).where(ClassSession.guest_access_code == code)
                )
                if not existing.scalar_one_or_none():
                    session.guest_access_code = code  # type: ignore[assignment]
                    break
            else:
                raise HTTPException(status_code=500, detail="无法生成唯一接入码，请重试")
    else:
        session.guest_access_enabled = False  # type: ignore[assignment]

    await db.commit()
    await db.refresh(session)
    return session


@router.get("/guest/join/{access_code}", response_model=GuestSessionInfoResponse)
async def guest_lookup_session(
    access_code: str,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """访客通过接入码查找课堂（无需登录）"""

    result = await db.execute(
        select(ClassSession)
        .where(ClassSession.guest_access_code == access_code.upper())
        .options(
            selectinload(ClassSession.lesson),
            selectinload(ClassSession.teacher),
            selectinload(ClassSession.classroom),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="无效的接入码")

    if not session.guest_access_enabled:
        raise HTTPException(status_code=403, detail="该课堂未开启访客模式")

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="课堂已结束")

    display_cell_orders = (session.settings or {}).get("display_cell_orders", [])

    display_mode = str((session.settings or {}).get("display_mode") or "window")

    return GuestSessionInfoResponse(
        session_id=cast(int, session.id),
        lesson_id=cast(int, session.lesson_id),
        lesson_title=session.lesson.title if session.lesson else None,
        teacher_name=(
            session.teacher.full_name or session.teacher.username
            if session.teacher else None
        ),
        classroom_name=session.classroom.name if session.classroom else None,
        status=cast(ClassSessionStatus, session.status),
        current_cell_id=session.current_cell_id,
        display_cell_orders=display_cell_orders,
        guest_count=session.guest_count or 0,
        display_mode=display_mode,
    )


def _serialize_cell_for_guest(cell: Cell) -> Dict[str, Any]:
    """ORM Cell → guest cells 列表项（与历史 JSON 字段一致）。"""
    return {
        "id": cell.id,
        "cell_type": cell.cell_type.value
        if hasattr(cell.cell_type, "value")
        else str(cell.cell_type),
        "title": cell.title,
        "content": cell.content,
        "config": cell.config,
        "order": cell.order,
    }


@router.get("/guest/session/{session_id}/cells")
async def guest_get_session_cells(
    session_id: int,
    access_code: str,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """访客获取当前可见的 Cell 内容（只读，无需登录）"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    if (
        not session.guest_access_enabled
        or session.guest_access_code != access_code.upper()
    ):
        raise HTTPException(status_code=403, detail="访客访问未授权")

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="课堂已结束")

    lesson_id_int = cast(int, session.lesson_id)
    lesson_row = await db.get(Lesson, lesson_id_int)
    lesson_content = getattr(lesson_row, "content", None) if lesson_row else None

    raw_orders = (session.settings or {}).get("display_cell_orders") or []
    display_orders: List[int] = []
    if isinstance(raw_orders, list):
        for x in raw_orders:
            try:
                display_orders.append(int(x))
            except (TypeError, ValueError):
                continue

    cells_data: List[Dict[str, Any]] = []

    if display_orders:
        # 同一 order：优先 Lesson.content（与导播台模块类型/顺序一致）；cells 表作活动题目补全与无 JSON 时的兜底
        db_by_order: Dict[int, Cell] = {}
        db_rows = await db.execute(
            select(Cell)
            .where(Cell.lesson_id == lesson_id_int, Cell.order.in_(display_orders))
            .order_by(Cell.order.asc(), Cell.id.asc())
        )
        for cell in db_rows.scalars().all():
            if cell.order is not None:
                db_by_order[int(cell.order)] = cell

        json_by_order = build_json_cells_by_effective_order(lesson_content)
        for o in display_orders:
            jc = json_by_order.get(o)
            db_c = db_by_order.get(o)

            # 与导播台一致：以 Lesson.content 扁平结果为准（类型/顺序与教师看到的相同）。
            # cells 表中同一 lesson_id+order 可能残留多条 ACTIVITY（同步/历史），若优先 DB
            # 会把前几个 order 错显示成活动，而实际教案已是 TEXT/BROWSER。
            if jc is not None:
                j_raw = jc.get("type") or jc.get("cell_type") or "TEXT"
                j_type = (
                    j_raw.value
                    if hasattr(j_raw, "value")
                    else str(j_raw)
                ).upper()

                if j_type == "ACTIVITY" and db_c is not None:
                    db_type = (
                        db_c.cell_type.value
                        if hasattr(db_c.cell_type, "value")
                        else str(db_c.cell_type)
                    )
                    if db_type == "ACTIVITY":
                        jcont = jc.get("content") if isinstance(jc, dict) else None
                        jitems = (
                            jcont.get("items")
                            if isinstance(jcont, dict)
                            else None
                        )
                        db_cont = db_c.content
                        db_items = (
                            db_cont.get("items")
                            if isinstance(db_cont, dict)
                            else None
                        )
                        if isinstance(db_items, list) and len(db_items) > 0 and (
                            not isinstance(jitems, list) or len(jitems) == 0
                        ):
                            cells_data.append(_serialize_cell_for_guest(db_c))
                            continue

                cells_data.append(guest_payload_from_lesson_cell_dict(jc, o))
            elif db_c is not None:
                cells_data.append(_serialize_cell_for_guest(db_c))
    else:
        if session.current_cell_id:
            cc = await db.get(Cell, cast(int, session.current_cell_id))
            if cc is not None and cast(int, cc.lesson_id) == lesson_id_int:
                cells_data.append(_serialize_cell_for_guest(cc))
                if cc.order is not None and int(cc.order) not in display_orders:
                    display_orders = [int(cc.order)]

        if (
            not cells_data
            and session.status == ClassSessionStatus.TEACHING  # type: ignore[comparison-overlap]
        ):
            result = await db.execute(
                select(Cell)
                .where(Cell.lesson_id == lesson_id_int)
                .order_by(Cell.order.asc(), Cell.id.asc())
                .limit(1)
            )
            first_cell = result.scalar_one_or_none()
            if first_cell is not None:
                cells_data.append(_serialize_cell_for_guest(first_cell))
                display_orders = (
                    [int(first_cell.order)]
                    if first_cell.order is not None
                    else [0]
                )

    # 全课模块目录：与教师导播台一致，来自 Lesson.content（sections 平铺）
    lesson_outline: List[Dict[str, Any]] = []
    if lesson_row is not None:
        lesson_outline = lesson_content_to_guest_outline(lesson_content)

    if not lesson_outline:
        outline_result = await db.execute(
            select(Cell.id, Cell.order, Cell.title, Cell.cell_type)
            .where(Cell.lesson_id == lesson_id_int)
            .order_by(Cell.order.asc(), Cell.id.asc())
        )
        for row in outline_result.all():
            ct = row.cell_type
            lesson_outline.append(
                {
                    "id": int(row.id),
                    "order": int(row.order) if row.order is not None else None,
                    "title": (row.title or "").strip(),
                    "cell_type": ct.value if hasattr(ct, "value") else str(ct),
                }
            )

    status_val = (
        session.status.value
        if hasattr(session.status, "value")
        else str(session.status)
    )

    display_mode = str((session.settings or {}).get("display_mode") or "window")

    return {
        "cells": cells_data,
        "current_cell_id": session.current_cell_id,
        "display_cell_orders": display_orders,
        "status": status_val,
        "lesson_outline": lesson_outline,
        "display_mode": display_mode,
    }


# ========== WebSocket 实时同步 ==========


# 导入 WebSocket 管理器
from app.services.websocket_manager import manager


# ========== 会话清理和检查 ==========

# 🚫 v2.0: 移除HTTP轮询端点 check-teacher-status
# v2.0 采用纯WebSocket通信，不需要HTTP轮询降级
# 教师连接状态通过WebSocket实时获取，无需定期HTTP检查
# 原 check_teacher_status 函数已删除（line 1385-1441, 共57行）

@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: str,  # JWT token from query parameter
    db: AsyncSession = Depends(deps.get_db),
):
    """
    WebSocket 连接端点（学生端）

    连接URL: ws://api/v1/classroom-sessions/sessions/{session_id}/ws?token={jwt}
    """

    logger.info(f"🔌 学生WebSocket连接请求: session_id={session_id}")

    # 初始化 student_id 避免未绑定错误
    student_id: Optional[int] = None

    # 先接受连接
    await websocket.accept()

    # 使用辅助函数验证Origin
    if not await validate_websocket_origin(websocket):
        await websocket.close(code=1008, reason="CORS validation failed")
        return

    try:
        # 使用辅助函数验证Token并获取用户信息
        current_user = await authenticate_websocket_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # 验证会话存在性
        session = await db.get(ClassSession, session_id)
        if not session:
            logger.error(f"❌ 会话不存在: session_id={session_id}")
            await websocket.close(code=1008, reason="Session not found")
            return

        # 使用辅助函数验证学生访问权限（角色 + 状态 + 班级权限）
        if not await validate_student_websocket_access(current_user, session, db):
            await websocket.close(code=1008, reason="Access denied")
            return

        student_id = cast(int, current_user.id)
        logger.info(f"✅ 学生验证通过: user_id={student_id}, session_id={session_id}")

        # 注册连接
        await manager.connect(websocket, session_id, student_id)
        logger.info(f"✅ 连接已注册: session_id={session_id}, student_id={student_id}")

        # 发送初始状态
        await send_initial_state(websocket, session, db)

        # 更新学生在线状态
        await update_student_online_status(db, session_id, student_id, is_online=True)

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                continue

            await handle_client_message(
                message=message,
                session_id=session_id,
                student_id=student_id,
                websocket=websocket,
                db=db,
            )

    except WebSocketDisconnect:
        logger.info("Student disconnected: session_id=%s, student_id=%s", session_id, student_id)
    except Exception:
        logger.exception("WebSocket error: session_id=%s, student_id=%s", session_id, student_id)
    finally:
        # 清理连接
        if student_id is not None:
            try:
                await manager.disconnect(session_id, student_id)
                await update_student_online_status(db, session_id, student_id, is_online=False)
                logger.info(f"✅ 连接已清理: session_id={session_id}, student_id={student_id}")
            except Exception as e:
                logger.error(f"⚠️ 清理连接时出错: {str(e)}")


async def handle_client_message(
    message: dict,
    session_id: int,
    student_id: int,
    websocket: WebSocket,
    db: AsyncSession,
):
    """处理客户端发送的消息"""
    
    message_type = message.get("type")
    
    if message_type == "ping":
        # 心跳响应
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }))
    
    elif message_type == "update_progress":
        # 更新学生进度
        data = message.get("data", {})
        await update_student_progress(
            db=db,
            session_id=session_id,
            student_id=student_id,
            current_cell_id=data.get("current_cell_id"),
            completed_cells=data.get("completed_cells", []),
            progress_percentage=data.get("progress_percentage", 0),
        )
    
    else:
        logger.warning("Unknown WS message type: %s (session=%s, student=%s)", message_type, session_id, student_id)


async def update_student_online_status(
    db: AsyncSession,
    session_id: int,
    student_id: int,
    is_online: bool,
):
    """更新学生在线状态"""
    
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.student_id == student_id,
            )
        )
    )
    participation = result.scalar_one_or_none()
    
    if participation:
        participation.is_active = is_online  # type: ignore[comparison-overlap]
        participation.last_active_at = datetime.utcnow()  # type: ignore[comparison-overlap]
        if not is_online:
            participation.left_at = datetime.utcnow()  # type: ignore[comparison-overlap]
        await db.commit()


async def update_student_progress(
    db: AsyncSession,
    session_id: int,
    student_id: int,
    current_cell_id: Optional[int],
    completed_cells: List[int],
    progress_percentage: float,
):
    """更新学生学习进度"""
    
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.student_id == student_id,
            )
        )
    )
    participation = result.scalar_one_or_none()
    
    if participation:
        if current_cell_id:
            participation.current_cell_id = current_cell_id  # type: ignore[comparison-overlap]
        participation.completed_cells = completed_cells  # type: ignore[comparison-overlap]
        participation.progress_percentage = progress_percentage  # type: ignore[comparison-overlap]
        participation.last_active_at = datetime.utcnow()  # type: ignore[comparison-overlap]
        await db.commit()


# ========== 访客 WebSocket（只读观摩） ==========


@router.websocket("/sessions/{session_id}/ws/guest")
async def websocket_guest_endpoint(
    websocket: WebSocket,
    session_id: int,
    code: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """访客 WebSocket — 只读观摩，无需登录。

    访客只能接收 cell_changed / session_ended 等广播，不能发送进度或提交活动。
    """

    await websocket.accept()

    session = await db.get(ClassSession, session_id)
    if (
        not session
        or not session.guest_access_enabled
        or session.guest_access_code != code.upper()
    ):
        await websocket.close(code=1008, reason="Access denied")
        return

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        await websocket.close(code=1008, reason="Session ended")
        return

    session.guest_count = (session.guest_count or 0) + 1  # type: ignore[assignment]
    await db.commit()

    guest_key = f"guest:{session_id}"
    if not hasattr(manager, "_guest_connections"):
        manager._guest_connections = {}  # type: ignore[attr-defined]
    manager._guest_connections.setdefault(guest_key, set())  # type: ignore[attr-defined]
    manager._guest_connections[guest_key].add(websocket)  # type: ignore[attr-defined]

    try:
        await send_initial_state(websocket, session, db)

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                continue
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {},
                }))
    except WebSocketDisconnect:
        logger.info("Guest disconnected from session %s", session_id)
    except Exception as e:
        logger.error("Guest WS error: %s", e)
    finally:
        if hasattr(manager, "_guest_connections"):
            conns = manager._guest_connections.get(guest_key)  # type: ignore[attr-defined]
            if conns:
                conns.discard(websocket)
                if not conns:
                    del manager._guest_connections[guest_key]  # type: ignore[attr-defined]
        try:
            session_refresh = await db.get(ClassSession, session_id)
            if session_refresh:
                session_refresh.guest_count = max((session_refresh.guest_count or 0) - 1, 0)  # type: ignore[assignment]
                await db.commit()
        except Exception:
            pass


# ========== 教师端 WebSocket 实时通知 ==========


@router.websocket("/sessions/{session_id}/ws/teacher")
async def websocket_teacher_session_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    教师端 WebSocket 连接端点（课堂模式）

    连接URL: ws://api/v1/classroom-sessions/sessions/{session_id}/ws/teacher?token={jwt}

    用于接收课堂实时通知：
    - 学生提交活动
    - 提交统计更新
    - 学生答题进度
    """

    logger.info(f"🔌 教师WebSocket连接请求（课堂）: session_id={session_id}")

    # 初始化 teacher_id
    teacher_id: Optional[int] = None

    # 先接受连接
    await websocket.accept()

    # 使用辅助函数验证Origin
    if not await validate_websocket_origin(websocket):
        await websocket.close(code=1008, reason="CORS validation failed")
        return

    try:
        # 使用辅助函数验证Token并获取用户信息
        current_user = await authenticate_websocket_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # 验证会话存在性
        session = await db.get(ClassSession, session_id)
        if not session:
            logger.error(f"❌ 会话不存在: session_id={session_id}")
            await websocket.close(code=1008, reason="Session not found")
            return

        # 使用辅助函数验证教师访问权限（角色 + 是否是会话创建者）
        if not await validate_teacher_websocket_access(current_user, session):
            await websocket.close(code=1008, reason="Access denied")
            return

        teacher_id = cast(int, current_user.id)
        logger.info(f"✅ 教师验证通过: teacher_id={teacher_id}, session_id={session_id}")

        # 注册连接
        await manager.connect_v2(
            websocket=websocket,
            scope="session",
            channel_id=session_id,
            user_id=teacher_id,
            role=UserRole.TEACHER
        )
        logger.info(f"✅ 教师连接已注册: session_id={session_id}")

        # 发送初始连接确认
        await websocket.send_text(json.dumps({
            "type": "teacher_connected",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "teacher_id": teacher_id,
            }
        }))

        # 监听客户端消息（心跳、请求统计等）
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")

            if message_type == "ping":
                # 心跳响应
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                }))

            elif message_type == "request_statistics":
                # 请求统计信息
                from app.services.realtime import get_submission_statistics, build_event, Channel
                from app.api.v1.activities import get_cell_uuid_from_db_id

                cell_id = message.get("data", {}).get("cell_id")  # 可能是 UUID 字符串或数字
                lesson_id = message.get("data", {}).get("lesson_id")

                if cell_id and lesson_id:
                    # get_submission_statistics 现在支持 UUID 字符串
                    stats = await get_submission_statistics(
                        db,
                        cell_id=cell_id,
                        lesson_id=lesson_id,
                        session_id=session_id
                    )

                    # 确保返回的 cell_id 是 UUID 格式（前端使用 UUID）
                    stats_cell_id = stats.get("cell_id")
                    if stats_cell_id is not None:
                        try:
                            numeric_id = int(stats_cell_id)
                            cell_uuid = await get_cell_uuid_from_db_id(db, numeric_id, lesson_id)
                            stats["cell_id"] = cell_uuid
                        except (ValueError, TypeError):
                            pass

                    event = build_event(
                        type="submission_statistics_updated",
                        channel=Channel(scope="session", id=session_id),
                        delivery_mode="unicast",
                        data=stats
                    )

                    await websocket.send_text(json.dumps(event))

    except WebSocketDisconnect:
        logger.info(f"🔌 教师断开连接: teacher_id={teacher_id}, session_id={session_id}")
    except Exception as e:
        logger.error(f"❌ 教师 WebSocket 异常: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理连接
        if teacher_id is not None:
            try:
                await manager.disconnect_v2(
                    scope="session",
                    channel_id=session_id,
                    user_id=teacher_id,
                    role=UserRole.TEACHER
                )
                logger.info(f"✅ 教师连接已清理: teacher_id={teacher_id}, session_id={session_id}")
            except Exception as e:
                logger.error(f"⚠️ 清理教师连接时出错: {str(e)}")


@router.websocket("/lessons/{lesson_id}/ws/teacher")
async def websocket_teacher_lesson_endpoint(
    websocket: WebSocket,
    lesson_id: int,
    token: str,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    教师端 WebSocket 连接端点（课后模式）

    连接URL: ws://api/v1/classroom-sessions/lessons/{lesson_id}/ws/teacher?token={jwt}

    用于接收课后实时通知：
    - 学生提交活动
    - 提交统计更新
    """

    logger.info(f"🔌 教师WebSocket连接请求（课后）: lesson_id={lesson_id}")

    # 初始化 teacher_id
    teacher_id: Optional[int] = None

    # 先接受连接
    await websocket.accept()

    # 使用辅助函数验证Origin
    if not await validate_websocket_origin(websocket):
        await websocket.close(code=1008, reason="CORS validation failed")
        return

    try:
        # 使用辅助函数验证Token并获取用户信息
        current_user = await authenticate_websocket_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # 验证用户角色（只允许教师连接）
        current_role = cast(UserRole, current_user.role)
        if current_role != UserRole.TEACHER:
            await websocket.close(code=1008, reason="Only teachers can connect to this endpoint")
            return

        # 验证教案存在性
        lesson = await db.get(Lesson, lesson_id)
        if not lesson:
            logger.error(f"❌ 教案不存在: lesson_id={lesson_id}")
            await websocket.close(code=1008, reason="Lesson not found")
            return

        # 验证教师有权访问该教案（通过班级或教案创建者）
        teacher_id = cast(int, current_user.id)
        from app.services.realtime import fetch_teachers_by_lesson

        authorized_teacher_ids = await fetch_teachers_by_lesson(db, lesson_id)
        if teacher_id not in authorized_teacher_ids:
            logger.warning(f"❌ 教师无权访问该教案: teacher_id={teacher_id}, lesson_id={lesson_id}")
            await websocket.close(code=1008, reason="Access denied: Not authorized for this lesson")
            return

        logger.info(f"✅ 教师验证通过（课后）: teacher_id={teacher_id}, lesson_id={lesson_id}")

        # 注册连接
        await manager.connect_v2(
            websocket=websocket,
            scope="lesson",
            channel_id=lesson_id,
            user_id=teacher_id,
            role=UserRole.TEACHER
        )
        logger.info(f"✅ 教师连接已注册（课后）: lesson_id={lesson_id}")

        # 发送初始连接确认
        await websocket.send_text(json.dumps({
            "type": "teacher_connected",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "lesson_id": lesson_id,
                "teacher_id": teacher_id,
            }
        }))

        # 监听客户端消息（心跳、请求统计等）
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")

            if message_type == "ping":
                # 心跳响应
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                }))

            elif message_type == "request_statistics":
                # 请求统计信息
                from app.services.realtime import get_submission_statistics, build_event, Channel
                from app.api.v1.activities import get_cell_uuid_from_db_id

                cell_id = message.get("data", {}).get("cell_id")
                lesson_id_param = message.get("data", {}).get("lesson_id")

                # 使用参数中的 lesson_id 或路径中的 lesson_id
                actual_lesson_id = lesson_id_param or lesson_id

                if cell_id and actual_lesson_id:
                    stats = await get_submission_statistics(
                        db,
                        cell_id=cell_id,
                        lesson_id=actual_lesson_id,
                        session_id=None
                    )

                    # 确保返回的 cell_id 是 UUID 格式
                    stats_cell_id = stats.get("cell_id")
                    if stats_cell_id is not None:
                        try:
                            numeric_id = int(stats_cell_id)
                            cell_uuid = await get_cell_uuid_from_db_id(db, numeric_id, actual_lesson_id)
                            stats["cell_id"] = cell_uuid
                        except (ValueError, TypeError):
                            pass

                    event = build_event(
                        type="submission_statistics_updated",
                        channel=Channel(scope="lesson", id=actual_lesson_id),
                        delivery_mode="unicast",
                        data=stats
                    )

                    await websocket.send_text(json.dumps(event))

    except WebSocketDisconnect:
        logger.info(f"🔌 教师断开连接（课后）: teacher_id={teacher_id}, lesson_id={lesson_id}")
    except Exception as e:
        logger.error(f"❌ 教师 WebSocket 异常（课后）: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理连接
        if teacher_id is not None:
            try:
                await manager.disconnect_v2(
                    scope="lesson",
                    channel_id=lesson_id,
                    user_id=teacher_id,
                    role=UserRole.TEACHER
                )
                logger.info(f"✅ 教师连接已清理（课后）: teacher_id={teacher_id}, lesson_id={lesson_id}")
            except Exception as e:
                logger.error(f"⚠️ 清理教师连接时出错（课后）: {str(e)}")

