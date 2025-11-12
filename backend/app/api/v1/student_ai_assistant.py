"""
学生 AI 助理接口
"""

from typing import List, Optional, Tuple, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.models import Lesson, LessonStatus, User, UserRole
from app.schemas.assistant import (
    AssistantAction,
    AssistantContext,
    AssistantInsight,
    AssistantLessonSnapshot,
    AssistantRequest,
    AssistantResponse,
)
from app.services.ai_qa import ai_qa_service

router = APIRouter()


def _build_context_lines(request: AssistantRequest) -> List[str]:
    context_lines: List[str] = []

    if request.topic:
        context_lines.append(f"助手主题：{request.topic}")

    ctx: Optional[AssistantContext] = request.context
    if ctx is None:
        return context_lines

    if ctx.progress is not None:
        context_lines.append(f"学习进度：{ctx.progress}%")

    if ctx.lesson_outline:
        context_lines.append(f"课程结构：{ctx.lesson_outline}")

    if ctx.recent_lessons:
        latest = ctx.recent_lessons[0]
        context_lines.append(f"当前课程：{latest.title}")

    return context_lines


def _generate_student_feedback(
    request: AssistantRequest,
) -> Tuple[List[AssistantInsight], List[AssistantAction], List[str]]:
    insights: List[AssistantInsight] = []
    actions: List[AssistantAction] = []
    follow_ups: List[str] = []

    ctx = request.context
    if ctx is None:
        return insights, actions, follow_ups

    progress = ctx.progress or 0
    if progress < 50:
        insights.append(
            AssistantInsight(
                title="学习进度偏低",
                detail="建议安排时间完成剩余内容，保持学习节奏。",
                metric=f"当前进度 {progress}%",
            )
        )
        actions.append(
            AssistantAction(
                label="制定学习计划",
                description="将剩余单元划分到未来几次学习中，设置提醒完成。",
            )
        )
        follow_ups.append("帮我列出未来三次的学习计划。")
    elif progress >= 90:
        insights.append(
            AssistantInsight(
                title="即将完成学习",
                detail="可以整理笔记或尝试自测，巩固知识点。",
                metric=f"当前进度 {progress}%",
            )
        )
        actions.append(
            AssistantAction(
                label="总结复盘",
                description="梳理课堂核心要点，准备问题向老师请教。",
            )
        )
        follow_ups.append("请帮我整理本节课的关键知识点。")

    if ctx.lesson_outline:
        actions.append(
            AssistantAction(
                label="关注结构要点",
                description="按照课程结构逐步完成，并在笔记中记录每个单元的疑问。",
            )
        )

    return insights, actions, follow_ups


@router.post("/query", response_model=AssistantResponse)
async def query_student_assistant(
    payload: AssistantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AssistantResponse:
    """
    学生 AI 助手，提供学习建议与知识点总结。
    """

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    if role_value != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="仅学生用户可使用 AI 助手")

    lesson_title: Optional[str] = None
    if payload.lesson_id:
        lesson = await db.get(Lesson, payload.lesson_id)
        if lesson is None or lesson.status != LessonStatus.PUBLISHED:
            raise HTTPException(status_code=404, detail="未找到指定课程")
        lesson_title = lesson.title

    context_lines = _build_context_lines(payload)
    context_text = "\n".join(context_lines) if context_lines else None

    ai_result = await ai_qa_service.ask_question(
        question=payload.question,
        context=context_text,
        lesson_title=lesson_title,
    )

    insights, actions, follow_ups = _generate_student_feedback(payload)

    return AssistantResponse(
        answer=ai_result.answer,
        insights=insights,
        suggested_actions=actions,
        follow_up_questions=follow_ups,
        model_used=ai_result.model_used,
        confidence=ai_result.confidence,
        response_time_ms=ai_result.response_time,
        context_used=context_lines,
    )


