"""
Section（大环节）模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class SectionType(str, Enum):
    """大环节类型枚举"""

    DEFAULT = "default"  # 默认大环节（5个固定大环节）
    CUSTOM = "custom"  # 自定义大环节


class Section(Base):
    """Section（大环节）模型"""

    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)

    # 所属教案
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)

    # 大环节名称
    name = Column(String(200), nullable=False)

    # 大环节类型
    type = Column(
        SQLEnum(SectionType, name="sectiontype"),
        nullable=False,
        default=SectionType.CUSTOM,
        comment="大环节类型：default（默认）或 custom（自定义）",
    )

    # 排序顺序
    order = Column(Integer, default=0, nullable=False)

    # 是否折叠（前端状态，可选同步到后端）
    is_collapsed = Column(Boolean, default=False, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    lesson = relationship("Lesson", back_populates="sections")
    cells = relationship(
        "Cell",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="Cell.order",
    )

    def __repr__(self) -> str:
        return f"<Section(id={self.id}, name={self.name}, lesson_id={self.lesson_id}, order={self.order})>"
