"""
管理员数据看板 API
提供平台级别的统计数据，不涉及具体教学内容
"""

from typing import Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models import Course, Lesson, LessonStatus, Resource, User, UserRole
from pydantic import BaseModel


router = APIRouter()


# ==================== Response Models ====================


class UserStats(BaseModel):
    """用户统计"""

    total_users: int
    admin_count: int
    researcher_count: int
    teacher_count: int
    student_count: int
    active_users: int
    inactive_users: int


class ContentStats(BaseModel):
    """内容统计"""

    total_courses: int
    active_courses: int
    total_lessons: int
    published_lessons: int
    draft_lessons: int
    total_resources: int


class ActivityStats(BaseModel):
    """活动统计"""

    users_created_today: int
    users_created_this_week: int
    users_created_this_month: int
    lessons_created_today: int
    lessons_created_this_week: int
    lessons_created_this_month: int


class DashboardOverview(BaseModel):
    """数据看板概览"""

    user_stats: UserStats
    content_stats: ContentStats
    activity_stats: ActivityStats
    last_updated: datetime


# ==================== Query Helpers ====================


async def _fetch_user_stats(db: AsyncSession) -> UserStats:
    """一次查询获取所有用户统计，减少多次 COUNT 往返。"""
    user_stats_query = select(
        func.count(User.id).label("total_users"),
        func.coalesce(
            func.sum(case((User.role == UserRole.ADMIN, 1), else_=0)), 0
        ).label("admin_count"),
        func.coalesce(
            func.sum(case((User.role == UserRole.RESEARCHER, 1), else_=0)), 0
        ).label("researcher_count"),
        func.coalesce(
            func.sum(case((User.role == UserRole.TEACHER, 1), else_=0)), 0
        ).label("teacher_count"),
        func.coalesce(
            func.sum(case((User.role == UserRole.STUDENT, 1), else_=0)), 0
        ).label("student_count"),
        func.coalesce(func.sum(case((User.is_active.is_(True), 1), else_=0)), 0).label(
            "active_users"
        ),
    )
    row = (await db.execute(user_stats_query)).mappings().one()

    total_users = int(row["total_users"] or 0)
    active_users = int(row["active_users"] or 0)

    return UserStats(
        total_users=total_users,
        admin_count=int(row["admin_count"] or 0),
        researcher_count=int(row["researcher_count"] or 0),
        teacher_count=int(row["teacher_count"] or 0),
        student_count=int(row["student_count"] or 0),
        active_users=active_users,
        inactive_users=total_users - active_users,
    )


async def _fetch_content_stats(db: AsyncSession) -> ContentStats:
    """使用聚合查询合并课程/课时统计，降低查询数量。"""
    course_stats_query = select(
        func.count(Course.id).label("total_courses"),
        func.coalesce(func.sum(case((Course.is_active.is_(True), 1), else_=0)), 0).label(
            "active_courses"
        ),
    )
    lesson_stats_query = select(
        func.count(Lesson.id).label("total_lessons"),
        func.coalesce(
            func.sum(case((Lesson.status == LessonStatus.PUBLISHED, 1), else_=0)), 0
        ).label("published_lessons"),
        func.coalesce(
            func.sum(case((Lesson.status == LessonStatus.DRAFT, 1), else_=0)), 0
        ).label("draft_lessons"),
    )

    course_row = (await db.execute(course_stats_query)).mappings().one()
    lesson_row = (await db.execute(lesson_stats_query)).mappings().one()
    total_resources = (await db.execute(select(func.count(Resource.id)))).scalar() or 0

    return ContentStats(
        total_courses=int(course_row["total_courses"] or 0),
        active_courses=int(course_row["active_courses"] or 0),
        total_lessons=int(lesson_row["total_lessons"] or 0),
        published_lessons=int(lesson_row["published_lessons"] or 0),
        draft_lessons=int(lesson_row["draft_lessons"] or 0),
        total_resources=int(total_resources),
    )


async def _fetch_activity_stats(db: AsyncSession, now: datetime) -> ActivityStats:
    """把按时间窗口的新增统计压缩成每表一次聚合查询。"""
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    users_activity_query = select(
        func.coalesce(func.sum(case((User.created_at >= today_start, 1), else_=0)), 0).label(
            "users_created_today"
        ),
        func.coalesce(func.sum(case((User.created_at >= week_start, 1), else_=0)), 0).label(
            "users_created_this_week"
        ),
        func.coalesce(func.sum(case((User.created_at >= month_start, 1), else_=0)), 0).label(
            "users_created_this_month"
        ),
    )
    lessons_activity_query = select(
        func.coalesce(
            func.sum(case((Lesson.created_at >= today_start, 1), else_=0)), 0
        ).label("lessons_created_today"),
        func.coalesce(
            func.sum(case((Lesson.created_at >= week_start, 1), else_=0)), 0
        ).label("lessons_created_this_week"),
        func.coalesce(
            func.sum(case((Lesson.created_at >= month_start, 1), else_=0)), 0
        ).label("lessons_created_this_month"),
    )

    users_row = (await db.execute(users_activity_query)).mappings().one()
    lessons_row = (await db.execute(lessons_activity_query)).mappings().one()

    return ActivityStats(
        users_created_today=int(users_row["users_created_today"] or 0),
        users_created_this_week=int(users_row["users_created_this_week"] or 0),
        users_created_this_month=int(users_row["users_created_this_month"] or 0),
        lessons_created_today=int(lessons_row["lessons_created_today"] or 0),
        lessons_created_this_week=int(lessons_row["lessons_created_this_week"] or 0),
        lessons_created_this_month=int(lessons_row["lessons_created_this_month"] or 0),
    )


# ==================== Endpoints ====================


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取管理员数据看板概览"""
    user_stats = await _fetch_user_stats(db)
    content_stats = await _fetch_content_stats(db)
    now = datetime.now()
    activity_stats = await _fetch_activity_stats(db, now)

    return DashboardOverview(
        user_stats=user_stats,
        content_stats=content_stats,
        activity_stats=activity_stats,
        last_updated=now,
    )


@router.get("/user-stats", response_model=UserStats)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取用户统计数据"""
    return await _fetch_user_stats(db)
