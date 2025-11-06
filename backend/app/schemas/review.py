"""
评分评论相关的Pydantic Schema
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, validator


class ReviewCreate(BaseModel):
    """创建评论"""

    lesson_id: int
    rating: int = Field(..., ge=1, le=5, description="评分1-5")
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    """更新评论"""

    rating: int = Field(..., ge=1, le=5, description="评分1-5")
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """评论响应"""

    id: int
    user_id: int
    lesson_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """带用户信息的评论"""

    user_name: str
    user_avatar: Optional[str]


class LessonRatingStats(BaseModel):
    """课程评分统计"""

    lesson_id: int
    average_rating: float
    review_count: int
    rating_distribution: Dict[int, int]  # {1: 10, 2: 20, 3: 30, 4: 40, 5: 50}
