"""
学科教研组模型
提供教师之间的协作和教学设计共享功能
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class GroupScope(str, Enum):
    """教研组范围"""

    SCHOOL = "school"  # 校级教研组
    REGION = "region"  # 区域级教研组
    NATIONAL = "national"  # 全国级教研组


class MemberRole(str, Enum):
    """教研组成员角色"""

    OWNER = "owner"  # 组长
    ADMIN = "admin"  # 管理员
    MEMBER = "member"  # 普通成员


class SubjectGroup(Base):
    """学科教研组模型"""

    __tablename__ = "subject_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="教研组名称")
    description = Column(Text, nullable=True, comment="教研组描述")

    # 学科关联
    subject_id = Column(
        Integer, ForeignKey("subjects.id"), nullable=False, index=True, comment="关联学科"
    )

    # 年级关联（可选，用于筛选）
    grade_id = Column(
        Integer, ForeignKey("grades.id"), nullable=True, index=True, comment="关联年级（可选）"
    )

    # 范围关联
    scope = Column(SQLEnum(GroupScope), nullable=False, comment="教研组范围")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True, comment="关联学校（校级）")
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, comment="关联区域（区域级）")

    # 创建者
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")

    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_public = Column(Boolean, default=False, nullable=False, comment="是否公开（可申请加入）")

    # 统计信息
    member_count = Column(Integer, default=1, nullable=False, comment="成员数量")
    lesson_count = Column(Integer, default=0, nullable=False, comment="共享教案数量")

    # 封面图
    cover_image_url = Column(String(500), nullable=True, comment="封面图URL")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    subject = relationship("Subject", foreign_keys=[subject_id])
    grade = relationship("Grade", foreign_keys=[grade_id])
    school = relationship("School", foreign_keys=[school_id])
    region = relationship("Region", foreign_keys=[region_id])
    creator = relationship("User", foreign_keys=[creator_id])
    memberships = relationship(
        "GroupMembership", back_populates="group", cascade="all, delete-orphan"
    )
    shared_lessons = relationship(
        "SharedLesson", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SubjectGroup(id={self.id}, name={self.name}, scope={self.scope})>"


class GroupMembership(Base):
    """教研组成员关系"""

    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)

    # 关联
    group_id = Column(
        Integer, ForeignKey("subject_groups.id"), nullable=False, index=True, comment="教研组ID"
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 角色
    role = Column(SQLEnum(MemberRole), default=MemberRole.MEMBER, nullable=False, comment="成员角色")

    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")

    # 时间戳
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="加入时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    group = relationship("SubjectGroup", back_populates="memberships")
    user = relationship("User")

    # 唯一约束：一个用户在一个教研组中只能有一个角色
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_user"),)

    def __repr__(self) -> str:
        return (
            f"<GroupMembership(group_id={self.group_id}, user_id={self.user_id}, role={self.role})>"
        )


class SharedLesson(Base):
    """共享的教学设计"""

    __tablename__ = "shared_lessons"

    id = Column(Integer, primary_key=True, index=True)

    # 关联
    group_id = Column(
        Integer, ForeignKey("subject_groups.id"), nullable=False, index=True, comment="教研组ID"
    )
    lesson_id = Column(
        Integer, ForeignKey("lessons.id"), nullable=False, index=True, comment="教案ID"
    )
    sharer_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="分享者ID")

    # 分享说明
    share_note = Column(Text, nullable=True, comment="分享说明")

    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")

    # 统计信息
    view_count = Column(Integer, default=0, nullable=False, comment="查看次数")
    download_count = Column(Integer, default=0, nullable=False, comment="下载/复制次数")
    like_count = Column(Integer, default=0, nullable=False, comment="点赞数")

    # 时间戳
    shared_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="分享时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    group = relationship("SubjectGroup", back_populates="shared_lessons")
    lesson = relationship("Lesson")
    sharer = relationship("User", foreign_keys=[sharer_id])

    # 唯一约束：一个教案在一个教研组中只能被分享一次（同一个教案）
    __table_args__ = (UniqueConstraint("group_id", "lesson_id", name="uq_group_lesson"),)

    def __repr__(self) -> str:
        return f"<SharedLesson(id={self.id}, group_id={self.group_id}, lesson_id={self.lesson_id})>"
