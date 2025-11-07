"""
教学活动 Schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.models.activity import ActivitySubmissionStatus, PeerReviewStatus


# ========== 活动提交 Schemas ==========


class ActivitySubmissionBase(BaseModel):
    """活动提交基础Schema"""

    cell_id: int
    lesson_id: int
    responses: Dict[str, Any] = Field(default_factory=dict)


class ActivitySubmissionCreate(ActivitySubmissionBase):
    """创建活动提交请求"""

    started_at: Optional[datetime] = None


class ActivitySubmissionUpdate(BaseModel):
    """更新活动提交请求"""

    responses: Optional[Dict[str, Any]] = None
    status: Optional[ActivitySubmissionStatus] = None
    time_spent: Optional[int] = None


class ActivitySubmissionSubmit(BaseModel):
    """提交活动请求"""

    responses: Dict[str, Any]
    time_spent: Optional[int] = None


class ActivitySubmissionGrade(BaseModel):
    """评分请求"""

    score: float
    teacher_feedback: Optional[str] = None
    item_scores: Optional[Dict[str, float]] = None  # 每题的分数


class ActivitySubmissionResponse(ActivitySubmissionBase):
    """活动提交响应"""

    id: int
    student_id: int
    score: Optional[float] = None
    max_score: Optional[float] = None
    auto_graded: bool
    status: ActivitySubmissionStatus
    teacher_feedback: Optional[str] = None
    graded_by: Optional[int] = None
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    submission_count: int
    time_spent: Optional[int] = None
    is_late: bool
    version: int
    synced: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivitySubmissionWithStudent(ActivitySubmissionResponse):
    """活动提交响应（包含学生信息）"""

    student_email: str
    student_name: str


# ========== 互评 Schemas ==========


class PeerReviewBase(BaseModel):
    """互评基础Schema"""

    submission_id: int
    review_data: Dict[str, Any] = Field(default_factory=dict)
    score: Optional[float] = None
    comment: Optional[str] = None


class PeerReviewCreate(PeerReviewBase):
    """创建互评请求"""

    pass


class PeerReviewUpdate(BaseModel):
    """更新互评请求"""

    review_data: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    comment: Optional[str] = None
    status: Optional[PeerReviewStatus] = None


class PeerReviewResponse(PeerReviewBase):
    """互评响应"""

    id: int
    reviewer_id: int
    lesson_id: int
    cell_id: int
    max_score: Optional[float] = None
    status: PeerReviewStatus
    is_anonymous: bool
    assigned_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PeerReviewWithReviewer(PeerReviewResponse):
    """互评响应（包含评价者信息）"""

    reviewer_name: Optional[str] = None  # 如果匿名则为 None


# ========== 互评分配请求 ==========


class PeerReviewAssignment(BaseModel):
    """互评分配请求"""

    cell_id: int
    lesson_id: int
    reviews_per_student: int = Field(default=2, ge=1, le=5, description="每个学生需要评价的作品数量")
    is_anonymous: bool = Field(default=True, description="是否匿名互评")


# ========== 活动统计 Schemas ==========


class ActivityStatisticsResponse(BaseModel):
    """活动统计响应"""

    id: int
    cell_id: int
    lesson_id: int
    total_students: int
    draft_count: int
    submitted_count: int
    graded_count: int
    average_score: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None
    median_score: Optional[float] = None
    average_time_spent: Optional[int] = None
    item_statistics: Optional[Dict[str, Any]] = None
    peer_review_count: int
    avg_peer_review_score: Optional[float] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 批量操作 ==========


class BulkGradeRequest(BaseModel):
    """批量评分请求"""

    submission_ids: List[int]
    score: float
    teacher_feedback: Optional[str] = None


class BulkReturnRequest(BaseModel):
    """批量退回请求"""

    submission_ids: List[int]
    teacher_feedback: str


# ========== 导出数据 ==========


class ExportSubmissionsRequest(BaseModel):
    """导出提交数据请求"""

    cell_id: int
    format: str = Field(default="csv", description="导出格式：csv, xlsx, json")
    include_responses: bool = Field(default=True, description="是否包含详细答案")


# ========== 离线同步 ==========


class OfflineSyncRequest(BaseModel):
    """离线数据同步请求"""

    submissions: List[Dict[str, Any]]  # 包含多个提交的数据


class OfflineSyncResponse(BaseModel):
    """离线数据同步响应"""

    synced_count: int
    failed_count: int
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)  # 冲突的记录
