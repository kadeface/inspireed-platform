"""
创建测试数据
包括：章节、资源（PDF）、示例教案
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import (
    Subject,
    Grade,
    Course,
    Chapter,
    Resource,
    User,
    Lesson,
    LessonStatus,
)


async def create_test_data():
    """创建测试数据"""

    async with AsyncSessionLocal() as db:
        print("🚀 开始创建测试数据...")

        # 1. 获取或创建测试教师用户
        print("\n1️⃣ 检查测试用户...")
        result = await db.execute(select(User).where(User.email == "teacher@test.com"))
        teacher = result.scalar_one_or_none()

        if not teacher:
            from app.core.security import get_password_hash
            from app.models import UserRole

            teacher = User(
                email="teacher@test.com",
                username="testteacher",
                full_name="测试教师",
                hashed_password=get_password_hash("password123"),
                role=UserRole.TEACHER,
                is_active=True,
            )
            db.add(teacher)
            await db.commit()
            await db.refresh(teacher)
            print(f"   ✓ 创建测试教师: {teacher.email}")
        else:
            print(f"   ✓ 测试教师已存在: {teacher.email}")

        # 2. 获取数学学科和高一年级
        print("\n2️⃣ 获取学科和年级...")
        result = await db.execute(select(Subject).where(Subject.code == "math"))
        math_subject = result.scalar_one_or_none()

        result = await db.execute(select(Grade).where(Grade.level == 10))
        grade_10 = result.scalar_one_or_none()

        if not math_subject or not grade_10:
            print("   ❌ 请先运行数据库迁移和初始化数据")
            return

        print(f"   ✓ 学科: {math_subject.name}")
        print(f"   ✓ 年级: {grade_10.name}")

        # 3. 获取或创建课程
        print("\n3️⃣ 检查课程...")
        result = await db.execute(
            select(Course).where(
                Course.subject_id == math_subject.id, Course.grade_id == grade_10.id
            )
        )
        course = result.scalar_one_or_none()

        if not course:
            course = Course(
                subject_id=math_subject.id,
                grade_id=grade_10.id,
                name=f"{grade_10.name}{math_subject.name}",
                code=f"grade{grade_10.level}-{math_subject.code}",
                description=f"{grade_10.name}的{math_subject.name}课程",
                is_active=True,
            )
            db.add(course)
            await db.commit()
            await db.refresh(course)
            print(f"   ✓ 创建课程: {course.name}")
        else:
            print(f"   ✓ 课程已存在: {course.name}")

        # 4. 创建章节
        print("\n4️⃣ 创建章节...")
        result = await db.execute(
            select(Chapter).where(
                Chapter.course_id == course.id, Chapter.code == "chapter-1"
            )
        )
        chapter1 = result.scalar_one_or_none()

        if not chapter1:
            chapter1 = Chapter(
                course_id=course.id,
                name="第一章：集合与函数",
                code="chapter-1",
                description="介绍集合的基本概念和运算",
                display_order=1,
                is_active=True,
            )
            db.add(chapter1)
            await db.commit()
            await db.refresh(chapter1)
            print(f"   ✓ 创建章节: {chapter1.name}")
        else:
            print(f"   ✓ 章节已存在: {chapter1.name}")

        # 创建子章节
        result = await db.execute(
            select(Chapter).where(
                Chapter.course_id == course.id, Chapter.code == "section-1-1"
            )
        )
        section1_1 = result.scalar_one_or_none()

        if not section1_1:
            section1_1 = Chapter(
                course_id=course.id,
                parent_id=chapter1.id,
                name="1.1 集合的概念",
                code="section-1-1",
                description="学习集合的定义和表示方法",
                display_order=1,
                is_active=True,
            )
            db.add(section1_1)
            await db.commit()
            await db.refresh(section1_1)
            print(f"   ✓ 创建小节: {section1_1.name}")
        else:
            print(f"   ✓ 小节已存在: {section1_1.name}")

        # 5. 创建 PDF 资源
        print("\n5️⃣ 创建 PDF 资源...")
        result = await db.execute(
            select(Resource).where(
                Resource.chapter_id == section1_1.id, Resource.title.like("%教学设计%")
            )
        )
        pdf_resource = result.scalar_one_or_none()

        if not pdf_resource:
            pdf_resource = Resource(
                chapter_id=section1_1.id,
                title="集合的概念 - 教学设计",
                description="官方标准教学设计文档，包含教学目标、重点难点、教学过程等内容",
                resource_type="pdf",
                file_url="/uploads/resources/sample_lesson_design.pdf",  # 模拟文件URL
                file_size=2 * 1024 * 1024,  # 2MB
                page_count=8,
                thumbnail_url="/uploads/thumbnails/sample_lesson_design.png",
                is_official=True,
                is_downloadable=True,
                is_active=True,
                display_order=1,
                created_by=teacher.id,
            )
            db.add(pdf_resource)
            await db.commit()
            await db.refresh(pdf_resource)
            print(f"   ✓ 创建 PDF 资源: {pdf_resource.title}")
        else:
            print(f"   ✓ PDF 资源已存在: {pdf_resource.title}")

        # 创建视频资源
        result = await db.execute(
            select(Resource).where(
                Resource.chapter_id == section1_1.id, Resource.resource_type == "video"
            )
        )
        video_resource = result.scalar_one_or_none()

        if not video_resource:
            video_resource = Resource(
                chapter_id=section1_1.id,
                title="集合的概念 - 讲解视频",
                description="集合概念的详细讲解，时长约15分钟",
                resource_type="video",
                file_url="/uploads/resources/sample_lesson_video.mp4",
                file_size=50 * 1024 * 1024,  # 50MB
                is_official=True,
                is_downloadable=False,
                is_active=True,
                display_order=2,
                created_by=teacher.id,
            )
            db.add(video_resource)
            await db.commit()
            await db.refresh(video_resource)
            print(f"   ✓ 创建视频资源: {video_resource.title}")
        else:
            print(f"   ✓ 视频资源已存在: {video_resource.title}")

        # 6. 创建示例教案
        print("\n6️⃣ 创建示例教案...")
        result = await db.execute(
            select(Lesson).where(
                Lesson.creator_id == teacher.id, Lesson.title.like("%集合的概念%")
            )
        )
        sample_lesson = result.scalar_one_or_none()

        if not sample_lesson:
            sample_lesson = Lesson(
                title="集合的概念 - 高一(1)班",
                description="基于官方教学设计，结合本班学生实际情况设计的交互式教案",
                creator_id=teacher.id,
                course_id=course.id,
                reference_resource_id=pdf_resource.id,
                reference_notes="""
