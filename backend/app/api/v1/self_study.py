"""
学生自学拍题伴学 API
"""

from __future__ import annotations

from typing import Optional, cast

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.models import User, UserRole
from app.schemas.self_study import (
    SelfStudyAppendTurnRequest,
    SelfStudyCompleteRequest,
    SelfStudyCreateSessionRequest,
    SelfStudyHandoffCreateRequest,
    SelfStudyHandoffResponse,
    SelfStudyHistoryListResponse,
    SelfStudySessionResponse,
    SelfStudyTeacherHandoffDetailResponse,
    SelfStudyTeacherHandoffListResponse,
    SelfStudyTeacherHandoffReplyRequest,
    SelfStudyTeacherHandoffReplyResponse,
    SelfStudyUploadCheckResponse,
)
from app.services.self_study import SelfStudyServiceError, self_study_service

router = APIRouter()


def _raise_service_error(exc: SelfStudyServiceError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "suggestions": exc.suggestions,
        },
    ) from exc


def _require_student(current_user: User) -> None:
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    if role_value != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="仅学生用户可使用自学拍题功能")


def _require_teacher(current_user: User) -> None:
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    if role_value not in {UserRole.TEACHER.value, UserRole.ADMIN.value}:
        raise HTTPException(status_code=403, detail="仅教师或管理员可访问教师处理队列")


@router.post(
    "/uploads/check",
    response_model=SelfStudyUploadCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
async def check_upload(
    request: Request,
    file: UploadFile = File(...),
    source: Optional[str] = Form(default="upload"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudyUploadCheckResponse:
    _require_student(current_user)
    try:
        result = await self_study_service.check_upload(
            db,
            request,
            file,
            current_user,
            source=source,
        )
        return SelfStudyUploadCheckResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/sessions", response_model=SelfStudySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: Request,
    payload: SelfStudyCreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudySessionResponse:
    _require_student(current_user)
    try:
        result = await self_study_service.create_session(
            db,
            request,
            current_user,
            upload_token=payload.upload_token,
            voice_transcript_raw=payload.voice_transcript_raw,
            question_text_confirmed=payload.question_text_confirmed,
            input_mode=payload.input_mode,
            tutor_style=payload.tutor_style,
        )
        return SelfStudySessionResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.get("/sessions/{session_id}", response_model=SelfStudySessionResponse)
async def get_session(
    request: Request,
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudySessionResponse:
    _require_student(current_user)
    try:
        session = await self_study_service.get_session(db, session_id, current_user)
        result = await self_study_service.serialize_session(session, request, db)
        return SelfStudySessionResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/sessions/{session_id}/turns", response_model=SelfStudySessionResponse)
async def append_turn(
    request: Request,
    session_id: int,
    payload: SelfStudyAppendTurnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudySessionResponse:
    _require_student(current_user)
    try:
        session = await self_study_service.get_session(db, session_id, current_user)
        result = await self_study_service.append_turn(
            db,
            request,
            session,
            current_user,
            voice_transcript_raw=payload.voice_transcript_raw,
            question_text_confirmed=payload.question_text_confirmed,
            input_mode=payload.input_mode,
        )
        return SelfStudySessionResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/sessions/{session_id}/reupload", response_model=SelfStudySessionResponse)
async def reupload_revision(
    request: Request,
    session_id: int,
    file: UploadFile = File(...),
    voice_transcript_raw: Optional[str] = Form(default=None),
    question_text_confirmed: Optional[str] = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudySessionResponse:
    _require_student(current_user)
    try:
        session = await self_study_service.get_session(db, session_id, current_user)
        result = await self_study_service.reupload_revision(
            db,
            request,
            session,
            current_user,
            file=file,
            voice_transcript_raw=voice_transcript_raw,
            question_text_confirmed=question_text_confirmed,
        )
        return SelfStudySessionResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/sessions/{session_id}/unlock-explanation", response_model=SelfStudySessionResponse)
async def unlock_explanation(
    request: Request,
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudySessionResponse:
    _require_student(current_user)
    try:
        session = await self_study_service.get_session(db, session_id, current_user)
        result = await self_study_service.unlock_explanation(
            db,
            request,
            session,
            current_user,
        )
        return SelfStudySessionResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/sessions/{session_id}/handoff", response_model=SelfStudyHandoffResponse, status_code=status.HTTP_201_CREATED)
async def create_handoff(
    request: Request,
    session_id: int,
    payload: SelfStudyHandoffCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudyHandoffResponse:
    _require_student(current_user)
    try:
        session = await self_study_service.get_session(db, session_id, current_user)
        result = await self_study_service.create_handoff(
            db,
            request,
            session,
            current_user,
            student_last_confusion=payload.student_last_confusion,
        )
        return SelfStudyHandoffResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/sessions/{session_id}/complete", response_model=SelfStudySessionResponse)
async def complete_session(
    request: Request,
    session_id: int,
    payload: SelfStudyCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudySessionResponse:
    _require_student(current_user)
    try:
        session = await self_study_service.get_session(db, session_id, current_user)
        result = await self_study_service.complete_session(
            db,
            request,
            session,
            current_user,
            summary_before=payload.summary_before,
            summary_after=payload.summary_after,
        )
        return SelfStudySessionResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.get("/student/history", response_model=SelfStudyHistoryListResponse)
async def list_student_history(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    result_judgment: Optional[str] = Query(default=None),
    session_phase: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudyHistoryListResponse:
    _require_student(current_user)
    result = await self_study_service.list_student_sessions(
        db,
        request,
        current_user,
        page=page,
        page_size=page_size,
        result_judgment=result_judgment,
        session_phase=session_phase,
    )
    return SelfStudyHistoryListResponse(**result)


@router.get("/teacher/handoffs", response_model=SelfStudyTeacherHandoffListResponse)
async def list_teacher_handoffs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudyTeacherHandoffListResponse:
    _require_teacher(current_user)
    result = await self_study_service.list_teacher_handoffs(
        db,
        page=page,
        page_size=page_size,
        status=status,
    )
    return SelfStudyTeacherHandoffListResponse(**result)


@router.get("/teacher/handoffs/{handoff_id}", response_model=SelfStudyTeacherHandoffDetailResponse)
async def get_teacher_handoff(
    request: Request,
    handoff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudyTeacherHandoffDetailResponse:
    _require_teacher(current_user)
    try:
        result = await self_study_service.get_teacher_handoff(db, request, handoff_id)
        return SelfStudyTeacherHandoffDetailResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)


@router.post("/teacher/handoffs/{handoff_id}/reply", response_model=SelfStudyTeacherHandoffReplyResponse)
async def reply_teacher_handoff(
    request: Request,
    handoff_id: int,
    payload: SelfStudyTeacherHandoffReplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SelfStudyTeacherHandoffReplyResponse:
    _require_teacher(current_user)
    try:
        result = await self_study_service.reply_handoff(
            db,
            request,
            handoff_id,
            current_user,
            reply_text=payload.reply_text,
            annotated_image_storage_key=payload.annotated_image_storage_key,
        )
        return SelfStudyTeacherHandoffReplyResponse(**result)
    except SelfStudyServiceError as exc:
        _raise_service_error(exc)
