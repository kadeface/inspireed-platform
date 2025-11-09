"""add activity system

Revision ID: 008_add_activity_system
Revises: 007_fix_lesson_enum_values
Create Date: 2025-11-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "008_add_activity_system"
down_revision = "007_fix_lesson_enum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 更新 celltype 枚举，添加 activity 和 flowchart
    op.execute("ALTER TYPE celltype ADD VALUE IF NOT EXISTS 'activity'")
    op.execute("ALTER TYPE celltype ADD VALUE IF NOT EXISTS 'flowchart'")

    # 2. 创建活动提交状态枚举（如果不存在）
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE activitysubmissionstatus AS ENUM ('draft', 'submitted', 'graded', 'returned');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # 3. 创建互评状态枚举（如果不存在）
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE peerreviewstatus AS ENUM ('pending', 'in_progress', 'completed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # 4. 创建活动提交表
    op.create_table(
        "activity_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column(
            "responses",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=True),
        sa.Column("auto_graded", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "submitted",
                "graded",
                "returned",
                name="activitysubmissionstatus",
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("teacher_feedback", sa.Text(), nullable=True),
        sa.Column("graded_by", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("graded_at", sa.DateTime(), nullable=True),
        sa.Column("submission_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("time_spent", sa.Integer(), nullable=True),
        sa.Column("is_late", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("synced", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"],
            ["cells.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["graded_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 创建索引
    op.create_index(
        "idx_activity_submissions_cell", "activity_submissions", ["cell_id"]
    )
    op.create_index(
        "idx_activity_submissions_lesson", "activity_submissions", ["lesson_id"]
    )
    op.create_index(
        "idx_activity_submissions_student", "activity_submissions", ["student_id"]
    )
    op.create_index(
        "idx_activity_submissions_status", "activity_submissions", ["status"]
    )
    op.create_index(
        "idx_activity_sub_cell_student",
        "activity_submissions",
        ["cell_id", "student_id"],
    )
    op.create_index(
        "idx_activity_sub_lesson_status",
        "activity_submissions",
        ["lesson_id", "status"],
    )

    # 5. 创建互评表
    op.create_table(
        "peer_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column(
            "review_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", name="peerreviewstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "assigned_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["activity_submissions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"],
            ["cells.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 创建索引
    op.create_index("idx_peer_review_submission", "peer_reviews", ["submission_id"])
    op.create_index("idx_peer_review_reviewer", "peer_reviews", ["reviewer_id"])
    op.create_index("idx_peer_reviews_lesson", "peer_reviews", ["lesson_id"])
    op.create_index("idx_peer_reviews_cell", "peer_reviews", ["cell_id"])

    # 6. 创建活动统计表
    op.create_table(
        "activity_statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("total_students", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("draft_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("submitted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("graded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_score", sa.Float(), nullable=True),
        sa.Column("highest_score", sa.Float(), nullable=True),
        sa.Column("lowest_score", sa.Float(), nullable=True),
        sa.Column("median_score", sa.Float(), nullable=True),
        sa.Column("average_time_spent", sa.Integer(), nullable=True),
        sa.Column(
            "item_statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "peer_review_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("avg_peer_review_score", sa.Float(), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"],
            ["cells.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cell_id"),
    )

    # 创建索引
    op.create_index(
        "idx_activity_statistics_lesson", "activity_statistics", ["lesson_id"]
    )


def downgrade() -> None:
    # 删除表
    op.drop_index("idx_activity_statistics_lesson", table_name="activity_statistics")
    op.drop_table("activity_statistics")

    op.drop_index("idx_peer_reviews_cell", table_name="peer_reviews")
    op.drop_index("idx_peer_reviews_lesson", table_name="peer_reviews")
    op.drop_index("idx_peer_review_reviewer", table_name="peer_reviews")
    op.drop_index("idx_peer_review_submission", table_name="peer_reviews")
    op.drop_table("peer_reviews")

    op.drop_index("idx_activity_sub_lesson_status", table_name="activity_submissions")
    op.drop_index("idx_activity_sub_cell_student", table_name="activity_submissions")
    op.drop_index("idx_activity_submissions_status", table_name="activity_submissions")
    op.drop_index("idx_activity_submissions_student", table_name="activity_submissions")
    op.drop_index("idx_activity_submissions_lesson", table_name="activity_submissions")
    op.drop_index("idx_activity_submissions_cell", table_name="activity_submissions")
    op.drop_table("activity_submissions")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS peerreviewstatus")
    op.execute("DROP TYPE IF EXISTS activitysubmissionstatus")

    # 注意：PostgreSQL 不支持直接删除 ENUM 值，所以我们不回滚 celltype 的修改
    # 如果需要完全回滚，需要重建整个 celltype 枚举
