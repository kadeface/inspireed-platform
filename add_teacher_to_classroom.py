"""
将教师 lzd 添加到"七年级一班"（班级ID: 203）
"""
import asyncio
import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def add_teacher_to_classroom():
    """添加教师到班级"""
    async with AsyncSessionLocal() as db:
        print("\n" + "="*60)
        print("📋 准备添加教师到班级")
        print("="*60)

        # 1. 查询用户信息
        query = text("""
            SELECT id, username, full_name, role
            FROM users
            WHERE username IN ('lzd', '2025400')
        """)
        result = await db.execute(query)
        users = {}
        for row in result:
            # row 是一个 tuple，需要通过索引访问
            # id, username, full_name, role
            users[row[1]] = {
                'id': row[0],
                'username': row[1],
                'full_name': row[2],
                'role': row[3]
            }

        if 'lzd' not in users:
            print("❌ 错误：未找到教师 lzd")
            return

        teacher_id = users['lzd']['id']
        classroom_id = 203  # 七年级一班

        print(f"\n👨‍🏫 教师：{users['lzd']['full_name']} (ID: {teacher_id})")
        print(f"🏫 班级ID: {classroom_id}")

        # 2. 检查是否已经是成员
        check_query = text("""
            SELECT id, role_in_class, is_active
            FROM classroom_memberships
            WHERE user_id = :teacher_id AND classroom_id = :classroom_id
        """)
        result = await db.execute(check_query, {
            "teacher_id": teacher_id,
            "classroom_id": classroom_id
        })
        existing = result.fetchone()

        if existing:
            print(f"\n✅ 教师 lzd 已经是班级成员")
            # existing[1] 是 role_in_class, existing[2] 是 is_active
            print(f"   角色: {existing[1]}")
            print(f"   状态: {'激活' if existing[2] else '未激活'}")

            # 如果未激活，激活它
            if not existing[2]:
                print(f"\n🔄 激活现有成员关系...")
                update_query = text("""
                    UPDATE classroom_memberships
                    SET is_active = true
                    WHERE user_id = :teacher_id AND classroom_id = :classroom_id
                """)
                await db.execute(update_query, {
                    "teacher_id": teacher_id,
                    "classroom_id": classroom_id
                })
                await db.commit()
                print("✅ 已激活成员关系")
            return

        # 3. 添加成员关系
        print(f"\n➕ 添加教师到班级...")

        # 使用正确的角色值（需要是数据库中存在的值）
        # 根据RoleInClass enum，任课教师是 "subject_teacher"
        insert_query = text("""
            INSERT INTO classroom_memberships (user_id, classroom_id, role_in_class, is_active)
            VALUES (:teacher_id, :classroom_id, :role, true)
        """)

        try:
            await db.execute(insert_query, {
                "teacher_id": teacher_id,
                "classroom_id": classroom_id,
                "role": "subject_teacher"  # 任课教师
            })
            await db.commit()
            print("✅ 成功将教师 lzd 添加到班级 203（七年级一班）")
        except Exception as e:
            print(f"❌ 添加失败: {e}")
            print("\n💡 可能的角色值：")
            # 查询可用的角色值
            role_query = text("SELECT DISTINCT role FROM classroom_memberships LIMIT 10")
            result = await db.execute(role_query)
            roles = [row['role'] for row in result._mapping.rows]
            for role in roles:
                print(f"   - {role}")
            return

        # 4. 验证添加结果
        print("\n" + "="*60)
        print("🔍 验证结果")
        print("="*60)

        verify_query = text("""
            SELECT
                u.username,
                u.full_name,
                u.role as user_role,
                cm.role_in_class as classroom_role,
                cm.is_active,
                c.name as classroom_name
            FROM classroom_memberships cm
            JOIN users u ON cm.user_id = u.id
            JOIN classrooms c ON cm.classroom_id = c.id
            WHERE cm.user_id = :teacher_id AND cm.classroom_id = :classroom_id
        """)
        result = await db.execute(verify_query, {
            "teacher_id": teacher_id,
            "classroom_id": classroom_id
        })
        membership = result.fetchone()

        if membership:
            # membership[0]=username, [1]=full_name, [2]=user_role, [3]=classroom_role, [4]=is_active, [5]=classroom_name
            print(f"\n✅ 教师 lzd 现在是班级成员：")
            print(f"   班级: {membership[5]}")
            print(f"   班级角色: {membership[3]}")
            print(f"   用户角色: {membership[2]}")
            print(f"   状态: {'激活' if membership[4] else '未激活'}")

            # 检查教师是否可以上课
            print("\n" + "="*60)
            print("✨ 功能验证")
            print("="*60)
            print("\n📝 教师 lzd 现在可以：")
            print(f"   1. 在'七年级一班'创建课堂会话")
            print(f"   2. 为班级学生上课")
            print(f"   3. 使用该班级发布教案")


if __name__ == "__main__":
    asyncio.run(add_teacher_to_classroom())
