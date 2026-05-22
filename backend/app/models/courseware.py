"""
课件交互数据模型 — 飞象老师 / 创AI 协同数据追踪
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class CoursewareInteraction(Base):
    """课件交互记录（学生每次答题/点击上报一条）"""

    __tablename__ = "courseware_interactions"

    id = Column(Integer, primary_key=True, index=True)

    # 课件标识
    courseware_id = Column(String(255), nullable=False, index=True, comment="课件唯一ID")
    courseware_title = Column(String(500), nullable=True, comment="课件标题")
    platform = Column(String(100), nullable=True, default="飞象老师", comment="AI平台来源")

    # 关联信息
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True, index=True, comment="关联教案")
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=True, index=True, comment="关联Cell")
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="学生")
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="授课教师")

    # 答题数据
    total_questions = Column(Integer, default=0, comment="总题数")
    correct_count = Column(Integer, default=0, comment="正确数")
    score = Column(Float, default=0.0, comment="得分(0-100)")
    total_time_ms = Column(Integer, default=0, comment="总用时(毫秒)")

    # 详细答题记录
    answers = Column(JSON, nullable=True, default=list, comment="答题明细 [{questionIndex, chosen, correct, isCorrect, timeMs}]")

    # PERMA维度追踪（学生自评）
    perma_scores = Column(JSON, nullable=True, comment="PERMA五维度评分 {P,E,R,M,A}")

    # 原始交互数据
    interaction_data = Column(JSON, nullable=True, comment="原始postMessage数据")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    cell = relationship("Cell", foreign_keys=[cell_id])
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])

    def __repr__(self) -> str:
        return f"<CoursewareInteraction(courseware_id={self.courseware_id}, score={self.score})>"


# 复合索引
Index("idx_cw_courseware_created", CoursewareInteraction.courseware_id, CoursewareInteraction.created_at)
Index("idx_cw_lesson_created", CoursewareInteraction.lesson_id, CoursewareInteraction.created_at)
Index("idx_cw_student_created", CoursewareInteraction.student_id, CoursewareInteraction.created_at)
