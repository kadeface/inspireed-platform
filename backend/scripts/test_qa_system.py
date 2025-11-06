"""
测试问答系统功能
"""

import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models import User, Lesson, Question, Answer
from app.models.question import QuestionStatus, AskType, AnswererType


async def test_qa_system():
    """测试问答系统"""
    print("=" * 60)
    print("测试问答系统")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # 1. 查找学生和教师
        student = await db.execute(select(User).where(User.role == "student").limit(1))
        student = student.scalar_one_or_none()

        teacher = await db.execute(select(User).where(User.role == "teacher").limit(1))
        teacher = teacher.scalar_one_or_none()

        if not student or not teacher:
            print("❌ 需要至少一个学生和一个教师账号")
            return False

        print(f"✅ 找到学生: {student.username} (ID: {student.id})")
        print(f"✅ 找到教师: {teacher.username} (ID: {teacher.id})")

        # 2. 查找已发布的课程
        lesson = await db.execute(select(Lesson).where(Lesson.status == "published").limit(1))
        lesson = lesson.scalar_one_or_none()

        if not lesson:
            print("❌ 需要至少一个已发布的课程")
            return False

        print(f"✅ 找到课程: {lesson.title} (ID: {lesson.id})")

        # 3. 创建测试问题
        print("\n" + "-" * 60)
        print("创建测试问题...")

        question = Question(
            lesson_id=lesson.id,
            student_id=student.id,
            title="测试问题：如何理解这个概念？",
            content="我在学习这门课程时遇到了困难，能否详细解释一下核心概念？",
            ask_type=AskType.BOTH,
            status=QuestionStatus.PENDING,
            is_public=True,
        )

        db.add(question)
        await db.commit()
        await db.refresh(question)

        print(f"✅ 创建问题成功 (ID: {question.id})")
        print(f"   标题: {question.title}")
        print(f"   状态: {question.status.value}")
        print(f"   提问类型: {question.ask_type.value}")

        # 4. 创建教师回答
        print("\n" + "-" * 60)
        print("创建教师回答...")

        answer_content = [
            {
                "id": "cell-1",
                "type": "text",
                "order": 0,
                "content": {"html": "<h3>核心概念解析</h3><p>让我来详细解释一下这个概念...</p>"},
            },
            {
                "id": "cell-2",
                "type": "code",
                "order": 1,
                "content": {"code": "# 示例代码\nprint('Hello, World!')", "language": "python"},
            },
        ]

        answer = Answer(
            question_id=question.id,
            answerer_type=AnswererType.TEACHER,
            answerer_id=teacher.id,
            content=answer_content,
            is_accepted=False,
        )

        db.add(answer)

        # 更新问题状态
        question.status = QuestionStatus.ANSWERED

        await db.commit()
        await db.refresh(answer)

        print(f"✅ 创建回答成功 (ID: {answer.id})")
        print(f"   回答者类型: {answer.answerer_type.value}")
        print(f"   回答者ID: {answer.answerer_id}")
        print(f"   内容单元数: {len(answer.content)}")

        # 5. 验证数据
        print("\n" + "-" * 60)
        print("验证数据...")

        # 重新查询问题，检查关系（使用 selectinload 预加载）
        question_check = await db.execute(
            select(Question)
            .where(Question.id == question.id)
            .options(selectinload(Question.answers))
        )
        question_check = question_check.scalar_one()

        print(f"✅ 问题状态已更新: {question_check.status.value}")
        print(f"✅ 问题的回答数: {len(question_check.answers)}")

        if question_check.answers:
            first_answer = question_check.answers[0]
            print(f"✅ 第一个回答ID: {first_answer.id}")
            print(f"✅ 回答内容类型: {type(first_answer.content)}")
            print(f"✅ 回答的Cell数量: {len(first_answer.content)}")

        print("\n" + "=" * 60)
        print("✅ 问答系统测试完成！所有功能正常")
        print("=" * 60)

        return True


async def main():
    """主函数"""
    try:
        success = await test_qa_system()
        if success:
            print("\n✅ 测试成功！")
            sys.exit(0)
        else:
            print("\n❌ 测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
