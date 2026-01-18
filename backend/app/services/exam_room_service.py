"""
考试考场安排服务

提供自动考场分配、考号生成、监考教师分配等功能
"""

import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.evaluation import Exam
from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor
from app.models.user import User, UserRole
from app.models.organization import Classroom, School
from app.models.room import Room
from app.schemas.exam_room import AutoAssignRoomsRequest, AutoAssignProctorsRequest
from app.services.exam_number_service import ExamNumberService

logger = logging.getLogger(__name__)


class ExamRoomService:
    """考场安排服务"""

    async def auto_assign_rooms(
        self, exam_id: int, request: AutoAssignRoomsRequest, db: AsyncSession
    ) -> List[ExamRoom]:
        """自动分配考场

        Args:
            exam_id: 考试ID
            request: 自动分配请求参数
            db: 数据库会话

        Returns:
            创建的考场列表

        Raises:
            ValueError: 考试不存在或学生数量为0
        """
        logger.info(f"Auto-assigning rooms for exam {exam_id}")

        # 1. 获取考试信息
        result = await db.execute(
            select(Exam).options(selectinload(Exam.exam_subjects)).where(Exam.id == exam_id)
        )
        exam = result.scalar_one_or_none()
        if not exam:
            raise ValueError("考试不存在")

        logger.info(
            f"Exam {exam_id} details: name={exam.name}, "
            f"school_id={exam.school_id}, grade_id={exam.grade_id}, "
            f"exam_type={exam.exam_type}"
        )

        # 2. 获取要分配的学生
        students = await self._get_exam_students(exam, db)

        if not students:
            raise ValueError("没有找到可分配的学生")

        # 3. 计算需要的考场数量
        num_students = len(students)
        capacity_per_room = request.capacity_per_room
        num_rooms = (num_students + capacity_per_room - 1) // capacity_per_room

        logger.info(f"Assigning {num_students} students to {num_rooms} rooms")

        # 4. 创建考场
        exam_rooms = []
        for i in range(num_rooms):
            room = ExamRoom(
                exam_id=exam_id,
                name=f"第{i+1}考场",
                school_id=exam.school_id or 1,  # 从exam获取school_id
                capacity=capacity_per_room,
                arrangement_type=request.arrangement_type,
                seat_pattern=request.seat_pattern,
                seat_count=0,  # 将在分配学生后更新
            )

            if request.use_existing_rooms:
                # 尝试找到可用的教室
                assigned_room = await self._find_available_room(
                    exam.school_id or 1, capacity_per_room, db
                )
                if assigned_room:
                    room.room_id = assigned_room.id
                    room.name = assigned_room.name

            db.add(room)
            await db.flush()  # 获取room.id

            exam_rooms.append(room)

        await db.commit()

        # 5. 将学生分配到考场（同时生成考号）
        await self._assign_students_to_rooms(exam_rooms, students, request, db, exam_id, exam)

        logger.info(f"Successfully created {len(exam_rooms)} exam rooms")
        return exam_rooms

    async def _get_exam_students(self, exam: Exam, db: AsyncSession) -> List[User]:
        """获取考试的学生

        从ExamNumberMapping获取学生，如果没有则根据grade_id获取

        对于区县级考试（school_id为None），获取该年级所有学生
        对于校级考试（school_id有值），只获取该校的学生
        """
        # 首先尝试从ExamNumberMapping获取
        from app.models.evaluation import ExamNumberMapping

        result = await db.execute(
            select(User)
            .join(ExamNumberMapping, User.id == ExamNumberMapping.student_id)
            .where(ExamNumberMapping.exam_id == exam.id)
            .order_by(User.classroom_id, User.id)
        )
        students = list(result.scalars().all())

        logger.info(f"Found {len(students)} students from ExamNumberMapping for exam {exam.id}")

        if not students:
            # 如果没有ExamNumberMapping，根据年级和学校/区县获取
            logger.info(
                f"No ExamNumberMapping found. Falling back to grade/school query. "
                f"Exam grade_id={exam.grade_id}, school_id={exam.school_id}, region_id={exam.region_id}"
            )

            # 构建查询条件
            conditions = [User.role == UserRole.STUDENT, User.grade_id == exam.grade_id]

            # 如果指定了学校，只查询该校的学生
            if exam.school_id:
                conditions.append(User.school_id == exam.school_id)
            # 如果指定了区县，查询该区县的学生
            elif exam.region_id:
                conditions.append(User.region_id == exam.region_id)

            result = await db.execute(
                select(User)
                .where(and_(*conditions))
                .order_by(User.school_id, User.classroom_id, User.id)
            )
            students = list(result.scalars().all())

            logger.info(
                f"Found {len(students)} students from grade/school/region query. "
                f"Filter by: school_id={exam.school_id}, region_id={exam.region_id}"
            )

        return students

    async def _find_available_room(
        self, school_id: int, min_capacity: int, db: AsyncSession
    ) -> Optional[Room]:
        """查找可用的教室

        选择容量满足要求的最小教室
        """
        result = await db.execute(
            select(Room)
            .where(and_(Room.school_id == school_id, Room.capacity >= min_capacity))
            .order_by(Room.capacity.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _assign_students_to_rooms(
        self,
        exam_rooms: List[ExamRoom],
        students: List[User],
        request: AutoAssignRoomsRequest,
        db: AsyncSession,
        exam_id: int,
        exam: Exam,  # 添加 exam 参数
    ):
        """将学生分配到考场

        根据arrangement_type选择分配策略：
        - by_class: 按班级编排（同班学生在一起）
        - mixed: 混排编排（不同班级学生混合）
        """
        room_capacity = request.capacity_per_room

        if request.arrangement_type == "by_class":
            # 按班级编排
            await self._assign_by_class(exam_rooms, students, room_capacity, db, exam_id, exam)
        else:
            # 混排编排
            await self._assign_mixed(exam_rooms, students, room_capacity, db, exam_id, exam)

    async def _assign_by_class(
        self,
        exam_rooms: List[ExamRoom],
        students: List[User],
        capacity: int,
        db: AsyncSession,
        exam_id: int,
        exam: Exam,
    ):
        """按班级分配学生

        将同班学生分配到同一考场，直到考场满
        """
        from app.models.evaluation import ExamNumberMapping

        room_index = 0
        room = exam_rooms[room_index]
        current_seat = 1

        # 获取学校代码（用于市级考号转换）
        school = None
        if exam.exam_level in ["district", "city"]:
            if exam.school_id:
                result = await db.execute(select(School).where(School.id == exam.school_id))
                school = result.scalar_one_or_none()
            elif students and students[0].school_id:
                # 使用第一个学生的学校
                result = await db.execute(select(School).where(School.id == students[0].school_id))
                school = result.scalar_one_or_none()

        for student in students:
            # 检查考场是否已满
            if current_seat > capacity:
                room_index += 1
                if room_index >= len(exam_rooms):
                    break
                room = exam_rooms[room_index]
                current_seat = 1

            # 根据考试级别选择考号格式
            if exam.exam_level == "school":
                # 学校级考试：直接使用校级考号（username）
                exam_number = student.username
            elif exam.exam_level in ["district", "city"]:
                # 区县/市级考试：转换为市级考号格式
                if school and school.code:
                    try:
                        exam_number = ExamNumberService.school_to_city_exam_number(
                            school_exam_number=student.username,
                            school_code=school.code,
                            exam_date=exam.exam_date
                        )
                    except ValueError as e:
                        logger.warning(f"考号转换失败，使用校级考号: {e}")
                        exam_number = student.username
                else:
                    logger.warning(f"学校代码不存在，使用校级考号")
                    exam_number = student.username
            else:
                # 默认使用校级考号
                exam_number = student.username

            # 创建座位分配
            seat = ExamRoomStudent(
                room_id=room.id,
                student_id=student.id,
                exam_number=exam_number,  # 使用 username 作为考号
                seat_number=current_seat,
                student_id_number=student.student_id_number,
                student_name=student.full_name,
                school_id=student.school_id,
                classroom_id=student.classroom_id,
            )
            db.add(seat)

            # 创建考号映射
            mapping = ExamNumberMapping(
                exam_id=exam_id,
                student_id=student.id,
                exam_number=exam_number,  # 使用 username 作为考号
                student_id_number=student.student_id_number,
                school_id=student.school_id,
                classroom_id=student.classroom_id,
            )
            db.add(mapping)

            current_seat += 1

        # 更新考场座位数和考号范围
        for idx, room in enumerate(exam_rooms, 1):
            # 获取该考场的座位数
            result = await db.execute(
                select(func.count(ExamRoomStudent.id)).where(ExamRoomStudent.room_id == room.id)
            )
            seat_count = result.scalar() or 0

            room.seat_count = seat_count

            # 获取该考场的考号范围
            numbers_result = await db.execute(
                select(ExamRoomStudent.exam_number)
                .where(ExamRoomStudent.room_id == room.id)
                .order_by(ExamRoomStudent.seat_number)
            )
            numbers = [n[0] for n in numbers_result.all()]
            if numbers:
                room.exam_number_start = numbers[0]
                room.exam_number_end = numbers[-1]

        await db.commit()

    async def _assign_mixed(
        self,
        exam_rooms: List[ExamRoom],
        students: List[User],
        capacity: int,
        db: AsyncSession,
        exam_id: int,
        exam: Exam,
    ):
        """混排分配学生

        使用轮询方式将学生分配到不同考场
        """
        from app.models.evaluation import ExamNumberMapping

        # 获取学校代码（用于市级考号转换）
        school = None
        if exam.exam_level in ["district", "city"]:
            if exam.school_id:
                result = await db.execute(select(School).where(School.id == exam.school_id))
                school = result.scalar_one_or_none()
            elif students and students[0].school_id:
                # 使用第一个学生的学校
                result = await db.execute(select(School).where(School.id == students[0].school_id))
                school = result.scalar_one_or_none()

        # 简单轮询混排
        for i, student in enumerate(students):
            room_index = i % len(exam_rooms)
            room = exam_rooms[room_index]
            seat_number = (i // len(exam_rooms)) + 1

            if seat_number > capacity:
                break

            # 根据考试级别选择考号格式
            if exam.exam_level == "school":
                # 学校级考试：直接使用校级考号（username）
                exam_number = student.username
            elif exam.exam_level in ["district", "city"]:
                # 区县/市级考试：转换为市级考号格式
                if school and school.code:
                    try:
                        exam_number = ExamNumberService.school_to_city_exam_number(
                            school_exam_number=student.username,
                            school_code=school.code,
                            exam_date=exam.exam_date
                        )
                    except ValueError as e:
                        logger.warning(f"考号转换失败，使用校级考号: {e}")
                        exam_number = student.username
                else:
                    logger.warning(f"学校代码不存在，使用校级考号")
                    exam_number = student.username
            else:
                # 默认使用校级考号
                exam_number = student.username

            seat = ExamRoomStudent(
                room_id=room.id,
                student_id=student.id,
                exam_number=exam_number,  # 使用 username 作为考号
                seat_number=seat_number,
                student_id_number=student.student_id_number,
                student_name=student.full_name,
                school_id=student.school_id,
                classroom_id=student.classroom_id,
            )
            db.add(seat)

            # 创建考号映射
            mapping = ExamNumberMapping(
                exam_id=exam_id,
                student_id=student.id,
                exam_number=exam_number,  # 使用 username 作为考号
                student_id_number=student.student_id_number,
                school_id=student.school_id,
                classroom_id=student.classroom_id,
            )
            db.add(mapping)

        # 更新考场座位数和考号范围
        for room in exam_rooms:
            # 获取该考场的座位数
            result = await db.execute(
                select(func.count(ExamRoomStudent.id)).where(ExamRoomStudent.room_id == room.id)
            )
            seat_count = result.scalar() or 0

            room.seat_count = seat_count

            # 获取该考场的考号范围
            numbers_result = await db.execute(
                select(ExamRoomStudent.exam_number)
                .where(ExamRoomStudent.room_id == room.id)
                .order_by(ExamRoomStudent.seat_number)
            )
            numbers = [n[0] for n in numbers_result.all()]
            if numbers:
                room.exam_number_start = numbers[0]
                room.exam_number_end = numbers[-1]

        await db.commit()

    async def auto_assign_proctors(
        self, exam_id: int, request: AutoAssignProctorsRequest, db: AsyncSession
    ) -> List[ExamProctor]:
        """自动分配监考教师

        每个考场分配2名监考（1主监考 + 1副监考）

        Args:
            exam_id: 考试ID
            request: 自动分配请求参数
            db: 数据库会话

        Returns:
            创建的监考分配列表

        Raises:
            ValueError: 教师数量不足
        """
        logger.info(f"Auto-assigning proctors for exam {exam_id}")

        # 1. 获取考场
        result = await db.execute(select(ExamRoom).where(ExamRoom.exam_id == exam_id))
        rooms = result.scalars().all()

        if not rooms:
            raise ValueError("考试还没有创建考场")

        # 2. 获取考试信息
        exam = await db.get(Exam, exam_id)
        if not exam:
            raise ValueError("考试不存在")

        # 3. 获取可用教师
        teachers_query = select(User).where(User.role == UserRole.TEACHER)

        if request.same_school_only and exam.school_id:
            teachers_query = teachers_query.where(User.school_id == exam.school_id)

        teachers_result = await db.execute(teachers_query)
        teachers = list(teachers_result.scalars().all())

        required_proctors = len(rooms) * 2
        if len(teachers) < required_proctors:
            raise ValueError(f"教师数量不足：需要 {required_proctors} 名教师，当前 {len(teachers)} 名")

        # 4. 为每个考场分配2名监考
        proctors = []
        used_teacher_ids = set()

        for room in rooms:
            # 获取考场学生以检查冲突
            students_result = await db.execute(
                select(ExamRoomStudent).where(ExamRoomStudent.room_id == room.id)
            )
            students = students_result.scalars().all()
            student_class_ids = set(s.classroom_id for s in students if s.classroom_id)

            # 查找合适的监考教师
            primary_teacher, assistant_teacher = await self._find_proctors_for_room(
                teachers, used_teacher_ids, student_class_ids, request, db
            )

            # 创建监考分配
            primary = ExamProctor(
                room_id=room.id, user_id=primary_teacher.id, proctor_type="primary"
            )

            assistant = ExamProctor(
                room_id=room.id, user_id=assistant_teacher.id, proctor_type="assistant"
            )

            db.add(primary)
            db.add(assistant)
            proctors.extend([primary, assistant])

            used_teacher_ids.add(primary_teacher.id)
            used_teacher_ids.add(assistant_teacher.id)

        await db.commit()
        logger.info(f"Successfully assigned {len(proctors)} proctors to {len(rooms)} rooms")
        return proctors

    async def _find_proctors_for_room(
        self,
        teachers: List[User],
        used_teacher_ids: set,
        student_class_ids: set,
        request: AutoAssignProctorsRequest,
        db: AsyncSession,
    ):
        """为考场查找合适的监考教师

        Args:
            teachers: 可用教师列表
            used_teacher_ids: 已使用的教师ID集合
            student_class_ids: 考场中学生所在的班级ID集合
            request: 分配请求参数
            db: 数据库会话

        Returns:
            (主监考, 副监考)
        """
        available = []

        for teacher in teachers:
            if teacher.id in used_teacher_ids:
                continue

            # 检查是否应避免该教师监考此考场
            if request.avoid_own_class:
                # 检查教师是否是该考场中任一班级的班主任
                if student_class_ids:
                    classrooms_result = await db.execute(
                        select(Classroom).where(
                            and_(
                                Classroom.head_teacher_id == teacher.id,
                                Classroom.id.in_(student_class_ids),
                            )
                        )
                    )
                    teacher_classes = list(classrooms_result.scalars().all())

                    if teacher_classes:
                        continue  # 跳过该教师

            available.append(teacher)
            if len(available) >= 2:
                break

        if len(available) < 2:
            # 回退：直接使用前两名教师
            unused_teachers = [t for t in teachers if t.id not in used_teacher_ids]
            if len(unused_teachers) >= 2:
                return unused_teachers[0], unused_teachers[1]
            else:
                # 实在没有足够的教师
                return available[0] if available else teachers[0], None

        return available[0], available[1]
