"""
检查教师 lzd 和学生 2025400 是否在同一个班级
"""
import asyncio
import sys
import os

# 添加后端路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.organization import Classroom
from app.models.classroom_assistant import ClassroomMembership


async def check_classroom_membership():
    """检查两个用户是否在同一个班级"""
    async with AsyncSessionLocal() as db:
        # 1. 查询两个用户的基本信息
        result = await db.execute(
            select(User)
            .where(User.username.in_(['lzd', '2025400']))
        )
        users = result.scalars().all()

        if len(users) != 2:
            print(f"❌ 错误：只找到 {len(users)} 个用户")
            for user in users:
                print(f"   - {user.username} (ID: {user.id}, Role: {user.role})")
            return

        teacher = None
        student = None

        for user in users:
            if user.role == UserRole.TEACHER:
                teacher = user
            elif user.role == UserRole.STUDENT:
                student = user

        if not teacher:
            print("❌ 错误：未找到教师 lzd")
            return

        if not student:
            print("❌ 错误：未找到学生 2025400")
            return

        print("\n" + "="*60)
        print("📋 用户基本信息")
        print("="*60)

        print(f"\n👨‍🏫 教师：{teacher.username}")
        print(f"   ID: {teacher.id}")
        print(f"   全名: {teacher.full_name or '未设置'}")
        print(f"   邮箱: {teacher.email or '未设置'}")
        print(f"   学校ID: {teacher.school_id}")
        print(f"   用户表中的班级ID: {teacher.classroom_id}")

        print(f"\n👨‍🎓 学生：{student.username}")
        print(f"   ID: {student.id}")
        print(f"   全名: {student.full_name or '未设置'}")
        print(f"   邮箱: {student.email or '未设置'}")
        print(f"   学校ID: {student.school_id}")
        print(f"   用户表中的班级ID: {student.classroom_id}")

        # 2. 检查班级关系
        print("\n" + "="*60)
        print("🏫 班级关系检查")
        print("="*60)

        # 检查教师的班级（通过 ClassroomMembership）
        # 简化查询，避免 enum 错误
        teacher_classrooms_result = await db.execute(
            select(ClassroomMembership)
            .where(ClassroomMembership.user_id == teacher.id)
        )
        teacher_memberships = teacher_classrooms_result.scalars().all()

        print(f"\n👨‍🏫 教师 {teacher.username} 关联的班级（通过 ClassroomMembership）:")
        if teacher_memberships:
            for membership in teacher_memberships:
                classroom = await db.get(Classroom, membership.classroom_id)
                if classroom:
                    print(f"   - 班级ID: {classroom.id}")
                    print(f"     班级名称: {classroom.name}")
                    print(f"     班级代码: {classroom.code}")
                    print(f"     角色代码: {membership.role}")
                    print(f"     是否激活: {membership.is_active}")
        else:
            print("   ⚠️  未找到通过 ClassroomMembership 关联的班级")
            print(f"   💡 教师的 school_id = {teacher.school_id}")

        # 检查学生的班级（通过 ClassroomMembership 和 User.classroom_id）
        student_classrooms_result = await db.execute(
            select(ClassroomMembership)
            .where(ClassroomMembership.user_id == student.id)
        )
        student_memberships = student_classrooms_result.scalars().all()

        print(f"\n👨‍🎓 学生 {student.username} 关联的班级:")
        print(f"   方式1 - User.classroom_id: {student.classroom_id}")
        if student.classroom_id:
            classroom = await db.get(Classroom, student.classroom_id)
            if classroom:
                print(f"      - 班级ID: {classroom.id}")
                print(f"      - 班级名称: {classroom.name}")
                print(f"      - 班级代码: {classroom.code}")
                print(f"      - 学校ID: {classroom.school_id}")

        print(f"\n   方式2 - ClassroomMembership:")
        if student_memberships:
            for membership in student_memberships:
                classroom = await db.get(Classroom, membership.classroom_id)
                if classroom:
                    print(f"      - 班级ID: {classroom.id}")
                    print(f"        班级名称: {classroom.name}")
                    print(f"        班级代码: {classroom.code}")
                    print(f"        是否激活: {membership.is_active}")
        else:
            print("      ⚠️  未找到通过 ClassroomMembership 关联的班级")

        # 3. 检查是否在同一个班级
        print("\n" + "="*60)
        print("🔍 是否在同一个班级？")
        print("="*60)

        # 收集所有班级ID
        teacher_classroom_ids = set()
        for membership in teacher_memberships:
            teacher_classroom_ids.add(membership.classroom_id)

        student_classroom_ids = set()

        if student.classroom_id:
            student_classroom_ids.add(student.classroom_id)
        for membership in student_memberships:
            student_classroom_ids.add(membership.classroom_id)

        # 检查交集
        common_classrooms = teacher_classroom_ids & student_classroom_ids

        if common_classrooms:
            print(f"\n✅ 是！教师 {teacher.username} 和学生 {student.username} 在同一个班级")
            for classroom_id in common_classrooms:
                classroom = await db.get(Classroom, classroom_id)
                print(f"   共同班级: {classroom.name} (ID: {classroom.id}, 代码: {classroom.code})")
        else:
            print(f"\n❌ 否！教师 {teacher.username} 和学生 {student.username} 不在同一个班级")

            if teacher_classroom_ids:
                print(f"\n教师的班级: {teacher_classroom_ids}")
            else:
                print(f"\n教师未分配到具体班级（只有 school_id: {teacher.school_id}）")

            if student_classroom_ids:
                print(f"学生的班级: {student_classroom_ids}")
            else:
                print(f"学生未分配到具体班级")

        # 4. 检查是否在同一学校
        print("\n" + "="*60)
        print("🏫 是否在同一学校？")
        print("="*60)

        if teacher.school_id and student.school_id:
            if teacher.school_id == student.school_id:
                print(f"\n✅ 是！他们在同一学校（school_id = {teacher.school_id}）")
                # 查询学校名称
                from app.models.organization import School
                school = await db.get(School, teacher.school_id)
                if school:
                    print(f"   学校名称: {school.name}")
            else:
                print(f"\n❌ 否！他们在不同学校")
                print(f"   教师学校ID: {teacher.school_id}")
                print(f"   学生学校ID: {student.school_id}")
        else:
            print(f"\n⚠️  无法判断（至少一人未分配学校）")
            print(f"   教师学校ID: {teacher.school_id}")
            print(f"   学生学校ID: {student.school_id}")


if __name__ == "__main__":
    asyncio.run(check_classroom_membership())
