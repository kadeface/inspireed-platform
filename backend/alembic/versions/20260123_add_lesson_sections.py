"""add lesson sections

Revision ID: 20260123_add_lesson_sections
Revises: 20260122_migrate_classroom_codes
Create Date: 2026-01-23 10:00:00.000000

This migration adds Section (大环节) support to lessons.
- Creates sections table
- Adds section_id to cells table
- Migrates existing cells to default "教学过程" section
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260123_add_lesson_sections'
down_revision = '20260122_migrate_classroom_codes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 sectiontype 枚举类型
    op.execute("""
        CREATE TYPE sectiontype AS ENUM ('default', 'custom')
    """)

    # 创建 sections 表
    op.create_table(
        'sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', postgresql.ENUM('default', 'custom', name='sectiontype', create_type=False), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_collapsed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sections_id'), 'sections', ['id'], unique=False)
    op.create_index(op.f('ix_sections_lesson_id'), 'sections', ['lesson_id'], unique=False)

    # 在 cells 表中添加 section_id 字段
    op.add_column('cells', sa.Column('section_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_cells_section_id'), 'cells', ['section_id'], unique=False)
    op.create_foreign_key(
        'fk_cells_section_id',
        'cells', 'sections',
        ['section_id'], ['id'],
        ondelete='SET NULL'
    )

    # 数据迁移：为每个教案创建默认大环节，并将现有 Cell 关联到"教学过程"
    op.execute("""
        -- 为每个教案创建默认大环节
        INSERT INTO sections (lesson_id, name, type, "order", is_collapsed, created_at, updated_at)
        SELECT DISTINCT
            l.id as lesson_id,
            CASE 
                WHEN s.order = 0 THEN '教学目标、教学重点难点、学生学情分析'
                WHEN s.order = 1 THEN '教学过程'
                WHEN s.order = 2 THEN '课堂练习'
                WHEN s.order = 3 THEN '课程资源'
                WHEN s.order = 4 THEN '反思总结'
            END as name,
            'default'::sectiontype as type,
            s.order,
            false as is_collapsed,
            NOW() as created_at,
            NOW() as updated_at
        FROM lessons l
        CROSS JOIN (
            SELECT 0 as "order" UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
        ) s
        ORDER BY l.id, s.order;
    """)

    # 将现有 Cell 关联到"教学过程"大环节（order=1）
    op.execute("""
        UPDATE cells c
        SET section_id = (
            SELECT s.id
            FROM sections s
            WHERE s.lesson_id = c.lesson_id
            AND s.name = '教学过程'
            AND s.type = 'default'
            LIMIT 1
        )
        WHERE c.section_id IS NULL;
    """)


def downgrade() -> None:
    # 移除 cells 表中的 section_id 字段
    op.drop_constraint('fk_cells_section_id', 'cells', type_='foreignkey')
    op.drop_index(op.f('ix_cells_section_id'), table_name='cells')
    op.drop_column('cells', 'section_id')

    # 删除 sections 表
    op.drop_index(op.f('ix_sections_lesson_id'), table_name='sections')
    op.drop_index(op.f('ix_sections_id'), table_name='sections')
    op.drop_table('sections')

    # 删除 sectiontype 枚举类型
    op.execute("DROP TYPE IF EXISTS sectiontype")
