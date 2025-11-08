"""
教案API路由
"""

from datetime import datetime
from typing import Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, Lesson, LessonStatus, Course, Resource, Chapter, DifficultyLevel
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse, LessonListResponse
from app.api.v1.auth import get_current_active_user
from app.api.deps import get_current_user_optional
from pydantic import BaseModel, Field

router = APIRouter()


@router.post("/", response_model=LessonResponse, status_code=201)
async def create_lesson(
    lesson_in: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建教案"""
    # 验证课程存在
    course_result = await db.execute(select(Course).where(Course.id == lesson_in.course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    if not course.is_active:
        raise HTTPException(status_code=400, detail="该课程已被禁用")

    # 验证章节存在（如果提供了章节ID）
    if lesson_in.chapter_id:
        chapter_result = await db.execute(select(Chapter).where(Chapter.id == lesson_in.chapter_id))
        chapter = chapter_result.scalar_one_or_none()
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")

        if chapter.course_id != lesson_in.course_id:
            raise HTTPException(status_code=400, detail="章节不属于指定课程")

        if not chapter.is_active:
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
    await db.refresh(lesson)

    # 重新加载以获取课程关联信息
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
        )
        .where(Lesson.id == lesson.id)
    )
    lesson = result.scalar_one()

    return lesson


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
    # 转换 status 字符串为枚举类型
    status_enum = None
    if status:
        try:
            status_enum = LessonStatus(status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")

    # 构建查询
    query = select(Lesson).options(
        selectinload(Lesson.course).selectinload(Course.subject),
        selectinload(Lesson.course).selectinload(Course.grade),
        selectinload(Lesson.creator),  # 加载教师信息
    )

    # 根据用户角色应用不同的过滤条件
    if current_user.role == "student":
        # 学生：只能看到已发布的课程
        query = query.where(Lesson.status == LessonStatus.PUBLISHED)
    else:
        # 教师/管理员/教研员：只能看到自己创建的课程
        query = query.where(Lesson.creator_id == current_user.id)
        # 对于非学生用户，可以通过status参数进一步筛选
        if status_enum:
            query = query.where(Lesson.status == status_enum)

    if search:
        query = query.where(Lesson.title.ilike(f"%{search}%"))

    if course_id:
        query = query.where(Lesson.course_id == course_id)

    if chapter_id:
        query = query.where(Lesson.chapter_id == chapter_id)

    # 如果按学科或年级筛选，需要join课程表
    if subject_id or grade_id:
        query = query.join(Course)
        if subject_id:
            query = query.where(Course.subject_id == subject_id)
        if grade_id:
            query = query.where(Course.grade_id == grade_id)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Lesson.updated_at.desc())

    result = await db.execute(query)
    lessons = result.scalars().all()

    # 为每个lesson添加教师信息
    lessons_with_creator = []
    for lesson in lessons:
        lesson_dict = {
            **{k: v for k, v in lesson.__dict__.items() if not k.startswith("_")},
            "creator_name": lesson.creator.full_name if lesson.creator else None,
            "creator_avatar": lesson.creator.avatar_url if lesson.creator else None,
        }
        lessons_with_creator.append(lesson_dict)

    return LessonListResponse(
        items=lessons_with_creator,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案详情"""
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.creator),  # 加载教师信息
        )
        .where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    # 检查权限（可以查看自己的或已发布的）
    if lesson.creator_id != current_user.id and lesson.status != LessonStatus.PUBLISHED:
        raise HTTPException(status_code=403, detail="无权访问该教案")

    # 添加教师信息
    lesson_dict = {
        **{k: v for k, v in lesson.__dict__.items() if not k.startswith("_")},
        "creator_name": lesson.creator.full_name if lesson.creator else None,
        "creator_avatar": lesson.creator.avatar_url if lesson.creator else None,
    }

    return lesson_dict


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

    if lesson.creator_id != current_user.id:
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
        if not course.is_active:
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
    if content_updated and lesson.status == LessonStatus.PUBLISHED:
        lesson.version = (lesson.version or 1) + 1
        # 更新 published_at 时间戳，表示内容已更新
        lesson.published_at = datetime.utcnow()

    await db.commit()
    await db.refresh(lesson)
    return lesson


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

    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该教案")

    await db.delete(lesson)
    await db.commit()


