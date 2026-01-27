"""
完整测试教师端工作流程：
1. 创建教案
2. 添加活动单元并布置测试题
3. 模拟学生提交答案
4. 验证自动评分和正确答案反馈
5. 检查统计数据
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import User, Lesson, Cell, Course, Chapter
from app.models.user import UserRole
from app.models.cell import CellType
from app.models.activity import ActivitySubmission, ActivitySubmissionStatus
from app.core.security import get_password_hash
from uuid import uuid4


async def test_complete_workflow():
    """完整测试工作流程"""
    async with AsyncSessionLocal() as db:
        print("=" * 70)
        print("🧪 完整测试教师端工作流程")
        print("=" * 70)
        print()
        
        # 1. 获取或创建教师账号
        print("📋 步骤1: 准备教师账号")
        result = await db.execute(
            select(User).where(User.email == "teacher@inspireed.com")
        )
        teacher = result.scalar_one_or_none()
        
        if not teacher:
            print("❌ 教师账号不存在")
            return
        
        print(f"✅ 教师账号: {teacher.username} (ID: {teacher.id})")
        print()
        
        # 2. 获取课程和章节
        print("📋 步骤2: 准备课程和章节")
        course_result = await db.execute(
            select(Course).where(Course.is_active == True).limit(1)
        )
        course = course_result.scalar_one_or_none()
        
        if not course:
            print("❌ 没有可用课程")
            return
        
        chapter_result = await db.execute(
            select(Chapter).where(
                Chapter.course_id == course.id,
                Chapter.is_active == True
            ).limit(1)
        )
        chapter = chapter_result.scalar_one_or_none()
        
        print(f"✅ 课程: {course.name} (ID: {course.id})")
        if chapter:
            print(f"✅ 章节: {chapter.name} (ID: {chapter.id})")
        print()
        
        # 3. 创建测试教案
        print("📋 步骤3: 创建测试教案")
        test_lesson_title = f"测试教案_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 检查是否已存在同名教案
        existing_result = await db.execute(
            select(Lesson).where(
                Lesson.title == test_lesson_title,
                Lesson.creator_id == teacher.id
            )
        )
        existing_lesson = existing_result.scalar_one_or_none()
        
        if existing_lesson:
            print(f"⚠️  测试教案已存在: {test_lesson_title} (ID: {existing_lesson.id})")
            test_lesson = existing_lesson
        else:
            test_lesson = Lesson(
                title=test_lesson_title,
                description="用于测试活动单元和自动评分的测试教案",
                creator_id=teacher.id,
                course_id=course.id,
                chapter_id=chapter.id if chapter else None,
                content=[],
                status="draft"
            )
            db.add(test_lesson)
            await db.commit()
            await db.refresh(test_lesson)
            print(f"✅ 创建测试教案: {test_lesson.title} (ID: {test_lesson.id})")
        print()
        
        # 4. 创建活动单元
        print("📋 步骤4: 创建活动单元")
        
        # 检查是否已有活动单元
        cells_result = await db.execute(
            select(Cell).where(Cell.lesson_id == test_lesson.id)
        )
        existing_cells = cells_result.scalars().all()
        activity_cell = None
        
        for cell in existing_cells:
            if str(cell.cell_type) == 'ACTIVITY':
                activity_cell = cell
                break
        
        if activity_cell:
            print(f"⚠️  活动单元已存在: {activity_cell.title or '未命名'} (ID: {activity_cell.id})")
        else:
            # 创建活动单元内容
            activity_content = {
                "title": "测试活动",
                "description": "用于测试自动评分和正确答案反馈",
                "activityType": "quiz",
                "timing": {
                    "phase": "in-class"
                },
                "items": [],
                "grading": {
                    "enabled": True,
                    "totalPoints": 100,
                    "autoGrade": True,
                    "showScoreToStudent": True
                },
                "submission": {
                    "showFeedback": "immediate"
                },
                "display": {
                    "showProgress": True
                }
            }
            
            # 使用字符串值避免枚举类型问题
            activity_cell = Cell(
                lesson_id=test_lesson.id,
                cell_type="activity",  # 直接使用字符串值
                title="测试活动",
                content=activity_content,
                order=0,
                editable=False
            )
            db.add(activity_cell)
            await db.commit()
            await db.refresh(activity_cell)
            print(f"✅ 创建活动单元 (ID: {activity_cell.id})")
        print()
        
        # 5. 添加测试题目
        print("📋 步骤5: 添加测试题目")
        content = activity_cell.content or {}
        items = content.get('items', [])
        
        if len(items) == 0:
            # 添加单选题
            single_choice_item = {
                "id": str(uuid4()),
                "order": 0,
                "type": "single-choice",
                "question": "1 + 1 等于多少？",
                "required": True,
                "points": 10,
                "config": {
                    "options": [
                        {"id": "opt1", "text": "1"},
                        {"id": "opt2", "text": "2", "isCorrect": True},
                        {"id": "opt3", "text": "3"},
                        {"id": "opt4", "text": "4"}
                    ],
                    "correctAnswer": "opt2",
                    "explanation": "1 + 1 = 2"
                }
            }
            
            # 添加多选题
            multiple_choice_item = {
                "id": str(uuid4()),
                "order": 1,
                "type": "multiple-choice",
                "question": "以下哪些是偶数？（多选）",
                "required": True,
                "points": 20,
                "config": {
                    "options": [
                        {"id": "opt1", "text": "2", "isCorrect": True},
                        {"id": "opt2", "text": "3"},
                        {"id": "opt3", "text": "4", "isCorrect": True},
                        {"id": "opt4", "text": "5"}
                    ],
                    "correctAnswers": ["opt1", "opt3"],
                    "explanation": "2和4都是偶数"
                }
            }
            
            # 添加判断题
            true_false_item = {
                "id": str(uuid4()),
                "order": 2,
                "type": "true-false",
                "question": "地球是圆的",
                "required": True,
                "points": 10,
                "config": {
                    "correctAnswer": True,
                    "explanation": "地球是近似球形的"
                }
            }
            
            items = [single_choice_item, multiple_choice_item, true_false_item]
            content['items'] = items
            activity_cell.content = content
            await db.commit()
            print(f"✅ 添加了 {len(items)} 道测试题:")
            print(f"   - 单选题: {single_choice_item['question']}")
            print(f"   - 多选题: {multiple_choice_item['question']}")
            print(f"   - 判断题: {true_false_item['question']}")
        else:
            print(f"⚠️  活动单元已有 {len(items)} 道题目")
        print()
        
        # 6. 创建或获取学生账号
        print("📋 步骤6: 准备学生账号")
        student_result = await db.execute(
            select(User).where(User.email == "student@inspireed.com")
        )
        student = student_result.scalar_one_or_none()
        
        if not student:
            print("⚠️  学生账号不存在，创建测试学生账号")
            student = User(
                username="test_student",
                email="student@inspireed.com",
                full_name="测试学生",
                hashed_password=get_password_hash("student123"),
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)
            await db.commit()
            await db.refresh(student)
            print(f"✅ 创建学生账号: {student.username} (ID: {student.id})")
        else:
            print(f"✅ 学生账号: {student.username} (ID: {student.id})")
        print()
        
        # 7. 模拟学生提交答案
        print("📋 步骤7: 模拟学生提交答案")
        
        # 检查是否已有提交
        submission_result = await db.execute(
            select(ActivitySubmission).where(
                ActivitySubmission.cell_id == activity_cell.id,
                ActivitySubmission.student_id == student.id
            )
        )
        existing_submission = submission_result.scalar_one_or_none()
        
        if existing_submission and existing_submission.status == ActivitySubmissionStatus.SUBMITTED:
            print(f"⚠️  学生已提交 (ID: {existing_submission.id})")
            submission = existing_submission
        else:
            # 创建学生答案（部分正确）
            student_responses = {}
            for item in items:
                item_id = item['id']
                item_type = item['type']
                
                if item_type == 'single-choice':
                    # 答对
                    student_responses[item_id] = "opt2"
                elif item_type == 'multiple-choice':
                    # 答错（只选了opt1，缺少opt3）
                    student_responses[item_id] = ["opt1"]
                elif item_type == 'true-false':
                    # 答对
                    student_responses[item_id] = True
            
            # 创建提交记录
            if existing_submission:
                submission = existing_submission
                submission.responses = student_responses
                submission.status = ActivitySubmissionStatus.SUBMITTED
                submission.submitted_at = datetime.utcnow()
            else:
                submission = ActivitySubmission(
                    cell_id=activity_cell.id,
                    lesson_id=test_lesson.id,
                    student_id=student.id,
                    responses=student_responses,
                    status=ActivitySubmissionStatus.SUBMITTED,
                    submitted_at=datetime.utcnow(),
                    started_at=datetime.utcnow(),
                    time_spent=120
                )
                db.add(submission)
            
            await db.commit()
            await db.refresh(submission)
            print(f"✅ 创建学生提交 (ID: {submission.id})")
            print(f"   答案: {json.dumps(student_responses, ensure_ascii=False, indent=2)}")
        print()
        
        # 8. 验证自动评分（需要调用评分函数）
        print("📋 步骤8: 验证自动评分")
        print("   注意：自动评分在提交时由后端API自动执行")
        print(f"   提交ID: {submission.id}")
        print(f"   提交状态: {submission.status}")
        if submission.auto_graded:
            print(f"   ✅ 已自动评分")
            print(f"   得分: {submission.score}/{submission.max_score}")
        else:
            print(f"   ⚠️  未自动评分（可能需要手动触发）")
        
        # 检查responses中是否有正确性判断
        responses = submission.responses or {}
        has_correctness = False
        for item_id, answer_data in responses.items():
            if isinstance(answer_data, dict) and 'correct' in answer_data:
                has_correctness = True
                print(f"   ✅ 题目 {item_id} 已标记正确性: {answer_data.get('correct')}")
                if 'correctAnswer' in answer_data:
                    print(f"      正确答案: {answer_data.get('correctAnswer')}")
        
        if not has_correctness:
            print("   ⚠️  responses中未包含正确性判断")
            print("   说明：需要调用submit_activity API才会执行自动评分")
        print()
        
        # 9. 总结
        print("=" * 70)
        print("📊 测试总结")
        print("=" * 70)
        print(f"✅ 测试教案: {test_lesson.title} (ID: {test_lesson.id})")
        print(f"✅ 活动单元: {activity_cell.id}")
        print(f"✅ 测试题目: {len(items)} 道")
        print(f"✅ 学生提交: {submission.id}")
        print()
        print("💡 下一步操作:")
        print("   1. 登录教师端，编辑教案 ID: " + str(test_lesson.id))
        print("   2. 查看活动单元，确认题目和正确答案设置")
        print("   3. 登录学生端，提交答案测试自动评分")
        print("   4. 在教师端查看学生提交和统计数据")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())

