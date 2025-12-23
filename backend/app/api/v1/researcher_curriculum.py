"""
教研员课程体系管理 API 路由
从管理员端迁移而来，专供教研员使用
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, Subject, Grade, Course, Lesson, Chapter
from app.schemas.curriculum import CourseMergeRequest, CourseMergeResponse
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
)
from app.api.deps import get_current_researcher

router = APIRouter()


# ==================== Subject Endpoints ====================


@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(
    include_inactive: bool = Query(False, description="是否包含未启用的学科"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """获取学科列表（教研员）"""
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
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """启用/禁用学科（教研员）"""
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
        if (course_count.scalar() or 0) > 0:
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
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """获取年级列表（教研员）"""
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
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """启用/禁用年级（教研员）"""
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
        if (course_count.scalar() or 0) > 0:
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
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """获取课程列表（教研员）"""
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
    
    # 过滤掉关联对象不存在或无效的课程（避免序列化错误）
    valid_courses = []
    for course in courses:
        try:
            # selectinload 应该已经加载了关联对象，但如果数据不一致可能导致 None
            # 验证关联对象是否存在
            if hasattr(course, 'subject') and hasattr(course, 'grade'):
                # 检查关联对象是否有效（不是 None 且是有效的对象）
                if course.subject is not None and course.grade is not None:
                    valid_courses.append(course)
                else:
                    # 关联对象为 None，可能是数据不一致，跳过该课程
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"跳过课程 {getattr(course, 'id', 'unknown')} "
                        f"({getattr(course, 'name', 'unknown')}): "
                        f"关联对象缺失 (subject={course.subject is not None}, "
                        f"grade={course.grade is not None})"
                    )
            else:
                # 如果对象没有这些属性，也跳过
                valid_courses.append(course)
        except Exception as e:
            # 如果访问关联对象时出错，跳过该课程并记录错误
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"跳过课程 {getattr(course, 'id', 'unknown')} "
                f"({getattr(course, 'name', 'unknown')}): 关联对象加载失败 - {str(e)}"
            )
            continue
    
    return valid_courses


@router.post("/courses", response_model=CourseResponse, status_code=201)
async def create_course(
    course_in: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """创建课程（教研员）"""
    # 验证学科存在
    subject_result = await db.execute(
        select(Subject).where(Subject.id == course_in.subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在")

    # 验证年级存在
    grade_result = await db.execute(select(Grade).where(Grade.id == course_in.grade_id))
    grade = grade_result.scalar_one_or_none()
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")

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
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """更新课程（教研员）"""
    from sqlalchemy import func
    
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
    
    # 如果更新年级，需要验证
    if "grade_id" in update_data:
        new_grade_id = update_data["grade_id"]
        if new_grade_id != course.grade_id:
            # 验证新年级是否存在且启用
            grade_result = await db.execute(
                select(Grade).where(Grade.id == new_grade_id)
            )
            new_grade = grade_result.scalar_one_or_none()
            if not new_grade:
                raise HTTPException(status_code=404, detail="年级不存在")
            if not new_grade.is_active:
                raise HTTPException(status_code=400, detail="目标年级已被禁用，无法调整")
            
            # 检查课程下是否有教案或章节（仅作为警告，不阻止操作）
            lesson_count_result = await db.execute(
                select(func.count(Lesson.id)).where(Lesson.course_id == course_id)
            )
            lesson_count = lesson_count_result.scalar() or 0
            
            chapter_count_result = await db.execute(
                select(func.count(Chapter.id)).where(Chapter.course_id == course_id)
            )
            chapter_count = chapter_count_result.scalar() or 0
            
            # 如果有数据，记录警告信息
            if lesson_count > 0 or chapter_count > 0:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"课程 {course_id} 调整年级从 {course.grade_id} 到 {new_grade_id}，"
                    f"课程下有 {lesson_count} 个教案和 {chapter_count} 个章节"
                )
    
    # 更新所有字段
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=204)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher),
) -> None:
    """删除课程（教研员）"""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 检查是否有关联的教案
    lesson_count = await db.execute(
        select(func.count()).select_from(Lesson).where(Lesson.course_id == course_id)
    )
    if (lesson_count.scalar() or 0) > 0:
        raise HTTPException(status_code=400, detail="该课程下有教案，无法删除。请先删除或移动相关教案。")

    await db.delete(course)
    await db.commit()


@router.get("/courses/by-code/{course_code}", response_model=List[CourseResponse])
async def get_courses_by_code(
    course_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """根据课程代码查找所有具有相同代码的课程（用于合并）
    支持去除首尾空格后的模糊匹配，以处理代码中的空格差异
    """
    from sqlalchemy import func
    
    # 去除输入代码的首尾空格
    normalized_code = course_code.strip()
    
    # 使用 func.trim 去除数据库中的首尾空格后比较
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(func.trim(Course.code) == normalized_code)
        .order_by(Course.created_at)
    )
    courses = result.scalars().all()
    return courses


@router.post("/courses/merge", response_model=CourseMergeResponse)
async def merge_courses(
    merge_request: CourseMergeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """合并课程（将源课程的数据合并到目标课程）- 教研员版本"""
    from app.utils.course_merge import merge_courses_impl
    
    # 验证源课程和目标课程
    source_result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == merge_request.source_course_id)
    )
    source_course = source_result.scalar_one_or_none()
    
    target_result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == merge_request.target_course_id)
    )
    target_course = target_result.scalar_one_or_none()
    
    if not source_course:
        raise HTTPException(status_code=404, detail="源课程不存在")
    if not target_course:
        raise HTTPException(status_code=404, detail="目标课程不存在")
    if source_course.id == target_course.id:
        raise HTTPException(status_code=400, detail="源课程和目标课程不能相同")
    
    # 验证课程代码是否相同（去除首尾空格后比较）
    source_code_normalized = (source_course.code or '').strip()
    target_code_normalized = (target_course.code or '').strip()
    
    if source_code_normalized != target_code_normalized:
        raise HTTPException(
            status_code=400, 
            detail=f"课程代码不匹配：源课程代码为 '{source_course.code}'，目标课程代码为 '{target_course.code}'"
        )
    
    try:
        result = await merge_courses_impl(merge_request, db, source_course, target_course)
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"合并课程失败: {str(e)}")


# ==================== Curriculum Tree Endpoint ====================


@router.get("/tree", response_model=CurriculumTreeResponse)
async def get_curriculum_tree(
    include_inactive: bool = Query(False, description="是否包含未启用的项"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher),
) -> Any:
    """获取完整的课程体系树形结构（教研员）"""

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
    course_query = select(Course).order_by(Course.display_order, Course.id)
    if not include_inactive:
        course_query = course_query.where(Course.is_active == True)
    course_result = await db.execute(course_query)
    courses = course_result.scalars().all()

    # 获取每个课程的教案数量（包括所有状态的教案，不区分创建者）
    lesson_count_query = select(
        Lesson.course_id, func.count(Lesson.id).label("count")
    ).where(Lesson.course_id.isnot(None)).group_by(Lesson.course_id)
    lesson_count_result = await db.execute(lesson_count_query)
    lesson_counts = {
        cast(int, course_id): cast(int, count)
        for course_id, count in lesson_count_result
    }

    # 构建课程字典 {(subject_id, grade_id): [courses]}
    course_map: dict[tuple[int, int], list[tuple[int, CourseTreeNode]]] = {}
    for course in courses:
        subject_id = cast(int, course.subject_id)
        grade_id = cast(int, course.grade_id)
        key = (subject_id, grade_id)
        course_node = CourseTreeNode(
            id=cast(int, course.id),
            name=cast(str, course.name),
            code=cast(Optional[str], course.code),
            description=cast(Optional[str], course.description),
            is_active=cast(bool, course.is_active),
            lesson_count=lesson_counts.get(cast(int, course.id), 0),
        )
        display_order = cast(int, getattr(course, "display_order", 0) or 0)
        course_map.setdefault(key, []).append((display_order, course_node))

    sorted_course_map: dict[tuple[int, int], list[CourseTreeNode]] = {}
    for key, nodes in course_map.items():
        nodes.sort(key=lambda item: (item[0], item[1].id))
        sorted_course_map[key] = [node for _, node in nodes]

    # 构建树形结构
    subject_nodes = []
    total_courses = 0
    total_lessons = 0

    for subject in subjects:
        grade_nodes = []
        subject_lesson_count = 0

        for grade in grades:
            key = (cast(int, subject.id), cast(int, grade.id))
            course_nodes = sorted_course_map.get(key)
            if course_nodes:
                grade_lesson_count = sum(node.lesson_count for node in course_nodes)
                grade_nodes.append(
                    GradeTreeNode(
                        id=cast(int, grade.id),
                        name=cast(str, grade.name),
                        level=cast(int, grade.level),
                        is_active=cast(bool, grade.is_active),
                        courses=course_nodes,
                        lesson_count=grade_lesson_count,
                    )
                )
                subject_lesson_count += grade_lesson_count
                total_courses += len(course_nodes)
                total_lessons += grade_lesson_count

        if grade_nodes or include_inactive:
            subject_nodes.append(
                SubjectTreeNode(
                    id=cast(int, subject.id),
                    name=cast(str, subject.name),
                    code=(cast(Optional[str], subject.code) or ""),
                    description=cast(Optional[str], subject.description),
                    is_active=cast(bool, subject.is_active),
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
