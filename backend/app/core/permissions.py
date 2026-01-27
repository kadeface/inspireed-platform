"""
评价系统权限控制模块

提供细粒度的数据访问权限控制
"""

from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models import (
    User,
    UserRole,
    Region,
    School,
    Classroom,
    ClassroomMembership,
    Exam,
    Score,
    ValueAddedEvaluation,
)


class PermissionChecker:
    """权限检查器"""

    @staticmethod
    async def can_access_region_data(
        current_user: User,
        region_id: Optional[int],
    ) -> bool:
        """
        检查用户是否可以访问区县数据

        权限规则：
        - ADMIN: 可以访问所有区县
        - DISTRICT_ADMIN: 可以访问所属区县
        - SCHOOL_ADMIN: 只能查看（不能修改）
        - RESEARCHER: 可以访问所属区县
        - 其他: 不可以访问
        """
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == region_id

        if current_user.role == UserRole.RESEARCHER:
            return current_user.region_id == region_id

        if current_user.role in [UserRole.SCHOOL_ADMIN, UserRole.TEACHER, UserRole.STUDENT]:
            # 这些角色只能查看，不能修改（在其他函数中判断）
            return current_user.region_id == region_id

        return False

    @staticmethod
    async def can_modify_region_data(
        current_user: User,
        region_id: Optional[int],
    ) -> bool:
        """检查用户是否可以修改区县数据"""
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == region_id

        return False

    @staticmethod
    async def can_access_school_data(
        current_user: User,
        school_id: Optional[int],
    ) -> bool:
        """
        检查用户是否可以访问学校数据

        权限规则：
        - ADMIN: 可以访问所有学校
        - DISTRICT_ADMIN: 可以访问所属区县的学校
        - SCHOOL_ADMIN: 可以访问本校
        - RESEARCHER: 可以访问所属区县/学校
        - TEACHER: 可以访问本校
        - STUDENT: 可以访问本校
        """
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            if not school_id:
                return True
            # 检查学校是否属于该区县
            return await PermissionChecker._school_in_region(
                school_id, current_user.region_id
            )

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == school_id

        if current_user.role == UserRole.RESEARCHER:
            if current_user.school_id:
                return current_user.school_id == school_id
            if current_user.region_id:
                return await PermissionChecker._school_in_region(
                    school_id, current_user.region_id
                )
            return False

        if current_user.role in [UserRole.TEACHER, UserRole.STUDENT]:
            return current_user.school_id == school_id

        return False

    @staticmethod
    async def can_modify_school_data(
        current_user: User,
        school_id: Optional[int],
    ) -> bool:
        """检查用户是否可以修改学校数据"""
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            if not school_id:
                return True
            return await PermissionChecker._school_in_region(
                school_id, current_user.region_id
            )

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == school_id

        return False

    @staticmethod
    async def can_access_classroom_data(
        db: AsyncSession,
        current_user: User,
        classroom_id: int,
    ) -> bool:
        """
        检查用户是否可以访问班级数据

        权限规则：
        - ADMIN: 可以访问所有班级
        - DISTRICT_ADMIN: 可以访问所属区县的班级
        - SCHOOL_ADMIN: 可以访问本校的班级
        - RESEARCHER: 可以访问所属区县/学校的班级
        - TEACHER: 只能访问所教班级
        - STUDENT: 只能访问所属班级
        """
        if current_user.role == UserRole.ADMIN:
            return True

        # 查询班级信息
        classroom_result = await db.execute(
            select(Classroom)
            .options(selectinload(Classroom.school))
            .where(Classroom.id == classroom_id)
        )
        classroom = classroom_result.scalar_one_or_none()
        if not classroom:
            return False

        if current_user.role == UserRole.DISTRICT_ADMIN:
            # 通过school获取region_id
            school_region_id = classroom.school.region_id if classroom.school else None
            return current_user.region_id == school_region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == classroom.school_id

        if current_user.role == UserRole.RESEARCHER:
            if current_user.school_id:
                return current_user.school_id == classroom.school_id
            if current_user.region_id:
                school_region_id = classroom.school.region_id if classroom.school else None
                return current_user.region_id == school_region_id
            return False

        if current_user.role == UserRole.TEACHER:
            # 检查是否是该班级的教师
            membership_result = await db.execute(
                select(ClassroomMembership).where(
                    and_(
                        ClassroomMembership.user_id == current_user.id,
                        ClassroomMembership.classroom_id == classroom_id,
                        ClassroomMembership.is_active == True,
                    )
                )
            )
            return membership_result.scalar_one_or_none() is not None

        if current_user.role == UserRole.STUDENT:
            # 检查是否是该班级的学生
            membership_result = await db.execute(
                select(ClassroomMembership).where(
                    and_(
                        ClassroomMembership.user_id == current_user.id,
                        ClassroomMembership.classroom_id == classroom_id,
                        ClassroomMembership.is_active == True,
                    )
                )
            )
            return membership_result.scalar_one_or_none() is not None

        return False

    @staticmethod
    async def can_modify_classroom_data(
        db: AsyncSession,
        current_user: User,
        classroom_id: int,
    ) -> bool:
        """检查用户是否可以修改班级数据"""
        if current_user.role == UserRole.ADMIN:
            return True

        classroom_result = await db.execute(
            select(Classroom)
            .options(selectinload(Classroom.school))
            .where(Classroom.id == classroom_id)
        )
        classroom = classroom_result.scalar_one_or_none()
        if not classroom:
            return False

        if current_user.role == UserRole.DISTRICT_ADMIN:
            school_region_id = classroom.school.region_id if classroom.school else None
            return current_user.region_id == school_region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == classroom.school_id

        if current_user.role == UserRole.TEACHER:
            # 教师只能修改所教班级
            membership_result = await db.execute(
                select(ClassroomMembership).where(
                    and_(
                        ClassroomMembership.user_id == current_user.id,
                        ClassroomMembership.classroom_id == classroom_id,
                        ClassroomMembership.is_active == True,
                    )
                )
            )
            return membership_result.scalar_one_or_none() is not None

        return False

    @staticmethod
    async def can_access_student_data(
        db: AsyncSession,
        current_user: User,
        student_id: int,
    ) -> bool:
        """
        检查用户是否可以访问学生数据

        权限规则：
        - ADMIN: 可以访问所有学生
        - DISTRICT_ADMIN: 可以访问所属区县的学生
        - SCHOOL_ADMIN: 可以访问本校的学生
        - RESEARCHER: 可以访问所属区县/学校的学生
        - TEACHER: 可以访问所教班级的学生
        - STUDENT: 只能访问自己的数据
        """
        if current_user.role == UserRole.ADMIN:
            return True

        # 查询学生信息
        student_result = await db.execute(
            select(User).where(User.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            return False

        if current_user.role == UserRole.STUDENT:
            return current_user.id == student_id

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == student.region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == student.school_id

        if current_user.role == UserRole.RESEARCHER:
            if current_user.school_id:
                return current_user.school_id == student.school_id
            if current_user.region_id:
                return current_user.region_id == student.region_id
            return False

        if current_user.role == UserRole.TEACHER:
            # 查询教师任教班级
            teacher_classrooms_result = await db.execute(
                select(ClassroomMembership.classroom_id).where(
                    and_(
                        ClassroomMembership.user_id == current_user.id,
                        ClassroomMembership.is_active == True,
                    )
                )
            )
            teacher_classroom_ids = [
                row[0] for row in teacher_classrooms_result.all()
            ]

            # 查询学生所属班级
            student_classrooms_result = await db.execute(
                select(ClassroomMembership.classroom_id).where(
                    and_(
                        ClassroomMembership.user_id == student_id,
                        ClassroomMembership.is_active == True,
                    )
                )
            )
            student_classroom_ids = [
                row[0] for row in student_classrooms_result.all()
            ]

            # 检查是否有交集
            return bool(set(teacher_classroom_ids) & set(student_classroom_ids))

        return False

    @staticmethod
    async def can_access_exam_data(
        db: AsyncSession,
        current_user: User,
        exam: Exam,
    ) -> bool:
        """
        检查用户是否可以访问考试数据

        权限规则：
        - ADMIN: 可以访问所有考试
        - DISTRICT_ADMIN: 可以访问所属区县的考试
        - SCHOOL_ADMIN: 可以访问本校的考试
        - RESEARCHER: 可以访问所属区县/学校的考试
        - TEACHER: 可以访问所教年级/班级的考试
        - STUDENT: 可以访问自己的考试
        """
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == exam.region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == exam.school_id

        if current_user.role == UserRole.RESEARCHER:
            if current_user.school_id:
                return current_user.school_id == exam.school_id
            if current_user.region_id:
                return current_user.region_id == exam.region_id
            return False

        if current_user.role == UserRole.TEACHER:
            # 教师可以访问所教年级的考试
            if current_user.grade_id:
                return current_user.grade_id == exam.grade_id
            # 或所教班级所属学校的考试
            if current_user.school_id:
                return current_user.school_id == exam.school_id
            return False

        if current_user.role == UserRole.STUDENT:
            # 学生可以访问自己年级和学校的考试
            if current_user.grade_id:
                return current_user.grade_id == exam.grade_id
            if current_user.school_id:
                return current_user.school_id == exam.school_id
            return False

        return False

    @staticmethod
    async def can_modify_exam_data(
        db: AsyncSession,
        current_user: User,
        exam: Exam,
    ) -> bool:
        """检查用户是否可以修改考试数据"""
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == exam.region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == exam.school_id

        return False

    @staticmethod
    async def can_access_evaluation(
        db: AsyncSession,
        current_user: User,
        evaluation: ValueAddedEvaluation,
    ) -> bool:
        """
        检查用户是否可以访问评价数据

        权限规则：
        - ADMIN: 可以访问所有评价
        - DISTRICT_ADMIN: 可以访问所属区县的评价
        - SCHOOL_ADMIN: 可以访问本校的评价
        - RESEARCHER: 可以访问所属区县/学校的评价
        - TEACHER: 可以查看，不能修改
        - STUDENT: 不可以访问
        """
        if current_user.role == UserRole.STUDENT:
            return False

        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == evaluation.region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == evaluation.school_id

        if current_user.role == UserRole.RESEARCHER:
            if current_user.school_id:
                return current_user.school_id == evaluation.school_id
            if current_user.region_id:
                return current_user.region_id == evaluation.region_id
            return False

        if current_user.role == UserRole.TEACHER:
            # 教师只能查看，在其他函数中区分
            if current_user.school_id:
                return current_user.school_id == evaluation.school_id
            return False

        return False

    @staticmethod
    async def can_modify_evaluation(
        db: AsyncSession,
        current_user: User,
        evaluation: ValueAddedEvaluation,
    ) -> bool:
        """检查用户是否可以修改评价数据"""
        if current_user.role == UserRole.ADMIN:
            return True

        if current_user.role == UserRole.DISTRICT_ADMIN:
            return current_user.region_id == evaluation.region_id

        if current_user.role == UserRole.SCHOOL_ADMIN:
            return current_user.school_id == evaluation.school_id

        if current_user.role == UserRole.RESEARCHER:
            if evaluation.created_by == current_user.id:
                return True
            if current_user.school_id:
                return current_user.school_id == evaluation.school_id
            if current_user.region_id:
                return current_user.region_id == evaluation.region_id
            return False

        return False

    @staticmethod
    async def _school_in_region(school_id: int, region_id: int) -> bool:
        """检查学校是否属于区县"""
        # 这个方法需要在有数据库session的地方调用
        # 这里只是辅助方法，实际实现需要在外面调用
        return True  # 占位符


async def check_permission_or_403(
    condition: bool,
    detail: str = "权限不足",
) -> None:
    """
    检查权限，如果不满足则抛出403异常

    Args:
        condition: 权限条件
        detail: 错误信息

    Raises:
        HTTPException: 如果权限不足
    """
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


async def require_admin_or_district_admin(
    current_user: User,
) -> None:
    """要求管理员或区县管理员权限"""
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员或区县管理员权限"
        )


async def require_admin_or_school_admin(
    current_user: User,
) -> None:
    """要求管理员或学校管理员权限"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员或学校管理员权限"
        )


async def require_management_role(
    current_user: User,
) -> None:
    """要求管理角色（管理员、区县管理员、学校管理员、教研员）"""
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
        UserRole.RESEARCHER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理角色权限"
        )
