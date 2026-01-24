"""
市级考号导入策略

导入市级考试院下发的考号映射表
Excel格式：校级考号 | 市级考号 | 姓名 | 学校
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.evaluation import ExamNumberMapping
from .base_strategy import BaseImportStrategy
from ..import_exceptions import ValidationError, EntityNotFoundError


logger = logging.getLogger(__name__)


class CityExamNumberImportStrategy(BaseImportStrategy):
    """市级考号导入策略

    导入市级考试院下发的正式考号，覆盖自动生成的考号
    """

    # Excel列名映射（支持多种列名别名）
    COLUMN_MAPPING = {
        "校级考号": "school_exam_number",
        "考号": "school_exam_number",  # 别名
        "市级考号": "city_exam_number",
        "准考证号": "city_exam_number",  # 别名
        "姓名": "student_name",
        "学生姓名": "student_name",  # 别名
        "学校": "school_name",
        "学校名称": "school_name",  # 别名
    }

    # 必填字段（字段名，不是列名）
    REQUIRED_COLUMNS = ["school_exam_number", "city_exam_number", "student_name"]

    def get_column_mapping(self) -> Dict[str, str]:
        """返回Excel列名到字段名的映射"""
        return self.COLUMN_MAPPING

    def get_required_columns(self) -> List[str]:
        """返回必填字段列表"""
        return self.REQUIRED_COLUMNS

    async def validate_record(
        self,
        db: AsyncSession,
        record: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """验证单条记录

        Args:
            db: 数据库会话
            record: Excel记录（已包含row_number）
            context: 上下文参数（必须包含exam_id）

        Returns:
            (is_valid, error_message, validated_data)

        Raises:
            ValidationError: 验证失败
            EntityNotFoundError: 实体不存在
        """
        # 获取exam_id
        exam_id = context.get("exam_id")
        if not exam_id:
            raise ValidationError(
                "缺少exam_id参数",
                row_number=record.get("row_number")
            )

        # 获取并验证校级考号
        school_exam_number = record.get("school_exam_number")
        if not school_exam_number:
            raise ValidationError(
                "校级考号不能为空",
                row_number=record.get("row_number"),
                field="school_exam_number"
            )

        school_exam_number = str(school_exam_number).strip()

        # 验证校级考号格式（8位数字）
        if not school_exam_number.isdigit() or len(school_exam_number) != 8:
            raise ValidationError(
                f"校级考号格式错误：{school_exam_number}，应为8位数字",
                row_number=record.get("row_number"),
                field="school_exam_number"
            )

        # 获取并验证市级考号
        city_exam_number = record.get("city_exam_number")
        if not city_exam_number:
            raise ValidationError(
                "市级考号不能为空",
                row_number=record.get("row_number"),
                field="city_exam_number"
            )

        city_exam_number = str(city_exam_number).strip()

        # 验证市级考号格式（10位数字）
        if not city_exam_number.isdigit() or len(city_exam_number) != 10:
            raise ValidationError(
                f"市级考号格式错误：{city_exam_number}，应为10位数字",
                row_number=record.get("row_number"),
                field="city_exam_number"
            )

        # 验证年级编码有效性（第1位：7=高一，8=高二，9=高三）
        grade_code = int(city_exam_number[0])
        if grade_code not in [7, 8, 9]:
            raise ValidationError(
                f"市级考号年级编码错误：{city_exam_number}，第1位应为7/8/9",
                row_number=record.get("row_number"),
                field="city_exam_number"
            )

        # 获取并验证姓名
        student_name = record.get("student_name")
        if not student_name:
            raise ValidationError(
                "姓名不能为空",
                row_number=record.get("row_number"),
                field="student_name"
            )

        student_name = str(student_name).strip()

        # 验证完成
        return (
            True,
            None,
            {
                "school_exam_number": school_exam_number,
                "city_exam_number": city_exam_number,
                "student_name": student_name,
                "school_name": record.get("school_name"),
                "row_number": record.get("row_number"),
            }
        )

    async def import_record(
        self,
        db: AsyncSession,
        validated_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """导入单条记录

        Args:
            db: 数据库会话
            validated_data: 验证后的数据
            context: 上下文参数

        Returns:
            导入结果字典

        Raises:
            EntityNotFoundError: 学生不存在
        """
        exam_id = context.get("exam_id")
        school_exam_number = validated_data["school_exam_number"]
        city_exam_number = validated_data["city_exam_number"]
        row_number = validated_data.get("row_number")

        self.logger.info(
            f"导入市级考号：校级考号={school_exam_number}, "
            f"市级考号={city_exam_number}, 考试ID={exam_id}"
        )

        # 通过校级考号（username）查找学生
        result = await db.execute(
            select(User).where(
                and_(
                    User.username == school_exam_number,
                    User.role == UserRole.STUDENT
                )
            )
        )
        student = result.scalar_one_or_none()

        if not student:
            raise EntityNotFoundError(
                f"学生不存在（校级考号: {school_exam_number}）",
                row_number=row_number,
                field="school_exam_number"
            )

        # 检查是否已存在考号映射
        existing = await db.execute(
            select(ExamNumberMapping).where(
                and_(
                    ExamNumberMapping.exam_id == exam_id,
                    ExamNumberMapping.student_id == student.id
                )
            )
        )
        existing_mapping = existing.scalar_one_or_none()

        if existing_mapping:
            # 更新现有映射（覆盖自动生成的考号）
            old_exam_number = existing_mapping.exam_number
            existing_mapping.exam_number = city_exam_number
            await db.flush()

            self.logger.info(
                f"更新考号映射：学生ID={student.id}, "
                f"旧考号={old_exam_number}, 新考号={city_exam_number}"
            )

            return {
                "status": "updated",
                "id": existing_mapping.id,
                "type": "city_exam_number_mapping",
                "student_name": student.full_name,
                "school_exam_number": school_exam_number,
                "old_exam_number": old_exam_number,
                "new_exam_number": city_exam_number,
                "row_number": row_number,
            }
        else:
            # 创建新映射
            new_mapping = ExamNumberMapping(
                exam_id=exam_id,
                student_id=student.id,
                exam_number=city_exam_number,
                student_id_number=student.student_id_number or "",
                school_id=student.school_id or 0,
                classroom_id=student.classroom_id or 0
            )
            db.add(new_mapping)
            await db.flush()

            self.logger.info(
                f"创建考号映射：学生ID={student.id}, "
                f"考号={city_exam_number}"
            )

            return {
                "status": "created",
                "id": new_mapping.id,
                "type": "city_exam_number_mapping",
                "student_name": student.full_name,
                "school_exam_number": school_exam_number,
                "exam_number": city_exam_number,
                "row_number": row_number,
            }
