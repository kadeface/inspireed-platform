"""
用户模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Enum as SQLEnum,
    ForeignKey,
)
from sqlalchemy.orm import relationship, validates

from app.core.database import Base
from app.core.validators import normalize_user_role


class UserRole(str, Enum):
    """用户角色枚举（简化为6种）"""

    # 系统角色
    ADMIN = "admin"                    # 系统管理员

    # 管理员角色
    DISTRICT_ADMIN = "district_admin"  # 区县管理员（包含考试管理、教研员职责）
    SCHOOL_ADMIN = "school_admin"      # 学校管理员（包含考试管理、教研员职责）

    # 专业角色
    RESEARCHER = "researcher"          # 教研员（区县/学校）
    TEACHER = "teacher"                # 教师（含班主任）

    # 学生角色
    STUDENT = "student"                # 学生


class StudentType(str, Enum):
    """学生类型枚举（用于文理科区分）

    适用场景：
    - 小学生、初中生：通常为 NONE
    - 高一未分科阶段：NONE（如第一学期，或选科前）
    - 高二、高三已分科：ARTS（文科）或 SCIENCE（理科）

    注意：分科时间因地区和学校而异，由学校根据实际情况设置
    """

    NONE = "none"           # 未分科（小学、初中、高中未分科阶段）
    ARTS = "arts"           # 文科（历史方向/偏文）
    SCIENCE = "science"     # 理科（物理方向/偏理）


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # 学籍号（唯一，跟随学生整个学习经历，不变）
    student_id_number = Column(String(50), unique=True, nullable=True, index=True, comment="学籍号/身份证号等唯一标识")

    # 学生类型（用于高中文理科区分）
    student_type = Column(
        SQLEnum(
            StudentType,
            native_enum=False,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=StudentType.NONE,
        nullable=True,
        comment="学生类型：none(未分科/非高中)/arts(文科)/science(理科)",
    )

    role = Column(
        SQLEnum(
            UserRole,
            native_enum=False,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=UserRole.STUDENT,
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 头像URL
    avatar_url = Column(String(500), nullable=True)

    # 组织关联
    region_id = Column(
        Integer, ForeignKey("regions.id"), nullable=True, comment="所属区/县ID"
    )
    school_id = Column(
        Integer, ForeignKey("schools.id"), nullable=True, comment="所属学校ID"
    )
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True, comment="所属年级ID")
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id"), nullable=True, comment="所属班级ID"
    )

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")

    # 关联关系
    region = relationship("Region")
    school = relationship("School", back_populates="users")
    grade = relationship("Grade")
    classroom = relationship(
        "Classroom", back_populates="students", foreign_keys=[classroom_id]
    )
    # lessons = relationship("Lesson", back_populates="creator", cascade="all, delete-orphan")
    # execution_logs = relationship("ExecutionLog", back_populates="user")
    # qa_records = relationship("QARecord", back_populates="user")
    questions_asked = relationship(
        "Question", foreign_keys="Question.student_id", back_populates="student"
    )
    answers_given = relationship(
        "Answer", foreign_keys="Answer.answerer_id", back_populates="answerer"
    )
    peer_reviews_given = relationship(
        "PeerReview", foreign_keys="PeerReview.reviewer_id", back_populates="reviewer"
    )

    @validates("role")
    def validate_role(self, key: str, value: UserRole) -> UserRole:
        """确保写入数据库的角色值始终规范化为 UserRole 枚举"""
        normalized = normalize_user_role(value)
        if normalized is None:
            raise ValueError("用户角色不能为空")
        return normalized

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
