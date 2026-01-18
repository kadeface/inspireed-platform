"""
考号生成和转换服务

支持校级考号和市级考号的相互转换：
- 校级考号格式：{入学年份}{班级编号:02d}{流水号:03d}
  例如：20250101（2025年入学，01班，01号）
- 市级考号格式：{年级编码}{学校代码}{班级编号:02d}{流水号:03d}
  例如：7783190101（7=高一，78319=学校代码，01班，01号）

年级编码映射：
- 7: 高一（Grade 1）
- 8: 高二（Grade 2）
- 9: 高三（Grade 3）
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import School

logger = logging.getLogger(__name__)


class ExamNumberService:
    """考号生成和转换服务"""

    # 年级编码映射（高中）
    GRADE_CODE_MAP = {
        1: 7,  # 高一
        2: 8,  # 高二
        3: 9,  # 高三
    }

    # 反向映射（年级编码 → 年级）
    CODE_GRADE_MAP = {
        7: 1,  # 高一
        8: 2,  # 高二
        9: 3,  # 高三
    }

    @staticmethod
    def get_academic_year(date: datetime) -> int:
        """获取日期所属的学年年份

        Args:
            date: 日期

        Returns:
            学年年份（例如：2025年9月-2026年8月返回2025）

        Examples:
            >>> get_academic_year(datetime(2026, 1, 15))
            2025
            >>> get_academic_year(datetime(2026, 9, 1))
            2026
        """
        year = date.year
        # 9月1日及之后属于下一学年
        if date.month >= 9:
            return year
        else:
            return year - 1

    @staticmethod
    def calculate_grade_level(enrollment_year: int, exam_date: datetime) -> int:
        """计算年级（按学年）

        Args:
            enrollment_year: 入学学年（例如：2025表示2025-2026学年入学）
            exam_date: 考试日期

        Returns:
            年级（1=高一，2=高二，3=高三）

        Examples:
            >>> calculate_grade_level(2025, datetime(2026, 1, 15))
            1  # 高一
            >>> calculate_grade_level(2025, datetime(2026, 9, 1))
            2  # 高二
        """
        exam_academic_year = ExamNumberService.get_academic_year(exam_date)
        grade_level = exam_academic_year - enrollment_year + 1

        # 确保年级在合理范围内
        if grade_level < 1:
            grade_level = 1
        elif grade_level > 3:
            grade_level = 3

        return grade_level

    @staticmethod
    def get_grade_code(enrollment_year: int, exam_date: datetime) -> int:
        """从入学年份获取年级编码

        Args:
            enrollment_year: 入学学年
            exam_date: 考试日期

        Returns:
            年级编码（7=高一，8=高二，9=高三）
        """
        grade_level = ExamNumberService.calculate_grade_level(enrollment_year, exam_date)
        return ExamNumberService.GRADE_CODE_MAP.get(grade_level, 7)

    @staticmethod
    def school_to_city_exam_number(
        school_exam_number: str,
        school_code: str,
        exam_date: datetime
    ) -> str:
        """校级考号转市级考号

        Args:
            school_exam_number: 校级考号（例如：20250101）
            school_code: 学校代码（例如：78319）
            exam_date: 考试日期

        Returns:
            市级考号（例如：7783190101）

        Examples:
            >>> school_to_city_exam_number("20250101", "78319", datetime(2026, 1, 15))
            "7783190101"
            >>> school_to_city_exam_number("20250101", "78319", datetime(2026, 9, 1))
            "7883190101"  # 升入高二，年级编码变为8
        """
        try:
            # 解析校级考号
            enrollment_year = int(school_exam_number[:4])
            class_num = school_exam_number[4:6]
            seat_num = school_exam_number[6:8]

            # 计算年级编码
            grade_code = ExamNumberService.get_grade_code(enrollment_year, exam_date)

            # 组合市级考号
            city_exam_number = f"{grade_code}{school_code}{class_num}{seat_num}"

            logger.debug(
                f"校级考号 {school_exam_number} -> 市级考号 {city_exam_number} "
                f"(入学年份:{enrollment_year}, 年级编码:{grade_code}, 学校代码:{school_code})"
            )

            return city_exam_number

        except (ValueError, IndexError) as e:
            logger.error(f"校级考号转换失败: {school_exam_number}, 错误: {e}")
            raise ValueError(f"无效的校级考号格式: {school_exam_number}")

    @staticmethod
    def city_to_school_exam_number(
        city_exam_number: str,
        enrollment_year: int
    ) -> str:
        """市级考号转校级考号

        Args:
            city_exam_number: 市级考号（例如：7783190101）
            enrollment_year: 入学学年

        Returns:
            校级考号（例如：20250101）

        Examples:
            >>> city_to_school_exam_number("7783190101", 2025)
            "20250101"
        """
        try:
            # 解析市级考号
            grade_code = int(city_exam_number[0])  # 年级编码
            # 学校代码：第2-6位
            class_num = city_exam_number[6:8]      # 班级编号
            seat_num = city_exam_number[8:10]      # 座位号

            # 组合校级考号
            school_exam_number = f"{enrollment_year}{class_num}{seat_num}"

            logger.debug(
                f"市级考号 {city_exam_number} -> 校级考号 {school_exam_number} "
                f"(年级编码:{grade_code}, 入学年份:{enrollment_year})"
            )

            return school_exam_number

        except (ValueError, IndexError) as e:
            logger.error(f"市级考号转换失败: {city_exam_number}, 错误: {e}")
            raise ValueError(f"无效的市级考号格式: {city_exam_number}")

    @staticmethod
    def validate_school_exam_number(exam_number: str) -> bool:
        """验证校级考号格式

        Args:
            exam_number: 校级考号

        Returns:
            是否有效
        """
        if not exam_number or len(exam_number) != 8:
            return False

        try:
            # 检查是否为数字
            int(exam_number)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_city_exam_number(exam_number: str) -> bool:
        """验证市级考号格式

        Args:
            exam_number: 市级考号

        Returns:
            是否有效
        """
        if not exam_number or len(exam_number) != 10:
            return False

        try:
            # 检查是否为数字
            int(exam_number)

            # 检查年级编码是否有效
            grade_code = int(exam_number[0])
            return grade_code in ExamNumberService.CODE_GRADE_MAP

        except ValueError:
            return False

    @staticmethod
    def parse_school_exam_number(exam_number: str) -> dict:
        """解析校级考号

        Args:
            exam_number: 校级考号（例如：20250101）

        Returns:
            包含各部分的字典
        """
        if not ExamNumberService.validate_school_exam_number(exam_number):
            raise ValueError(f"无效的校级考号格式: {exam_number}")

        return {
            "enrollment_year": int(exam_number[:4]),
            "class_number": exam_number[4:6],
            "seat_number": exam_number[6:8],
        }

    @staticmethod
    def parse_city_exam_number(exam_number: str) -> dict:
        """解析市级考号

        Args:
            exam_number: 市级考号（例如：7783190101）

        Returns:
            包含各部分的字典
        """
        if not ExamNumberService.validate_city_exam_number(exam_number):
            raise ValueError(f"无效的市级考号格式: {exam_number}")

        grade_code = int(exam_number[0])
        school_code = exam_number[1:6]
        class_number = exam_number[6:8]
        seat_number = exam_number[8:10]

        return {
            "grade_code": grade_code,
            "grade_level": ExamNumberService.CODE_GRADE_MAP.get(grade_code),
            "school_code": school_code,
            "class_number": class_number,
            "seat_number": seat_number,
        }
