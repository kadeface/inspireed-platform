"""
Student Import Strategy

Strategy for importing student exam mappings from Excel files.
Maps students to exam numbers for a specific exam.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import (
    User,
    Exam,
    ExamNumberMapping,
    Region,
    School,
    Grade,
    Classroom,
)
from .base_strategy import BaseImportStrategy
from ..import_exceptions import ValidationError, EntityNotFoundError


class StudentImportStrategy(BaseImportStrategy):
    """Student exam mapping import strategy"""

    # Column mapping (supports multiple aliases)
    COLUMN_MAPPING = {
        # Region name
        "市(区)": "region_name",
        "区域名称": "region_name",
        "区域": "region_name",
        "市": "region_name",
        "区": "region_name",
        # School name
        "学校": "school_name",
        "学校名称": "school_name",
        # School code
        "学校代码": "school_code",
        "代码": "school_code",
        # Student name
        "姓名": "full_name",
        "学生姓名": "full_name",
        # Student ID number
        "身份证号": "student_id_number",
        "学籍号": "student_id_number",
        "学生学籍号": "student_id_number",
        # Exam number
        "考生号": "exam_number",
        "考号": "exam_number",
        "考试号": "exam_number",
        "准考证号": "exam_number",
        # Classroom code
        "班级": "classroom_code",
        "班级编号": "classroom_code",
    }

    REQUIRED_COLUMNS = [
        "region_name", "school_name", "full_name",
        "student_id_number", "exam_number", "classroom_code"
    ]

    def get_column_mapping(self) -> Dict[str, str]:
        """Return Excel column name to field name mapping"""
        return self.COLUMN_MAPPING

    def get_required_columns(self) -> List[str]:
        """Return list of required field names"""
        return self.REQUIRED_COLUMNS

    async def validate_record(
        self,
        db: AsyncSession,
        record: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate student exam mapping record

        Args:
            db: Database session
            record: Raw record from Excel
            context: Import context (exam_id is required)

        Returns:
            (is_valid, error_message, validated_data)
        """
        # Validate exam_id exists in context
        exam_id = context.get("exam_id")
        if not exam_id:
            raise ValidationError(
                "缺少考试ID (exam_id)",
                row_number=record.get("row_number")
            )

        # Validate required fields
        region_name = record.get("region_name")
        if not region_name:
            raise ValidationError(
                "市(区)不能为空",
                row_number=record.get("row_number"),
                field="region_name"
            )

        school_name = record.get("school_name")
        if not school_name:
            raise ValidationError(
                "学校名称不能为空",
                row_number=record.get("row_number"),
                field="school_name"
            )

        full_name = record.get("full_name")
        if not full_name:
            raise ValidationError(
                "姓名不能为空",
                row_number=record.get("row_number"),
                field="full_name"
            )

        student_id_number = record.get("student_id_number")
        if not student_id_number:
            raise ValidationError(
                "身份证号/学籍号不能为空",
                row_number=record.get("row_number"),
                field="student_id_number"
            )

        exam_number = record.get("exam_number")
        if not exam_number:
            raise ValidationError(
                "考生号不能为空",
                row_number=record.get("row_number"),
                field="exam_number"
            )

        classroom_code = record.get("classroom_code")
        if not classroom_code:
            raise ValidationError(
                "班级编号不能为空",
                row_number=record.get("row_number"),
                field="classroom_code"
            )

        # Return validated data
        return True, None, {
            "exam_id": exam_id,
            "region_name": region_name,
            "school_name": school_name,
            "school_code": record.get("school_code"),
            "full_name": full_name,
            "student_id_number": student_id_number,
            "exam_number": exam_number,
            "classroom_code": classroom_code,
            "row_number": record.get("row_number")
        }

    async def import_record(
        self,
        db: AsyncSession,
        validated_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import student exam mapping record

        Args:
            db: Database session
            validated_data: Validated student data
            context: Import context

        Returns:
            Dict with status information
        """
        row_number = validated_data.get("row_number", 0)
        exam_id = validated_data["exam_id"]
        region_name = validated_data["region_name"]
        school_name = validated_data["school_name"]
        school_code = validated_data.get("school_code")
        student_id_number = validated_data["student_id_number"]
        exam_number = validated_data["exam_number"]
        classroom_code = validated_data["classroom_code"]

        # 1. Find region (using cache)
        cache_key = f"region:{region_name}"
        if cache_key in self._cache:
            region = self._cache[cache_key]
        else:
            region = await self.find_region(db, region_name)
            if not region:
                raise EntityNotFoundError(
                    f"区域 '{region_name}' 不存在",
                    row_number=row_number,
                    field="region_name"
                )
            self._cache[cache_key] = region

        # 2. Find school (using cache)
        cache_key = f"school:{school_name}:{region.id}"  # type: ignore
        if cache_key in self._cache:
            school = self._cache[cache_key]
        else:
            school = await self.find_school(
                db, school_name, int(region.id), school_code  # type: ignore
            )
            if not school:
                raise EntityNotFoundError(
                    f"学校 '{school_name}' 在区域 '{region_name}' 中不存在",
                    row_number=row_number,
                    field="school_name"
                )
            self._cache[cache_key] = school

        # 3. Find classroom
        classroom = await self.find_classroom(
            db, classroom_code, int(school.id)  # type: ignore
        )
        if not classroom:
            raise EntityNotFoundError(
                f"班级编号 '{classroom_code}' 在学校 '{school_name}' 中不存在或格式不正确",
                row_number=row_number,
                field="classroom_code"
            )

        # 4. Find student
        student = await self.find_student(db, student_id_number)
        if not student:
            raise EntityNotFoundError(
                f"学籍号 '{student_id_number}' 对应的学生不存在，请先创建学生账户",
                row_number=row_number,
                field="student_id_number"
            )

        # 5. Check if student belongs to classroom (warning only)
        if student.classroom_id != classroom.id:  # type: ignore
            self.logger.warning(
                f"学生 {student_id_number} 的班级ID ({student.classroom_id}) "
                f"与导入的班级ID ({classroom.id}) 不匹配"
            )

        # 6. Check if exam number mapping already exists
        existing_mapping = await self.find_existing_mapping(
            db, exam_id, exam_number
        )

        if existing_mapping:
            # Update existing mapping
            if existing_mapping.student_id != student.id:  # type: ignore
                raise ValidationError(
                    f"考生号 '{exam_number}' 已被其他学生使用",
                    row_number=row_number,
                    field="exam_number"
                )

            # Update redundant fields
            existing_mapping.student_id_number = student_id_number  # type: ignore
            existing_mapping.school_id = int(school.id)  # type: ignore
            existing_mapping.classroom_id = int(classroom.id)  # type: ignore
            await db.flush()

            return {
                "status": "updated",
                "id": int(existing_mapping.id),  # type: ignore
                "type": "exam_number_mapping"
            }
        else:
            # Create new mapping
            new_mapping = ExamNumberMapping(
                exam_id=exam_id,
                student_id=int(student.id),  # type: ignore
                exam_number=exam_number,
                student_id_number=student_id_number,
                school_id=int(school.id),  # type: ignore
                classroom_id=int(classroom.id),  # type: ignore
            )
            db.add(new_mapping)
            await db.flush()

            return {
                "status": "created",
                "id": int(new_mapping.id),  # type: ignore
                "type": "exam_number_mapping"
            }

    async def find_region(
        self,
        db: AsyncSession,
        region_name: str,
    ):
        """Find region by name"""
        # 1. Exact match
        result = await db.execute(
            select(Region).where(Region.name == region_name)
        )
        region = result.scalar_one_or_none()
        if region:
            return region

        # 2. Fuzzy match
        result = await db.execute(
            select(Region).where(Region.name.ilike(f"%{region_name}%"))
        )
        return result.scalar_one_or_none()

    async def find_school(
        self,
        db: AsyncSession,
        school_name: str,
        region_id: int,
        school_code: Optional[str] = None,
    ):
        """Find school by name/code/region"""
        # 1. Match by school code
        if school_code:
            result = await db.execute(
                select(School).where(School.code == school_code)
            )
            school = result.scalar_one_or_none()
            if school:
                return school

        # 2. Match by name + region
        result = await db.execute(
            select(School).where(
                and_(
                    School.name == school_name,
                    School.region_id == region_id
                )
            )
        )
        return result.scalar_one_or_none()

    def parse_classroom_code(self, classroom_code: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse classroom code to extract grade level and class sequence

        Examples:
            - 701 -> 7年级1班 (grade_level=7, class_seq=1) - 初一1班
            - 802 -> 8年级2班 (grade_level=8, class_seq=2) - 初二2班
            - 1001 -> 10年级1班 (grade_level=10, class_seq=1) - 高一1班
            - 1203 -> 12年级3班 (grade_level=12, class_seq=3) - 高三3班

        Args:
            classroom_code: Classroom code string

        Returns:
            (grade_level, class_seq) or (None, None) if parsing fails
        """
        if not classroom_code:
            return None, None

        code = str(classroom_code).strip()

        # 根据数字长度决定如何分割：
        # - 3位数字（如701）：第1位是年级，后2位是班级
        # - 4位数字（如1001）：前2位是年级，后2位是班级
        if len(code) == 3:
            # 3位数字：年级1位 + 班级2位
            grade_part = code[0]      # 第1位
            class_part = code[1:3]    # 后2位
        elif len(code) >= 4:
            # 4位及以上：前2位是年级，后2位是班级
            grade_part = code[0:2]    # 前2位
            class_part = code[-2:]    # 后2位
        else:
            return None, None

        try:
            grade_level = int(grade_part)
            class_seq = int(class_part)

            # Validate range: grade 1-12, class 1-99
            if 1 <= grade_level <= 12 and 1 <= class_seq <= 99:
                return grade_level, class_seq
        except ValueError:
            pass

        return None, None

    async def find_classroom(
        self,
        db: AsyncSession,
        classroom_code: str,
        school_id: int,
    ):
        """Find classroom by parsing code and matching to school/grade"""
        # Parse classroom code
        grade_level, class_seq = self.parse_classroom_code(classroom_code)
        if not grade_level or not class_seq:
            return None

        # Find grade
        result = await db.execute(
            select(Grade).where(Grade.level == grade_level)
        )
        grade = result.scalar_one_or_none()
        if not grade:
            return None

        # Find classroom: match by school_id, grade_id, and code/name
        classroom_name_patterns = [
            f"{grade.name}{class_seq}班",  # 五年级1班
            f"{grade.name}第{class_seq}班",  # 五年级第1班
            f"{class_seq}班",  # 1班
        ]

        for pattern in classroom_name_patterns:
            result = await db.execute(
                select(Classroom).where(
                    and_(
                        Classroom.school_id == school_id,
                        Classroom.grade_id == grade.id,
                        or_(
                            Classroom.name == pattern,
                            Classroom.name.ilike(f"%{pattern}%"),
                            Classroom.code == classroom_code,
                        )
                    )
                )
            )
            classroom = result.scalar_one_or_none()
            if classroom:
                return classroom

        # Try exact code match
        result = await db.execute(
            select(Classroom).where(
                and_(
                    Classroom.school_id == school_id,
                    Classroom.grade_id == grade.id,
                    Classroom.code == classroom_code,
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
            select(User).where(User.student_id_number == student_id_number)
        )
        return result.scalar_one_or_none()

    async def find_existing_mapping(
        self,
        db: AsyncSession,
        exam_id: int,
        exam_number: str,
    ):
        """Find existing exam number mapping"""
        result = await db.execute(
            select(ExamNumberMapping).where(
                and_(
                    ExamNumberMapping.exam_id == exam_id,
                    ExamNumberMapping.exam_number == exam_number
                )
            )
        )
        return result.scalar_one_or_none()