@router.post("/{lesson_id}/publish", response_model=LessonResponse)
async def publish_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """发布教案"""
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

    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权发布该教案")

    lesson.status = LessonStatus.PUBLISHED
    lesson.published_at = datetime.utcnow()

    await db.commit()
    await db.refresh(lesson)

    # 重新加载以确保关联信息完整
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
        )
        .where(Lesson.id == lesson.id)
    )
    lesson = result.scalar_one()

    return lesson


@router.post("/{lesson_id}/unpublish", response_model=LessonResponse)
async def unpublish_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """将已发布的教案切换回草稿状态"""
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

    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该教案")

    if lesson.status != LessonStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="该教案不是已发布状态，无需取消发布")

    lesson.status = LessonStatus.DRAFT
    lesson.published_at = None

    await db.commit()
    await db.refresh(lesson)

    # 重新加载以确保关联信息完整
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
        )
        .where(Lesson.id == lesson.id)
    )
    lesson = result.scalar_one()

    return lesson


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
    await db.refresh(new_lesson)

    # 重新加载以获取课程关联信息
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
        )
        .where(Lesson.id == new_lesson.id)
    )
    new_lesson = result.scalar_one()

    return new_lesson


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

    if not course.is_active:
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
    await db.refresh(lesson)

    # 4. 重新加载以获取关联信息
    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.reference_resource),
        )
        .where(Lesson.id == lesson.id)
    )
    lesson = result.scalar_one()

    return lesson


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

    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该教案")

    if not lesson.reference_resource_id:
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

    result = await db.execute(
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.reference_resource),
        )
        .where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该教案")

    lesson.reference_notes = data.notes

    await db.commit()
    await db.refresh(lesson)

    return lesson


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

    if not chapter.is_active:
        raise HTTPException(status_code=400, detail="该章节已被禁用")

    # 构建查询
    query = (
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.chapter),
        )
        .where(Lesson.creator_id == current_user.id, Lesson.chapter_id == chapter_id)
    )

    if status_enum:
        query = query.where(Lesson.status == status_enum)

    if search:
        query = query.where(Lesson.title.ilike(f"%{search}%"))

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Lesson.updated_at.desc())

    result = await db.execute(query)
    lessons = result.scalars().all()

    return LessonListResponse(items=lessons, total=total, page=page, page_size=page_size)


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
    # 获取已发布的课程，按评分和发布时间排序
    query = (
        select(Lesson)
        .options(
            selectinload(Lesson.course).selectinload(Course.subject),
            selectinload(Lesson.course).selectinload(Course.grade),
            selectinload(Lesson.creator),  # 加载教师信息
        )
        .where(Lesson.status == LessonStatus.PUBLISHED)
        .order_by(
            func.coalesce(Lesson.average_rating, 0).desc(),
            func.coalesce(Lesson.published_at, Lesson.created_at).desc()
        )
        .limit(limit)
    )

    result = await db.execute(query)
    lessons = result.scalars().all()

    # 为每个lesson添加教师信息（使用字典格式，与list_lessons保持一致）
    lessons_with_creator = []
    for lesson in lessons:
        lesson_dict = {
            **{k: v for k, v in lesson.__dict__.items() if not k.startswith("_")},
            "creator_name": lesson.creator.full_name if lesson.creator else None,
            "creator_avatar": lesson.creator.avatar_url if lesson.creator else None,
        }
        lessons_with_creator.append(lesson_dict)

    return LessonListResponse(
        items=lessons_with_creator, total=len(lessons), page=1, page_size=limit
    )
