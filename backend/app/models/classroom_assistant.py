"""
班级教学助手相关模型
包括班级成员关系、考勤、课堂表现、纪律记录、值日等
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    JSON,
    UniqueConstraint,
    Index,
    SmallInteger,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RoleInClass(str, Enum):
    """班级内角色枚举"""

    HEAD_TEACHER_PRIMARY = "head_teacher_primary"
    HEAD_TEACHER_DEPUTY = "head_teacher_deputy"
    SUBJECT_TEACHER = "subject_teacher"
    CADRE = "cadre"
    STUDENT = "student"


class AttendanceStatus(str, Enum):
    """考勤状态枚举"""

    PRESENT = "present"
    LATE = "late"
    LEAVE = "leave"
    ABSENT = "absent"


class PositiveBehaviorType(str, Enum):
    """正面行为类型枚举"""

    ACTIVE_RESPONSE = "active_response"  # 积极回答，+2
    CORRECT_ANSWER = "correct_answer"  # 回答正确，+3
    HELP_CLASSMATE = "help_classmate"  # 帮助同学，+3
    EXCELLENT_HOMEWORK = "excellent_homework"  # 优秀作业，+2
    PROACTIVE_THINKING = "proactive_thinking"  # 主动思考，+2
    COLLABORATIVE_WORK = "collaborative_work"  # 团队协作，+3
    OTHER = "other"  # 其他，+1


class DisciplineEventType(str, Enum):
    """纪律事件类型枚举"""

    # 课堂行为类
    TALKING = "talking"
    WALKING = "walking"
    NOT_PARTICIPATING = "not_participating"
    SLEEPING = "sleeping"
    DISTRACTED = "distracted"
    # 课堂秩序类
    INTERRUPTING = "interrupting"
    DISTURBING_OTHERS = "disturbing_others"
    NOT_FOLLOWING_INSTRUCTIONS = "not_following_instructions"
    # 作业与学习准备类
    MISSING_MATERIALS = "missing_materials"
    HOMEWORK_INCOMPLETE = "homework_incomplete"
    HOMEWORK_NOT_AS_REQUIRED = "homework_not_as_required"
    # 课间与公共区域行为
    HALLWAY_ROUGHHOUSING = "hallway_roughhousing"
    RUNNING_IN_HALLWAY = "running_in_hallway"
    LOUD_NOISE = "loud_noise"
    # 其他
    OTHER = "other"


class DutyRotationType(str, Enum):
    """值日轮换类型枚举"""

    DAILY = "daily"
    WEEKLY = "weekly"


class DutyAssignmentStatus(str, Enum):
    """值日任务状态枚举"""

    PENDING = "pending"
    COMPLETED = "completed"


class ClassroomMembership(Base):
    """班级成员关系"""

    __tablename__ = "classroom_memberships"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_in_class = Column(
        SQLEnum(RoleInClass, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_primary_class = Column(
        Boolean, default=False, nullable=False, comment="是否为主班级/默认进入班级"
    )
    # 学生管理扩展字段
    student_no = Column(String(50), nullable=True, comment="学号/学籍号")
    seat_no = Column(SmallInteger, nullable=True, comment="座号")
    cadre_title = Column(String(50), nullable=True, comment="班干部职务名称")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关联关系
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("classroom_id", "user_id", name="uq_classroom_user"),
        Index("idx_membership_user_active", "user_id", "is_active"),
        Index("idx_membership_classroom_role", "classroom_id", "role_in_class"),
    )


class AttendanceSession(Base):
    """考勤会话"""

    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=False, index=True
    )
    initiated_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    window_seconds = Column(
        Integer, default=60, nullable=False, comment="点名时间窗口（秒）"
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 关联关系
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    initiator = relationship("User", foreign_keys=[initiated_by_user_id])
    entries = relationship(
        "AttendanceEntry",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class AttendanceEntry(Base):
    """考勤记录条目"""

    __tablename__ = "attendance_entries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("attendance_sessions.id"), nullable=False, index=True
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        SQLEnum(AttendanceStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    updated_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关联关系
    session = relationship("AttendanceSession", foreign_keys=[session_id], back_populates="entries")
    student = relationship("User", foreign_keys=[student_id])
    updated_by = relationship("User", foreign_keys=[updated_by_user_id])

    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )


class PositiveBehavior(Base):
    """正面行为记录"""

    __tablename__ = "positive_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=False, index=True
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    behavior_type = Column(
        SQLEnum(PositiveBehaviorType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    custom_behavior_text = Column(String(100), nullable=True, comment="自定义行为描述（仅当类型为other时）")
    points = Column(SmallInteger, nullable=False, comment="积分")
    note = Column(String(100), nullable=True, comment="教师备注（0-50字）")
    recorded_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    recorded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # 关联关系
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    student = relationship("User", foreign_keys=[student_id])
    recorded_by = relationship("User", foreign_keys=[recorded_by_user_id])

    __table_args__ = (
        Index("idx_positive_classroom_student_date", "classroom_id", "student_id", "recorded_at"),
        Index("idx_positive_student_date", "student_id", "recorded_at"),
    )


class DisciplineRecord(Base):
    """纪律记录"""

    __tablename__ = "discipline_records"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=False, index=True
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(
        SQLEnum(DisciplineEventType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    custom_event_text = Column(String(100), nullable=True, comment="自定义事件描述（仅当类型为other时）")
    note = Column(String(100), nullable=True, comment="教师备注（0-50字）")
    recorded_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    recorded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # 关联关系
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    student = relationship("User", foreign_keys=[student_id])
    recorded_by = relationship("User", foreign_keys=[recorded_by_user_id])

    __table_args__ = (
        Index("idx_discipline_classroom_student_date", "classroom_id", "student_id", "recorded_at"),
        Index("idx_discipline_student_date", "student_id", "recorded_at"),
    )


class DutyRule(Base):
    """值日规则"""

    __tablename__ = "duty_rules"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=False, index=True
    )
    rotation_type = Column(
        SQLEnum(DutyRotationType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    start_date = Column(DateTime(timezone=True), nullable=False, comment="轮换开始日期")
    member_user_ids = Column(
        JSON, nullable=False, comment="参与值日的学生ID列表（JSON数组）"
    )
    group_size = Column(
        SmallInteger, default=1, nullable=False, comment="每组值日人数"
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关联关系
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    assignments = relationship(
        "DutyAssignment",
        back_populates="rule",
        cascade="all, delete-orphan",
    )


class DutyAssignment(Base):
    """值日任务分配"""

    __tablename__ = "duty_assignments"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=False, index=True
    )
    rule_id = Column(Integer, ForeignKey("duty_rules.id"), nullable=True, index=True)
    duty_date = Column(DateTime(timezone=True), nullable=False, index=True)
    assignee_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    status = Column(
        SQLEnum(DutyAssignmentStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        default=DutyAssignmentStatus.PENDING,
        nullable=False,
    )
    completed_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # 关联关系
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    rule = relationship("DutyRule", foreign_keys=[rule_id], back_populates="assignments")
    assignee = relationship("User", foreign_keys=[assignee_user_id])
    completed_by = relationship("User", foreign_keys=[completed_by_user_id])

    __table_args__ = (
        UniqueConstraint("classroom_id", "duty_date", "assignee_user_id", name="uq_classroom_date_assignee"),
        Index("idx_duty_classroom_date", "classroom_id", "duty_date"),
    )
