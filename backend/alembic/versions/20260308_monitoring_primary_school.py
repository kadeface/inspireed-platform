"""Add primary school support: report_type, rename g3->g789, add g4/g5/g6/g456

Revision ID: 20260308_primary
Revises: 20260308_wide
Create Date: 2026-03-08

初中：四率+七八九+3级合计(g789)。小学：三率+四五六+3级合计(g456)。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260308_primary"
down_revision: Union[str, None] = "20260308_wide"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. monitoring_reports 添加 report_type
    op.add_column(
        "monitoring_reports",
        sa.Column("report_type", sa.String(20), nullable=True),
    )
    op.execute("UPDATE monitoring_reports SET report_type = 'junior_high' WHERE report_type IS NULL")
    op.alter_column(
        "monitoring_reports",
        "report_type",
        nullable=False,
    )

    # 2. monitoring_report_schools: 重命名 g3_* -> g789_*
    for old, new in [
        ("g3_one_point", "g789_one_point"),
        ("g3_excellent_rate", "g789_excellent_rate"),
        ("g3_good_rate", "g789_good_rate"),
        ("g3_pass_rate", "g789_pass_rate"),
        ("g3_low_rate", "g789_low_rate"),
        ("g3_total_score", "g789_total_score"),
        ("g3_rank", "g789_rank"),
        ("g3_value_added_score", "g789_value_added_score"),
        ("g3_value_added_rank", "g789_value_added_rank"),
    ]:
        op.execute(f'ALTER TABLE monitoring_report_schools RENAME COLUMN "{old}" TO "{new}"')

    # 添加 小学列
    for col, typ in [
        ("g6_one_point", sa.Float()), ("g6_excellent_rate", sa.Float()), ("g6_good_rate", sa.Float()),
        ("g6_pass_rate", sa.Float()), ("g6_comprehensive", sa.Float()), ("g6_score", sa.Float()),
        ("g6_rank", sa.Integer()), ("g6_value_added_score", sa.Float()), ("g6_value_added_rank", sa.Integer()),
        ("g5_one_point", sa.Float()), ("g5_excellent_rate", sa.Float()), ("g5_good_rate", sa.Float()),
        ("g5_pass_rate", sa.Float()), ("g5_comprehensive", sa.Float()), ("g5_score", sa.Float()),
        ("g5_rank", sa.Integer()), ("g5_value_added_score", sa.Float()), ("g5_value_added_rank", sa.Integer()),
        ("g4_one_point", sa.Float()), ("g4_excellent_rate", sa.Float()), ("g4_good_rate", sa.Float()),
        ("g4_pass_rate", sa.Float()), ("g4_comprehensive", sa.Float()), ("g4_score", sa.Float()),
        ("g4_rank", sa.Integer()), ("g4_value_added_score", sa.Float()), ("g4_value_added_rank", sa.Integer()),
        ("g456_one_point", sa.Float()), ("g456_excellent_rate", sa.Float()), ("g456_good_rate", sa.Float()),
        ("g456_pass_rate", sa.Float()), ("g456_total_score", sa.Float()), ("g456_rank", sa.Integer()),
        ("g456_value_added_score", sa.Float()), ("g456_value_added_rank", sa.Integer()),
    ]:
        op.add_column("monitoring_report_schools", sa.Column(col, typ, nullable=True))


def downgrade() -> None:
    for col in [
        "g456_value_added_rank", "g456_value_added_score", "g456_rank", "g456_total_score",
        "g456_pass_rate", "g456_good_rate", "g456_excellent_rate", "g456_one_point",
        "g4_value_added_rank", "g4_value_added_score", "g4_rank", "g4_score", "g4_comprehensive",
        "g4_pass_rate", "g4_good_rate", "g4_excellent_rate", "g4_one_point",
        "g5_value_added_rank", "g5_value_added_score", "g5_rank", "g5_score", "g5_comprehensive",
        "g5_pass_rate", "g5_good_rate", "g5_excellent_rate", "g5_one_point",
        "g6_value_added_rank", "g6_value_added_score", "g6_rank", "g6_score", "g6_comprehensive",
        "g6_pass_rate", "g6_good_rate", "g6_excellent_rate", "g6_one_point",
    ]:
        op.drop_column("monitoring_report_schools", col)

    for new, old in [
        ("g3_value_added_rank", "g789_value_added_rank"),
        ("g3_value_added_score", "g789_value_added_score"),
        ("g3_rank", "g789_rank"),
        ("g3_total_score", "g789_total_score"),
        ("g3_low_rate", "g789_low_rate"),
        ("g3_pass_rate", "g789_pass_rate"),
        ("g3_good_rate", "g789_good_rate"),
        ("g3_excellent_rate", "g789_excellent_rate"),
        ("g3_one_point", "g789_one_point"),
    ]:
        op.execute(f'ALTER TABLE monitoring_report_schools RENAME COLUMN "{old}" TO "{new}"')

    op.drop_column("monitoring_reports", "report_type")
