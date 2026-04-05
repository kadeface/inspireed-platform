"""
分析系统中用户、班级、学校的关联关系
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def analyze_user_relationships():
    """分析用户关系模型"""
    async with AsyncSessionLocal() as db:
        print("\n" + "="*80)
        print("📊 系统：用户、班级、学校关系分析")
        print("="*80)

        # 1. User 表的直接关联字段
        print("\n📋 1. User 表的直接关联字段")
        print("-" * 80)

        user_fields_query = text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name IN ('school_id', 'classroom_id', 'role')
            ORDER BY ordinal_position
        """)
        result = await db.execute(user_fields_query)
        fields = result.fetchall()

        print("User 表中的关联字段：")
        for field in fields:
            print(f"  - {field[0]} ({field[1]})")

        # 2. ClassroomMembership 表（多对多关系）
        print("\n📋 2. ClassroomMembership 表（多对多关系）")
        print("-" * 80)

        membership_query = text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'classroom_memberships'
            ORDER BY ordinal_position
        """)
        result = await db.execute(membership_query)
        columns = result.fetchall()

        print("ClassroomMembership 表结构：")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")

        # 3. 统计各种关联方式的数据
        print("\n📊 3. 关联方式统计")
        print("-" * 80)

        # 学生通过 User.classroom_id 关联
        student_direct_query = text("""
            SELECT COUNT(DISTINCT u.id) as count
            FROM users u
            WHERE u.role = 'student' AND u.classroom_id IS NOT NULL
        """)
        result = await db.execute(student_direct_query)
        student_direct = result.scalar()

        # 学生通过 ClassroomMembership 关联
        student_membership_query = text("""
            SELECT COUNT(DISTINCT cm.user_id) as count
            FROM classroom_memberships cm
            JOIN users u ON cm.user_id = u.id
            WHERE u.role = 'student' AND cm.is_active = true
        """)
        result = await db.execute(student_membership_query)
        student_membership = result.scalar()

        # 教师通过 ClassroomMembership 关联
        teacher_membership_query = text("""
            SELECT COUNT(DISTINCT cm.user_id) as count
            FROM classroom_memberships cm
            JOIN users u ON cm.user_id = u.id
            WHERE u.role = 'teacher' AND cm.is_active = true
        """)
        result = await db.execute(teacher_membership_query)
        teacher_membership = result.scalar()

        print(f"\n学生关联方式：")
        print(f"  - 通过 User.classroom_id（主班级）: {student_direct} 人")
        print(f"  - 通过 ClassroomMembership（多班级）: {student_membership} 人")

        print(f"\n教师关联方式：")
        print(f"  - 通过 User.school_id（所属学校）: 所有教师")
        print(f"  - 通过 ClassroomMembership（任教班级）: {teacher_membership} 人")

        # 4. 具体示例：教师 lzd 的关联
        print("\n📝 4. 示例：教师 lzd 的班级关联")
        print("-" * 80)

        lzd_info_query = text("""
            SELECT
                u.id,
                u.username,
                u.full_name,
                u.role,
                u.school_id,
                u.classroom_id,
                s.name as school_name
            FROM users u
            LEFT JOIN schools s ON u.school_id = s.id
            WHERE u.username = 'lzd'
        """)
        result = await db.execute(lzd_info_query)
        lzd_info = result.fetchone()

        if lzd_info:
            print(f"\n教师基本信息：")
            print(f"  - ID: {lzd_info[0]}")
            print(f"  - 用户名: {lzd_info[1]}")
            print(f"  - 姓名: {lzd_info[2]}")
            print(f"  - 角色: {lzd_info[3]}")
            print(f"  - 所属学校: {lzd_info[6]} (ID: {lzd_info[4]})")
            print(f"  - 用户表中的班级: {lzd_info[5]}")

            # 查询 lzd 通过 ClassroomMembership 关联的班级
            lzd_classes_query = text("""
                SELECT
                    c.id,
                    c.name,
                    c.code,
                    s.name as school_name,
                    cm.role_in_class,
                    cm.is_active
                FROM classroom_memberships cm
                JOIN classrooms c ON cm.classroom_id = c.id
                JOIN schools s ON c.school_id = s.id
                WHERE cm.user_id = :user_id
                ORDER BY cm.is_active DESC, c.name
            """)
            result = await db.execute(lzd_classes_query, {"user_id": lzd_info[0]})
            lzd_classes = result.fetchall()

            print(f"\n通过 ClassroomMembership 关联的班级：")
            if lzd_classes:
                print(f"  {'班级ID':<10} {'班级名称':<30} {'学校':<30} {'角色':<20} {'状态':<10}")
                print("  " + "-" * 120)
                for cls in lzd_classes:
                    print(f"  {cls[0]:<10} {cls[1]:<30} {cls[3]:<30} {cls[4]:<20} {'激活' if cls[5] else '未激活':<10}")
            else:
                print(f"  ⚠️  未关联任何班级")

        # 5. 具体示例：学生 2025400 的关联
        print("\n📝 5. 示例：学生 2025400 的班级关联")
        print("-" * 80)

        student_info_query = text("""
            SELECT
                u.id,
                u.username,
                u.full_name,
                u.role,
                u.school_id,
                u.classroom_id,
                c.name as classroom_name,
                s.name as school_name
            FROM users u
            LEFT JOIN classrooms c ON u.classroom_id = c.id
            LEFT JOIN schools s ON u.school_id = s.id
            WHERE u.username = '2025400'
        """)
        result = await db.execute(student_info_query)
        student_info = result.fetchone()

        if student_info:
            print(f"\n学生基本信息：")
            print(f"  - ID: {student_info[0]}")
            print(f"  - 用户名: {student_info[1]}")
            print(f"  - 姓名: {student_info[2]}")
            print(f"  - 角色: {student_info[3]}")
            print(f"  - 所属学校: {student_info[7]} (ID: {student_info[4]})")
            print(f"  - 主班级（User表）: {student_info[6] or '未设置'} (ID: {student_info[5]})")

            # 查询学生通过 ClassroomMembership 关联的其他班级
            student_classes_query = text("""
                SELECT
                    c.id,
                    c.name,
                    c.code,
                    cm.role_in_class,
                    cm.is_active,
                    cm.is_primary_class
                FROM classroom_memberships cm
                JOIN classrooms c ON cm.classroom_id = c.id
                WHERE cm.user_id = :user_id
                ORDER BY cm.is_primary_class DESC, c.name
            """)
            result = await db.execute(student_classes_query, {"user_id": student_info[0]})
            student_classes = result.fetchall()

            print(f"\n通过 ClassroomMembership 关联的班级：")
            if student_classes:
                print(f"  {'班级ID':<10} {'班级名称':<30} {'角色':<15} {'主班级':<10} {'状态':<10}")
                print("  " + "-" * 80)
                for cls in student_classes:
                    print(f"  {cls[0]:<10} {cls[1]:<30} {cls[3]:<15} {'是' if cls[5] else '否':<10} {'激活' if cls[4] else '未激活':<10}")
            else:
                print(f"  ⚠️  未通过 ClassroomMembership 关联其他班级")

        # 6. 系统中的班级成员类型
        print("\n📊 6. 班级成员角色类型")
        print("-" * 80)

        role_stats_query = text("""
            SELECT
                cm.role_in_class,
                u.role as user_role,
                COUNT(DISTINCT cm.user_id) as user_count,
                COUNT(DISTINCT cm.classroom_id) as classroom_count
            FROM classroom_memberships cm
            JOIN users u ON cm.user_id = u.id
            WHERE cm.is_active = true
            GROUP BY cm.role_in_class, u.role
            ORDER BY cm.role_in_class, u.role
        """)
        result = await db.execute(role_stats_query)
        role_stats = result.fetchall()

        print(f"\n班级成员角色分布：")
        print(f"  {'班级角色':<25} {'用户角色':<15} {'用户数':<10} {'涉及班级数':<10}")
        print("  " + "-" * 80)
        for stat in role_stats:
            print(f"  {stat[0]:<25} {stat[1]:<15} {stat[2]:<10} {stat[3]:<10}")


if __name__ == "__main__":
    asyncio.run(analyze_user_relationships())
