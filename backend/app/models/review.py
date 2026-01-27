"""
课程评分评论模型
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    """课程评分评论模型"""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    lesson_id = Column(
        Integer, ForeignKey("lessons.id"), nullable=False, comment="课程ID"
    )
    rating = Column(Integer, nullable=False, comment="评分（1-5）")
    comment = Column(Text, nullable=True, comment="评论内容")
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间",
    )

    # 关联关系
    user = relationship("User", foreign_keys=[user_id])
    lesson = relationship("Lesson", foreign_keys=[lesson_id])

    # 约束
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        UniqueConstraint("user_id", "lesson_id", name="unique_user_lesson_review"),
    )

    def __repr__(self) -> str:
        return f"<Review(user_id={self.user_id}, lesson_id={self.lesson_id}, rating={self.rating})>"
