"""
资源库资产管理 API
"""

from typing import Optional, List, cast
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import LibraryAsset, User, UserRole, Resource, Chapter, Course
from app.schemas.library_asset import (
    LibraryAssetSummary,
    LibraryAssetDetail,
    LibraryAssetListResponse,
    LibraryAssetUpdate,
    LibraryAssetUploadResponse,
    LibraryAssetUsage,
    LibraryAssetUsageResponse,
)
from app.services.upload import upload_service
from app.api.deps import get_current_user

router = APIRouter()


def _check_library_access(current_user: User) -> None:
    """检查用户是否有资源库访问权限（学生禁止访问）"""
    if not isinstance(current_user.role, UserRole) or cast(
        UserRole, current_user.role
    ) == UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="学生无权访问资源库")
    
    if current_user.school_id is None:
        raise HTTPException(status_code=400, detail="用户必须归属某个学校才能使用资源库")


@router.get("/", response_model=LibraryAssetListResponse)
async def list_library_assets(
    query: Optional[str] = Query(None, description="搜索关键词（标题/描述/知识点名称）"),
    asset_type: Optional[str] = Query(None, description="资源类型筛选"),
    visibility: Optional[str] = Query(None, description="可见性筛选"),
    subject_id: Optional[int] = Query(None, description="学科ID筛选"),
    grade_id: Optional[int] = Query(None, description="年级ID筛选"),
    knowledge_point_category: Optional[str] = Query(None, description="知识点分类筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源库资产列表（仅限非学生访问，按学校隔离）"""
    _check_library_access(current_user)
    
    school_id = cast(int, current_user.school_id)
    user_id = cast(int, current_user.id)
    user_role = cast(UserRole, current_user.role)
    
    # 构建查询
    base_query = select(LibraryAsset).where(LibraryAsset.school_id == school_id)
    
    # 可见性过滤：教师只能看自己上传的和全校可见的；管理员/教研员看全部
    if user_role == UserRole.TEACHER:
        base_query = base_query.where(
            or_(
                LibraryAsset.owner_user_id == user_id,
                LibraryAsset.visibility == "school",
            )
        )
    
    # 搜索
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.where(
            or_(
                LibraryAsset.title.ilike(search_pattern),
                LibraryAsset.description.ilike(search_pattern),
                LibraryAsset.knowledge_point_name.ilike(search_pattern),
            )
        )
    
    # 类型筛选
    if asset_type:
        base_query = base_query.where(LibraryAsset.asset_type == asset_type)
    
    # 可见性筛选
    if visibility:
        base_query = base_query.where(LibraryAsset.visibility == visibility)
    
    # 学科筛选
    if subject_id:
        base_query = base_query.where(LibraryAsset.subject_id == subject_id)
    
    # 年级筛选
    if grade_id is not None:
        base_query = base_query.where(LibraryAsset.grade_id == grade_id)
    
    # 知识点分类筛选
    if knowledge_point_category:
        base_query = base_query.where(LibraryAsset.knowledge_point_category == knowledge_point_category)
    
    # 状态筛选（默认只显示 active）
    if status:
        base_query = base_query.where(LibraryAsset.status == status)
    else:
        base_query = base_query.where(LibraryAsset.status == "active")
    
    # 计数
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页排序
    query_with_order = base_query.order_by(LibraryAsset.updated_at.desc())
    query_with_pagination = query_with_order.offset((page - 1) * page_size).limit(
        page_size
    )
    
    result = await db.execute(query_with_pagination)
    assets = result.scalars().all()
    
    return LibraryAssetListResponse(
        items=[LibraryAssetSummary.model_validate(asset) for asset in assets],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{asset_id}", response_model=LibraryAssetDetail)
async def get_library_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源库资产详情"""
    _check_library_access(current_user)
    
    asset = await db.get(LibraryAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资源库资产不存在")
    
    # 校验归属学校
    asset_school_id = cast(int, asset.school_id)
    user_school_id = cast(int, current_user.school_id)
    if asset_school_id != user_school_id:
        raise HTTPException(status_code=403, detail="无权访问其他学校的资源")
    
    # 可见性校验：教师只能访问自己上传的或全校可见的
    user_role = cast(UserRole, current_user.role)
    user_id = cast(int, current_user.id)
    asset_owner_id = cast(int, asset.owner_user_id)
    asset_visibility = cast(str, asset.visibility)
    
    if user_role == UserRole.TEACHER:
        if asset_owner_id != user_id and asset_visibility != "school":
            raise HTTPException(status_code=403, detail="无权访问此资源")
    
    return LibraryAssetDetail.model_validate(asset)


@router.post("/", response_model=LibraryAssetUploadResponse)
async def upload_library_asset(
    title: str = Form(..., description="资源标题"),
    description: Optional[str] = Form(None, description="资源描述"),
    asset_type: Optional[str] = Form(None, description="资源类型（可选，自动推断）"),
    visibility: str = Form("teacher_only", description="可见性：teacher_only/school"),
    subject_id: Optional[int] = Form(None, description="学科ID（可选）"),
    grade_id: Optional[int] = Form(None, description="年级ID（可选）"),
    knowledge_point_category: Optional[str] = Form(None, description="知识点分类（如：计算类/速算技巧）"),
    knowledge_point_name: Optional[str] = Form(None, description="具体知识点名称（如：乘法口诀可视化）"),
    file: UploadFile = File(..., description="上传的文件"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传资源到资源库"""
    _check_library_access(current_user)
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    school_id = cast(int, current_user.school_id)
    user_id = cast(int, current_user.id)
    
    # 上传文件（复用现有 upload_service）
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    # 根据文件扩展名推断资源类型
    if not asset_type:
        if file_ext in ["pdf"]:
            asset_type = "pdf"
        elif file_ext in ["mp4", "avi", "mov", "webm"]:
            asset_type = "video"
        elif file_ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            asset_type = "image"
        elif file_ext in ["mp3", "wav", "ogg"]:
            asset_type = "audio"
        elif file_ext in ["html", "htm"]:
            asset_type = "interactive"
        elif file_ext in ["doc", "docx", "ppt", "pptx", "xls", "xlsx"]:
            asset_type = "document"
        elif file_ext in ["zip", "rar", "7z"]:
            asset_type = "zip"
        else:
            asset_type = "other"
    
    # 上传文件
    if asset_type == "pdf":
        upload_result = await upload_service.upload_pdf(file)
    else:
        upload_result = await upload_service.upload_file(file)
    
    # 验证学科ID（如果提供）
    if subject_id:
        from app.models import Subject
        subject = await db.get(Subject, subject_id)
        if not subject:
            raise HTTPException(status_code=400, detail="学科不存在")
    
    # 验证年级ID（如果提供）
    if grade_id:
        from app.models import Grade
        grade = await db.get(Grade, grade_id)
        if not grade:
            raise HTTPException(status_code=400, detail="年级不存在")
    
    # 创建资源库资产记录
    library_asset = LibraryAsset(
        school_id=school_id,
        owner_user_id=user_id,
        title=title,
        description=description,
        asset_type=asset_type,
        mime_type=file.content_type,
        size_bytes=upload_result.get("file_size"),
        storage_provider="local",
        storage_key=upload_result["file_url"],  # 存储相对路径
        public_url=upload_result["file_url"],
        thumbnail_url=upload_result.get("thumbnail_url"),
        page_count=upload_result.get("page_count"),
        visibility=visibility,
        status="active",
        subject_id=subject_id,
        grade_id=grade_id,
        knowledge_point_category=knowledge_point_category,
        knowledge_point_name=knowledge_point_name,
    )
    
    db.add(library_asset)
    await db.commit()
    await db.refresh(library_asset)
    
    return LibraryAssetUploadResponse(
        id=cast(int, library_asset.id),
        title=cast(str, library_asset.title),
        asset_type=cast(str, library_asset.asset_type),
        public_url=cast(Optional[str], library_asset.public_url),
        size_bytes=cast(Optional[int], library_asset.size_bytes),
        thumbnail_url=cast(Optional[str], library_asset.thumbnail_url),
    )


@router.patch("/{asset_id}", response_model=LibraryAssetDetail)
async def update_library_asset(
    asset_id: int,
    data: LibraryAssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新资源库资产信息"""
    _check_library_access(current_user)
    
    asset = await db.get(LibraryAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资源库资产不存在")
    
    # 校验归属学校
    asset_school_id = cast(int, asset.school_id)
    user_school_id = cast(int, current_user.school_id)
    if asset_school_id != user_school_id:
        raise HTTPException(status_code=403, detail="无权修改其他学校的资源")
    
    # 权限校验：教师只能修改自己上传的；管理员/教研员可修改全部
    user_role = cast(UserRole, current_user.role)
    user_id = cast(int, current_user.id)
    asset_owner_id = cast(int, asset.owner_user_id)
    
    if user_role == UserRole.TEACHER and asset_owner_id != user_id:
        raise HTTPException(status_code=403, detail="只能修改自己上传的资源")
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    await db.commit()
    await db.refresh(asset)
    
    return LibraryAssetDetail.model_validate(asset)


@router.delete("/{asset_id}")
async def delete_library_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除资源库资产（软删除）"""
    _check_library_access(current_user)
    
    asset = await db.get(LibraryAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资源库资产不存在")
    
    # 校验归属学校
    asset_school_id = cast(int, asset.school_id)
    user_school_id = cast(int, current_user.school_id)
    if asset_school_id != user_school_id:
        raise HTTPException(status_code=403, detail="无权删除其他学校的资源")
    
    # 权限校验：教师只能删除自己上传的；管理员/教研员可删除全部
    user_role = cast(UserRole, current_user.role)
    user_id = cast(int, current_user.id)
    asset_owner_id = cast(int, asset.owner_user_id)
    
    if user_role == UserRole.TEACHER and asset_owner_id != user_id:
        raise HTTPException(status_code=403, detail="只能删除自己上传的资源")
    
    # 检查是否被引用
    usage_query = select(func.count()).select_from(Resource).where(
        Resource.asset_id == asset_id
    )
    usage_result = await db.execute(usage_query)
    usage_count = usage_result.scalar() or 0
    
    if usage_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"无法删除：该资源正被 {usage_count} 个课程资源引用",
        )
    
    # 软删除
    setattr(asset, "status", "deleted")
    await db.commit()
    
    return {"message": "资源已删除", "asset_id": asset_id}


@router.post("/{asset_id}/increment-view")
async def increment_asset_view(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """增加资源库资产的点击次数"""
    _check_library_access(current_user)
    
    asset = await db.get(LibraryAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资源库资产不存在")
    
    # 校验归属学校
    asset_school_id = cast(int, asset.school_id)
    user_school_id = cast(int, current_user.school_id)
    if asset_school_id != user_school_id:
        raise HTTPException(status_code=403, detail="无权访问其他学校的资源")
    
    # 可见性校验：教师只能访问自己上传的或全校可见的
    user_role = cast(UserRole, current_user.role)
    user_id = cast(int, current_user.id)
    asset_owner_id = cast(int, asset.owner_user_id)
    asset_visibility = cast(str, asset.visibility)
    
    if user_role == UserRole.TEACHER:
        if asset_owner_id != user_id and asset_visibility != "school":
            raise HTTPException(status_code=403, detail="无权访问此资源")
    
    # 增加点击次数
    setattr(asset, "view_count", cast(int, asset.view_count) + 1)
    await db.commit()
    
    return {"message": "点击次数已更新", "view_count": asset.view_count}


@router.get("/{asset_id}/usages", response_model=LibraryAssetUsageResponse)
async def get_library_asset_usages(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源库资产的使用情况（被哪些课程资源引用）"""
    _check_library_access(current_user)
    
    asset = await db.get(LibraryAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资源库资产不存在")
    
    # 校验归属学校
    asset_school_id = cast(int, asset.school_id)
    user_school_id = cast(int, current_user.school_id)
    if asset_school_id != user_school_id:
        raise HTTPException(status_code=403, detail="无权访问其他学校的资源")
    
    # 查询引用此资产的所有 Resource
    query = (
        select(Resource, Chapter, Course)
        .join(Chapter, Resource.chapter_id == Chapter.id)
        .join(Course, Chapter.course_id == Course.id)
        .where(Resource.asset_id == asset_id)
        .order_by(Resource.updated_at.desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    usages = []
    for resource, chapter, course in rows:
        usages.append(
            LibraryAssetUsage(
                resource_id=cast(int, resource.id),
                resource_title=cast(str, resource.title),
                chapter_id=cast(int, chapter.id),
                chapter_name=cast(str, chapter.name),
                course_id=cast(int, course.id),
                course_name=cast(str, course.name),
            )
        )
    
    return LibraryAssetUsageResponse(
        asset_id=asset_id,
        asset_title=cast(str, asset.title),
        usages=usages,
        total_usages=len(usages),
    )


@router.get("/{asset_id}/content")
async def get_library_asset_content(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源库资产的文件内容（用于编辑HTML等文本文件）"""
    _check_library_access(current_user)
    
    asset = await db.get(LibraryAsset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资源库资产不存在")
    
    # 校验归属学校
    asset_school_id = cast(int, asset.school_id)
    user_school_id = cast(int, current_user.school_id)
    if asset_school_id != user_school_id:
        raise HTTPException(status_code=403, detail="无权访问其他学校的资源")
    
    # 权限校验：教师只能访问自己上传的；管理员/教研员可访问全部
    user_role = cast(UserRole, current_user.role)
    user_id = cast(int, current_user.id)
    asset_owner_id = cast(int, asset.owner_user_id)
    
    if user_role == UserRole.TEACHER and asset_owner_id != user_id:
        raise HTTPException(status_code=403, detail="只能访问自己上传的资源")
    
    # 只允许获取文本类型的文件内容（HTML、文本等）
    asset_type = cast(str, asset.asset_type)
    mime_type = cast(Optional[str], asset.mime_type)
    
    if asset_type not in ["interactive", "document"] and mime_type not in ["text/html", "text/plain"]:
        raise HTTPException(status_code=400, detail="此资源类型不支持获取文件内容")
    
    # 获取文件路径
    storage_key = cast(str, asset.storage_key)
    if not storage_key:
        raise HTTPException(status_code=404, detail="资源文件不存在")
    
    # 构建完整文件路径
    import os
    import aiofiles
    from app.core.config import settings
    
    # storage_key 通常是相对路径，如 /uploads/resources/xxx.html
    # 根据upload_service的实现，文件实际存储在 storage/resources/ 目录下
    # 但storage_key返回的是 /uploads/resources/xxx.html
    # 需要转换为: storage/resources/xxx.html
    if storage_key.startswith("/uploads/"):
        # 去掉 /uploads/ 前缀，得到 resources/xxx.html
        relative_path = storage_key.replace("/uploads/", "", 1)
        # 构建完整路径: storage/resources/xxx.html
        file_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    else:
        # 如果storage_key是绝对路径或其他格式，直接使用
        file_path = storage_key
    
    # 安全检查：确保文件路径在允许的目录内
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    file_abspath = os.path.abspath(file_path)
    
    if not file_abspath.startswith(upload_dir):
        raise HTTPException(status_code=403, detail="文件路径不安全")
    
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 读取文件内容
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
        return {"content": content}
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        try:
            async with aiofiles.open(file_path, "r", encoding="gbk") as f:
                content = await f.read()
            return {"content": content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")