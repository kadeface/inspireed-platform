"""
课件交互数据 API — 创AI协同数据追踪
提供交互数据上报、分析查询、看板数据等接口
"""

from typing import Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.courseware import CoursewareInteraction

router = APIRouter()


# ==================== Request Models ====================


class InteractionReport(BaseModel):
    """交互数据上报请求"""
    courseware_id: str = Field(..., description="课件唯一ID")
    courseware_title: str = Field("", description="课件标题")
    platform: str = Field("飞象老师", description="AI平台")
    student_id: str = Field("anonymous", description="学生标识")
    total_questions: int = Field(0, description="总题数")
    correct_count: int = Field(0, description="正确数")
    score: float = Field(0.0, description="得分")
    total_time_ms: int = Field(0, description="总用时")
    answers: list[dict] = Field(default_factory=list, description="答题明细")
    interaction_data: Optional[dict] = Field(None, description="原始交互数据")
    lesson_id: Optional[int] = Field(None, description="关联教案ID")
    cell_id: Optional[int] = Field(None, description="关联Cell ID")
    teacher_id: Optional[int] = Field(None, description="教师ID")


# ==================== Response Models ====================


class CoursewareSummary(BaseModel):
    """课件概览统计"""
    courseware_id: str
    courseware_title: str
    platform: str
    total_sessions: int = 0
    avg_score: float = 0.0
    avg_time_ms: int = 0
    student_count: int = 0
    last_used: Optional[datetime] = None


class StudentAnalytics(BaseModel):
    """学生分析数据"""
    student_id: str
    total_interactions: int = 0
    avg_score: float = 0.0
    total_time_ms: int = 0
    coursewares_used: int = 0
    recent_scores: list[dict] = Field(default_factory=list)


# ==================== API Endpoints ====================


@router.post("/interactions", response_model=dict)
async def report_interaction(
    payload: InteractionReport,
    db: AsyncSession = Depends(get_db),
):
    """上报课件交互数据（页面postMessage自动调用）"""
    interaction = CoursewareInteraction(
        courseware_id=payload.courseware_id,
        courseware_title=payload.courseware_title,
        platform=payload.platform,
        student_id=payload.student_id,
        total_questions=payload.total_questions,
        correct_count=payload.correct_count,
        score=payload.score,
        total_time_ms=payload.total_time_ms,
        answers=payload.answers,
        interaction_data=payload.interaction_data,
        lesson_id=payload.lesson_id,
        cell_id=payload.cell_id,
        teacher_id=payload.teacher_id,
    )
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    return {"status": "ok", "id": interaction.id}


@router.get("/analytics/courseware/{courseware_id}", response_model=CoursewareSummary)
async def get_courseware_analytics(
    courseware_id: str,
    days: int = Query(30, description="统计最近N天"),
    db: AsyncSession = Depends(get_db),
):
    """获取课件分析数据"""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.count(CoursewareInteraction.id).label("total_sessions"),
            func.avg(CoursewareInteraction.score).label("avg_score"),
            func.avg(CoursewareInteraction.total_time_ms).label("avg_time_ms"),
            func.count(func.distinct(CoursewareInteraction.student_id)).label("student_count"),
            func.max(CoursewareInteraction.created_at).label("last_used"),
        ).where(
            and_(
                CoursewareInteraction.courseware_id == courseware_id,
                CoursewareInteraction.created_at >= since,
            )
        )
    )
    row = result.one()

    return CoursewareSummary(
        courseware_id=courseware_id,
        courseware_title="",
        platform="",
        total_sessions=row.total_sessions or 0,
        avg_score=round(row.avg_score or 0, 1),
        avg_time_ms=int(row.avg_time_ms or 0),
        student_count=row.student_count or 0,
        last_used=row.last_used,
    )


