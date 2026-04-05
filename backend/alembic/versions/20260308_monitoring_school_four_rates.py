"""Monitoring report school: one row per semester+school+grade, four rates as columns

Revision ID: 20260308_rates
Revises: 20260308_monitoring
Create Date: 2026-03-08

将 monitoring_report_schools 改为按「学期+学校+年级」一条记录，四率拆成优秀率/优良率/合格率/低分率四个字段。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260308_rates"
down_revision: Union[str, None] = "20260308_monitoring"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("idx_monitoring_school_report", table_name="monitoring_report_schools")
    op.drop_table("monitoring_report_schools")

    op.create_table(
        "monitoring_report_schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("school_code", sa.String(50), nullable=True, comment="学校代码"),
        sa.Column("school_id", sa.Integer(), nullable=True, comment="学校ID"),
        sa.Column("school_name", sa.String(200), nullable=False, comment="学校名称"),
        sa.Column("grade_level", sa.String(20), nullable=False, comment="年级 g7/g8/g9/g3"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("one_point", sa.Float(), nullable=True, comment="一分"),
        sa.Column("excellent_rate", sa.Float(), nullable=True, comment="优秀率"),
        sa.Column("good_rate", sa.Float(), nullable=True, comment="优良率"),
        sa.Column("pass_rate", sa.Float(), nullable=True, comment="合格率"),
        sa.Column("low_rate", sa.Float(), nullable=True, comment="低分率"),
        sa.Column("comprehensive", sa.Float(), nullable=True, comment="综合"),
        sa.Column("score", sa.Float(), nullable=True, comment="得分"),
        sa.Column("rank", sa.Integer(), nullable=True, comment="排名"),
        sa.Column("value_added_score", sa.Float(), nullable=True, comment="增值评价得分"),
        sa.Column("value_added_rank", sa.Integer(), nullable=True, comment="增值评价排名"),
        sa.Column("remarks", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["monitoring_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitoring_school_report", "monitoring_report_schools", ["report_id"])
    op.create_index("idx_monitoring_school_grade", "monitoring_report_schools", ["report_id", "grade_level"])


def downgrade() -> None:
    op.drop_index("idx_monitoring_school_grade", table_name="monitoring_report_schools")
    op.drop_index("idx_monitoring_school_report", table_name="monitoring_report_schools")
    op.drop_table("monitoring_report_schools")

    op.create_table(
        "monitoring_report_schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("school_code", sa.String(50), nullable=True),
        sa.Column("school_id", sa.Integer(), nullable=True),
        sa.Column("school_name", sa.String(200), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("data_json", sa.JSON(), nullable=True),
        sa.Column("remarks", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["monitoring_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitoring_school_report", "monitoring_report_schools", ["report_id"])
