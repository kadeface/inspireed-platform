"""
教案Schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.lesson import LessonStatus
from app.schemas.curriculum import CourseResponse


class LessonBase(BaseModel):
    """教案基础Schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class LessonCreate(LessonBase):
    """教案创建Schema"""
    course_id: int = Field(..., description="所属课程ID")
    content: List[dict] = Field(default_factory=list)
    national_resource_id: Optional[str] = None


class LessonUpdate(BaseModel):
    """教案更新Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    course_id: Optional[int] = Field(None, description="所属课程ID")
    content: Optional[List[dict]] = None
    tags: Optional[List[str]] = None
    status: Optional[LessonStatus] = None


class LessonResponse(LessonBase):
    """教案响应Schema"""
    id: int
    creator_id: int
    course_id: int
    status: LessonStatus
    content: List[dict]
    version: int
    parent_id: Optional[int] = None
    national_resource_id: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    # 嵌套课程信息
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """教案列表响应"""
    items: List[LessonResponse]
    total: int
    page: int
    page_size: int

