"""add classrooms and user scope fields

Revision ID: 088e21d1e159
Revises: f920685b3054
Create Date: 2025-11-08 13:58:11.564077+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "088e21d1e159"
down_revision = "f920685b3054"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("classrooms"):
        op.create_table(
            "classrooms",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("code", sa.String(length=50), nullable=True),
            sa.Column("school_id", sa.Integer(), nullable=False),
            sa.Column("grade_id", sa.Integer(), nullable=False),
            sa.Column("enrollment_year", sa.Integer(), nullable=True),
            sa.Column("head_teacher_id", sa.Integer(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(
                ["school_id"], ["schools.id"], name="fk_classrooms_school_id", ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["grade_id"], ["grades.id"], name="fk_classrooms_grade_id", ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["head_teacher_id"],
                ["users.id"],
                name="fk_classrooms_head_teacher_id",
                ondelete="SET NULL",
            ),
        )

    existing_classroom_indexes = {index["name"] for index in inspector.get_indexes("classrooms")}
    if "ix_classrooms_school_id" not in existing_classroom_indexes:
        op.create_index("ix_classrooms_school_id", "classrooms", ["school_id"])
    if "ix_classrooms_grade_id" not in existing_classroom_indexes:
        op.create_index("ix_classrooms_grade_id", "classrooms", ["grade_id"])
    if "ix_classrooms_is_active" not in existing_classroom_indexes:
        op.create_index("ix_classrooms_is_active", "classrooms", ["is_active"])

    op.add_column("users", sa.Column("region_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("grade_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("classroom_id", sa.Integer(), nullable=True))

    op.create_index("ix_users_region_id", "users", ["region_id"])
    op.create_index("ix_users_grade_id", "users", ["grade_id"])
    op.create_index("ix_users_classroom_id", "users", ["classroom_id"])

    op.create_foreign_key(
        "fk_users_region_id",
        "users",
        "regions",
        ["region_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_users_grade_id",
        "users",
        "grades",
        ["grade_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_users_classroom_id",
        "users",
        "classrooms",
        ["classroom_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_classroom_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_grade_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_region_id", "users", type_="foreignkey")

    op.drop_index("ix_users_classroom_id", table_name="users")
    op.drop_index("ix_users_grade_id", table_name="users")
    op.drop_index("ix_users_region_id", table_name="users")

    op.drop_column("users", "classroom_id")
    op.drop_column("users", "grade_id")
    op.drop_column("users", "region_id")

    op.drop_index("ix_classrooms_is_active", table_name="classrooms")
    op.drop_index("ix_classrooms_grade_id", table_name="classrooms")
    op.drop_index("ix_classrooms_school_id", table_name="classrooms")

    op.drop_table("classrooms")
