"""
为 activity_submissions 表添加 session_id 列
"""

import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def add_session_id_column():
    """添加 session_id 列"""
    async with AsyncSessionLocal() as db:
        try:
            # 检查列是否已存在
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'activity_submissions' 
                AND column_name = 'session_id'
            """)
            
            result = await db.execute(check_query)
            existing = result.scalar_one_or_none()
            
            if existing:
                print("✅ session_id 列已存在")
                return
            
            print("🔧 添加 session_id 列...")
            
            # 添加列
            add_column_query = text("""
                ALTER TABLE activity_submissions 
                ADD COLUMN session_id INTEGER NULL
            """)
            await db.execute(add_column_query)
            
            # 添加外键约束
            add_fk_query = text("""
                ALTER TABLE activity_submissions 
                ADD CONSTRAINT fk_activity_submissions_session_id 
                FOREIGN KEY (session_id) 
                REFERENCES class_sessions(id)
            """)
            await db.execute(add_fk_query)
            
            # 添加索引
            add_index_query = text("""
                CREATE INDEX ix_activity_submissions_session_id 
                ON activity_submissions (session_id)
            """)
            await db.execute(add_index_query)
            
            await db.commit()
            
            print("✅ session_id 列添加成功")
            
        except Exception as e:
            print(f"❌ 添加失败: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


async def main():
    print("🔧 开始添加 session_id 列...")
    await add_session_id_column()


if __name__ == "__main__":
    asyncio.run(main())

