"""
检查学生提交状态的脚本
用于排查"已提交但显示为草稿"的问题
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.activity import ActivitySubmission, ActivitySubmissionStatus
from app.models.user import User


async def check_submissions():
    """检查所有提交的状态"""
    print("=" * 80)
    print("📊 检查活动提交状态")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 查询所有提交
        result = await db.execute(
            select(ActivitySubmission, User)
            .join(User, ActivitySubmission.student_id == User.id)
            .order_by(ActivitySubmission.created_at.desc())
            .limit(20)
        )
        
        submissions = result.all()
        
        if not submissions:
            print("\n❌ 没有找到任何提交记录")
            return
        
        print(f"\n✅ 找到 {len(submissions)} 条最近的提交记录\n")
        
        # 打印表头
        print(f"{'ID':<5} {'学生':<15} {'Cell ID':<8} {'状态':<12} {'分数':<8} {'提交时间':<20}")
        print("-" * 80)
        
        draft_count = 0
        submitted_count = 0
        graded_count = 0
        
        for submission, user in submissions:
            student_name = getattr(user, 'full_name', None) or user.username
            status_str = submission.status.value if submission.status else "unknown"
            score_str = f"{submission.score}/{submission.max_score}" if submission.score is not None else "-"
            submitted_at = submission.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if submission.submitted_at else "-"
            
            # 状态符号
            if submission.status == ActivitySubmissionStatus.DRAFT:
                status_display = "📝 草稿"
                draft_count += 1
            elif submission.status == ActivitySubmissionStatus.SUBMITTED:
                status_display = "✅ 已提交"
                submitted_count += 1
            elif submission.status == ActivitySubmissionStatus.GRADED:
                status_display = "💯 已评分"
                graded_count += 1
            else:
                status_display = f"❓ {status_str}"
            
            print(f"{submission.id:<5} {student_name:<15} {submission.cell_id:<8} {status_display:<12} {score_str:<8} {submitted_at:<20}")
        
        # 统计
        print("\n" + "=" * 80)
        print("📊 统计结果:")
        print(f"   📝 草稿: {draft_count}")
        print(f"   ✅ 已提交: {submitted_count}")
        print(f"   💯 已评分: {graded_count}")
        print("=" * 80)
        
        # 检查异常情况
        print("\n🔍 检查异常情况...")
        
        # 检查：有 submitted_at 但状态是 DRAFT 的记录
        result = await db.execute(
            select(ActivitySubmission, User)
            .join(User, ActivitySubmission.student_id == User.id)
            .where(
                ActivitySubmission.status == ActivitySubmissionStatus.DRAFT,
                ActivitySubmission.submitted_at.isnot(None)
            )
        )
        
        anomalies = result.all()
        
        if anomalies:
            print(f"\n⚠️ 发现 {len(anomalies)} 条异常记录（状态为草稿但有提交时间）:")
            print(f"{'ID':<5} {'学生':<15} {'Cell ID':<8} {'提交时间':<20}")
            print("-" * 80)
            
            for submission, user in anomalies:
                student_name = getattr(user, 'full_name', None) or user.username
                submitted_at = submission.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if submission.submitted_at else "-"
                print(f"{submission.id:<5} {student_name:<15} {submission.cell_id:<8} {submitted_at:<20}")
            
            # 询问是否修复
            print("\n❓ 是否要修复这些异常记录？(y/n): ", end="")
            answer = input().strip().lower()
            
            if answer == 'y':
                await fix_submissions(db, [s[0].id for s, u in anomalies])
        else:
            print("✅ 没有发现异常记录")


async def fix_submissions(db: AsyncSession, submission_ids: list[int]):
    """修复异常提交状态"""
    print(f"\n🔧 开始修复 {len(submission_ids)} 条记录...")
    
    for sub_id in submission_ids:
        submission = await db.get(ActivitySubmission, sub_id)
        if submission and submission.submitted_at:
            submission.status = ActivitySubmissionStatus.SUBMITTED
            print(f"  ✅ 已修复提交 {sub_id} 的状态：草稿 → 已提交")
    
    await db.commit()
    print("\n✅ 修复完成！")


async def check_specific_student(student_id: int):
    """检查特定学生的提交"""
    print(f"\n🔍 检查学生 ID {student_id} 的提交记录...\n")
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ActivitySubmission)
            .where(ActivitySubmission.student_id == student_id)
            .order_by(ActivitySubmission.created_at.desc())
        )
        
        submissions = result.scalars().all()
        
        if not submissions:
            print(f"❌ 学生 {student_id} 没有提交记录")
            return
        
        print(f"✅ 找到 {len(submissions)} 条提交记录\n")
        
        for submission in submissions:
            print(f"提交 ID: {submission.id}")
            print(f"Cell ID: {submission.cell_id}")
            print(f"Lesson ID: {submission.lesson_id}")
            print(f"Session ID: {submission.session_id or '(课后)'}")
            print(f"状态: {submission.status.value}")
            print(f"分数: {submission.score}/{submission.max_score}" if submission.score is not None else "分数: 未评分")
            print(f"开始时间: {submission.started_at}")
            print(f"提交时间: {submission.submitted_at}")
            print(f"创建时间: {submission.created_at}")
            print(f"更新时间: {submission.updated_at}")
            print(f"答案数量: {len(submission.responses) if submission.responses else 0}")
            print("-" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果提供了学生ID参数
        try:
            student_id = int(sys.argv[1])
            asyncio.run(check_specific_student(student_id))
        except ValueError:
            print("❌ 请提供有效的学生ID")
    else:
        # 检查所有提交
        asyncio.run(check_submissions())

