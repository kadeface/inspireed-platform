"""
组织架构相关模型
包括区域、学校等组织单位
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, select
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import Base


class Region(Base):
    """区域模型（省/市/区）"""

    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="区域名称")
    code = Column(String(20), unique=True, nullable=False, comment="区域编码")
    level = Column(Integer, nullable=False, comment="区域级别：1-省，2-市，3-区")
    parent_id = Column(
        Integer, ForeignKey("regions.id"), nullable=True, comment="父级区域ID"
    )
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="区域描述")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关系
    parent = relationship("Region", remote_side=[id], back_populates="children")
    children = relationship("Region", back_populates="parent")
    schools = relationship("School", back_populates="region")


class School(Base):
    """学校模型"""

    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="学校名称")
    code = Column(String(50), unique=True, nullable=False, comment="学校编码")
    region_id = Column(
        Integer, ForeignKey("regions.id"), nullable=False, comment="所属区域ID"
    )
    school_type = Column(String(50), nullable=False, comment="学校类型：小学、初中、高中、大学等")
    address = Column(String(500), nullable=True, comment="学校地址")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    principal = Column(String(50), nullable=True, comment="校长姓名")
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="学校描述")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关系
    region = relationship("Region", back_populates="schools")
    users = relationship("User", back_populates="school")
    classrooms = relationship(
        "Classroom", back_populates="school", cascade="all, delete-orphan"
    )
    rooms = relationship(
        "Room", back_populates="school", cascade="all, delete-orphan"
    )


class Classroom(Base):
    """班级模型"""

    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="班级名称（如 一年级一班）")
    code = Column(String(50), nullable=True, comment="班级编码，可选")
    school_id = Column(
        Integer, ForeignKey("schools.id"), nullable=False, comment="所属学校ID"
    )
    grade_id = Column(
        Integer, ForeignKey("grades.id"), nullable=False, comment="所属年级ID"
    )
    enrollment_year = Column(Integer, nullable=True, comment="入学年份/届别")

    # ✅ DEPRECATED: These fields are kept for backward compatibility
    # but should not be used for new code. Use ClassroomMembership instead.
    head_teacher_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="正班主任ID (已弃用，请使用ClassroomMembership)"
    )
    deputy_head_teacher_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="副班主任ID (已弃用，请使用ClassroomMembership)"
    )
    settings = Column(
        JSON,
        nullable=True,
        comment="班级设置（JSON格式，如可见性控制等）",
    )
    capacity = Column(Integer, nullable=True, comment="班级容量（计划人数）")
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="班级描述")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    school = relationship("School", back_populates="classrooms")
    grade = relationship("Grade", back_populates="classrooms")
    head_teacher = relationship("User", foreign_keys=[head_teacher_id])
    deputy_head_teacher = relationship("User", foreign_keys=[deputy_head_teacher_id])
    students = relationship(
        "User", back_populates="classroom", foreign_keys="User.classroom_id"
    )

    async def get_head_teacher(self, db: AsyncSession) -> Optional["User"]:
        """
        Get head teacher from ClassroomMembership (single source of truth).

        This method queries ClassroomMembership instead of using head_teacher_id.
        The head_teacher_id field is deprecated.

        Args:
            db: Database session

        Returns:
            User object if head teacher exists, None otherwise
        """
        from app.models.classroom_assistant import ClassroomMembership, RoleInClass
        from app.models.user import User

        result = await db.execute(
            select(User).join(ClassroomMembership).where(
                ClassroomMembership.classroom_id == self.id,
                ClassroomMembership.role_in_class == RoleInClass.HEAD_TEACHER_PRIMARY,
                ClassroomMembership.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_deputy_head_teacher(self, db: AsyncSession) -> Optional["User"]:
        """
        Get deputy head teacher from ClassroomMembership (single source of truth).

        Args:
            db: Database session

        Returns:
            User object if deputy exists, None otherwise
        """
        from app.models.classroom_assistant import ClassroomMembership, RoleInClass
        from app.models.user import User

        result = await db.execute(
            select(User).join(ClassroomMembership).where(
                ClassroomMembership.classroom_id == self.id,
                ClassroomMembership.role_in_class == RoleInClass.HEAD_TEACHER_DEPUTY,
                ClassroomMembership.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_teachers(self, db: AsyncSession) -> List["User"]:
        """
        Get all teachers associated with this classroom via ClassroomMembership.

        Args:
            db: Database session

        Returns:
            List of User objects with teacher roles
        """
        from app.models.classroom_assistant import ClassroomMembership, RoleInClass
        from app.models.user import User

        result = await db.execute(
            select(User).join(ClassroomMembership).where(
                ClassroomMembership.classroom_id == self.id,
                ClassroomMembership.role_in_class.in_([
                    RoleInClass.HEAD_TEACHER_PRIMARY,
                    RoleInClass.HEAD_TEACHER_DEPUTY,
                    RoleInClass.SUBJECT_TEACHER,
                ]),
                ClassroomMembership.is_active == True
            )
        )
        return list(result.scalars().all())
