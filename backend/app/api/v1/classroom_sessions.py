"""
课堂会话 API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast
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
    
    # 确保 display_cell_ids 是列表类型
    if "display_cell_ids" in settings:
        if not isinstance(settings.get("display_cell_ids"), list):
            settings["display_cell_ids"] = []
    else:
        settings["display_cell_ids"] = []
    
    display_cell_ids = settings.get("display_cell_ids", [])
    
    print(f"📤 返回会话数据: session_id={session_id}, settings={settings}, display_cell_ids={display_cell_ids}, display_cell_ids_length={len(display_cell_ids) if isinstance(display_cell_ids, list) else 0}, display_cell_ids_type={type(display_cell_ids)}")

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
        # 确保 settings 被正确包含，并包含 display_cell_ids
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

    # 确保 settings 和 display_cell_ids 被正确序列化
    session_list = []
    for session in sessions:
        # 确保 settings 被正确序列化
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
        
        # 确保 display_cell_ids 是列表类型
        if "display_cell_ids" in settings:
            if not isinstance(settings.get("display_cell_ids"), list):
                settings["display_cell_ids"] = []
        else:
            settings["display_cell_ids"] = []
        
        # 创建响应字典，确保 settings 被正确包含
        session_dict = {
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
            "settings": settings,  # 确保 settings 被正确包含
        }
        
        session_list.append(session_dict)

    return session_list


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

    if session.status != ClassSessionStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"会话状态为 {session.status}，无法开始")

    # 更新状态
    session.status = ClassSessionStatus.ACTIVE
    session.actual_start = datetime.utcnow()

    # 默认不显示任何Cell，等待教师手动切换
    # 这样更符合实际教学流程：教师可以先准备，然后再切换给学生看
    session.current_cell_id = None

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

    if session.status != ClassSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="只能暂停进行中的会话")

    session.status = ClassSessionStatus.PAUSED
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

    if session.status != ClassSessionStatus.PAUSED:
        raise HTTPException(status_code=400, detail="只能继续已暂停的会话")

    session.status = ClassSessionStatus.ACTIVE
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

    if session.status == ClassSessionStatus.ENDED:
        raise HTTPException(status_code=400, detail="会话已结束")

    # 更新状态
    session.status = ClassSessionStatus.ENDED
    session.ended_at = datetime.utcnow()

    # 计算时长
    if session.actual_start:
        duration = (session.ended_at - session.actual_start).total_seconds() / 60
        session.duration_minutes = int(duration)

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
        participation.is_active = False
        participation.left_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    return session


# ========== 内容导航 ==========


@router.post("/sessions/{session_id}/navigate", response_model=ClassSessionResponse)
async def navigate_to_cell(
    session_id: int,
    data: NavigateToCellRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """切换当前Cell（cell_id=0表示隐藏所有内容，也可以通过cell_order来查找）"""
    
    try:
        print(f"🎯 导航请求: session_id={session_id}, cell_id={data.cell_id}, cell_order={data.cell_order}, action={data.action}, multi_select={data.multi_select}")

        session = await db.get(ClassSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 重要：刷新 session 以确保获取最新的 settings（包括 display_cell_ids）
        await db.refresh(session, ["settings"])
        print(f"🔄 刷新后的 session.settings: {session.settings}")

        session_teacher_id = cast(int, session.teacher_id)
        current_user_id = cast(int, current_user.id)
        if session_teacher_id != current_user_id:
            raise HTTPException(status_code=403, detail="无权操作")

        if session.status != ClassSessionStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="只能在活跃会话中切换Cell")

        # 如果cell_id为0且没有cell_order，且不是多选模式，表示隐藏所有内容
        # 注意：如果提供了cell_order，即使cell_id为0，也应该尝试通过order查找Cell
        if (not data.cell_id or data.cell_id == 0) and data.cell_order is None and not data.multi_select:
            session.current_cell_id = None
            # 清除多选列表
            # 重要：创建新的 settings 字典，以确保 SQLAlchemy 检测到变更
            new_settings = dict(session.settings) if session.settings else {}
            new_settings["display_cell_ids"] = []
            setattr(session, "settings", new_settings)
            await db.commit()
            await db.refresh(session)
            return session
        
        # 初始化 settings 和 display_cell_ids
        # 重要：确保从刷新后的 session.settings 中获取最新的 display_cell_ids
        if session.settings is None:
            session.settings = {}
        
        # 获取当前的 display_cell_ids（确保是列表类型）
        raw_display_cell_ids = session.settings.get("display_cell_ids")
        if isinstance(raw_display_cell_ids, list):
            display_cell_ids = list(raw_display_cell_ids)  # 创建副本，避免直接修改原列表
        else:
            display_cell_ids = []
        
        print(f"📋 当前 display_cell_ids: {display_cell_ids}, 操作: {data.action}, 多选: {data.multi_select}")

        # 首先尝试通过cell_id查找
        cell: Optional[Cell] = None
        if data.cell_id:
            cell = await db.get(Cell, data.cell_id)
        
        # 如果通过cell_id找不到，且提供了cell_order，尝试通过order查找
        if not cell and data.cell_order is not None:
            session_lesson_id = cast(int, session.lesson_id)
            result = await db.execute(
                select(Cell).where(
                    and_(
                        Cell.lesson_id == session_lesson_id,
                        Cell.order == data.cell_order,
                    )
                )
            )
            cell = result.scalar_one_or_none()
        
        # 如果仍然找不到，尝试从lesson.content中查找并创建
        if not cell and data.cell_order is not None:
            session_lesson_id = cast(int, session.lesson_id)
            lesson = await db.get(Lesson, session_lesson_id)
            print(f"🔍 尝试从lesson.content创建cell: lesson_id={session_lesson_id}, cell_order={data.cell_order}")
            if not lesson:
                print(f"❌ Lesson不存在: {session_lesson_id}")
            elif not lesson.content:
                print(f"❌ Lesson.content为空: {session_lesson_id}")
            else:
                lesson_content = cast(List[Dict[str, Any]], lesson.content)
                print(f"📋 Lesson.content长度: {len(lesson_content)}, 尝试访问索引: {data.cell_order}")
                if data.cell_order < 0:
                    print(f"❌ cell_order不能为负数: {data.cell_order}")
                elif data.cell_order >= len(lesson_content):
                    print(f"❌ cell_order超出范围: {data.cell_order} >= {len(lesson_content)}")
                else:
                    cell_data = lesson_content[data.cell_order]
                    print(f"✅ 找到cell_data: {cell_data}")
                    cell_type_str = cell_data.get("type") or cell_data.get("cell_type")
                    print(f"🔍 cell_type_str: {cell_type_str}")
                    
                    # 导入CellType
                    from app.models.cell import CellType
                    
                    # 尝试解析cell_type（确保转换为小写以匹配枚举值）
                    try:
                        if cell_type_str:
                            # 将字符串转换为小写，因为枚举值是小写的（如 "activity" 而不是 "ACTIVITY"）
                            cell_type_str_lower = cell_type_str.lower()
                            # 尝试直接使用小写字符串
                            try:
                                cell_type = CellType(cell_type_str_lower)
                                print(f"✅ 解析cell_type成功（小写）: {cell_type}")
                            except (ValueError, TypeError):
                                # 如果小写失败，尝试原始值
                                cell_type = CellType(cell_type_str)
                                print(f"✅ 解析cell_type成功（原始值）: {cell_type}")
                        else:
                            cell_type = CellType.TEXT
                            print(f"✅ 使用默认cell_type: {cell_type}")
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ 解析cell_type失败: {e}, 使用默认值TEXT")
                        cell_type = CellType.TEXT
                    
                    # 检查是否已经有相同order的cell
                    existing_result = await db.execute(
                        select(Cell).where(
                            and_(
                                Cell.lesson_id == session_lesson_id,
                                Cell.order == data.cell_order,
                            )
                        )
                    )
                    existing_cell = existing_result.scalar_one_or_none()
                    
                    if existing_cell:
                        print(f"✅ 找到已存在的cell: id={existing_cell.id}")
                        cell = existing_cell
                    else:
                        # 创建新的cell记录
                        print(f"📝 创建新的cell: order={data.cell_order}, type={cell_type}")
                        try:
                            # 确保 content 是字典类型
                            content = cell_data.get("content")
                            if not isinstance(content, dict):
                                print(f"⚠️ content不是字典类型，转换为字典: {type(content)}")
                                content = {} if content is None else {"data": content}
                            
                            # 确保 config 是字典类型或 None
                            config = cell_data.get("config")
                            if config is not None and not isinstance(config, dict):
                                print(f"⚠️ config不是字典类型，转换为字典: {type(config)}")
                                config = {"data": config} if config is not None else {}
                            
                            print(f"📦 准备创建cell: title={cell_data.get('title')}, content={type(content)}, config={type(config)}")
                            
                            new_cell = Cell(
                                lesson_id=session_lesson_id,
                                cell_type=cell_type,
                                title=cell_data.get("title"),
                                content=content,
                                config=config or {},
                                order=data.cell_order,
                                editable=cell_data.get("editable", False),
                            )
                            db.add(new_cell)
                            await db.flush()  # 获取ID但不提交
                            cell = new_cell
                            print(f"✅ 创建cell成功: id={cell.id}")
                        except Exception as e:
                            print(f"❌ 创建cell失败: {type(e).__name__}: {str(e)}")
                            import traceback
                            print(traceback.format_exc())
                            raise
        
        # 如果仍然没有cell，返回错误
        if not cell:
            raise HTTPException(
                status_code=404,
                detail=f"Cell不存在 (cell_id: {data.cell_id}, order: {data.cell_order})"
            )
        
        # 验证Cell属于该教案
        cell_lesson_id = cast(int, cell.lesson_id)
        session_lesson_id = cast(int, session.lesson_id)
        if cell_lesson_id != session_lesson_id:
            raise HTTPException(status_code=400, detail="Cell不属于该教案")

        cell_db_id = cast(int, cell.id)
        action = data.action or "toggle"
        
        # 处理多选逻辑
        if data.multi_select or action != "toggle":
            # 多选模式：添加或移除 Cell
            if action == "add":
                if cell_db_id not in display_cell_ids:
                    display_cell_ids.append(cell_db_id)
            elif action == "remove":
                if cell_db_id in display_cell_ids:
                    display_cell_ids.remove(cell_db_id)
            elif action == "toggle":
                # 切换：如果存在则移除，否则添加
                if cell_db_id in display_cell_ids:
                    display_cell_ids.remove(cell_db_id)
                else:
                    display_cell_ids.append(cell_db_id)
            
            # 重要：创建新的 settings 字典，以确保 SQLAlchemy 检测到变更
            # 直接修改字典内部值可能不会被 SQLAlchemy 检测到
            new_settings = dict(session.settings) if session.settings else {}
            new_settings["display_cell_ids"] = list(display_cell_ids)  # 创建列表副本
            setattr(session, "settings", new_settings)
            
            print(f"✅ 更新后的 display_cell_ids: {display_cell_ids}, 长度: {len(display_cell_ids)}")
            
            # 设置当前显示的 Cell（用于兼容性，显示最后一个或第一个）
            if len(display_cell_ids) > 0:
                session.current_cell_id = display_cell_ids[-1]  # 使用最后一个作为主显示
                print(f"✅ 设置 current_cell_id 为: {session.current_cell_id}")
            else:
                session.current_cell_id = None
                print(f"✅ 清空 current_cell_id")
        else:
            # 单选模式（向后兼容）：只显示单个 Cell
            session.current_cell_id = cell_db_id
            # 重要：创建新的 settings 字典，以确保 SQLAlchemy 检测到变更
            new_settings = dict(session.settings) if session.settings else {}
            new_settings["display_cell_ids"] = [cell_db_id]
            setattr(session, "settings", new_settings)
            display_cell_ids = [cell_db_id]  # 确保变量也被更新
        
        # 重要：保存更新后的 display_cell_ids，以便在刷新后使用（如果刷新后丢失）
        saved_display_cell_ids = list(display_cell_ids)  # 创建副本
        
        await db.commit()
        
        # 刷新 session 以获取最新的数据（包括 settings）
        await db.refresh(session, ["settings"])
        
        # 确保 settings 是最新的（刷新后重新获取）
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
        
        # 确保 display_cell_ids 是列表类型
        # 重要：优先使用刷新后的数据，但如果丢失，使用保存的值
        if "display_cell_ids" in settings:
            display_cell_ids_value = settings.get("display_cell_ids")
            if not isinstance(display_cell_ids_value, list):
                # 如果不是列表类型，修复它，但使用保存的值
                print(f"⚠️ display_cell_ids 不是列表类型: {type(display_cell_ids_value)}, 值: {display_cell_ids_value}")
                if saved_display_cell_ids:
                    print(f"✅ 使用保存的 display_cell_ids: {saved_display_cell_ids}")
                    settings["display_cell_ids"] = saved_display_cell_ids
                    display_cell_ids = saved_display_cell_ids
                else:
                    settings["display_cell_ids"] = []
                    display_cell_ids = []
            else:
                # 是列表类型，直接使用
                display_cell_ids = display_cell_ids_value
                # 如果刷新后的数据是空数组，但保存的值不是空数组，使用保存的值
                if not display_cell_ids and saved_display_cell_ids:
                    print(f"⚠️ 刷新后的 display_cell_ids 是空数组，但保存的值不是，使用保存的值: {saved_display_cell_ids}")
                    settings["display_cell_ids"] = saved_display_cell_ids
                    display_cell_ids = saved_display_cell_ids
        else:
            # 如果不存在，可能是刷新后丢失，使用保存的值
            if saved_display_cell_ids:
                print(f"⚠️ settings 中没有 display_cell_ids，使用保存的值: {saved_display_cell_ids}")
                settings["display_cell_ids"] = saved_display_cell_ids
                display_cell_ids = saved_display_cell_ids
            else:
                # 如果还是不存在，尝试从 session.settings 直接获取
                if hasattr(session, 'settings') and session.settings and isinstance(session.settings, dict):
                    direct_display_cell_ids = session.settings.get("display_cell_ids")
                    if isinstance(direct_display_cell_ids, list) and direct_display_cell_ids:
                        print(f"⚠️ settings 中没有 display_cell_ids，但从 session.settings 直接获取到: {direct_display_cell_ids}")
                        settings["display_cell_ids"] = direct_display_cell_ids
                        display_cell_ids = direct_display_cell_ids
                    else:
                        print(f"⚠️ display_cell_ids 不存在于 settings 中，使用空数组")
                        settings["display_cell_ids"] = []
                        display_cell_ids = []
                else:
                    print(f"⚠️ display_cell_ids 不存在且无法从 session.settings 获取，使用空数组")
                    settings["display_cell_ids"] = []
                    display_cell_ids = []
        
        print(f"✅ 导航成功: session_id={session_id}, current_cell_id={session.current_cell_id}")
        print(f"📊 刷新后的 settings (raw): {raw_settings}")
        print(f"📊 刷新后的 settings (processed): {settings}")
        print(f"📊 display_cell_ids: {display_cell_ids}, 长度: {len(display_cell_ids) if isinstance(display_cell_ids, list) else 0}, 类型: {type(display_cell_ids)}")
        
        # 显式构建响应字典，确保 settings 被正确包含（避免 Pydantic 序列化问题）
        # 加载关联信息
        session_lesson = await db.get(Lesson, cast(int, session.lesson_id))
        session_classroom = await db.get(Classroom, cast(int, session.classroom_id))
        session_teacher = await db.get(User, session_teacher_id)
        
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
            "settings": settings,  # 确保 settings 被正确包含，并包含 display_cell_ids
        }
        
        print(f"📤 返回导航响应: settings={settings}, display_cell_ids={display_cell_ids}, display_cell_ids_length={len(display_cell_ids) if isinstance(display_cell_ids, list) else 0}")
        
        return response_dict
    
    except HTTPException:
        # 重新抛出 HTTP 异常（这些异常已经有正确的状态码）
        raise
    except Exception as e:
        # 捕获其他异常，记录详细信息
        import traceback
        print(f"❌ 导航异常: {type(e).__name__}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"导航失败: {str(e)}"
        )


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

    if session.status != ClassSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="只能在活跃会话中开始活动")

    # 验证Cell存在且是活动类型
    cell = await db.get(Cell, data.cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell不存在")

    from app.models.cell import CellType
    cell_type = cast(CellType, cell.cell_type)
    if cell_type != CellType.ACTIVITY:
        raise HTTPException(status_code=400, detail="该Cell不是活动类型")

    session.current_activity_id = data.cell_id
    session.current_cell_id = data.cell_id  # 同时设置为当前Cell
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

    session.current_activity_id = None
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

    if session.status == ClassSessionStatus.ENDED:
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
        existing.is_active = True
        existing.last_active_at = datetime.utcnow()
        if session.current_cell_id:
            existing.current_cell_id = session.current_cell_id
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
    session.total_students = (session.total_students or 0) + 1
    session.active_students = (session.active_students or 0) + 1

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

    participation.is_active = False
    participation.left_at = datetime.utcnow()

    # 更新会话统计
    session = await db.get(ClassSession, session_id)
    if session:
        session.active_students = max((session.active_students or 0) - 1, 0)

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
    active_students = sum(1 for p in participations if p.is_active)
    
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

