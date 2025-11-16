"""
课堂会话 Schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.models.classroom_session import ClassSessionStatus


# ========== 课堂会话 Schemas ==========


class ClassSessionBase(BaseModel):
    """课堂会话基础Schema"""

    lesson_id: int
    classroom_id: int
    scheduled_start: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ClassSessionCreate(ClassSessionBase):
    """创建课堂会话请求"""

    pass


class ClassSessionUpdate(BaseModel):
    """更新课堂会话请求"""

    status: Optional[ClassSessionStatus] = None
    current_cell_id: Optional[int] = None
    current_activity_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None


class ClassSessionResponse(ClassSessionBase):
    """课堂会话响应"""

    id: int
    teacher_id: int
    status: ClassSessionStatus
    actual_start: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    current_cell_id: Optional[int] = None
    current_activity_id: Optional[int] = None
    total_students: int
    active_students: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassSessionWithDetails(ClassSessionResponse):
    """课堂会话响应（包含详细信息）"""

    lesson_title: Optional[str] = None
    classroom_name: Optional[str] = None
    teacher_name: Optional[str] = None


# ========== 学生参与 Schemas ==========


class StudentParticipationBase(BaseModel):
    """学生参与基础Schema"""

    session_id: int
    current_cell_id: Optional[int] = None
    completed_cells: Optional[List[int]] = Field(default_factory=list)
    progress_percentage: float = 0.0


class StudentParticipationResponse(StudentParticipationBase):
    """学生参与响应"""

    id: int
    student_id: int
    joined_at: datetime
    last_active_at: datetime
    left_at: Optional[datetime] = None
    is_active: bool
    student_name: Optional[str] = None
    student_email: Optional[str] = None

    class Config:
        from_attributes = True


# ========== WebSocket 消息 Schemas ==========


class ClassroomEvent(BaseModel):
    """课堂事件"""

    type: str  # session_started, cell_changed, activity_started, student_joined, etc.
    session_id: int
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NavigateToCellRequest(BaseModel):
    """导航到Cell请求"""

    cell_id: Optional[int] = None  # Cell的数字ID
    cell_order: Optional[int] = None  # Cell的order（作为备选方案，用于UUID的情况）
    action: Optional[str] = "toggle"  # 操作类型：toggle（切换，默认）/ add（添加）/ remove（移除）
    multi_select: Optional[bool] = False  # 是否多选模式


class StartActivityRequest(BaseModel):
    """开始活动请求"""

    cell_id: int


class StudentProgressUpdate(BaseModel):
    """学生进度更新"""

    current_cell_id: Optional[int] = None
    completed_cells: List[int] = Field(default_factory=list)
    progress_percentage: float = 0.0


# ========== 会话操作请求 ==========


class StartSessionRequest(BaseModel):
    """开始会话请求"""

    pass


class PauseSessionRequest(BaseModel):
    """暂停会话请求"""

    pass


class ResumeSessionRequest(BaseModel):
    """继续会话请求"""

    pass


class EndSessionRequest(BaseModel):
    """结束会话请求"""

    notes: Optional[str] = None  # 课后笔记


# ========== 统计数据 ==========


class SessionStatistics(BaseModel):
    """会话统计数据"""

    total_students: int
    active_students: int
    completed_students: int
    average_progress: float
    students_by_progress: Dict[str, int]  # {"0-25%": 5, "25-50%": 10, ...}


