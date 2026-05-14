"""add form cells and form_responses tables

Revision ID: 20260514_add_form_cells
Revises: 20260426_image_cell
Create Date: 2026-05-14 00:00:00.000000

Creates tables for interactive form cell functionality:
- form_cells: Stores form configuration and metadata
- form_responses: Stores user responses to form cells
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260514_add_form_cells'
down_revision = '20260426_image_cell'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 form_cells 表
    op.create_table(
        'form_cells',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('project_cell_id', sa.Integer(), nullable=True),
        sa.Column('cell_type', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('options', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('settings', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_cell_id'], ['project_cells.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 为 form_cells 创建索引
    op.create_index(op.f('ix_form_cells_id'), 'form_cells', ['id'], unique=False)
    op.create_index(op.f('ix_form_cells_lesson_id'), 'form_cells', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_form_cells_project_cell_id'), 'form_cells', ['project_cell_id'], unique=False)
    op.create_index(op.f('ix_form_cells_created_by'), 'form_cells', ['created_by'], unique=False)

    # 创建 form_responses 表
    op.create_table(
        'form_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_cell_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('answers', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['form_cell_id'], ['form_cells.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['class_sessions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 为 form_responses 创建索引
    op.create_index(op.f('ix_form_responses_id'), 'form_responses', ['id'], unique=False)
    op.create_index(op.f('ix_form_responses_form_cell_id'), 'form_responses', ['form_cell_id'], unique=False)
    op.create_index(op.f('ix_form_responses_user_id'), 'form_responses', ['user_id'], unique=False)
    op.create_index(op.f('ix_form_responses_session_id'), 'form_responses', ['session_id'], unique=False)


def downgrade() -> None:
    # 删除 form_responses 表及其索引
    op.drop_index(op.f('ix_form_responses_session_id'), table_name='form_responses')
    op.drop_index(op.f('ix_form_responses_user_id'), table_name='form_responses')
    op.drop_index(op.f('ix_form_responses_form_cell_id'), table_name='form_responses')
    op.drop_index(op.f('ix_form_responses_id'), table_name='form_responses')
    op.drop_table('form_responses')

    # 删除 form_cells 表及其索引
    op.drop_index(op.f('ix_form_cells_created_by'), table_name='form_cells')
    op.drop_index(op.f('ix_form_cells_project_cell_id'), table_name='form_cells')
    op.drop_index(op.f('ix_form_cells_lesson_id'), table_name='form_cells')
    op.drop_index(op.f('ix_form_cells_id'), table_name='form_cells')
    op.drop_table('form_cells')