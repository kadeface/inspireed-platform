"""
课堂会话 API
"""

from datetime import datetime, timedelta
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
from app.models.classroom_assistant import ClassroomMembership
from app.core.classroom_utils import get_user_classroom_ids, check_user_in_classroom
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
    UpdateDisplayModeRequest,
    SessionStatistics,
    StudentPendingSessionResponse,
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
        print(f"✅ 开始上课时自动显示第一个 cell: order={first_cell_order}, cell_id={first_cell.id}")
    else:
        # 如果没有找到 cell，保持为空（等待教师手动切换）
        session.current_cell_id = None # type: ignore[comparison-overlap]
        print(f"⚠️ 课程 {session_lesson_id} 没有 cell，等待教师手动切换")

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
    print(f"📢 已广播会话状态变化（会话 {session_id}）：pending -> active")
    
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
            print(f"📢 已广播内容初始化（会话 {session_id}），显示第一个 cell")

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

    # 🆕 通过 WebSocket 通知所有学生会话状态已变化
    await manager.broadcast_to_session(
        message={
            "type": "session_status_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
            }
        },
        session_id=session_id
    )
    print(f"📢 已广播会话状态变化（会话 {session_id}）：active -> paused")

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

    # 🆕 通过 WebSocket 通知所有学生会话状态已变化
    await manager.broadcast_to_session(
        message={
            "type": "session_status_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
            }
        },
        session_id=session_id
    )
    print(f"📢 已广播会话状态变化（会话 {session_id}）：paused -> active")

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

    # 🆕 幂等操作：如果会话已结束，直接返回（不报错）
    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        print(f"ℹ️ 会话 {session_id} 已经是 ENDED 状态，直接返回（幂等操作）")
        return session

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
            raise HTTPException(
                status_code=400, 
                detail=f"请先点击“开始上课”按钮，等待教师开始上课"
            )

        # 使用 display_cell_orders（直接传递 order 数组）
        if data.display_cell_orders is None:
            raise HTTPException(status_code=400, detail="必须提供 display_cell_orders 参数")
        
        # 🆕 记录原始状态，确保导航不会改变会话状态
        original_status = session.status
        print(f"🔍 导航前会话状态: {original_status}")
        
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
        
        # 🆕 验证状态未被错误修改
        # 使用 type: ignore 避免 SQLAlchemy ColumnElement 的 linter 警告
        if session.status != original_status:  # type: ignore[comparison-overlap]
            print(f"⚠️ 警告: 导航过程中会话状态发生了变化! 原始={original_status}, 当前={session.status}")
            # 这不应该发生，记录错误但继续执行
        
        print(f"✅ 导航成功: session_id={session_id}, display_cell_orders={data.display_cell_orders}, current_cell_id={session.current_cell_id}")
        print(f"📊 会话状态: status={session.status}, settings={session.settings}")
        
        # ✅ 新增：通过 WebSocket 广播变化
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
        
        print(f"📤 准备广播消息: {broadcast_message}")
        
        await ws_manager.broadcast_to_session(
            message=broadcast_message,
            session_id=session_id,
        )
        
        print(f"📢 已广播内容切换（会话 {session_id}），消息类型: cell_changed")
        
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


