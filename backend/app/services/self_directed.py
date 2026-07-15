"""
学生自主学习会话服务
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.self_directed import SelfDirectedSession, SelfDirectedSessionStatus
from app.services.knowledge_ingest import knowledge_ingest_service
from app.services.knowledge_query import knowledge_query_service
from app.services.self_directed_lesson import self_directed_lesson_service
from app.services.self_study_tutor_styles import normalize_tutor_style

logger = logging.getLogger(__name__)


class SelfDirectedServiceError(Exception):
    def __init__(self, detail: str, error_code: str = "self_directed_error", status_code: int = 400):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class SelfDirectedService:
    async def create_session(
        self,
        db: AsyncSession,
        current_user: User,
        *,
        goal_text: str,
        mission_why: Optional[str],
        mission_success: Optional[str],
        tutor_style: str = "default",
    ) -> Dict[str, Any]:
        goal = goal_text.strip()
        if not goal:
            raise SelfDirectedServiceError("请先填写想学的知识点。", "empty_goal", status_code=422)

        session = SelfDirectedSession(
            student_id=current_user.id,
            goal_text=goal,
            mission_why=(mission_why or "").strip() or None,
            mission_success=(mission_success or "").strip() or None,
            tutor_style=normalize_tutor_style(tutor_style),
            status=SelfDirectedSessionStatus.GENERATING.value,
        )
        db.add(session)
        await db.flush()

        try:
            prior = await knowledge_query_service.query_prior_knowledge(
                db,
                current_user.id,
                goal,
            )
            session.prior_summary = prior or None
            lesson = await self_directed_lesson_service.generate_lesson(
                db,
                goal_text=goal,
                mission_why=session.mission_why,
                mission_success=session.mission_success,
                prior_summary=prior or "",
                tutor_style=session.tutor_style,
            )
            session.lesson_json = lesson
            session.status = SelfDirectedSessionStatus.IN_PROGRESS.value
            session.error_message = None
        except Exception as exc:
            logger.exception("generate self-directed lesson failed")
            session.status = SelfDirectedSessionStatus.FAILED.value
            session.error_message = "微课生成失败，请稍后重试。"
            await db.flush()
            raise SelfDirectedServiceError(
                "微课生成失败，请稍后重试。",
                "lesson_generation_failed",
                status_code=502,
            ) from exc

        await db.flush()
        return self.serialize(session)

    async def get_session(
        self,
        db: AsyncSession,
        session_id: int,
        current_user: User,
    ) -> SelfDirectedSession:
        result = await db.execute(
            select(SelfDirectedSession).where(SelfDirectedSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise SelfDirectedServiceError("学习会话不存在。", "session_not_found", status_code=404)
        if session.student_id != current_user.id:
            raise SelfDirectedServiceError("无权访问该学习会话。", "forbidden", status_code=403)
        return session

    async def submit_practice(
        self,
        db: AsyncSession,
        session: SelfDirectedSession,
        *,
        answers: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        if session.status not in {
            SelfDirectedSessionStatus.IN_PROGRESS.value,
            SelfDirectedSessionStatus.COMPLETED.value,
        }:
            raise SelfDirectedServiceError("当前会话还不能提交练习。", "invalid_status", status_code=409)
        lesson = session.lesson_json or {}
        items = await self_directed_lesson_service.grade_practice(
            db,
            lesson=lesson,
            answers=answers,
        )
        existing = dict(session.check_answers_json or {})
        existing["practice"] = [
            {"id": a.get("id"), "answer": a.get("answer")} for a in answers
        ]
        existing["practice_feedback"] = items
        session.check_answers_json = existing
        await db.flush()
        return {"items": items}

    async def complete_session(
        self,
        db: AsyncSession,
        session: SelfDirectedSession,
        current_user: User,
        *,
        mastery_answer: str,
        practice_answers: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        if session.status == SelfDirectedSessionStatus.COMPLETED.value:
            return self.serialize(session)
        if session.status != SelfDirectedSessionStatus.IN_PROGRESS.value:
            raise SelfDirectedServiceError("当前会话还不能完成。", "invalid_status", status_code=409)

        mastery = mastery_answer.strip()
        if not mastery:
            raise SelfDirectedServiceError("请先完成验收回答。", "empty_mastery", status_code=422)

        lesson = session.lesson_json or {}
        feedback_items: List[Dict[str, Any]] = []
        if practice_answers:
            feedback_items = await self_directed_lesson_service.grade_practice(
                db,
                lesson=lesson,
                answers=practice_answers,
            )

        session.check_answers_json = {
            "practice": [
                {"id": a.get("id"), "answer": a.get("answer")} for a in practice_answers
            ],
            "practice_feedback": feedback_items,
            "mastery_answer": mastery,
        }
        session.status = SelfDirectedSessionStatus.COMPLETED.value
        session.completed_at = datetime.utcnow()
        await db.flush()

        try:
            path = knowledge_ingest_service.ingest_from_self_directed_session(
                current_user.id,
                session_id=session.id,
                goal_text=session.goal_text,
                mission_why=session.mission_why,
                lesson=lesson,
                mastery_answer=mastery,
                prior_summary=session.prior_summary,
            )
            session.vault_lesson_path = path
            await db.flush()
        except Exception:
            logger.exception("self-directed ingest failed for session %s", session.id)

        return self.serialize(session)

    def serialize(self, session: SelfDirectedSession) -> Dict[str, Any]:
        return {
            "id": session.id,
            "student_id": session.student_id,
            "goal_text": session.goal_text,
            "mission_why": session.mission_why,
            "mission_success": session.mission_success,
            "tutor_style": session.tutor_style,
            "status": session.status,
            "prior_summary": session.prior_summary,
            "lesson_json": session.lesson_json,
            "check_answers_json": session.check_answers_json,
            "vault_lesson_path": session.vault_lesson_path,
            "error_message": session.error_message,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "completed_at": session.completed_at,
        }


self_directed_service = SelfDirectedService()
