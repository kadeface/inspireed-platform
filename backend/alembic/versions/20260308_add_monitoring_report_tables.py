"""Add monitoring report tables

Revision ID: 20260308_monitoring
Revises: 20260206_add_cell_types
Create Date: 2026-03-08

质量监测报告：支持导入外部统计表（如 25-26学年初中质量监测分校总分综合统计表）
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260308_monitoring"
down_revision: Union[str, None] = "20260206_add_cell_types"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "monitoring_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False, comment="报告名称"),
        sa.Column("academic_year", sa.String(20), nullable=False, comment="学年"),
        sa.Column("semester_type", sa.String(20), nullable=False, comment="学期类型"),
        sa.Column("region_id", sa.Integer(), nullable=True, comment="区县ID"),
        sa.Column("source_file", sa.String(500), nullable=True, comment="原始文件名"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitoring_report_year", "monitoring_reports", ["academic_year"])
    op.create_index("idx_monitoring_report_region", "monitoring_reports", ["region_id"])

    op.create_table(
        "monitoring_report_schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("school_code", sa.String(50), nullable=True, comment="学校代码"),
        sa.Column("school_id", sa.Integer(), nullable=True, comment="学校ID"),
        sa.Column("school_name", sa.String(200), nullable=False, comment="学校名称"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("data_json", sa.JSON(), nullable=True, comment="年级数据JSON"),
        sa.Column("remarks", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["monitoring_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitoring_school_report", "monitoring_report_schools", ["report_id"])


def downgrade() -> None:
    op.drop_index("idx_monitoring_school_report", table_name="monitoring_report_schools")
    op.drop_index("idx_monitoring_report_region", table_name="monitoring_reports")
    op.drop_index("idx_monitoring_report_year", table_name="monitoring_reports")
    op.drop_table("monitoring_reports")
