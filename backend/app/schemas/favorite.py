"""
收藏相关的Pydantic Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    """创建收藏"""
    lesson_id: int


class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: int
    user_id: int
    lesson_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FavoriteWithLesson(FavoriteResponse):
    """带课程信息的收藏"""
    lesson_title: str
    lesson_description: Optional[str]
    lesson_cover_image: Optional[str]
    lesson_difficulty: Optional[str]
    lesson_rating: float

