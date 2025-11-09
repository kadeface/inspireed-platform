"""add formative assessment supporting structures

Revision ID: b2e6f4321abc
Revises: 5a7c9d8b1f23
Create Date: 2025-11-09 14:30:00.000000+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "b2e6f4321abc"
down_revision = "5a7c9d8b1f23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- activity_submissions extensions ---
    op.add_column(
        "activity_submissions",
        sa.Column("process_trace", sa.JSON(), nullable=True),
    )
    op.add_column(
        "activity_submissions",
        sa.Column("context", sa.JSON(), nullable=True),
    )
    op.add_column(
        "activity_submissions",
        sa.Column(
            "attempt_no",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.add_column(
        "activity_submissions",
        sa.Column("activity_phase", sa.String(length=32), nullable=True),
    )
    op.create_index(
        "ix_activity_submissions_activity_phase",
        "activity_submissions",
        ["activity_phase"],
    )

    op.add_column(
        "activity_statistics",
        sa.Column("flowchart_metrics", sa.JSON(), nullable=True),
    )

    # --- activity_item_statistics ---
    op.create_table(
        "activity_item_statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.String(length=64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_score", sa.Float(), nullable=True),
        sa.Column("avg_time_spent", sa.Float(), nullable=True),
        sa.Column("option_distribution", sa.JSON(), nullable=True),
        sa.Column("score_distribution", sa.JSON(), nullable=True),
        sa.Column("knowledge_stats", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"],
            ["cells.id"],
            name="fk_activity_item_statistics_cell_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            name="fk_activity_item_statistics_lesson_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cell_id",
            "item_id",
            name="uq_activity_item_stats_cell_item",
        ),
    )
    op.create_index(
        "ix_activity_item_statistics_cell_id",
        "activity_item_statistics",
        ["cell_id"],
    )
    op.create_index(
        "ix_activity_item_statistics_lesson_id",
        "activity_item_statistics",
        ["lesson_id"],
    )

    # --- flowchart_snapshots ---
    op.create_table(
        "flowchart_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("graph", sa.JSON(), nullable=False),
        sa.Column("analysis", sa.JSON(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["activity_submissions.id"],
            name="fk_flowchart_snapshots_submission_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name="fk_flowchart_snapshots_student_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            name="fk_flowchart_snapshots_lesson_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"],
            ["cells.id"],
            name="fk_flowchart_snapshots_cell_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_flowchart_snapshots_submission",
        "flowchart_snapshots",
        ["submission_id", "version"],
    )
    op.create_index(
        "ix_flowchart_snapshots_student",
        "flowchart_snapshots",
        ["student_id"],
    )

    # --- formative_assessments ---
    op.create_table(
        "formative_assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(length=32), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("risk_level", sa.String(length=16), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            name="fk_formative_assessments_lesson_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name="fk_formative_assessments_student_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "lesson_id",
            "student_id",
            "phase",
            name="uq_formative_assessment_scope",
        ),
    )
    op.create_index(
        "ix_formative_assessments_student_lesson",
        "formative_assessments",
        ["student_id", "lesson_id"],
    )
    op.create_index(
        "ix_formative_assessments_phase",
        "formative_assessments",
        ["phase"],
    )

    # remove server default for attempt_no after data migration
    op.alter_column(
        "activity_submissions",
        "attempt_no",
        server_default=None,
        existing_type=sa.Integer(),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_formative_assessments_phase",
        table_name="formative_assessments",
    )
    op.drop_index(
        "ix_formative_assessments_student_lesson",
        table_name="formative_assessments",
    )
    op.drop_table("formative_assessments")

    op.drop_index(
        "ix_flowchart_snapshots_student",
        table_name="flowchart_snapshots",
    )
    op.drop_index(
        "ix_flowchart_snapshots_submission",
        table_name="flowchart_snapshots",
    )
    op.drop_table("flowchart_snapshots")

    op.drop_index(
        "ix_activity_item_statistics_lesson_id",
        table_name="activity_item_statistics",
    )
    op.drop_index(
        "ix_activity_item_statistics_cell_id",
        table_name="activity_item_statistics",
    )
    op.drop_table("activity_item_statistics")

    op.drop_index(
        "ix_activity_submissions_activity_phase",
        table_name="activity_submissions",
    )
    op.drop_column("activity_statistics", "flowchart_metrics")
    op.drop_column("activity_submissions", "activity_phase")
    op.drop_column("activity_submissions", "attempt_no")
    op.drop_column("activity_submissions", "context")
    op.drop_column("activity_submissions", "process_trace")

