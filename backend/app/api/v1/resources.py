"""
资源管理 API
"""

from typing import List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from fastapi import Request

from app.core.database import get_db
from app.models import Resource, Chapter, Lesson, User, UserRole, LibraryAsset
from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceDetail,
    ResourceListResponse,
)
from app.schemas.library_asset import LibraryAssetSummary
from app.services.upload import upload_service
from app.services.office_converter import office_converter_service
from app.api.deps import get_current_user, get_current_admin
from app.utils.resource_url import filename_to_url, url_to_filename

router = APIRouter()


async def _enrich_resource_response(
    resource: Resource, db: AsyncSession, request: Optional[Request] = None
) -> ResourceResponse:
    """
    为资源响应补充 asset 和 resolved_file_url 字段
    并将文件名转换为完整URL
    """
    resource_dict = {
        "id": resource.id,
        "chapter_id": resource.chapter_id,
        "title": resource.title,
        "description": resource.description,
        "resource_type": resource.resource_type,
        "is_official": resource.is_official,
        "is_downloadable": resource.is_downloadable,
        "display_order": resource.display_order,
        "asset_id": resource.asset_id,
        "file_url": resource.file_url,
        "file_size": resource.file_size,
        "page_count": resource.page_count,
        "thumbnail_url": resource.thumbnail_url,
        "is_active": resource.is_active,
        "view_count": resource.view_count,
        "download_count": resource.download_count,
        "created_by": resource.created_by,
        "created_at": resource.created_at,
        "updated_at": resource.updated_at,
    }
    
    # 如果有 asset_id，加载 asset 信息
    asset_summary = None
    asset_id_value = cast(Optional[int], resource.asset_id)
    if asset_id_value:
        asset = await db.get(LibraryAsset, asset_id_value)
        if asset:
            asset_summary = LibraryAssetSummary.model_validate(asset)
            # 转换asset中的URL
            if asset_summary and asset_summary.public_url:
                asset_summary.public_url = filename_to_url(asset_summary.public_url, request)
            if asset_summary and asset_summary.thumbnail_url:
                asset_summary.thumbnail_url = filename_to_url(asset_summary.thumbnail_url, request)
    
    resource_dict["asset"] = asset_summary
    
    # 转换URL：将文件名转换为完整URL
    file_url_value = cast(Optional[str], resource_dict["file_url"])
    if file_url_value:
        resource_dict["file_url"] = filename_to_url(file_url_value, request)
    thumbnail_url_value = cast(Optional[str], resource_dict["thumbnail_url"])
    if thumbnail_url_value:
        resource_dict["thumbnail_url"] = filename_to_url(thumbnail_url_value, request)
    
    # 计算 resolved_file_url（优先使用 file_url，否则使用 asset.public_url）
    resolved_file_url = cast(Optional[str], resource.file_url)
    if not resolved_file_url and asset_summary:
        resolved_file_url = asset_summary.public_url
    
    # 转换resolved_file_url
    if resolved_file_url:
        resolved_file_url = filename_to_url(resolved_file_url, request)
    
    resource_dict["resolved_file_url"] = resolved_file_url
    
    return ResourceResponse(**resource_dict)



@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    request: Request,
    chapter_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    is_official: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源列表（支持按章节筛选）"""

    query = select(Resource).order_by(Resource.display_order, Resource.created_at.desc())

    # 按章节筛选
    if chapter_id is not None:
        query = query.where(Resource.chapter_id == chapter_id)

    # 按类型筛选
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)

    # 按是否官方筛选
    if is_official is not None:
        query = query.where(Resource.is_official == is_official)

    result = await db.execute(query)
    resources = result.scalars().all()

    # 补充 asset 和 resolved_file_url
    enriched_resources = []
    for resource in resources:
        enriched = await _enrich_resource_response(resource, db, request)
        enriched_resources.append(enriched)
    
    return enriched_resources


@router.get("/{resource_id}", response_model=ResourceDetail)
async def get_resource(
    resource_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源详情"""

    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")

    # 增加查看次数
    current_view_count = resource.view_count or 0
    setattr(resource, "view_count", current_view_count + 1)
    await db.commit()

    # 获取章节信息
    chapter = await db.get(Chapter, resource.chapter_id)

    # 统计基于此资源的教案数量
    lessons_count_query = (
        select(func.count()).select_from(Lesson).where(Lesson.reference_resource_id == resource_id)
    )
    lessons_count_result = await db.execute(lessons_count_query)
    lessons_count = lessons_count_result.scalar()

    # 先获取基础响应（包含 asset 和 resolved_file_url）
    base_response = await _enrich_resource_response(resource, db, request)
    
    # 构建详情响应
    resource_dict = base_response.model_dump()
    resource_dict["chapter"] = (
        {"id": chapter.id, "name": chapter.name, "course_id": chapter.course_id}
        if chapter
        else None
    )
    resource_dict["lessons_count"] = lessons_count

    return ResourceDetail(**resource_dict)


