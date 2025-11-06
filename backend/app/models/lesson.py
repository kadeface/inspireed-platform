"""
教案模型
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
    Float,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class LessonStatus(str, Enum):
    """教案状态"""

    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"  # 已归档


class DifficultyLevel(str, Enum):
    """难度等级枚举"""

    BEGINNER = "beginner"  # 基础
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级


class Lesson(Base):
    """教案模型"""

    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # 教案创建者
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 所属课程
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)

    # 所属章节（可选，用于将教案关联到具体章节）
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)

    # 状态
    status = Column(
        SQLEnum(LessonStatus, name="lessonstatus"), default=LessonStatus.DRAFT, nullable=False
    )

    # 教案内容（JSON格式存储Cell配置）
    content = Column(JSON, nullable=False, default=list)

    # 版本控制
    version = Column(Integer, default=1, nullable=False)
    parent_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)

    # 国家平台资源映射
    national_resource_id = Column(String(100), nullable=True, index=True)

    # 参考资源（MVP新增）
    reference_resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True, index=True)
    reference_notes = Column(Text, nullable=True)  # 教师的参考笔记

    # 标签
    tags = Column(JSON, nullable=True, default=list)

    # 封面图
    cover_image_url = Column(String(500), nullable=True)

    # 教案统计（MVP新增）
    cell_count = Column(Integer, default=0, nullable=False)  # Cell数量
    estimated_duration = Column(Integer, nullable=True)  # 预计时长（分钟）
    view_count = Column(Integer, default=0, nullable=False)  # 查看次数

    # 难度和评分（学生端增强）
    # 注意：数据库中的 difficultylevel 枚举值为小写（migration 004），
    # 为避免大小写不一致导致的插入错误，这里不设置 Python 端默认值，保持为 NULL。
    difficulty_level = Column(SQLEnum(DifficultyLevel), default=None, nullable=True, comment="难度等级")
    average_rating = Column(Float, default=0.0, nullable=False, comment="平均评分")
    review_count = Column(Integer, default=0, nullable=False, comment="评论数量")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    # 关联关系
    creator = relationship("User", foreign_keys=[creator_id])
    course = relationship("Course", back_populates="lessons")
    chapter = relationship("Chapter", foreign_keys=[chapter_id])
    reference_resource = relationship("Resource", foreign_keys=[reference_resource_id])
    # cells = relationship("Cell", back_populates="lesson", cascade="all, delete-orphan")
    # execution_logs = relationship("ExecutionLog", back_populates="lesson")
    questions = relationship("Question", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title={self.title}, status={self.status})>"
