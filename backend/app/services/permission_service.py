"""
Permission Service for centralized permission checking
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    Classroom, 
    ClassroomMembership, 
    RoleInClass, 
    UserRole, 
    Lesson,
    LessonClassroom, 
    LessonStatus,
    ClassSession,
    ClassSessionStatus,
)


class PermissionService:
    async def can_teacher_publish_to_classroom(self, db: AsyncSession, teacher: "User", classroom: Classroom) -> bool:
        """
        Check if a teacher can publish lessons to a specific classroom

        Priority:
        1. Check ClassroomMembership first (HEAD_TEACHER_PRIMARY, HEAD_TEACHER_DEPUTY, SUBJECT_TEACHER)
        2. Fallback: check school_id

        Args:
            db: Database session
            teacher: The teacher user
            classroom: The target classroom

        Returns:
            bool: True if teacher can publish, False otherwise
        """
        # Check ClassroomMembership first (HEAD_TEACHER_PRIMARY, HEAD_TEACHER_DEPUTY, SUBJECT_TEACHER)
        membership = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.classroom_id == classroom.id,
                ClassroomMembership.user_id == teacher.id,
                ClassroomMembership.role_in_class.in_([
                    RoleInClass.HEAD_TEACHER_PRIMARY,
                    RoleInClass.HEAD_TEACHER_DEPUTY,
                    RoleInClass.SUBJECT_TEACHER,
                ]),
                ClassroomMembership.is_active == True
            )
        )
        if membership.scalar_one_or_none():
            return True
        # Fallback: check school_id
        if teacher.school_id is not None and teacher.school_id == classroom.school_id:
            return True
        return False

    async def can_student_view_lesson(self, db: AsyncSession, student: "User", lesson_id: int) -> bool:
        """
        Check if a student can view a specific lesson

        Args:
            db: Database session
            student: The student user
            lesson_id: The lesson ID to check

        Returns:
            bool: True if student can view the lesson, False otherwise
        """
        # 🆕 使用统一的班级查询函数（支持多班级和向后兼容）
        from app.core.classroom_utils import get_user_classroom_ids
        classroom_ids = await get_user_classroom_ids(db, student)
        
        if not classroom_ids:
            return False

        # 🆕 优先检查：如果学生有活跃的课堂会话（PREPARING或TEACHING），允许访问
        # 这样可以确保学生能够从待开始课堂列表进入课程
        active_session_result = await db.execute(
            select(ClassSession).where(
                ClassSession.lesson_id == lesson_id,
                ClassSession.classroom_id.in_(list(classroom_ids)),
                ClassSession.status.in_([ClassSessionStatus.PREPARING, ClassSessionStatus.TEACHING])
            )
        )
        if active_session_result.scalar_one_or_none() is not None:
            return True

        # Check if lesson is published and assigned to any of student's classrooms
        assignment = await db.execute(
            select(LessonClassroom).join(Lesson).where(
                LessonClassroom.lesson_id == lesson_id,
                LessonClassroom.classroom_id.in_(list(classroom_ids)),
                Lesson.status == LessonStatus.PUBLISHED
            )
        )
        return assignment.scalar_one_or_none() is not None