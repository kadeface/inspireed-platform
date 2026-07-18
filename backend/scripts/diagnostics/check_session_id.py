"""
测试 sessionId 传递功能
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.activity import ActivitySubmission
from app.models.classroom_session import ClassSession, StudentSessionParticipation


async def run_tests():
    """运行所有测试"""
    print("=" * 80)
    print("🧪 测试 SessionId 传递功能")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 测试1：检查活跃会话
        print("\n📍 测试1：检查活跃会话")
        result = await db.execute(
            select(ClassSession)
            .where(ClassSession.status == 'active')
            .order_by(ClassSession.id.desc())
            .limit(5)
        )
        sessions = result.scalars().all()
        print(f"   活跃会话数: {len(sessions)}")
        for session in sessions:
            print(f"   - Session {session.id}: Lesson {session.lesson_id}, Teacher {session.teacher_id}")
        
        # 测试2：检查学生参与记录
        print("\n📍 测试2：检查学生参与记录")
        result = await db.execute(
            select(StudentSessionParticipation, ClassSession)
            .join(ClassSession)
            .where(ClassSession.status == 'active')
            .limit(10)
        )
        participations = result.all()
        print(f"   参与记录数: {len(participations)}")
        for part, session in participations:
            print(f"   - Student {part.student_id} in Session {part.session_id} (Lesson {session.lesson_id})")
        
        # 测试3：检查最新提交的 session_id
        print("\n📍 测试3：检查最新提交的 session_id")
        result = await db.execute(
            select(ActivitySubmission)
            .order_by(ActivitySubmission.created_at.desc())
            .limit(10)
        )
        submissions = result.scalars().all()
        print(f"   最新提交数: {len(submissions)}")
        
        with_session = 0
        without_session = 0
        
        for sub in submissions:
            status = "✅" if sub.session_id else "❌"
            print(f"   {status} ID {sub.id}: Student {sub.student_id}, Session {sub.session_id or 'NULL'}, Status {sub.status}")
            if sub.session_id:
                with_session += 1
            else:
                without_session += 1
        
        print(f"\n   📊 统计:")
        print(f"      有 session_id: {with_session}")
        print(f"      无 session_id: {without_session}")
        
        if without_session > 0:
            print(f"\n   ⚠️ 发现 {without_session} 条记录没有 session_id")
            print(f"      这可能是:")
            print(f"      1. 课后模式提交（正常）")
            print(f"      2. 旧数据（需要忽略）")
            print(f"      3. 新的bug（需要修复）")
        
        # 测试4：检查推断逻辑需要的数据
        print("\n📍 测试4：检查推断逻辑的数据完整性")
        
        # 找一个活跃的学生参与记录
        result = await db.execute(
            select(StudentSessionParticipation, ClassSession)
            .join(ClassSession)
            .where(ClassSession.status == 'active')
            .limit(1)
        )
        pair = result.first()
        
        if pair:
            part, session = pair
            print(f"   ✅ 找到活跃参与记录:")
            print(f"      Student ID: {part.student_id}")
            print(f"      Session ID: {part.session_id}")
            print(f"      Lesson ID: {session.lesson_id}")
            print(f"      Status: {session.status}")
            
            # 测试推断逻辑
            print(f"\n   🔍 测试推断逻辑（模拟学生 {part.student_id} 在教案 {session.lesson_id} 中提交）")
            result = await db.execute(
                select(StudentSessionParticipation.session_id)
                .join(ClassSession, StudentSessionParticipation.session_id == ClassSession.id)
                .where(
                    StudentSessionParticipation.student_id == part.student_id,
                    ClassSession.lesson_id == session.lesson_id,
                    ClassSession.status == 'active'
                )
                .order_by(ClassSession.id.desc())
                .limit(1)
            )
            inferred_session = result.scalar_one_or_none()
            
            if inferred_session:
                print(f"   ✅ 推断成功！Session ID: {inferred_session}")
                if inferred_session == part.session_id:
                    print(f"   ✅ 推断结果正确！")
                else:
                    print(f"   ⚠️ 推断结果不匹配！预期: {part.session_id}, 实际: {inferred_session}")
            else:
                print(f"   ❌ 推断失败！没有找到匹配的会话")
        else:
            print(f"   ⚠️ 没有活跃的学生参与记录，无法测试推断逻辑")
        
        print("\n" + "=" * 80)
        print("✅ 测试完成！")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_tests())

