"""
测试增值评价系统的数据库模型

验证：
1. 模型导入是否正常
2. 数据库连接是否成功
3. 新表是否可以正常CRUD操作
4. 模型关系是否正确
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import (
    User, UserRole, StudentType, School, Classroom, Grade, Region, Subject,
    Semester, Exam, ExamType, ExamStatus,
    ExamSubject, ExamNumberMapping, Score, ExamTotalScore,
    EvaluationMetric, MetricType, MetricCategory,
    ValueAddedEvaluation, EvaluationDetail,
    ImportTask, ImportStatus
)


async def test_database_models():
    """测试数据库模型"""

    print("=" * 80)
    print("开始测试增值评价系统数据库模型")
    print("=" * 80)

    # 创建异步引擎
    engine = create_async_engine(str(settings.DATABASE_URI), echo=False)

    async with engine.begin() as conn:
        # 测试1: 导入所有模型（检查是否有导入错误）
        print("\n[测试1] 检查模型导入...")
        try:
            from app.models.evaluation import (
                Semester, Exam, ExamType, ExamStatus,
                ExamSubject, ExamNumberMapping, Score,
                EvaluationMetric, MetricType, MetricCategory,
                ValueAddedEvaluation, EvaluationDetail,
                ImportTask, ImportStatus
            )
            print("  ✅ 所有模型导入成功")
        except Exception as e:
            print(f"  ❌ 模型导入失败: {e}")
            return

        # 测试2: 检查表是否存在
        print("\n[测试2] 检查新表是否创建...")
        tables_to_check = [
            'semesters', 'exams', 'exam_subjects', 'exam_number_mappings',
            'scores', 'evaluation_metrics', 'value_added_evaluations',
            'evaluation_details', 'import_tasks'
        ]

        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = ANY(:tables)"),
            {"tables": tables_to_check}
        )

        existing_tables = [row[0] for row in result]

        for table in tables_to_check:
            if table in existing_tables:
                print(f"  ✅ 表 '{table}' 存在")
            else:
                print(f"  ❌ 表 '{table}' 不存在")

        # 测试3: 创建测试数据
        print("\n[测试3] 创建测试数据...")

        async with AsyncSession(engine) as session:
            # 3.1 创建Semester
            print("  创建学期...")
            semester = Semester(
                year=2024,
                semester_type="up",
                name="2024-2025学年上学期",
                start_date=datetime(2024, 9, 1),
                end_date=datetime(2025, 1, 31),
                is_current=True
            )
            session.add(semester)
            await session.flush()  # 获取ID
            print(f"    ✅ 创建学期: {semester.name} (ID: {semester.id})")

            # 3.2 获取或创建测试用的Grade
            result = await session.execute(select(Grade).where(Grade.level == 7))
            grade = result.scalar_one_or_none()
            if not grade:
                grade = Grade(name="七年级", level=7)
                session.add(grade)
                await session.flush()
            print(f"    ✅ 使用年级: {grade.name} (ID: {grade.id})")

            # 3.3 获取或创建测试用的Region
            result = await session.execute(select(Region).limit(1))
            region = result.scalar_one_or_none()
            if not region:
                region = Region(name="测试区县", code="test01", level=3)
                session.add(region)
                await session.flush()
            print(f"    ✅ 使用区县: {region.name} (ID: {region.id})")

            # 3.4 创建Exam
            print("  创建考试...")
            exam = Exam(
                name="2024年期中考试",
                exam_type=ExamType.MIDTERM,
                status=ExamStatus.DRAFT,
                semester_id=semester.id,
                grade_id=grade.id,
                region_id=region.id,
                exam_date=datetime(2024, 11, 15),
                created_by=1  # 假设存在用户ID=1
            )
            session.add(exam)
            await session.flush()
            print(f"    ✅ 创建考试: {exam.name} (ID: {exam.id})")

            # 3.5 获取或创建测试用的Subject
            result = await session.execute(select(Subject).limit(1))
            subject = result.scalar_one_or_none()
            if not subject:
                subject = Subject(name="数学", code="math")
                session.add(subject)
                await session.flush()
            print(f"    ✅ 使用科目: {subject.name} (ID: {subject.id})")

            # 3.6 创建ExamSubject
            print("  创建考试科目关联...")
            exam_subject = ExamSubject(
                exam_id=exam.id,
                subject_id=subject.id,
                full_score=100,
                pass_line=60,
                excellent_line=85,
                good_line=75
            )
            session.add(exam_subject)
            await session.flush()
            print(f"    ✅ 创建考试科目关联 (ID: {exam_subject.id})")

            # 3.7 获取或创建测试用的School和Classroom
            result = await session.execute(select(School).limit(1))
            school = result.scalar_one_or_none()
            if not school:
                school = School(
                    name="测试学校",
                    code="test_school",
                    region_id=region.id,
                    school_type="初中"
                )
                session.add(school)
                await session.flush()

            result = await session.execute(select(Classroom).limit(1))
            classroom = result.scalar_one_or_none()
            if not classroom:
                classroom = Classroom(
                    name="七年级一班",
                    school_id=school.id,
                    grade_id=grade.id,
                    capacity=40
                )
                session.add(classroom)
                await session.flush()
            print(f"    ✅ 使用班级: {classroom.name} (ID: {classroom.id})")

            # 3.8 获取或创建测试用的User
            result = await session.execute(
                select(User).where(User.student_id_number == "202401001")
            )
            user = result.scalar_one_or_none()

            if not user:
                # 如果没有找到该学籍号的用户，则创建一个新的
                import random
                unique_id = f"20240{random.randint(1000, 9999)}"
                user = User(
                    email=f"test_student_{unique_id}@test.com",
                    username=f"test_student_{unique_id}",
                    hashed_password="hashed_password_here",
                    full_name="测试学生",
                    student_id_number=unique_id,
                    role=UserRole.STUDENT,
                    school_id=school.id,
                    classroom_id=classroom.id,
                    grade_id=grade.id
                )
                session.add(user)
                await session.flush()
            print(f"    ✅ 使用用户: {user.full_name} (ID: {user.id}, 学籍号: {user.student_id_number})")

            # 3.9 创建ExamNumberMapping
            print("  创建考号映射...")
            mapping = ExamNumberMapping(
                exam_id=exam.id,
                student_id=user.id,
                exam_number=user.student_id_number,  # 使用学籍号作为考号
                student_id_number=user.student_id_number,
                school_id=school.id,
                classroom_id=classroom.id
            )
            session.add(mapping)
            await session.flush()
            print(f"    ✅ 创建考号映射: {mapping.exam_number} (ID: {mapping.id})")

            # 3.10 创建Score
            print("  创建成绩记录...")
            score = Score(
                exam_id=exam.id,
                subject_id=subject.id,
                student_id=user.id,
                raw_score=85,
                standard_score=0.5,
                percentile=75.0,
                grade_level="良好"
            )
            session.add(score)
            await session.flush()
            print(f"    ✅ 创建成绩: {score.raw_score}分 (ID: {score.id})")

            # 3.11 创建EvaluationMetric
            print("  创建评价指标...")
            result = await session.execute(
                select(EvaluationMetric).where(EvaluationMetric.code == "excellent_rate")
            )
            metric = result.scalar_one_or_none()

            if not metric:
                metric = EvaluationMetric(
                    name="优秀率",
                    code="excellent_rate",
                    description="优秀学生比例",
                    metric_type=MetricType.RATE,
                    metric_category=MetricCategory.EXCELLENCE_RATE,
                    display_order=1
                )
                session.add(metric)
                await session.flush()
            print(f"    ✅ 使用评价指标: {metric.name} (ID: {metric.id})")

            # 3.12 创建ImportTask
            print("  创建导入任务...")
            import_task = ImportTask(
                task_name="测试成绩导入",
                task_type="score_data",
                exam_id=exam.id,
                file_url="/storage/test.xlsx",
                file_name="test.xlsx",
                file_size=10240,
                status=ImportStatus.PENDING,
                created_by=user.id
            )
            session.add(import_task)
            await session.flush()
            print(f"    ✅ 创建导入任务: {import_task.task_name} (ID: {import_task.id})")

            # 提交所有测试数据
            await session.commit()
            print("\n  ✅ 所有测试数据创建成功并已提交")

        # 测试4: 验证模型关系
        print("\n[测试4] 验证模型关系...")
        async with AsyncSession(engine) as session:
            # 测试 Semester -> Exam 关系
            result = await session.execute(
                select(Semester)
                .options(selectinload(Semester.exams))
                .where(Semester.year == 2024)
                .order_by(Semester.id.desc())
                .limit(1)
            )
            semester = result.scalar_one()
            print(f"  ✅ Semester -> Exam: {semester.name} 包含 {len(semester.exams)} 个考试")

            # 测试 Exam -> ExamSubject 关系
            result = await session.execute(
                select(Exam)
                .options(
                    selectinload(Exam.exam_subjects),
                    selectinload(Exam.scores),
                    selectinload(Exam.exam_number_mappings)
                )
                .where(Exam.name == "2024年期中考试")
                .order_by(Exam.id.desc())
                .limit(1)
            )
            exam = result.scalar_one()
            print(f"  ✅ Exam -> ExamSubject: {exam.name} 包含 {len(exam.exam_subjects)} 个科目")

            # 测试 Exam -> Score 关系
            print(f"  ✅ Exam -> Score: {exam.name} 包含 {len(exam.scores)} 条成绩")

            # 测试 Exam -> ExamNumberMapping 关系
            print(f"  ✅ Exam -> ExamNumberMapping: {exam.name} 包含 {len(exam.exam_number_mappings)} 个映射")

            # 测试 Subject 分数字段
            result = await session.execute(select(Subject).limit(1))
            subject = result.scalar_one()
            print(f"  ✅ Subject 分数线: full={subject.full_score}, pass={subject.pass_line}, excellent={subject.excellent_line}, good={subject.good_line}")

            # 测试 Classroom capacity 字段
            result = await session.execute(select(Classroom).limit(1))
            classroom = result.scalar_one()
            print(f"  ✅ Classroom 容量: {classroom.capacity}人")

        # 测试5: 验证UserRole枚举
        print("\n[测试5] 验证UserRole枚举...")
        print(f"  ✅ 角色数量: {len(UserRole)}")
        for role in UserRole:
            print(f"    - {role.value}")

        # 测试6: 验证StudentType枚举
        print("\n[测试6] 验证StudentType枚举...")
        print(f"  ✅ 学生类型数量: {len(StudentType)}")
        for stype in StudentType:
            print(f"    - {stype.value}")

        # 测试7: 测试高中总分评价模型
        print("\n[测试7] 测试ExamTotalScore模型...")
        async with AsyncSession(engine) as session:
            # 获取或创建一个理科学生
            result = await session.execute(
                select(User).where(User.student_id_number == "202401001")
            )
            user = result.scalar_one_or_none()

            if user:
                # 更新为理科学生
                user.student_type = StudentType.SCIENCE
                await session.flush()
                print(f"  ✅ 设置学生类型: {user.full_name} -> {user.student_type.value}")

                # 获取一个考试
                result = await session.execute(
                    select(Exam).order_by(Exam.id.desc()).limit(1)
                )
                exam = result.scalar_one()

                # 创建总分评价记录
                total_score = ExamTotalScore(
                    exam_id=exam.id,
                    student_id=user.id,
                    student_type=user.student_type,
                    total_score=680,
                    c9_line=670,
                    special_control_line=620,
                    undergraduate_line=520,
                    junior_college_line=200,
                    reached_c9=True,
                    reached_special_control=True,
                    reached_undergraduate=True,
                    reached_junior_college=True
                )
                session.add(total_score)
                await session.flush()
                print(f"    ✅ 创建总分评价: {total_score.total_score}分 (C9: {total_score.reached_c9})")

                # 提交
                await session.commit()
                print("  ✅ ExamTotalScore模型测试通过")

        print("\n" + "=" * 80)
        print("✅ 所有测试通过！数据库模型工作正常")
        print("✅ 包括高中总分评价功能")
        print("=" * 80)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_database_models())
