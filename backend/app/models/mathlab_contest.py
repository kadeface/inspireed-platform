"""
MathLab 课堂竞赛模型
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class MathlabContestStatus(str, Enum):
    PREPARING = "preparing"
    RUNNING = "running"
    ENDED = "ended"


class MathlabContest(Base):
    """一场 MathLab 课堂竞赛（挂在 ClassSession + SimCell）"""

    __tablename__ = "mathlab_contests"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("class_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cell_id = Column(Integer, ForeignKey("cells.id", ondelete="SET NULL"), nullable=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(String(32), nullable=False)
    status = Column(
        SQLEnum(MathlabContestStatus),
        default=MathlabContestStatus.RUNNING,
        nullable=False,
        index=True,
    )
    time_limit_sec = Column(Integer, nullable=True)
    allow_resubmit = Column(Boolean, default=False, nullable=False)
    pass_threshold = Column(Integer, default=85, nullable=False)
    settings = Column(JSON, nullable=True, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ClassSession", foreign_keys=[session_id])
    submissions = relationship(
        "MathlabContestSubmission",
        back_populates="contest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<MathlabContest(id={self.id}, session_id={self.session_id}, status={self.status})>"


class MathlabContestSubmission(Base):
    """学生竞赛提交"""

    __tablename__ = "mathlab_contest_submissions"
    __table_args__ = (
        UniqueConstraint("contest_id", "student_id", name="uq_mathlab_contest_student"),
        Index("ix_mathlab_contest_submissions_contest_score", "contest_id", "final_score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(
        Integer,
        ForeignKey("mathlab_contests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    auto_score = Column(Float, nullable=False, default=0)
    auto_passed = Column(Boolean, default=False, nullable=False)
    final_score = Column(Float, nullable=False, default=0)
    passed = Column(Boolean, default=False, nullable=False)
    elapsed_sec = Column(Float, nullable=True)
    payload = Column(JSON, nullable=True, default=dict)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contest = relationship("MathlabContest", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])

    def __repr__(self) -> str:
        return f"<MathlabContestSubmission(contest_id={self.contest_id}, student_id={self.student_id})>"
