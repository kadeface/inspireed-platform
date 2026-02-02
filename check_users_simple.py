"""
使用原始 SQL 查询避免 enum 错误
"""
import asyncio
import sys
import os

# 添加后端路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def check_with_raw_sql():
    """使用原始 SQL 查询"""
    async with AsyncSessionLocal() as db:
        print("\n" + "="*60)
        print("📋 用户基本信息")
        print("="*60)

        # 查询用户基本信息
        query = text("""
            SELECT
                u.id,
                u.username,
                u.role,
                u.full_name,
                u.email,
                u.school_id,
                u.classroom_id
            FROM users u
            WHERE u.username IN ('lzd', '2025400')
            ORDER BY u.role
        """)

        result = await db.execute(query)
        users = result.fetchall()

        teacher = None
        student = None

        for user in users:
            user_dict = dict(user._mapping)
            if user_dict['role'] == 'teacher':
                teacher = user_dict
            elif user_dict['role'] == 'student':
                student = user_dict

        if not teacher or not student:
            print("❌ 错误：未找到教师或学生")
            return

        print(f"\n👨‍🏫 教师：{teacher['username']}")
        print(f"   ID: {teacher['id']}")
        print(f"   全名: {teacher['full_name'] or '未设置'}")
        print(f"   学校ID: {teacher['school_id']}")
        print(f"   班级ID (User表): {teacher['classroom_id']}")

        print(f"\n👨‍🎓 学生：{student['username']}")
        print(f"   ID: {student['id']}")
        print(f"   全名: {student['full_name'] or '未设置'}")
        print(f"   学校ID: {student['school_id']}")
        print(f"   班级ID (User表): {student['classroom_id']}")

        print("\n" + "="*60)
        print("🏫 班级信息")
        print("="*60)

        # 查询班级详情
        classrooms_query = text("""
            SELECT
                c.id,
                c.name,
                c.code,
                c.school_id,
                c.is_active,
                s.name as school_name
            FROM classrooms c
            LEFT JOIN schools s ON c.school_id = s.id
            WHERE c.id IN (:class1, :class2)
        """)

        result = await db.execute(classrooms_query, {
            "class1": teacher['classroom_id'],
            "class2": student['classroom_id']
        })
        classrooms = result.fetchall()

        for classroom in classrooms:
            c = dict(classroom._mapping)
            role = "教师" if c['id'] == teacher['classroom_id'] else "学生"
            print(f"\n{role}的班级:")
            print(f"   班级ID: {c['id']}")
            print(f"   班级名称: {c['name']}")
            print(f"   班级代码: {c['code']}")
            print(f"   学校ID: {c['school_id']}")
            print(f"   学校名称: {c['school_name']}")
            print(f"   是否激活: {c['is_active']}")

        print("\n" + "="*60)
        print("🔍 结论")
        print("="*60)

        # 比较班级
        if teacher['classroom_id'] == student['classroom_id']:
            print(f"\n✅ 是！教师 {teacher['username']} 和学生 {student['username']} 在同一个班级")
            print(f"   班级ID: {teacher['classroom_id']}")
        else:
            print(f"\n❌ 否！教师 {teacher['username']} 和学生 {student['username']} 不在同一个班级")
            print(f"   教师班级ID: {teacher['classroom_id']}")
            print(f"   学生班级ID: {student['classroom_id']}")

        # 比较学校
        if teacher['school_id'] == student['school_id']:
            print(f"\n✅ 但他们在同一所学校（school_id = {teacher['school_id']}）")
        else:
            print(f"\n❌ 他们也在不同的学校")
            print(f"   教师学校ID: {teacher['school_id']}")
            print(f"   学生学校ID: {student['school_id']}")


if __name__ == "__main__":
    asyncio.run(check_with_raw_sql())
