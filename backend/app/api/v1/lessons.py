"""
教案API路由
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, selectinload

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
    LessonCreatorStatusCounts,
    LessonClassroomInfo,
    LessonPublishRequest,
    LessonRelatedMaterial,
    LessonRelatedMaterialListResponse,
)
from app.api.v1.auth import get_current_active_user
from app.api.deps import get_current_user_optional
from pydantic import BaseModel, Field
from app.utils.resource_url import filename_to_url, url_to_filename
from app.services.classroom_service import ClassroomQueryService

router = APIRouter()


async def _get_lesson_with_relations(
    db: AsyncSession, lesson_id: int
) -> Optional[Lesson]:
    """加载包含必要关联关系的教案"""
    # 确保 Lesson 已导入（防止作用域问题）
    from app.models.lesson import Lesson
    
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


def _convert_content_urls(content: Any, request: Optional[Request] = None) -> Any:
    """
    递归转换content中的URL（文件名 → 完整URL）
    用于在API返回前转换lesson.content中的资源URL
    
    转换规则：
    - 动态服务器地址（从 request.base_url 获取，如果没有设置 RESOURCE_BASE_URL）
    - .env设定的目录（RESOURCE_BASE_PATH，默认 /uploads/resources）
    - 文件名（数据库存储的格式）
    
    最终格式：{动态服务器地址}/{RESOURCE_BASE_PATH}/{文件名}
    例如：http://192.168.2.53:8000/uploads/resources/7a7a6bc2-64fa-4ec7-ae0b-27127fae74ba.png
    """
    if isinstance(content, dict):
        result = {}
        for key, value in content.items():
            # 转换常见的URL字段（视频、缩略图等）
            if key in ("videoUrl", "video_url", "thumbnail", "thumbnail_url", "url", "src"):
                if isinstance(value, str) and value:
                    # blob URL和data URL不转换
                    if value.startswith(("blob:", "data:")):
                        result[key] = value
                    # 如果是完整URL，检查是否是资源URL，如果是则提取文件名后重新构建（使用动态服务器地址）
                    elif value.startswith(("http://", "https://")):
                        # 检查是否是资源URL（/uploads/resources/或/uploads/thumbnails/）
                        if "/uploads/resources/" in value or "/uploads/thumbnails/" in value:
                            # 提取文件名，然后使用动态服务器地址重新构建URL
                            filename = url_to_filename(value)
                            result[key] = filename_to_url(filename, request)
                        else:
                            # 不是资源URL，保持原样（可能是外部链接）
                            result[key] = value
                    # 如果是文件名或相对路径，转换为完整URL
                    # 使用 filename_to_url：动态服务器地址 + .env目录 + 文件名
                    else:
                        result[key] = filename_to_url(value, request)
                else:
                    result[key] = value
            elif key == "html" and isinstance(value, str):
                # 处理文本模块HTML内容中的资源URL（图片、文件、PDF等）
                import re
                html = value
                # 替换img标签中的src属性（文本模块中的图片）
                html = re.sub(
                    r'(<img[^>]*\s+src\s*=\s*["\'])([^"\']+)(["\'][^>]*>)',
                    lambda m: (
                        # 使用 filename_to_url：动态服务器地址 + .env目录 + 文件名
                        f'{m.group(1)}{filename_to_url(m.group(2), request)}{m.group(3)}'
                        if m.group(2) and not m.group(2).startswith(("blob:", "data:", "http://", "https://"))
                        else m.group(0)
                    ),
                    html,
                    flags=re.IGNORECASE
                )
                # 替换data-pdf-url、data-file-url等属性（文本模块中的文件附件）
                for attr in ["data-pdf-url", "data-file-url", "data-file-download-url", "data-pdf-view-url", "href"]:
                    pattern = f'({attr}\\s*=\\s*["\'])([^"\']+)(["\'])'
                    html = re.sub(
                        pattern,
                        lambda m: (
                            # 使用 filename_to_url：动态服务器地址 + .env目录 + 文件名
                            f'{m.group(1)}{filename_to_url(m.group(2), request)}{m.group(3)}'
                            if m.group(2) and not m.group(2).startswith(("blob:", "data:", "http://", "https://"))
                            else m.group(0)
                        ),
                        html,
                        flags=re.IGNORECASE
                    )
                result[key] = html
            else:
                result[key] = _convert_content_urls(value, request)
        return result
    elif isinstance(content, list):
        return [_convert_content_urls(item, request) for item in content]
    else:
        return content


def _lesson_to_response(lesson: Lesson, request: Optional[Request] = None, skip_content_conversion: bool = False, include_content: bool = True) -> LessonResponse:
    """将教案对象转换为响应字典，并转换URL为完整URL

    Args:
        lesson: 教案对象
        request: FastAPI请求对象
        skip_content_conversion: 是否跳过content字段的URL转换（用于列表API优化性能）
        include_content: 是否包含完整的content字段（列表API设为False以减少响应大小）
    """
    # 导入日志记录器
    import logging
    logger = logging.getLogger(__name__)

    lesson_data = {
        k: v
        for k, v in lesson.__dict__.items()
        if not k.startswith("_") and k not in {"lesson_classrooms", "creator"}
    }

    # 如果 cell_count 为 0，从 content 动态计算（支持新旧格式）
    def _calculate_cell_count(content: Any) -> int:
        """计算 content 中的 cell 数量，支持 List[dict] 或 {sections:[{cells:[]}]}"""
        if content is None:
            return 0
        if isinstance(content, list):
            return len(content)
        if isinstance(content, dict) and "sections" in content:
            sections = content.get("sections", [])
            return sum(len(s.get("cells", [])) for s in sections)
        return 0

    db_cell_count = cast(int, lesson.cell_count) if lesson.cell_count is not None else 0
    # 列表 API 使用 defer(content) 时不应访问 lesson.content，否则会按行懒加载，抵消优化
    if db_cell_count == 0 and include_content:
        calculated_count = _calculate_cell_count(lesson.content)
        if calculated_count > 0:
            lesson_data["cell_count"] = calculated_count

    # 性能优化：列表API可以完全不返回content，只返回元数据
    # 这样可以将响应大小从27MB降到几百KB
    if not include_content:
        # 不返回content，只返回cell_count供前端显示
        lesson_data["content"] = []
    elif skip_content_conversion:
        # 跳过URL转换，直接返回原始content
        raw_content = lesson.content or []
        lesson_data["content"] = raw_content
    else:
        # 转换content中的URL（文件名 → 完整URL）
        raw_content = lesson.content or []
        converted_content = _convert_content_urls(raw_content, request)
        # 确保转换后的content被设置到lesson_data中
        lesson_data["content"] = converted_content
    lesson_data.setdefault("tags", lesson.tags or [])
    
    # 转换cover_image_url
    cover_image_url = cast(Optional[str], lesson.cover_image_url)
    if cover_image_url:
        lesson_data["cover_image_url"] = filename_to_url(cover_image_url, request)
    
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
    
    # 在验证前记录原始数据
    content_before_validate = lesson_data["content"]
    content_before_length = len(content_before_validate) if isinstance(content_before_validate, list) else 0
    
    try:
        response = LessonResponse.model_validate(lesson_data)
        content_after_length = len(response.content) if isinstance(response.content, list) else 0
        
        # 如果验证前后数量不一致，记录警告
        if content_before_length != content_after_length:
            logger.warning(
                f"⚠️ 教案 {lesson.id} 在 _lesson_to_response 验证时 content 数量变化: "
                f"{content_before_length} -> {content_after_length}"
            )
            # 记录详细信息
            if isinstance(content_before_validate, list):
                before_ids = [cell.get('id') if isinstance(cell, dict) else None for cell in content_before_validate]
                logger.warning(f"  验证前的IDs: {before_ids}")
            if isinstance(response.content, list):
                after_ids = [cell.get('id') if isinstance(cell, dict) else None for cell in response.content]
                logger.warning(f"  验证后的IDs: {after_ids}")
        
        return response
    except Exception as e:
        logger.error(
            f"❌ 教案 {lesson.id} 在 _lesson_to_response 验证时出错: {e}, "
            f"content长度={content_before_length}"
        )
        raise


@router.post("/", response_model=LessonResponse, status_code=201)
async def create_lesson(
    request: Request,
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

    # 计算 cell_count（支持旧格式 List 和新格式 {sections: [{cells:[]}]}）
    if isinstance(lesson_in.content, dict) and "sections" in lesson_in.content:
        cell_count = sum(
            len(s.get("cells") or [])
            for s in (lesson_in.content.get("sections") or [])
        )
    else:
        content_list = lesson_in.content if isinstance(lesson_in.content, list) else []
        cell_count = len(content_list)

    lesson = Lesson(
        title=lesson_in.title,
        description=lesson_in.description,
        creator_id=current_user.id,
        course_id=lesson_in.course_id,
        chapter_id=lesson_in.chapter_id,
        content=lesson_in.content,
        tags=lesson_in.tags or [],
        national_resource_id=lesson_in.national_resource_id,
        cell_count=cell_count,  # 设置 cell_count
    )
    db.add(lesson)
    await db.commit()
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案创建后加载失败")
    return _lesson_to_response(lesson, request)


@router.get("/", response_model=LessonListResponse)
async def list_lessons(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态筛选: draft, published, archived"),
    search: Optional[str] = None,
    course_id: Optional[int] = Query(None, description="按课程ID筛选"),
    chapter_id: Optional[int] = Query(None, description="按章节ID筛选"),
    subject_id: Optional[int] = Query(None, description="按学科ID筛选"),
    grade_id: Optional[int] = Query(None, description="按年级ID筛选"),
    creator_only: bool = Query(False, description="是否只返回当前用户创建的教案"),
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
        defer(Lesson.content),
        selectinload(Lesson.course).selectinload(Course.subject),
        selectinload(Lesson.course).selectinload(Course.grade),
        selectinload(Lesson.creator),
        selectinload(Lesson.lesson_classrooms).selectinload(
            LessonClassroom.classroom
        ),
    )

    if user_role == UserRole.STUDENT:
        # UPDATED: Get ALL active classroom memberships, not just User.classroom_id
        from app.models.classroom_assistant import ClassroomMembership, RoleInClass

        memberships_result = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.user_id == current_user.id,
                ClassroomMembership.role_in_class == RoleInClass.STUDENT,
                ClassroomMembership.is_active == True
            )
        )
        classroom_ids = [m.classroom_id for m in memberships_result.scalars()]

        if not classroom_ids:
            return LessonListResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
            )

        base_query = (
            base_query.join(LessonClassroom)
            .where(Lesson.status == LessonStatus.PUBLISHED)
            .where(LessonClassroom.classroom_id.in_(classroom_ids))
            .distinct(Lesson.id)
        )
    else:
        # 教师/管理员/教研员
        if creator_only:
            # 如果指定了creator_only=True，只返回当前用户创建的教案
            base_query = base_query.where(Lesson.creator_id == current_user.id)
            if status_enum:
                base_query = base_query.where(Lesson.status == status_enum)
        else:
            # 管理员和教研员可以看到所有教案（用于课程体系管理）
            if user_role in {UserRole.ADMIN, UserRole.RESEARCHER}:
                # 管理员和教研员：可以看到所有教案
                if status_enum:
                    base_query = base_query.where(Lesson.status == status_enum)
                # 如果没有状态筛选，显示所有状态的教案（不添加状态过滤）
            else:
                # 教师：默认行为：可以看到自己创建的教案 + 所有已发布的教案（共享教案）
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
    # 性能优化：列表API完全不返回content，将响应大小从27MB降到几百KB
    # content会在详情API(get_lesson)中返回
    serialized_lessons = [_lesson_to_response(lesson, request, include_content=False) for lesson in lessons]

    return LessonListResponse(
        items=serialized_lessons,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/creator-status-counts", response_model=LessonCreatorStatusCounts)
async def get_creator_lesson_status_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """当前用户创建的教案按状态计数。供教师工作台 PDCA 首屏使用，替代 3 次分页列表请求。"""
    stmt = (
        select(Lesson.status, func.count(Lesson.id))
        .where(Lesson.creator_id == current_user.id)
        .group_by(Lesson.status)
    )
    result = await db.execute(stmt)
    counts = {LessonStatus.DRAFT: 0, LessonStatus.PUBLISHED: 0, LessonStatus.ARCHIVED: 0}
    for row in result.all():
        status_val, cnt = row[0], int(row[1] or 0)
        if isinstance(status_val, LessonStatus):
            key = status_val
        else:
            try:
                key = LessonStatus(str(status_val).lower())
            except ValueError:
                continue
        if key in counts:
            counts[key] = cnt
    return LessonCreatorStatusCounts(
        draft=counts[LessonStatus.DRAFT],
        published=counts[LessonStatus.PUBLISHED],
        archived=counts[LessonStatus.ARCHIVED],
    )


@router.get("/recommended", response_model=LessonListResponse)
async def get_recommended_lessons(
    request: Request,
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
            defer(Lesson.content),
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

    # 性能优化：推荐课程列表不返回content，减少响应大小
    lesson_responses = [_lesson_to_response(lesson, request, include_content=False) for lesson in lessons]

    if (
        current_user
        and isinstance(current_user.role, UserRole)
        and cast(UserRole, current_user.role) == UserRole.STUDENT
    ):
        # UPDATED: Get ALL active classroom memberships for student
        from app.models.classroom_assistant import ClassroomMembership, RoleInClass

        memberships_result = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.user_id == current_user.id,
                ClassroomMembership.role_in_class == RoleInClass.STUDENT,
                ClassroomMembership.is_active == True
            )
        )
        student_classroom_ids = {m.classroom_id for m in memberships_result.scalars()}

        if student_classroom_ids:
            lesson_responses = [
                lesson
                for lesson in lesson_responses
                if student_classroom_ids.intersection(lesson.classroom_ids)
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
                .options(defer(Lesson.content))
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
    from app.models import UserRole

    # Validate user role
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    # Only teachers, admins, and researchers can publish lessons
    if user_role not in {UserRole.TEACHER, UserRole.ADMIN, UserRole.RESEARCHER}:
        raise HTTPException(status_code=403, detail="仅教师或管理员可查看班级列表")

    # Use unified service to get active classrooms only
    service = ClassroomQueryService()
    classrooms = await service.get_classrooms_for_user(
        db, current_user, is_active=True
    )

    return [
        LessonClassroomInfo.model_validate(classroom) for classroom in classrooms
    ]


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案详情"""
    # 确保 Lesson 已导入（防止作用域问题）
    from app.models.lesson import Lesson
    from app.models.classroom_assistant import ClassroomMembership, RoleInClass
    from app.services.permission_service import PermissionService

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

        # Use PermissionService to check access via ClassroomMembership
        permission_service = PermissionService()
        has_access = await permission_service.can_student_view_lesson(db, current_user, lesson_id)

        if not has_access:
            raise HTTPException(status_code=403, detail="该教案未分配到你的班级")
    elif user_role in {UserRole.ADMIN, UserRole.RESEARCHER}:
        # 管理员和教研员可以查看所有教案（包括草稿状态）
        # 不需要额外的权限检查
        pass
    else:
        # 教师：只能查看自己创建的教案或已发布的教案
        if creator_id != current_user.id and lesson_status != LessonStatus.PUBLISHED:
            raise HTTPException(status_code=403, detail="无权访问该教案")

    return _lesson_to_response(lesson, request)


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    request: Request,
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

    # 权限检查：创建者可以修改，管理员和研究员也可以修改（用于课程管理）
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        user_role = None
    
    is_admin = user_role == UserRole.ADMIN
    is_researcher = user_role == UserRole.RESEARCHER
    is_creator = cast(Optional[int], lesson.creator_id) == current_user.id
    
    # 如果更新 course_id，验证课程存在
    # 使用 exclude_unset=True 只包含明确设置的字段
    # 注意：空数组 [] 会被视为已设置，所以会被包含
    update_data = lesson_in.model_dump(exclude_unset=True)
    
    # 如果只是更新 chapter_id（关联到章节），管理员和研究员也可以操作
    is_only_chapter_update = len(update_data) == 1 and 'chapter_id' in update_data
    
    if not is_creator:
        if not (is_admin or is_researcher):
            raise HTTPException(status_code=403, detail="无权修改该教案")
        # 管理员和研究员只能更新章节关联，不能修改其他内容
        if not is_only_chapter_update:
            raise HTTPException(
                status_code=403, 
                detail="管理员和研究员只能关联教案到章节，不能修改教案的其他内容"
            )
    
    # 调试日志：记录更新数据（包括原始请求数据）
    import logging
    logger = logging.getLogger(__name__)
    
    # 记录原始请求数据（在 Pydantic 验证之前）
    raw_content = getattr(lesson_in, 'content', None)
    raw_content_length = len(raw_content) if isinstance(raw_content, list) else (0 if raw_content is None else 'N/A')
    logger.info(
        f"更新教案 {lesson_id}: 原始请求 content长度={raw_content_length}, "
        f"更新字段={list(update_data.keys())}, "
        f"处理后content长度={len(update_data.get('content', [])) if 'content' in update_data else '未更新'}"
    )
    
    # 如果 content 在原始请求中但不在 update_data 中，说明可能有问题
    if hasattr(lesson_in, 'content') and lesson_in.content is not None and 'content' not in update_data:
        logger.error(
            f"❌ 严重错误：教案 {lesson_id} 的 content 字段在请求中存在但未包含在 update_data 中！"
            f"原始content类型={type(lesson_in.content)}, 值={lesson_in.content}"
        )
        # 强制包含 content 字段
        update_data['content'] = lesson_in.content
    
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

    def _content_cell_count(c: Any) -> int:
        """计算 content 中的 cell 数量，支持 List[dict] 或 {sections:[{cells:[]}]}"""
        if c is None:
            return 0
        if isinstance(c, list):
            return len(c)
        if isinstance(c, dict) and "sections" in c:
            return sum(len(s.get("cells") or []) for s in (c.get("sections") or []))
        return 0

    if "content" in update_data:
        old_content = lesson.content
        new_content = update_data["content"]

        # 支持两种格式：List[dict]（旧）或 { "sections": [ { "cells": [...] } ] }（新）
        # 不要将 sections 格式错误地替换为 []，否则会导致所有 cell 丢失
        if new_content is not None and not isinstance(new_content, list) and not (
            isinstance(new_content, dict) and "sections" in new_content
        ):
            logger.error(
                f"❌ 教案 {lesson_id} content 字段类型错误: 期望 list 或 {{sections}}，实际 {type(new_content)}"
            )
            if isinstance(new_content, (str, bytes)):
                try:
                    parsed = json.loads(new_content)
                    if isinstance(parsed, list) or (
                        isinstance(parsed, dict) and "sections" in parsed
                    ):
                        new_content = parsed
                    else:
                        new_content = []
                except Exception:
                    new_content = []
            else:
                new_content = []
            update_data["content"] = new_content

        # 详细日志：记录保存前后的内容对比（兼容 list 与 sections）
        old_count = _content_cell_count(old_content)
        new_count = _content_cell_count(new_content)
        logger.info(
            f"教案 {lesson_id} 内容更新详情: "
            f"保存前 cell 数={old_count}, "
            f"保存后 cell 数={new_count}"
        )

        # 检查每个 cell 的详细信息并验证数据完整性（支持 list 与 sections）
        if new_content and isinstance(new_content, list):
            cell_ids = []
            invalid_cells = []
            for idx, cell in enumerate(new_content):
                if not isinstance(cell, dict):
                    logger.warning(
                        f"⚠️ 教案 {lesson_id} Cell[{idx}] 不是字典类型: {type(cell)}, 值={cell}"
                    )
                    # 尝试修复：如果是其他类型，转换为字典
                    if hasattr(cell, '__dict__'):
                        cell = cell.__dict__
                    elif hasattr(cell, 'model_dump'):
                        cell = cell.model_dump()
                    else:
                        invalid_cells.append(idx)
                        cell_ids.append(f"invalid_{idx}")
                        continue
                    # 更新列表中的 cell
                    new_content[idx] = cell
                
                cell_id = cell.get('id')
                cell_type = cell.get('type')
                has_content = bool(cell.get('content'))
                cell_ids.append(str(cell_id) if cell_id else f"no_id_{idx}")
                
                # 验证必需的字段（只记录警告，不过滤）
                if not cell_id:
                    logger.warning(
                        f"⚠️ 教案 {lesson_id} Cell[{idx}] 缺少 id 字段，将使用索引作为临时ID"
                    )
                    # 如果没有 id，生成一个临时 ID（但这不是最佳实践，应该由前端提供）
                    if not cell_id:
                        import uuid
                        cell['id'] = str(uuid.uuid4())
                        logger.debug("Cell[%d] assigned temp ID: %s", idx, cell['id'])
                
                if not cell_type:
                    logger.warning(
                        f"⚠️ 教案 {lesson_id} Cell[{idx}] 缺少 type 字段，将使用默认值 'text'"
                    )
                    # 如果没有 type，使用默认值
                    if not cell_type:
                        cell['type'] = 'text'
                        logger.debug("Cell[%d] defaulted to type=text", idx)
                
                logger.debug(
                    f"  保存Cell[{idx}]: id={cell.get('id')}, type={cell.get('type')}, "
                    f"has_content={has_content}"
                )
            
            # 移除无效的 cell（如果无法修复）
            if invalid_cells:
                logger.error(
                    f"❌ 教案 {lesson_id} 发现 {len(invalid_cells)} 个无法修复的无效 cell，索引: {invalid_cells}"
                )
                # 记录每个被移除的 cell 的详细信息
                for idx in invalid_cells:
                    if idx < len(new_content):
                        invalid_cell = new_content[idx]
                        logger.error(
                            f"  被移除的 Cell[{idx}]: type={type(invalid_cell)}, "
                            f"value={invalid_cell if not isinstance(invalid_cell, dict) else f'dict with keys: {list(invalid_cell.keys())}'}"
                        )
                # 从后往前删除，避免索引变化
                for idx in reversed(invalid_cells):
                    new_content.pop(idx)
                logger.debug("Removed invalid cells, remaining: %d", len(new_content))
            
            logger.debug("Lesson %s saving %d cells", lesson_id, len(new_content))
            # 更新 update_data 中的 content
            update_data["content"] = new_content

        elif isinstance(new_content, dict) and "sections" in new_content:
            # 新格式 { sections: [ { cells: [...] } ] }：对每个 section 的 cells 做校验与补全
            import uuid as _uuid
            for sec in new_content.get("sections") or []:
                cells = sec.get("cells") or []
                invalid_cells = []
                for idx, cell in enumerate(cells):
                    if not isinstance(cell, dict):
                        if hasattr(cell, "__dict__"):
                            cells[idx] = cell.__dict__
                            cell = cells[idx]
                        elif hasattr(cell, "model_dump"):
                            cells[idx] = cell.model_dump()
                            cell = cells[idx]
                        else:
                            invalid_cells.append(idx)
                            continue
                    if not cell.get("id"):
                        cell["id"] = str(_uuid.uuid4())
                    if not cell.get("type"):
                        cell["type"] = "text"
                for idx in reversed(invalid_cells):
                    cells.pop(idx)
                sec["cells"] = cells
            logger.debug("Lesson %s saving sections format, %d cells", lesson_id, _content_cell_count(new_content))

        # 比较内容是否真正发生变化（兼容 list 与 {sections}）
        # cast: 避免类型检查器将 lesson.content 的 != 推断为 ColumnElement[bool]
        content_changed = cast(bool, old_content != new_content)
        if content_changed:
            content_updated = True
            oc, nc = _content_cell_count(old_content), _content_cell_count(new_content)
            if oc != nc:
                logger.warning(
                    f"⚠️ 教案 {lesson_id} 内容 cell 数变化: {oc} -> {nc}"
                )

    # 更新字段
    for field, value in update_data.items():
        # 对于 content 字段：支持 list 或 {sections}，仅对非法类型做修复
        if field == "content":
            if value is not None and not isinstance(value, list) and not (
                isinstance(value, dict) and "sections" in value
            ):
                logger.error(
                    f"❌ 教案 {lesson_id} 在设置 content 字段时类型错误: "
                    f"期望 list 或 {{sections}}，实际 {type(value)}"
                )
                if isinstance(value, (str, bytes)):
                    try:
                        value = json.loads(value)
                        if not isinstance(value, list) and not (
                            isinstance(value, dict) and "sections" in value
                        ):
                            value = []
                    except Exception:
                        value = []
                else:
                    value = []
            if value is None:
                value = []
            logger.debug("Lesson %s content set: type=%s cells=%d", lesson_id, type(value).__name__, _content_cell_count(value))
        setattr(lesson, field, value)

        if field == "content":
            set_value = getattr(lesson, field, None)
            logger.debug("Lesson %s content verified: type=%s cells=%d", lesson_id, type(set_value).__name__, _content_cell_count(set_value))

    # 如果更新了内容，自动更新 cell_count（兼容 list 与 {sections}）
    if content_updated:
        cell_count = _content_cell_count(lesson.content)
        setattr(lesson, "cell_count", cell_count)
        logger.debug("Lesson %s cell_count updated: %d", lesson_id, cell_count)
    
    # 如果更新了已发布教案的内容，自动更新版本号
    # 这样学生端可以通过版本号判断是否有新内容
    if content_updated and cast(str, lesson.status) == LessonStatus.PUBLISHED:
        current_version = cast(Optional[int], lesson.version)
        new_version = (current_version or 1) + 1
        setattr(lesson, "version", new_version)
        # 更新 published_at 时间戳，表示内容已更新
        setattr(lesson, "published_at", datetime.utcnow())

    await db.commit()
    # 刷新对象以确保获取最新数据
    await db.refresh(lesson)
    
    # 调试日志：记录提交后的数据
    content_after_save = lesson.content if isinstance(lesson.content, list) else ([] if lesson.content is None else [])
    logger.info(
        f"教案 {lesson_id} 已提交并刷新: content长度={len(content_after_save)}, "
        f"version={lesson.version}, content类型={type(lesson.content)}"
    )
    
    # 检查数据库中的实际内容 - 详细记录每个 cell
    if isinstance(lesson.content, list) and len(lesson.content) > 0:
        cell_details = []
        for idx, cell in enumerate(lesson.content):
            if isinstance(cell, dict):
                cell_details.append({
                    'index': idx,
                    'id': cell.get('id'),
                    'type': cell.get('type'),
                    'order': cell.get('order'),
                })
            else:
                cell_details.append({'index': idx, 'raw_type': type(cell).__name__})
        logger.info(
            f"  数据库中的content详情: 长度={len(lesson.content)}, "
            f"所有cell信息={cell_details}"
        )
    elif not isinstance(lesson.content, list):
        logger.warning(
            f"⚠️ 教案 {lesson_id} 刷新后 content 不是列表类型: {type(lesson.content)}"
        )
    
    lesson_id_value = cast(int, lesson.id)
    lesson = await _get_lesson_with_relations(db, lesson_id_value)
    if not lesson:
        raise HTTPException(status_code=500, detail="教案更新后加载失败")
    
    # 检查重新加载后的内容
    reloaded_content = lesson.content if isinstance(lesson.content, list) else ([] if lesson.content is None else [])
    reloaded_count = len(reloaded_content)
    logger.info(
        f"教案 {lesson_id} 重新加载后: content长度={reloaded_count}"
    )
    
    # 调试日志：记录返回前的数据
    response_lesson = _lesson_to_response(lesson, request)
    response_count = len(response_lesson.content) if response_lesson.content else 0
    logger.info(
        f"教案 {lesson_id} 返回数据: content长度={response_count}, "
        f"version={response_lesson.version}"
    )
    
    # 如果数量不一致，记录警告
    if "content" in update_data:
        saved_count = len(update_data["content"]) if update_data["content"] else 0
        if saved_count != response_count:
            logger.error(
                f"❌ 严重警告：教案 {lesson_id} 保存前后数量不一致！"
                f"保存时={saved_count}, 返回时={response_count}"
            )
            # 记录详细信息
            if update_data["content"] and isinstance(update_data["content"], list):
                saved_ids = [
                    cell.get('id') if isinstance(cell, dict) else None 
                    for cell in update_data["content"]
                ]
                logger.error(f"  保存时的IDs: {saved_ids}")
                # 记录最后一个 cell 的详细信息
                if len(update_data["content"]) > 0:
                    last_cell = update_data["content"][-1]
                    logger.error(f"  保存时的最后一个cell: {json.dumps(last_cell, ensure_ascii=False, default=str)}")
            if response_lesson.content and isinstance(response_lesson.content, list):
                returned_ids = [
                    cell.get('id') if isinstance(cell, dict) else None 
                    for cell in response_lesson.content
                ]
                logger.error(f"  返回时的IDs: {returned_ids}")
                # 记录最后一个 cell 的详细信息
                if len(response_lesson.content) > 0:
                    last_cell = response_lesson.content[-1]
                    logger.error(f"  返回时的最后一个cell: {json.dumps(last_cell, ensure_ascii=False, default=str)}")
            # 记录数据库中的实际内容
            logger.error(f"  数据库中的content长度: {len(reloaded_content)}")
            if isinstance(reloaded_content, list) and len(reloaded_content) > 0:
                db_last_cell = reloaded_content[-1]
                logger.error(f"  数据库中的最后一个cell: {json.dumps(db_last_cell, ensure_ascii=False, default=str) if isinstance(db_last_cell, dict) else str(db_last_cell)}")
    
    return response_lesson


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

    # 权限检查：创建者可以删除，管理员和教研员也可以删除（用于课程管理）
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        user_role = None
    
    is_admin = user_role == UserRole.ADMIN
    is_researcher = user_role == UserRole.RESEARCHER
    is_creator = cast(Optional[int], lesson.creator_id) == current_user.id
    
    if not (is_creator or is_admin or is_researcher):
        raise HTTPException(status_code=403, detail="无权删除该教案")

    await db.delete(lesson)
    await db.commit()


