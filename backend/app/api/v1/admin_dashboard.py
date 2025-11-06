"""
管理员数据看板 API
提供平台级别的统计数据，不涉及具体教学内容
"""

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User, UserRole, Course, Lesson, Resource
from app.api.deps import get_current_admin
from pydantic import BaseModel
from datetime import datetime, timedelta


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


# ==================== Endpoints ====================


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取管理员数据看板概览"""

    # 用户统计
    total_users_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_result.scalar() or 0

    admin_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "ADMIN")
    )
    admin_count = admin_count_result.scalar() or 0

    researcher_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "RESEARCHER")
    )
    researcher_count = researcher_count_result.scalar() or 0

    teacher_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "TEACHER")
    )
    teacher_count = teacher_count_result.scalar() or 0

    student_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "STUDENT")
    )
    student_count = student_count_result.scalar() or 0

    active_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0

    inactive_users = total_users - active_users

    user_stats = UserStats(
        total_users=total_users,
        admin_count=admin_count,
        researcher_count=researcher_count,
        teacher_count=teacher_count,
        student_count=student_count,
        active_users=active_users,
        inactive_users=inactive_users,
    )

    # 内容统计
    total_courses_result = await db.execute(select(func.count()).select_from(Course))
    total_courses = total_courses_result.scalar() or 0

    active_courses_result = await db.execute(
        select(func.count()).select_from(Course).where(Course.is_active == True)
    )
    active_courses = active_courses_result.scalar() or 0

    total_lessons_result = await db.execute(select(func.count()).select_from(Lesson))
    total_lessons = total_lessons_result.scalar() or 0

    published_lessons_result = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.status == "published")
    )
    published_lessons = published_lessons_result.scalar() or 0

    draft_lessons_result = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.status == "draft")
    )
    draft_lessons = draft_lessons_result.scalar() or 0

    total_resources_result = await db.execute(select(func.count()).select_from(Resource))
    total_resources = total_resources_result.scalar() or 0

    content_stats = ContentStats(
        total_courses=total_courses,
        active_courses=active_courses,
        total_lessons=total_lessons,
        published_lessons=published_lessons,
        draft_lessons=draft_lessons,
        total_resources=total_resources,
    )

    # 活动统计
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    users_created_today_result = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= today_start)
    )
    users_created_today = users_created_today_result.scalar() or 0

    users_created_this_week_result = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= week_start)
    )
    users_created_this_week = users_created_this_week_result.scalar() or 0

    users_created_this_month_result = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= month_start)
    )
    users_created_this_month = users_created_this_month_result.scalar() or 0

    lessons_created_today_result = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.created_at >= today_start)
    )
    lessons_created_today = lessons_created_today_result.scalar() or 0

    lessons_created_this_week_result = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.created_at >= week_start)
    )
    lessons_created_this_week = lessons_created_this_week_result.scalar() or 0

    lessons_created_this_month_result = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.created_at >= month_start)
    )
    lessons_created_this_month = lessons_created_this_month_result.scalar() or 0

    activity_stats = ActivityStats(
        users_created_today=users_created_today,
        users_created_this_week=users_created_this_week,
        users_created_this_month=users_created_this_month,
        lessons_created_today=lessons_created_today,
        lessons_created_this_week=lessons_created_this_week,
        lessons_created_this_month=lessons_created_this_month,
    )

    return DashboardOverview(
        user_stats=user_stats,
        content_stats=content_stats,
        activity_stats=activity_stats,
        last_updated=datetime.now(),
    )


@router.get("/user-stats", response_model=UserStats)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取用户统计数据"""
    total_users_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_result.scalar() or 0

    admin_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "ADMIN")
    )
    admin_count = admin_count_result.scalar() or 0

    researcher_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "RESEARCHER")
    )
    researcher_count = researcher_count_result.scalar() or 0

    teacher_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "TEACHER")
    )
    teacher_count = teacher_count_result.scalar() or 0

    student_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "STUDENT")
    )
    student_count = student_count_result.scalar() or 0

    active_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0

    inactive_users = total_users - active_users

    return UserStats(
        total_users=total_users,
        admin_count=admin_count,
        researcher_count=researcher_count,
        teacher_count=teacher_count,
        student_count=student_count,
        active_users=active_users,
        inactive_users=inactive_users,
    )