@router.post("/", response_model=ResourceResponse)
async def create_resource(
    request: Request,
    chapter_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    resource_type: str = Form("pdf"),
    is_official: bool = Form(False),
    is_downloadable: bool = Form(True),
    asset_id: Optional[int] = Form(None, description="资源库资产ID（与file二选一）"),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建资源（管理员或教研员）"""
    # 权限：管理员或教研员可创建资源
    if current_user.role not in [UserRole.ADMIN, UserRole.RESEARCHER]:
        raise HTTPException(403, "需要管理员或教研员权限")

    # 验证章节是否存在
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")

    # asset_id 和 file 不能同时为空（至少提供一个）
    if not asset_id and not file:
        raise HTTPException(400, "必须提供 asset_id 或上传文件")
    
    # asset_id 和 file 不能同时存在（二选一）
    if asset_id and file:
        raise HTTPException(400, "asset_id 和文件上传只能选择其一")

    # 创建资源记录
    role_value = cast(str, current_user.role)
    resource_is_official = is_official if role_value == UserRole.ADMIN else False

    resource = Resource(
        chapter_id=chapter_id,
        title=title,
        description=description,
        resource_type=resource_type,
        # 教研员上传的资源不标记为官方
        is_official=resource_is_official,
        is_downloadable=is_downloadable,
        created_by=current_user.id,
    )

    # 如果引用资源库资产
    if asset_id:
        # 验证资产是否存在
        asset = await db.get(LibraryAsset, asset_id)
        if not asset:
            raise HTTPException(404, "资源库资产不存在")
        
        # 验证资产状态
        if cast(str, asset.status) != "active":
            raise HTTPException(400, "资源库资产状态无效")
        
        # 验证资产归属学校（确保同校）
        user_school_id = cast(Optional[int], current_user.school_id)
        asset_school_id = cast(Optional[int], asset.school_id)
        if user_school_id and asset_school_id and user_school_id != asset_school_id:
            raise HTTPException(403, "无权引用其他学校的资源库资产")
        
        # 验证可见性（教师只能引用自己上传的或全校可见的）
        user_role = cast(UserRole, current_user.role)
        if user_role == UserRole.TEACHER:
            asset_owner_id = cast(int, asset.owner_user_id)
            asset_visibility = cast(str, asset.visibility)
            if asset_owner_id != current_user.id and asset_visibility != "school":
                raise HTTPException(403, "无权引用此资源库资产")
        
        # 设置引用
        setattr(resource, "asset_id", asset_id)
        # 从资产继承资源类型（如果未指定）
        if not resource_type or resource_type == "pdf":
            asset_type_value = cast(str, asset.asset_type)
            setattr(resource, "resource_type", asset_type_value)
    
    # 如果有文件上传
    elif file:
        if resource_type == "pdf":
            # 上传 PDF 并提取元数据（upload_service现在返回文件名）
            upload_result = await upload_service.upload_pdf(file)
            # 确保保存的是文件名（而不是路径）
            file_url_value = url_to_filename(upload_result["file_url"])
            setattr(resource, "file_url", file_url_value)
            setattr(resource, "file_size", upload_result["file_size"])
            setattr(resource, "page_count", upload_result["page_count"])
            thumbnail_url = cast(Optional[str], upload_result.get("thumbnail_url"))
            if thumbnail_url:
                # 确保保存的是文件名
                setattr(resource, "thumbnail_url", url_to_filename(thumbnail_url))
        else:
            # 上传其他类型文件（upload_service现在返回文件名）
            upload_result = await upload_service.upload_file(file)
            # 确保保存的是文件名（而不是路径）
            file_url_value = url_to_filename(upload_result["file_url"])
            setattr(resource, "file_url", file_url_value)
            setattr(resource, "file_size", upload_result["file_size"])

    db.add(resource)
    await db.commit()
    await db.refresh(resource)

    # 返回时补充 asset 和 resolved_file_url（转换为完整URL）
    return await _enrich_resource_response(resource, db, request)


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    request: Request,
    data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """更新资源（管理员）"""

    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # 如果更新的是URL字段，确保保存的是文件名
        if field in ("file_url", "thumbnail_url") and value:
            value = url_to_filename(value)
        setattr(resource, field, value)

    await db.commit()
    await db.refresh(resource)

    # 返回时转换为完整URL
    return await _enrich_resource_response(resource, db, request)


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除资源（管理员或教研员可删除自己创建的资源）"""

    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")

    # 权限检查：管理员可以删除任何资源，教研员只能删除自己创建的资源
    role_value = cast(str, current_user.role)
    is_admin = role_value == UserRole.ADMIN.value
    is_researcher = role_value == UserRole.RESEARCHER.value
    
    if not is_admin:
        if not is_researcher:
            raise HTTPException(403, "需要管理员或教研员权限")
        
        # 教研员只能删除自己创建的资源
        resource_creator_id = cast(Optional[int], getattr(resource, "created_by", None))
        current_user_id = cast(int, current_user.id)
        if resource_creator_id != current_user_id:
            raise HTTPException(403, "只能删除自己创建的资源")

    # 检查是否有教案引用此资源
    lessons_query = (
        select(func.count()).select_from(Lesson).where(Lesson.reference_resource_id == resource_id)
    )
    lessons_count_result = await db.execute(lessons_query)
    lessons_count = lessons_count_result.scalar()

    lessons_count = lessons_count or 0
    if lessons_count > 0:
        raise HTTPException(
            400, f"Cannot delete resource: {lessons_count} lesson(s) are referencing it"
        )

    # 删除文件
    file_url = cast(Optional[str], resource.file_url)
    if file_url:
        await upload_service.delete_file(file_url)

    # 删除资源记录
    await db.delete(resource)
    await db.commit()

    return {"message": "Resource deleted successfully"}


@router.post("/{resource_id}/download")
async def download_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下载资源（增加下载计数）"""

    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")

    if not (cast(bool, resource.is_downloadable)):
        raise HTTPException(403, "Resource is not downloadable")

    # 增加下载次数
    current_download_count = resource.download_count or 0
    setattr(resource, "download_count", current_download_count + 1)
    await db.commit()

    # 从 file_url 中提取文件扩展名
    def get_file_extension(url: str) -> str:
        if not url:
            return ""
        path = url.split("/")[-1]  # 获取文件名部分
        last_dot_index = path.rfind(".")
        return path[last_dot_index:] if last_dot_index > 0 else ""

    # 构建完整的文件名（标题 + 扩展名）
    extension = get_file_extension(cast(str, resource.file_url))
    full_filename = f"{resource.title}{extension}" if extension else resource.title

    return {"download_url": resource.file_url, "filename": full_filename}


@router.get("/{resource_id}/preview")
async def get_resource_preview(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取资源预览信息，包括Office文档的PDF转换版本"""

    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")

    # 检查文件类型
    file_ext = (
        cast(str, resource.file_url).split(".")[-1].lower() if cast(Optional[str], resource.file_url) else ""
    )

    preview_info = {
        "resource_id": resource.id,
        "title": resource.title,
        "file_url": resource.file_url,
        "file_type": file_ext,
        "file_size": resource.file_size,
        "page_count": resource.page_count,
        "can_preview_directly": file_ext in ["pdf", "jpg", "jpeg", "png", "gif", "webp", "svg"],
        "preview_url": resource.file_url,
        "converted_to_pdf": False,
        "conversion_error": None,
    }

    # 如果是Office文档，尝试获取转换后的PDF
    if file_ext in ["docx", "doc", "pptx", "ppt"]:
        try:
            converted_pdf_url = await office_converter_service.get_converted_pdf_url(
                cast(str, resource.file_url)
            )
            if converted_pdf_url:
                preview_info["preview_url"] = converted_pdf_url
                preview_info["converted_to_pdf"] = True
                preview_info["conversion_method"] = "auto_conversion"
            else:
                preview_info["converted_to_pdf"] = False
                preview_info["conversion_error"] = "无法转换文档为PDF格式，请使用其他预览方式"
        except Exception as e:
            preview_info["converted_to_pdf"] = False
            preview_info["conversion_error"] = f"转换过程中出现错误: {str(e)}"

    return preview_info
