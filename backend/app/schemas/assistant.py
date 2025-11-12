"""
通用 AI 助手请求/响应 Schema
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.question import QuestionStats
from app.schemas.subject_group import SubjectGroupStatistics


class AssistantLessonSnapshot(BaseModel):
    """近期教案/课程快照"""

    id: int
    title: str
    status: Optional[str] = None
    updated_at: Optional[datetime] = None


class AssistantContext(BaseModel):
    """助手参考的上下文"""

    lesson_summary: Optional[Dict[str, int]] = None
    question_stats: Optional[QuestionStats] = None
    subject_group_stats: Optional[SubjectGroupStatistics] = None
    recent_lessons: Optional[List[AssistantLessonSnapshot]] = None
    lesson_outline: Optional[str] = Field(
        None, description="课程/教案结构概览，用于辅助生成建议"
    )
    progress: Optional[int] = Field(
        None, ge=0, le=100, description="学习进度（学生端使用）"
    )


class AssistantRequest(BaseModel):
    """助手请求体"""

    question: str = Field(..., min_length=3, max_length=400)
    topic: Optional[str] = Field(
        None,
        description="助手主题，例如 pdca、lesson_plan、qa、study_support",
    )
    lesson_id: Optional[int] = Field(
        None, ge=1, description="关联的课程/教案 ID（可选）"
    )
    context: Optional[AssistantContext] = None


class AssistantInsight(BaseModel):
    """结构化洞察"""

    title: str
    detail: str
    metric: Optional[str] = None


class AssistantAction(BaseModel):
    """行动建议"""

    label: str
    description: Optional[str] = None


class AssistantResponse(BaseModel):
    """助手响应"""

    answer: str
    insights: List[AssistantInsight] = Field(default_factory=list)
    suggested_actions: List[AssistantAction] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    model_used: Optional[str] = None
    confidence: Optional[float] = None
    response_time_ms: Optional[float] = None
    context_used: List[str] = Field(default_factory=list)

