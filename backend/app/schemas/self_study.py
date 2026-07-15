"""
学生自学拍题伴学 Schema
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from app.models.self_study import (
    SelfStudyErrorType,
    SelfStudyHandoffStatus,
    SelfStudyResultJudgment,
    SelfStudySessionPhase,
    SelfStudySpeaker,
    SelfStudyTurnKind,
)


class SelfStudyUploadCheckResponse(BaseModel):
    accepted: bool
    upload_token: Optional[str] = None
    storage_key: Optional[str] = None
    file_url: Optional[str] = None
    problem_text_preview: Optional[str] = None
    student_work_text_preview: Optional[str] = None
    message: Optional[str] = None


class SelfStudyErrorResponse(BaseModel):
    detail: str
    error_code: str
    suggestions: List[str] = Field(default_factory=list)


class SelfStudyTurnMeta(BaseModel):
    counts_as_failed_guidance_round: Optional[bool] = None
    confidence: Optional[float] = None
    input_mode: Optional[str] = None
    from_reupload: Optional[bool] = None


class SelfStudyTurnResponse(BaseModel):
    turn_index: int
    speaker: SelfStudySpeaker
    turn_kind: SelfStudyTurnKind
    content_text: str
    meta_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SelfStudyCreateSessionRequest(BaseModel):
    upload_token: str
    voice_transcript_raw: Optional[str] = None
    question_text_confirmed: str = Field(..., min_length=1, max_length=800)
    input_mode: Literal["voice", "text"] = "voice"
    tutor_style: Literal["default", "socratic", "feynman", "confucius"] = "default"


class SelfStudyAppendTurnRequest(BaseModel):
    voice_transcript_raw: Optional[str] = None
    question_text_confirmed: str = Field(..., min_length=1, max_length=800)
    input_mode: Literal["voice", "text"] = "voice"


class SelfStudyUnlockExplanationRequest(BaseModel):
    pass


class SelfStudyHandoffCreateRequest(BaseModel):
    student_last_confusion: str = Field(..., min_length=1, max_length=1000)


class SelfStudyCompleteRequest(BaseModel):
    summary_before: str = Field(..., min_length=1, max_length=1000)
    summary_after: str = Field(..., min_length=1, max_length=1000)


class SelfStudyCurrentAIMessage(BaseModel):
    turn_index: int
    turn_kind: SelfStudyTurnKind
    content_text: str


class SelfStudySessionResponse(BaseModel):
    id: int
    student_id: int
    mode: str
    subject: str
    grade_band: str
    tutor_style: str = "default"
    original_image_url: str
    revised_image_url: Optional[str] = None
    problem_text: Optional[str] = None
    student_work_text: Optional[str] = None
    session_phase: SelfStudySessionPhase
    result_judgment: Optional[SelfStudyResultJudgment] = None
    primary_error_type: Optional[SelfStudyErrorType] = None
    guidance_round_count: int
    explanation_unlocked: bool
    can_view_explanation: bool
    can_handoff_to_teacher: bool
    teacher_handoff_status: Optional[SelfStudyHandoffStatus] = None
    teacher_reply_text: Optional[str] = None
    teacher_reply_image_url: Optional[str] = None
    summary_before: Optional[str] = None
    summary_after: Optional[str] = None
    current_ai_message: Optional[SelfStudyCurrentAIMessage] = None
    turns: List[SelfStudyTurnResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class SelfStudyHandoffResponse(BaseModel):
    handoff_id: int
    session_id: int
    status: SelfStudyHandoffStatus
    teacher_reply_expected: bool = True
    created_at: datetime


class SelfStudyHistoryListItem(BaseModel):
    id: int
    subject: str
    grade_band: str
    thumbnail_url: str
    result_judgment: Optional[SelfStudyResultJudgment] = None
    session_phase: SelfStudySessionPhase
    created_at: datetime


class SelfStudyHistoryListResponse(BaseModel):
    items: List[SelfStudyHistoryListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class SelfStudyTeacherHandoffListItem(BaseModel):
    id: int
    session_id: int
    student_id: int
    student_name: str
    status: SelfStudyHandoffStatus
    title: str
    created_at: datetime


class SelfStudyTeacherHandoffListResponse(BaseModel):
    items: List[SelfStudyTeacherHandoffListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class SelfStudyTeacherHandoffDetailResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    student_name: str
    status: SelfStudyHandoffStatus
    title: str
    original_image_url: str
    revised_image_url: Optional[str] = None
    voice_transcript_raw: Optional[str] = None
    question_text_confirmed: Optional[str] = None
    ai_guidance_summary: List[str] = Field(default_factory=list)
    student_last_confusion: Optional[str] = None
    summary_before: Optional[str] = None
    summary_after: Optional[str] = None
    teacher_reply_text: Optional[str] = None
    teacher_reply_image_url: Optional[str] = None
    created_at: datetime
    answered_at: Optional[datetime] = None


class SelfStudyTeacherHandoffReplyRequest(BaseModel):
    reply_text: str = Field(..., min_length=1, max_length=4000)
    annotated_image_storage_key: Optional[str] = Field(None, max_length=255)


class SelfStudyTeacherHandoffReplyResponse(BaseModel):
    id: int
    status: SelfStudyHandoffStatus
    teacher_reply: Dict[str, Any]
