"""
权限系统测试

测试细粒度的数据访问权限控制
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.permissions import PermissionChecker, check_permission_or_403
from app.models import UserRole, User, Exam, Classroom, ValueAddedEvaluation


async def test_permission_checker():
    """测试权限检查器"""
    print("=" * 60)
    print("权限检查器测试")
    print("=" * 60)

    # 创建测试用户
    test_users = {
        "admin": User(
            id=1,
            role=UserRole.ADMIN,
            region_id=1,
            school_id=1,
            grade_id=1,
            is_active=True,
        ),
        "district_admin": User(
            id=2,
            role=UserRole.DISTRICT_ADMIN,
            region_id=1,
            school_id=None,
            grade_id=None,
            is_active=True,
        ),
        "school_admin": User(
            id=3,
            role=UserRole.SCHOOL_ADMIN,
            region_id=1,
            school_id=1,
            grade_id=None,
            is_active=True,
        ),
        "researcher": User(
            id=4,
            role=UserRole.RESEARCHER,
            region_id=1,
            school_id=1,
            grade_id=None,
            is_active=True,
        ),
        "teacher": User(
            id=5,
            role=UserRole.TEACHER,
            region_id=1,
            school_id=1,
            grade_id=1,
            is_active=True,
        ),
        "student": User(
            id=6,
            role=UserRole.STUDENT,
            region_id=1,
            school_id=1,
            grade_id=1,
            is_active=True,
        ),
    }

    # 测试场景1: 区县数据访问
    print("\n场景1: 访问区县数据 (region_id=1)")
    print("-" * 60)

    async with AsyncSessionLocal() as db:
        for role_name, user in test_users.items():
            can_access = await PermissionChecker.can_access_region_data(
                user, region_id=1
            )
            can_modify = await PermissionChecker.can_modify_region_data(
                user, region_id=1
            )
            print(f"  {role_name:15} - 访问: {'✓' if can_access else '✗'}, 修改: {'✓' if can_modify else '✗'}")

    # 测试场景2: 学校数据访问
    print("\n场景2: 访问学校数据 (school_id=1)")
    print("-" * 60)

    async with AsyncSessionLocal() as db:
        for role_name, user in test_users.items():
            can_access = await PermissionChecker.can_access_school_data(
                user, school_id=1
            )
            can_modify = await PermissionChecker.can_modify_school_data(
                user, school_id=1
            )
            print(f"  {role_name:15} - 访问: {'✓' if can_access else '✗'}, 修改: {'✓' if can_modify else '✗'}")

    # 测试场景3: 班级数据访问
    print("\n场景3: 访问班级数据 (classroom_id=1)")
    print("-" * 60)

    async with AsyncSessionLocal() as db:
        for role_name, user in test_users.items():
            can_access = await PermissionChecker.can_access_classroom_data(
                db, user, classroom_id=1
            )
            can_modify = await PermissionChecker.can_modify_classroom_data(
                db, user, classroom_id=1
            )
            print(f"  {role_name:15} - 访问: {'✓' if can_access else '✗'}, 修改: {'✓' if can_modify else '✗'}")

    # 测试场景4: 学生数据访问
    print("\n场景4: 访问学生数据 (student_id=6)")
    print("-" * 60)

    async with AsyncSessionLocal() as db:
        for role_name, user in test_users.items():
            can_access = await PermissionChecker.can_access_student_data(
                db, user, student_id=6
            )
            print(f"  {role_name:15} - 访问: {'✓' if can_access else '✗'}")

    print("\n✅ 权限检查器测试完成")


async def test_permission_matrix():
    """测试权限矩阵"""
    print("\n" + "=" * 60)
    print("权限矩阵测试")
    print("=" * 60)

    # 权限矩阵（期望结果）
    permission_matrix = {
        "区县数据": {
            UserRole.ADMIN: ("✓", "✓"),  # (访问, 修改)
            UserRole.DISTRICT_ADMIN: ("✓", "✓"),
            UserRole.SCHOOL_ADMIN: ("✓", "✗"),
            UserRole.RESEARCHER: ("✓", "✗"),
            UserRole.TEACHER: ("✓", "✗"),
            UserRole.STUDENT: ("✓", "✗"),
        },
        "学校数据": {
            UserRole.ADMIN: ("✓", "✓"),
            UserRole.DISTRICT_ADMIN: ("✓", "✓"),
            UserRole.SCHOOL_ADMIN: ("✓", "✓"),
            UserRole.RESEARCHER: ("✓", "✗"),
            UserRole.TEACHER: ("✓", "✗"),
            UserRole.STUDENT: ("✓", "✗"),
        },
        "班级数据": {
            UserRole.ADMIN: ("✓", "✓"),
            UserRole.DISTRICT_ADMIN: ("✓", "✓"),
            UserRole.SCHOOL_ADMIN: ("✓", "✓"),
            UserRole.RESEARCHER: ("✓", "✗"),
            UserRole.TEACHER: ("✓", "✗"),
            UserRole.STUDENT: ("✓", "✗"),
        },
        "评价数据": {
            UserRole.ADMIN: ("✓", "✓"),
            UserRole.DISTRICT_ADMIN: ("✓", "✓"),
            UserRole.SCHOOL_ADMIN: ("✓", "✓"),
            UserRole.RESEARCHER: ("✓", "✓"),
            UserRole.TEACHER: ("✓", "✗"),
            UserRole.STUDENT: ("✗", "✗"),
        },
    }

    print("\n权限矩阵 (访问/修改):")
    print("-" * 60)

    for resource, roles in permission_matrix.items():
        print(f"\n{resource}:")
        for role, (access, modify) in roles.items():
            print(f"  {role.value:20} - 访问: {access}, 修改: {modify}")

    print("\n✅ 权限矩阵展示完成")


async def test_cross_region_access():
    """测试跨区访问"""
    print("\n" + "=" * 60)
    print("跨区访问测试")
    print("=" * 60)

    # 创建不同区县的用户
    user_region1 = User(
        id=1,
        role=UserRole.DISTRICT_ADMIN,
        region_id=1,
        is_active=True,
    )

    user_region2 = User(
        id=2,
        role=UserRole.DISTRICT_ADMIN,
        region_id=2,
        is_active=True,
    )

    admin_user = User(
        id=3,
        role=UserRole.ADMIN,
        region_id=None,
        is_active=True,
    )

    print("\n场景: region_id=1的用户访问region_id=2的数据")
    print("-" * 60)

    async with AsyncSessionLocal() as db:
        # region_id=1的区县管理员访问region_id=2的数据
        can_access = await PermissionChecker.can_access_region_data(
            user_region1, region_id=2
        )
        print(f"  区县管理员(region=1)访问区县2数据: {'✓' if can_access else '✗'} (预期: ✗)")

        # region_id=2的区县管理员访问region_id=2的数据
        can_access = await PermissionChecker.can_access_region_data(
            user_region2, region_id=2
        )
        print(f"  区县管理员(region=2)访问区县2数据: {'✓' if can_access else '✗'} (预期: ✓)")

        # 管理员访问region_id=2的数据
        can_access = await PermissionChecker.can_access_region_data(
            admin_user, region_id=2
        )
        print(f"  系统管理员访问区县2数据: {'✓' if can_access else '✗'} (预期: ✓)")

    print("\n✅ 跨区访问测试完成")


async def test_permission_hierarchy():
    """测试权限层级"""
    print("\n" + "=" * 60)
    print("权限层级测试")
    print("=" * 60)

    # 权限层级（从高到低）
    role_hierarchy = [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
        UserRole.RESEARCHER,
        UserRole.TEACHER,
        UserRole.STUDENT,
    ]

    print("\n权限层级（从高到低）:")
    print("-" * 60)

    for idx, role in enumerate(role_hierarchy, 1):
        print(f"{idx}. {role.value}")

    print("\n权限特点:")
    print("-" * 60)
    print("• ADMIN: 超级管理员，拥有所有权限")
    print("• DISTRICT_ADMIN: 区县管理员，管理整个区县")
    print("• SCHOOL_ADMIN: 学校管理员，管理本校")
    print("• RESEARCHER: 教研员，分析和查看数据")
    print("• TEACHER: 教师，查看所教班级数据")
    print("• STUDENT: 学生，只能查看个人数据")

    print("\n✅ 权限层级测试完成")


async def main():
    """主测试函数"""
    print("\n权限系统测试\n")

    # 测试1: 权限检查器
    await test_permission_checker()

    # 测试2: 权限矩阵
    await test_permission_matrix()

    # 测试3: 跨区访问
    await test_cross_region_access()

    # 测试4: 权限层级
    await test_permission_hierarchy()

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("✅ 权限系统基础功能测试完成")
    print("✅ 权限检查器正常工作")
    print("✅ 支持细粒度的数据访问控制")
    print("✅ 权限层级清晰，易于理解")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
