"""
资源管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models import Resource, Chapter, Lesson, User, UserRole
from app.schemas.resource import (
    ResourceCreate, ResourceUpdate, ResourceResponse, 
    ResourceDetail, ResourceListResponse
)
from app.services.upload import upload_service
from app.api.deps import get_current_user, get_current_admin

router = APIRouter()


@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    chapter_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    is_official: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    
    return resources


@router.get("/{resource_id}", response_model=ResourceDetail)
async def get_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资源详情"""
    
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    
    # 增加查看次数
    resource.view_count += 1
    await db.commit()
    
    # 获取章节信息
    chapter = await db.get(Chapter, resource.chapter_id)
    
    # 统计基于此资源的教案数量
    lessons_count_query = select(func.count()).select_from(Lesson).where(
        Lesson.reference_resource_id == resource_id
    )
    lessons_count_result = await db.execute(lessons_count_query)
    lessons_count = lessons_count_result.scalar()
    
    # 构建响应
    resource_dict = {
        **resource.__dict__,
        'chapter': {
            'id': chapter.id,
            'name': chapter.name,
            'course_id': chapter.course_id
        } if chapter else None,
        'lessons_count': lessons_count
    }
    
    return ResourceDetail(**resource_dict)


@router.post("/", response_model=ResourceResponse)
async def create_resource(
    chapter_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    resource_type: str = Form("pdf"),
    is_official: bool = Form(False),
    is_downloadable: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建资源（管理员）"""
    
    # 验证章节是否存在
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    
    # 创建资源记录
    resource = Resource(
        chapter_id=chapter_id,
        title=title,
        description=description,
        resource_type=resource_type,
        is_official=is_official,
        is_downloadable=is_downloadable,
        created_by=current_user.id
    )
    
    # 如果有文件上传
    if file:
        if resource_type == 'pdf':
            # 上传 PDF 并提取元数据
            upload_result = await upload_service.upload_pdf(file)
            resource.file_url = upload_result['file_url']
            resource.file_size = upload_result['file_size']
            resource.page_count = upload_result['page_count']
            resource.thumbnail_url = upload_result.get('thumbnail_url')
        else:
            # 上传其他类型文件
            upload_result = await upload_service.upload_file(file)
            resource.file_url = upload_result['file_url']
            resource.file_size = upload_result['file_size']
    
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新资源（管理员）"""
    
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    await db.commit()
    await db.refresh(resource)
    
    return resource


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """删除资源（管理员）"""
    
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    
    # 检查是否有教案引用此资源
    lessons_query = select(func.count()).select_from(Lesson).where(
        Lesson.reference_resource_id == resource_id
    )
    lessons_count_result = await db.execute(lessons_query)
    lessons_count = lessons_count_result.scalar()
    
    if lessons_count > 0:
        raise HTTPException(
            400, 
            f"Cannot delete resource: {lessons_count} lesson(s) are referencing it"
        )
    
    # 删除文件
    if resource.file_url:
        await upload_service.delete_file(resource.file_url)
    
    # 删除资源记录
    await db.delete(resource)
    await db.commit()
    
    return {"message": "Resource deleted successfully"}


@router.post("/{resource_id}/download")
async def download_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载资源（增加下载计数）"""
    
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    
    if not resource.is_downloadable:
        raise HTTPException(403, "Resource is not downloadable")
    
    # 增加下载次数
    resource.download_count += 1
    await db.commit()
    
    # 从 file_url 中提取文件扩展名
    def get_file_extension(url: str) -> str:
        if not url:
            return ""
        path = url.split('/')[-1]  # 获取文件名部分
        last_dot_index = path.rfind('.')
        return path[last_dot_index:] if last_dot_index > 0 else ""
    
    # 构建完整的文件名（标题 + 扩展名）
    extension = get_file_extension(resource.file_url)
    full_filename = f"{resource.title}{extension}" if extension else resource.title
    
    return {
        "download_url": resource.file_url,
        "filename": full_filename
    }

