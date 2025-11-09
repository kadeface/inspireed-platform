"""
课程体系管理 API 路由
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, Subject, Grade, Course, Lesson, UserRole, Chapter
from app.schemas.curriculum import (
    SubjectResponse,
    SubjectToggle,
    GradeResponse,
    GradeToggle,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CurriculumTreeResponse,
    SubjectTreeNode,
    GradeTreeNode,
    CourseTreeNode,
    CourseWithChaptersResponse,
    ChapterTreeNode,
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()


def _safe_int(value: Any, default: int = 0) -> int:
    """将可能为 None 或其他类型的值安全地转换为 int。"""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_optional_int(value: Any) -> Optional[int]:
    """将值安全地转换为可选的 int。"""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_str(value: Any, default: str = "") -> str:
    """将值安全地转换为字符串。"""
    if value is None:
        return default
    return str(value)


def _safe_optional_str(value: Any) -> Optional[str]:
    """将值安全地转换为可选字符串。"""
    if value is None:
        return None
    return str(value)


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """要求管理员权限"""
    user_role = cast(str, getattr(current_user, "role", ""))
    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# ==================== Subject Endpoints ====================


@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(
    include_inactive: bool = Query(False, description="是否包含未启用的学科"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取学科列表"""
    query = select(Subject).order_by(Subject.display_order, Subject.id)

    if not include_inactive:
        query = query.where(Subject.is_active == True)

    result = await db.execute(query)
    subjects = result.scalars().all()
    return subjects


