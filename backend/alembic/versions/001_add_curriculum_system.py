"""Add curriculum system

Revision ID: 001
Revises:
Create Date: 2025-10-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create curriculum tables and add course_id to lessons"""

    # Create subjects table
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_subjects_id"), "subjects", ["id"], unique=False)

    # Create grades table
    op.create_table(
        "grades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("level"),
    )
    op.create_index(op.f("ix_grades_id"), "grades", ["id"], unique=False)

    # Create courses table
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("grade_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["grade_id"],
            ["grades.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subject_id", "grade_id", name="uix_subject_grade"),
    )
    op.create_index(op.f("ix_courses_id"), "courses", ["id"], unique=False)

    # Seed subjects data
    op.execute(
        """
        INSERT INTO subjects (name, code, description, display_order) VALUES
        ('数学', 'math', '数学学科', 1),
        ('物理', 'physics', '物理学科', 2),
        ('化学', 'chemistry', '化学学科', 3),
        ('生物', 'biology', '生物学科', 4),
        ('语文', 'chinese', '语文学科', 5),
        ('英语', 'english', '英语学科', 6),
        ('历史', 'history', '历史学科', 7),
        ('地理', 'geography', '地理学科', 8),
        ('政治', 'politics', '政治学科', 9),
        ('信息技术', 'computer', '信息技术学科', 10)
    """
    )

    # Seed grades data
    op.execute(
        """
        INSERT INTO grades (name, level) VALUES
        ('一年级', 1),
        ('二年级', 2),
        ('三年级', 3),
        ('四年级', 4),
        ('五年级', 5),
        ('六年级', 6),
        ('七年级', 7),
        ('八年级', 8),
        ('九年级', 9),
        ('高一', 10),
        ('高二', 11),
        ('高三', 12)
    """
    )

    # Add course_id column to lessons table (nullable initially for existing data)
    op.add_column("lessons", sa.Column("course_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_lessons_course_id"), "lessons", ["course_id"], unique=False
    )
    op.create_foreign_key(
        "fk_lessons_course_id", "lessons", "courses", ["course_id"], ["id"]
    )


def downgrade() -> None:
    """Remove curriculum tables and course_id from lessons"""

    # Remove course_id from lessons
    op.drop_constraint("fk_lessons_course_id", "lessons", type_="foreignkey")
    op.drop_index(op.f("ix_lessons_course_id"), table_name="lessons")
    op.drop_column("lessons", "course_id")

    # Drop courses table
    op.drop_index(op.f("ix_courses_id"), table_name="courses")
    op.drop_table("courses")

    # Drop grades table
    op.drop_index(op.f("ix_grades_id"), table_name="grades")
    op.drop_table("grades")

    # Drop subjects table
    op.drop_index(op.f("ix_subjects_id"), table_name="subjects")
    op.drop_table("subjects")
