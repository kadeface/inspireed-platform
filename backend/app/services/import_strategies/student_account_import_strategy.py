"""
Student Account Import Strategy

Strategy for importing student accounts from Excel files.
Uses similar format to classroom import: school name, grade level, classroom code.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole, Region, School, Grade, Classroom
from app.utils.username_generator import generate_username
from .base_strategy import BaseImportStrategy
from ..import_exceptions import ValidationError, EntityNotFoundError


class StudentAccountImportStrategy(BaseImportStrategy):
    """Student account import strategy with dual-mode support"""

    # District admin column mapping (includes school columns)
    DISTRICT_COLUMN_MAPPING = {
        # School name
        "学校名称": "school_name",
        "学校": "school_name",
        "学校名称*": "school_name",
        # School code
        "学校代码": "school_code",
        "代码": "school_code",
        # Grade level
        "年级级别": "grade_level",
        "年级级别*": "grade_level",
        "级别": "grade_level",
        "level": "grade_level",
        # Classroom code
        "班级编号": "classroom_code",
        "班级编号*": "classroom_code",
        "班级代码": "classroom_code",
        "班级编码": "classroom_code",
        # Student ID number (学籍号)
        "学籍号": "student_id_number",
        "学籍号*": "student_id_number",
        "身份证号": "student_id_number",
        "学生证号": "student_id_number",
        # Student name
        "姓名": "full_name",
        "姓名*": "full_name",
        "学生姓名": "full_name",
        # Username (optional, will use student_id_number if not provided)
        "用户名": "username",
        "学号": "username",
        "登录名": "username",
        # Email (optional, will auto-generate if not provided)
        "邮箱": "email",
        "电子邮件": "email",
        # Phone (optional)
        "手机号": "phone",
        "联系电话": "phone",
        # Gender (optional)
        "性别": "gender",
        # Password (optional, fallback to default)
        "密码": "password",
        "初始密码": "password",
    }

    # School admin column mapping (no school columns)
    SCHOOL_COLUMN_MAPPING = {
        # Grade level
        "年级级别": "grade_level",
        "年级级别*": "grade_level",
        "级别": "grade_level",
        "level": "grade_level",
        # Classroom code
        "班级编号": "classroom_code",
        "班级编号*": "classroom_code",
        "班级代码": "classroom_code",
        "班级编码": "classroom_code",
        # Student ID number
        "学籍号": "student_id_number",
        "学籍号*": "student_id_number",
        "身份证号": "student_id_number",
        "学生证号": "student_id_number",
        # Student name
        "姓名": "full_name",
        "姓名*": "full_name",
        "学生姓名": "full_name",
        # Username
        "用户名": "username",
        "学号": "username",
        "登录名": "username",
        # Email
        "邮箱": "email",
        "电子邮件": "email",
        # Phone
        "手机号": "phone",
        "联系电话": "phone",
        # Gender
        "性别": "gender",
        # Password (optional, fallback to default)
        "密码": "password",
        "初始密码": "password",
    }

    DISTRICT_REQUIRED_COLUMNS = [
        "school_name",
        "grade_level",
        "classroom_code",
        "student_id_number",
        "full_name",
    ]
    SCHOOL_REQUIRED_COLUMNS = ["grade_level", "classroom_code", "student_id_number", "full_name"]

    # Default password for new student accounts
    DEFAULT_PASSWORD = "123456"

    def __init__(self):
        super().__init__()
        self._column_mapping = None
        self._required_columns = None

    async def parse_excel(self, file_path, context: Optional[Dict[str, Any]] = None):
        """
        Override to support dual-mode column mapping

        Args:
            file_path: Path to Excel file
            context: Import context (must include is_school_admin)
        """
        if context is None:
            context = {}

        is_school_admin = context.get("is_school_admin", False)

        # Use appropriate column mapping based on mode
        if is_school_admin:
            self._column_mapping = self.SCHOOL_COLUMN_MAPPING
            self._required_columns = self.SCHOOL_REQUIRED_COLUMNS
        else:
            self._column_mapping = self.DISTRICT_COLUMN_MAPPING
            self._required_columns = self.DISTRICT_REQUIRED_COLUMNS

        # Call parent parse_excel with updated mappings
        return await super().parse_excel(file_path)

    def get_column_mapping(self) -> Dict[str, str]:
        """Return Excel column name to field name mapping"""
        return self.DISTRICT_COLUMN_MAPPING

    def get_required_columns(self) -> List[str]:
        """Return list of required field names"""
        return self.DISTRICT_REQUIRED_COLUMNS

    async def validate_record(
        self, db: AsyncSession, record: Dict[str, Any], context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate student account record

        Args:
            db: Database session
            record: Raw record from Excel
            context: Import context (is_school_admin, school_id, region_id, etc.)

        Returns:
            (is_valid, error_message, validated_data)
        """
        is_school_admin = context.get("is_school_admin", False)

        # Validate based on mode
        if not is_school_admin:
            # District mode: require school_name
            school_name = record.get("school_name")
            if not school_name:
                raise ValidationError(
                    "学校名称不能为空", row_number=record.get("row_number"), field="school_name"
                )
            # Convert to string and strip (Excel might provide various types)
            school_name = str(school_name).strip()
            if not school_name:
                raise ValidationError(
                    "学校名称不能为空", row_number=record.get("row_number"), field="school_name"
                )

        # Validate grade_level
        grade_level = record.get("grade_level")
        if not grade_level:
            raise ValidationError(
                "年级级别不能为空", row_number=record.get("row_number"), field="grade_level"
            )
        # Convert to int (Excel might provide as string or int)
        try:
            grade_level = int(grade_level)
        except (ValueError, TypeError):
            raise ValidationError(
                f"年级级别必须是数字，当前值: {grade_level}",
                row_number=record.get("row_number"),
                field="grade_level",
            )

        # Validate classroom_code
        classroom_code = record.get("classroom_code")
        if not classroom_code:
            raise ValidationError(
                "班级编号不能为空", row_number=record.get("row_number"), field="classroom_code"
            )
        # Convert to string (Excel might provide as int or string)
        classroom_code = str(classroom_code).strip()

        # Validate student_id_number
        student_id_number = record.get("student_id_number")
        if not student_id_number:
            raise ValidationError(
                "学籍号不能为空", row_number=record.get("row_number"), field="student_id_number"
            )

        # Validate full_name
        full_name = record.get("full_name")
        if not full_name:
            raise ValidationError("姓名不能为空", row_number=record.get("row_number"), field="full_name")

        # Return validated data
        # Handle school_code: convert to string if provided
        school_code = record.get("school_code")
        if school_code is not None:
            school_code = str(school_code).strip()

        return (
            True,
            None,
            {
                "school_name": school_name if not is_school_admin else None,
                "school_code": school_code,
                "grade_level": grade_level,
                "classroom_code": classroom_code,
                "student_id_number": str(student_id_number).strip(),
                "full_name": str(full_name).strip(),
                "username": record.get("username"),
                "email": record.get("email"),
                "phone": record.get("phone"),
                "gender": record.get("gender"),
                "password": record.get("password"),
                "row_number": record.get("row_number"),
            },
        )

    async def import_record(
        self, db: AsyncSession, validated_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import student account record

        Args:
            db: Database session
            validated_data: Validated student data
            context: Import context (is_school_admin, school_id, region_id, etc.)

        Returns:
            Dict with status information
        """
        is_school_admin = context.get("is_school_admin", False)
        update_existing = context.get("update_existing", False)

        # 1. Get school_id
        if is_school_admin:
            school_id = context.get("school_id")
            if not school_id:
                raise ValidationError(
                    "学校管理员模式下必须提供school_id", row_number=validated_data.get("row_number")
                )
        else:
            # District mode: find school
            school_name = validated_data["school_name"]
            school_code = validated_data.get("school_code")
            region_id = context.get("region_id")

            school = await self.find_school(db, school_name, region_id, school_code)

            if not school:
                raise EntityNotFoundError(
                    f"学校 '{school_name}' 未找到",
                    row_number=validated_data.get("row_number"),
                    field="school_name",
                )

            school_id = int(school.id)

        # 2. Find grade
        grade_level = validated_data["grade_level"]
        grade = await self.find_grade_by_level(db, grade_level)

        if not grade:
            raise EntityNotFoundError(
                f"年级级别 {grade_level} 不存在",
                row_number=validated_data.get("row_number"),
                field="grade_level",
            )

        # 3. Find classroom
        classroom_code = validated_data["classroom_code"]
        classroom = await self.find_classroom(db, classroom_code, school_id, int(grade.id))

        if not classroom:
            raise EntityNotFoundError(
                f"班级编号 '{classroom_code}' 在年级 {grade_level} 中不存在",
                row_number=validated_data.get("row_number"),
                field="classroom_code",
            )

        # 4. Generate username using new utility
        student_id_number = validated_data["student_id_number"]
        username = generate_username(school.code, student_id_number)

        # 5. Check if student already exists
        existing_student = await self.find_student(db, student_id_number)

        if existing_student:
            if update_existing:
                # Update existing student
                existing_student.full_name = validated_data["full_name"]
                existing_student.school_id = school_id
                existing_student.grade_id = int(grade.id)
                existing_student.classroom_id = int(classroom.id)
                existing_student.username = username  # Update username

                # Update email if provided
                if validated_data.get("email"):
                    existing_student.email = validated_data["email"]

                await db.flush()
                await db.refresh(existing_student)

                return {
                    "status": "updated",
                    "id": int(existing_student.id),
                    "type": "student_account",
                }
            else:
                # Skip existing student
                return {
                    "status": "skipped",
                    "id": int(existing_student.id),
                    "type": "student_account",
                }
        else:
            # Create new student account
            full_name = validated_data["full_name"]

            # Use generated username (ignore username from Excel if provided)
            # Generate email if not provided
            email = validated_data.get("email")
            if not email:
                email = f"{username}@inspireed.com"
            raw_password = validated_data.get("password")
            initial_password = (
                str(raw_password).strip() if raw_password is not None and str(raw_password).strip() else self.DEFAULT_PASSWORD
            )

            # Create student user
            from app.core.security import get_password_hash

            new_student = User(
                username=username,
                full_name=full_name,
                email=email,
                hashed_password=get_password_hash(initial_password),
                role=UserRole.STUDENT,
                school_id=school_id,
                grade_id=int(grade.id),
                classroom_id=int(classroom.id),
                region_id=int(school.region_id) if hasattr(school, "region_id") else None,  # type: ignore
                student_id_number=student_id_number,
                is_active=True,
            )

            db.add(new_student)
            await db.flush()

            return {
                "status": "created",
                "id": int(new_student.id),
                "type": "student_account",
                "username": username,
                "password": initial_password,
            }

    async def find_grade_by_level(self, db: AsyncSession, grade_level: int):
        """Find grade by level"""
        result = await db.execute(select(Grade).where(Grade.level == grade_level))
        return result.scalar_one_or_none()

    async def find_school(
        self,
        db: AsyncSession,
        school_name: str,
        region_id: Optional[int] = None,
        school_code: Optional[str] = None,
    ):
        """Find school by name/code/region"""
        # Priority 1: School code exact match
        if school_code:
            result = await db.execute(select(School).where(School.code == str(school_code).strip()))
            school = result.scalar_one_or_none()
            if school:
                return school

        # Priority 2: School name match
        if school_name:
            query = select(School).where(School.name == school_name.strip())
            if region_id:
                query = query.where(School.region_id == region_id)
            result = await db.execute(query)
            school = result.scalar_one_or_none()
            if school:
                return school

        # Priority 3: School name fuzzy match (only if no region specified)
        if school_name and not region_id:
            result = await db.execute(
                select(School).where(School.name.ilike(f"%{school_name.strip()}%"))
            )
            schools = result.scalars().all()
            if len(schools) == 1:  # Only return if unique match
                return schools[0]

        return None

    async def find_classroom(
        self,
        db: AsyncSession,
        classroom_code: str,
        school_id: int,
        grade_id: int,
    ):
        """Find classroom by code, school, and grade"""
        result = await db.execute(
            select(Classroom).where(
                and_(
                    Classroom.school_id == school_id,
                    Classroom.grade_id == grade_id,
                    Classroom.code == str(classroom_code).strip(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_student(
        self,
        db: AsyncSession,
        student_id_number: str,
    ):
        """Find student by student ID number"""
        result = await db.execute(
            select(User).where(
                and_(User.student_id_number == student_id_number, User.role == UserRole.STUDENT)
            )
        )
        return result.scalar_one_or_none()

    async def find_user_by_username(
        self,
        db: AsyncSession,
        username: str,
    ):
        """Find user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