@router.patch("/subjects/{subject_id}/toggle", response_model=SubjectResponse)
async def toggle_subject(
    subject_id: int,
    toggle_data: SubjectToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """启用/禁用学科 (仅管理员)"""
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在")

    # 检查是否有关联的活跃课程
    if not toggle_data.is_active:
        course_count = await db.execute(
            select(func.count())
            .select_from(Course)
            .where(Course.subject_id == subject_id, Course.is_active == True)
        )
        active_courses = course_count.scalar() or 0
        if active_courses > 0:
            raise HTTPException(status_code=400, detail="该学科下有活跃的课程，无法禁用")

    setattr(subject, "is_active", toggle_data.is_active)
    await db.commit()
    await db.refresh(subject)
    return subject


# ==================== Grade Endpoints ====================


@router.get("/grades", response_model=List[GradeResponse])
async def list_grades(
    include_inactive: bool = Query(False, description="是否包含未启用的年级"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取年级列表"""
    query = select(Grade).order_by(Grade.level)

    if not include_inactive:
        query = query.where(Grade.is_active == True)

    result = await db.execute(query)
    grades = result.scalars().all()
    return grades


@router.patch("/grades/{grade_id}/toggle", response_model=GradeResponse)
async def toggle_grade(
    grade_id: int,
    toggle_data: GradeToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """启用/禁用年级 (仅管理员)"""
    result = await db.execute(select(Grade).where(Grade.id == grade_id))
    grade = result.scalar_one_or_none()

    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")

    # 检查是否有关联的活跃课程
    if not toggle_data.is_active:
        course_count = await db.execute(
            select(func.count())
            .select_from(Course)
            .where(Course.grade_id == grade_id, Course.is_active == True)
        )
        active_courses = course_count.scalar() or 0
        if active_courses > 0:
            raise HTTPException(status_code=400, detail="该年级下有活跃的课程，无法禁用")

    setattr(grade, "is_active", toggle_data.is_active)
    await db.commit()
    await db.refresh(grade)
    return grade


# ==================== Course Endpoints ====================


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    subject_id: Optional[int] = Query(None, description="按学科ID筛选"),
    grade_id: Optional[int] = Query(None, description="按年级ID筛选"),
    include_inactive: bool = Query(False, description="是否包含未启用的课程"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取课程列表"""
    query = (
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .order_by(Course.display_order, Course.id)
    )

    if subject_id:
        query = query.where(Course.subject_id == subject_id)

    if grade_id:
        query = query.where(Course.grade_id == grade_id)

    if not include_inactive:
        query = query.where(Course.is_active == True)

    result = await db.execute(query)
    courses = result.scalars().all()
    return courses


@router.post("/courses", response_model=CourseResponse, status_code=201)
async def create_course(
    course_in: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """创建课程 (仅管理员)"""
    # 验证学科存在
    subject_result = await db.execute(select(Subject).where(Subject.id == course_in.subject_id))
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在")

    # 验证年级存在
    grade_result = await db.execute(select(Grade).where(Grade.id == course_in.grade_id))
    grade = grade_result.scalar_one_or_none()
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")

    # 检查是否已存在相同的学科+年级组合
    existing_result = await db.execute(
        select(Course).where(
            Course.subject_id == course_in.subject_id, Course.grade_id == course_in.grade_id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该学科和年级的课程已存在")

    # 创建课程
    course = Course(
        subject_id=course_in.subject_id,
        grade_id=course_in.grade_id,
        name=course_in.name,
        code=course_in.code,
        description=course_in.description,
        display_order=course_in.display_order,
        created_by=current_user.id,
    )

    db.add(course)
    await db.commit()
    await db.refresh(course)

    # 重新加载以获取关联的 subject 和 grade
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == course.id)
    )
    course = result.scalar_one()

    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """更新课程 (仅管理员)"""
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 更新字段
    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=204)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """删除课程 (仅管理员)"""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 检查是否有关联的教案
    lesson_count = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.course_id == course_id)
    )
    lessons_total = lesson_count.scalar() or 0
    if lessons_total > 0:
        raise HTTPException(status_code=400, detail="该课程下有教案，无法删除。请先删除或移动相关教案。")

    await db.delete(course)
    await db.commit()


# ==================== Curriculum Tree Endpoint ====================


@router.get("/tree", response_model=CurriculumTreeResponse)
async def get_curriculum_tree(
    include_inactive: bool = Query(False, description="是否包含未启用的项"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取完整的课程体系树形结构"""

    # 获取所有学科
    subject_query = select(Subject).order_by(Subject.display_order, Subject.id)
    if not include_inactive:
        subject_query = subject_query.where(Subject.is_active == True)
    subject_result = await db.execute(subject_query)
    subjects = subject_result.scalars().all()

    # 获取所有年级
    grade_query = select(Grade).order_by(Grade.level)
    if not include_inactive:
        grade_query = grade_query.where(Grade.is_active == True)
    grade_result = await db.execute(grade_query)
    grades = grade_result.scalars().all()

    # 获取所有课程
    course_query = select(Course)
    if not include_inactive:
        course_query = course_query.where(Course.is_active == True)
    course_result = await db.execute(course_query)
    courses = course_result.scalars().all()

    # 获取每个课程的教案数量
    lesson_count_query = select(Lesson.course_id, func.count(Lesson.id).label("count")).group_by(
        Lesson.course_id
    )
    lesson_count_result = await db.execute(lesson_count_query)
    lesson_counts: dict[int, int] = {}
    for row in lesson_count_result:
        course_id_val = _safe_optional_int(getattr(row, "course_id", None))
        if course_id_val is None:
            continue
        count_value = getattr(row, "count", 0)
        if callable(count_value):
            count_value = count_value()
        lesson_counts[course_id_val] = _safe_int(count_value, 0)

    # 构建课程字典 {(subject_id, grade_id): course}
    course_map = {}
    for course in courses:
        subject_id = _safe_optional_int(getattr(course, "subject_id", None))
        grade_id = _safe_optional_int(getattr(course, "grade_id", None))
        course_id = _safe_optional_int(getattr(course, "id", None))
        if subject_id is None or grade_id is None or course_id is None:
            continue

        key = (subject_id, grade_id)
        course_map[key] = CourseTreeNode(
            id=course_id,
            name=_safe_str(getattr(course, "name", "")),
            code=_safe_optional_str(getattr(course, "code", None)),
            description=_safe_optional_str(getattr(course, "description", None)),
            is_active=bool(getattr(course, "is_active", True)),
            lesson_count=lesson_counts.get(course_id, 0),
        )

    # 构建树形结构
    subject_nodes = []
    total_courses = 0
    total_lessons = 0

    for subject in subjects:
        grade_nodes = []
        subject_lesson_count = 0

        for grade in grades:
            subject_id_val = _safe_optional_int(getattr(subject, "id", None))
            grade_id_val = _safe_optional_int(getattr(grade, "id", None))
            if subject_id_val is None or grade_id_val is None:
                continue

            key = (subject_id_val, grade_id_val)
            if key in course_map:
                course_node = course_map[key]
                grade_nodes.append(
                    GradeTreeNode(
                        id=grade_id_val,
                        name=_safe_str(getattr(grade, "name", "")),
                        level=_safe_int(getattr(grade, "level", 0)),
                        is_active=bool(getattr(grade, "is_active", True)),
                        courses=[course_node],
                        lesson_count=course_node.lesson_count,
                    )
                )
                subject_lesson_count += course_node.lesson_count
                total_courses += 1
                total_lessons += course_node.lesson_count

        if grade_nodes or include_inactive:
            subject_id_val = _safe_optional_int(getattr(subject, "id", None))
            if subject_id_val is None:
                continue

            subject_nodes.append(
                SubjectTreeNode(
                    id=subject_id_val,
                    name=_safe_str(getattr(subject, "name", "")),
                    code=_safe_str(getattr(subject, "code", "")),
                    description=_safe_optional_str(getattr(subject, "description", None)),
                    is_active=bool(getattr(subject, "is_active", True)),
                    grades=grade_nodes,
                    lesson_count=subject_lesson_count,
                )
            )

    return CurriculumTreeResponse(
        subjects=subject_nodes,
        total_subjects=len(subjects),
        total_grades=len(grades),
        total_courses=total_courses,
        total_lessons=total_lessons,
    )


@router.get("/courses/{course_id}/with-chapters", response_model=CourseWithChaptersResponse)
async def get_course_with_chapters(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取课程详情及其章节树形结构（包含每个章节的教案数量）"""

    # 获取课程
    course_result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 获取所有章节
    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.course_id == course_id)
        .where(Chapter.is_active == True)
        .order_by(Chapter.display_order, Chapter.id)
    )
    chapters = chapters_result.scalars().all()

    # 获取每个章节的教案数量
    lesson_count_query = (
        select(Lesson.chapter_id, func.count(Lesson.id).label("count"))
        .where(Lesson.course_id == course_id)
        .group_by(Lesson.chapter_id)
    )

    lesson_count_result = await db.execute(lesson_count_query)
    lesson_counts: dict[int, int] = {}
    for row in lesson_count_result:
        chapter_id_val = _safe_optional_int(getattr(row, "chapter_id", None))
        if chapter_id_val is None:
            continue
        count_value = getattr(row, "count", 0)
        if callable(count_value):
            count_value = count_value()
        lesson_counts[chapter_id_val] = _safe_int(count_value, 0)

    # 构建章节树形结构
    chapter_map = {}  # {id: chapter_node}
    for chapter in chapters:
        chapter_id = _safe_optional_int(getattr(chapter, "id", None))
        if chapter_id is None:
            continue

        chapter_map[chapter_id] = ChapterTreeNode(
            id=chapter_id,
            name=_safe_str(getattr(chapter, "name", "")),
            code=_safe_optional_str(getattr(chapter, "code", None)),
            description=_safe_optional_str(getattr(chapter, "description", None)),
            display_order=_safe_int(getattr(chapter, "display_order", 0)),
            parent_id=_safe_optional_int(getattr(chapter, "parent_id", None)),
            lesson_count=lesson_counts.get(chapter_id, 0),
            children=[],
        )

    # 构建父子关系
    root_chapters = []
    for chapter_node in chapter_map.values():
        parent_id = chapter_node.parent_id
        if parent_id:
            parent = chapter_map.get(parent_id)
            if parent:
                parent.children.append(chapter_node)
        else:
            root_chapters.append(chapter_node)

    # 计算总教案数（包括没有关联章节的）
    total_lessons_result = await db.execute(
        select(func.count(Lesson.id)).where(Lesson.course_id == course_id)
    )
    total_lessons = total_lessons_result.scalar() or 0

    return CourseWithChaptersResponse(
        id=_safe_int(getattr(course, "id", course_id), course_id),
        name=_safe_str(getattr(course, "name", "")),
        code=_safe_optional_str(getattr(course, "code", None)),
        description=_safe_optional_str(getattr(course, "description", None)),
        subject=SubjectResponse.model_validate(course.subject) if course.subject else None,
        grade=GradeResponse.model_validate(course.grade) if course.grade else None,
        chapters=root_chapters,
        total_chapters=len(chapters),
        total_lessons=total_lessons,
    )
