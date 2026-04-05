"""
诊断学生无法加入课堂的问题
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.lesson import Lesson
from app.models.classroom_session import ClassSession, ClassSessionStatus


async def diagnose_student_join_issue():
    """诊断学生无法加入课堂的问题"""
    async with AsyncSessionLocal() as db:
        print("\n" + "="*80)
        print("🔍 学生加入课堂问题诊断")
        print("="*80)

        # 1. 查询教师 lzd
        print("\n📋 1. 教师信息")
        print("-" * 80)
        teacher_query = text("""
            SELECT id, username, full_name, role, school_id, classroom_id
            FROM users
            WHERE username = 'lzd'
        """)
        result = await db.execute(teacher_query)
        teacher = result.fetchone()

        if teacher:
            print(f"\n✅ 找到教师:")
            print(f"   ID: {teacher[0]}")
            print(f"   用户名: {teacher[1]}")
            print(f"   姓名: {teacher[2]}")
            print(f"   角色: {teacher[3]}")
            print(f"   所属学校: {teacher[4]}")
            print(f"   用户表中的班级: {teacher[5]}")
        else:
            print("\n❌ 未找到教师 lzd")
            return

        teacher_id = teacher[0]
        teacher_school_id = teacher[4]

        # 2. 查询学生 2025400
        print("\n📋 2. 学生信息")
        print("-" * 80)
        student_query = text("""
            SELECT id, username, full_name, role, school_id, classroom_id
            FROM users
            WHERE username = '2025400'
        """)
        result = await db.execute(student_query)
        student = result.fetchone()

        if student:
            print(f"\n✅ 找到学生:")
            print(f"   ID: {student[0]}")
            print(f"   用户名: {student[1]}")
            print(f"   姓名: {student[2]}")
            print(f"   角色: {student[3]}")
            print(f"   所属学校: {student[4]}")
            print(f"   用户表中的班级: {student[5]}")
        else:
            print("\n❌ 未找到学生 2025400")
            return

        student_id = student[0]
        student_classroom_id = student[5]
        student_school_id = student[4]

        # 3. 查询教师的班级成员关系
        print("\n📋 3. 教师的班级关联（ClassroomMembership）")
        print("-" * 80)
        teacher_classes_query = text("""
            SELECT cm.id, cm.classroom_id, cm.role_in_class, cm.is_active,
                   c.name as classroom_name, c.school_id as classroom_school_id
            FROM classroom_memberships cm
            JOIN classrooms c ON cm.classroom_id = c.id
            WHERE cm.user_id = :teacher_id
        """)
        result = await db.execute(teacher_classes_query, {"teacher_id": teacher_id})
        teacher_classes = result.fetchall()

        if teacher_classes:
            print(f"\n✅ 教师关联的班级数: {len(teacher_classes)}")
            print(f"   {'ID':<10} {'班级ID':<12} {'班级名称':<30} {'学校ID':<10} {'角色':<20} {'激活':<10}")
            print("   " + "-" * 120)
            for tc in teacher_classes:
                print(f"   {tc[0]:<10} {tc[1]:<12} {tc[4]:<30} {tc[5]:<10} {tc[2]:<20} {'是' if tc[3] else '否':<10}")
        else:
            print("\n⚠️  教师未关联任何班级")

        # 4. 查询学生的班级成员关系
        print("\n📋 4. 学生的班级关联（ClassroomMembership）")
        print("-" * 80)
        student_classes_query = text("""
            SELECT cm.id, cm.classroom_id, cm.role_in_class, cm.is_active, cm.is_primary_class,
                   c.name as classroom_name
            FROM classroom_memberships cm
            JOIN classrooms c ON cm.classroom_id = c.id
            WHERE cm.user_id = :student_id
        """)
        result = await db.execute(student_classes_query, {"student_id": student_id})
        student_classes = result.fetchall()

        if student_classes:
            print(f"\n✅ 学生关联的班级数: {len(student_classes)}")
            print(f"   {'ID':<10} {'班级ID':<12} {'班级名称':<30} {'角色':<15} {'主班级':<10} {'激活':<10}")
            print("   " + "-" * 90)
            for sc in student_classes:
                print(f"   {sc[0]:<10} {sc[1]:<12} {sc[4]:<30} {sc[2]:<15} {'是' if sc[5] else '否':<10} {'是' if sc[3] else '否':<10}")
        else:
            print("\n⚠️  学生未通过 ClassroomMembership 关联任何班级")
            print(f"   但用户表中有班级ID: {student_classroom_id}")

        # 5. 查询课堂会话
        print("\n📋 5. 课堂会话检查")
        print("-" * 80)
        sessions_query = text("""
            SELECT cs.id, cs.lesson_id, cs.classroom_id, cs.status,
                   cs.created_at, cs.actual_start, cs.ended_at,
                   l.title as lesson_title, t.full_name as teacher_name
            FROM class_sessions cs
            JOIN lessons l ON cs.lesson_id = l.id
            JOIN users t ON cs.teacher_id = t.id
            WHERE cs.teacher_id = :teacher_id
            ORDER BY cs.created_at DESC
            LIMIT 10
        """)
        result = await db.execute(sessions_query, {"teacher_id": teacher_id})
        sessions = result.fetchall()

        if sessions:
            print(f"\n✅ 找到 {len(sessions)} 个课堂会话:")
            print(f"   {'会话ID':<10} {'教案ID':<10} {'班级ID':<10} {'状态':<15} {'创建时间':<25} {'教案标题'}")
            print("   " + "-" * 120)
            for s in sessions:
                print(f"   {s[0]:<10} {s[1]:<10} {s[2]:<10} {s[3]:<15} {str(s[4]):<25} {s[7] or '无标题'}")
        else:
            print("\n❌ 未找到任何课堂会话")
            print("   这是问题原因 #1：教师尚未创建课堂")
            print("   解决方案：教师需要先创建课堂会话")

        # 6. 检查会话与学生的班级匹配
        print("\n📋 6. 会话与学生的班级匹配检查")
        print("-" * 80)

        # 获取学生所有可加入的班级
        student_classroom_ids = set()

        # 从 ClassroomMembership 获取
        if student_classes:
            for sc in student_classes:
                student_classroom_ids.add(sc[1])
        # 从 User.classroom_id 获取
        elif student_classroom_id:
            student_classroom_ids.add(student_classroom_id)

        print(f"\n👨‍🎓 学生可加入的班级ID: {student_classroom_ids}")

        if sessions:
            for s in sessions:
                session_id = s[0]
                session_classroom_id = s[2]
                session_status = s[3]

                print(f"\n📌 会话 {session_id}:")
                print(f"   会话班级ID: {session_classroom_id}")
                print(f"   会话状态: {session_status}")

                # 检查学生是否在这个班级
                can_join = session_classroom_id in student_classroom_ids
                print(f"   学生可加入: {'✅ 是' if can_join else '❌ 否'}")

                if not can_join:
                    print(f"\n   ⚠️  这是问题原因 #2：教师创建的课堂不属于学生的班级")
                    print(f"   学生可加入的班级: {student_classroom_ids}")
                    print(f"   会话所在的班级: {session_classroom_id}")
                    print(f"\n   解决方案:")
                    if len(student_classroom_ids) == 0:
                        print(f"   1. 将学生分配到班级 {session_classroom_id}")
                        print(f"   2. 或者让教师在班级 {session_classroom_id} 中创建课堂")
                    else:
                        print(f"   1. 让教师在班级 {list(student_classroom_ids)[0]} 中创建课堂")
                        print(f"   2. 或者将学生加入班级 {session_classroom_id}")

                # 检查会话状态
                if session_status == 'ended':
                    print(f"\n   ⚠️  这是问题原因 #3：课堂会话已结束")
                    print(f"   解决方案：教师需要重新创建课堂会话")

        # 7. 总结
        print("\n" + "="*80)
        print("📊 诊断总结")
        print("="*80)

        issues = []

        if not sessions:
            issues.append("❌ 教师尚未创建课堂")
        else:
            # 检查是否有匹配的会话
            has_match = False
            for s in sessions:
                if s[2] in student_classroom_ids and s[3] in ['pending', 'active']:
                    has_match = True
                    break

            if not has_match:
                issues.append("❌ 教师创建的课堂不属于学生的班级或已结束")
            else:
                print("\n✅ 找到可加入的课堂会话！")
                for s in sessions:
                    if s[2] in student_classroom_ids and s[3] in ['pending', 'active']:
                        print(f"   会话ID {s[0]}: {s[3]} 状态，班级ID {s[2]}")

        if issues:
            print("\n发现的问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✅ 未发现问题，学生应该可以加入课堂")


if __name__ == "__main__":
    asyncio.run(diagnose_student_join_issue())
