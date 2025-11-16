"""
课堂会话模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
    JSON,
    Enum as SQLEnum,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClassSessionStatus(str, Enum):
    """课堂会话状态"""

    PENDING = "pending"  # 准备中（教师已创建但未开始）
    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 已暂停
    ENDED = "ended"  # 已结束


class ClassSession(Base):
    """课堂会话"""

    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 会话状态
    status = Column(
        SQLEnum(ClassSessionStatus),
        default=ClassSessionStatus.PENDING,
        nullable=False,
        index=True,
    )

    # 时间信息
    scheduled_start = Column(DateTime, nullable=True)  # 计划开始时间
    actual_start = Column(DateTime, nullable=True)  # 实际开始时间
    ended_at = Column(DateTime, nullable=True)  # 结束时间
    duration_minutes = Column(Integer, nullable=True)  # 实际时长（分钟）

    # 当前状态
    current_cell_id = Column(
        Integer, ForeignKey("cells.id"), nullable=True, index=True
    )  # 当前显示的Cell
    current_activity_id = Column(Integer, nullable=True, index=True)  # 当前活动的Cell ID

    # 会话设置（JSON格式）
    # 示例：
    # {
    #   "allow_advance": true,      # 允许学生提前查看
    #   "sync_mode": "strict",      # 同步模式：strict/free
    #   "show_leaderboard": false,  # 显示排行榜
    #   "auto_save": true           # 自动保存学生答案
    # }
    settings = Column(JSON, nullable=True, default=dict)

    # 统计数据
    total_students = Column(Integer, default=0, nullable=False)  # 参与学生数
    active_students = Column(Integer, default=0, nullable=False)  # 在线学生数

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
    current_cell = relationship("Cell", foreign_keys=[current_cell_id])
    participations = relationship(
        "StudentSessionParticipation",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ClassSession(id={self.id}, lesson_id={self.lesson_id}, status={self.status})>"


class StudentSessionParticipation(Base):
    """学生会话参与记录"""

    __tablename__ = "student_session_participations"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    session_id = Column(
        Integer, ForeignKey("class_sessions.id"), nullable=False, index=True
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 参与状态
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # 加入时间
    last_active_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )  # 最后活跃时间
    left_at = Column(DateTime, nullable=True)  # 离开时间
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # 是否在线

    # 进度信息
    current_cell_id = Column(Integer, nullable=True, index=True)  # 当前所在Cell
    completed_cells = Column(JSON, nullable=True, default=list)  # 已完成的Cell ID列表
    progress_percentage = Column(Float, default=0.0, nullable=False)  # 完成百分比

    # 关联关系
    session = relationship("ClassSession", foreign_keys=[session_id], back_populates="participations")
    student = relationship("User", foreign_keys=[student_id])

    def __repr__(self) -> str:
        return f"<StudentSessionParticipation(session_id={self.session_id}, student_id={self.student_id})>"


# 创建索引以优化查询性能
Index("idx_session_status_teacher", ClassSession.teacher_id, ClassSession.status)
Index(
    "idx_session_classroom_status",
    ClassSession.classroom_id,
    ClassSession.status,
)
Index(
    "idx_participation_session_active",
    StudentSessionParticipation.session_id,
    StudentSessionParticipation.is_active,
)

