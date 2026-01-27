"""
高中总分评价计算服务

用于计算高中学生的总分成绩和达标情况
支持文理科区分和4条分数线（C9线、特控线、本科线、专科线）
"""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Exam, ExamTotalScore, StudentType
)


class TotalScoreCalculator:
    """高中总分评价计算器"""

    # 默认分数线配置（理科）
    DEFAULT_SCIENCE_LINES = {
        "c9_line": 670,              # C9联盟线
        "special_control_line": 620, # 特控线（一本线）
        "undergraduate_line": 520,   # 本科线
        "junior_college_line": 200,  # 专科线
    }

    # 默认分数线配置（文科）
    DEFAULT_ARTS_LINES = {
        "c9_line": 650,              # C9联盟线
        "special_control_line": 600, # 特控线（一本线）
        "undergraduate_line": 500,   # 本科线
        "junior_college_line": 200,  # 专科线
    }

    # 默认分数线配置（未分科）
    DEFAULT_NONE_LINES = {
        "c9_line": 660,              # C9联盟线（文理综合）
        "special_control_line": 610, # 特控线（一本线）
        "undergraduate_line": 510,   # 本科线
        "junior_college_line": 200,  # 专科线
    }

    @staticmethod
    async def create_total_score(
        session: AsyncSession,
        exam_id: int,
        student_id: int,
        total_score: int,
        student_type: StudentType,
        score_lines: dict = None,
        created_by: int = 1
    ) -> ExamTotalScore:
        """
        创建高中总分评价记录

        Args:
            session: 数据库会话
            exam_id: 考试ID
            student_id: 学生ID
            total_score: 总分
            student_type: 学生类型（arts/science/none）
            score_lines: 自定义分数线（可选）
            created_by: 创建人ID

        Returns:
            ExamTotalScore: 总分评价记录
        """
        # 获取学生信息（验证学生是否存在）
        student_result = await session.execute(
            select(User).where(User.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # 使用默认分数线或自定义分数线
        if score_lines is None:
            score_lines = TotalScoreCalculator._get_default_lines(student_type)

        # 提取分数线
        c9_line = score_lines.get("c9_line")
        special_control_line = score_lines.get("special_control_line")
        undergraduate_line = score_lines.get("undergraduate_line")
        junior_college_line = score_lines.get("junior_college_line")

        # 计算达标情况
        reached_c9 = total_score >= c9_line if c9_line is not None else None
        reached_special_control = total_score >= special_control_line if special_control_line is not None else None
        reached_undergraduate = total_score >= undergraduate_line if undergraduate_line is not None else None
        reached_junior_college = total_score >= junior_college_line if junior_college_line is not None else None

        # 创建总分评价记录
        total_score_record = ExamTotalScore(
            exam_id=exam_id,
            student_id=student_id,
            student_type=student_type.value if hasattr(student_type, 'value') else student_type,
            total_score=total_score,
            c9_line=c9_line,
            special_control_line=special_control_line,
            undergraduate_line=undergraduate_line,
            junior_college_line=junior_college_line,
            reached_c9=reached_c9,
            reached_special_control=reached_special_control,
            reached_undergraduate=reached_undergraduate,
            reached_junior_college=reached_junior_college,
        )

        return total_score_record

    @staticmethod
    async def batch_create_for_exam(
        session: AsyncSession,
        exam_id: int,
        scores_data: list[dict],
        created_by: int = 1
    ) -> list[ExamTotalScore]:
        """
        批量创建考试的总分评价记录

        Args:
            session: 数据库会话
            exam_id: 考试ID
            scores_data: 成绩数据列表
                [
                    {
                        "student_id": 1,
                        "total_score": 680,
                        "student_type": StudentType.SCIENCE,
                        "score_lines": {...}  # 可选
                    },
                    ...
                ]
            created_by: 创建人ID

        Returns:
            list[ExamTotalScore]: 总分评价记录列表
        """
        total_scores = []

        for score_data in scores_data:
            student_id = score_data["student_id"]
            total_score = score_data["total_score"]
            student_type = score_data.get("student_type", StudentType.NONE)
            score_lines = score_data.get("score_lines")

            # 创建总分评价记录
            total_score_record = await TotalScoreCalculator.create_total_score(
                session=session,
                exam_id=exam_id,
                student_id=student_id,
                total_score=total_score,
                student_type=student_type,
                score_lines=score_lines,
                created_by=created_by
            )
            total_scores.append(total_score_record)

        return total_scores

    @staticmethod
    def _get_default_lines(student_type: StudentType) -> dict:
        """获取学生类型对应的默认分数线"""
        if student_type == StudentType.ARTS:
            return TotalScoreCalculator.DEFAULT_ARTS_LINES.copy()
        elif student_type == StudentType.SCIENCE:
            return TotalScoreCalculator.DEFAULT_SCIENCE_LINES.copy()
        else:
            return TotalScoreCalculator.DEFAULT_NONE_LINES.copy()

    @staticmethod
    def get_grade_level(total_score: int, student_type: StudentType) -> str:
        """
        根据总分和学生类型获取等级

        Args:
            total_score: 总分
            student_type: 学生类型

        Returns:
            str: 等级（C9联盟/特控线/本科线/专科线/未达标）
        """
        score_lines = TotalScoreCalculator._get_default_lines(student_type)

        if total_score >= score_lines["c9_line"]:
            return "C9联盟"
        elif total_score >= score_lines["special_control_line"]:
            return "特控线"
        elif total_score >= score_lines["undergraduate_line"]:
            return "本科线"
        elif total_score >= score_lines["junior_college_line"]:
            return "专科线"
        else:
            return "未达标"

    @staticmethod
    async def get_exam_statistics(
        session: AsyncSession,
        exam_id: int,
        student_type: StudentType = None
    ) -> dict:
        """
        获取考试的总分统计信息

        Args:
            session: 数据库会话
            exam_id: 考试ID
            student_type: 学生类型（可选，用于筛选）

        Returns:
            dict: 统计信息
                {
                    "total_count": 总人数,
                    "c9_count": C9达标人数,
                    "special_control_count": 特控线达标人数,
                    "undergraduate_count": 本科线达标人数,
                    "junior_college_count": 专科线达标人数,
                    "average_score": 平均分,
                    "max_score": 最高分,
                    "min_score": 最低分,
                    "score_distribution": 分数段分布
                }
        """
        # 构建查询
        query = select(ExamTotalScore).where(ExamTotalScore.exam_id == exam_id)

        if student_type:
            query = query.where(ExamTotalScore.student_type == student_type)

        result = await session.execute(query)
        total_scores = result.scalars().all()

        if not total_scores:
            return {
                "total_count": 0,
                "c9_count": 0,
                "special_control_count": 0,
                "undergraduate_count": 0,
                "junior_college_count": 0,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0,
                "score_distribution": {}
            }

        # 统计各项数据
        total_count = len(total_scores)
        c9_count = sum(1 for s in total_scores if s.reached_c9)
        special_control_count = sum(1 for s in total_scores if s.reached_special_control)
        undergraduate_count = sum(1 for s in total_scores if s.reached_undergraduate)
        junior_college_count = sum(1 for s in total_scores if s.reached_junior_college)

        scores = [s.total_score for s in total_scores]
        average_score = sum(scores) / total_count
        max_score = max(scores)
        min_score = min(scores)

        # 分数段分布
        score_distribution = {
            "700+": sum(1 for s in scores if s >= 700),
            "650-699": sum(1 for s in scores if 650 <= s < 700),
            "600-649": sum(1 for s in scores if 600 <= s < 650),
            "550-599": sum(1 for s in scores if 550 <= s < 600),
            "500-549": sum(1 for s in scores if 500 <= s < 550),
            "450-499": sum(1 for s in scores if 450 <= s < 500),
            "400-449": sum(1 for s in scores if 400 <= s < 450),
            "400以下": sum(1 for s in scores if s < 400),
        }

        return {
            "total_count": total_count,
            "c9_count": c9_count,
            "special_control_count": special_control_count,
            "undergraduate_count": undergraduate_count,
            "junior_college_count": junior_college_count,
            "average_score": round(average_score, 2),
            "max_score": max_score,
            "min_score": min_score,
            "score_distribution": score_distribution,
        }


# 使用示例
async def example_usage():
    """使用示例"""
    from app.core.database import get_db
    from app.models.user import StudentType

    async for session in get_db():
        # 示例1: 为单个理科学生创建高考总分评价
        science_score = await TotalScoreCalculator.create_total_score(
            session=session,
            exam_id=1,  # 2024年高考
            student_id=1,
            total_score=680,
            student_type=StudentType.SCIENCE,
            created_by=1
        )
        session.add(science_score)
        await session.commit()

        print(f"理科学生 {science_score.student_id} 的高考成绩: {science_score.total_score}分")
        print(f"  C9线（{science_score.c9_line}分）: {'✅ 达标' if science_score.reached_c9 else '❌ 未达标'}")
        print(f"  特控线（{science_score.special_control_line}分）: {'✅ 达标' if science_score.reached_special_control else '❌ 未达标'}")
        print(f"  本科线（{science_score.undergraduate_line}分）: {'✅ 达标' if science_score.reached_undergraduate else '❌ 未达标'}")
        print(f"  专科线（{science_score.junior_college_line}分）: {'✅ 达标' if science_score.reached_junior_college else '❌ 未达标'}")

        # 示例2: 批量创建文科学生成绩
        arts_scores_data = [
            {"student_id": 2, "total_score": 655, "student_type": StudentType.ARTS},
            {"student_id": 3, "total_score": 620, "student_type": StudentType.ARTS},
            {"student_id": 4, "total_score": 510, "student_type": StudentType.ARTS},
        ]

        arts_scores = await TotalScoreCalculator.batch_create_for_exam(
            session=session,
            exam_id=1,
            scores_data=arts_scores_data,
            created_by=1
        )

        # 批量保存
        session.add_all(arts_scores)
        await session.commit()

        print(f"\n批量创建完成，共 {len(arts_scores)} 名文科学生")

        # 示例3: 获取考试统计信息
        stats = await TotalScoreCalculator.get_exam_statistics(
            session=session,
            exam_id=1,
            student_type=StudentType.SCIENCE
        )

        print(f"\n理科考试统计:")
        print(f"  总人数: {stats['total_count']}")
        print(f"  C9线达标: {stats['c9_count']}人 ({stats['c9_count']/stats['total_count']*100:.1f}%)")
        print(f"  特控线达标: {stats['special_control_count']}人 ({stats['special_control_count']/stats['total_count']*100:.1f}%)")
        print(f"  本科线达标: {stats['undergraduate_count']}人 ({stats['undergraduate_count']/stats['total_count']*100:.1f}%)")
        print(f"  平均分: {stats['average_score']}")
        print(f"  最高分: {stats['max_score']}")
        print(f"  最低分: {stats['min_score']}")