@router.post("/sessions/{session_id}/display-mode", response_model=ClassSessionResponse)
async def update_display_mode(
    session_id: int,
    data: UpdateDisplayModeRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """更新学生端显示模式（全屏/窗口）"""
    
    try:
        # 验证display_mode值
        if data.display_mode not in ["fullscreen", "window"]:
            raise HTTPException(status_code=400, detail="display_mode 必须是 'fullscreen' 或 'window'")
        
        print(f"🖥️ 更新显示模式: session_id={session_id}, display_mode={data.display_mode}")

        session = await db.get(ClassSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        session_teacher_id = cast(int, session.teacher_id)
        current_user_id = cast(int, current_user.id)
        if session_teacher_id != current_user_id:
            raise HTTPException(status_code=403, detail="无权操作")

        if session.status != ClassSessionStatus.ACTIVE:  # type: ignore[comparison-overlap]
            raise HTTPException(status_code=400, detail="只能在活跃会话中更新显示模式")
        
        # 保存 display_mode 到 settings
        new_settings = dict(session.settings) if session.settings else {} # type: ignore[assignment]
        new_settings["display_mode"] = data.display_mode # type: ignore[assignment]
        setattr(session, "settings", new_settings)
        
        await db.commit()
        await db.refresh(session)
        
        print(f"✅ 显示模式更新成功: session_id={session_id}, display_mode={data.display_mode}")
        
        # 通过 WebSocket 广播变化
        from app.services.websocket_manager import manager as ws_manager
        
        await ws_manager.broadcast_to_session(
            message={
                "type": "display_mode_changed",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "display_mode": data.display_mode,
                    "changed_by": {
                        "user_id": current_user.id,
                        "user_name": current_user.full_name or current_user.username,
                    }
                }
            },
            session_id=session_id,
        )
        
        print(f"📢 已广播显示模式变化（会话 {session_id}）")
        
        return session
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ 更新显示模式异常: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"更新显示模式失败: {str(e)}"
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

    # 🆕 获取学生所在班级ID（同时检查 User.classroom_id 和 ClassroomMembership）
    student_classroom_ids = set()
    
    # 方式1：检查 User.classroom_id（向后兼容）
    student_classroom_id = cast(Optional[int], current_user.classroom_id)
    if student_classroom_id:
        student_classroom_ids.add(student_classroom_id)
    
    # 方式2：检查 ClassroomMembership（支持多班级）
    membership_result = await db.execute(
        select(ClassroomMembership).where(
            and_(
                ClassroomMembership.user_id == current_user.id,
                ClassroomMembership.is_active == True,
            )
        )
    )
    memberships = membership_result.scalars().all()
    for membership in memberships:
        student_classroom_ids.add(membership.classroom_id)
    
    if not student_classroom_ids:
        # 如果学生没有分配班级，返回空列表
        return []

    # 计算48小时前的时间点
    cutoff_time = datetime.utcnow() - timedelta(hours=48)

    # 查询学生所在班级的最近48小时内的pending状态会话
    query = (
        select(ClassSession)
        .where(ClassSession.classroom_id.in_(list(student_classroom_ids)))
        .where(ClassSession.status == ClassSessionStatus.PENDING)
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
        .where(ClassSession.status == ClassSessionStatus.ACTIVE)
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


# ========== WebSocket 实时同步 ==========


# 导入 WebSocket 管理器
from app.services.websocket_manager import manager


# ========== 会话清理和检查 ==========


@router.post("/sessions/{session_id}/check-teacher-status")
async def check_teacher_status(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    检查会话的教师连接状态（用于定期检查）
    如果没有教师连接且会话处于活跃状态，自动结束会话
    """
    
    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 权限检查：教师可以检查自己的会话，管理员可以检查所有会话
    current_role = cast(UserRole, current_user.role)
    session_teacher_id = cast(int, session.teacher_id)
    current_user_id = cast(int, current_user.id)
    
    if current_role == UserRole.TEACHER and session_teacher_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权访问该会话")
    
    # 如果会话已结束，直接返回
    if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
        return {
            "session_id": session_id,
            "status": "ended",
            "has_teacher_connection": False,
            "message": "会话已结束"
        }
    
    # 检查是否有教师连接
    has_teacher = manager.has_teacher_connection("session", session_id)
    
    # 🚫 已禁用自动结束逻辑：教师应该主动点击"结束授课"按钮来结束会话
    # WebSocket 断开不等于教师离开（可能是网络波动、页面刷新等）
    # 过于激进的自动结束会导致误操作和用户体验问题
    
    # 🔍 仅检查和返回状态，不自动结束会话
    if not has_teacher and session.status in [ClassSessionStatus.ACTIVE, ClassSessionStatus.PAUSED]:  # type: ignore[comparison-overlap]
        print(f"⚠️ 会话 {session_id} 当前没有教师 WebSocket 连接（状态：{session.status}），但不会自动结束")
        # 返回警告状态，但不结束会话
        return {
            "session_id": session_id,
            "status": session.status,
            "has_teacher_connection": False,
            "warning": True,
            "message": "会话正常运行，但教师 WebSocket 未连接"
        }
    
    return {
        "session_id": session_id,
        "status": session.status,
        "has_teacher_connection": has_teacher,
        "message": "会话状态正常" if has_teacher else "会话正常但无教师连接"
    }


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
    
    print(f"🔌 WebSocket连接请求: session_id={session_id}, token_length={len(token) if token else 0}")
    
    # 🆕 手动处理 WebSocket CORS（CORSMiddleware 对 WebSocket 支持有限）
    origin = websocket.headers.get("origin")
    print(f"🔍 WebSocket Origin: {origin}")
    
    # 验证 Origin（允许局域网访问和 Cloud Studio 域名）
    allowed = False
    if origin:
        import re
        # 匹配 localhost、局域网 IP 和 Cloud Studio 域名
        # Cloud Studio URL 格式：https://{id}--{port}.{region}.cloudstudio.club
        pattern = r"^https?://((localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?|.*\.cloudstudio\.club|.*\.coding\.net)$"
        if re.match(pattern, origin):
            allowed = True
            print(f"✅ Origin 验证通过: {origin}")
        else:
            print(f"❌ Origin 验证失败: {origin}")
    else:
        # 如果没有 Origin 头（某些客户端可能不发送），也允许连接
        allowed = True
        print("⚠️ 没有 Origin 头，允许连接")
    
    # 先接受连接（必须先accept才能close并发送关闭原因）
    await websocket.accept()
    
    # 如果 CORS 验证失败，立即关闭连接
    if not allowed:
        print(f"❌ CORS 验证失败，关闭 WebSocket 连接")
        await websocket.close(code=1008, reason="CORS validation failed")
        return
    
    # 🆕 初始化 student_id 避免未绑定错误
    student_id: Optional[int] = None
    
    try:
        # 1. 验证Token并获取用户信息
        try:
            current_user = await deps.get_current_user_from_token(token, db)
            if not current_user:
                print(f"❌ Token验证失败: 用户不存在")
                await websocket.close(code=1008, reason="Invalid token")
                return
            print(f"✅ Token验证成功: user_id={current_user.id}, role={current_user.role}")
        except Exception as e:
            print(f"❌ Token验证异常: {str(e)}")
            await websocket.close(code=1008, reason=f"Auth failed: {str(e)}")
            return
        
        # 2. 验证用户角色（只允许学生连接，教师端使用HTTP API）
        current_role = cast(UserRole, current_user.role)
        if current_role != UserRole.STUDENT:
            print(f"❌ 角色验证失败: 只允许学生连接，当前角色={current_role}")
            await websocket.close(code=1008, reason="Only students can connect via WebSocket")
            return
        
        # 3. 验证会话存在性和权限
        session = await db.get(ClassSession, session_id)
        if not session:
            print(f"❌ 会话不存在: session_id={session_id}")
            await websocket.close(code=1008, reason="Session not found")
            return
        
        # 🆕 检查会话状态
        if session.status == ClassSessionStatus.ENDED:  # type: ignore[comparison-overlap]
            print(f"❌ 会话已结束: session_id={session_id}, status={session.status}")
            await websocket.close(code=1008, reason="Session has ended")
            return
        
        # 🆕 使用统一函数验证学生属于该班级
        classroom_id = cast(int, session.classroom_id)
        has_access = await check_user_in_classroom(db, current_user, classroom_id)
        
        if not has_access:
            print(f"❌ 权限验证失败: session_classroom_id={classroom_id}")
            await websocket.close(code=1008, reason="Access denied: Student does not belong to this classroom")
            return
        
        print(f"✅ 所有验证通过，开始建立连接: session_id={session_id}, student_id={current_user.id}")
        student_id = cast(int, current_user.id)
        
        # 5. 注册连接
        await manager.connect(websocket, session_id, student_id)
        print(f"✅ 连接已注册到管理器: session_id={session_id}, student_id={student_id}")
        
        # 6. 发送初始状态（当前会话状态）
        await send_initial_state(websocket, session, db)
        print(f"✅ 初始状态已发送: session_id={session_id}")
        
        # 7. 更新学生在线状态（数据库）
        await update_student_online_status(db, session_id, student_id, is_online=True)
        print(f"✅ 学生在线状态已更新: session_id={session_id}, student_id={student_id}")
        
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
        print(f"🔌 学生断开连接（会话 {session_id}），student_id={student_id if student_id else 'unknown'}")
    
    except Exception as e:
        # 异常断开
        import traceback
        print(f"❌ WebSocket异常: {str(e)}")
        print(traceback.format_exc())
    
    finally:
        # 9. 清理：移除连接、更新状态
        # 🆕 修复：确保 student_id 已定义再使用
        if student_id is not None:
            try:
                await manager.disconnect(session_id, student_id)
                await update_student_online_status(db, session_id, student_id, is_online=False)
                print(f"✅ 学生 {student_id} 连接已清理（会话 {session_id}）")
            except Exception as e:
                print(f"⚠️ 清理连接时出错: {str(e)}")


async def send_initial_state(websocket: WebSocket, session: ClassSession, db: AsyncSession):
    """发送初始状态给新连接的客户端"""
    
    # 加载关联信息（教师、课程、班级）
    session_lesson = await db.get(Lesson, cast(int, session.lesson_id))
    session_teacher = await db.get(User, cast(int, session.teacher_id))
    session_classroom = await db.get(Classroom, cast(int, session.classroom_id))
    
    message = {
        "type": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "session_id": session.id,
            "current_state": {
                "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
                "display_cell_orders": (session.settings or {}).get("display_cell_orders", []),
                "display_mode": (session.settings or {}).get("display_mode", "window"),
                "current_cell_id": session.current_cell_id,
                "current_activity_id": session.current_activity_id,
                # 🆕 添加教师和课程信息
                "teacher_name": session_teacher.full_name or session_teacher.username if session_teacher else None,
                "lesson_title": session_lesson.title if session_lesson else None,
                "classroom_name": session_classroom.name if session_classroom else None,
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
    
    # 🆕 手动处理 WebSocket CORS（CORSMiddleware 对 WebSocket 支持有限）
    origin = websocket.headers.get("origin")
    print(f"🔍 [教师WebSocket] Origin: {origin}")
    
    # 验证 Origin（允许局域网访问和 Cloud Studio 域名）
    allowed = False
    if origin:
        import re
        # 匹配 localhost、局域网 IP 和 Cloud Studio 域名
        pattern = r"^https?://((localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?|.*\.cloudstudio\.club|.*\.coding\.net)$"
        if re.match(pattern, origin):
            allowed = True
            print(f"✅ [教师WebSocket] Origin 验证通过: {origin}")
        else:
            print(f"❌ [教师WebSocket] Origin 验证失败: {origin}")
    else:
        allowed = True  # 没有 Origin 头也允许
        print("⚠️ [教师WebSocket] 没有 Origin 头，允许连接")
    
    # 先接受连接（必须先accept才能close）
    await websocket.accept()
    
    if not allowed:
        print(f"❌ [教师WebSocket] CORS 验证失败")
        await websocket.close(code=1008, reason="CORS validation failed")
        return
    
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
                from app.api.v1.activities import get_cell_uuid_from_db_id
                
                cell_id = message.get("data", {}).get("cell_id")  # 可能是 UUID 字符串或数字
                lesson_id = message.get("data", {}).get("lesson_id")
                
                if cell_id and lesson_id:
                    # get_submission_statistics 现在支持 UUID 字符串
                    stats = await get_submission_statistics(
                        db,
                        cell_id=cell_id,  # 支持 UUID 字符串
                        lesson_id=lesson_id,
                        session_id=session_id
                    )
                    
                    # 确保返回的 cell_id 是 UUID 格式（前端使用 UUID）
                    stats_cell_id = stats.get("cell_id")
                    if stats_cell_id is not None:
                        # 如果是数字 ID，转换为 UUID
                        try:
                            numeric_id = int(stats_cell_id)
                            # 是数字 ID，需要转换为 UUID
                            cell_uuid = await get_cell_uuid_from_db_id(db, numeric_id, lesson_id)
                            stats["cell_id"] = cell_uuid
                        except (ValueError, TypeError):
                            # 已经是 UUID 字符串，保持不变
                            pass
                    
                    event = build_event(
                        type="submission_statistics_updated",
                        channel=Channel(scope="session", id=session_id),
                        delivery_mode="unicast",
                        data=stats
                    )
                    
                    await websocket.send_text(json.dumps(event))
    
    except WebSocketDisconnect:
        print(f"🔌 教师 {teacher_id} 断开连接（会话 {session_id}）")
        
        # 🆕 检查是否还有其他教师连接（排除当前正在断开的教师）
        # 注意：此时连接还未断开，所以检查时需要排除当前教师
        has_other_teacher = manager.has_teacher_connection("session", session_id, exclude_user_id=teacher_id)
        
        # 🆕 修复：不要立即结束会话，因为教师可能只是WebSocket暂时断开（如网络波动、页面刷新等）
        # 会话应该由教师主动点击"结束课程"按钮来结束，或者由定时清理任务处理长时间无人的会话
        # 这样可以避免误结束正在进行的课程
        if not has_other_teacher:
            print(f"⚠️ 教师 WebSocket 断开，但不会自动结束会话 {session_id}（教师可能正在重连）")
            # 不自动结束会话，让教师有机会重新连接
            # 如果真的需要结束，教师可以主动点击"结束课程"按钮
            
            # 注释掉自动结束逻辑
            """
            try:
                # 重新获取会话最新状态
                session = await db.get(ClassSession, session_id)
                if session and session.status in [ClassSessionStatus.ACTIVE, ClassSessionStatus.PAUSED]:
                    print(f"⚠️ 教师异常退出，自动结束会话 {session_id}（状态：{session.status}）")
                    
                    # 更新会话状态为已结束
                    session.status = ClassSessionStatus.ENDED  # type: ignore[assignment]
                    session.ended_at = datetime.utcnow()  # type: ignore[assignment]
                    
                    # 计算时长
                    if session.actual_start:  # type: ignore[comparison-overlap]
                        duration = (session.ended_at - session.actual_start).total_seconds() / 60  # type: ignore[union-attr]
                        session.duration_minutes = int(duration)  # type: ignore[assignment]
                    
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
                        participation.is_active = False  # type: ignore[assignment]
                        participation.left_at = datetime.utcnow()  # type: ignore[assignment]
                    
                    await db.commit()
                    await db.refresh(session)
                    
                    # 通知所有学生会话已结束
                    await manager.broadcast_to_session(
                        message={
                            "type": "session_ended",
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": {
                                "session_id": session_id,
                                "ended_at": session.ended_at.isoformat() if session.ended_at else None,  # type: ignore[union-attr]
                                "reason": "teacher_disconnected",
                                "message": "教师已断开连接，课程已自动结束"
                            }
                        },
                        session_id=session_id
                    )
                    
                    print(f"✅ 已自动结束会话 {session_id} 并通知学生")
            except Exception as end_error:
                print(f"❌ 自动结束会话失败: {str(end_error)}")
                import traceback
                traceback.print_exc()
            """  # 自动结束逻辑已注释，避免误结束会话
    
    except Exception as e:
        print(f"❌ 教师 WebSocket 异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
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
    
    # 🆕 手动处理 WebSocket CORS（CORSMiddleware 对 WebSocket 支持有限）
    origin = websocket.headers.get("origin")
    print(f"🔍 [教师WebSocket-课后] Origin: {origin}")
    
    # 验证 Origin（允许局域网访问）
    allowed = False
    if origin:
        import re
        pattern = r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?$"
        if re.match(pattern, origin):
            allowed = True
    else:
        allowed = True
    
    # 先接受连接（必须先accept才能close）
    await websocket.accept()
    
    if not allowed:
        print(f"❌ [教师WebSocket-课后] CORS 验证失败")
        await websocket.close(code=1008, reason="CORS validation failed")
        return
    
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
                from app.api.v1.activities import get_cell_uuid_from_db_id
                
                cell_id = message.get("data", {}).get("cell_id")  # 可能是 UUID 字符串或数字
                lesson_id_param = message.get("data", {}).get("lesson_id")
                
                # 使用参数中的 lesson_id 或路径中的 lesson_id
                actual_lesson_id = lesson_id_param or lesson_id
                
                if cell_id and actual_lesson_id:
                    # get_submission_statistics 现在支持 UUID 字符串
                    stats = await get_submission_statistics(
                        db,
                        cell_id=cell_id,  # 支持 UUID 字符串
                        lesson_id=actual_lesson_id,
                        session_id=None
                    )
                    
                    # 确保返回的 cell_id 是 UUID 格式（前端使用 UUID）
                    stats_cell_id = stats.get("cell_id")
                    if stats_cell_id is not None:
                        # 如果是数字 ID，转换为 UUID
                        try:
                            numeric_id = int(stats_cell_id)
                            # 是数字 ID，需要转换为 UUID
                            cell_uuid = await get_cell_uuid_from_db_id(db, numeric_id, actual_lesson_id)
                            stats["cell_id"] = cell_uuid
                        except (ValueError, TypeError):
                            # 已经是 UUID 字符串，保持不变
                            pass
                    
                    event = build_event(
                        type="submission_statistics_updated",
                        channel=Channel(scope="lesson", id=actual_lesson_id),
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

