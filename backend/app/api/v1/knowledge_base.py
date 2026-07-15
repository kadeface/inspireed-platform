"""
学生个人知识库 API
"""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.models import User, UserRole
from app.schemas.knowledge_base import (
    KnowledgeBaseNoteContent,
    KnowledgeBaseNoteListResponse,
    KnowledgeBasePriorResponse,
)
from app.services.knowledge_base import KnowledgeBaseError, knowledge_base_service
from app.services.knowledge_query import knowledge_query_service

router = APIRouter()


def _require_student(current_user: User) -> None:
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    if role_value != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="仅学生用户可访问个人知识库")


def _raise_kb_error(exc: KnowledgeBaseError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={"detail": exc.detail, "error_code": exc.error_code},
    ) from exc


@router.get("/notes", response_model=KnowledgeBaseNoteListResponse)
async def list_notes(
    current_user: User = Depends(get_current_active_user),
) -> KnowledgeBaseNoteListResponse:
    _require_student(current_user)
    try:
        result = knowledge_base_service.list_notes(current_user.id)
        return KnowledgeBaseNoteListResponse(**result)
    except KnowledgeBaseError as exc:
        _raise_kb_error(exc)


@router.get("/notes/content", response_model=KnowledgeBaseNoteContent)
async def get_note_content(
    path: str = Query(..., min_length=1, description="vault 相对路径，如 wiki/hot.md"),
    current_user: User = Depends(get_current_active_user),
) -> KnowledgeBaseNoteContent:
    _require_student(current_user)
    try:
        result = knowledge_base_service.get_note(current_user.id, path)
        return KnowledgeBaseNoteContent(**result)
    except KnowledgeBaseError as exc:
        _raise_kb_error(exc)


@router.get("/prior", response_model=KnowledgeBasePriorResponse)
async def get_prior_knowledge(
    q: str = Query(..., min_length=1, max_length=800),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> KnowledgeBasePriorResponse:
    _require_student(current_user)
    try:
        summary = await knowledge_query_service.query_prior_knowledge(
            db,
            current_user.id,
            q,
        )
        return KnowledgeBasePriorResponse(
            query=q,
            prior_summary=summary,
            has_prior=bool(summary.strip()),
        )
    except KnowledgeBaseError as exc:
        _raise_kb_error(exc)
