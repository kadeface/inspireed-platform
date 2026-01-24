"""
Classroom Import Strategy

Strategy for importing classroom information from Excel files.
Supports dual-mode: school admin (no school column) vs district admin (with school column).
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import Region, School, Grade, Classroom
from .base_strategy import BaseImportStrategy
from ..import_exceptions import ValidationError, EntityNotFoundError


class ClassroomImportStrategy(BaseImportStrategy):
    """Classroom import strategy with dual-mode support"""

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
        # Grade name
        "年级名称": "grade_name",
        "年级": "grade_name",
        "年级名称*": "grade_name",
        # Classroom code
        "班级编号": "classroom_code",
        "班级编号*": "classroom_code",
        "班级代码": "classroom_code",
        "班级编码": "classroom_code",
        # Classroom name
        "班级名称": "classroom_name",
        "班级名称*": "classroom_name",
        "班级": "classroom_name",
        # Enrollment year
        "入学年份": "enrollment_year",
        "年份": "enrollment_year",
        "届别": "enrollment_year",
        # Capacity
        "班级容量": "capacity",
        "容量": "capacity",
        "计划人数": "capacity",
        # Description
        "班级描述": "description",
        "描述": "description",
        "备注": "description",
    }

    # School admin column mapping (no school columns)
    SCHOOL_COLUMN_MAPPING = {
        # Grade level
        "年级级别": "grade_level",
        "年级级别*": "grade_level",
        "级别": "grade_level",
        "level": "grade_level",
        # Grade name
        "年级名称": "grade_name",
        "年级": "grade_name",
        "年级名称*": "grade_name",
        # Classroom code
        "班级编号": "classroom_code",
        "班级编号*": "classroom_code",
        "班级代码": "classroom_code",
        "班级编码": "classroom_code",
        # Classroom name
        "班级名称": "classroom_name",
        "班级名称*": "classroom_name",
        "班级": "classroom_name",
        # Enrollment year
        "入学年份": "enrollment_year",
        "年份": "enrollment_year",
        "届别": "enrollment_year",
        # Capacity
        "班级容量": "capacity",
        "容量": "capacity",
        "计划人数": "capacity",
        # Description
        "班级描述": "description",
        "描述": "description",
        "备注": "description",
    }

    DISTRICT_REQUIRED_COLUMNS = ["school_name", "grade_level", "classroom_code"]
    SCHOOL_REQUIRED_COLUMNS = ["grade_level", "classroom_code"]

    def __init__(self):
        super().__init__()
        self._column_mapping = None
        self._required_columns = None

    async def parse_excel(
        self,
        file_path,
        context: Optional[Dict[str, Any]] = None
    ):
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
        # This shouldn't be called directly, but provide district mapping as default
        return self.DISTRICT_COLUMN_MAPPING

    def get_required_columns(self) -> List[str]:
        """Return list of required field names"""
        # This shouldn't be called directly, but provide district columns as default
        return self.DISTRICT_REQUIRED_COLUMNS

    async def validate_record(
        self,
        db: AsyncSession,
        record: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate classroom record

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
                    "学校名称不能为空",
                    row_number=record.get("row_number"),
                    field="school_name"
                )

        # Validate grade_level
        grade_level = record.get("grade_level")
        if not grade_level:
            raise ValidationError(
                "年级级别不能为空",
                row_number=record.get("row_number"),
                field="grade_level"
            )

        # Validate classroom_code
        classroom_code = record.get("classroom_code")
        if not classroom_code:
            raise ValidationError(
                "班级编号不能为空",
                row_number=record.get("row_number"),
                field="classroom_code"
            )

        # Parse classroom code to validate format
        parsed_grade, class_seq = self.parse_classroom_code(classroom_code)
        if not parsed_grade or not class_seq:
            raise ValidationError(
                f"班级编号 '{classroom_code}' 格式不正确（应为：年级级别+班级序号，如701表示7年级1班）",
                row_number=record.get("row_number"),
                field="classroom_code"
            )

        # Validate parsed grade matches provided grade
        if parsed_grade != grade_level:
            raise ValidationError(
                f"班级编号 '{classroom_code}' 中的年级级别 ({parsed_grade}) 与提供的年级级别 ({grade_level}) 不一致",
                row_number=record.get("row_number"),
                field="classroom_code"
            )

        # Return validated data
        validated = {
            "school_name": record.get("school_name") if not is_school_admin else None,
            "school_code": record.get("school_code"),
            "grade_level": grade_level,
            "grade_name": record.get("grade_name"),
            "classroom_code": classroom_code,
            "classroom_name": record.get("classroom_name"),
            "enrollment_year": record.get("enrollment_year"),
            "capacity": record.get("capacity"),
            "description": record.get("description"),
            "row_number": record.get("row_number")
        }

        return True, None, validated

    async def import_record(
        self,
        db: AsyncSession,
        validated_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import classroom record

        Args:
            db: Database session
            validated_data: Validated classroom data
            context: Import context (is_school_admin, school_id, region_id, etc.)

        Returns:
            Dict with status information
        """
        is_school_admin = context.get("is_school_admin", False)
        update_existing = context.get("update_existing", False)
        enrollment_year = context.get("enrollment_year")  # Unified setting
        capacity = context.get("capacity")  # Unified setting

        # 1. Get school_id
        if is_school_admin:
            school_id = context.get("school_id")
            if not school_id:
                raise ValidationError(
                    "学校管理员模式下必须提供school_id",
                    row_number=validated_data.get("row_number")
                )
        else:
            # District mode: find school
            school_name = validated_data["school_name"]
            school_code = validated_data.get("school_code")
            region_id = context.get("region_id")

            school = await self.find_school(
                db, school_name, region_id, school_code
            )

            if not school:
                raise EntityNotFoundError(
                    f"学校 '{school_name}' 未找到",
                    row_number=validated_data.get("row_number"),
                    field="school_name"
                )

            school_id = int(school.id)  # type: ignore

        # 2. Find grade
        grade_level = validated_data["grade_level"]
        grade = await self.find_grade_by_level(db, grade_level)

        if not grade:
            raise EntityNotFoundError(
                f"年级级别 {grade_level} 不存在",
                row_number=validated_data.get("row_number"),
                field="grade_level"
            )

        # 3. Parse classroom code
        classroom_code = validated_data["classroom_code"]
        parsed_grade, class_seq = self.parse_classroom_code(classroom_code)

        # 4. Generate classroom name if not provided
        grade_name = str(grade.name)  # Use database grade name
        classroom_name = validated_data.get("classroom_name")
        if not classroom_name:
            classroom_name = self.generate_classroom_name(grade_name, class_seq)

        # 5. Prepare classroom data
        classroom_data = {
            "name": classroom_name,
            "code": str(classroom_code).strip(),
            "school_id": school_id,
            "grade_id": int(grade.id),  # type: ignore
            "description": validated_data.get("description"),
            "is_active": True,
        }

        # 6. Handle enrollment_year (unified setting takes precedence)
        if enrollment_year is not None:
            classroom_data["enrollment_year"] = enrollment_year
        elif validated_data.get("enrollment_year"):
            classroom_data["enrollment_year"] = validated_data["enrollment_year"]

        # 7. Handle capacity (unified setting takes precedence)
        if capacity is not None:
            classroom_data["capacity"] = capacity
        elif validated_data.get("capacity"):
            classroom_data["capacity"] = validated_data["capacity"]

        # 8. Check if classroom exists
        existing = await self.find_existing_classroom(
            db, school_id, int(grade.id), classroom_data["code"], classroom_data["name"]  # type: ignore
        )

        if existing:
            if update_existing:
                # Update existing classroom
                for field, value in classroom_data.items():
                    if field not in ["school_id", "grade_id"]:  # Don't update school/grade
                        setattr(existing, field, value)
                await db.flush()
                await db.refresh(existing)
                return {
                    "status": "updated",
                    "id": int(existing.id),  # type: ignore
                    "type": "classroom"
                }
            else:
                # Skip existing classroom
                return {
                    "status": "skipped",
                    "id": int(existing.id),  # type: ignore
                    "type": "classroom"
                }
        else:
            # Create new classroom
            classroom = Classroom(**classroom_data)  # type: ignore
            db.add(classroom)
            await db.flush()
            return {
                "status": "created",
                "id": int(classroom.id),  # type: ignore
                "type": "classroom"
            }

    def parse_classroom_code(self, classroom_code: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse classroom code to extract grade level and class sequence

        Examples:
            - 701 -> (7, 1)
            - 1001 -> (10, 1)
            - 1203 -> (12, 3)

        Args:
            classroom_code: Classroom code string

        Returns:
            (grade_level, class_seq) or (None, None) if parsing fails
        """
        if not classroom_code:
            return None, None

        code = str(classroom_code).strip()

        # Try 1-digit class sequence first
        match1 = re.match(r'^(\d+)(\d{1})$', code)
        if match1:
            grade_part = match1.group(1)
            class_part = match1.group(2)
            try:
                grade_level = int(grade_part)
                class_seq = int(class_part)
                if 1 <= grade_level <= 12 and 1 <= class_seq <= 9:
                    return grade_level, class_seq
            except ValueError:
                pass

        # Try 2-digit class sequence
        match2 = re.match(r'^(\d+)(\d{2})$', code)
        if match2:
            grade_part = match2.group(1)
            class_part = match2.group(2)
            try:
                grade_level = int(grade_part)
                class_seq = int(class_part)
                # Validate: grade 1-12, class 10-99 or 01-09
                if 1 <= grade_level <= 12 and 10 <= class_seq <= 99:
                    return grade_level, class_seq
                # Handle 01-09 case
                if class_part.startswith('0'):
                    class_seq = int(class_part[1])
                    if 1 <= grade_level <= 12 and 1 <= class_seq <= 9:
                        return grade_level, class_seq
            except ValueError:
                pass

        return None, None

    async def find_grade_by_level(
        self,
        db: AsyncSession,
        grade_level: int
    ):
        """Find grade by level"""
        result = await db.execute(select(Grade).where(Grade.level == grade_level))
        return result.scalar_one_or_none()

    def generate_classroom_name(self, grade_name: str, class_seq: int) -> str:
        """Generate classroom name from grade name and sequence"""
        return f"{grade_name}{class_seq}班"

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
            result = await db.execute(
                select(School).where(School.code == school_code.strip())
            )
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

    async def find_existing_classroom(
        self,
        db: AsyncSession,
        school_id: int,
        grade_id: int,
        classroom_code: str,
        classroom_name: str
    ):
        """Find existing classroom by school, grade, code, or name"""
        result = await db.execute(
            select(Classroom).where(
                and_(
                    Classroom.school_id == school_id,
                    Classroom.grade_id == grade_id,
                    (Classroom.code == classroom_code) | (Classroom.name == classroom_name)
                )
            )
        )
        return result.scalar_one_or_none()
