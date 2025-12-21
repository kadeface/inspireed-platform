"""
班级教学助手相关 Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.classroom_assistant import (
    RoleInClass,
    AttendanceStatus,
    PositiveBehaviorType,
    DisciplineEventType,
    DutyRotationType,
    DutyAssignmentStatus,
)


# ==================== 班级成员关系 ====================


class ClassroomMembershipCreate(BaseModel):
    """创建班级成员关系"""

    classroom_id: int
    user_id: int
    role_in_class: RoleInClass
    student_no: Optional[str] = Field(None, max_length=50)
    seat_no: Optional[int] = None
    cadre_title: Optional[str] = Field(None, max_length=50)
    is_primary_class: bool = False


class ClassroomMembershipUpdate(BaseModel):
    """更新班级成员关系"""

    role_in_class: Optional[RoleInClass] = None
    is_active: Optional[bool] = None
    is_primary_class: Optional[bool] = None
    student_no: Optional[str] = Field(None, max_length=50)
    seat_no: Optional[int] = None
    cadre_title: Optional[str] = Field(None, max_length=50)


class ClassroomMembershipResponse(BaseModel):
    """班级成员关系响应"""

    id: int
    classroom_id: int
    user_id: int
    role_in_class: RoleInClass
    is_active: bool
    is_primary_class: bool
    student_no: Optional[str] = None
    seat_no: Optional[int] = None
    cadre_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # 用户信息（可选，在查询时填充）
    user_name: Optional[str] = None
    user_full_name: Optional[str] = None
    user_email: Optional[str] = None
    user_username: Optional[str] = None

    class Config:
        from_attributes = True


class ClassroomMemberBatchItem(BaseModel):
    """批量导入班级成员单项"""

    # 用户匹配字段（至少提供一个）
    user_id: Optional[int] = None  # 用户ID（可选，如果提供则直接使用）
    student_id_number: Optional[str] = Field(None, max_length=50, description="学籍号（唯一，推荐使用，跟随学生整个学习经历）")
    full_name: Optional[str] = Field(None, max_length=100, description="姓名")
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    username: Optional[str] = Field(None, max_length=100, description="用户名")
    student_no: Optional[str] = Field(None, max_length=50, description="学号（班级内的学号，非学籍号）")
    
    # 班级成员信息
    role_in_class: RoleInClass = RoleInClass.STUDENT
    seat_no: Optional[int] = None
    cadre_title: Optional[str] = Field(None, max_length=50)
    is_primary_class: bool = False
    
    @field_validator("user_id", "full_name", "email", "username", "student_no", mode="before")
    @classmethod
    def normalize_empty_string(cls, v):
        """将空字符串转换为None"""
        return v if v != "" else None
    
    @model_validator(mode="after")
    def validate_at_least_one_identifier(self):
        """确保至少提供了一个用户标识字段"""
        has_identifier = any([
            self.user_id is not None,
            self.student_id_number,
            self.full_name,
            self.email,
            self.username,
            self.student_no,
        ])
        if not has_identifier:
            raise ValueError("至少需要提供一个用户标识字段（用户ID、学籍号、姓名、邮箱、用户名或学号）")
        return self


class ClassroomMemberBatchImportRequest(BaseModel):
    """批量导入班级成员请求"""

    members: List[ClassroomMemberBatchItem]


class ClassroomMemberBatchImportResponse(BaseModel):
    """批量导入班级成员响应"""

    message: str
    success_count: int
    error_count: int
    errors: List[str]
    created_members: List[ClassroomMembershipResponse]


# ==================== 考勤 ====================


class AttendanceSessionCreate(BaseModel):
    """创建考勤会话"""

    window_seconds: int = Field(default=60, ge=1, le=3600)


class AttendanceSessionResponse(BaseModel):
    """考勤会话响应"""

    id: int
    classroom_id: int
    initiated_by_user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    window_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceEntryUpdate(BaseModel):
    """更新考勤记录"""

    status: AttendanceStatus


class AttendanceEntryResponse(BaseModel):
    """考勤记录响应"""

    id: int
    session_id: int
    student_id: int
    status: AttendanceStatus
    updated_by_user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class AttendanceSessionWithEntries(AttendanceSessionResponse):
    """考勤会话及记录详情"""

    entries: List[AttendanceEntryResponse] = []


# ==================== 正面行为 ====================


class PositiveBehaviorTypeInfo(BaseModel):
    """正面行为类型信息"""

    type: PositiveBehaviorType
    name: str
    points: int
    description: Optional[str] = None


class PositiveBehaviorCreate(BaseModel):
    """创建正面行为记录"""

    student_id: int
    behavior_type: PositiveBehaviorType
    custom_behavior_text: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = Field(None, max_length=100)

    @field_validator("custom_behavior_text")
    @classmethod
    def validate_custom_text(cls, v, info):
        behavior_type = info.data.get("behavior_type")
        if behavior_type == PositiveBehaviorType.OTHER and not v:
            raise ValueError("当行为类型为'其他'时，必须填写自定义行为描述")
        return v


class PositiveBehaviorResponse(BaseModel):
    """正面行为记录响应"""

    id: int
    classroom_id: int
    student_id: int
    behavior_type: PositiveBehaviorType
    custom_behavior_text: Optional[str] = None
    points: int
    note: Optional[str] = None
    recorded_by_user_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class PositiveBehaviorLeaderboardEntry(BaseModel):
    """积分榜条目"""

    student_id: int
    student_name: str
    total_points: int
    record_count: int


# ==================== 纪律记录 ====================


class DisciplineEventTypeInfo(BaseModel):
    """纪律事件类型信息"""

    type: DisciplineEventType
    name: str
    category: str
    description: Optional[str] = None


class DisciplineRecordCreate(BaseModel):
    """创建纪律记录"""

    student_id: int
    event_type: DisciplineEventType
    custom_event_text: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = Field(None, max_length=100)

    @field_validator("custom_event_text")
    @classmethod
    def validate_custom_text(cls, v, info):
        event_type = info.data.get("event_type")
        if event_type == DisciplineEventType.OTHER and not v:
            raise ValueError("当事件类型为'其他'时，必须填写自定义事件描述")
        return v


class DisciplineRecordResponse(BaseModel):
    """纪律记录响应"""

    id: int
    classroom_id: int
    student_id: int
    event_type: DisciplineEventType
    custom_event_text: Optional[str] = None
    note: Optional[str] = None
    recorded_by_user_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


# ==================== 值日 ====================


class DutyRuleCreate(BaseModel):
    """创建值日规则"""

    rotation_type: DutyRotationType
    start_date: datetime
    member_user_ids: List[int] = Field(..., min_items=1)
    group_size: int = Field(default=1, ge=1)


class DutyRuleResponse(BaseModel):
    """值日规则响应"""

    id: int
    classroom_id: int
    rotation_type: DutyRotationType
    start_date: datetime
    member_user_ids: List[int]
    group_size: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DutyGenerateRequest(BaseModel):
    """生成值日任务请求"""

    days: int = Field(default=7, ge=1, le=365, description="生成天数（按日轮换）")
    weeks: int = Field(default=4, ge=1, le=52, description="生成周数（按周轮换）")


class DutyAssignmentResponse(BaseModel):
    """值日任务响应"""

    id: int
    classroom_id: int
    rule_id: Optional[int] = None
    duty_date: datetime
    assignee_user_id: int
    status: DutyAssignmentStatus
    completed_by_user_id: Optional[int] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DutyAssignmentUpdate(BaseModel):
    """更新值日任务"""

    status: DutyAssignmentStatus


# ==================== 班级设置 ====================


class ClassroomSettingsUpdate(BaseModel):
    """更新班级设置"""

    show_positive_behaviors_publicly: Optional[bool] = None
    show_discipline_publicly: Optional[bool] = None


class ClassroomSettingsResponse(BaseModel):
    """班级设置响应"""

    show_positive_behaviors_publicly: bool = False
    show_discipline_publicly: bool = False


# ==================== 统计 ====================


class AttendanceStats(BaseModel):
    """出勤统计"""

    total_sessions: int
    present_count: int
    late_count: int
    leave_count: int
    absent_count: int
    attendance_rate: float = Field(..., ge=0, le=1, description="出勤率")


class PositiveBehaviorStats(BaseModel):
    """正面行为统计"""

    total_points: int
    total_records: int
    points_by_type: Dict[str, int] = Field(default_factory=dict)


class DisciplineStats(BaseModel):
    """纪律统计"""

    total_records: int
    records_by_type: Dict[str, int] = Field(default_factory=dict)


class DutyStats(BaseModel):
    """值日统计"""

    total_assignments: int
    completed_count: int
    pending_count: int
    completion_rate: float = Field(..., ge=0, le=1, description="完成率")


class ClassroomStatsResponse(BaseModel):
    """班级统计响应"""

    classroom_id: int
    period_start: datetime
    period_end: datetime
    attendance: Optional[AttendanceStats] = None
    positive_behaviors: Optional[PositiveBehaviorStats] = None
    discipline: Optional[DisciplineStats] = None
    duty: Optional[DutyStats] = None


class StudentStatsResponse(BaseModel):
    """学生个人统计响应"""

    student_id: int
    period_start: datetime
    period_end: datetime
    attendance: Optional[AttendanceStats] = None
    positive_behaviors: Optional[PositiveBehaviorStats] = None
    discipline: Optional[DisciplineStats] = None
    duty: Optional[DutyStats] = None


# ==================== 班级和学生列表 ====================


class ClassroomInfo(BaseModel):
    """班级信息"""

    id: int
    name: str
    code: Optional[str] = None
    school_id: int
    grade_id: int
    head_teacher_id: Optional[int] = None
    deputy_head_teacher_id: Optional[int] = None
    role_in_class: Optional[RoleInClass] = None

    class Config:
        from_attributes = True


class StudentInfo(BaseModel):
    """学生信息"""

    id: int
    username: str
    full_name: Optional[str] = None
    student_no: Optional[str] = None
    seat_no: Optional[int] = None
    cadre_title: Optional[str] = None

    class Config:
        from_attributes = True
