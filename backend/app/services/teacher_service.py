"""
教师教学任务服务

提供教师教学任务的CRUD操作和业务逻辑
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import (
    User,
    UserRole,
    School,
    Grade,
    Classroom,
    Subject,
    Semester,
    TeacherTeachingAssignment,
    TeachingAssignmentType,
)

from app.schemas.teacher import (
    TeacherTeachingAssignmentCreate,
    TeacherTeachingAssignmentUpdate,
)

logger = logging.getLogger(__name__)


class TeacherServiceError(Exception):
    """教师服务错误"""
    pass


class TeacherService:
    """教师教学任务服务"""

    @staticmethod
    async def create_assignment(
        db: AsyncSession,
        assignment_data: TeacherTeachingAssignmentCreate,
    ) -> TeacherTeachingAssignment:
        """
        创建教师教学任务

        Args:
            db: 数据库会话
            assignment_data: 教学任务创建数据

        Returns:
            创建的教学任务对象

        Raises:
            TeacherServiceError: 如果验证失败或创建失败
        """
        # 验证教师是否存在且角色为TEACHER
        teacher_result = await db.execute(
            select(User).where(User.id == assignment_data.teacher_id)
        )
        teacher = teacher_result.scalar_one_or_none()
        if not teacher:
            raise TeacherServiceError(f"教师ID {assignment_data.teacher_id} 不存在")
        if teacher.role != UserRole.TEACHER:
            raise TeacherServiceError(f"用户ID {assignment_data.teacher_id} 不是教师角色")

        # 验证学校是否存在
        school_result = await db.execute(
            select(School).where(School.id == assignment_data.school_id)
        )
        school = school_result.scalar_one_or_none()
        if not school:
            raise TeacherServiceError(f"学校ID {assignment_data.school_id} 不存在")

        # 验证年级是否存在
        grade_result = await db.execute(
            select(Grade).where(Grade.id == assignment_data.grade_id)
        )
        grade = grade_result.scalar_one_or_none()
        if not grade:
            raise TeacherServiceError(f"年级ID {assignment_data.grade_id} 不存在")

        # 验证班级是否存在
        classroom_result = await db.execute(
            select(Classroom).where(Classroom.id == assignment_data.classroom_id)
        )
        classroom = classroom_result.scalar_one_or_none()
        if not classroom:
            raise TeacherServiceError(f"班级ID {assignment_data.classroom_id} 不存在")

        # 验证班级是否属于指定学校
        if classroom.school_id != assignment_data.school_id:
            raise TeacherServiceError(
                f"班级ID {assignment_data.classroom_id} 不属于学校ID {assignment_data.school_id}"
            )

        # 验证班级是否属于指定年级
        if classroom.grade_id != assignment_data.grade_id:
            raise TeacherServiceError(
                f"班级ID {assignment_data.classroom_id} 不属于年级ID {assignment_data.grade_id}"
            )

        # 验证学科是否存在
        subject_result = await db.execute(
            select(Subject).where(Subject.id == assignment_data.subject_id)
        )
        subject = subject_result.scalar_one_or_none()
        if not subject:
            raise TeacherServiceError(f"学科ID {assignment_data.subject_id} 不存在")

        # 验证学期是否存在
        semester_result = await db.execute(
            select(Semester).where(Semester.id == assignment_data.semester_id)
        )
        semester = semester_result.scalar_one_or_none()
        if not semester:
            raise TeacherServiceError(f"学期ID {assignment_data.semester_id} 不存在")

        # 检查唯一约束：同一学期，同一教师，同一班级，同一学科只能有一条记录
        existing_result = await db.execute(
            select(TeacherTeachingAssignment).where(
                and_(
                    TeacherTeachingAssignment.teacher_id == assignment_data.teacher_id,
                    TeacherTeachingAssignment.semester_id == assignment_data.semester_id,
                    TeacherTeachingAssignment.classroom_id == assignment_data.classroom_id,
                    TeacherTeachingAssignment.subject_id == assignment_data.subject_id,
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise TeacherServiceError(
                f"该教师在此学期、此班级、此学科的教学任务已存在（ID: {existing.id}）"
            )

        # 创建教学任务
        assignment = TeacherTeachingAssignment(
            teacher_id=assignment_data.teacher_id,
            school_id=assignment_data.school_id,
            grade_id=assignment_data.grade_id,
            classroom_id=assignment_data.classroom_id,
            subject_id=assignment_data.subject_id,
            semester_id=assignment_data.semester_id,
            academic_year=assignment_data.academic_year,
            assignment_type=assignment_data.assignment_type,
            is_active=assignment_data.is_active,
        )

        try:
            db.add(assignment)
            await db.commit()
            await db.refresh(assignment)
            return assignment
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"创建教学任务失败: {e}")
            raise TeacherServiceError(f"创建教学任务失败: {str(e)}")

    @staticmethod
    async def get_assignment(
        db: AsyncSession,
        assignment_id: int,
        include_relations: bool = True,
    ) -> Optional[TeacherTeachingAssignment]:
        """
        获取单个教学任务

        Args:
            db: 数据库会话
            assignment_id: 教学任务ID
            include_relations: 是否加载关联对象

        Returns:
            教学任务对象，如果不存在返回None
        """
        query = select(TeacherTeachingAssignment).where(
            TeacherTeachingAssignment.id == assignment_id
        )

        if include_relations:
            query = query.options(
                selectinload(TeacherTeachingAssignment.teacher),
                selectinload(TeacherTeachingAssignment.school).selectinload(School.region),
                selectinload(TeacherTeachingAssignment.grade),
                selectinload(TeacherTeachingAssignment.classroom),
                selectinload(TeacherTeachingAssignment.subject),
                selectinload(TeacherTeachingAssignment.semester),
                selectinload(TeacherTeachingAssignment.position_type),
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_assignments(
        db: AsyncSession,
        teacher_id: Optional[int] = None,
        school_id: Optional[int] = None,
        grade_id: Optional[int] = None,
        classroom_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        semester_id: Optional[int] = None,
        region_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 10,
        include_relations: bool = True,
    ) -> Tuple[List[TeacherTeachingAssignment], int]:
        """
        获取教学任务列表

        Args:
            db: 数据库会话
            teacher_id: 教师ID筛选
            school_id: 学校ID筛选
            grade_id: 年级ID筛选
            classroom_id: 班级ID筛选
            subject_id: 学科ID筛选
            semester_id: 学期ID筛选
            region_id: 区域ID筛选（通过学校关联）
            is_active: 是否激活筛选
            page: 页码
            size: 每页数量
            include_relations: 是否加载关联对象

        Returns:
            (教学任务列表, 总记录数)
        """
        # 构建查询
        query = select(TeacherTeachingAssignment)
        count_query = select(func.count(TeacherTeachingAssignment.id))

        # 如果需要按区域筛选，需要 join School 表
        if region_id is not None:
            query = query.join(School, TeacherTeachingAssignment.school_id == School.id)
            count_query = count_query.join(School, TeacherTeachingAssignment.school_id == School.id)

        # 应用筛选条件
        conditions = []
        if teacher_id is not None:
            conditions.append(TeacherTeachingAssignment.teacher_id == teacher_id)
        if school_id is not None:
            conditions.append(TeacherTeachingAssignment.school_id == school_id)
        if grade_id is not None:
            conditions.append(TeacherTeachingAssignment.grade_id == grade_id)
        if classroom_id is not None:
            conditions.append(TeacherTeachingAssignment.classroom_id == classroom_id)
        if subject_id is not None:
            conditions.append(TeacherTeachingAssignment.subject_id == subject_id)
        if semester_id is not None:
            conditions.append(TeacherTeachingAssignment.semester_id == semester_id)
        if region_id is not None:
            conditions.append(School.region_id == region_id)
        if is_active is not None:
            conditions.append(TeacherTeachingAssignment.is_active == is_active)

        if conditions:
            filter_condition = and_(*conditions)
            query = query.where(filter_condition)
            count_query = count_query.where(filter_condition)

        # 加载关联对象
        if include_relations:
            query = query.options(
                selectinload(TeacherTeachingAssignment.teacher),
                selectinload(TeacherTeachingAssignment.school).selectinload(School.region),
                selectinload(TeacherTeachingAssignment.grade),
                selectinload(TeacherTeachingAssignment.classroom),
                selectinload(TeacherTeachingAssignment.subject),
                selectinload(TeacherTeachingAssignment.semester),
                selectinload(TeacherTeachingAssignment.position_type),
            )

        # 获取总数
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(
            TeacherTeachingAssignment.academic_year.desc(),
            TeacherTeachingAssignment.semester_id.desc(),
            TeacherTeachingAssignment.teacher_id,
        )

        # 执行查询
        result = await db.execute(query)
        assignments = result.scalars().all()

        return list(assignments), total

    @staticmethod
    async def update_assignment(
        db: AsyncSession,
        assignment_id: int,
        assignment_data: TeacherTeachingAssignmentUpdate,
    ) -> TeacherTeachingAssignment:
        """
        更新教学任务

        Args:
            db: 数据库会话
            assignment_id: 教学任务ID
            assignment_data: 更新数据

        Returns:
            更新后的教学任务对象

        Raises:
            TeacherServiceError: 如果任务不存在或更新失败
        """
        # 获取现有任务
        assignment_result = await db.execute(
            select(TeacherTeachingAssignment).where(
                TeacherTeachingAssignment.id == assignment_id
            )
        )
        assignment = assignment_result.scalar_one_or_none()
        if not assignment:
            raise TeacherServiceError(f"教学任务ID {assignment_id} 不存在")

        # 验证更新的字段
        if assignment_data.teacher_id is not None:
            teacher_result = await db.execute(
                select(User).where(User.id == assignment_data.teacher_id)
            )
            teacher = teacher_result.scalar_one_or_none()
            if not teacher:
                raise TeacherServiceError(f"教师ID {assignment_data.teacher_id} 不存在")
            if teacher.role != UserRole.TEACHER:
                raise TeacherServiceError(f"用户ID {assignment_data.teacher_id} 不是教师角色")
            assignment.teacher_id = assignment_data.teacher_id

        if assignment_data.school_id is not None:
            school_result = await db.execute(
                select(School).where(School.id == assignment_data.school_id)
            )
            school = school_result.scalar_one_or_none()
            if not school:
                raise TeacherServiceError(f"学校ID {assignment_data.school_id} 不存在")
            assignment.school_id = assignment_data.school_id

        if assignment_data.grade_id is not None:
            grade_result = await db.execute(
                select(Grade).where(Grade.id == assignment_data.grade_id)
            )
            grade = grade_result.scalar_one_or_none()
            if not grade:
                raise TeacherServiceError(f"年级ID {assignment_data.grade_id} 不存在")
            assignment.grade_id = assignment_data.grade_id

        if assignment_data.classroom_id is not None:
            classroom_result = await db.execute(
                select(Classroom).where(Classroom.id == assignment_data.classroom_id)
            )
            classroom = classroom_result.scalar_one_or_none()
            if not classroom:
                raise TeacherServiceError(f"班级ID {assignment_data.classroom_id} 不存在")
            assignment.classroom_id = assignment_data.classroom_id

        if assignment_data.subject_id is not None:
            subject_result = await db.execute(
                select(Subject).where(Subject.id == assignment_data.subject_id)
            )
            subject = subject_result.scalar_one_or_none()
            if not subject:
                raise TeacherServiceError(f"学科ID {assignment_data.subject_id} 不存在")
            assignment.subject_id = assignment_data.subject_id

        if assignment_data.semester_id is not None:
            semester_result = await db.execute(
                select(Semester).where(Semester.id == assignment_data.semester_id)
            )
            semester = semester_result.scalar_one_or_none()
            if not semester:
                raise TeacherServiceError(f"学期ID {assignment_data.semester_id} 不存在")
            assignment.semester_id = assignment_data.semester_id

        if assignment_data.academic_year is not None:
            assignment.academic_year = assignment_data.academic_year

        if assignment_data.assignment_type is not None:
            assignment.assignment_type = assignment_data.assignment_type

        if assignment_data.is_active is not None:
            assignment.is_active = assignment_data.is_active

        # 如果更新了关键字段，检查唯一约束
        if any([
            assignment_data.teacher_id is not None,
            assignment_data.semester_id is not None,
            assignment_data.classroom_id is not None,
            assignment_data.subject_id is not None,
        ]):
            existing_result = await db.execute(
                select(TeacherTeachingAssignment).where(
                    and_(
                        TeacherTeachingAssignment.teacher_id == assignment.teacher_id,
                        TeacherTeachingAssignment.semester_id == assignment.semester_id,
                        TeacherTeachingAssignment.classroom_id == assignment.classroom_id,
                        TeacherTeachingAssignment.subject_id == assignment.subject_id,
                        TeacherTeachingAssignment.id != assignment_id,  # 排除自己
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()
            if existing:
                raise TeacherServiceError(
                    f"该教师在此学期、此班级、此学科的教学任务已存在（ID: {existing.id}）"
                )

        try:
            await db.commit()
            await db.refresh(assignment)
            return assignment
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"更新教学任务失败: {e}")
            raise TeacherServiceError(f"更新教学任务失败: {str(e)}")

    @staticmethod
    async def delete_assignment(
        db: AsyncSession,
        assignment_id: int,
    ) -> bool:
        """
        删除教学任务

        Args:
            db: 数据库会话
            assignment_id: 教学任务ID

        Returns:
            True if deleted, False if not found

        Raises:
            TeacherServiceError: 如果删除失败
        """
        assignment_result = await db.execute(
            select(TeacherTeachingAssignment).where(
                TeacherTeachingAssignment.id == assignment_id
            )
        )
        assignment = assignment_result.scalar_one_or_none()
        if not assignment:
            return False

        try:
            await db.delete(assignment)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"删除教学任务失败: {e}")
            raise TeacherServiceError(f"删除教学任务失败: {str(e)}")

    @staticmethod
    async def get_teacher_assignments(
        db: AsyncSession,
        teacher_id: int,
        semester_id: Optional[int] = None,
        is_active: Optional[bool] = True,
        include_relations: bool = True,
    ) -> List[TeacherTeachingAssignment]:
        """
        获取某教师的所有教学任务

        Args:
            db: 数据库会话
            teacher_id: 教师ID
            semester_id: 学期ID筛选（可选）
            is_active: 是否激活筛选（默认True）
            include_relations: 是否加载关联对象

        Returns:
            教学任务列表
        """
        query = select(TeacherTeachingAssignment).where(
            TeacherTeachingAssignment.teacher_id == teacher_id
        )

        if semester_id is not None:
            query = query.where(
                TeacherTeachingAssignment.semester_id == semester_id
            )

        if is_active is not None:
            query = query.where(
                TeacherTeachingAssignment.is_active == is_active
            )

        if include_relations:
            query = query.options(
                selectinload(TeacherTeachingAssignment.teacher),
                selectinload(TeacherTeachingAssignment.school).selectinload(School.region),
                selectinload(TeacherTeachingAssignment.grade),
                selectinload(TeacherTeachingAssignment.classroom),
                selectinload(TeacherTeachingAssignment.subject),
                selectinload(TeacherTeachingAssignment.semester),
                selectinload(TeacherTeachingAssignment.position_type),
            )

        query = query.order_by(
            TeacherTeachingAssignment.academic_year.desc(),
            TeacherTeachingAssignment.semester_id.desc(),
            TeacherTeachingAssignment.classroom_id,
        )

        result = await db.execute(query)
        return list(result.scalars().all())
