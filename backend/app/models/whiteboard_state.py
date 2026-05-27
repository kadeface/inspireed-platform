"""
课堂白板运行时状态（按 session + cell）
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, UniqueConstraint

from app.core.database import Base


class WhiteboardState(Base):
    __tablename__ = "whiteboard_states"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cell_id = Column(Integer, nullable=False, index=True)
    document = Column(JSON, nullable=False, default=dict)
    version = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "cell_id", name="uq_whiteboard_session_cell"),
    )
