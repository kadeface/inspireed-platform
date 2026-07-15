"""
学生自主学习（/teach 工作流移植）数据模型
"""

from __future__ import annotations

from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class SelfDirectedSessionStatus(str, enum.Enum):
    GENERATING = "generating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SelfDirectedSession(Base):
    __tablename__ = "self_directed_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    goal_text = Column(Text, nullable=False)
    mission_why = Column(Text, nullable=True)
    mission_success = Column(Text, nullable=True)
    tutor_style = Column(String(50), nullable=False, default="default")

    status = Column(String(30), nullable=False, default=SelfDirectedSessionStatus.GENERATING.value, index=True)
    prior_summary = Column(Text, nullable=True)
    lesson_json = Column(JSON, nullable=True)
    check_answers_json = Column(JSON, nullable=True)
    vault_lesson_path = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)

    student = relationship("User", foreign_keys=[student_id])
