"""add lesson classroom assignments

Revision ID: 5a7c9d8b1f23
Revises: 088e21d1e159
Create Date: 2025-11-09 10:15:00.000000+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "5a7c9d8b1f23"
down_revision = "088e21d1e159"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("lesson_classrooms"):
        op.create_table(
            "lesson_classrooms",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("lesson_id", sa.Integer(), nullable=False),
            sa.Column("classroom_id", sa.Integer(), nullable=False),
            sa.Column("assigned_by", sa.Integer(), nullable=True),
            sa.Column(
                "assigned_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.ForeignKeyConstraint(
                ["lesson_id"],
                ["lessons.id"],
                name="fk_lesson_classrooms_lesson_id",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["classroom_id"],
                ["classrooms.id"],
                name="fk_lesson_classrooms_classroom_id",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["assigned_by"],
                ["users.id"],
                name="fk_lesson_classrooms_assigned_by",
                ondelete="SET NULL",
            ),
            sa.UniqueConstraint(
                "lesson_id", "classroom_id", name="uq_lesson_classroom"
            ),
        )

        op.create_index(
            "ix_lesson_classrooms_lesson_id",
            "lesson_classrooms",
            ["lesson_id"],
        )
        op.create_index(
            "ix_lesson_classrooms_classroom_id",
            "lesson_classrooms",
            ["classroom_id"],
        )
        op.create_index(
            "ix_lesson_classrooms_assigned_by",
            "lesson_classrooms",
            ["assigned_by"],
        )


def downgrade() -> None:
    op.drop_index(
        "ix_lesson_classrooms_assigned_by", table_name="lesson_classrooms"
    )
    op.drop_index(
        "ix_lesson_classrooms_classroom_id", table_name="lesson_classrooms"
    )
    op.drop_index("ix_lesson_classrooms_lesson_id", table_name="lesson_classrooms")
    op.drop_table("lesson_classrooms")

