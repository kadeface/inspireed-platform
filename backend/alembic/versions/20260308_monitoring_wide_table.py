"""Monitoring report school: wide table matching import structure

Revision ID: 20260308_wide
Revises: 20260308_rates
Create Date: 2026-03-08

按导入表结构：每学校一行，列对应Excel（九年级/八年级/七年级/3级 一分四率综合得分排名、增值评价）
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260308_wide"
down_revision: Union[str, None] = "20260308_rates"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("idx_monitoring_school_grade", table_name="monitoring_report_schools")
    op.drop_table("monitoring_report_schools")

    op.create_table(
        "monitoring_report_schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("school_code", sa.String(50), nullable=True),
        sa.Column("school_id", sa.Integer(), nullable=True),
        sa.Column("school_name", sa.String(200), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("g9_one_point", sa.Float(), nullable=True),
        sa.Column("g9_excellent_rate", sa.Float(), nullable=True),
        sa.Column("g9_good_rate", sa.Float(), nullable=True),
        sa.Column("g9_pass_rate", sa.Float(), nullable=True),
        sa.Column("g9_low_rate", sa.Float(), nullable=True),
        sa.Column("g9_comprehensive", sa.Float(), nullable=True),
        sa.Column("g9_score", sa.Float(), nullable=True),
        sa.Column("g9_rank", sa.Integer(), nullable=True),
        sa.Column("g8_one_point", sa.Float(), nullable=True),
        sa.Column("g8_excellent_rate", sa.Float(), nullable=True),
        sa.Column("g8_good_rate", sa.Float(), nullable=True),
        sa.Column("g8_pass_rate", sa.Float(), nullable=True),
        sa.Column("g8_low_rate", sa.Float(), nullable=True),
        sa.Column("g8_comprehensive", sa.Float(), nullable=True),
        sa.Column("g8_score", sa.Float(), nullable=True),
        sa.Column("g8_rank", sa.Integer(), nullable=True),
        sa.Column("g7_one_point", sa.Float(), nullable=True),
        sa.Column("g7_excellent_rate", sa.Float(), nullable=True),
        sa.Column("g7_good_rate", sa.Float(), nullable=True),
        sa.Column("g7_pass_rate", sa.Float(), nullable=True),
        sa.Column("g7_low_rate", sa.Float(), nullable=True),
        sa.Column("g7_comprehensive", sa.Float(), nullable=True),
        sa.Column("g7_score", sa.Float(), nullable=True),
        sa.Column("g7_rank", sa.Integer(), nullable=True),
        sa.Column("g3_one_point", sa.Float(), nullable=True),
        sa.Column("g3_excellent_rate", sa.Float(), nullable=True),
        sa.Column("g3_good_rate", sa.Float(), nullable=True),
        sa.Column("g3_pass_rate", sa.Float(), nullable=True),
        sa.Column("g3_low_rate", sa.Float(), nullable=True),
        sa.Column("g3_total_score", sa.Float(), nullable=True),
        sa.Column("g3_rank", sa.Integer(), nullable=True),
        sa.Column("g9_value_added_score", sa.Float(), nullable=True),
        sa.Column("g9_value_added_rank", sa.Integer(), nullable=True),
        sa.Column("g8_value_added_score", sa.Float(), nullable=True),
        sa.Column("g8_value_added_rank", sa.Integer(), nullable=True),
        sa.Column("g7_value_added_score", sa.Float(), nullable=True),
        sa.Column("g7_value_added_rank", sa.Integer(), nullable=True),
        sa.Column("g3_value_added_score", sa.Float(), nullable=True),
        sa.Column("g3_value_added_rank", sa.Integer(), nullable=True),
        sa.Column("remarks", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["monitoring_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitoring_school_report", "monitoring_report_schools", ["report_id"])


def downgrade() -> None:
    op.drop_index("idx_monitoring_school_report", table_name="monitoring_report_schools")
    op.drop_table("monitoring_report_schools")
    op.create_table(
        "monitoring_report_schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("school_code", sa.String(50), nullable=True),
        sa.Column("school_id", sa.Integer(), nullable=True),
        sa.Column("school_name", sa.String(200), nullable=False),
        sa.Column("grade_level", sa.String(20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("one_point", sa.Float(), nullable=True),
        sa.Column("excellent_rate", sa.Float(), nullable=True),
        sa.Column("good_rate", sa.Float(), nullable=True),
        sa.Column("pass_rate", sa.Float(), nullable=True),
        sa.Column("low_rate", sa.Float(), nullable=True),
        sa.Column("comprehensive", sa.Float(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("value_added_score", sa.Float(), nullable=True),
        sa.Column("value_added_rank", sa.Integer(), nullable=True),
        sa.Column("remarks", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["monitoring_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_monitoring_school_report", "monitoring_report_schools", ["report_id"])
    op.create_index("idx_monitoring_school_grade", "monitoring_report_schools", ["report_id", "grade_level"])
