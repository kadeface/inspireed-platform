"""
教师教学任务相关模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TeachingAssignmentType(str, Enum):
    """教学任务类型枚举（已废弃，保留用于向后兼容）"""
    HEAD_TEACHER = "head_teacher"          # 班主任
    SUBJECT_TEACHER = "subject_teacher"   # 学科教师


class TeacherTeachingAssignment(Base):
    """教师教学任务表（支持多学科、多年级、多班级）"""
    __tablename__ = "teacher_teaching_assignments"

    id = Column(Integer, primary_key=True, index=True)

    # 教师关联
    teacher_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="教师ID"
    )

    # 组织关联
    school_id = Column(
        Integer,
        ForeignKey("schools.id"),
        nullable=False,
        index=True,
        comment="学校ID"
    )
    grade_id = Column(
        Integer,
        ForeignKey("grades.id"),
        nullable=False,
        index=True,
        comment="年级ID"
    )
    classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=False,
        index=True,
        comment="班级ID"
    )
    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False,
        index=True,
        comment="学科ID"
    )

    # 时间维度
    semester_id = Column(
        Integer,
        ForeignKey("semesters.id"),
        nullable=False,
        index=True,
        comment="学期ID"
    )
    academic_year = Column(
        String(20),
        nullable=False,
        index=True,
        comment="学年，如 2023-2024"
    )

    # 任务类型（已废弃，保留用于向后兼容）
    assignment_type = Column(
        SQLEnum(
            TeachingAssignmentType,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=True,  # 改为可空，新数据使用position_type_id
        comment="任务类型（已废弃）：HEAD_TEACHER(班主任)/SUBJECT_TEACHER(学科教师)"
    )
    
    # 职务类型（新字段，支持自定义职务）
    position_type_id = Column(
        Integer,
        ForeignKey("teacher_position_types.id"),
        nullable=True,  # 暂时可空，用于迁移期间
        index=True,
        comment="职务类型ID（关联TeacherPositionType）"
    )

    # 状态
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="是否激活"
    )

    # 时间戳
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    # 关联关系
    teacher = relationship("User", foreign_keys=[teacher_id])
    school = relationship("School", foreign_keys=[school_id])
    grade = relationship("Grade", foreign_keys=[grade_id])
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    subject = relationship("Subject", foreign_keys=[subject_id])
    semester = relationship("Semester", foreign_keys=[semester_id])
    position_type = relationship("TeacherPositionType", foreign_keys=[position_type_id])

    # 唯一约束和索引
    __table_args__ = (
        # 唯一约束：同一学期，同一教师，同一班级，同一学科只能有一条记录
        UniqueConstraint(
            'teacher_id',
            'semester_id',
            'classroom_id',
            'subject_id',
            name='uq_teacher_semester_classroom_subject'
        ),
        # 索引：用于快速查询教师在某学期的所有任务
        Index('idx_teacher_semester', 'teacher_id', 'semester_id'),
        # 索引：用于快速查询学校、年级、学科的所有教师
        Index('idx_school_grade_subject', 'school_id', 'grade_id', 'subject_id'),
        # 索引：用于快速查询某学期的所有任务
        Index('idx_semester_active', 'semester_id', 'is_active'),
    )

    def __repr__(self) -> str:
        return (
            f"<TeacherTeachingAssignment("
            f"id={self.id}, "
            f"teacher_id={self.teacher_id}, "
            f"classroom_id={self.classroom_id}, "
            f"subject_id={self.subject_id}, "
            f"semester_id={self.semester_id}"
            f")>"
        )
