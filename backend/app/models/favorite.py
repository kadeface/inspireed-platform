"""
课程收藏模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Favorite(Base):
    """课程收藏模型"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, comment="课程ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="收藏时间")
    
    # 关联关系
    user = relationship("User", foreign_keys=[user_id])
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    
    # 唯一约束：同一用户不能重复收藏同一课程
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_favorite'),
    )
    
    def __repr__(self) -> str:
        return f"<Favorite(user_id={self.user_id}, lesson_id={self.lesson_id})>"