@router.post("/{lesson_id}/publish", response_model=LessonResponse)
async def publish_lesson(
    lesson_id: int,
    request: Request,
    publish_in: LessonPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """发布教案（可不选班级，班级在上课时选择）"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        lesson = await _get_lesson_with_relations(db, lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="教案不存在")

        lesson_id_value = cast(int, lesson.id)  # 尽早赋值，避免空 classroom_ids 时未定义
        if cast(Optional[int], lesson.creator_id) != current_user.id:
            raise HTTPException(status_code=403, detail="无权发布该教案")

        classroom_ids = set(publish_in.classroom_ids) if publish_in.classroom_ids else set()

        # 如果提供了班级ID，验证并创建关系（向后兼容）
        if classroom_ids:
            # Use ClassroomQueryService to validate classrooms (checks is_active)
            classrooms_result = await db.execute(
                select(Classroom).where(
                    Classroom.id.in_(classroom_ids),
                    Classroom.is_active == True  # ✅ Explicitly check is_active
                )
            )
            classrooms = classrooms_result.scalars().all()
            existing_classroom_ids = {cast(int, classroom.id) for classroom in classrooms}
            missing_ids = classroom_ids - existing_classroom_ids
            if missing_ids:
                missing_str = ", ".join(str(cid) for cid in sorted(missing_ids))
                raise HTTPException(status_code=404, detail=f"班级不存在或未激活: {missing_str}")

            role_value = cast(str, getattr(current_user.role, "value", current_user.role))
            try:
                user_role = UserRole(role_value)
            except ValueError:
                raise HTTPException(status_code=403, detail="当前用户角色无效")

            if user_role == UserRole.TEACHER:
                from app.services.permission_service import PermissionService

                permission_service = PermissionService()
                for classroom in classrooms:
                    if not await permission_service.can_teacher_publish_to_classroom(
                        db, current_user, classroom
                    ):
                        raise HTTPException(
                            status_code=403,
                            detail=f"无权将教案发布到班级 {classroom.name}",
                        )

            existing_relations = {
                cast(int, relation.classroom_id): relation
                for relation in (lesson.lesson_classrooms or [])
            }

            for classroom_id, relation in list(existing_relations.items()):
                if classroom_id not in classroom_ids:
                    await db.delete(relation)

            now = datetime.utcnow()
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

        return _lesson_to_response(lesson, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("publish_lesson failed: %s", e)
        raise HTTPException(status_code=500, detail="发布失败")


@router.post("/{lesson_id}/unpublish", response_model=LessonResponse)
async def unpublish_lesson(
    lesson_id: int,
    request: Request,
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

    return _lesson_to_response(lesson, request)


@router.post("/{lesson_id}/duplicate", response_model=LessonResponse)
async def duplicate_lesson(
    lesson_id: int,
    request: Request,
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

    return _lesson_to_response(lesson_copy, request)


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
    request: Request,
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

    return _lesson_to_response(lesson, request)


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
    request: Request,
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

    return _lesson_to_response(lesson, request)


@router.get("/chapter/{chapter_id}", response_model=LessonListResponse)
async def get_chapter_lessons(
    chapter_id: int,
    request: Request,
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
            defer(Lesson.content),
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
    # 性能优化：章节教案列表不返回content，减少响应大小
    serialized_lessons = [_lesson_to_response(lesson, request, include_content=False) for lesson in lessons]

    return LessonListResponse(
        items=serialized_lessons,
        total=total,
        page=page,
        page_size=page_size,
    )
