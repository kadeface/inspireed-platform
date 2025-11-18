"""
课堂会话 API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast
import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User, UserRole
from app.models.classroom_session import (
    ClassSession,
    ClassSessionStatus,
    StudentSessionParticipation,
)
from app.models.lesson import Lesson
from app.models.cell import Cell
from app.models.organization import Classroom
from app.schemas.classroom_session import (
    ClassSessionCreate,
    ClassSessionUpdate,
    ClassSessionResponse,
    ClassSessionWithDetails,
    StudentParticipationResponse,
    NavigateToCellRequest,
    StartActivityRequest,
    StartSessionRequest,
    PauseSessionRequest,
    ResumeSessionRequest,
    EndSessionRequest,
    SessionStatistics,
)

router = APIRouter()


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

    # 检查是否已有活跃的会话
    result = await db.execute(
        select(ClassSession).where(
            and_(
                ClassSession.lesson_id == lesson_id,
                ClassSession.classroom_id == data.classroom_id,
                ClassSession.status.in_([ClassSessionStatus.PENDING, ClassSessionStatus.ACTIVE, ClassSessionStatus.PAUSED]),
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
    }
    # 合并用户自定义设置
    session_settings = {**default_settings, **(data.settings or {})}
    
    session = ClassSession(
        lesson_id=lesson_id,
        classroom_id=data.classroom_id,
        teacher_id=current_user_id,
        scheduled_start=data.scheduled_start,
        settings=session_settings,
        status=ClassSessionStatus.PENDING,
        total_students=0,
        active_students=0,
        current_cell_id=None,  # 初始不显示任何Cell，等待教师手动切换
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

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
        # 检查学生是否属于该班级
        classroom_id = cast(int, session.classroom_id)
        student_classroom_id = cast(Optional[int], current_user.classroom_id)
        if student_classroom_id != classroom_id:
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
    
    print(f"📤 返回会话数据: session_id={session_id}, settings={settings}")

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

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status != ClassSessionStatus.PENDING:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail=f"会话状态为 {session.status}，无法开始")

    # 更新状态
    session.status = ClassSessionStatus.ACTIVE # type: ignore[comparison-overlap]
    session.actual_start = datetime.utcnow() # type: ignore[comparison-overlap]

    # 默认不显示任何Cell，等待教师手动切换
    # 这样更符合实际教学流程：教师可以先准备，然后再切换给学生看
    session.current_cell_id = None # type: ignore[comparison-overlap]

    await db.commit()
    await db.refresh(session)

    return session


@router.post("/sessions/{session_id}/pause", response_model=ClassSessionResponse)
async def pause_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """暂停课堂会话"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status != ClassSessionStatus.ACTIVE:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="只能暂停进行中的会话")

    session.status = ClassSessionStatus.PAUSED # type: ignore[comparison-overlap]
    await db.commit()
    await db.refresh(session)

    return session


