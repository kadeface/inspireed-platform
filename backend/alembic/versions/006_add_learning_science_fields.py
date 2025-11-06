"""add learning science fields to cells

Revision ID: 006_learning_science
Revises: 005_add_qa_system
Create Date: 2025-11-04

学习科学优化：为 Cell 模型添加认知脚手架支持
- cognitive_level: 基于Bloom分类学的认知层级
- prerequisite_cells: 前置依赖关系
- mastery_criteria: 掌握标准配置
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_learning_science'
down_revision = '005_add_qa_system'
branch_labels = None
depends_on = None


def upgrade():
    # 创建认知层级枚举类型
    cognitive_level_enum = postgresql.ENUM(
        'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create',
        name='cognitivelevel',
        create_type=False
    )
    cognitive_level_enum.create(op.get_bind(), checkfirst=True)
    
    # 添加新字段到 cells 表
    op.add_column('cells', 
        sa.Column('cognitive_level', 
                  sa.Enum('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create', 
                         name='cognitivelevel'),
                  nullable=True,
                  comment='认知层级（基于Bloom分类学）：remember/understand/apply/analyze/evaluate/create'))
    
    op.add_column('cells',
        sa.Column('prerequisite_cells',
                  sa.JSON(),
                  nullable=True,
                  comment='前置依赖的Cell ID列表，例如: [1, 2, 3]'))
    
    op.add_column('cells',
        sa.Column('mastery_criteria',
                  sa.JSON(),
                  nullable=True,
                  comment='掌握标准配置，例如: {"min_attempts": 1, "min_accuracy": 0.8, "max_time_seconds": 300}'))
    
    # 为新字段添加注释（PostgreSQL）
    op.execute("""
        COMMENT ON COLUMN cells.cognitive_level IS 
        '认知层级（Bloom分类学）：remember=记忆, understand=理解, apply=应用, analyze=分析, evaluate=评价, create=创造'
    """)
    
    op.execute("""
        COMMENT ON COLUMN cells.prerequisite_cells IS 
        '前置Cell依赖列表，学生必须先完成这些Cell才能访问当前Cell，支持智能解锁机制'
    """)
    
    op.execute("""
        COMMENT ON COLUMN cells.mastery_criteria IS 
        '掌握标准JSON配置：min_attempts(最小尝试次数), min_accuracy(最低正确率0-1), max_time_seconds(最大完成时间)'
    """)


def downgrade():
    # 移除添加的字段
    op.drop_column('cells', 'mastery_criteria')
    op.drop_column('cells', 'prerequisite_cells')
    op.drop_column('cells', 'cognitive_level')
    
    # 删除枚举类型
    sa.Enum(name='cognitivelevel').drop(op.get_bind(), checkfirst=True)

