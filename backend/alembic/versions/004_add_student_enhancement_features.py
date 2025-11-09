"""
添加学生端增强功能表
- 收藏表 (favorites)
- 评论评分表 (reviews)
- 学习路径表 (learning_paths, learning_path_lessons)
- Lesson表添加难度和评分字段

Revision ID: 004
Revises: 003
Create Date: 2025-10-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003_add_organization"
branch_labels = None
depends_on = None


def upgrade():
    """升级"""
    # 创建收藏表
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("lesson_id", sa.Integer(), nullable=False, comment="课程ID"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="收藏时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
        sa.UniqueConstraint("user_id", "lesson_id", name="unique_user_lesson_favorite"),
    )
    op.create_index(op.f("ix_favorites_id"), "favorites", ["id"], unique=False)

    # 创建评论评分表
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("lesson_id", sa.Integer(), nullable=False, comment="课程ID"),
        sa.Column("rating", sa.Integer(), nullable=False, comment="评分（1-5）"),
        sa.Column("comment", sa.Text(), nullable=True, comment="评论内容"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        sa.UniqueConstraint("user_id", "lesson_id", name="unique_user_lesson_review"),
    )
    op.create_index(op.f("ix_reviews_id"), "reviews", ["id"], unique=False)

    # 创建学习路径表
    op.create_table(
        "learning_paths",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False, comment="路径标题"),
        sa.Column("description", sa.Text(), nullable=True, comment="路径描述"),
        sa.Column("creator_id", sa.Integer(), nullable=False, comment="创建者ID"),
        sa.Column(
            "difficulty_level",
            sa.Enum("beginner", "intermediate", "advanced", name="difficultylevel"),
            nullable=False,
            comment="难度等级",
        ),
        sa.Column(
            "cover_image_url", sa.String(length=500), nullable=True, comment="封面图URL"
        ),
        sa.Column("is_published", sa.Boolean(), nullable=False, comment="是否已发布"),
        sa.Column("estimated_hours", sa.Integer(), nullable=True, comment="预计学习时长（小时）"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
        ),
    )
    op.create_index(
        op.f("ix_learning_paths_id"), "learning_paths", ["id"], unique=False
    )

    # 创建学习路径课程关联表
    op.create_table(
        "learning_path_lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("learning_path_id", sa.Integer(), nullable=False, comment="学习路径ID"),
        sa.Column("lesson_id", sa.Integer(), nullable=False, comment="课程ID"),
        sa.Column("order_index", sa.Integer(), nullable=False, comment="顺序索引"),
        sa.Column("is_required", sa.Boolean(), nullable=False, comment="是否必修"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["learning_path_id"],
            ["learning_paths.id"],
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
    )
    op.create_index(
        op.f("ix_learning_path_lessons_id"),
        "learning_path_lessons",
        ["id"],
        unique=False,
    )

    # 给Lesson表添加新字段
    op.add_column(
        "lessons",
        sa.Column(
            "difficulty_level",
            sa.Enum("beginner", "intermediate", "advanced", name="difficultylevel"),
            nullable=True,
            comment="难度等级",
        ),
    )
    op.add_column(
        "lessons",
        sa.Column(
            "average_rating",
            sa.Float(),
            nullable=False,
            server_default="0.0",
            comment="平均评分",
        ),
    )
    op.add_column(
        "lessons",
        sa.Column(
            "review_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="评论数量",
        ),
    )


def downgrade():
    """降级"""
    # 删除Lesson表新增字段
    op.drop_column("lessons", "review_count")
    op.drop_column("lessons", "average_rating")
    op.drop_column("lessons", "difficulty_level")

    # 删除学习路径课程关联表
    op.drop_index(
        op.f("ix_learning_path_lessons_id"), table_name="learning_path_lessons"
    )
    op.drop_table("learning_path_lessons")

    # 删除学习路径表
    op.drop_index(op.f("ix_learning_paths_id"), table_name="learning_paths")
    op.drop_table("learning_paths")

    # 删除评论评分表
    op.drop_index(op.f("ix_reviews_id"), table_name="reviews")
    op.drop_table("reviews")

    # 删除收藏表
    op.drop_index(op.f("ix_favorites_id"), table_name="favorites")
    op.drop_table("favorites")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS difficultylevel")
