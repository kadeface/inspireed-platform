"""
考试考场安排 Pydantic Schemas

包括：
- 考场管理（ExamRoom）
- 考场学生（ExamRoomStudent）
- 监考教师（ExamProctor）
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# 考场学生（ExamRoomStudent）
# ============================================================================

class ExamRoomStudentBase(BaseModel):
    """考场学生基础模型"""
    student_id: int = Field(..., description="学生ID")
    exam_number: str = Field(..., max_length=20, description="考号")
    seat_number: int = Field(..., ge=1, le=100, description="座位号")
    student_id_number: Optional[str] = Field(None, max_length=50, description="学籍号")
    student_name: Optional[str] = Field(None, max_length=100, description="学生姓名")
    school_id: Optional[int] = Field(None, description="学校ID")
    classroom_id: Optional[int] = Field(None, description="班级ID")


class ExamRoomStudentResponse(ExamRoomStudentBase):
    """考场学生响应模型"""
    id: int
    room_id: int
    table_number: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 监考教师（ExamProctor）
# ============================================================================

class ExamProctorBase(BaseModel):
    """监考教师基础模型"""
    user_id: int = Field(..., description="教师用户ID")
    proctor_type: str = Field(..., pattern="^(primary|assistant)$", description="监考类型：primary/assistant")
    responsibilities: Optional[List[str]] = Field(None, description="职责列表")


class ExamProctorResponse(ExamProctorBase):
    """监考教师响应模型"""
    id: int
    room_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 考场管理（ExamRoom）
# ============================================================================

class ExamRoomBase(BaseModel):
    """考场基础模型"""
    name: str = Field(..., max_length=100, description="考场名称")
    room_id: Optional[int] = Field(None, description="使用的教室ID")
    capacity: int = Field(30, ge=10, le=100, description="考场容量")
    arrangement_type: str = Field("by_class", pattern="^(by_class|mixed)$", description="编排类型：by_class/mixed")
    seat_pattern: str = Field("s_shape", pattern="^(sequential|s_shape)$", description="座位排列：sequential/s_shape")


class ExamRoomCreate(ExamRoomBase):
    """创建考场"""
    pass


class ExamRoomUpdate(BaseModel):
    """更新考场"""
    capacity: Optional[int] = Field(None, ge=10, le=100, description="考场容量")
    arrangement_type: Optional[str] = Field(None, pattern="^(by_class|mixed)$", description="编排类型")
    seat_pattern: Optional[str] = Field(None, pattern="^(sequential|s_shape)$", description="座位排列")


class ExamRoomResponse(ExamRoomBase):
    """考场响应模型"""
    id: int
    exam_id: int
    school_id: int
    seat_count: int
    exam_number_start: Optional[str]
    exam_number_end: Optional[str]
    students: List[ExamRoomStudentResponse] = []
    proctors: List[ExamProctorResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 批量操作
# ============================================================================

class AutoAssignRoomsRequest(BaseModel):
    """自动分配考场请求"""
    capacity_per_room: int = Field(30, ge=10, le=100, description="每个考场人数")
    arrangement_type: str = Field("by_class", pattern="^(by_class|mixed)$", description="编排类型")
    seat_pattern: str = Field("s_shape", pattern="^(sequential|s_shape)$", description="座位排列")
    use_existing_rooms: bool = Field(True, description="是否使用现有教室作为考场")


class AutoAssignProctorsRequest(BaseModel):
    """自动分配监考教师请求"""
    auto_assign: bool = Field(True, description="是否自动分配")
    avoid_own_class: bool = Field(True, description="避免监考本班")
    same_school_only: bool = Field(True, description="仅使用本校教师")


class ProctorAssignmentResponse(BaseModel):
    """监考分配响应"""
    message: str = Field(..., description="响应消息")
    total_proctors: int = Field(..., description="分配的监考总数")
    rooms_assigned: int = Field(..., description="分配的考场数")
