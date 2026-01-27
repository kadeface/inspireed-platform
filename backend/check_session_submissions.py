"""
检查会话提交记录
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.activity import ActivitySubmission
from app.models.user import User


async def check_session_submissions(cell_id: int = 11, session_id: int = 98):
    """检查特定会话的提交记录"""
    print("=" * 80)
    print(f"📊 检查会话提交记录 (Cell ID: {cell_id}, Session ID: {session_id})")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 查询该Cell的所有提交
        result = await db.execute(
            select(ActivitySubmission, User)
            .join(User, ActivitySubmission.student_id == User.id)
            .where(ActivitySubmission.cell_id == cell_id)
            .order_by(ActivitySubmission.created_at.desc())
        )
        
        submissions = result.all()
        
        print(f"\n✅ 找到 {len(submissions)} 条提交记录\n")
        print(f"{'ID':<5} {'学生':<15} {'状态':<12} {'Session ID':<12} {'提交时间':<20}")
        print("-" * 80)
        
        matching_session_count = 0
        for submission, user in submissions:
            student_name = getattr(user, 'full_name', None) or user.username
            status_str = submission.status.value
            session_id_str = str(submission.session_id) if submission.session_id else "NULL"
            submitted_at = submission.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if submission.submitted_at else "-"
            
            print(f"{submission.id:<5} {student_name:<15} {status_str:<12} {session_id_str:<12} {submitted_at:<20}")
            
            if submission.session_id == session_id:
                matching_session_count += 1
        
        print(f"\n匹配 Session {session_id} 的记录数: {matching_session_count}")
        
        # 检查参与者
        from app.models.classroom_session import StudentSessionParticipation
        
        participants_result = await db.execute(
            select(StudentSessionParticipation, User)
            .join(User, StudentSessionParticipation.student_id == User.id)
            .where(StudentSessionParticipation.session_id == session_id)
        )
        
        participants = participants_result.all()
        
        print(f"\n✅ 会话 {session_id} 的参与者:")
        for participation, user in participants:
            student_name = getattr(user, 'full_name', None) or user.username
            print(f"   - {student_name} (ID: {participation.student_id})")


if __name__ == "__main__":
    cell_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    session_id = int(sys.argv[2]) if len(sys.argv) > 2 else 98
    
    asyncio.run(check_session_submissions(cell_id, session_id))

