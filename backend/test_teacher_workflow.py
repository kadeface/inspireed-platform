"""
测试教师端工作流程：
1. 创建教案
2. 添加活动单元并布置测试题
3. 查看学生提交和统计数据
4. 使用问答系统
"""

import asyncio
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import User, Lesson, Cell, Course, Chapter, ActivitySubmission, ActivityStatistics
from app.models.user import UserRole
from app.models.cell import CellType
from app.models.activity import ActivitySubmissionStatus


async def test_teacher_workflow():
    """测试教师端工作流程"""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("🧪 开始测试教师端工作流程")
        print("=" * 60)
        print()
        
        # 1. 检查教师账号
        print("📋 步骤1: 检查教师账号")
        result = await db.execute(
            select(User).where(User.email == "teacher@inspireed.com")
        )
        teacher = result.scalar_one_or_none()
        
        if not teacher:
            print("❌ 教师账号不存在，请先运行: python scripts/check_teacher.py")
            return
        
        print(f"✅ 教师账号存在: {teacher.username} (ID: {teacher.id})")
        print()
        
        # 2. 检查是否有课程和章节
        print("📋 步骤2: 检查课程和章节")
        course_result = await db.execute(
            select(Course).where(Course.is_active == True).limit(1)
        )
        course = course_result.scalar_one_or_none()
        
        if not course:
            print("⚠️  没有找到可用课程，需要先创建课程")
            print("   建议：通过前端界面创建课程，或使用课程导入功能")
        else:
            print(f"✅ 找到课程: {course.name} (ID: {course.id})")
            
            chapter_result = await db.execute(
                select(Chapter).where(
                    Chapter.course_id == course.id,
                    Chapter.is_active == True
                ).limit(1)
            )
            chapter = chapter_result.scalar_one_or_none()
            
            if chapter:
                print(f"✅ 找到章节: {chapter.name} (ID: {chapter.id})")
            else:
                print("⚠️  课程下没有章节")
        print()
        
        # 3. 检查教案
        print("📋 步骤3: 检查教案")
        lesson_result = await db.execute(
            select(Lesson).where(Lesson.creator_id == teacher.id).limit(5)
        )
        lessons = lesson_result.scalars().all()
        
        if lessons:
            print(f"✅ 找到 {len(lessons)} 个教案:")
            for lesson in lessons:
                print(f"   - {lesson.title} (ID: {lesson.id}, 状态: {lesson.status})")
        else:
            print("⚠️  教师还没有创建教案")
            print("   建议：通过前端界面创建教案")
        print()
        
        # 4. 检查活动单元
        print("📋 步骤4: 检查活动单元")
        activity_cells = []
        if lessons:
            # 先获取所有cells，然后过滤
            all_cells_result = await db.execute(
                select(Cell).where(
                    Cell.lesson_id.in_([l.id for l in lessons])
                )
            )
            all_cells = all_cells_result.scalars().all()
            activity_cells = [c for c in all_cells if str(c.cell_type) == 'ACTIVITY' or c.cell_type == CellType.ACTIVITY]
            
            if activity_cells:
                print(f"✅ 找到 {len(activity_cells)} 个活动单元:")
                for cell in activity_cells:
                    content = cell.content or {}
                    items = content.get('items', [])
                    print(f"   - {cell.title or '未命名'} (ID: {cell.id}, 题目数: {len(items)})")
                    
                    # 检查是否有正确答案设置
                    for item in items:
                        item_type = item.get('type', '')
                        config = item.get('config', {})
                        if item_type == 'single-choice':
                            correct = config.get('correctAnswer')
                            if correct:
                                print(f"     ✓ 单选题已设置正确答案: {correct}")
                        elif item_type == 'multiple-choice':
                            correct = config.get('correctAnswers', [])
                            if correct:
                                print(f"     ✓ 多选题已设置正确答案: {correct}")
                        elif item_type == 'true-false':
                            correct = config.get('correctAnswer')
                            if correct is not None:
                                print(f"     ✓ 判断题已设置正确答案: {correct}")
            else:
                print("⚠️  教案中没有活动单元")
                print("   建议：在教案编辑页面添加活动单元")
        else:
            print("⚠️  没有教案，无法检查活动单元")
        print()
        
        # 5. 检查学生提交
        print("📋 步骤5: 检查学生提交")
        if lessons:
            submission_result = await db.execute(
                select(ActivitySubmission).where(
                    ActivitySubmission.lesson_id.in_([l.id for l in lessons])
                )
            )
            submissions = submission_result.scalars().all()
            
            if submissions:
                print(f"✅ 找到 {len(submissions)} 个学生提交:")
                
                # 按状态统计
                status_count = {}
                for sub in submissions:
                    status = sub.status.value if hasattr(sub.status, 'value') else str(sub.status)
                    status_count[status] = status_count.get(status, 0) + 1
                
                for status, count in status_count.items():
                    print(f"   - {status}: {count} 个")
                
                # 检查自动评分
                auto_graded = [s for s in submissions if s.auto_graded]
                if auto_graded:
                    print(f"   ✅ {len(auto_graded)} 个提交已自动评分")
                    for sub in auto_graded[:3]:  # 只显示前3个
                        print(f"      - 提交ID {sub.id}: 得分 {sub.score}/{sub.max_score}")
            else:
                print("⚠️  还没有学生提交")
                print("   建议：使用学生账号登录并提交答案")
        else:
            print("⚠️  没有教案，无法检查学生提交")
        print()
        
        # 6. 检查统计数据
        print("📋 步骤6: 检查统计数据")
        stats = []
        if activity_cells:
            stats_result = await db.execute(
                select(ActivityStatistics).where(
                    ActivityStatistics.cell_id.in_([c.id for c in activity_cells])
                )
            )
            stats = stats_result.scalars().all()
            
            if stats:
                print(f"✅ 找到 {len(stats)} 个活动的统计数据:")
                for stat in stats:
                    print(f"   - Cell ID {stat.cell_id}:")
                    print(f"     总学生数: {stat.total_students}")
                    print(f"     已提交: {stat.submitted_count}")
                    print(f"     已评分: {stat.graded_count}")
                    if stat.average_score:
                        print(f"     平均分: {stat.average_score:.2f}")
            else:
                print("⚠️  没有统计数据")
                print("   说明：统计数据在学生提交后自动生成")
        else:
            print("⚠️  没有活动单元，无法检查统计数据")
        print()
        
        # 7. 检查问答系统
        print("📋 步骤7: 检查问答系统")
        from app.models.question import Question
        question_result = await db.execute(
            select(Question).where(Question.lesson_id.in_([l.id for l in lessons]) if lessons else False).limit(5)
        )
        questions = question_result.scalars().all()
        
        if questions:
            print(f"✅ 找到 {len(questions)} 个问题:")
            for q in questions:
                has_answer = q.answers and len(q.answers) > 0
                print(f"   - {q.title[:50]}... (ID: {q.id}, 已回答: {'是' if has_answer else '否'})")
        else:
            print("⚠️  没有找到问题")
            print("   说明：问答系统需要学生提问后才会显示")
        print()
        
        # 总结
        print("=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"✅ 教师账号: 正常")
        print(f"{'✅' if course else '⚠️ '} 课程: {'存在' if course else '需要创建'}")
        print(f"{'✅' if lessons else '⚠️ '} 教案: {len(lessons)} 个")
        print(f"{'✅' if activity_cells else '⚠️ '} 活动单元: {len(activity_cells) if activity_cells else 0} 个")
        print(f"{'✅' if submissions else '⚠️ '} 学生提交: {len(submissions) if submissions else 0} 个")
        print(f"{'✅' if stats else '⚠️ '} 统计数据: {len(stats) if stats else 0} 个")
        print(f"{'✅' if questions else '⚠️ '} 问答记录: {len(questions)} 个")
        print()
        print("💡 建议:")
        if not course:
            print("   1. 先创建课程和章节")
        if not lessons:
            print("   2. 创建教案")
        if not activity_cells:
            print("   3. 在教案中添加活动单元并布置测试题")
        if not submissions:
            print("   4. 使用学生账号提交答案以测试自动评分")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_teacher_workflow())

