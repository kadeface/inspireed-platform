"""add organization tables

Revision ID: 003_add_organization
Revises: 2f1d0b37129d
Create Date: 2025-10-23

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003_add_organization"
down_revision = "2f1d0b37129d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 regions 表
    op.create_table(
        "regions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False, comment="区域名称"),
        sa.Column("code", sa.String(length=20), nullable=False, comment="区域编码"),
        sa.Column("level", sa.Integer(), nullable=False, comment="区域级别：1-省，2-市，3-区"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父级区域ID"),
        sa.Column("is_active", sa.Boolean(), nullable=True, comment="是否激活"),
        sa.Column("description", sa.Text(), nullable=True, comment="区域描述"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["regions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_regions_id"), "regions", ["id"], unique=False)

    # 创建 schools 表
    op.create_table(
        "schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, comment="学校名称"),
        sa.Column("code", sa.String(length=50), nullable=False, comment="学校编码"),
        sa.Column("region_id", sa.Integer(), nullable=False, comment="所属区域ID"),
        sa.Column(
            "school_type",
            sa.String(length=50),
            nullable=False,
            comment="学校类型：小学、初中、高中、大学等",
        ),
        sa.Column("address", sa.String(length=500), nullable=True, comment="学校地址"),
        sa.Column("phone", sa.String(length=20), nullable=True, comment="联系电话"),
        sa.Column("email", sa.String(length=100), nullable=True, comment="邮箱"),
        sa.Column("principal", sa.String(length=50), nullable=True, comment="校长姓名"),
        sa.Column("is_active", sa.Boolean(), nullable=True, comment="是否激活"),
        sa.Column("description", sa.Text(), nullable=True, comment="学校描述"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["regions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_schools_id"), "schools", ["id"], unique=False)

    # 在 users 表添加 school_id 字段
    op.add_column("users", sa.Column("school_id", sa.Integer(), nullable=True, comment="所属学校ID"))
    op.create_foreign_key("fk_users_school_id", "users", "schools", ["school_id"], ["id"])


def downgrade() -> None:
    # 删除 users 表的 school_id 字段
    op.drop_constraint("fk_users_school_id", "users", type_="foreignkey")
    op.drop_column("users", "school_id")

    # 删除 schools 表
    op.drop_index(op.f("ix_schools_id"), table_name="schools")
    op.drop_table("schools")

    # 删除 regions 表
    op.drop_index(op.f("ix_regions_id"), table_name="regions")
    op.drop_table("regions")
