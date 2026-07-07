"""
学生自学拍题伴学服务
"""

from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

import httpx
from fastapi import Request, UploadFile
from jose import JWTError, jwt
from PIL import Image
from sqlalchemy import func, inspect as sa_inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import User
from app.models.self_study import (
    SelfStudyErrorType,
    SelfStudyHandoffStatus,
    SelfStudyReadabilityStatus,
    SelfStudyResultJudgment,
    SelfStudySession,
    SelfStudySessionPhase,
    SelfStudySpeaker,
    SelfStudyTeacherHandoff,
    SelfStudyTurn,
    SelfStudyTurnKind,
)
from app.services.ai_settings import AIChannelRuntimeConfig, ai_settings_service
from app.services.upload import upload_service
from app.utils.resource_url import filename_to_url, url_to_filename


READABILITY_SUGGESTIONS = [
    "请确保图片只包含一道题。",
    "请同时拍到题干和你的作答过程。",
    "请保持图片清晰、无遮挡、无明显反光。",
]


class SelfStudyServiceError(Exception):
    def __init__(
        self,
        detail: str,
        error_code: str,
        *,
        status_code: int = 400,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        self.suggestions = suggestions or []


@dataclass
class ReadabilityCheckResult:
    accepted: bool
    error_code: Optional[str] = None
    detail: Optional[str] = None
    suggestions: Optional[List[str]] = None
    problem_text_preview: Optional[str] = None
    student_work_text_preview: Optional[str] = None


class SelfStudyService:
    def __init__(self) -> None:
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)

    async def check_upload(
        self,
        db: AsyncSession,
        request: Request,
        file: UploadFile,
        current_user: User,
        *,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        uploaded = await upload_service.upload_file(file)
        storage_key = uploaded["file_url"]
        file_path = self._storage_key_to_path(storage_key)
        public_url = filename_to_url(storage_key, request)

        runtime_config = await ai_settings_service.get_runtime_config(db)
        readability = await self._check_readability(
            file_path,
            runtime_config.self_study_vision,
        )
        if not readability.accepted:
            self._delete_if_exists(file_path)
            raise SelfStudyServiceError(
                readability.detail or "题目识别不清晰，请重新上传。",
                readability.error_code or "image_not_clear",
                status_code=422,
                suggestions=readability.suggestions or READABILITY_SUGGESTIONS,
            )

        token_payload = {
            "purpose": "self_study_upload",
            "sub": str(current_user.id),
            "storage_key": storage_key,
            "problem_text_preview": readability.problem_text_preview,
            "student_work_text_preview": readability.student_work_text_preview,
            "source": source or "upload",
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        upload_token = jwt.encode(
            token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return {
            "accepted": True,
            "upload_token": upload_token,
            "storage_key": storage_key,
            "file_url": public_url,
            "problem_text_preview": readability.problem_text_preview,
            "student_work_text_preview": readability.student_work_text_preview,
            "message": "图片可用，请继续提问。",
        }

    def decode_upload_token(self, token: str, current_user: User) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError as exc:
            raise SelfStudyServiceError(
                "上传凭证无效或已过期。",
                "invalid_upload_token",
                status_code=400,
            ) from exc
        if payload.get("purpose") != "self_study_upload":
            raise SelfStudyServiceError(
                "上传凭证用途不正确。",
                "invalid_upload_token",
                status_code=400,
            )
        if str(current_user.id) != str(payload.get("sub")):
            raise SelfStudyServiceError(
                "无权使用该上传凭证。",
                "permission_denied",
                status_code=403,
            )
        return payload

    async def create_session(
        self,
        db: AsyncSession,
        request: Request,
        current_user: User,
        *,
        upload_token: str,
        voice_transcript_raw: Optional[str],
        question_text_confirmed: str,
        input_mode: str,
    ) -> Dict[str, Any]:
        payload = self.decode_upload_token(upload_token, current_user)
        storage_key = payload["storage_key"]
        session = SelfStudySession(
            student_id=current_user.id,
            original_image_storage_key=storage_key,
            problem_text=payload.get("problem_text_preview"),
            student_work_text=payload.get("student_work_text_preview"),
            voice_transcript_raw=voice_transcript_raw,
            question_text_confirmed=question_text_confirmed,
            readability_status=SelfStudyReadabilityStatus.ACCEPTED,
            session_phase=SelfStudySessionPhase.GUIDING,
        )
        db.add(session)
        await db.flush()

        student_turn = SelfStudyTurn(
            session_id=session.id,
            turn_index=1,
            speaker=SelfStudySpeaker.STUDENT,
            turn_kind=SelfStudyTurnKind.QUESTION,
            content_text=question_text_confirmed,
            meta_json={"input_mode": input_mode},
        )
        db.add(student_turn)

        analysis = await self._generate_guidance(
            db=db,
            session=session,
            question_text=question_text_confirmed,
            response_mode="initial",
        )
        self._apply_analysis(session, analysis)
        ai_turn = SelfStudyTurn(
            session_id=session.id,
            turn_index=2,
            speaker=SelfStudySpeaker.AI,
            turn_kind=analysis["turn_kind"],
            content_text=analysis["content_text"],
            meta_json=analysis["meta_json"],
        )
        db.add(ai_turn)
        await db.flush()
        loaded_session = await self.get_session(db, session.id, current_user)
        return await self.serialize_session(
            loaded_session,
            request,
            db,
        )

    async def append_turn(
        self,
        db: AsyncSession,
        request: Request,
        session: SelfStudySession,
        current_user: User,
        *,
        voice_transcript_raw: Optional[str],
        question_text_confirmed: str,
        input_mode: str,
    ) -> Dict[str, Any]:
        self._ensure_owner(session, current_user)
        self._ensure_phase(
            session,
            {
                SelfStudySessionPhase.GUIDING,
                SelfStudySessionPhase.AWAITING_REUPLOAD,
                SelfStudySessionPhase.EXPLANATION_UNLOCKED,
            },
        )
        next_turn = (len(session.turns) if session.turns else 0) + 1
        student_turn = SelfStudyTurn(
            session_id=session.id,
            turn_index=next_turn,
            speaker=SelfStudySpeaker.STUDENT,
            turn_kind=SelfStudyTurnKind.QUESTION,
            content_text=question_text_confirmed,
            meta_json={"input_mode": input_mode},
        )
        db.add(student_turn)
        session.voice_transcript_raw = voice_transcript_raw
        session.question_text_confirmed = question_text_confirmed

        analysis = await self._generate_guidance(
            db=db,
            session=session,
            question_text=question_text_confirmed,
            response_mode="followup",
        )
        self._apply_analysis(session, analysis)
        ai_turn = SelfStudyTurn(
            session_id=session.id,
            turn_index=next_turn + 1,
            speaker=SelfStudySpeaker.AI,
            turn_kind=analysis["turn_kind"],
            content_text=analysis["content_text"],
            meta_json=analysis["meta_json"],
        )
        db.add(ai_turn)
        await db.flush()
        loaded_session = await self.get_session(db, session.id, current_user)
        return await self.serialize_session(loaded_session, request, db)

    async def reupload_revision(
        self,
        db: AsyncSession,
        request: Request,
        session: SelfStudySession,
        current_user: User,
        *,
        file: UploadFile,
        voice_transcript_raw: Optional[str],
        question_text_confirmed: Optional[str],
    ) -> Dict[str, Any]:
        self._ensure_owner(session, current_user)
        self._ensure_phase(
            session,
            {
                SelfStudySessionPhase.AWAITING_REUPLOAD,
                SelfStudySessionPhase.EXPLANATION_UNLOCKED,
            },
        )
        uploaded = await upload_service.upload_file(file)
        storage_key = uploaded["file_url"]
        file_path = self._storage_key_to_path(storage_key)
        runtime_config = await ai_settings_service.get_runtime_config(db)
        readability = await self._check_readability(
            file_path,
            runtime_config.self_study_vision,
        )
        if not readability.accepted:
            self._delete_if_exists(file_path)
            raise SelfStudyServiceError(
                readability.detail or "题目识别不清晰，请重新上传。",
                readability.error_code or "image_not_clear",
                status_code=422,
                suggestions=readability.suggestions or READABILITY_SUGGESTIONS,
            )

        session.revised_image_storage_key = storage_key
        if readability.problem_text_preview:
            session.problem_text = readability.problem_text_preview
        if readability.student_work_text_preview:
            session.student_work_text = readability.student_work_text_preview
        if voice_transcript_raw:
            session.voice_transcript_raw = voice_transcript_raw
        if question_text_confirmed:
            session.question_text_confirmed = question_text_confirmed

        if question_text_confirmed:
            next_turn = (len(session.turns) if session.turns else 0) + 1
            db.add(
                SelfStudyTurn(
                    session_id=session.id,
                    turn_index=next_turn,
                    speaker=SelfStudySpeaker.STUDENT,
                    turn_kind=SelfStudyTurnKind.QUESTION,
                    content_text=question_text_confirmed,
                    meta_json={"input_mode": "reupload", "from_reupload": True},
                )
            )

        analysis = await self._generate_guidance(
            db=db,
            session=session,
            question_text=question_text_confirmed or session.question_text_confirmed or "我改好了，请再看一下。",
            response_mode="reupload",
        )
        self._apply_analysis(session, analysis)
        ai_turn = SelfStudyTurn(
            session_id=session.id,
            turn_index=(len(session.turns) if session.turns else 0) + 2,
            speaker=SelfStudySpeaker.AI,
            turn_kind=analysis["turn_kind"],
            content_text=analysis["content_text"],
            meta_json=analysis["meta_json"] | {"from_reupload": True},
        )
        db.add(ai_turn)
        await db.flush()
        loaded_session = await self.get_session(db, session.id, current_user)
        return await self.serialize_session(loaded_session, request, db)

    async def unlock_explanation(
        self,
        db: AsyncSession,
        request: Request,
        session: SelfStudySession,
        current_user: User,
    ) -> Dict[str, Any]:
        self._ensure_owner(session, current_user)
        if not session.explanation_unlocked:
            raise SelfStudyServiceError(
                "当前还未达到查看标准解释的条件。",
                "explanation_not_unlocked",
                status_code=409,
            )
        if session.session_phase == SelfStudySessionPhase.EXPLANATION_UNLOCKED:
            raise SelfStudyServiceError(
                "标准解释已经打开，无需重复解锁。",
                "explanation_already_unlocked",
                status_code=409,
            )
        analysis = await self._generate_explanation(db, session)
        session.session_phase = SelfStudySessionPhase.EXPLANATION_UNLOCKED
        ai_turn = SelfStudyTurn(
            session_id=session.id,
            turn_index=(len(session.turns) if session.turns else 0) + 1,
            speaker=SelfStudySpeaker.AI,
            turn_kind=SelfStudyTurnKind.EXPLANATION,
            content_text=analysis["content_text"],
            meta_json={
                "input_mode": "system",
                "diagram_mermaid": analysis.get("diagram_mermaid"),
            },
        )
        db.add(ai_turn)
        await db.flush()
        loaded_session = await self.get_session(db, session.id, current_user)
        return await self.serialize_session(loaded_session, request, db)

    async def create_handoff(
        self,
        db: AsyncSession,
        request: Request,
        session: SelfStudySession,
        current_user: User,
        *,
        student_last_confusion: str,
    ) -> Dict[str, Any]:
        self._ensure_owner(session, current_user)
        if session.session_phase != SelfStudySessionPhase.EXPLANATION_UNLOCKED:
            raise SelfStudyServiceError(
                "请先完成引导并查看标准解释，再转交老师。",
                "handoff_not_available",
                status_code=409,
            )
        if session.teacher_handoff is not None:
            raise SelfStudyServiceError(
                "该会话已经转交老师，请勿重复提交。",
                "handoff_already_exists",
                status_code=409,
            )
        payload_json = {
            "original_image_storage_key": session.original_image_storage_key,
            "revised_image_storage_key": session.revised_image_storage_key,
            "voice_transcript_raw": session.voice_transcript_raw,
            "question_text_confirmed": session.question_text_confirmed,
            "ai_guidance_summary": self._build_ai_guidance_summary(session.turns),
            "summary_before": session.summary_before,
            "summary_after": session.summary_after,
        }
        handoff = SelfStudyTeacherHandoff(
            session_id=session.id,
            student_id=current_user.id,
            status=SelfStudyHandoffStatus.PENDING,
            title="自学拍题求助",
            student_last_confusion=student_last_confusion,
            payload_json=payload_json,
        )
        db.add(handoff)
        session.session_phase = SelfStudySessionPhase.HANDED_OFF
        session.result_judgment = SelfStudyResultJudgment.NEEDS_TEACHER
        await db.flush()
        await db.refresh(handoff)
        return {
            "handoff_id": handoff.id,
            "session_id": session.id,
            "status": handoff.status,
            "teacher_reply_expected": True,
            "created_at": handoff.created_at,
        }

    async def complete_session(
        self,
        db: AsyncSession,
        request: Request,
        session: SelfStudySession,
        current_user: User,
        *,
        summary_before: str,
        summary_after: str,
    ) -> Dict[str, Any]:
        self._ensure_owner(session, current_user)
        if (
            session.result_judgment != SelfStudyResultJudgment.UNDERSTOOD
            and session.session_phase != SelfStudySessionPhase.HANDED_OFF
        ):
            raise SelfStudyServiceError(
                "当前会话还不能结束，请先完成理解确认或等待老师接手。",
                "completion_not_available",
                status_code=409,
            )
        session.summary_before = summary_before
        session.summary_after = summary_after
        session.session_phase = SelfStudySessionPhase.COMPLETED
        if session.result_judgment is None:
            session.result_judgment = SelfStudyResultJudgment.UNDERSTOOD
        await db.flush()
        loaded_session = await self.get_session(db, session.id, current_user)
        return await self.serialize_session(loaded_session, request, db)

    async def get_session(
        self,
        db: AsyncSession,
        session_id: int,
        current_user: User,
    ) -> SelfStudySession:
        query = (
            select(SelfStudySession)
            .where(SelfStudySession.id == session_id)
            .options(
                selectinload(SelfStudySession.turns),
                selectinload(SelfStudySession.teacher_handoff),
            )
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if session is None:
            raise SelfStudyServiceError("会话不存在。", "session_not_found", status_code=404)
        self._ensure_owner(session, current_user)
        return session

    async def list_student_sessions(
        self,
        db: AsyncSession,
        request: Request,
        current_user: User,
        *,
        page: int,
        page_size: int,
        result_judgment: Optional[str],
        session_phase: Optional[str],
    ) -> Dict[str, Any]:
        query = select(SelfStudySession).where(SelfStudySession.student_id == current_user.id)
        count_query = select(func.count()).select_from(SelfStudySession).where(
            SelfStudySession.student_id == current_user.id
        )
        if result_judgment:
            query = query.where(SelfStudySession.result_judgment == result_judgment)
            count_query = count_query.where(SelfStudySession.result_judgment == result_judgment)
        if session_phase:
            query = query.where(SelfStudySession.session_phase == session_phase)
            count_query = count_query.where(SelfStudySession.session_phase == session_phase)
        query = query.order_by(SelfStudySession.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        total = (await db.execute(count_query)).scalar() or 0
        items = list((await db.execute(query)).scalars().all())
        serialized = [
            {
                "id": item.id,
                "subject": item.subject,
                "grade_band": item.grade_band,
                "thumbnail_url": filename_to_url(item.revised_image_storage_key or item.original_image_storage_key, request),
                "result_judgment": item.result_judgment,
                "session_phase": item.session_phase,
                "created_at": item.created_at,
            }
            for item in items
        ]
        return {
            "items": serialized,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": page * page_size < total,
        }

    async def list_teacher_handoffs(
        self,
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        status: Optional[str],
    ) -> Dict[str, Any]:
        query = (
            select(SelfStudyTeacherHandoff)
            .options(selectinload(SelfStudyTeacherHandoff.student))
        )
        count_query = select(func.count()).select_from(SelfStudyTeacherHandoff)
        if status:
            query = query.where(SelfStudyTeacherHandoff.status == status)
            count_query = count_query.where(SelfStudyTeacherHandoff.status == status)
        query = query.order_by(SelfStudyTeacherHandoff.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        total = (await db.execute(count_query)).scalar() or 0
        items = list((await db.execute(query)).scalars().all())
        return {
            "items": [
                {
                    "id": item.id,
                    "session_id": item.session_id,
                    "student_id": item.student_id,
                    "student_name": item.student.username if item.student else f"学生{item.student_id}",
                    "status": item.status,
                    "title": item.title,
                    "created_at": item.created_at,
                }
                for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": page * page_size < total,
        }

    async def get_teacher_handoff(
        self,
        db: AsyncSession,
        request: Request,
        handoff_id: int,
    ) -> Dict[str, Any]:
        query = (
            select(SelfStudyTeacherHandoff)
            .where(SelfStudyTeacherHandoff.id == handoff_id)
            .options(selectinload(SelfStudyTeacherHandoff.student))
        )
        handoff = (await db.execute(query)).scalar_one_or_none()
        if handoff is None:
            raise SelfStudyServiceError("教师待处理记录不存在。", "handoff_not_found", status_code=404)
        payload = handoff.payload_json or {}
        return {
            "id": handoff.id,
            "session_id": handoff.session_id,
            "student_id": handoff.student_id,
            "student_name": handoff.student.username if handoff.student else f"学生{handoff.student_id}",
            "status": handoff.status,
            "title": handoff.title,
            "original_image_url": filename_to_url(payload.get("original_image_storage_key"), request),
            "revised_image_url": filename_to_url(payload.get("revised_image_storage_key"), request)
            if payload.get("revised_image_storage_key")
            else None,
            "voice_transcript_raw": payload.get("voice_transcript_raw"),
            "question_text_confirmed": payload.get("question_text_confirmed"),
            "ai_guidance_summary": payload.get("ai_guidance_summary", []),
            "student_last_confusion": handoff.student_last_confusion,
            "summary_before": payload.get("summary_before"),
            "summary_after": payload.get("summary_after"),
            "teacher_reply_text": handoff.teacher_reply_text,
            "teacher_reply_image_url": filename_to_url(handoff.teacher_reply_image_storage_key, request)
            if handoff.teacher_reply_image_storage_key
            else None,
            "created_at": handoff.created_at,
            "answered_at": handoff.answered_at,
        }

    async def reply_handoff(
        self,
        db: AsyncSession,
        request: Request,
        handoff_id: int,
        current_user: User,
        *,
        reply_text: str,
        annotated_image_storage_key: Optional[str],
    ) -> Dict[str, Any]:
        query = select(SelfStudyTeacherHandoff).where(SelfStudyTeacherHandoff.id == handoff_id)
        handoff = (await db.execute(query)).scalar_one_or_none()
        if handoff is None:
            raise SelfStudyServiceError("教师待处理记录不存在。", "handoff_not_found", status_code=404)
        handoff.status = SelfStudyHandoffStatus.ANSWERED
        handoff.teacher_id = current_user.id
        handoff.teacher_reply_text = reply_text
        handoff.teacher_reply_image_storage_key = annotated_image_storage_key
        handoff.answered_at = datetime.utcnow()
        handoff.updated_at = datetime.utcnow()
        await db.flush()
        return {
            "id": handoff.id,
            "status": handoff.status,
            "teacher_reply": {
                "reply_text": handoff.teacher_reply_text,
                "annotated_image_url": filename_to_url(annotated_image_storage_key, request)
                if annotated_image_storage_key
                else None,
                "answered_at": handoff.answered_at,
            },
        }

    async def serialize_session(
        self,
        session: SelfStudySession,
        request: Request,
        db: AsyncSession,
        *,
        current_ai_message: Optional[SelfStudyTurn] = None,
    ) -> Dict[str, Any]:
        if current_ai_message is None:
            current_ai_message = next(
                (turn for turn in reversed(session.turns) if turn.speaker == SelfStudySpeaker.AI),
                None,
            )
        return {
            "id": session.id,
            "student_id": session.student_id,
            "mode": session.mode.value if hasattr(session.mode, "value") else str(session.mode),
            "subject": session.subject,
            "grade_band": session.grade_band,
            "original_image_url": filename_to_url(session.original_image_storage_key, request),
            "revised_image_url": filename_to_url(session.revised_image_storage_key, request)
            if session.revised_image_storage_key
            else None,
            "problem_text": session.problem_text,
            "student_work_text": session.student_work_text,
            "session_phase": session.session_phase,
            "result_judgment": session.result_judgment,
            "primary_error_type": session.primary_error_type,
            "guidance_round_count": session.guidance_round_count,
            "explanation_unlocked": session.explanation_unlocked,
            "can_view_explanation": session.explanation_unlocked,
            "can_handoff_to_teacher": (
                session.session_phase == SelfStudySessionPhase.EXPLANATION_UNLOCKED
                and session.teacher_handoff is None
            ),
            "teacher_handoff_status": session.teacher_handoff.status if session.teacher_handoff else None,
            "teacher_reply_text": (
                session.teacher_handoff.teacher_reply_text if session.teacher_handoff else None
            ),
            "teacher_reply_image_url": (
                filename_to_url(session.teacher_handoff.teacher_reply_image_storage_key, request)
                if session.teacher_handoff and session.teacher_handoff.teacher_reply_image_storage_key
                else None
            ),
            "summary_before": session.summary_before,
            "summary_after": session.summary_after,
            "current_ai_message": {
                "turn_index": current_ai_message.turn_index,
                "turn_kind": current_ai_message.turn_kind,
                "content_text": current_ai_message.content_text,
            }
            if current_ai_message
            else None,
            "turns": [
                {
                    "turn_index": turn.turn_index,
                    "speaker": turn.speaker,
                    "turn_kind": turn.turn_kind,
                    "content_text": turn.content_text,
                    "meta_json": turn.meta_json,
                    "created_at": turn.created_at,
                }
                for turn in session.turns
            ],
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }

    async def _check_readability(
        self,
        file_path: str,
        vision_config: AIChannelRuntimeConfig,
    ) -> ReadabilityCheckResult:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                if width < 300 or height < 300:
                    return ReadabilityCheckResult(
                        accepted=False,
                        error_code="image_not_clear",
                        detail="题目识别不清晰，请重新上传。",
                        suggestions=READABILITY_SUGGESTIONS,
                    )
                aspect_ratio = max(width / max(height, 1), height / max(width, 1))
                if aspect_ratio > 3.8:
                    return ReadabilityCheckResult(
                        accepted=False,
                        error_code="image_not_clear",
                        detail="题目识别不清晰，请重新上传。",
                        suggestions=READABILITY_SUGGESTIONS,
                    )
        except Exception as exc:
            raise SelfStudyServiceError(
                "图片无法读取，请重新上传。",
                "image_not_clear",
                status_code=422,
                suggestions=READABILITY_SUGGESTIONS,
            ) from exc

        return await self._vision_readability_check(file_path, vision_config)

    async def _vision_readability_check(
        self,
        file_path: str,
        vision_config: AIChannelRuntimeConfig,
    ) -> ReadabilityCheckResult:
        prompt = (
            "你在检查学生上传的数学题图片是否可用于自学拍题伴学。"
            "要求：第一版只允许一张图里有一道题，并且要尽量同时看到题干和学生作答。"
            "请只返回 JSON，字段为 accepted(boolean), error_code(string|null), detail(string|null), "
            "problem_text_preview(string|null), student_work_text_preview(string|null), suggestions(string[])."
            "如果看起来有多道题、题干缺失、没有看到学生作答、严重模糊/反光/遮挡，则 accepted=false。"
        )
        if not self._has_ai():
            return ReadabilityCheckResult(
                accepted=False,
                error_code="image_check_unavailable",
                detail="题图检查服务暂时不可用，请稍后再试。",
                suggestions=["请稍后重试。", "如持续失败，请联系老师或管理员。"],
            )
        fallback = {
            "accepted": False,
            "error_code": "image_check_unavailable",
            "detail": "题图检查服务暂时不可用，请稍后再试。",
            "problem_text_preview": None,
            "student_work_text_preview": None,
            "suggestions": ["请稍后重试。", "如持续失败，请联系老师或管理员。"],
        }
        result = await self._call_vision_json(
            prompt=prompt,
            image_paths=[file_path],
            fallback=fallback,
            channel_config=vision_config,
        )
        accepted = bool(result.get("accepted"))
        return ReadabilityCheckResult(
            accepted=accepted,
            error_code=result.get("error_code"),
            detail=result.get("detail"),
            suggestions=result.get("suggestions") or READABILITY_SUGGESTIONS,
            problem_text_preview=result.get("problem_text_preview"),
            student_work_text_preview=result.get("student_work_text_preview"),
        )

    async def _generate_guidance(
        self,
        *,
        db: AsyncSession,
        session: SelfStudySession,
        question_text: str,
        response_mode: str,
    ) -> Dict[str, Any]:
        runtime_config = await ai_settings_service.get_runtime_config(db)
        vision_config = runtime_config.self_study_vision
        original_path = self._storage_key_to_path(session.original_image_storage_key)
        image_paths = [original_path]
        if session.revised_image_storage_key:
            image_paths.append(self._storage_key_to_path(session.revised_image_storage_key))
        prompt = self._build_guidance_prompt(session, question_text, response_mode)
        fallback = self._mock_guidance(session, response_mode)
        result = await self._call_vision_json(
            prompt=prompt,
            image_paths=image_paths,
            fallback=fallback,
            channel_config=vision_config,
        )
        return self._normalize_guidance_result(result or fallback)

    async def _generate_explanation(
        self,
        db: AsyncSession,
        session: SelfStudySession,
    ) -> Dict[str, Any]:
        runtime_config = await ai_settings_service.get_runtime_config(db)
        vision_config = runtime_config.self_study_vision
        original_path = self._storage_key_to_path(session.original_image_storage_key)
        image_paths = [original_path]
        if session.revised_image_storage_key:
            image_paths.append(self._storage_key_to_path(session.revised_image_storage_key))
        prompt = (
            "你是一位小学数学老师。请根据学生上传的题目和作答，给出一段面向学生的标准解释。"
            "要求：解释为什么原来的做法有问题，正确思路是什么，语言简洁。"
            "同时用 Mermaid 画一张简单图示（flowchart TD 或 LR），帮助学生看清数量关系或解题步骤；"
            "节点标签用中文双引号包裹，节点数 3-6 个，不要复杂语法。"
            "只返回 JSON，字段为 content_text(string), diagram_mermaid(string|null)。"
        )
        result = await self._call_vision_json(
            prompt=prompt,
            image_paths=image_paths,
            fallback={
                "content_text": "请重新回到题目中的数量关系，先确认题目在问什么，再逐步检查列式和计算。",
                "diagram_mermaid": None,
            },
            channel_config=vision_config,
        )
        parsed = result or {}
        return {
            "content_text": parsed.get("content_text")
            or "请重新回到题目中的数量关系，先确认题目在问什么，再逐步检查列式和计算。",
            "diagram_mermaid": self._normalize_diagram_mermaid(parsed.get("diagram_mermaid")),
        }

    def _build_guidance_prompt(
        self, session: SelfStudySession, question_text: str, response_mode: str
    ) -> str:
        turn_summary = self._summarize_turns(self._loaded_turns(session))
        return (
            "你是一位小学数学自学伴学教练。学生上传的是一道已做完的单题图。"
            "你的目标不是直接给答案，而是帮助学生讲清楚为什么错、为什么改对。"
            "请根据图片与对话，输出 JSON："
            "{"
            "\"result_judgment\":\"incorrect|correct_unexplained|understood\","
            "\"primary_error_type\":\"reading_error|relation_error|calculation_error|unit_expression_error|explanation_gap|null\","
            "\"turn_kind\":\"probe|hint|summary\","
            "\"content_text\":\"给学生看的中文文字\","
            "\"diagram_mermaid\":\"可选，Mermaid 图示代码；用 flowchart TD 或 LR，3-6 个中文节点，帮学生看清数量关系、两问区别或易混点；没有合适图示则 null\","
            "\"counts_as_failed_guidance_round\":true|false"
            "}。"
            "图示要求：节点标签用中文双引号；优先画「题目在问什么」「已知量→未知量」「两问对比」等认知结构，不要画最终答案。"
            "规则：如果学生做对但解释不清楚，用 correct_unexplained 并给一个理解验收问题；"
            "如果学生做错，用 incorrect，并先追问原来怎么想或给一阶提示；"
            "如果学生已经能清楚说明为什么错、为什么改对，用 understood。"
            f" 当前模式：{response_mode}。"
            f" 学生确认后的提问：{question_text}。"
            f" 已有会话摘要：{turn_summary or '无'}。"
        )

    def _normalize_guidance_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result_judgment = str(result.get("result_judgment") or "incorrect").lower()
        if result_judgment not in {
            SelfStudyResultJudgment.INCORRECT.value,
            SelfStudyResultJudgment.CORRECT_UNEXPLAINED.value,
            SelfStudyResultJudgment.UNDERSTOOD.value,
        }:
            result_judgment = SelfStudyResultJudgment.INCORRECT.value

        primary_error_type = result.get("primary_error_type")
        if primary_error_type in {"null", "", None}:
            normalized_error = None
        else:
            normalized_error = str(primary_error_type).lower()
            valid_errors = {item.value for item in SelfStudyErrorType}
            if normalized_error not in valid_errors:
                normalized_error = SelfStudyErrorType.EXPLANATION_GAP.value

        turn_kind = str(result.get("turn_kind") or "probe").lower()
        if turn_kind not in {item.value for item in SelfStudyTurnKind}:
            turn_kind = SelfStudyTurnKind.PROBE.value

        content_text = str(result.get("content_text") or "你先说说，你原来为什么这样做？").strip()
        counts_as_failed_guidance_round = bool(result.get("counts_as_failed_guidance_round"))
        diagram_mermaid = self._normalize_diagram_mermaid(result.get("diagram_mermaid"))
        return {
            "result_judgment": result_judgment,
            "primary_error_type": normalized_error,
            "turn_kind": turn_kind,
            "content_text": content_text,
            "meta_json": {
                "counts_as_failed_guidance_round": counts_as_failed_guidance_round,
                "confidence": float(result.get("confidence") or 0.8),
                "diagram_mermaid": diagram_mermaid,
            },
        }

    def _normalize_diagram_mermaid(self, value: Any) -> Optional[str]:
        if value in {None, "", "null", "NULL"}:
            return None
        text = str(value).strip()
        if not text or text.lower() == "null":
            return None
        return text

    def _mock_guidance(self, session: SelfStudySession, response_mode: str) -> Dict[str, Any]:
        if response_mode == "reupload":
            return {
                "result_judgment": "correct_unexplained",
                "primary_error_type": None,
                "turn_kind": "probe",
                "content_text": "现在结果看起来更接近正确了。你能用自己的话说说，为什么这里应该这样算吗？",
                "diagram_mermaid": (
                    'flowchart LR\n'
                    '  A["你的新答案"] --> B["和题目要求一致吗？"]\n'
                    '  B --> C["能说出每一步为什么吗？"]'
                ),
                "counts_as_failed_guidance_round": False,
            }
        if session.guidance_round_count >= 1:
            return {
                "result_judgment": "incorrect",
                "primary_error_type": "calculation_error",
                "turn_kind": "hint",
                "content_text": "先不看整道题，只看你最后一步计算。你可以把这一小步再算一次吗？",
                "diagram_mermaid": (
                    'flowchart TD\n'
                    '  A["题目要的量"] --> B["你列的式子"]\n'
                    '  B --> C["最后一步计算"]\n'
                    '  C --> D["再算一遍试试"]'
                ),
                "counts_as_failed_guidance_round": True,
            }
        return {
            "result_judgment": "incorrect",
            "primary_error_type": "explanation_gap",
            "turn_kind": "probe",
            "content_text": "我先看到了一个主要问题。你先说说，你原来为什么这样做？",
            "diagram_mermaid": (
                'flowchart TD\n'
                '  A["题目在问什么？"] --> B["你用了哪些数？"]\n'
                '  B --> C["这些数之间是什么关系？"]'
            ),
            "counts_as_failed_guidance_round": True,
        }

    async def _call_vision_json(
        self,
        *,
        prompt: str,
        image_paths: List[str],
        fallback: Dict[str, Any],
        channel_config: AIChannelRuntimeConfig,
    ) -> Dict[str, Any]:
        if not self._has_ai():
            return fallback

        content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
        for image_path in image_paths:
            if not image_path or not os.path.exists(image_path):
                continue
            data_url = self._image_path_to_data_url(image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                }
            )

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": channel_config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你必须只返回 JSON，不能返回额外说明。",
                },
                {"role": "user", "content": content},
            ],
            "max_tokens": channel_config.max_tokens,
            "temperature": channel_config.temperature,
        }
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{channel_config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code != 200:
                    return fallback
                body = response.json()
                text = body["choices"][0]["message"]["content"]
                return self._extract_json(text) or fallback
        except Exception:
            return fallback

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        text = text.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
        return None

    def _image_path_to_data_url(self, image_path: str) -> str:
        ext = os.path.splitext(image_path)[1].lower().lstrip(".") or "png"
        if ext == "jpg":
            ext = "jpeg"
        with open(image_path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("ascii")
        return f"data:image/{ext};base64,{encoded}"

    def _apply_analysis(self, session: SelfStudySession, analysis: Dict[str, Any]) -> None:
        session.result_judgment = SelfStudyResultJudgment(analysis["result_judgment"])
        session.primary_error_type = (
            SelfStudyErrorType(analysis["primary_error_type"])
            if analysis["primary_error_type"]
            else None
        )
        failed_round = bool(analysis["meta_json"].get("counts_as_failed_guidance_round"))
        if failed_round:
            session.guidance_round_count += 1
        if session.result_judgment == SelfStudyResultJudgment.INCORRECT:
            session.session_phase = SelfStudySessionPhase.AWAITING_REUPLOAD
        elif session.result_judgment == SelfStudyResultJudgment.CORRECT_UNEXPLAINED:
            session.session_phase = SelfStudySessionPhase.GUIDING
        else:
            session.session_phase = SelfStudySessionPhase.GUIDING
        if (
            session.guidance_round_count >= 2
            and session.result_judgment != SelfStudyResultJudgment.UNDERSTOOD
        ):
            session.explanation_unlocked = True

    def _build_ai_guidance_summary(self, turns: Iterable[SelfStudyTurn]) -> List[str]:
        summary: List[str] = []
        for turn in turns:
            if turn.speaker == SelfStudySpeaker.AI:
                summary.append(turn.content_text)
        return summary[-3:]

    def _summarize_turns(self, turns: Iterable[SelfStudyTurn]) -> str:
        lines: List[str] = []
        for turn in list(turns)[-6:]:
            prefix = "学生" if turn.speaker == SelfStudySpeaker.STUDENT else "AI"
            lines.append(f"{prefix}: {turn.content_text}")
        return "\n".join(lines)

    def _loaded_turns(self, session: SelfStudySession) -> List[SelfStudyTurn]:
        # 避免在异步上下文里对未预加载的 turns 关系触发懒加载（会抛 MissingGreenlet）。
        # 新建会话时 turns 尚未加载，历史本就为空，返回空列表即可。
        if "turns" in sa_inspect(session).unloaded:
            return []
        return list(session.turns)

    def _storage_key_to_path(self, storage_key: str) -> str:
        return os.path.join(upload_service.resources_dir, url_to_filename(storage_key))

    def _delete_if_exists(self, path: str) -> None:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except OSError:
            return

    def _ensure_owner(self, session: SelfStudySession, current_user: User) -> None:
        if session.student_id != current_user.id:
            raise SelfStudyServiceError("无权访问该会话。", "permission_denied", status_code=403)

    def _ensure_phase(
        self, session: SelfStudySession, allowed: set[SelfStudySessionPhase]
    ) -> None:
        if session.session_phase not in allowed:
            raise SelfStudyServiceError(
                "当前会话状态不允许执行该操作。",
                "invalid_session_phase",
                status_code=409,
            )

    def _has_ai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())


self_study_service = SelfStudyService()
