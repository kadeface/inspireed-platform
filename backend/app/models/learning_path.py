"""
学习路径模型
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
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class DifficultyLevel(str, Enum):
    """难度等级枚举"""

    BEGINNER = "beginner"  # 基础
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级


class LearningPath(Base):
    """学习路径模型"""

    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="路径标题")
    description = Column(Text, nullable=True, comment="路径描述")
    creator_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID"
    )
    difficulty_level = Column(
        SQLEnum(DifficultyLevel),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
        comment="难度等级",
    )
    cover_image_url = Column(String(500), nullable=True, comment="封面图URL")
    is_published = Column(Boolean, default=False, nullable=False, comment="是否已发布")
    estimated_hours = Column(Integer, nullable=True, comment="预计学习时长（小时）")
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
    creator = relationship("User", foreign_keys=[creator_id])
    path_lessons = relationship(
        "LearningPathLesson",
        back_populates="learning_path",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LearningPath(id={self.id}, title={self.title})>"


class LearningPathLesson(Base):
    """学习路径课程关联模型"""

    __tablename__ = "learning_path_lessons"

    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(
        Integer, ForeignKey("learning_paths.id"), nullable=False, comment="学习路径ID"
    )
    lesson_id = Column(
        Integer, ForeignKey("lessons.id"), nullable=False, comment="课程ID"
    )
    order_index = Column(Integer, nullable=False, comment="顺序索引")
    is_required = Column(Boolean, default=True, nullable=False, comment="是否必修")
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )

    # 关联关系
    learning_path = relationship("LearningPath", back_populates="path_lessons")
    lesson = relationship("Lesson", foreign_keys=[lesson_id])

    def __repr__(self) -> str:
        return f"<LearningPathLesson(path_id={self.learning_path_id}, lesson_id={self.lesson_id}, order={self.order_index})>"
