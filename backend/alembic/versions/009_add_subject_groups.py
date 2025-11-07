"""add subject groups system

Revision ID: 009_add_subject_groups
Revises: 008_add_activity_system
Create Date: 2025-11-07

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "009_add_subject_groups"
down_revision = "008_add_activity_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 subject_groups 表
    op.create_table(
        "subject_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, comment="教研组名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="教研组描述"),
        sa.Column("subject_id", sa.Integer(), nullable=False, comment="关联学科"),
        sa.Column(
            "scope",
            sa.Enum("school", "region", "national", name="groupscope"),
            nullable=False,
            comment="教研组范围",
        ),
        sa.Column("school_id", sa.Integer(), nullable=True, comment="关联学校（校级）"),
        sa.Column("region_id", sa.Integer(), nullable=True, comment="关联区域（区域级）"),
        sa.Column("creator_id", sa.Integer(), nullable=False, comment="创建者ID"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", comment="是否激活"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false", comment="是否公开"),
        sa.Column("member_count", sa.Integer(), nullable=False, server_default="1", comment="成员数量"),
        sa.Column("lesson_count", sa.Integer(), nullable=False, server_default="0", comment="共享教案数量"),
        sa.Column("cover_image_url", sa.String(length=500), nullable=True, comment="封面图URL"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subject_groups_id"), "subject_groups", ["id"], unique=False)
    op.create_index(op.f("ix_subject_groups_subject_id"), "subject_groups", ["subject_id"], unique=False)

    # 创建 group_memberships 表
    op.create_table(
        "group_memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False, comment="教研组ID"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "member", name="memberrole"),
            nullable=False,
            server_default="member",
            comment="成员角色",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", comment="是否激活"),
        sa.Column("joined_at", sa.DateTime(), nullable=False, server_default=sa.text("now()"), comment="加入时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["group_id"], ["subject_groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "user_id", name="uq_group_user"),
    )
    op.create_index(op.f("ix_group_memberships_id"), "group_memberships", ["id"], unique=False)
    op.create_index(op.f("ix_group_memberships_group_id"), "group_memberships", ["group_id"], unique=False)
    op.create_index(op.f("ix_group_memberships_user_id"), "group_memberships", ["user_id"], unique=False)

    # 创建 shared_lessons 表
    op.create_table(
        "shared_lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False, comment="教研组ID"),
        sa.Column("lesson_id", sa.Integer(), nullable=False, comment="教案ID"),
        sa.Column("sharer_id", sa.Integer(), nullable=False, comment="分享者ID"),
        sa.Column("share_note", sa.Text(), nullable=True, comment="分享说明"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", comment="是否激活"),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0", comment="查看次数"),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0", comment="下载/复制次数"),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0", comment="点赞数"),
        sa.Column("shared_at", sa.DateTime(), nullable=False, server_default=sa.text("now()"), comment="分享时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["group_id"], ["subject_groups.id"]),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.ForeignKeyConstraint(["sharer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "lesson_id", name="uq_group_lesson"),
    )
    op.create_index(op.f("ix_shared_lessons_id"), "shared_lessons", ["id"], unique=False)
    op.create_index(op.f("ix_shared_lessons_group_id"), "shared_lessons", ["group_id"], unique=False)
    op.create_index(op.f("ix_shared_lessons_lesson_id"), "shared_lessons", ["lesson_id"], unique=False)


def downgrade() -> None:
    # 删除 shared_lessons 表
    op.drop_index(op.f("ix_shared_lessons_lesson_id"), table_name="shared_lessons")
    op.drop_index(op.f("ix_shared_lessons_group_id"), table_name="shared_lessons")
    op.drop_index(op.f("ix_shared_lessons_id"), table_name="shared_lessons")
    op.drop_table("shared_lessons")

    # 删除 group_memberships 表
    op.drop_index(op.f("ix_group_memberships_user_id"), table_name="group_memberships")
    op.drop_index(op.f("ix_group_memberships_group_id"), table_name="group_memberships")
    op.drop_index(op.f("ix_group_memberships_id"), table_name="group_memberships")
    op.drop_table("group_memberships")

    # 删除 subject_groups 表
    op.drop_index(op.f("ix_subject_groups_subject_id"), table_name="subject_groups")
    op.drop_index(op.f("ix_subject_groups_id"), table_name="subject_groups")
    op.drop_table("subject_groups")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS groupscope")
    op.execute("DROP TYPE IF EXISTS memberrole")

