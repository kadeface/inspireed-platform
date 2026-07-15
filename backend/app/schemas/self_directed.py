"""
学生自主学习 Schema
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class SelfDirectedCreateRequest(BaseModel):
    goal_text: str = Field(..., min_length=1, max_length=500)
    mission_why: Optional[str] = Field(None, max_length=800)
    mission_success: Optional[str] = Field(None, max_length=500)
    tutor_style: Literal["default", "socratic", "feynman", "confucius"] = "default"


class SelfDirectedPracticeAnswer(BaseModel):
    id: str
    answer: str = Field(..., min_length=1, max_length=1000)


class SelfDirectedSubmitPracticeRequest(BaseModel):
    answers: List[SelfDirectedPracticeAnswer] = Field(default_factory=list)


class SelfDirectedCompleteRequest(BaseModel):
    mastery_answer: str = Field(..., min_length=1, max_length=2000)
    practice_answers: List[SelfDirectedPracticeAnswer] = Field(default_factory=list)


class SelfDirectedPracticeFeedbackItem(BaseModel):
    id: str
    ok: bool
    feedback: str


class SelfDirectedSubmitPracticeResponse(BaseModel):
    items: List[SelfDirectedPracticeFeedbackItem] = Field(default_factory=list)


class SelfDirectedSessionResponse(BaseModel):
    id: int
    student_id: int
    goal_text: str
    mission_why: Optional[str] = None
    mission_success: Optional[str] = None
    tutor_style: str = "default"
    status: str
    prior_summary: Optional[str] = None
    lesson_json: Optional[Dict[str, Any]] = None
    check_answers_json: Optional[Dict[str, Any]] = None
    vault_lesson_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
