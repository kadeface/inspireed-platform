"""add_grade_id_to_subject_groups

Revision ID: f920685b3054
Revises: 009_add_subject_groups
Create Date: 2025-11-07 09:12:35.999717+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f920685b3054'
down_revision = '009_add_subject_groups'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 grade_id 字段到 subject_groups 表
    op.add_column(
        'subject_groups',
        sa.Column('grade_id', sa.Integer(), nullable=True, comment='关联年级（可选）')
    )
    # 添加外键约束
    op.create_foreign_key(
        'fk_subject_groups_grade_id',
        'subject_groups',
        'grades',
        ['grade_id'],
        ['id']
    )
    # 添加索引
    op.create_index(
        op.f('ix_subject_groups_grade_id'),
        'subject_groups',
        ['grade_id'],
        unique=False
    )


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f('ix_subject_groups_grade_id'), table_name='subject_groups')
    # 删除外键约束
    op.drop_constraint('fk_subject_groups_grade_id', 'subject_groups', type_='foreignkey')
    # 删除字段
    op.drop_column('subject_groups', 'grade_id')

