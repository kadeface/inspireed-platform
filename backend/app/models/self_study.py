"""
学生自学拍题伴学数据模型
"""

from __future__ import annotations

from datetime import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class SelfStudyMode(str, enum.Enum):
    COMPLETED_CHECK = "completed_check"


class SelfStudyTutorStyle(str, enum.Enum):
    DEFAULT = "default"
    SOCRATIC = "socratic"
    FEYNMAN = "feynman"
    CONFUCIUS = "confucius"


class SelfStudyReadabilityStatus(str, enum.Enum):
    ACCEPTED = "accepted"


class SelfStudySessionPhase(str, enum.Enum):
    AWAITING_QUESTION = "awaiting_question"
    GUIDING = "guiding"
    AWAITING_REUPLOAD = "awaiting_reupload"
    EXPLANATION_UNLOCKED = "explanation_unlocked"
    HANDED_OFF = "handed_off"
    COMPLETED = "completed"


class SelfStudyResultJudgment(str, enum.Enum):
    INCORRECT = "incorrect"
    CORRECT_UNEXPLAINED = "correct_unexplained"
    UNDERSTOOD = "understood"
    NEEDS_TEACHER = "needs_teacher"


class SelfStudyErrorType(str, enum.Enum):
    READING_ERROR = "reading_error"
    RELATION_ERROR = "relation_error"
    CALCULATION_ERROR = "calculation_error"
    UNIT_EXPRESSION_ERROR = "unit_expression_error"
    EXPLANATION_GAP = "explanation_gap"


class SelfStudySpeaker(str, enum.Enum):
    STUDENT = "student"
    AI = "ai"
    SYSTEM = "system"


class SelfStudyTurnKind(str, enum.Enum):
    QUESTION = "question"
    PROBE = "probe"
    HINT = "hint"
    EXPLANATION = "explanation"
    SUMMARY = "summary"


class SelfStudyHandoffStatus(str, enum.Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    CLOSED = "closed"


class SelfStudySession(Base):
    __tablename__ = "self_study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    mode = Column(
        SQLEnum(SelfStudyMode, values_callable=lambda x: [e.value for e in x], name="selfstudy_mode"),
        nullable=False,
        default=SelfStudyMode.COMPLETED_CHECK,
    )
    subject = Column(String(50), nullable=False, default="math")
    grade_band = Column(String(50), nullable=False, default="primary")

    tutor_style = Column(String(50), nullable=False, default=SelfStudyTutorStyle.DEFAULT.value)

    original_image_storage_key = Column(String(255), nullable=False)
    revised_image_storage_key = Column(String(255), nullable=True)

    problem_text = Column(Text, nullable=True)
    student_work_text = Column(Text, nullable=True)

    voice_transcript_raw = Column(Text, nullable=True)
    question_text_confirmed = Column(Text, nullable=True)

    readability_status = Column(
        SQLEnum(
            SelfStudyReadabilityStatus,
            values_callable=lambda x: [e.value for e in x],
            name="selfstudy_readability_status",
        ),
        nullable=False,
        default=SelfStudyReadabilityStatus.ACCEPTED,
    )
    session_phase = Column(
        SQLEnum(SelfStudySessionPhase, values_callable=lambda x: [e.value for e in x], name="selfstudy_session_phase"),
        nullable=False,
        default=SelfStudySessionPhase.AWAITING_QUESTION,
        index=True,
    )
    result_judgment = Column(
        SQLEnum(
            SelfStudyResultJudgment,
            values_callable=lambda x: [e.value for e in x],
            name="selfstudy_result_judgment",
        ),
        nullable=True,
        index=True,
    )
    primary_error_type = Column(
        SQLEnum(SelfStudyErrorType, values_callable=lambda x: [e.value for e in x], name="selfstudy_error_type"),
        nullable=True,
    )
    guidance_round_count = Column(Integer, nullable=False, default=0)
    explanation_unlocked = Column(Boolean, nullable=False, default=False)

    summary_before = Column(Text, nullable=True)
    summary_after = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    student = relationship("User", foreign_keys=[student_id])
    turns = relationship(
        "SelfStudyTurn",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SelfStudyTurn.turn_index",
        foreign_keys="SelfStudyTurn.session_id",
    )
    teacher_handoff = relationship(
        "SelfStudyTeacherHandoff",
        back_populates="session",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="SelfStudyTeacherHandoff.session_id",
    )


class SelfStudyTurn(Base):
    __tablename__ = "self_study_turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("self_study_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    turn_index = Column(Integer, nullable=False)
    speaker = Column(
        SQLEnum(SelfStudySpeaker, values_callable=lambda x: [e.value for e in x], name="selfstudy_speaker"),
        nullable=False,
    )
    turn_kind = Column(
        SQLEnum(SelfStudyTurnKind, values_callable=lambda x: [e.value for e in x], name="selfstudy_turn_kind"),
        nullable=False,
    )
    content_text = Column(Text, nullable=False)
    meta_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("SelfStudySession", back_populates="turns")


class SelfStudyTeacherHandoff(Base):
    __tablename__ = "self_study_teacher_handoffs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("self_study_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    status = Column(
        SQLEnum(
            SelfStudyHandoffStatus,
            values_callable=lambda x: [e.value for e in x],
            name="selfstudy_handoff_status",
        ),
        nullable=False,
        default=SelfStudyHandoffStatus.PENDING,
        index=True,
    )
    title = Column(String(200), nullable=False)
    student_last_confusion = Column(Text, nullable=True)
    payload_json = Column(JSON, nullable=False)
    teacher_reply_text = Column(Text, nullable=True)
    teacher_reply_image_storage_key = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    answered_at = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    session = relationship(
        "SelfStudySession",
        back_populates="teacher_handoff",
        foreign_keys=[session_id],
    )
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
