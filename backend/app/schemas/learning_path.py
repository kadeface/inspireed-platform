"""
学习路径相关的Pydantic Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class LearningPathLessonCreate(BaseModel):
    """添加课程到学习路径"""
    lesson_id: int
    order_index: int
    is_required: bool = True


class LearningPathLessonResponse(BaseModel):
    """学习路径课程响应"""
    id: int
    learning_path_id: int
    lesson_id: int
    order_index: int
    is_required: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathLessonWithDetails(LearningPathLessonResponse):
    """带课程详情的学习路径课程"""
    lesson_title: str
    lesson_description: Optional[str]
    lesson_cover_image: Optional[str]
    lesson_difficulty: Optional[str]
    lesson_rating: float
    lesson_duration: Optional[int]


class LearningPathCreate(BaseModel):
    """创建学习路径"""
    title: str
    description: Optional[str] = None
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    cover_image_url: Optional[str] = None
    estimated_hours: Optional[int] = None
    lessons: List[LearningPathLessonCreate] = []


class LearningPathUpdate(BaseModel):
    """更新学习路径"""
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    cover_image_url: Optional[str] = None
    estimated_hours: Optional[int] = None
    is_published: Optional[bool] = None


class LearningPathResponse(BaseModel):
    """学习路径响应"""
    id: int
    title: str
    description: Optional[str]
    creator_id: int
    difficulty_level: str
    cover_image_url: Optional[str]
    is_published: bool
    estimated_hours: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathWithLessons(LearningPathResponse):
    """带课程列表的学习路径"""
    lessons: List[LearningPathLessonWithDetails]
    lesson_count: int
    creator_name: str


class LearningPathListItem(LearningPathResponse):
    """学习路径列表项"""
    lesson_count: int
    creator_name: str

