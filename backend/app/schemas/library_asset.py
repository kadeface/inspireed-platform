"""
资源库资产相关的 Schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LibraryAssetBase(BaseModel):
    """资源库资产基础 Schema"""

    title: str = Field(..., max_length=200, description="资源标题")
    description: Optional[str] = Field(None, description="资源描述")
    asset_type: str = Field(
        ...,
        max_length=20,
        description="资源类型：pdf/video/image/audio/document/link/zip/interactive/other",
    )
    visibility: str = Field(
        default="teacher_only",
        description="可见性：teacher_only（仅上传者）/school（全校可见）",
    )
    subject_id: Optional[int] = Field(None, description="学科ID（可选）")
    grade_id: Optional[int] = Field(None, description="年级ID（可选，NULL表示跨年级通用）")
    knowledge_point_category: Optional[str] = Field(
        None, max_length=100, description="知识点分类（如：计算类/速算技巧、几何类/图形认知）"
    )
    knowledge_point_name: Optional[str] = Field(
        None, max_length=200, description="具体知识点名称（如：乘法口诀可视化）"
    )


class LibraryAssetCreate(BaseModel):
    """创建资源库资产 Schema（用于表单提交，文件另通过 multipart 上传）"""

    title: str = Field(..., max_length=200, description="资源标题")
    description: Optional[str] = Field(None, description="资源描述")
    asset_type: Optional[str] = Field(
        None,
        max_length=20,
        description="资源类型（可选，后端可从文件自动推断）",
    )
    visibility: str = Field(
        default="teacher_only",
        description="可见性：teacher_only/school",
    )
    subject_id: Optional[int] = Field(None, description="学科ID（可选）")
    grade_id: Optional[int] = Field(None, description="年级ID（可选）")
    knowledge_point_category: Optional[str] = Field(
        None, max_length=100, description="知识点分类（如：计算类/速算技巧、几何类/图形认知）"
    )
    knowledge_point_name: Optional[str] = Field(
        None, max_length=200, description="具体知识点名称（如：乘法口诀可视化）"
    )


class LibraryAssetUpdate(BaseModel):
    """更新资源库资产 Schema"""

    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    visibility: Optional[str] = None
    status: Optional[str] = None
    subject_id: Optional[int] = None
    grade_id: Optional[int] = None
    knowledge_point_category: Optional[str] = None
    knowledge_point_name: Optional[str] = None


class LibraryAssetSummary(BaseModel):
    """资源库资产摘要 Schema（用于列表、选择器等场景）"""

    id: int
    title: str
    asset_type: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    thumbnail_url: Optional[str] = None
    public_url: Optional[str] = None
    page_count: Optional[int] = None
    duration_seconds: Optional[int] = None
    visibility: str
    status: str
    subject_id: Optional[int] = None
    grade_id: Optional[int] = None
    knowledge_point_category: Optional[str] = None
    knowledge_point_name: Optional[str] = None
    view_count: int = 0
    version: int = 1
    updated_at: datetime

    class Config:
        from_attributes = True


class LibraryAssetDetail(BaseModel):
    """资源库资产详情 Schema"""

    id: int
    school_id: int
    owner_user_id: int
    title: str
    description: Optional[str] = None
    asset_type: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_provider: str
    storage_key: str
    public_url: Optional[str] = None
    sha256: Optional[str] = None
    thumbnail_url: Optional[str] = None
    page_count: Optional[int] = None
    duration_seconds: Optional[int] = None
    visibility: str
    status: str
    subject_id: Optional[int] = None
    grade_id: Optional[int] = None
    knowledge_point_category: Optional[str] = None
    knowledge_point_name: Optional[str] = None
    view_count: int = 0
    version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LibraryAssetListResponse(BaseModel):
    """资源库资产列表响应"""

    items: List[LibraryAssetSummary]
    total: int
    page: int
    page_size: int


class LibraryAssetUploadResponse(BaseModel):
    """资源库资产上传响应"""

    id: int
    title: str
    asset_type: str
    public_url: Optional[str] = None
    size_bytes: Optional[int] = None
    thumbnail_url: Optional[str] = None


class LibraryAssetUsage(BaseModel):
    """资源库资产使用情况（被哪些课程资源引用）"""

    resource_id: int
    resource_title: str
    chapter_id: int
    chapter_name: str
    course_id: int
    course_name: str


class LibraryAssetUsageResponse(BaseModel):
    """资源库资产使用情况响应"""

    asset_id: int
    asset_title: str
    usages: List[LibraryAssetUsage]
    total_usages: int


class LibraryAssetVersionDetail(BaseModel):
    """资源库资产版本详情 Schema"""

    id: int
    asset_id: int
    version: int
    storage_key: str
    public_url: Optional[str] = None
    size_bytes: Optional[int] = None
    sha256: Optional[str] = None
    created_by: int
    change_note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LibraryAssetVersionListResponse(BaseModel):
    """资源库资产版本列表响应"""

    asset_id: int
    current_version: int
    versions: List[LibraryAssetVersionDetail]
    total: int


class LibraryAssetCreateVersionRequest(BaseModel):
    """创建新版本请求 Schema"""

    change_note: Optional[str] = Field(None, description="版本变更说明")
