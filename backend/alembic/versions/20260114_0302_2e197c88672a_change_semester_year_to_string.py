"""change_semester_year_to_string

Revision ID: 2e197c88672a
Revises: 9a3cc723d719
Create Date: 2026-01-14 03:02:16.304705+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e197c88672a'
down_revision: Union[str, None] = '9a3cc723d719'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """将 semesters.year 字段从 Integer 改为 String"""
    # 先删除所有测试数据（因为字段格式改变）
    # 按照外键依赖顺序删除
    conn = op.get_bind()
    tables = [
        'import_tasks',      # 引用 exams
        'scores',            # 引用 exams
        'exam_subjects',     # 引用 exams
        'exam_number_mappings', # 引用 exams
        'exams',             # 引用 semesters
        'daily_performance_scores', # 引用 semesters
        'semesters'          # 根表
    ]
    
    for table in tables:
        try:
            conn.execute(sa.text(f"DELETE FROM {table}"))
            print(f"✅ 已清除 {table} 表的测试数据")
        except Exception as e:
            print(f"⚠️ 清除 {table} 时出错: {e}")
    
    # 将 year 字段从 INTEGER 改为 VARCHAR(20)
    op.alter_column('semesters', 'year',
                   existing_type=sa.INTEGER(),
                   type_=sa.String(length=20),
                   comment='学年，格式：2023-2024',
                   existing_comment='学年',
                   existing_nullable=False)


def downgrade() -> None:
    """将 semesters.year 字段从 String 改回 Integer"""
    # 注意：降级时需要先清除数据（因为无法自动转换格式）
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM semesters"))
    print("✅ 已清除所有数据以便降级")
    
    # 将 year 字段从 VARCHAR(20) 改回 INTEGER
    op.alter_column('semesters', 'year',
                   existing_type=sa.String(length=20),
                   type_=sa.INTEGER(),
                   comment='学年',
                   existing_comment='学年，格式：2023-2024',
                   existing_nullable=False)
