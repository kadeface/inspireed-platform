"""add_grade_subject_config_table

Revision ID: 20260118_grade_subject
Revises: add_student_id_number_scores
Create Date: 2026-01-18 22:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260118_grade_subject'
down_revision = 'add_student_id_number_scores'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建年级考试科目配置表
    op.create_table(
        'grade_subject_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grade_id', sa.Integer(), nullable=False, comment='年级ID'),
        sa.Column('subject_id', sa.Integer(), nullable=False, comment='学科ID'),
        sa.Column('full_score', sa.Integer(), nullable=False, default=100, comment='满分'),
        sa.Column('pass_line', sa.Integer(), nullable=False, default=60, comment='及格线'),
        sa.Column('excellent_line', sa.Integer(), nullable=False, default=85, comment='优秀线'),
        sa.Column('good_line', sa.Integer(), nullable=False, default=75, comment='良好线'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, comment='是否启用'),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0, comment='显示顺序'),
        sa.Column('description', sa.String(length=200), nullable=True, comment='备注说明'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_grade_subject_config_creator'),
        sa.ForeignKeyConstraint(['grade_id'], ['grades.id'], name='fk_grade_subject_config_grade'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='fk_grade_subject_config_subject'),
        sa.PrimaryKeyConstraint('id', name='pk_grade_subject_configs'),
        sa.UniqueConstraint('grade_id', 'subject_id', name='uq_grade_subject')
    )
    op.create_index('ix_grade_subject_configs_id', 'grade_subject_configs', ['id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_grade_subject_configs_id', table_name='grade_subject_configs')
    op.drop_table('grade_subject_configs')
