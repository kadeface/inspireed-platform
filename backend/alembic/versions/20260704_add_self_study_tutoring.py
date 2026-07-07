"""add self study tutoring tables

Revision ID: 20260704_self_study
Revises: 002, 007_fix_lesson_enum, 018, 20260113_1400, 20260426_image_cell, 20260526_whiteboard, 20260603_site_stats, session_id_formative
Create Date: 2026-07-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260704_self_study"
down_revision: Union[str, tuple[str, ...], None] = (
    "002",
    "007_fix_lesson_enum",
    "018",
    "20260113_1400",
    "20260426_image_cell",
    "20260526_whiteboard",
    "20260603_site_stats",
    "session_id_formative",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


self_study_mode = postgresql.ENUM(
    "completed_check", name="selfstudy_mode", create_type=False
)
self_study_readability_status = postgresql.ENUM(
    "accepted", name="selfstudy_readability_status", create_type=False
)
self_study_session_phase = postgresql.ENUM(
    "awaiting_question",
    "guiding",
    "awaiting_reupload",
    "explanation_unlocked",
    "handed_off",
    "completed",
    name="selfstudy_session_phase",
    create_type=False,
)
self_study_result_judgment = postgresql.ENUM(
    "incorrect",
    "correct_unexplained",
    "understood",
    "needs_teacher",
    name="selfstudy_result_judgment",
    create_type=False,
)
self_study_error_type = postgresql.ENUM(
    "reading_error",
    "relation_error",
    "calculation_error",
    "unit_expression_error",
    "explanation_gap",
    name="selfstudy_error_type",
    create_type=False,
)
self_study_speaker = postgresql.ENUM(
    "student", "ai", "system", name="selfstudy_speaker", create_type=False
)
self_study_turn_kind = postgresql.ENUM(
    "question",
    "probe",
    "hint",
    "explanation",
    "summary",
    name="selfstudy_turn_kind",
    create_type=False,
)
self_study_handoff_status = postgresql.ENUM(
    "pending",
    "answered",
    "closed",
    name="selfstudy_handoff_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    self_study_mode.create(bind, checkfirst=True)
    self_study_readability_status.create(bind, checkfirst=True)
    self_study_session_phase.create(bind, checkfirst=True)
    self_study_result_judgment.create(bind, checkfirst=True)
    self_study_error_type.create(bind, checkfirst=True)
    self_study_speaker.create(bind, checkfirst=True)
    self_study_turn_kind.create(bind, checkfirst=True)
    self_study_handoff_status.create(bind, checkfirst=True)

    op.create_table(
        "self_study_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("mode", self_study_mode, nullable=False, server_default="completed_check"),
        sa.Column("subject", sa.String(length=50), nullable=False, server_default="math"),
        sa.Column("grade_band", sa.String(length=50), nullable=False, server_default="primary"),
        sa.Column("original_image_storage_key", sa.String(length=255), nullable=False),
        sa.Column("revised_image_storage_key", sa.String(length=255), nullable=True),
        sa.Column("problem_text", sa.Text(), nullable=True),
        sa.Column("student_work_text", sa.Text(), nullable=True),
        sa.Column("voice_transcript_raw", sa.Text(), nullable=True),
        sa.Column("question_text_confirmed", sa.Text(), nullable=True),
        sa.Column(
            "readability_status",
            self_study_readability_status,
            nullable=False,
            server_default="accepted",
        ),
        sa.Column(
            "session_phase",
            self_study_session_phase,
            nullable=False,
            server_default="awaiting_question",
        ),
        sa.Column("result_judgment", self_study_result_judgment, nullable=True),
        sa.Column("primary_error_type", self_study_error_type, nullable=True),
        sa.Column("guidance_round_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("explanation_unlocked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("summary_before", sa.Text(), nullable=True),
        sa.Column("summary_after", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_self_study_sessions_student_id", "self_study_sessions", ["student_id"])
    op.create_index("ix_self_study_sessions_session_phase", "self_study_sessions", ["session_phase"])
    op.create_index("ix_self_study_sessions_result_judgment", "self_study_sessions", ["result_judgment"])
    op.create_index("ix_self_study_sessions_created_at", "self_study_sessions", ["created_at"])

    op.create_table(
        "self_study_teacher_handoffs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("self_study_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", self_study_handoff_status, nullable=False, server_default="pending"),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("student_last_confusion", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("teacher_reply_text", sa.Text(), nullable=True),
        sa.Column("teacher_reply_image_storage_key", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("answered_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("session_id", name="uq_self_study_teacher_handoffs_session_id"),
    )
    op.create_index("ix_self_study_teacher_handoffs_session_id", "self_study_teacher_handoffs", ["session_id"])
    op.create_index("ix_self_study_teacher_handoffs_student_id", "self_study_teacher_handoffs", ["student_id"])
    op.create_index("ix_self_study_teacher_handoffs_teacher_id", "self_study_teacher_handoffs", ["teacher_id"])
    op.create_index("ix_self_study_teacher_handoffs_status", "self_study_teacher_handoffs", ["status"])
    op.create_index("ix_self_study_teacher_handoffs_created_at", "self_study_teacher_handoffs", ["created_at"])

    op.create_table(
        "self_study_turns",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("self_study_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("speaker", self_study_speaker, nullable=False),
        sa.Column("turn_kind", self_study_turn_kind, nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_self_study_turns_session_id", "self_study_turns", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_self_study_turns_session_id", table_name="self_study_turns")
    op.drop_table("self_study_turns")

    op.drop_index("ix_self_study_teacher_handoffs_created_at", table_name="self_study_teacher_handoffs")
    op.drop_index("ix_self_study_teacher_handoffs_status", table_name="self_study_teacher_handoffs")
    op.drop_index("ix_self_study_teacher_handoffs_teacher_id", table_name="self_study_teacher_handoffs")
    op.drop_index("ix_self_study_teacher_handoffs_student_id", table_name="self_study_teacher_handoffs")
    op.drop_index("ix_self_study_teacher_handoffs_session_id", table_name="self_study_teacher_handoffs")
    op.drop_table("self_study_teacher_handoffs")

    op.drop_index("ix_self_study_sessions_created_at", table_name="self_study_sessions")
    op.drop_index("ix_self_study_sessions_result_judgment", table_name="self_study_sessions")
    op.drop_index("ix_self_study_sessions_session_phase", table_name="self_study_sessions")
    op.drop_index("ix_self_study_sessions_student_id", table_name="self_study_sessions")
    op.drop_table("self_study_sessions")

    bind = op.get_bind()
    self_study_handoff_status.drop(bind, checkfirst=True)
    self_study_turn_kind.drop(bind, checkfirst=True)
    self_study_speaker.drop(bind, checkfirst=True)
    self_study_error_type.drop(bind, checkfirst=True)
    self_study_result_judgment.drop(bind, checkfirst=True)
    self_study_session_phase.drop(bind, checkfirst=True)
    self_study_readability_status.drop(bind, checkfirst=True)
    self_study_mode.drop(bind, checkfirst=True)