参考笔记：
1. PDF中的教学目标非常清晰，可以直接使用
2. 重点关注第3节的实例讲解，需要增加更多贴近学生生活的例子
3. 教学过程建议增加互动环节，使用代码演示加深理解
4. 最后的练习题可以适当增加难度
                """.strip(),
                tags=["集合", "高一", "交互式"],
                estimated_duration=45,
                content=[
                    {
                        "id": "cell-1",
                        "type": "text",
                        "order": 0,
                        "title": "课程导入",
                        "editable": True,
                        "cognitive_level": "remember",
                        "prerequisite_cells": [],
                        "mastery_criteria": {
                            "min_attempts": 1,
                            "min_accuracy": 0.6,
                            "max_time_seconds": 180,
                        },
                        "content": {
                            "html": "<h2>一、课程导入</h2><p>通过日常生活中的例子引入集合的概念...</p><p>🎯 学习目标：了解集合的基本概念</p>"
                        },
                    },
                    {
                        "id": "cell-2",
                        "type": "text",
                        "order": 1,
                        "title": "集合的定义",
                        "editable": False,
                        "cognitive_level": "understand",
                        "prerequisite_cells": ["cell-1"],
                        "mastery_criteria": {
                            "min_attempts": 1,
                            "min_accuracy": 0.7,
                            "max_time_seconds": 300,
                        },
                        "content": {
                            "html": "<h3>二、集合的定义</h3><p>集合是由确定的不同的对象组成的整体。</p><p>📚 关键概念：确定性、互异性、无序性</p>"
                        },
                    },
                    {
                        "id": "cell-3",
                        "type": "code",
                        "order": 2,
                        "title": "Python集合演示",
                        "editable": True,
                        "cognitive_level": "apply",
                        "prerequisite_cells": ["cell-1", "cell-2"],
                        "mastery_criteria": {
                            "min_attempts": 2,
                            "min_accuracy": 0.8,
                            "max_time_seconds": 600,
                        },
                        "content": {
                            "code": "# Python 集合演示\nstudents = {'张三', '李四', '王五'}\nprint(f'班级人数: {len(students)}')\n\n# 添加新成员\nstudents.add('赵六')\nprint(f'添加后: {students}')",
                            "language": "python",
                        },
                        "config": {"environment": "jupyterlite"},
                    },
                    {
                        "id": "cell-4",
                        "type": "text",
                        "order": 3,
                        "title": "集合的应用",
                        "editable": False,
                        "cognitive_level": "analyze",
                        "prerequisite_cells": ["cell-2", "cell-3"],
                        "mastery_criteria": {
                            "min_attempts": 1,
                            "min_accuracy": 0.75,
                            "max_time_seconds": 420,
                        },
                        "content": {
                            "html": "<h3>三、集合的实际应用</h3><p>分析集合在数据去重、成员检查等场景中的应用。</p><p>💡 思考：为什么使用集合而不是列表？</p>"
                        },
                    },
                    {
                        "id": "cell-5",
                        "type": "code",
                        "order": 4,
                        "title": "集合操作练习",
                        "editable": True,
                        "cognitive_level": "create",
                        "prerequisite_cells": ["cell-3", "cell-4"],
                        "mastery_criteria": {
                            "min_attempts": 3,
                            "min_accuracy": 0.85,
                            "max_time_seconds": 900,
                        },
                        "content": {
                            "code": "# 创建性练习：设计一个使用集合解决实际问题的程序\n# 任务：编写代码找出两个班级的共同学生\n\nclass_a = {'张三', '李四', '王五', '赵六'}\nclass_b = {'李四', '王五', '钱七', '孙八'}\n\n# 请完成以下代码\ncommon_students = # 你的代码\nprint(f'共同学生: {common_students}')",
                            "language": "python",
                        },
                        "config": {
                            "environment": "jupyterlite",
                            "test_cases": [
                                {"input": "", "expected_output": "共同学生: {'李四', '王五'}"}
                            ],
                        },
                    },
                ],
                cell_count=5,
                status=LessonStatus.DRAFT,
            )
            db.add(sample_lesson)
            await db.commit()
            await db.refresh(sample_lesson)
            print(f"   ✓ 创建示例教案: {sample_lesson.title}")
        else:
            print(f"   ✓ 示例教案已存在: {sample_lesson.title}")

        print("\n✅ 测试数据创建完成！")
        print(f"\n📊 数据摘要:")
        print(f"   - 学科: {math_subject.name}")
        print(f"   - 年级: {grade_10.name}")
        print(f"   - 课程: {course.name}")
        print(f"   - 章节: {chapter1.name}")
        print(f"   - 小节: {section1_1.name}")
        print(f"   - PDF 资源: {pdf_resource.title}")
        print(f"   - 视频资源: {video_resource.title}")
        print(f"   - 示例教案: {sample_lesson.title}")
        print(f"\n🔑 测试账号:")
        print(f"   邮箱: teacher@test.com")
        print(f"   密码: password123")


if __name__ == "__main__":
    asyncio.run(create_test_data())
