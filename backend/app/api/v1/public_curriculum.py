"""
公开访问的课程体系 API
允许未登录用户浏览学科与课程信息
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Chapter, Course, Lesson, Subject
from app.schemas.curriculum import (
    ChapterTreeNode,
    CourseResponse,
    CourseWithChaptersResponse,
    SubjectResponse,
)

router = APIRouter()


def _build_chapter_tree(
    chapters: List[Chapter], lesson_counts: Dict[int, int]
) -> List[ChapterTreeNode]:
    """根据章节列表构建树形结构"""

    node_map: Dict[int, ChapterTreeNode] = {}
    roots: List[ChapterTreeNode] = []

    for chapter in chapters:
        if not chapter.is_active:
            continue

        node_map[chapter.id] = ChapterTreeNode(
            id=chapter.id,
            name=chapter.name,
            code=chapter.code,
            description=chapter.description,
            display_order=chapter.display_order,
            parent_id=chapter.parent_id,
            lesson_count=lesson_counts.get(chapter.id, 0),
            children=[],
        )

    for chapter in chapters:
        if not chapter.is_active:
            continue

        node = node_map[chapter.id]
        if chapter.parent_id and chapter.parent_id in node_map:
            node_map[chapter.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/subjects", response_model=List[SubjectResponse])
async def public_get_subjects(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取所有启用的学科列表（公开）"""

    result = await db.execute(
        select(Subject)
        .where(Subject.is_active == True)  # noqa: E712
        .order_by(Subject.display_order, Subject.id)
    )
    return result.scalars().all()


@router.get("/subjects/{subject_code}/courses", response_model=List[CourseResponse])
async def public_get_courses_by_subject(
    subject_code: str,
    grade_id: Optional[int] = Query(default=None, description="按年级ID筛选"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """根据学科代码获取课程列表（公开）"""

    subject_result = await db.execute(
        select(Subject).where(
            Subject.code == subject_code, Subject.is_active == True  # noqa: E712
        )
    )
    subject = subject_result.scalar_one_or_none()

    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在或未启用")

    query = (
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.subject_id == subject.id, Course.is_active == True)  # noqa: E712
        .order_by(Course.display_order, Course.id)
    )

    if grade_id is not None:
        query = query.where(Course.grade_id == grade_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/courses/{course_id}/with-chapters",
    response_model=CourseWithChaptersResponse,
)
async def public_get_course_with_chapters(
    course_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取课程详情及章节结构（公开）"""

    course_result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == course_id, Course.is_active == True)  # noqa: E712
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在或未启用")

    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.course_id == course_id, Chapter.is_active == True)  # noqa: E712
        .order_by(Chapter.display_order, Chapter.id)
    )
    chapters = chapters_result.scalars().all()

    lesson_count_query = (
        select(Lesson.chapter_id, func.count(Lesson.id).label("count"))
        .where(Lesson.course_id == course_id)
        .group_by(Lesson.chapter_id)
    )

    lesson_count_result = await db.execute(lesson_count_query)
    lesson_counts: Dict[int, int] = {}
    for row in lesson_count_result:
        chapter_id = getattr(row, "chapter_id", None)
        count_value = getattr(row, "count", 0)
        if chapter_id is None:
            continue
        if callable(count_value):
            count_value = count_value()
        lesson_counts[int(chapter_id)] = int(count_value or 0)

    chapter_tree = _build_chapter_tree(chapters, lesson_counts)

    total_lessons = sum(lesson_counts.values())

    return CourseWithChaptersResponse(
        id=course.id,
        name=course.name,
        code=course.code,
        description=course.description,
        subject=course.subject,
        grade=course.grade,
        chapters=chapter_tree,
        total_chapters=len(chapters),
        total_lessons=total_lessons,
    )

