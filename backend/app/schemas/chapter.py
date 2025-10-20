"""
章节相关的 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChapterBase(BaseModel):
    """章节基础 Schema"""
    name: str = Field(..., max_length=200, description="章节名称")
    code: Optional[str] = Field(None, max_length=50, description="章节编码")
    description: Optional[str] = Field(None, description="章节描述")
    display_order: int = Field(default=0, description="显示顺序")


class ChapterCreate(ChapterBase):
    """创建章节 Schema"""
    course_id: int = Field(..., description="所属课程ID")
    parent_id: Optional[int] = Field(None, description="父章节ID（用于多级章节）")


class ChapterUpdate(BaseModel):
    """更新章节 Schema"""
    name: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ChapterResponse(ChapterBase):
    """章节响应 Schema"""
    id: int
    course_id: int
    parent_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChapterWithChildren(ChapterResponse):
    """包含子章节的章节响应"""
    children: List['ChapterWithChildren'] = []
    resources_count: int = Field(default=0, description="资源数量")


class ChapterListResponse(BaseModel):
    """章节列表响应"""
    items: List[ChapterResponse]
    total: int

