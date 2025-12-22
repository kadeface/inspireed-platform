"""add teacher classrooms table

Revision ID: f7g8h9i0j1k2
Revises: a1b2c3d4e5f6
Create Date: 2025-11-30 22:08:00.000000+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "f7g8h9i0j1k2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("teacher_classrooms"):
        op.create_table(
            "teacher_classrooms",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("teacher_id", sa.Integer(), nullable=False),
            sa.Column("classroom_id", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.ForeignKeyConstraint(
                ["teacher_id"],
                ["users.id"],
                name="fk_teacher_classrooms_teacher_id",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["classroom_id"],
                ["classrooms.id"],
                name="fk_teacher_classrooms_classroom_id",
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint(
                "teacher_id", "classroom_id", name="uq_teacher_classroom"
            ),
        )

        op.create_index(
            "ix_teacher_classrooms_teacher_id",
            "teacher_classrooms",
            ["teacher_id"],
        )
        op.create_index(
            "ix_teacher_classrooms_classroom_id",
            "teacher_classrooms",
            ["classroom_id"],
        )


def downgrade() -> None:
    op.drop_index(
        "ix_teacher_classrooms_classroom_id", table_name="teacher_classrooms"
    )
    op.drop_index("ix_teacher_classrooms_teacher_id", table_name="teacher_classrooms")
    op.drop_table("teacher_classrooms")

