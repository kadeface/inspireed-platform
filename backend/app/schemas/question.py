"""
问答系统Schema定义
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from app.models.question import QuestionStatus, AskType, AnswererType


# ==================== Question Schemas ====================

class QuestionBase(BaseModel):
    """问题基础Schema"""
    title: str = Field(..., max_length=200, description="问题标题")
    content: str = Field(..., description="问题详情")
    lesson_id: int = Field(..., description="所属课程ID")
    cell_id: Optional[int] = Field(None, description="关联的Cell ID（可选）")
    ask_type: AskType = Field(AskType.TEACHER, description="提问类型")
    is_public: bool = Field(True, description="是否公开")


class QuestionCreate(QuestionBase):
    """创建问题Schema"""
    pass


class QuestionUpdate(BaseModel):
    """更新问题Schema"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    status: Optional[QuestionStatus] = None
    is_public: Optional[bool] = None
    is_pinned: Optional[bool] = None


class QuestionInDBBase(QuestionBase):
    """数据库中的问题基础Schema"""
    id: int
    student_id: int
    status: QuestionStatus
    is_pinned: bool
    views: int
    upvotes: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 简化的用户信息
class UserBrief(BaseModel):
    """用户简要信息"""
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# 简化的课程信息
class LessonBrief(BaseModel):
    """课程简要信息"""
    id: int
    title: str
    
    class Config:
        from_attributes = True


# 简化的Cell信息
class CellBrief(BaseModel):
    """Cell简要信息"""
    id: int
    cell_type: str
    order: int
    
    class Config:
        from_attributes = True


class QuestionListItem(QuestionInDBBase):
    """问题列表项Schema（带统计信息）"""
    student: UserBrief
    lesson: LessonBrief
    cell: Optional[CellBrief] = None
    answer_count: int = 0
    has_ai_answer: bool = False
    has_teacher_answer: bool = False


class QuestionResponse(QuestionInDBBase):
    """问题响应Schema（带关联信息）"""
    student: UserBrief
    lesson: LessonBrief
    cell: Optional[CellBrief] = None
    answers: List["AnswerResponse"] = []


# ==================== Answer Schemas ====================

class AnswerBase(BaseModel):
    """回答基础Schema"""
    question_id: int = Field(..., description="问题ID")
    content: List[dict] = Field(..., description="回答内容（Cell数组）")


class AnswerCreate(AnswerBase):
    """创建回答Schema"""
    pass


class AnswerUpdate(BaseModel):
    """更新回答Schema"""
    content: Optional[List[dict]] = None
    is_accepted: Optional[bool] = None


class AnswerInDBBase(AnswerBase):
    """数据库中的回答基础Schema"""
    id: int
    answerer_type: AnswererType
    answerer_id: Optional[int]
    ai_model: Optional[str]
    ai_prompt_tokens: Optional[int]
    ai_completion_tokens: Optional[int]
    rating: Optional[int]
    is_accepted: bool
    upvotes: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AnswerResponse(AnswerInDBBase):
    """回答响应Schema（带回答者信息）"""
    answerer: Optional[UserBrief] = None


# ==================== Vote Schemas ====================

class VoteCreate(BaseModel):
    """创建点赞Schema"""
    question_id: Optional[int] = None
    answer_id: Optional[int] = None


# ==================== Rating Schemas ====================

class RatingCreate(BaseModel):
    """评分Schema"""
    rating: int = Field(..., ge=1, le=5, description="评分1-5星")


# ==================== List Response Schemas ====================

class QuestionListResponse(BaseModel):
    """问题列表响应Schema"""
    items: List[QuestionListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


# ==================== Statistics Schemas ====================

class QuestionStats(BaseModel):
    """问题统计Schema"""
    total: int = 0
    pending: int = 0
    answered: int = 0
    resolved: int = 0
    closed: int = 0


# 解决前向引用
QuestionResponse.model_rebuild()

