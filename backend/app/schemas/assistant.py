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


class CourseDesignContext(BaseModel):
    """课程设计 Wiki 教学包快照上下文（受限长度）"""

    snapshot_id: str = Field(..., min_length=1, max_length=120)
    snapshot_version: str = Field(..., min_length=1, max_length=40)
    teaching_context: str = Field(..., min_length=2, max_length=12000)


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
    agent_prompt: Optional[str] = Field(
        None, description="自定义智能体的提示词，用于定义AI的角色和行为"
    )
    course_design_context: Optional[CourseDesignContext] = Field(
        None, description="课程设计 Skill 的 Wiki 教学包快照上下文"
    )


class AssistantRequest(BaseModel):
    """助手请求体"""

    question: str = Field(..., min_length=3, max_length=400)
    topic: Optional[str] = Field(
        None,
        description="助手主题，例如 pdca、lesson_plan、qa、study_support、course_design",
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

