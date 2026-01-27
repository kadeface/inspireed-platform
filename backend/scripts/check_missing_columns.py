"""
检查 activity_submissions 表中缺失的列
"""

import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def check_missing_columns():
    """检查缺失的列"""
    async with AsyncSessionLocal() as db:
        try:
            # 获取表的所有列
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'activity_submissions'
                ORDER BY ordinal_position
            """)
            
            result = await db.execute(check_query)
            existing_columns = [row[0] for row in result.all()]
            
            print("📋 现有列:")
            for col in existing_columns:
                print(f"  - {col}")
            
            # 模型中的列
            model_columns = [
                'id',
                'cell_id',
                'lesson_id',
                'student_id',
                'session_id',
                'responses',
                'score',
                'max_score',
                'auto_graded',
                'status',
                'teacher_feedback',
                'graded_by',
                'started_at',
                'submitted_at',
                'graded_at',
                'submission_count',
                'time_spent',
                'is_late',
                'version',
                'synced',
                'created_at',
                'updated_at',
                'process_trace',
                'context',
                'activity_phase',
                'attempt_no',
            ]
            
            missing_columns = [col for col in model_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"\n⚠️ 缺失的列: {missing_columns}")
            else:
                print("\n✅ 所有列都存在")
            
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            import traceback
            traceback.print_exc()


async def main():
    print("🔍 检查缺失的列...")
    await check_missing_columns()


if __name__ == "__main__":
    asyncio.run(main())

