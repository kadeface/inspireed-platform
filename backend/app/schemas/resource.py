"""
资源相关的 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ResourceBase(BaseModel):
    """资源基础 Schema"""
    title: str = Field(..., max_length=200, description="资源标题")
    description: Optional[str] = Field(None, description="资源描述")
    resource_type: str = Field(..., max_length=20, description="资源类型：pdf/video/document/link")
    is_official: bool = Field(default=False, description="是否官方资源")
    is_downloadable: bool = Field(default=True, description="是否允许下载")
    display_order: int = Field(default=0, description="显示顺序")


class ResourceCreate(ResourceBase):
    """创建资源 Schema"""
    chapter_id: int = Field(..., description="所属章节ID")


class ResourceUpdate(BaseModel):
    """更新资源 Schema"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_official: Optional[bool] = None
    is_downloadable: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class ResourceResponse(ResourceBase):
    """资源响应 Schema"""
    id: int
    chapter_id: int
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    view_count: int
    download_count: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResourceDetail(ResourceResponse):
    """资源详情 Schema（包含关联信息）"""
    chapter: Optional[dict] = None  # 章节信息
    lessons_count: int = Field(default=0, description="基于此资源创建的教案数量")


class ResourceListResponse(BaseModel):
    """资源列表响应"""
    items: List[ResourceResponse]
    total: int
    page: int
    page_size: int

