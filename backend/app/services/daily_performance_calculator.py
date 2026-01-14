"""
日常表现成绩计算服务

展示如何将 PositiveBehavior, DisciplineRecord, AttendanceEntry, DutyAssignment
等日常表现数据转换为百分制成绩（0-100分）
"""

from datetime import datetime
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Classroom, Semester,
    PositiveBehavior, DisciplineRecord, AttendanceEntry, DutyAssignment,
    DailyPerformanceScore
)


class DailyPerformanceCalculator:
    """日常表现成绩计算器"""

    # 默认权重配置
    DEFAULT_WEIGHTS = {
        "attendance": 0.20,    # 考勤权重 20%
        "behavior": 0.40,      # 课堂表现权重 40%
        "discipline": 0.30,    # 纪律权重 30%
        "duty": 0.10,          # 值日权重 10%
    }

    # 默认分数线
    DEFAULT_SCORE_LINES = {
        "excellent": 90,  # 优秀
        "good": 80,       # 良好
        "pass": 60,       # 合格
    }

    @staticmethod
    async def calculate_for_student(
        session: AsyncSession,
        student_id: int,
        classroom_id: int,
        start_date: datetime,
        end_date: datetime,
        period_name: str,
        semester_id: int = None,
        weights: dict = None,
        created_by: int = 1
    ) -> DailyPerformanceScore:
        """
        为单个学生计算日常表现成绩

        Args:
            session: 数据库会话
            student_id: 学生ID
            classroom_id: 班级ID
            start_date: 统计开始日期
            end_date: 统计结束日期
            period_name: 统计周期名称
            semester_id: 学期ID（可选）
            weights: 自定义权重（可选）
            created_by: 创建人ID

        Returns:
            DailyPerformanceScore: 日常表现成绩记录
        """
        # 使用默认权重或自定义权重
        if weights is None:
            weights = DailyPerformanceCalculator.DEFAULT_WEIGHTS.copy()

        # 1. 统计正面行为积分
        positive_result = await session.execute(
            select(
                func.count(PositiveBehavior.id).label('count'),
                func.sum(PositiveBehavior.points).label('total_points')
            ).where(
                PositiveBehavior.student_id == student_id,
                PositiveBehavior.recorded_at >= start_date,
                PositiveBehavior.recorded_at <= end_date
            )
        )
        positive_row = positive_result.one()
        positive_count = positive_row.count or 0
        positive_points = positive_row.total_points or 0

        # 2. 统计违纪次数（假设每次违纪扣5分）
        discipline_result = await session.execute(
            select(func.count(DisciplineRecord.id))
            .where(
                DisciplineRecord.student_id == student_id,
                DisciplineRecord.recorded_at >= start_date,
                DisciplineRecord.recorded_at <= end_date
            )
        )
        discipline_count = discipline_result.scalar() or 0
        discipline_points = discipline_count * 5  # 每次违纪扣5分

        # 3. 统计考勤记录
        attendance_result = await session.execute(
            select(
                func.sum(
                    case(
                        (AttendanceEntry.status == 'present', 1),
                        else_=0
                    )
                ).label('present_count'),
                func.sum(
                    case(
                        (AttendanceEntry.status == 'late', 1),
                        else_=0
                    )
                ).label('late_count'),
                func.sum(
                    case(
                        (AttendanceEntry.status == 'leave', 1),
                        else_=0
                    )
                ).label('leave_count'),
                func.sum(
                    case(
                        (AttendanceEntry.status == 'absent', 1),
                        else_=0
                    )
                ).label('absent_count'),
            )
            .where(
                AttendanceEntry.student_id == student_id,
                AttendanceEntry.updated_at >= start_date,
                AttendanceEntry.updated_at <= end_date
            )
        )
        attendance_row = attendance_result.one()
        attendance_present = attendance_row.present_count or 0
        attendance_late = attendance_row.late_count or 0
        attendance_leave = attendance_row.leave_count or 0
        attendance_absent = attendance_row.absent_count or 0

        # 4. 统计值日完成次数
        duty_result = await session.execute(
            select(func.count(DutyAssignment.id))
            .where(
                DutyAssignment.assignee_user_id == student_id,
                DutyAssignment.duty_date >= start_date,
                DutyAssignment.duty_date <= end_date,
                DutyAssignment.status == 'completed'
            )
        )
        duty_completed = duty_result.scalar() or 0

        # 5. 计算各分类得分（百分制）
        # 考勤得分：满分100，每次缺勤扣10分，每次迟到扣2分
        total_attendance = attendance_present + attendance_late + attendance_leave + attendance_absent
        if total_attendance > 0:
            attendance_score = 100 - (attendance_absent * 10) - (attendance_late * 2)
            attendance_score = max(0, min(100, attendance_score))  # 限制在0-100
        else:
            attendance_score = 100  # 无考勤记录，默认满分

        # 表现得分：基于正面行为积分，转换为百分制
        # 假设：平均每节课获得2分是优秀，0分是及格
        behavior_score = min(100, positive_points * 2) if positive_count > 0 else 60

        # 纪律得分：满分100，每次违纪扣5分
        discipline_score = max(0, 100 - discipline_points)

        # 值日得分：每次完成值日+10分，上限100分
        duty_score = min(100, duty_completed * 10)

        # 6. 计算加权总分
        final_score = (
            attendance_score * weights['attendance'] +
            behavior_score * weights['behavior'] +
            discipline_score * weights['discipline'] +
            duty_score * weights['duty']
        )

        # 7. 计算等级
        grade_level = DailyPerformanceCalculator._calculate_grade_level(final_score)

        # 8. 创建成绩记录
        detail_scores = {
            "attendance_score": round(attendance_score, 2),
            "behavior_score": round(behavior_score, 2),
            "discipline_score": round(discipline_score, 2),
            "duty_score": round(duty_score, 2),
            "attendance_weight": weights['attendance'],
            "behavior_weight": weights['behavior'],
            "discipline_weight": weights['discipline'],
            "duty_weight": weights['duty'],
        }

        performance_score = DailyPerformanceScore(
            student_id=student_id,
            classroom_id=classroom_id,
            semester_id=semester_id,
            period_name=period_name,
            start_date=start_date,
            end_date=end_date,
            positive_behavior_count=positive_count,
            positive_behavior_points=positive_points,
            discipline_count=discipline_count,
            discipline_points=discipline_points,
            attendance_present_count=attendance_present,
            attendance_late_count=attendance_late,
            attendance_leave_count=attendance_leave,
            attendance_absent_count=attendance_absent,
            duty_completed_count=duty_completed,
            final_score=round(final_score, 2),
            grade_level=grade_level,
            detail_scores=detail_scores,
            created_by=created_by,
            calculated_at=datetime.utcnow()
        )

        return performance_score

    @staticmethod
    def _calculate_grade_level(score: float) -> str:
        """根据分数计算等级"""
        if score >= DailyPerformanceCalculator.DEFAULT_SCORE_LINES['excellent']:
            return "优秀"
        elif score >= DailyPerformanceCalculator.DEFAULT_SCORE_LINES['good']:
            return "良好"
        elif score >= DailyPerformanceCalculator.DEFAULT_SCORE_LINES['pass']:
            return "合格"
        else:
            return "不合格"

    @staticmethod
    async def batch_calculate_for_classroom(
        session: AsyncSession,
        classroom_id: int,
        start_date: datetime,
        end_date: datetime,
        period_name: str,
        semester_id: int = None,
        weights: dict = None,
        created_by: int = 1
    ) -> list[DailyPerformanceScore]:
        """
        批量为班级所有学生计算日常表现成绩

        Args:
            session: 数据库会话
            classroom_id: 班级ID
            start_date: 统计开始日期
            end_date: 统计结束日期
            period_name: 统计周期名称
            semester_id: 学期ID（可选）
            weights: 自定义权重（可选）
            created_by: 创建人ID

        Returns:
            list[DailyPerformanceScore]: 日常表现成绩记录列表
        """
        # 获取班级所有学生
        result = await session.execute(
            select(User.id)
            .join(ClassroomMembership, User.id == ClassroomMembership.user_id)
            .where(
                ClassroomMembership.classroom_id == classroom_id,
                ClassroomMembership.is_active == True
            )
        )
        student_ids = [row[0] for row in result]

        # 为每个学生计算成绩
        performance_scores = []
        for student_id in student_ids:
            score = await DailyPerformanceCalculator.calculate_for_student(
                session=session,
                student_id=student_id,
                classroom_id=classroom_id,
                start_date=start_date,
                end_date=end_date,
                period_name=period_name,
                semester_id=semester_id,
                weights=weights,
                created_by=created_by
            )
            performance_scores.append(score)

        return performance_scores