@router.get("/analytics/student/{student_id}", response_model=StudentAnalytics)
async def get_student_analytics(
    student_id: str,
    days: int = Query(30, description="统计最近N天"),
    db: AsyncSession = Depends(get_db),
):
    """获取学生个人分析数据"""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.count(CoursewareInteraction.id).label("total"),
            func.avg(CoursewareInteraction.score).label("avg_score"),
            func.sum(CoursewareInteraction.total_time_ms).label("total_time"),
            func.count(func.distinct(CoursewareInteraction.courseware_id)).label("coursewares"),
        ).where(
            and_(
                CoursewareInteraction.student_id == student_id,
                CoursewareInteraction.created_at >= since,
            )
        )
    )
    row = result.one()

    # 最近10次成绩
    recent_result = await db.execute(
        select(
            CoursewareInteraction.score,
            CoursewareInteraction.courseware_title,
            CoursewareInteraction.created_at,
        ).where(
            and_(
                CoursewareInteraction.student_id == student_id,
                CoursewareInteraction.created_at >= since,
            )
        ).order_by(CoursewareInteraction.created_at.desc()).limit(10)
    )
    recent_scores = [
        {"score": r.score, "courseware": r.courseware_title, "time": r.created_at.isoformat() if r.created_at else None}
        for r in recent_result
    ]

    return StudentAnalytics(
        student_id=student_id,
        total_interactions=row.total or 0,
        avg_score=round(row.avg_score or 0, 1),
        total_time_ms=int(row.total_time or 0),
        coursewares_used=row.coursewares or 0,
        recent_scores=recent_scores,
    )


@router.get("/dashboard/overview", response_model=dict)
async def get_courseware_dashboard(
    days: int = Query(30, description="统计最近N天"),
    db: AsyncSession = Depends(get_db),
):
    """获取课件看板概览数据"""
    since = datetime.utcnow() - timedelta(days=days)

    # 总体统计
    result = await db.execute(
        select(
            func.count(CoursewareInteraction.id).label("total"),
            func.count(func.distinct(CoursewareInteraction.courseware_id)).label("coursewares"),
            func.count(func.distinct(CoursewareInteraction.student_id)).label("students"),
            func.avg(CoursewareInteraction.score).label("avg_score"),
            func.avg(CoursewareInteraction.total_time_ms).label("avg_time"),
        ).where(CoursewareInteraction.created_at >= since)
    )
    row = result.one()

    # 每日趋势
    daily_result = await db.execute(
        select(
            func.date(CoursewareInteraction.created_at).label("date"),
            func.count(CoursewareInteraction.id).label("count"),
            func.avg(CoursewareInteraction.score).label("avg_score"),
        ).where(CoursewareInteraction.created_at >= since)
        .group_by(func.date(CoursewareInteraction.created_at))
        .order_by(func.date(CoursewareInteraction.created_at))
    )
    daily_trend = [
        {"date": str(r.date), "count": r.count, "avg_score": round(r.avg_score or 0, 1)}
        for r in daily_result
    ]

    # 课件排行
    top_result = await db.execute(
        select(
            CoursewareInteraction.courseware_id,
            CoursewareInteraction.courseware_title,
            func.count(CoursewareInteraction.id).label("count"),
            func.avg(CoursewareInteraction.score).label("avg_score"),
        ).where(CoursewareInteraction.created_at >= since)
        .group_by(CoursewareInteraction.courseware_id, CoursewareInteraction.courseware_title)
        .order_by(func.count(CoursewareInteraction.id).desc())
        .limit(10)
    )
    top_coursewares = [
        {"id": r.courseware_id, "title": r.courseware_title or r.courseware_id, "count": r.count, "avg_score": round(r.avg_score or 0, 1)}
        for r in top_result
    ]

    return {
        "overview": {
            "total_interactions": row.total or 0,
            "total_coursewares": row.coursewares or 0,
            "total_students": row.students or 0,
            "avg_score": round(row.avg_score or 0, 1),
            "avg_time_ms": int(row.avg_time or 0),
        },
        "daily_trend": daily_trend,
        "top_coursewares": top_coursewares,
    }
