"""Add value added evaluation system

Revision ID: 20260113_1400
Revises: 20251225_2219_4eac54cf4de2
Create Date: 2026-01-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "20260113_1400"
down_revision: Union[str, None] = "4eac54cf4de2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add value added evaluation system tables and modify existing tables"""

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # ========================================
    # Step 1: 扩展UserRole枚举类型
    # ========================================
    print("Step 1: Extending UserRole enum...")

    # PostgreSQL需要特殊处理枚举类型扩展
    # 先获取当前enum值
    user_role_enum_query = sa.text("""
        SELECT enumlabel
        FROM pg_enum
        WHERE enumtypid = (
            SELECT oid FROM pg_type WHERE typname = 'userrole'
        )
    """)
    result = conn.execute(user_role_enum_query)
    existing_roles = [row[0] for row in result]

    # 添加新的角色值
    new_roles = ['district_admin', 'school_admin']
    for role in new_roles:
        if role not in existing_roles:
            alter_stmt = sa.text(f"ALTER TYPE userrole ADD VALUE '{role}'")
            conn.execute(alter_stmt)
            print(f"  Added UserRole: {role}")

    # ========================================
    # Step 2: 修改现有表
    # ========================================
    print("Step 2: Modifying existing tables...")

    # 2.1 修改subjects表 - 添加分数线字段
    if 'subjects' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('subjects')]

        if 'full_score' not in columns:
            op.add_column(
                'subjects',
                sa.Column('full_score', sa.Integer(), nullable=True, server_default='100', comment='满分')
            )
            print("  Added subjects.full_score")

        if 'pass_line' not in columns:
            op.add_column(
                'subjects',
                sa.Column('pass_line', sa.Integer(), nullable=True, server_default='60', comment='及格线')
            )
            print("  Added subjects.pass_line")

        if 'excellent_line' not in columns:
            op.add_column(
                'subjects',
                sa.Column('excellent_line', sa.Integer(), nullable=True, server_default='85', comment='优秀线')
            )
            print("  Added subjects.excellent_line")

        if 'good_line' not in columns:
            op.add_column(
                'subjects',
                sa.Column('good_line', sa.Integer(), nullable=True, server_default='75', comment='良好线')
            )
            print("  Added subjects.good_line")

    # 2.2 修改classrooms表 - 添加capacity字段
    if 'classrooms' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('classrooms')]

        if 'capacity' not in columns:
            op.add_column(
                'classrooms',
                sa.Column('capacity', sa.Integer(), nullable=True, comment='班级容量')
            )
            print("  Added classrooms.capacity")

    # ========================================
    # Step 3: 创建新表
    # ========================================
    print("Step 3: Creating new evaluation system tables...")

    # 3.1 创建semesters表
    op.create_table(
        'semesters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False, comment='学年'),
        sa.Column('semester_type', sa.String(20), nullable=False, comment='学期类型'),
        sa.Column('name', sa.String(50), nullable=False, comment='学期名称'),
        sa.Column('start_date', sa.DateTime(), nullable=False, comment='学期开始日期'),
        sa.Column('end_date', sa.DateTime(), nullable=False, comment='学期结束日期'),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('region_id', sa.Integer(), nullable=True, comment='区县ID'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='学期表'
    )
    op.create_index('ix_semesters_id', 'semesters', ['id'])
    print("  Created table: semesters")

    # 3.2 创建exam_types, exam_statuses等枚举类型（如果使用PostgreSQL native enums）
    # 注意：这里我们使用String类型存储枚举值，在应用层使用Python Enum

    # 3.3 创建exams表
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False, comment='考试名称'),
        sa.Column('exam_type', sa.String(50), nullable=False, comment='考试类型'),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft', comment='考试状态'),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('grade_id', sa.Integer(), nullable=False, comment='年级ID'),
        sa.Column('region_id', sa.Integer(), nullable=True, comment='区县ID'),
        sa.Column('school_id', sa.Integer(), nullable=True, comment='学校ID'),
        sa.Column('exam_date', sa.DateTime(), nullable=False, comment='考试日期'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('statistics', sa.JSON(), nullable=True, comment='考试统计结果'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id']),
        sa.ForeignKeyConstraint(['grade_id'], ['grades.id']),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='考试表'
    )
    op.create_index('ix_exams_id', 'exams', ['id'])
    print("  Created table: exams")

    # 3.4 创建exam_subjects表
    op.create_table(
        'exam_subjects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('full_score', sa.Integer(), nullable=False, server_default='100', comment='满分'),
        sa.Column('pass_line', sa.Integer(), nullable=False, server_default='60', comment='及格线'),
        sa.Column('excellent_line', sa.Integer(), nullable=False, server_default='85', comment='优秀线'),
        sa.Column('good_line', sa.Integer(), nullable=False, server_default='75', comment='良好线'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_id', 'subject_id', name='uq_exam_subject'),
        comment='考试科目关联表'
    )
    print("  Created table: exam_subjects")

    # 3.5 创建exam_number_mappings表
    op.create_table(
        'exam_number_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('exam_number', sa.String(50), nullable=False, comment='考号'),
        sa.Column('student_id_number', sa.String(50), nullable=False, comment='学籍号'),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('classroom_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_id', 'exam_number', name='uq_exam_number'),
        comment='考号映射表'
    )
    op.create_index('idx_exam_student_mapping', 'exam_number_mappings', ['exam_id', 'student_id'])
    print("  Created table: exam_number_mappings")

    # 3.6 创建scores表
    op.create_table(
        'scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('raw_score', sa.Integer(), nullable=False, comment='原始分'),
        sa.Column('standard_score', sa.Float(), nullable=True, comment='标准分'),
        sa.Column('percentile', sa.Float(), nullable=True, comment='百分位'),
        sa.Column('grade_level', sa.String(20), nullable=True, comment='等级'),
        sa.Column('is_absent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_cheated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id']),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('exam_id', 'subject_id', 'student_id', name='uq_exam_subject_student'),
        comment='成绩表'
    )
    op.create_index('idx_exam_subject_score', 'scores', ['exam_id', 'subject_id'])
    op.create_index('idx_student_scores', 'scores', ['student_id'])
    print("  Created table: scores")

    # 3.7 创建evaluation_metrics表
    op.create_table(
        'evaluation_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='指标名称'),
        sa.Column('code', sa.String(50), nullable=False, unique=True, comment='指标代码'),
        sa.Column('description', sa.Text(), nullable=True, comment='指标说明'),
        sa.Column('metric_type', sa.String(50), nullable=False, comment='指标类型'),
        sa.Column('metric_category', sa.String(50), nullable=False, comment='指标分类'),
        sa.Column('calculation_config', sa.JSON(), nullable=True, comment='计算配置'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        comment='评价指标表'
    )
    print("  Created table: evaluation_metrics")

    # 3.8 创建value_added_evaluations表
    op.create_table(
        'value_added_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False, comment='评价名称'),
        sa.Column('region_id', sa.Integer(), nullable=True, comment='区县ID'),
        sa.Column('school_id', sa.Integer(), nullable=True, comment='学校ID'),
        sa.Column('classroom_id', sa.Integer(), nullable=True, comment='班级ID'),
        sa.Column('scope_type', sa.String(20), nullable=False, comment='评价范围类型'),
        sa.Column('baseline_exam_id', sa.Integer(), nullable=False, comment='基线考试ID'),
        sa.Column('endline_exam_id', sa.Integer(), nullable=False, comment='结束考试ID'),
        sa.Column('subject_id', sa.Integer(), nullable=False, comment='科目ID'),
        sa.Column('baseline_value', sa.Float(), nullable=False, comment='基线值'),
        sa.Column('endline_value', sa.Float(), nullable=False, comment='结束值'),
        sa.Column('value_added', sa.Float(), nullable=False, comment='增值量'),
        sa.Column('value_added_rate', sa.Float(), nullable=False, comment='增值率'),
        sa.Column('is_significant', sa.Boolean(), nullable=True, comment='是否显著'),
        sa.Column('p_value', sa.Float(), nullable=True, comment='p值'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['baseline_exam_id'], ['exams.id']),
        sa.ForeignKeyConstraint(['endline_exam_id'], ['exams.id']),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='增值评价结果表'
    )
    op.create_index('idx_evaluation_scope', 'value_added_evaluations', ['scope_type', 'region_id', 'school_id', 'classroom_id'])
    op.create_index('idx_evaluation_exams', 'value_added_evaluations', ['baseline_exam_id', 'endline_exam_id'])
    op.create_index('idx_evaluation_subject', 'value_added_evaluations', ['subject_id'])
    print("  Created table: value_added_evaluations")

    # 3.9 创建evaluation_details表
    op.create_table(
        'evaluation_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('evaluation_id', sa.Integer(), nullable=False),
        sa.Column('metric_id', sa.Integer(), nullable=False),
        sa.Column('scope_type', sa.String(20), nullable=False, comment='层级'),
        sa.Column('scope_id', sa.Integer(), nullable=True, comment='层级ID'),
        sa.Column('baseline_count', sa.Integer(), nullable=False, comment='基线分子数'),
        sa.Column('baseline_total', sa.Integer(), nullable=False, comment='基线分母数'),
        sa.Column('baseline_rate', sa.Float(), nullable=False, comment='基线率'),
        sa.Column('endline_count', sa.Integer(), nullable=False, comment='结束分子数'),
        sa.Column('endline_total', sa.Integer(), nullable=False, comment='结束分母数'),
        sa.Column('endline_rate', sa.Float(), nullable=False, comment='结束率'),
        sa.Column('value_added', sa.Float(), nullable=False, comment='增值量'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['evaluation_id'], ['value_added_evaluations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['metric_id'], ['evaluation_metrics.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evaluation_id', 'metric_id', 'scope_type', 'scope_id', name='uq_evaluation_metric_scope'),
        comment='评价明细表'
    )
    print("  Created table: evaluation_details")

    # 3.10 创建import_tasks表
    op.create_table(
        'import_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(200), nullable=False, comment='任务名称'),
        sa.Column('task_type', sa.String(50), nullable=False, comment='导入类型'),
        sa.Column('exam_id', sa.Integer(), nullable=True, comment='关联考试ID'),
        sa.Column('file_url', sa.String(500), nullable=False, comment='文件URL'),
        sa.Column('file_name', sa.String(200), nullable=False, comment='文件名'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending', comment='任务状态'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0', comment='进度'),
        sa.Column('total_rows', sa.Integer(), nullable=True, comment='总行数'),
        sa.Column('processed_rows', sa.Integer(), nullable=False, server_default='0', comment='已处理行数'),
        sa.Column('failed_rows', sa.Integer(), nullable=False, server_default='0', comment='失败行数'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('error_details', sa.JSON(), nullable=True, comment='错误详情'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='开始时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='导入任务表'
    )
    print("  Created table: import_tasks")

    print("\nMigration completed successfully!")


def downgrade() -> None:
    """Rollback value added evaluation system changes"""

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    print("Rolling back changes...")

    # 按依赖关系逆序删除表
    tables_to_drop = [
        'evaluation_details',
        'value_added_evaluations',
        'evaluation_metrics',
        'import_tasks',
        'scores',
        'exam_number_mappings',
        'exam_subjects',
        'exams',
        'semesters',
    ]

    for table in tables_to_drop:
        if table in inspector.get_table_names():
            op.drop_table(table)
            print(f"  Dropped table: {table}")

    # 删除现有表的修改
    if 'subjects' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('subjects')]

        for field in ['good_line', 'excellent_line', 'pass_line', 'full_score']:
            if field in columns:
                op.drop_column('subjects', field)
                print(f"  Dropped subjects.{field}")

    if 'classrooms' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('classrooms')]

        if 'capacity' in columns:
            op.drop_column('classrooms', 'capacity')
            print(f"  Dropped classrooms.capacity")

    # 回滚UserRole枚举修改（需要手动处理）
    # 注意：PostgreSQL不支持删除枚举值，需要重建类型
    print("\nNote: UserRole enum changes need manual rollback")
    print("The new roles (district_admin, school_admin) will remain in the database")

    print("\nRollback completed!")
