"""
教师 AI 助理接口
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.models import Lesson, User, UserRole
from app.schemas.assistant import (
    AssistantAction,
    AssistantContext,
    AssistantInsight,
    AssistantLessonSnapshot,
    AssistantRequest,
    AssistantResponse,
)
from app.schemas.question import QuestionStats
from app.schemas.subject_group import SubjectGroupStatistics
from app.services.ai_qa import ai_qa_service

router = APIRouter()


def _format_lesson_summary(summary: Dict[str, int]) -> str:
    draft = summary.get("draft", 0)
    published = summary.get("published", 0)
    archived = summary.get("archived", 0)
    total = draft + published + archived
    return (
        f"教案总览：共 {total} 篇（草稿 {draft}，已发布 {published}，已归档 {archived}）。"
    )


def _format_question_stats(stats: QuestionStats) -> str:
    return (
        f"问答数据：累计 {stats.total} 个问题，"
        f"待答 {stats.pending} 个，已答 {stats.answered} 个，已解决 {stats.resolved} 个。"
    )


def _format_subject_group_stats(stats: SubjectGroupStatistics) -> str:
    return (
        "教研协作："
        f"加入 {stats.my_groups} 个教研组，已分享 {stats.my_shared_lessons} 篇教案，"
        f"平台总计 {stats.total_shared_lessons} 篇共享教案。"
    )


def _format_recent_lessons(
    lessons: List[AssistantLessonSnapshot],
) -> str:
    if not lessons:
        return ""

    items = []
    for lesson in lessons:
        updated = (
            lesson.updated_at.strftime("%Y-%m-%d")
            if isinstance(lesson.updated_at, datetime)
            else None
        )
        parts = [lesson.title]
        if lesson.status:
            parts.append(f"状态：{lesson.status}")
        if updated:
            parts.append(f"更新于 {updated}")
        items.append("，".join(parts))
    joined = "；".join(items)
    return f"近期教案：{joined}。"


def _build_context_lines(
    request: AssistantRequest,
) -> List[str]:
    context_lines: List[str] = []

    if request.topic:
        context_lines.append(f"助手主题：{request.topic}")

    ctx = request.context
    if ctx is None:
        return context_lines

    if ctx.lesson_summary:
        context_lines.append(_format_lesson_summary(ctx.lesson_summary))

    if ctx.question_stats:
        context_lines.append(_format_question_stats(ctx.question_stats))

    if ctx.subject_group_stats:
        context_lines.append(_format_subject_group_stats(ctx.subject_group_stats))

    if ctx.recent_lessons:
        recent_line = _format_recent_lessons(ctx.recent_lessons)
        if recent_line:
            context_lines.append(recent_line)

    if ctx.lesson_outline:
        context_lines.append(f"教案结构：{ctx.lesson_outline}")

    return context_lines


def _generate_structured_feedback(
    request: AssistantRequest,
) -> Tuple[
    List[AssistantInsight], List[AssistantAction], List[str]
]:
    insights: List[AssistantInsight] = []
    actions: List[AssistantAction] = []
    follow_ups: List[str] = []

    ctx = request.context
    if ctx is None:
        return insights, actions, follow_ups

    summary = ctx.lesson_summary or {}
    draft = summary.get("draft", 0)
    published = summary.get("published", 0)

    if draft > published:
        insights.append(
            AssistantInsight(
                title="草稿教案较多",
                detail="当前草稿数量高于已发布教案，可以优先梳理并择优发布。",
                metric=f"草稿 {draft} 篇 · 已发布 {published} 篇",
            )
        )
        actions.append(
            AssistantAction(
                label="制定草稿清单",
                description="按课堂紧迫度排序草稿，安排复盘时间和共创资源，推进发布。",
            )
        )
        follow_ups.append("如何高效完成草稿教案的发布？")

    stats = ctx.question_stats
    if stats and stats.pending > 0:
        insights.append(
            AssistantInsight(
                title="存在待答问题",
                detail="留意学生的实时反馈，优先回复高频或高优先级问题。",
                metric=f"待答 {stats.pending} 个 · 已解答 {stats.answered}",
            )
        )
        actions.append(
            AssistantAction(
                label="批量整理答疑",
                description="设定答疑模板或使用 AI 草拟回答，加速课堂反馈闭环。",
            )
        )
        follow_ups.append("请帮我生成待答问题的回复模板。")

    sg_stats = ctx.subject_group_stats
    if sg_stats and sg_stats.my_shared_lessons == 0:
        insights.append(
            AssistantInsight(
                title="尚未在教研组沉淀成果",
                detail="可挑选优质教案或课堂案例，发起一次共研分享。",
                metric=f"已加入 {sg_stats.my_groups} 个教研组 · 共享 0 篇",
            )
        )
        actions.append(
            AssistantAction(
                label="准备共研分享",
                description="选取最新发布教案的亮点，整理成分享提纲，邀请组内教师共创。",
            )
        )
        follow_ups.append("帮我生成一份教研分享的结构化提纲。")

    if request.topic == "pdca" and not follow_ups:
        follow_ups.append("还能提供哪些课堂改进行动？")

    return insights, actions, follow_ups


@router.post("/query", response_model=AssistantResponse)
async def query_teacher_assistant(
    payload: AssistantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AssistantResponse:
    """
    调用 AI 助理，为教师提供课堂洞察与建议。
    """

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    if role_value != UserRole.TEACHER.value:
        raise HTTPException(status_code=403, detail="仅教师用户可使用 AI 助理")

    lesson_title: Optional[str] = None
    if payload.lesson_id:
        lesson = await db.get(Lesson, payload.lesson_id)
        if lesson is None or lesson.creator_id != current_user.id:
            raise HTTPException(status_code=404, detail="未找到指定教案")
        lesson_title = lesson.title

    context_lines = _build_context_lines(payload)
    context_text = "\n".join(context_lines) if context_lines else None

    ai_result = await ai_qa_service.ask_question(
        question=payload.question,
        context=context_text,
        lesson_title=lesson_title,
    )

    insights, actions, follow_ups = _generate_structured_feedback(payload)

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


