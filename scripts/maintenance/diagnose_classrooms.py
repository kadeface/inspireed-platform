"""
诊断班级列表问题：检查为什么前端看不到班级
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import select, text, func
from app.core.database import AsyncSessionLocal
from app.models import User, Classroom, School, UserRole
from app.services.classroom_service import ClassroomQueryService


async def diagnose_classroom_issue():
    """诊断班级列表问题"""
    async with AsyncSessionLocal() as db:
        print("\n" + "="*80)
        print("🔍 班级列表问题诊断")
        print("="*80)

        # 1. 检查数据库中的班级总数
        print("\n📊 1. 数据库中的班级统计")
        print("-" * 80)

        count_result = await db.execute(select(func.count(Classroom.id)))
        total_count = count_result.scalar()
        print(f"班级总数: {total_count}")

        # 2. 检查班级分布
        stats_query = text("""
            SELECT
                s.id as school_id,
                s.name as school_name,
                COUNT(c.id) as classroom_count,
                COUNT(c.id) FILTER (WHERE c.is_active = true) as active_count
            FROM schools s
            LEFT JOIN classrooms c ON s.id = c.school_id
            GROUP BY s.id, s.name
            ORDER BY classroom_count DESC
            LIMIT 10
        """)
        result = await db.execute(stats_query)
        stats = result.fetchall()

        print(f"\n前10个学校的班级分布：")
        print(f"{'学校ID':<10} {'学校名称':<30} {'班级数':<10} {'激活数':<10}")
        print("-" * 80)
        for row in stats:
            print(f"{row[0]:<10} {row[1]:<30} {row[2]:<10} {row[3]:<10}")

        # 3. 检查管理员用户
        print("\n👤 2. 检查管理员账号")
        print("-" * 80)

        admin_query = text("""
            SELECT
                u.id,
                u.username,
                u.role,
                u.school_id,
                u.region_id
            FROM users u
            WHERE u.role IN ('admin', 'school_admin', 'district_admin')
            ORDER BY u.id
            LIMIT 10
        """)
        result = await db.execute(admin_query)
        admins = result.fetchall()

        print(f"\n找到 {len(admins)} 个管理员账号：")
        print(f"{'ID':<10} {'用户名':<20} {'角色':<20} {'学校ID':<10} {'区域ID':<10}")
        print("-" * 80)
        for row in admins:
            print(f"{row[0]:<10} {row[1]:<20} {row[2]:<20} {row[3] or 'N/A':<10} {row[4] or 'N/A':<10}")

        # 4. 测试 ClassroomQueryService（获取第一个管理员）
        if admins:
            first_admin_id = admins[0][0]
            first_admin_role = admins[0][2]
            first_admin_school_id = admins[0][3]
            first_admin_region_id = admins[0][4]

            print(f"\n🔍 3. 测试 ClassroomQueryService")
            print("-" * 80)
            print(f"使用管理员: {admins[0][1]} (ID: {first_admin_id}, Role: {first_admin_role})")

            # 获取用户对象
            user = await db.get(User, first_admin_id)

            # 测试服务
            service = ClassroomQueryService()
            classrooms_for_user = await service.get_classrooms_for_user(
                db,
                user,
                is_active=None  # 不过滤激活状态
            )

            print(f"\n服务返回的班级数: {len(classrooms_for_user)}")

            if len(classrooms_for_user) > 0:
                print(f"\n前5个班级：")
                print(f"{'ID':<10} {'名称':<30} {'学校ID':<10} {'激活':<10}")
                print("-" * 80)
                for c in classrooms_for_user[:5]:
                    print(f"{c.id:<10} {c.name:<30} {c.school_id:<10} {str(c.is_active):<10}")
            else:
                print("\n⚠️ 服务返回空列表！")
                print(f"\n可能的原因：")
                print(f"  - 用户角色: {first_admin_role}")
                print(f"  - 用户学校ID: {first_admin_school_id}")
                print(f"  - 用户区域ID: {first_admin_region_id}")

        # 5. 直接查询班级（不过滤）
        print("\n📋 4. 直接查询所有班级（不过滤）")
        print("-" * 80)

        direct_query = text("""
            SELECT
                c.id,
                c.name,
                c.code,
                c.school_id,
                c.is_active,
                s.name as school_name
            FROM classrooms c
            JOIN schools s ON c.school_id = s.id
            ORDER BY c.id
            LIMIT 10
        """)
        result = await db.execute(direct_query)
        classrooms = result.fetchall()

        print(f"\n前10个班级（直接查询）：")
        print(f"{'ID':<10} {'名称':<30} {'编码':<15} {'学校':<30} {'激活':<10}")
        print("-" * 80)
        for row in classrooms:
            print(f"{row[0]:<10} {row[1]:<30} {row[2] or 'N/A':<15} {row[5]:<30} {row[4]:<10}")

        # 6. 检查API响应模型
        print("\n🔧 5. 检查可能的问题")
        print("-" * 80)

        print("\n常见问题排查：")
        print("1. ✅ 数据库中确实有班级记录")
        print("2. ❓ ClassroomQueryService 的过滤逻辑")
        print("   - ADMIN角色应该能看到所有班级")
        print("   - SCHOOL_ADMIN只能看到本校班级")
        print("   - DISTRICT_ADMIN只能看到本区域班级")
        print("3. ❓ 前端是否传递了错误的筛选参数")
        print("4. ❓ API响应是否正确序列化")


if __name__ == "__main__":
    asyncio.run(diagnose_classroom_issue())