@router.post("/sessions/{session_id}/resume", response_model=ClassSessionResponse)
async def resume_session(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """继续课堂会话"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status != ClassSessionStatus.PAUSED:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="只能继续已暂停的会话")

    session.status = ClassSessionStatus.ACTIVE # type: ignore[comparison-overlap]
    await db.commit()
    await db.refresh(session)

    return session


@router.post("/sessions/{session_id}/end", response_model=ClassSessionResponse)
async def end_session(
    session_id: int,
    data: Optional[EndSessionRequest] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """结束课堂会话"""

    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    if session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="会话已结束")

    # 更新状态
    session.status = ClassSessionStatus.ENDED # type: ignore[comparison-overlap]
    session.ended_at = datetime.utcnow() # type: ignore[comparison-overlap]

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

    await db.commit()
    await db.refresh(session)

    # 🆕 通过 WebSocket 通知所有学生会话已结束
    await manager.broadcast_to_session(
        message={
            "type": "session_ended",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None, # type: ignore[union-attr]
                "message": "课程已结束"
            }
        },
        session_id=session_id
    )

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
        print(f"🎯 导航请求: session_id={session_id}, display_cell_orders={data.display_cell_orders}")

        session = await db.get(ClassSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        session_teacher_id = cast(int, session.teacher_id)
        current_user_id = cast(int, current_user.id)
        if session_teacher_id != current_user_id:
            raise HTTPException(status_code=403, detail="无权操作")

        if session.status != ClassSessionStatus.ACTIVE:  # type: ignore[comparison-overlap]
            raise HTTPException(status_code=400, detail="只能在活跃会话中切换Cell")

        # 使用 display_cell_orders（直接传递 order 数组）
        if data.display_cell_orders is None:
            raise HTTPException(status_code=400, detail="必须提供 display_cell_orders 参数")
        
        # 保存 display_cell_orders 到 settings
        new_settings = dict(session.settings) if session.settings else {} # type: ignore[assignment]
        new_settings["display_cell_orders"] = data.display_cell_orders # type: ignore[assignment]
        setattr(session, "settings", new_settings)
        
        # 设置 current_cell_id（用于兼容性，可选）
        if len(data.display_cell_orders) > 0:
            # 尝试根据第一个 order 查找对应的 cell_id
            session_lesson_id = cast(int, session.lesson_id)
            result = await db.execute(
                select(Cell).where(
                    and_(
                        Cell.lesson_id == session_lesson_id,
                        Cell.order == data.display_cell_orders[0],
                    )
                )
            )
            first_cell = result.scalar_one_or_none()
            session.current_cell_id = cast(int, first_cell.id) if first_cell else None  # type: ignore[comparison-overlap]
        else:
            session.current_cell_id = None  # type: ignore[comparison-overlap]
        
        await db.commit()
        await db.refresh(session)
        
        print(f"✅ 导航成功: session_id={session_id}, display_cell_orders={data.display_cell_orders}")
        
        # ✅ 新增：通过 WebSocket 广播变化
        from app.services.websocket_manager import manager as ws_manager
        
        await ws_manager.broadcast_to_session(
            message={
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
            },
            session_id=session_id,
        )
        
        print(f"📢 已广播内容切换（会话 {session_id}）")
        
        return session
    
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 捕获其他异常
        import traceback
        print(f"❌ 导航异常: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"导航失败: {str(e)}"
        )


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

    if session.status != ClassSessionStatus.ACTIVE:  # type: ignore[comparison-overlap]
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

    # 检查学生是否属于该班级
    classroom_id = cast(int, session.classroom_id)
    student_classroom_id = cast(Optional[int], current_user.classroom_id)
    if student_classroom_id != classroom_id:
        raise HTTPException(status_code=403, detail="无权加入该会话")

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
        # 如果已加入，更新状态
        existing.is_active = True # type: ignore[comparison-overlap]
        existing.last_active_at = datetime.utcnow() # type: ignore[comparison-overlap]
        if session.current_cell_id: # type: ignore[comparison-overlap]
            existing.current_cell_id = session.current_cell_id # type: ignore[comparison-overlap]   
        await db.commit()
        await db.refresh(existing)

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


# ========== WebSocket 实时同步 ==========


# 导入 WebSocket 管理器
from app.services.websocket_manager import manager


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: str,  # JWT token from query parameter
    db: AsyncSession = Depends(deps.get_db),
):
    """
    WebSocket 连接端点
    
    连接URL: ws://api/v1/classroom-sessions/sessions/{session_id}/ws?token={jwt}
    """
    
    # 1. 验证Token并获取用户信息
    try:
        current_user = await deps.get_current_user_from_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Auth failed: {str(e)}")
        return
    
    # 2. 验证用户角色（只允许学生连接，教师端使用HTTP API）
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.STUDENT:
        await websocket.close(code=1008, reason="Only students can connect via WebSocket")
        return
    
    # 3. 验证会话存在性和权限
    session = await db.get(ClassSession, session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # 🆕 检查会话状态
    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        await websocket.close(code=1008, reason="Session has ended")
        return
    
    # 验证学生属于该班级
    classroom_id = cast(int, session.classroom_id)
    student_classroom_id = cast(Optional[int], current_user.classroom_id)
    if student_classroom_id != classroom_id:
        await websocket.close(code=1008, reason="Access denied")
        return
    
    # 4. 接受连接
    await websocket.accept()
    student_id = cast(int, current_user.id)
    
    # 5. 注册连接
    await manager.connect(websocket, session_id, student_id)
    
    # 6. 发送初始状态（当前会话状态）
    await send_initial_state(websocket, session, db)
    
    # 7. 更新学生在线状态（数据库）
    await update_student_online_status(db, session_id, student_id, is_online=True)
    
    try:
        # 8. 监听客户端消息
        while True:
            # 接收文本消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            await handle_client_message(
                message=message,
                session_id=session_id,
                student_id=student_id,
                websocket=websocket,
                db=db,
            )
    
    except WebSocketDisconnect:
        # 客户端主动断开
        print(f"🔌 学生 {student_id} 断开连接（会话 {session_id}）")
    
    except Exception as e:
        # 异常断开
        print(f"❌ WebSocket异常: {str(e)}")
    
    finally:
        # 9. 清理：移除连接、更新状态
        await manager.disconnect(session_id, student_id)
        await update_student_online_status(db, session_id, student_id, is_online=False)
        print(f"✅ 学生 {student_id} 连接已清理（会话 {session_id}）")


async def send_initial_state(websocket: WebSocket, session: ClassSession, db: AsyncSession):
    """发送初始状态给新连接的客户端"""
    
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
            }
        }
    }
    
    await websocket.send_text(json.dumps(message))


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
        # 未知消息类型
        print(f"⚠️ 未知消息类型: {message_type}")


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
    
    # 1. 验证Token并获取用户信息
    try:
        current_user = await deps.get_current_user_from_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Auth failed: {str(e)}")
        return
    
    # 2. 验证用户角色（只允许教师连接）
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        await websocket.close(code=1008, reason="Only teachers can connect to this endpoint")
        return
    
    # 3. 验证会话存在性和权限
    session = await db.get(ClassSession, session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # 验证教师是该会话的授课教师
    teacher_id = cast(int, current_user.id)
    session_teacher_id = cast(int, session.teacher_id)
    if session_teacher_id != teacher_id:
        await websocket.close(code=1008, reason="Access denied: Not the session teacher")
        return
    
    # 4. 接受连接
    await websocket.accept()
    
    # 5. 注册连接
    await manager.connect_v2(
        websocket=websocket,
        scope="session",
        channel_id=session_id,
        user_id=teacher_id,
        role=UserRole.TEACHER
    )
    
    # 6. 发送初始连接确认
    await websocket.send_text(json.dumps({
        "type": "teacher_connected",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "session_id": session_id,
            "teacher_id": teacher_id,
        }
    }))
    
    try:
        # 7. 监听客户端消息（心跳、请求统计等）
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
                
                cell_id = message.get("data", {}).get("cell_id")
                lesson_id = message.get("data", {}).get("lesson_id")
                
                if cell_id and lesson_id:
                    stats = await get_submission_statistics(
                        db,
                        cell_id=cell_id,
                        lesson_id=lesson_id,
                        session_id=session_id
                    )
                    
                    event = build_event(
                        type="submission_statistics_updated",
                        channel=Channel(scope="session", id=session_id),
                        delivery_mode="unicast",
                        data=stats
                    )
                    
                    await websocket.send_text(json.dumps(event))
    
    except WebSocketDisconnect:
        print(f"🔌 教师 {teacher_id} 断开连接（会话 {session_id}）")
    
    except Exception as e:
        print(f"❌ 教师 WebSocket 异常: {str(e)}")
    
    finally:
        # 8. 清理：移除连接
        await manager.disconnect_v2(
            scope="session",
            channel_id=session_id,
            user_id=teacher_id,
            role=UserRole.TEACHER
        )
        print(f"✅ 教师 {teacher_id} 连接已清理（会话 {session_id}）")


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
    
    # 1. 验证Token并获取用户信息
    try:
        current_user = await deps.get_current_user_from_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Auth failed: {str(e)}")
        return
    
    # 2. 验证用户角色（只允许教师连接）
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        await websocket.close(code=1008, reason="Only teachers can connect to this endpoint")
        return
    
    # 3. 验证教案存在性和权限
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        await websocket.close(code=1008, reason="Lesson not found")
        return
    
    # 验证教师有权访问该教案（通过班级或教案创建者）
    teacher_id = cast(int, current_user.id)
    from app.services.realtime import fetch_teachers_by_lesson
    
    authorized_teacher_ids = await fetch_teachers_by_lesson(db, lesson_id)
    if teacher_id not in authorized_teacher_ids:
        await websocket.close(code=1008, reason="Access denied: Not authorized for this lesson")
        return
    
    # 4. 接受连接
    await websocket.accept()
    
    # 5. 注册连接
    await manager.connect_v2(
        websocket=websocket,
        scope="lesson",
        channel_id=lesson_id,
        user_id=teacher_id,
        role=UserRole.TEACHER
    )
    
    # 6. 发送初始连接确认
    await websocket.send_text(json.dumps({
        "type": "teacher_connected",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "lesson_id": lesson_id,
            "teacher_id": teacher_id,
        }
    }))
    
    try:
        # 7. 监听客户端消息（心跳、请求统计等）
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
                
                cell_id = message.get("data", {}).get("cell_id")
                
                if cell_id:
                    stats = await get_submission_statistics(
                        db,
                        cell_id=cell_id,
                        lesson_id=lesson_id,
                        session_id=None
                    )
                    
                    event = build_event(
                        type="submission_statistics_updated",
                        channel=Channel(scope="lesson", id=lesson_id),
                        delivery_mode="unicast",
                        data=stats
                    )
                    
                    await websocket.send_text(json.dumps(event))
    
    except WebSocketDisconnect:
        print(f"🔌 教师 {teacher_id} 断开连接（教案 {lesson_id}）")
    
    except Exception as e:
        print(f"❌ 教师 WebSocket 异常: {str(e)}")
    
    finally:
        # 8. 清理：移除连接
        await manager.disconnect_v2(
            scope="lesson",
            channel_id=lesson_id,
            user_id=teacher_id,
            role=UserRole.TEACHER
        )
        print(f"✅ 教师 {teacher_id} 连接已清理（教案 {lesson_id}）")

