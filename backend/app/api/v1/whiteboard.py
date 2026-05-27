"""
课堂白板与分组 API
"""

import random
from datetime import datetime
from typing import Any, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.classroom_session import ClassSession, StudentSessionParticipation
from app.models.session_group import SessionGroup, SessionGroupMember
from app.models.user import User, UserRole
from app.schemas.whiteboard import (
    PatchMemberGroupRequest,
    SessionGroupMemberOut,
    SessionGroupsResponse,
    SetupGroupsRequest,
    WhiteboardModeRequest,
    WhiteboardStateResponse,
)
from app.services.whiteboard import default_document, get_or_create_state, set_whiteboard_mode
from app.services.websocket_manager import manager as ws_manager

router = APIRouter()


async def _get_session_or_404(db: AsyncSession, session_id: int) -> ClassSession:
    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


async def _require_teacher(session: ClassSession, user: User) -> None:
    if user.role != UserRole.TEACHER or session.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="仅授课教师可操作")


async def _broadcast(session_id: int, event_type: str, data: dict) -> None:
    msg = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }
    try:
        await ws_manager.broadcast_to_session(message=msg, session_id=session_id)
        await ws_manager.send_to_teacher(event=msg, scope="session", channel_id=session_id)
    except Exception:
        pass


@router.get("/sessions/{session_id}/groups", response_model=SessionGroupsResponse)
async def get_session_groups(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _get_session_or_404(db, session_id)
    groups_result = await db.execute(
        select(SessionGroup)
        .where(SessionGroup.session_id == session_id)
        .order_by(SessionGroup.group_index)
    )
    groups = [
        {"id": g.id, "group_index": g.group_index, "label": g.label}
        for g in groups_result.scalars().all()
    ]
    members_result = await db.execute(
        select(SessionGroupMember)
        .where(SessionGroupMember.session_id == session_id)
        .options(selectinload(SessionGroupMember.user))
    )
    members: List[SessionGroupMemberOut] = []
    for m in members_result.scalars().all():
        name = None
        if m.user:
            name = getattr(m.user, "full_name", None) or getattr(m.user, "username", None)
        members.append(
            SessionGroupMemberOut(
                user_id=m.user_id,
                group_index=m.group_index,
                display_name=name,
            )
        )
    return SessionGroupsResponse(session_id=session_id, groups=groups, members=members)


@router.put("/sessions/{session_id}/groups/setup", response_model=SessionGroupsResponse)
async def setup_session_groups(
    session_id: int,
    body: SetupGroupsRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    session = await _get_session_or_404(db, session_id)
    await _require_teacher(session, current_user)

    await db.execute(delete(SessionGroupMember).where(SessionGroupMember.session_id == session_id))
    await db.execute(delete(SessionGroup).where(SessionGroup.session_id == session_id))

    for i in range(1, body.group_count + 1):
        db.add(
            SessionGroup(
                session_id=session_id,
                group_index=i,
                label=f"第 {i} 组",
            )
        )

    student_ids: List[int] = []
    if body.random_assign:
        part_result = await db.execute(
            select(StudentSessionParticipation.student_id).where(
                StudentSessionParticipation.session_id == session_id
            )
        )
        student_ids = [int(r[0]) for r in part_result.all()]
        random.shuffle(student_ids)
        for idx, sid in enumerate(student_ids):
            gi = (idx % body.group_count) + 1
            db.add(
                SessionGroupMember(
                    session_id=session_id,
                    user_id=sid,
                    group_index=gi,
                )
            )

    await db.commit()
    resp = await get_session_groups(session_id, db, current_user)
    await _broadcast(
        session_id,
        "whiteboard.groups",
        {"session_id": session_id, "groups": resp.groups, "members": [m.model_dump() for m in resp.members]},
    )
    return resp


@router.patch("/sessions/{session_id}/groups/members/{user_id}", response_model=SessionGroupMemberOut)
async def patch_member_group(
    session_id: int,
    user_id: int,
    body: PatchMemberGroupRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    session = await _get_session_or_404(db, session_id)
    await _require_teacher(session, current_user)

    result = await db.execute(
        select(SessionGroupMember).where(
            and_(
                SessionGroupMember.session_id == session_id,
                SessionGroupMember.user_id == user_id,
            )
        )
    )
    m = result.scalar_one_or_none()
    if not m:
        m = SessionGroupMember(
            session_id=session_id,
            user_id=user_id,
            group_index=body.group_index,
        )
        db.add(m)
    else:
        m.group_index = body.group_index  # type: ignore[assignment]
    await db.commit()

    out = SessionGroupMemberOut(user_id=user_id, group_index=body.group_index)
    await _broadcast(
        session_id,
        "whiteboard.groups",
        {"session_id": session_id, "members": [out.model_dump()]},
    )
    return out


@router.get(
    "/sessions/{session_id}/whiteboard/{cell_id}/state",
    response_model=WhiteboardStateResponse,
)
async def get_whiteboard_state(
    session_id: int,
    cell_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _get_session_or_404(db, session_id)
    state = await get_or_create_state(db, session_id, cell_id)
    return WhiteboardStateResponse(
        session_id=session_id,
        cell_id=cell_id,
        document=state.document or default_document(),
        version=state.version,
        updated_at=state.updated_at,
    )


@router.patch(
    "/sessions/{session_id}/whiteboard/{cell_id}/mode",
    response_model=WhiteboardStateResponse,
)
async def patch_whiteboard_mode(
    session_id: int,
    cell_id: int,
    body: WhiteboardModeRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    session = await _get_session_or_404(db, session_id)
    await _require_teacher(session, current_user)
    result = await set_whiteboard_mode(db, session_id, cell_id, body.mode)
    await _broadcast(
        session_id,
        "whiteboard.mode",
        {"session_id": session_id, **result},
    )
    state = await get_or_create_state(db, session_id, cell_id)
    return WhiteboardStateResponse(
        session_id=session_id,
        cell_id=cell_id,
        document=state.document or default_document(),
        version=state.version,
        updated_at=state.updated_at,
    )
