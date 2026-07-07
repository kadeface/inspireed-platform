"""
系统级配置模型
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class SystemSetting(Base):
    """系统级键值配置"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value_json = Column(JSON, nullable=False, default=dict)
    description = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    updater = relationship("User", foreign_keys=[updated_by])

    def __repr__(self) -> str:
        return f"<SystemSetting(key={self.key})>"
