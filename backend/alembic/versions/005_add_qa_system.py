"""add qa system tables

Revision ID: 005_add_qa_system
Revises: 004_add_student_enhancement_features
Create Date: 2025-10-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_qa_system'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建问题表
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('cell_id', sa.Integer(), nullable=True),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('ask_type', sa.Enum('teacher', 'ai', 'both', name='asktype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'answered', 'resolved', 'closed', name='questionstatus'), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cell_id'], ['cells.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_lesson_id'), 'questions', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_questions_student_id'), 'questions', ['student_id'], unique=False)
    op.create_index(op.f('ix_questions_status'), 'questions', ['status'], unique=False)
    op.create_index(op.f('ix_questions_created_at'), 'questions', ['created_at'], unique=False)

    # 创建回答表
    op.create_table(
        'answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('answerer_type', sa.Enum('teacher', 'ai', name='answerertype'), nullable=False),
        sa.Column('answerer_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('ai_model', sa.String(length=50), nullable=True),
        sa.Column('ai_prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('ai_completion_tokens', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('is_accepted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['answerer_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_answers_id'), 'answers', ['id'], unique=False)
    op.create_index(op.f('ix_answers_question_id'), 'answers', ['question_id'], unique=False)
    op.create_index(op.f('ix_answers_answerer_id'), 'answers', ['answerer_id'], unique=False)

    # 创建点赞表
    op.create_table(
        'question_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('answer_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_question_votes_id'), 'question_votes', ['id'], unique=False)


def downgrade() -> None:
    # 删除表
    op.drop_index(op.f('ix_question_votes_id'), table_name='question_votes')
    op.drop_table('question_votes')
    
    op.drop_index(op.f('ix_answers_answerer_id'), table_name='answers')
    op.drop_index(op.f('ix_answers_question_id'), table_name='answers')
    op.drop_index(op.f('ix_answers_id'), table_name='answers')
    op.drop_table('answers')
    
    op.drop_index(op.f('ix_questions_created_at'), table_name='questions')
    op.drop_index(op.f('ix_questions_status'), table_name='questions')
    op.drop_index(op.f('ix_questions_student_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_lesson_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    
    # 删除枚举类型
    op.execute('DROP TYPE answerertype')
    op.execute('DROP TYPE questionstatus')
    op.execute('DROP TYPE asktype')

