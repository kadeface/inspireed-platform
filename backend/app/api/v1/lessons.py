"""
教案API路由
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import (
    User,
    UserRole,
    Lesson,
    LessonStatus,
    LessonClassroom,
    Course,
    Resource,
    Chapter,
    DifficultyLevel,
    Classroom,
)
from app.schemas.lesson import (
    LessonCreate,
    LessonUpdate,
    LessonResponse,
    LessonListResponse,
    LessonClassroomInfo,
    LessonPublishRequest,
    LessonRelatedMaterial,
    LessonRelatedMaterialListResponse,
)
from app.api.v1.auth import get_current_active_user
from app.api.deps import get_current_user_optional
from pydantic import BaseModel, Field

router = APIRouter()


async def _get_lesson_with_relations(
    db: AsyncSession, lesson_id: int
) -> Optional[Lesson]:
    """加载包含必要关联关系的教案"""
    result = await db.execute(
        select(Lesson)
            .options(
                selectinload(Lesson.course).selectinload(Course.subject),
                selectinload(Lesson.course).selectinload(Course.grade),
                selectinload(Lesson.creator),
                selectinload(Lesson.chapter),
                selectinload(Lesson.reference_resource),
                selectinload(Lesson.lesson_classrooms).selectinload(
                    LessonClassroom.classroom
                ),
            )
            .where(Lesson.id == lesson_id)
    )
    return result.scalar_one_or_none()


def _lesson_to_response(lesson: Lesson) -> LessonResponse:
    """将教案对象转换为响应字典"""
    lesson_data = {
        k: v
        for k, v in lesson.__dict__.items()
        if not k.startswith("_") and k not in {"lesson_classrooms", "creator"}
    }
    lesson_data.setdefault("content", lesson.content or [])
    lesson_data.setdefault("tags", lesson.tags or [])
    lesson_data.update(
        {
            "creator_name": lesson.creator.full_name if lesson.creator else None,
            "creator_avatar": lesson.creator.avatar_url if lesson.creator else None,
            "classroom_ids": [
                relation.classroom_id for relation in lesson.lesson_classrooms
            ],
            "classrooms": [
                LessonClassroomInfo.model_validate(relation.classroom).model_dump()
                for relation in lesson.lesson_classrooms
                if relation.classroom is not None
            ],
        }
    )
    if lesson_data["content"] is None:
        lesson_data["content"] = []
    if lesson_data.get("tags") is None:
        lesson_data["tags"] = []
    return LessonResponse.model_validate(lesson_data)


@router.post("/", response_model=LessonResponse, status_code=201)
async def create_lesson(
    lesson_in: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建教案"""
    # 验证课程存在
    course = await db.get(Course, lesson_in.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    is_course_active = cast(Optional[bool], course.is_active)
    if is_course_active is False:
        raise HTTPException(status_code=400, detail="该课程已被禁用")

    # 验证章节存在（如果提供了章节ID）
    if lesson_in.chapter_id:
        chapter = await db.get(Chapter, lesson_in.chapter_id)
        if chapter is None:
            raise HTTPException(status_code=404, detail="章节不存在")

        if cast(int, chapter.course_id) != lesson_in.course_id:
            raise HTTPException(status_code=400, detail="章节不属于指定课程")

        if chapter.is_active is False:
            raise HTTPException(status_code=400, detail="该章节已被禁用")

    lesson = Lesson(
        title=lesson_in.title,
        description=lesson_in.description,
        creator_id=current_user.id,
        course_id=lesson_in.course_id,
        chapter_id=lesson_in.chapter_id,
        content=lesson_in.content,
        tags=lesson_in.tags or [],
        national_resource_id=lesson_in.national_resource_id,
    )
    db.add(lesson)
    await db.commit()
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案创建后加载失败")
    return _lesson_to_response(lesson)


@router.get("/", response_model=LessonListResponse)
async def list_lessons(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态筛选: draft, published, archived"),
    search: Optional[str] = None,
    course_id: Optional[int] = Query(None, description="按课程ID筛选"),
    chapter_id: Optional[int] = Query(None, description="按章节ID筛选"),
    subject_id: Optional[int] = Query(None, description="按学科ID筛选"),
    grade_id: Optional[int] = Query(None, description="按年级ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案列表"""
    try:
        status_enum = LessonStatus(status.lower()) if status else None
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    base_query = select(Lesson).options(
        selectinload(Lesson.course).selectinload(Course.subject),
        selectinload(Lesson.course).selectinload(Course.grade),
        selectinload(Lesson.creator),
        selectinload(Lesson.lesson_classrooms).selectinload(
            LessonClassroom.classroom
        ),
    )

    if user_role == UserRole.STUDENT:
        classroom_id = current_user.classroom_id
        if classroom_id is None:
            return LessonListResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
            )
        base_query = (
            base_query.join(LessonClassroom)
            .where(Lesson.status == LessonStatus.PUBLISHED)
            .where(LessonClassroom.classroom_id == classroom_id)
            .distinct(Lesson.id)
        )
    else:
        # 教师/管理员/教研员：可以看到自己创建的教案 + 所有已发布的教案（共享教案）
        if status_enum:
            # 如果指定了状态筛选
            if status_enum == LessonStatus.PUBLISHED:
                # 查看已发布教案时，显示自己的 + 所有已发布的
                base_query = base_query.where(
                    or_(
                        Lesson.creator_id == current_user.id,
                        Lesson.status == LessonStatus.PUBLISHED
                    )
                )
            else:
                # 查看其他状态时，只显示自己创建的
                base_query = base_query.where(
                    and_(
                        Lesson.creator_id == current_user.id,
                        Lesson.status == status_enum
                    )
                )
        else:
            # 没有状态筛选时，显示自己创建的 + 所有已发布的
            base_query = base_query.where(
                or_(
                    Lesson.creator_id == current_user.id,
                    Lesson.status == LessonStatus.PUBLISHED
                )
            )

    if search:
        base_query = base_query.where(Lesson.title.ilike(f"%{search}%"))

    if course_id:
        base_query = base_query.where(Lesson.course_id == course_id)

    if chapter_id:
        base_query = base_query.where(Lesson.chapter_id == chapter_id)

    if subject_id or grade_id:
        base_query = base_query.join(Course)
        if subject_id:
            base_query = base_query.where(Course.subject_id == subject_id)
        if grade_id:
            base_query = base_query.where(Course.grade_id == grade_id)

    count_subquery = (
        base_query.with_only_columns(Lesson.id)
        .order_by(None)
        .distinct()
        .subquery()
    )
    count_query = select(func.count()).select_from(count_subquery)
    total = (await db.execute(count_query)).scalar() or 0

    if user_role == UserRole.STUDENT:
        ordered_query = base_query.order_by(Lesson.id, Lesson.updated_at.desc())
    else:
        ordered_query = base_query.order_by(Lesson.updated_at.desc())
    paginated_query = ordered_query.offset((page - 1) * page_size).limit(page_size)

    lessons = (await db.execute(paginated_query)).scalars().all()
    serialized_lessons = [_lesson_to_response(lesson) for lesson in lessons]

    return LessonListResponse(
        items=serialized_lessons,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/recommended", response_model=LessonListResponse)
async def get_recommended_lessons(
    limit: int = Query(10, ge=1, le=50, description="推荐课程数量"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    """
    获取推荐课程（公开接口，无需登录）
    基于以下因素推荐：
    1. 热门课程（评分高、查看多）
    2. 新发布的课程
    """
    query = (
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.creator),
            selectinload(Lesson.lesson_classrooms).selectinload(
                LessonClassroom.classroom
            ),
            selectinload(Lesson.reference_resource),
        )
        .where(Lesson.status == LessonStatus.PUBLISHED)
        .order_by(
            func.coalesce(Lesson.average_rating, 0).desc(),
            func.coalesce(Lesson.published_at, Lesson.created_at).desc(),
        )
        .limit(limit)
    )

    result = await db.execute(query)
    lessons = result.scalars().all()

    lesson_responses = [_lesson_to_response(lesson) for lesson in lessons]

    if (
        current_user
        and isinstance(current_user.role, UserRole)
        and cast(UserRole, current_user.role) == UserRole.STUDENT
    ):
        classroom_id = current_user.classroom_id
        if classroom_id is not None:
            lesson_responses = [
                lesson
                for lesson in lesson_responses
                if classroom_id in lesson.classroom_ids
            ]

    return LessonListResponse(
        items=lesson_responses,
        total=len(lesson_responses),
        page=1,
        page_size=limit,
    )


@router.get(
    "/courses/{course_id}/related-materials",
    response_model=LessonRelatedMaterialListResponse,
)
async def get_course_related_materials(
    course_id: int,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="按标题搜索关联素材"),
    resource_type: Optional[str] = Query(None, description="按资源类型筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取课程关联素材列表"""

    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    is_course_active = cast(Optional[bool], course.is_active)
    if is_course_active is False:
        raise HTTPException(status_code=400, detail="该课程已被禁用")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    if user_role == UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="学生无权访问课程素材")

    resource_query = (
        select(Resource)
        .join(Chapter, Resource.chapter_id == Chapter.id)
        .where(Chapter.course_id == course_id, Resource.is_active.is_(True))
    )

    if search:
        resource_query = resource_query.where(Resource.title.ilike(f"%{search}%"))

    if resource_type and resource_type.lower() != "all":
        resource_query = resource_query.where(Resource.resource_type == resource_type)

    count_query = resource_query.with_only_columns(func.count()).order_by(None)
    total = (await db.execute(count_query)).scalar() or 0

    ordered_query = resource_query.order_by(Resource.updated_at.desc())
    paginated_query = ordered_query.offset((page - 1) * page_size).limit(page_size)
    resources = (await db.execute(paginated_query)).scalars().unique().all()

    resource_ids = [cast(int, resource.id) for resource in resources]
    lesson_map: Dict[int, Lesson] = {}

    if resource_ids:
        lessons_result = await db.execute(
            select(Lesson)
                .where(Lesson.reference_resource_id.in_(resource_ids))
                .order_by(Lesson.updated_at.desc())
        )
        for lesson in lessons_result.scalars().all():
            resource_id_value = cast(Optional[int], lesson.reference_resource_id)
            if resource_id_value and resource_id_value not in lesson_map:
                lesson_map[resource_id_value] = lesson

    base_url = str(request.base_url).rstrip("/")

    def build_absolute_url(url: Optional[str]) -> Optional[str]:
        if not url:
            return None
        if url.startswith("http://") or url.startswith("https://"):
            return url
        normalized = url.lstrip("/")
        return f"{base_url}/{normalized}"

    items: List[LessonRelatedMaterial] = []
    for resource in resources:
        resource_id_value = cast(int, resource.id)
        linked_lesson = lesson_map.get(resource_id_value)
        file_url = cast(Optional[str], resource.file_url)
        preview_url = build_absolute_url(file_url)
        is_resource_downloadable = cast(Optional[bool], resource.is_downloadable)
        download_url = (
            build_absolute_url(file_url) if is_resource_downloadable else None
        )

        items.append(
            LessonRelatedMaterial(
                id=resource_id_value,
                title=cast(str, resource.title),
                summary=cast(Optional[str], resource.description),
                resource_type=cast(str, resource.resource_type),
                source_lesson_id=(
                    cast(Optional[int], linked_lesson.id) if linked_lesson else None
                ),
                source_lesson_title=(
                    cast(Optional[str], linked_lesson.title)
                    if linked_lesson
                    else None
                ),
                preview_url=preview_url,
                download_url=download_url,
                is_accessible=bool(resource.is_active),
                tags=[],
                updated_at=cast(Optional[datetime], resource.updated_at),
            )
        )

    return LessonRelatedMaterialListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/available-classrooms", response_model=List[LessonClassroomInfo])
async def get_available_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教师可选的班级列表"""
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    query = select(Classroom).where(Classroom.is_active.is_(True))

    if user_role == UserRole.TEACHER:
        if current_user.school_id is None:
            raise HTTPException(status_code=400, detail="教师未关联学校，无法获取班级列表")
        query = query.where(Classroom.school_id == current_user.school_id)
    elif user_role in {UserRole.ADMIN, UserRole.RESEARCHER}:
        # 管理员或教研员可以查看全部激活班级
        pass
    else:
        raise HTTPException(status_code=403, detail="仅教师或管理员可查看班级列表")

    query = query.order_by(Classroom.grade_id, Classroom.name)

    classrooms = (await db.execute(query)).scalars().all()
    return [
        LessonClassroomInfo.model_validate(classroom) for classroom in classrooms
    ]


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案详情"""
    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    lesson_status = LessonStatus(cast(str, lesson.status))
    creator_id = cast(Optional[int], lesson.creator_id)

    if user_role == UserRole.STUDENT:
        if lesson_status != LessonStatus.PUBLISHED:
            raise HTTPException(status_code=403, detail="无权访问该教案")
        classroom_id = current_user.classroom_id
        assigned_classroom_ids = {
            relation.classroom_id for relation in lesson.lesson_classrooms
        }
        if classroom_id is None or classroom_id not in assigned_classroom_ids:
            raise HTTPException(status_code=403, detail="该教案未分配到你的班级")
    else:
        if creator_id != current_user.id and lesson_status != LessonStatus.PUBLISHED:
            raise HTTPException(status_code=403, detail="无权访问该教案")

    return _lesson_to_response(lesson)


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_in: LessonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新教案"""
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
        )
        .where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该教案")

    # 如果更新 course_id，验证课程存在
    update_data = lesson_in.model_dump(exclude_unset=True)
    if "course_id" in update_data:
        course_result = await db.execute(
            select(Course).where(Course.id == update_data["course_id"])
        )
        course = course_result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        if course.is_active is False:
            raise HTTPException(status_code=400, detail="该课程已被禁用")

    # 检查是否更新了内容（content字段）
    content_updated = False
    if "content" in update_data:
        old_content = lesson.content
        new_content = update_data["content"]
        # 比较内容是否真正发生变化（简单比较长度和结构）
        if old_content != new_content:
            content_updated = True

    # 更新字段
    for field, value in update_data.items():
        setattr(lesson, field, value)

    # 如果更新了已发布教案的内容，自动更新版本号
    # 这样学生端可以通过版本号判断是否有新内容
    if content_updated and cast(str, lesson.status) == LessonStatus.PUBLISHED:
        current_version = cast(Optional[int], lesson.version)
        new_version = (current_version or 1) + 1
        setattr(lesson, "version", new_version)
        # 更新 published_at 时间戳，表示内容已更新
        setattr(lesson, "published_at", datetime.utcnow())

    await db.commit()
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案更新后加载失败")
    return _lesson_to_response(lesson)


@router.delete("/{lesson_id}", status_code=204)
async def delete_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """删除教案"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该教案")

    await db.delete(lesson)
    await db.commit()


@router.post("/{lesson_id}/publish", response_model=LessonResponse)
async def publish_lesson(
    lesson_id: int,
    publish_in: LessonPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """发布教案"""
    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权发布该教案")

    classroom_ids = set(publish_in.classroom_ids)
    if not classroom_ids:
        raise HTTPException(status_code=400, detail="发布教案时必须指定至少一个班级")

    classrooms_result = await db.execute(
        select(Classroom).where(Classroom.id.in_(classroom_ids))
    )
    classrooms = classrooms_result.scalars().all()
    existing_classroom_ids = {cast(int, classroom.id) for classroom in classrooms}
    missing_ids = classroom_ids - existing_classroom_ids
    if missing_ids:
        missing_str = ", ".join(str(cid) for cid in sorted(missing_ids))
        raise HTTPException(status_code=404, detail=f"班级不存在: {missing_str}")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    if user_role == UserRole.TEACHER:
        if current_user.school_id is None:
            raise HTTPException(status_code=400, detail="教师缺少所属学校信息，无法分配班级")
        for classroom in classrooms:
            classroom_school_id = cast(Optional[int], classroom.school_id)
            classroom_head_teacher_id = cast(Optional[int], classroom.head_teacher_id)
            if (
                classroom_school_id != current_user.school_id
                and classroom_head_teacher_id != current_user.id
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"无权将教案发布到班级 {classroom.name}",
                )

    existing_relations = {
        cast(int, relation.classroom_id): relation
        for relation in lesson.lesson_classrooms
    }

    for classroom_id, relation in list(existing_relations.items()):
        if classroom_id not in classroom_ids:
            await db.delete(relation)

    now = datetime.utcnow()
    lesson_id_value = cast(int, lesson.id)
    for classroom in classrooms:
        classroom_id_value = cast(int, classroom.id)
        relation = existing_relations.get(classroom_id_value)
        if relation:
            relation.assigned_by = current_user.id
            relation.assigned_at = now
        else:
            db.add(
                LessonClassroom(
                    lesson_id=lesson_id_value,
                    classroom_id=classroom_id_value,
                    assigned_by=current_user.id,
                    assigned_at=now,
                )
            )

    setattr(lesson, "status", LessonStatus.PUBLISHED)
    setattr(lesson, "published_at", datetime.utcnow())

    await db.commit()
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案发布后加载失败")

    return _lesson_to_response(lesson)


@router.post("/{lesson_id}/unpublish", response_model=LessonResponse)
async def unpublish_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """将已发布的教案切换回草稿状态"""
    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该教案")

    if LessonStatus(cast(str, lesson.status)) != LessonStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="该教案不是已发布状态，无需取消发布")

    setattr(lesson, "status", LessonStatus.DRAFT)
    setattr(lesson, "published_at", None)

    await db.commit()
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案取消发布后加载失败")

    return _lesson_to_response(lesson)


@router.post("/{lesson_id}/duplicate", response_model=LessonResponse)
async def duplicate_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """复制教案"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    # 创建副本
    new_lesson = Lesson(
        title=f"{lesson.title} (副本)",
        description=lesson.description,
        creator_id=current_user.id,
        course_id=lesson.course_id,
        content=lesson.content,
        tags=lesson.tags,
        parent_id=lesson.id,
        national_resource_id=lesson.national_resource_id,
    )

    db.add(new_lesson)
    await db.commit()
    new_lesson_id = cast(int, new_lesson.id)
    lesson_copy = await _get_lesson_with_relations(db, new_lesson_id)
    if not lesson_copy:
        raise HTTPException(status_code=500, detail="教案复制后加载失败")

    return _lesson_to_response(lesson_copy)


# ========== MVP: 基于资源创建教案相关端点 ==========


class CreateFromResourceRequest(BaseModel):
    """基于资源创建教案的请求"""

    reference_resource_id: int = Field(..., description="参考资源ID")
    title: str = Field(..., max_length=200, description="教案标题")
    description: Optional[str] = Field(None, description="教案描述")
    reference_notes: Optional[str] = Field(None, description="参考笔记")
    tags: Optional[List[str]] = Field(None, description="标签")
    estimated_duration: Optional[int] = Field(None, description="预计时长（分钟）")


@router.post("/from-resource", response_model=LessonResponse, status_code=201)
async def create_lesson_from_resource(
    data: CreateFromResourceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """基于参考资源创建教案"""

    # 1. 验证资源存在
    resource = await db.get(Resource, data.reference_resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 2. 获取资源所属的章节和课程
    chapter = await db.get(Chapter, resource.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    course = await db.get(Course, chapter.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    if course.is_active is False:
        raise HTTPException(status_code=400, detail="该课程已被禁用")

    # 3. 创建教案，自动关联到章节
    lesson = Lesson(
        title=data.title,
        description=data.description,
        creator_id=current_user.id,
        course_id=course.id,
        chapter_id=chapter.id,  # 自动关联到章节
        reference_resource_id=data.reference_resource_id,
        reference_notes=data.reference_notes,
        tags=data.tags or [],
        estimated_duration=data.estimated_duration,
        content=[],  # 空内容，教师自己添加Cell
        cell_count=0,
        status=LessonStatus.DRAFT,
    )

    db.add(lesson)
    await db.commit()
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案创建后加载失败")

    return _lesson_to_response(lesson)


@router.get("/{lesson_id}/reference-resource")
async def get_lesson_reference_resource(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案的参考资源"""

    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该教案")

    if lesson.reference_resource_id is None:
        return None

    resource = await db.get(Resource, lesson.reference_resource_id)
    if not resource:
        return None

    # 获取章节信息
    chapter = await db.get(Chapter, resource.chapter_id)

    return {
        **resource.__dict__,
        "chapter": (
            {"id": chapter.id, "name": chapter.name, "course_id": chapter.course_id}
            if chapter
            else None
        ),
    }


class UpdateReferenceNotesRequest(BaseModel):
    """更新参考笔记的请求"""

    notes: str = Field(..., description="参考笔记内容")


@router.put("/{lesson_id}/reference-notes", response_model=LessonResponse)
async def update_reference_notes(
    lesson_id: int,
    data: UpdateReferenceNotesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新教案的参考笔记"""

    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该教案")

    setattr(lesson, "reference_notes", data.notes)

    await db.commit()
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="更新参考笔记后加载失败")

    return _lesson_to_response(lesson)


@router.get("/chapter/{chapter_id}", response_model=LessonListResponse)
async def get_chapter_lessons(
    chapter_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态筛选: draft, published, archived"),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取指定章节下的教案列表"""

    # 转换 status 字符串为枚举类型
    status_enum = None
    if status:
        try:
            status_enum = LessonStatus(status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")

    # 验证章节存在
    chapter_result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = chapter_result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    if chapter.is_active is False:
        raise HTTPException(status_code=400, detail="该章节已被禁用")

    query = (
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.chapter),
            selectinload(Lesson.creator),
            selectinload(Lesson.lesson_classrooms).selectinload(
                LessonClassroom.classroom
            ),
            selectinload(Lesson.reference_resource),
        )
        .where(
            or_(
                Lesson.creator_id == current_user.id,
                Lesson.status == LessonStatus.PUBLISHED
            ),
            Lesson.chapter_id == chapter_id
        )
    )

    if status_enum:
        query = query.where(Lesson.status == status_enum)

    if search:
        query = query.where(Lesson.title.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    ordered_query = query.order_by(Lesson.updated_at.desc())
    paginated_query = ordered_query.offset((page - 1) * page_size).limit(page_size)

    lessons = (await db.execute(paginated_query)).scalars().all()
    serialized_lessons = [_lesson_to_response(lesson) for lesson in lessons]

    return LessonListResponse(
        items=serialized_lessons,
        total=total,
        page=page,
        page_size=page_size,
    )
