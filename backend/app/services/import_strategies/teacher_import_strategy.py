"""
Teacher Import Strategy

Strategy for importing teacher teaching assignments from Excel files.
Supports auto-creation of teachers and semesters.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pypinyin import lazy_pinyin, Style
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

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
    TeacherPositionType,
)
from app.core.security import get_password_hash
from .base_strategy import BaseImportStrategy
from ..import_exceptions import ValidationError, EntityNotFoundError


logger = logging.getLogger(__name__)


class TeacherImportStrategy(BaseImportStrategy):
    """Teacher teaching assignment import strategy"""

    # Column mapping (supports multiple aliases)
    COLUMN_MAPPING = {
        # Teacher name
        "教师姓名": "teacher_name",
        "教师": "teacher_name",
        "教师姓名*": "teacher_name",
        "姓名": "teacher_name",
        # School name
        "学校名称": "school_name",
        "学校": "school_name",
        "学校名称*": "school_name",
        # Grade name/level
        "年级名称": "grade_name",
        "年级": "grade_name",
        "年级名称*": "grade_name",
        "年级级别": "grade_level",
        "年级级别*": "grade_level",
        "级别": "grade_level",
        # Classroom name/code
        "班级名称": "classroom_name",
        "班级": "classroom_name",
        "班级名称*": "classroom_name",
        "班级编码": "classroom_code",
        "班级编码*": "classroom_code",
        "班级编号": "classroom_code",
        "班级代码": "classroom_code",
        # Subject name
        "学科名称": "subject_name",
        "学科": "subject_name",
        "学科名称*": "subject_name",
        # Semester name/number
        "学期名称": "semester_name",
        "学期": "semester_name",
        "学期名称*": "semester_name",
        "学期编号": "semester_number",
        "学期编号*": "semester_number",
        "学期": "semester_number",
        # Academic year
        "学年": "academic_year",
        "学年*": "academic_year",
        # Assignment type
        "任务类型": "assignment_type",
        "任务类型*": "assignment_type",
        "类型": "assignment_type",
        # Is active
        "是否激活": "is_active",
        "激活": "is_active",
        "状态": "is_active",
    }

    def get_column_mapping(self) -> Dict[str, str]:
        """Return Excel column name to field name mapping"""
        return self.COLUMN_MAPPING

    def get_required_columns(self) -> List[str]:
        """Return list of required field names (at least one of alternatives)"""
        return ["teacher_name", "school_name", "grade_level", "subject_name",
                "academic_year", "assignment_type"]

    async def validate_record(
        self,
        db: AsyncSession,
        record: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate teacher assignment record

        Args:
            db: Database session
            record: Raw record from Excel
            context: Import context

        Returns:
            (is_valid, error_message, validated_data)
        """
        # Validate teacher name
        teacher_name = record.get("teacher_name")
        if not teacher_name:
            raise ValidationError(
                "教师姓名不能为空",
                row_number=record.get("row_number"),
                field="teacher_name"
            )

        # Validate school name
        school_name = record.get("school_name")
        if not school_name:
            raise ValidationError(
                "学校名称不能为空",
                row_number=record.get("row_number"),
                field="school_name"
            )

        # Validate grade (either name or level)
        grade_level = record.get("grade_level")
        grade_name = record.get("grade_name")
        if not grade_level and not grade_name:
            raise ValidationError(
                "年级名称或年级级别不能为空",
                row_number=record.get("row_number"),
                field="grade_level"
            )

        # Validate classroom (either name or code)
        classroom_name = record.get("classroom_name")
        classroom_code = record.get("classroom_code")
        if not classroom_name and not classroom_code:
            raise ValidationError(
                "班级名称或班级编码不能为空",
                row_number=record.get("row_number"),
                field="classroom_code"
            )

        # Validate subject
        subject_name = record.get("subject_name")
        if not subject_name:
            raise ValidationError(
                "学科名称不能为空",
                row_number=record.get("row_number"),
                field="subject_name"
            )

        # Validate academic year
        academic_year = record.get("academic_year")
        if not academic_year:
            raise ValidationError(
                "学年不能为空",
                row_number=record.get("row_number"),
                field="academic_year"
            )

        # Validate assignment type
        assignment_type = record.get("assignment_type")
        if not assignment_type:
            raise ValidationError(
                "任务类型不能为空",
                row_number=record.get("row_number"),
                field="assignment_type"
            )

        # Parse and validate academic year format
        try:
            self._parse_academic_year(academic_year)
        except ValueError as e:
            raise ValidationError(
                str(e),
                row_number=record.get("row_number"),
                field="academic_year"
            )

        # Return validated data
        return True, None, {
            "teacher_name": teacher_name,
            "school_name": school_name,
            "grade_name": grade_name,
            "grade_level": grade_level,
            "classroom_name": classroom_name,
            "classroom_code": classroom_code,
            "subject_name": subject_name,
            "semester_name": record.get("semester_name"),
            "semester_number": record.get("semester_number"),
            "academic_year": academic_year,
            "assignment_type": assignment_type,
            "is_active": self.parse_is_active(record.get("is_active")),
            "row_number": record.get("row_number")
        }

    async def import_record(
        self,
        db: AsyncSession,
        validated_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import teacher assignment record

        Args:
            db: Database session
            validated_data: Validated assignment data
            context: Import context (auto_create_teachers, auto_create_semesters)

        Returns:
            Dict with status information
        """
        auto_create_teachers = context.get("auto_create_teachers", False)
        auto_create_semesters = context.get("auto_create_semesters", False)
        update_existing = context.get("update_existing", False)

        row_number = validated_data.get("row_number", 0)

        # 1. Find school
        school_name = validated_data["school_name"]
        school = await self.find_school(db, school_name)
        if not school:
            raise EntityNotFoundError(
                f"学校 '{school_name}' 不存在",
                row_number=row_number,
                field="school_name"
            )

        # 2. Find or create grade
        grade_level = validated_data.get("grade_level")
        if grade_level:
            grade = await self.find_grade_by_level(db, grade_level)
            if not grade:
                raise EntityNotFoundError(
                    f"年级级别 {grade_level} 不存在",
                    row_number=row_number,
                    field="grade_level"
                )
        else:
            # Find by name
            grade_name = validated_data.get("grade_name")
            grade = await self.find_grade_by_name(db, grade_name)
            if not grade:
                raise EntityNotFoundError(
                    f"年级 '{grade_name}' 不存在",
                    row_number=row_number,
                    field="grade_name"
                )

        # 3. Find classroom
        classroom_code = validated_data.get("classroom_code")
        classroom_name = validated_data.get("classroom_name")

        if classroom_code:
            classroom = await self.find_classroom_by_code(
                db, classroom_code, int(school.id)  # type: ignore
            )
        else:
            classroom = await self.find_classroom_by_name(
                db, classroom_name, int(school.id), int(grade.id)  # type: ignore
            )

        if not classroom:
            raise EntityNotFoundError(
                f"班级 '{classroom_code or classroom_name}' 不存在",
                row_number=row_number,
                field="classroom_code"
            )

        # 4. Find subject
        subject_name = validated_data["subject_name"]
        subject = await self.find_subject(db, subject_name)
        if not subject:
            raise EntityNotFoundError(
                f"学科 '{subject_name}' 不存在",
                row_number=row_number,
                field="subject_name"
            )

        # 5. Find or create semester
        semester_number = validated_data.get("semester_number")
        semester_name = validated_data.get("semester_name")

        if semester_number:
            semester = await self.find_semester_by_number(
                db, semester_number, validated_data["academic_year"]
            )
            if not semester and auto_create_semesters:
                semester, _ = await self.create_semester_if_not_exists(
                    db, validated_data["academic_year"], semester_number,
                    int(school.region_id) if school.region_id else None  # type: ignore
                )
        else:
            semester = await self.find_semester_by_name(
                db, semester_name, validated_data["academic_year"]
            )

        if not semester:
            raise EntityNotFoundError(
                f"学期不存在",
                row_number=row_number,
                field="semester_number"
            )

        # 6. Find or create teacher
        teacher_name = validated_data["teacher_name"]
        teacher = await self.find_teacher(db, teacher_name)

        if not teacher:
            if auto_create_teachers:
                teacher, _ = await self.create_teacher_if_not_exists(
                    db, teacher_name, school, grade, classroom
                )
            else:
                raise EntityNotFoundError(
                    f"教师 '{teacher_name}' 不存在",
                    row_number=row_number,
                    field="teacher_name"
                )

        # 7. Parse assignment type
        assignment_type_str = validated_data["assignment_type"]
        assignment_type = self.parse_assignment_type(assignment_type_str)

        # 8. Check if assignment exists
        existing_assignment = await self.find_existing_assignment(
            db,
            int(teacher.id),  # type: ignore
            int(school.id),  # type: ignore
            int(grade.id),  # type: ignore
            int(classroom.id) if classroom else None,  # type: ignore
            int(subject.id),  # type: ignore
            int(semester.id),  # type: ignore
        )

        if existing_assignment:
            if update_existing:
                # Update existing assignment
                existing_assignment.assignment_type = assignment_type  # type: ignore
                existing_assignment.is_active = validated_data["is_active"]  # type: ignore
                await db.flush()

                return {
                    "status": "updated",
                    "id": int(existing_assignment.id),  # type: ignore
                    "type": "teaching_assignment"
                }
            else:
                return {
                    "status": "skipped",
                    "id": int(existing_assignment.id),  # type: ignore
                    "type": "teaching_assignment"
                }

        # 9. Create new assignment
        assignment = TeacherTeachingAssignment(
            teacher_id=int(teacher.id),  # type: ignore
            school_id=int(school.id),  # type: ignore
            grade_id=int(grade.id),  # type: ignore
            classroom_id=int(classroom.id) if classroom else None,  # type: ignore
            subject_id=int(subject.id),  # type: ignore
            semester_id=int(semester.id),  # type: ignore
            academic_year=validated_data["academic_year"],
            assignment_type=assignment_type,
            is_active=validated_data["is_active"],
        )

        db.add(assignment)
        await db.flush()

        return {
            "status": "created",
            "id": int(assignment.id),  # type: ignore
            "type": "teaching_assignment"
        }

    # ========== Helper Methods ==========

    async def find_teacher(
        self,
        db: AsyncSession,
        teacher_name: str,
    ):
        """Find teacher by name"""
        if not teacher_name:
            return None

        teacher_name = str(teacher_name).strip()

        result = await db.execute(
            select(User).where(
                and_(
                    User.role == UserRole.TEACHER,
                    or_(
                        User.full_name == teacher_name,
                        User.username == teacher_name,
                        User.email == teacher_name,
                    ),
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _name_to_pinyin(name: str) -> str:
        """Convert Chinese name to pinyin (lowercase, no spaces)"""
        if not name:
            return ""
        pinyin_list = lazy_pinyin(name, style=Style.NORMAL)
        return "".join(pinyin_list).lower()

    def _generate_username(
        self,
        teacher_name: str,
        school_code: str,
        classroom_code: Optional[str] = None,
        is_duplicate: bool = False,
    ) -> str:
        """Generate teacher username"""
        name_pinyin = self._name_to_pinyin(teacher_name)

        if is_duplicate and classroom_code:
            username = f"{name_pinyin}_{school_code}_{classroom_code}"
        else:
            username = name_pinyin

        # Clean special characters
        username = re.sub(r"[^a-z0-9_]", "", username)
        return username

    async def _ensure_unique_username(
        self,
        db: AsyncSession,
        base_username: str,
    ) -> str:
        """Ensure username is unique, append counter if needed"""
        username = base_username
        counter = 1

        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                return username

            username = f"{base_username}_{counter}"
            counter += 1

    async def _ensure_unique_email(
        self,
        db: AsyncSession,
        base_email: str,
    ) -> str:
        """Ensure email is unique, append counter if needed"""
        email = base_email
        counter = 1

        while True:
            result = await db.execute(select(User).where(User.email == email))
            if not result.scalar_one_or_none():
                return email

            email_local, email_domain = base_email.split("@")
            email = f"{email_local}_{counter}@{email_domain}"
            counter += 1

    async def create_teacher_if_not_exists(
        self,
        db: AsyncSession,
        teacher_name: str,
        school: School,
        grade: Grade,
        classroom: Optional[Classroom] = None,
        default_password: str = "Teacher@123456",
    ) -> Tuple[User, bool]:
        """Create teacher if not exists, return (teacher, is_newly_created)"""
        # Try to find existing teacher
        teacher = await self.find_teacher(db, teacher_name)
        if teacher:
            return teacher, False

        # Check for duplicate name
        classroom_code_str = None
        if classroom and classroom.code:  # type: ignore
            classroom_code_str = str(classroom.code)  # type: ignore

        is_duplicate = await self._check_duplicate_teacher_name(
            db, teacher_name,
            int(school.id),  # type: ignore
            int(grade.id),  # type: ignore
            classroom_code_str
        )

        # Generate username
        base_username = self._generate_username(
            teacher_name=teacher_name,
            school_code=str(school.code),
            classroom_code=classroom_code_str,
            is_duplicate=is_duplicate,
        )
        username = await self._ensure_unique_username(db, base_username)

        # Generate email
        base_email = f"{username}@inspireed.local"
        email = await self._ensure_unique_email(db, base_email)

        # Create teacher
        teacher = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(default_password),
            full_name=teacher_name,
            role=UserRole.TEACHER,
            is_active=True,
            school_id=int(school.id),  # type: ignore
            region_id=int(school.region_id) if school.region_id else None,  # type: ignore
            grade_id=int(grade.id) if grade else None,  # type: ignore
            classroom_id=int(classroom.id) if classroom else None,  # type: ignore
        )

        db.add(teacher)
        await db.flush()

        logger.info(f"Auto-created teacher: {teacher_name} (username={username})")

        return teacher, True

    async def _check_duplicate_teacher_name(
        self,
        db: AsyncSession,
        teacher_name: str,
        school_id: int,
        grade_id: int,
        classroom_code: Optional[str],
    ) -> bool:
        """Check if duplicate teacher name exists"""
        query = select(User).where(
            and_(
                User.role == UserRole.TEACHER,
                User.full_name == teacher_name,
                User.school_id == school_id,
                User.grade_id == grade_id,
            )
        )

        if classroom_code:
            classroom = await self.find_classroom_by_code(db, classroom_code, school_id)
            if classroom:
                query = query.where(User.classroom_id == classroom.id)

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    async def find_school(
        self,
        db: AsyncSession,
        school_name: str,
    ):
        """Find school by name"""
        if not school_name:
            return None

        school_name = str(school_name).strip()

        result = await db.execute(
            select(School).where(
                or_(
                    School.name == school_name,
                    School.name.ilike(f"%{school_name}%"),
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_grade_by_level(
        self,
        db: AsyncSession,
        grade_level: int,
    ):
        """Find grade by level"""
        result = await db.execute(
            select(Grade).where(Grade.level == grade_level)
        )
        return result.scalar_one_or_none()

    async def find_grade_by_name(
        self,
        db: AsyncSession,
        grade_name: str,
    ):
        """Find grade by name"""
        if not grade_name:
            return None

        result = await db.execute(
            select(Grade).where(Grade.name == grade_name)
        )
        return result.scalar_one_or_none()

    async def find_classroom_by_code(
        self,
        db: AsyncSession,
        classroom_code: str,
        school_id: int,
    ):
        """Find classroom by code and school"""
        result = await db.execute(
            select(Classroom).where(
                and_(
                    Classroom.school_id == school_id,
                    Classroom.code == classroom_code,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_classroom_by_name(
        self,
        db: AsyncSession,
        classroom_name: str,
        school_id: int,
        grade_id: int,
    ):
        """Find classroom by name, school, and grade"""
        if not classroom_name:
            return None

        result = await db.execute(
            select(Classroom).where(
                and_(
                    Classroom.school_id == school_id,
                    Classroom.grade_id == grade_id,
                    Classroom.name == classroom_name,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_subject(
        self,
        db: AsyncSession,
        subject_name: str,
    ):
        """Find subject by name"""
        if not subject_name:
            return None

        subject_name = str(subject_name).strip()

        result = await db.execute(
            select(Subject).where(
                or_(
                    Subject.name == subject_name,
                    Subject.name.ilike(f"%{subject_name}%"),
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_semester_by_number(
        self,
        db: AsyncSession,
        semester_number: int,
        academic_year: str,
    ):
        """Find semester by number and year"""
        # Convert number to type
        if semester_number == 1:
            semester_type = "up"
        elif semester_number == 2:
            semester_type = "down"
        else:
            return None

        result = await db.execute(
            select(Semester).where(
                and_(
                    Semester.year == academic_year,
                    Semester.semester_type == semester_type,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_semester_by_name(
        self,
        db: AsyncSession,
        semester_name: str,
        academic_year: str,
    ):
        """Find semester by name and year"""
        if not semester_name:
            return None

        result = await db.execute(
            select(Semester).where(
                and_(
                    Semester.name == semester_name,
                    Semester.year == academic_year,
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _parse_academic_year(academic_year: str) -> Tuple[int, int]:
        """Parse academic year string (YYYY-YYYY format)"""
        try:
            parts = academic_year.split("-")
            if len(parts) != 2:
                raise ValueError(f"学年格式错误：{academic_year}，应为 YYYY-YYYY 格式")
            start_year = int(parts[0])
            end_year = int(parts[1])
            if end_year != start_year + 1:
                raise ValueError(f"学年格式错误：{academic_year}，结束年份应为开始年份+1")
            return start_year, end_year
        except (ValueError, IndexError) as e:
            raise ValueError(f"学年格式错误：{academic_year}，应为 YYYY-YYYY 格式") from e

    def _calculate_semester_dates(
        self,
        start_year: int,
        semester_type: str,
    ) -> Tuple[datetime, datetime]:
        """Calculate semester start and end dates"""
        if semester_type == "up":
            start_date = datetime(start_year, 9, 1)
            end_date = datetime(start_year + 1, 1, 31)
        elif semester_type == "down":
            start_date = datetime(start_year + 1, 2, 1)
            end_date = datetime(start_year + 1, 7, 31)
        else:
            raise ValueError(f"无效的学期类型：{semester_type}")

        return start_date, end_date

    def _generate_semester_name(self, academic_year: str, semester_type: str) -> str:
        """Generate semester name"""
        if semester_type == "up":
            return f"{academic_year}学年上学期"
        elif semester_type == "down":
            return f"{academic_year}学年下学期"
        else:
            raise ValueError(f"无效的学期类型：{semester_type}")

    async def create_semester_if_not_exists(
        self,
        db: AsyncSession,
        academic_year: str,
        semester_number: int,
        region_id: Optional[int] = None,
    ) -> Tuple[Semester, bool]:
        """Create semester if not exists"""
        # Convert semester number to type
        if semester_number == 1:
            semester_type = "up"
        elif semester_number == 2:
            semester_type = "down"
        else:
            raise ValueError(f"无效的学期编号：{semester_number}，应为 1 或 2")

        # Try to find existing
        semester = await self.find_semester_by_number(
            db, semester_number, academic_year
        )
        if semester:
            return semester, False

        # Create new semester
        start_year, _ = self._parse_academic_year(academic_year)
        start_date, end_date = self._calculate_semester_dates(
            start_year, semester_type
        )
        semester_name = self._generate_semester_name(academic_year, semester_type)

        semester = Semester(
            year=academic_year,
            semester_type=semester_type,
            name=semester_name,
            start_date=start_date,
            end_date=end_date,
            is_current=False,
            region_id=region_id,
            is_active=True,
        )

        db.add(semester)
        await db.flush()

        logger.info(f"Auto-created semester: {semester_name}")

        return semester, True

    @staticmethod
    def parse_assignment_type(assignment_type_str: str) -> Optional[TeachingAssignmentType]:
        """Parse assignment type string"""
        if not assignment_type_str:
            return None

        assignment_type_str = str(assignment_type_str).strip().lower()

        if assignment_type_str in ["班主任", "head_teacher", "headteacher"]:
            return TeachingAssignmentType.HEAD_TEACHER
        elif assignment_type_str in ["学科教师", "subject_teacher", "subjectteacher", "任课教师"]:
            return TeachingAssignmentType.SUBJECT_TEACHER

        return None

    @staticmethod
    def parse_is_active(is_active_str: Optional[str]) -> bool:
        """Parse is_active field"""
        if not is_active_str:
            return True  # Default to active

        is_active_str = str(is_active_str).strip().lower()

        if is_active_str in ["是", "yes", "true", "1", "激活", "启用"]:
            return True
        elif is_active_str in ["否", "no", "false", "0", "非激活", "停用"]:
            return False

        return True  # Default to active

    async def find_existing_assignment(
        self,
        db: AsyncSession,
        teacher_id: int,
        school_id: int,
        grade_id: int,
        classroom_id: Optional[int],
        subject_id: int,
        semester_id: int,
    ):
        """Find existing teaching assignment"""
        conditions = [
            TeacherTeachingAssignment.teacher_id == teacher_id,
            TeacherTeachingAssignment.school_id == school_id,
            TeacherTeachingAssignment.grade_id == grade_id,
            TeacherTeachingAssignment.subject_id == subject_id,
            TeacherTeachingAssignment.semester_id == semester_id,
        ]

        if classroom_id is not None:
            conditions.append(TeacherTeachingAssignment.classroom_id == classroom_id)

        result = await db.execute(
            select(TeacherTeachingAssignment).where(and_(*conditions))
        )
        return result.scalar_one_or_none()