# 使用示例
async def example_usage():
    """使用示例"""
    from app.core.database import get_db

    async for session in get_db():
        # 示例1: 为单个学生计算月度表现成绩
        march_score = await DailyPerformanceCalculator.calculate_for_student(
            session=session,
            student_id=1,
            classroom_id=1,
            start_date=datetime(2024, 3, 1),
            end_date=datetime(2024, 3, 31, 23, 59, 59),
            period_name="2024年3月",
            semester_id=1,
            created_by=1
        )
        session.add(march_score)
        await session.commit()

        print(f"学生 {march_score.student_id} 的3月表现成绩: {march_score.final_score}分")
        print(f"  正面行为: {march_score.positive_behavior_count}次, {march_score.positive_behavior_points}分")
        print(f"  纪律: {march_score.discipline_count}次, 扣{march_score.discipline_points}分")
        print(f"  考勤: 出勤{march_score.attendance_present_count}, 迟到{march_score.attendance_late_count}次")
        print(f"  等级: {march_score.grade_level}")

        # 示例2: 批量为班级计算学期表现成绩
        semester_scores = await DailyPerformanceCalculator.batch_calculate_for_classroom(
            session=session,
            classroom_id=1,
            start_date=datetime(2024, 2, 26),
            end_date=datetime(2024, 7, 15),
            period_name="2023-2024学年下学期",
            semester_id=1,
            weights={  # 自定义权重
                "attendance": 0.25,  # 提高考勤权重
                "behavior": 0.35,
                "discipline": 0.30,
                "duty": 0.10,
            },
            created_by=1
        )

        # 批量保存
        session.add_all(semester_scores)
        await session.commit()

        print(f"\n批量计算完成，共 {len(semester_scores)} 名学生")
        avg_score = sum(s.final_score for s in semester_scores) / len(semester_scores)
        print(f"  班级平均分: {avg_score:.2f}分")


# 导入 ClassroomMembership（用于查询班级学生）
from app.models.classroom_assistant import ClassroomMembership
