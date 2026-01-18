"""
年级考试科目配置模型
用于教务管理员配置每个年级的考试科目及分数设置
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class GradeSubjectConfig(Base):
    """年级考试科目配置模型

    用于配置某个年级在考试中包含哪些科目，以及每个科目的分数设置
    例如：七年级考试包含语文(100分)、数学(100分)、英语(100分)
    """

    __tablename__ = "grade_subject_configs"

    id = Column(Integer, primary_key=True, index=True)

    # 关联年级和学科
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, comment="年级ID")
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, comment="学科ID")

    # 分数设置（可针对不同年级设置不同分数）
    full_score = Column(Integer, nullable=False, default=100, comment="满分")
    pass_line = Column(Integer, nullable=False, default=60, comment="及格线")
    excellent_line = Column(Integer, nullable=False, default=85, comment="优秀线")
    good_line = Column(Integer, nullable=False, default=75, comment="良好线")

    # 其他配置
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    display_order = Column(Integer, default=0, nullable=False, comment="显示顺序")
    description = Column(String(200), nullable=True, comment="备注说明")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人")

    # 唯一约束：同一个年级+学科只能有一条配置
    __table_args__ = (
        UniqueConstraint('grade_id', 'subject_id', name='uq_grade_subject'),
    )

    # 关联关系
    grade = relationship("Grade", backref="exam_subjects")
    subject = relationship("Subject", backref="exam_grades")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<GradeSubjectConfig(grade_id={self.grade_id}, subject_id={self.subject_id}, full_score={self.full_score})>"
