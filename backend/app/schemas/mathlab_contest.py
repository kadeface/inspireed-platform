"""
MathLab 课堂竞赛 Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.mathlab_contest import MathlabContestStatus


class MathlabContestStartRequest(BaseModel):
    cell_id: int
    task_id: Optional[str] = None
    time_limit_sec: Optional[int] = Field(None, ge=30, le=3600)
    allow_resubmit: bool = False
    pass_threshold: int = Field(85, ge=0, le=100)
    settings: Optional[Dict[str, Any]] = None


class MathlabContestTaskUpdate(BaseModel):
    task_id: str = Field(..., min_length=1, max_length=32)


class MathlabContestSubmitRequest(BaseModel):
    auto_score: float = Field(..., ge=0, le=100)
    auto_passed: bool = False
    elapsed_sec: Optional[float] = Field(None, ge=0)
    payload: Dict[str, Any] = Field(default_factory=dict)


class MathlabContestScoreUpdate(BaseModel):
    final_score: float = Field(..., ge=0, le=100)
    passed: Optional[bool] = None


class MathlabContestResponse(BaseModel):
    id: int
    session_id: int
    cell_id: Optional[int]
    teacher_id: int
    task_id: str
    status: MathlabContestStatus
    time_limit_sec: Optional[int]
    allow_resubmit: bool
    pass_threshold: int
    settings: Optional[Dict[str, Any]]
    started_at: datetime
    ended_at: Optional[datetime]
    ends_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MathlabContestSubmissionResponse(BaseModel):
    id: int
    contest_id: int
    student_id: int
    student_name: Optional[str] = None
    auto_score: float
    auto_passed: bool
    final_score: float
    passed: bool
    elapsed_sec: Optional[float]
    payload: Optional[Dict[str, Any]]
    submitted_at: datetime
    rank: Optional[int] = None

    class Config:
        from_attributes = True


class MathlabContestLeaderboardResponse(BaseModel):
    contest: MathlabContestResponse
    submissions: List[MathlabContestSubmissionResponse]
    submitted_count: int
    total_students: int
