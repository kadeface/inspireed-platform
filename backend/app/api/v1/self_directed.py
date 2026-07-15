"""
学生自主学习 API
"""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.models import User, UserRole
from app.schemas.self_directed import (
    SelfDirectedCompleteRequest,
    SelfDirectedCreateRequest,
    SelfDirectedSessionResponse,
    SelfDirectedSubmitPracticeRequest,
    SelfDirectedSubmitPracticeResponse,
)
from app.services.self_directed import SelfDirectedServiceError, self_directed_service

router = APIRouter()


def _require_student(current_user: User) -> None:
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    if role_value != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="仅学生用户可使用自主学习")


def _raise(exc: SelfDirectedServiceError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={"detail": exc.detail, "error_code": exc.error_code},
    ) from exc


@router.post("/sessions", response_model=SelfDirectedSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SelfDirectedCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfDirectedSessionResponse:
    _require_student(current_user)
    try:
        result = await self_directed_service.create_session(
            db,
            current_user,
            goal_text=payload.goal_text,
            mission_why=payload.mission_why,
            mission_success=payload.mission_success,
            tutor_style=payload.tutor_style,
        )
        return SelfDirectedSessionResponse(**result)
    except SelfDirectedServiceError as exc:
        _raise(exc)


@router.get("/sessions/{session_id}", response_model=SelfDirectedSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfDirectedSessionResponse:
    _require_student(current_user)
    try:
        session = await self_directed_service.get_session(db, session_id, current_user)
        return SelfDirectedSessionResponse(**self_directed_service.serialize(session))
    except SelfDirectedServiceError as exc:
        _raise(exc)


@router.post(
    "/sessions/{session_id}/practice",
    response_model=SelfDirectedSubmitPracticeResponse,
)
async def submit_practice(
    session_id: int,
    payload: SelfDirectedSubmitPracticeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfDirectedSubmitPracticeResponse:
    _require_student(current_user)
    try:
        session = await self_directed_service.get_session(db, session_id, current_user)
        result = await self_directed_service.submit_practice(
            db,
            session,
            answers=[item.model_dump() for item in payload.answers],
        )
        return SelfDirectedSubmitPracticeResponse(**result)
    except SelfDirectedServiceError as exc:
        _raise(exc)


@router.post("/sessions/{session_id}/complete", response_model=SelfDirectedSessionResponse)
async def complete_session(
    session_id: int,
    payload: SelfDirectedCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfDirectedSessionResponse:
    _require_student(current_user)
    try:
        session = await self_directed_service.get_session(db, session_id, current_user)
        result = await self_directed_service.complete_session(
            db,
            session,
            current_user,
            mastery_answer=payload.mastery_answer,
            practice_answers=[item.model_dump() for item in payload.practice_answers],
        )
        return SelfDirectedSessionResponse(**result)
    except SelfDirectedServiceError as exc:
        _raise(exc)
