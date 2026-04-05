"""
快速修复：为班级203创建测试学生
"""
import asyncio
import sys
import os
import bcrypt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def create_test_student():
    """为班级203创建测试学生"""
    async with AsyncSessionLocal() as db:
        print("\n" + "="*80)
        print("🚀 快速修复：为班级203创建测试学生")
        print("="*80)

        # 检查班级203是否存在
        classroom_query = text("""
            SELECT id, name, code, school_id
            FROM classrooms
            WHERE id = 203
        """)
        result = await db.execute(classroom_query)
        classroom = result.fetchone()

        if not classroom:
            print("\n❌ 错误：班级203不存在")
            return

        print(f"\n✅ 找到班级:")
        print(f"   ID: {classroom[0]}")
        print(f"   名称: {classroom[1]}")
        print(f"   代码: {classroom[2]}")
        print(f"   学校ID: {classroom[3]}")

        # 创建测试学生
        print(f"\n➕ 创建测试学生...")

        # 生成正确的 bcrypt 密码哈希
        password = "password123"
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        print(f"   密码哈希: {hashed_password}")

        insert_query = text("""
            INSERT INTO users (username, email, hashed_password, full_name, role, school_id, classroom_id)
            VALUES ('test_student_203', 'test_student_203@example.com', :hashed_password, '测试学生', 'student', 2, 203)
            ON CONFLICT (username) DO UPDATE SET
                classroom_id = 203,
                school_id = 2,
                email = 'test_student_203@example.com',
                hashed_password = :hashed_password
        """)
        await db.execute(insert_query, {"hashed_password": hashed_password})
        await db.commit()

        # 验证创建结果
        verify_query = text("""
            SELECT id, username, full_name, school_id, classroom_id
            FROM users
            WHERE username = 'test_student_203'
        """)
        result = await db.execute(verify_query)
        student = result.fetchone()

        if student:
            print(f"\n✅ 测试学生创建成功！")
            print(f"\n📋 学生信息:")
            print(f"   ID: {student[0]}")
            print(f"   用户名: {student[1]}")
            print(f"   姓名: {student[2]}")
            print(f"   学校ID: {student[3]}")
            print(f"   班级ID: {student[4]}")
            print(f"\n🔐 登录信息:")
            print(f"   用户名: test_student_203")
            print(f"   密码: password123")
            print(f"\n✨ 现在该学生可以:")
            print(f"   1. 登录系统")
            print(f"   2. 打开教师 lzd 在班级203创建的课堂")
            print(f"   3. 成功加入课堂会话")
        else:
            print(f"\n❌ 创建失败")

        # 检查班级203的所有学生
        students_query = text("""
            SELECT COUNT(*) as count
            FROM users
            WHERE classroom_id = 203 AND role = 'student'
        """)
        result = await db.execute(students_query)
        count = result.scalar()

        print(f"\n📊 班级203现在有 {count} 个学生")


if __name__ == "__main__":
    asyncio.run(create_test_student())
