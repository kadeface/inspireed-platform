"""
增值评价计算服务

实现"首尾对比"模型，计算教学增值效果
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload

from app.models import (
    User,
    Exam,
    Subject,
    Score,
    ValueAddedEvaluation,
    EvaluationDetail,
    EvaluationMetric,
    MetricCategory,
    Classroom,
    ClassroomMembership,
    School,
    Region,
)

logger = logging.getLogger(__name__)


class RateMetricsCalculator:
    """率指标计算器"""

    # 默认分数线定义
    DEFAULT_SCORE_LINES = {
        "excellent": 85,  # 优秀线
        "good": 75,      # 良好线
        "pass": 60,      # 及格线
    }

    @staticmethod
    async def calculate_exam_metrics(
        db: AsyncSession,
        exam_id: int,
        subject_id: int,
        scope_type: str,
        scope_id: Optional[int] = None,
        score_lines: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        计算指定考试、科目、范围的率指标

        Args:
            db: 数据库会话
            exam_id: 考试ID
            subject_id: 科目ID
            scope_type: 范围类型 (region/school/classroom)
            scope_id: 范围ID (region_id/school_id/classroom_id)
            score_lines: 分数线配置

        Returns:
            率指标结果 {
                "total_count": 总人数,
                "valid_count": 有效人数,
                "excellent_count": 优秀人数,
                "good_count": 良好人数,
                "pass_count": 及格人数,
                "low_count": 低分人数,
                "excellent_rate": 优秀率,
                "good_rate": 优良率,
                "pass_rate": 合格率,
                "low_rate": 低分率,
                "average_score": 平均分,
            }
        """
        lines = score_lines or RateMetricsCalculator.DEFAULT_SCORE_LINES

        # 构建查询条件
        conditions = [
            Score.exam_id == exam_id,
            Score.subject_id == subject_id,
            Score.is_absent == False,
            Score.is_cheated == False,
        ]

        # 根据范围筛选
        if scope_type == "classroom" and scope_id:
            # 查询班级所有学生
            membership_result = await db.execute(
                select(ClassroomMembership.user_id).where(
                    and_(
                        ClassroomMembership.classroom_id == scope_id,
                        ClassroomMembership.is_active == True
                    )
                )
            )
            student_ids = [row[0] for row in membership_result.all()]
            conditions.append(Score.student_id.in_(student_ids))

        elif scope_type == "school" and scope_id:
            # 查询学校所有学生（通过班级）
            classrooms_result = await db.execute(
                select(Classroom.id).where(Classroom.school_id == scope_id)
            )
            classroom_ids = [row[0] for row in classrooms_result.all()]

            membership_result = await db.execute(
                select(ClassroomMembership.user_id).where(
                    and_(
                        ClassroomMembership.classroom_id.in_(classroom_ids),
                        ClassroomMembership.is_active == True
                    )
                )
            )
            student_ids = [row[0] for row in membership_result.all()]
            conditions.append(Score.student_id.in_(student_ids))

        elif scope_type == "region" and scope_id:
            # 查询区县所有学生
            schools_result = await db.execute(
                select(School.id).where(School.region_id == scope_id)
            )
            school_ids = [row[0] for row in schools_result.all()]

            classrooms_result = await db.execute(
                select(Classroom.id).where(Classroom.school_id.in_(school_ids))
            )
            classroom_ids = [row[0] for row in classrooms_result.all()]

            membership_result = await db.execute(
                select(ClassroomMembership.user_id).where(
                    and_(
                        ClassroomMembership.classroom_id.in_(classroom_ids),
                        ClassroomMembership.is_active == True
                    )
                )
            )
            student_ids = [row[0] for row in membership_result.all()]
            conditions.append(Score.student_id.in_(student_ids))

        # 执行查询
        result = await db.execute(
            select(
                func.count(Score.id).label('total_count'),
                func.sum(case((Score.raw_score >= lines["excellent"], 1), else_=0)).label('excellent_count'),
                func.sum(case((Score.raw_score >= lines["good"], 1), else_=0)).label('good_count'),
                func.sum(case((Score.raw_score >= lines["pass"], 1), else_=0)).label('pass_count'),
                func.sum(case((Score.raw_score < lines["pass"], 1), else_=0)).label('low_count'),
                func.avg(Score.raw_score).label('average_score'),
            )
            .where(and_(*conditions))
        )

        stats = result.one()

        total_count = stats.total_count or 0
        excellent_count = stats.excellent_count or 0
        good_count = stats.good_count or 0
        pass_count = stats.pass_count or 0
        low_count = stats.low_count or 0

        return {
            "total_count": total_count,
            "valid_count": total_count,
            "excellent_count": excellent_count,
            "good_count": good_count,
            "pass_count": pass_count,
            "low_count": low_count,
            "excellent_rate": round(excellent_count / total_count * 100, 2) if total_count > 0 else 0,
            "good_rate": round(good_count / total_count * 100, 2) if total_count > 0 else 0,
            "pass_rate": round(pass_count / total_count * 100, 2) if total_count > 0 else 0,
            "low_rate": round(low_count / total_count * 100, 2) if total_count > 0 else 0,
            "average_score": round(stats.average_score or 0, 2),
        }


class ValueAddedEvaluationService:
    """增值评价服务（首尾对比模型）"""

    @staticmethod
    async def calculate_value_added_evaluation(
        db: AsyncSession,
        name: str,
        baseline_exam_id: int,
        endline_exam_id: int,
        subject_id: int,
        scope_type: str,
        scope_id: Optional[int],
        region_id: Optional[int],
        school_id: Optional[int],
        classroom_id: Optional[int],
        created_by: int,
        metrics: Optional[List[str]] = None,
        score_lines: Optional[Dict[str, float]] = None,
    ) -> ValueAddedEvaluation:
        """
        计算增值评价（首尾对比）

        Args:
            db: 数据库会话
            name: 评价名称
            baseline_exam_id: 基线考试ID
            endline_exam_id: 结束考试ID
            subject_id: 科目ID
            scope_type: 范围类型 (region/school/classroom)
            scope_id: 范围ID
            region_id: 区县ID
            school_id: 学校ID
            classroom_id: 班级ID
            created_by: 创建者ID
            metrics: 指标列表（默认使用所有率指标）
            score_lines: 分数线配置

        Returns:
            增值评价结果对象
        """
        # 验证考试
        baseline_exam_result = await db.execute(
            select(Exam).where(Exam.id == baseline_exam_id)
        )
        baseline_exam = baseline_exam_result.scalar_one_or_none()
        if not baseline_exam:
            raise ValueError(f"基线考试 {baseline_exam_id} 不存在")

        endline_exam_result = await db.execute(
            select(Exam).where(Exam.id == endline_exam_id)
        )
        endline_exam = endline_exam_result.scalar_one_or_none()
        if not endline_exam:
            raise ValueError(f"结束考试 {endline_exam_id} 不存在")

        # 默认使用所有率指标
        if metrics is None:
            metrics = [
                MetricCategory.EXCELLENCE_RATE.value,
                MetricCategory.GOOD_RATE.value,
                MetricCategory.PASS_RATE.value,
                MetricCategory.LOW_RATE.value,
            ]

        # 计算基线指标
        baseline_metrics = await RateMetricsCalculator.calculate_exam_metrics(
            db, baseline_exam_id, subject_id, scope_type, scope_id, score_lines
        )

        # 计算结束指标
        endline_metrics = await RateMetricsCalculator.calculate_exam_metrics(
            db, endline_exam_id, subject_id, scope_type, scope_id, score_lines
        )

        # 创建评价结果
        evaluation = ValueAddedEvaluation(
            name=name,
            scope_type=scope_type,
            region_id=region_id,
            school_id=school_id,
            classroom_id=classroom_id,
            baseline_exam_id=baseline_exam_id,
            endline_exam_id=endline_exam_id,
            subject_id=subject_id,
            created_by=created_by,
        )
        db.add(evaluation)
        await db.flush()

        # 创建详细记录
        details = []
        for metric_code in metrics:
            # 获取指标
            metric_result = await db.execute(
                select(EvaluationMetric).where(EvaluationMetric.code == metric_code)
            )
            metric = metric_result.scalar_one_or_none()
            if not metric:
                logger.warning(f"指标 {metric_code} 不存在，跳过")
                continue

            # 获取基线和结束值
            baseline_rate = baseline_metrics.get(f"{metric_code}", 0)
            endline_rate = endline_metrics.get(f"{metric_code}", 0)

            # 计算增值（百分点）
            value_added = round(endline_rate - baseline_rate, 2)

            # 计算增值率（百分比）
            baseline_value = baseline_rate if baseline_rate != 0 else 0.01  # 避免除零
            value_added_rate = round((endline_rate - baseline_rate) / baseline_value * 100, 2)

            detail = EvaluationDetail(
                evaluation_id=evaluation.id,
                metric_id=metric.id,
                scope_type=scope_type,
                scope_id=scope_id,
                baseline_count=int(baseline_metrics.get(f"{metric_code.replace('_rate', '_count')}", 0)),
                baseline_total=baseline_metrics["valid_count"],
                baseline_rate=baseline_rate,
                endline_count=int(endline_metrics.get(f"{metric_code.replace('_rate', '_count')}", 0)),
                endline_total=endline_metrics["valid_count"],
                endline_rate=endline_rate,
                value_added=value_added,
            )
            details.append(detail)

        db.add_all(details)
        await db.commit()
        await db.refresh(evaluation)

        logger.info(f"增值评价创建成功: {evaluation.id}, 包含 {len(details)} 个指标")
        return evaluation

    @staticmethod
    async def get_evaluation_summary(
        db: AsyncSession,
        evaluation_id: int,
    ) -> Dict[str, Any]:
        """
        获取评价汇总信息

        Args:
            db: 数据库会话
            evaluation_id: 评价ID

        Returns:
            评价汇总信息
        """
        # 查询评价
        evaluation_result = await db.execute(
            select(ValueAddedEvaluation)
            .options(selectinload(ValueAddedEvaluation.details))
            .where(ValueAddedEvaluation.id == evaluation_id)
        )
        evaluation = evaluation_result.scalar_one_or_none()
        if not evaluation:
            raise ValueError(f"评价 {evaluation_id} 不存在")

        # 查询考试信息
        baseline_exam_result = await db.execute(
            select(Exam).where(Exam.id == evaluation.baseline_exam_id)
        )
        baseline_exam = baseline_exam_result.scalar_one_or_none()

        endline_exam_result = await db.execute(
            select(Exam).where(Exam.id == evaluation.endline_exam_id)
        )
        endline_exam = endline_exam_result.scalar_one_or_none()

        # 查询科目信息
        subject_result = await db.execute(
            select(Subject).where(Subject.id == evaluation.subject_id)
        )
        subject = subject_result.scalar_one_or_none()

        # 组装汇总信息
        summary = {
            "evaluation_id": evaluation.id,
            "name": evaluation.name,
            "scope_type": evaluation.scope_type,
            "scope_id": evaluation.scope_id,
            "baseline_exam": {
                "id": baseline_exam.id if baseline_exam else None,
                "name": baseline_exam.name if baseline_exam else None,
                "date": baseline_exam.exam_date.isoformat() if baseline_exam and baseline_exam.exam_date else None,
            },
            "endline_exam": {
                "id": endline_exam.id if endline_exam else None,
                "name": endline_exam.name if endline_exam else None,
                "date": endline_exam.exam_date.isoformat() if endline_exam and endline_exam.exam_date else None,
            },
            "subject": {
                "id": subject.id if subject else None,
                "name": subject.name if subject else None,
            },
            "metrics": [],
            "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
        }

        # 添加指标明细
        for detail in evaluation.details:
            metric_result = await db.execute(
                select(EvaluationMetric).where(EvaluationMetric.id == detail.metric_id)
            )
            metric = metric_result.scalar_one_or_none()

            summary["metrics"].append({
                "metric_id": detail.metric_id,
                "metric_name": metric.name if metric else "",
                "metric_code": metric.code if metric else "",
                "baseline_rate": detail.baseline_rate,
                "endline_rate": detail.endline_rate,
                "value_added": detail.value_added,
                "improvement": "提升" if detail.value_added > 0 else "下降" if detail.value_added < 0 else "持平",
            })

        return summary

    @staticmethod
    async def batch_evaluate_classrooms(
        db: AsyncSession,
        name: str,
        baseline_exam_id: int,
        endline_exam_id: int,
        subject_id: int,
        school_id: int,
        created_by: int,
        classroom_ids: Optional[List[int]] = None,
        score_lines: Optional[Dict[str, float]] = None,
    ) -> List[ValueAddedEvaluation]:
        """
        批量评价班级

        Args:
            db: 数据库会话
            name: 评价名称（基础）
            baseline_exam_id: 基线考试ID
            endline_exam_id: 结束考试ID
            subject_id: 科目ID
            school_id: 学校ID
            created_by: 创建者ID
            classroom_ids: 班级ID列表（None表示全校所有班级）
            score_lines: 分数线配置

        Returns:
            评价结果列表
        """
        # 如果没有指定班级，查询学校所有班级
        if classroom_ids is None:
            classrooms_result = await db.execute(
                select(Classroom.id).where(Classroom.school_id == school_id)
            )
            classroom_ids = [row[0] for row in classrooms_result.all()]

        evaluations = []
        for idx, classroom_id in enumerate(classroom_ids):
            # 查询班级信息
            classroom_result = await db.execute(
                select(Classroom).where(Classroom.id == classroom_id)
            )
            classroom = classroom_result.scalar_one_or_none()
            if not classroom:
                logger.warning(f"班级 {classroom_id} 不存在，跳过")
                continue

            # 创建评价名称
            eval_name = f"{name} - {classroom.name}"

            try:
                evaluation = await ValueAddedEvaluationService.calculate_value_added_evaluation(
                    db=db,
                    name=eval_name,
                    baseline_exam_id=baseline_exam_id,
                    endline_exam_id=endline_exam_id,
                    subject_id=subject_id,
                    scope_type="classroom",
                    scope_id=classroom_id,
                    region_id=classroom.region_id if hasattr(classroom, 'region_id') else None,
                    school_id=school_id,
                    classroom_id=classroom_id,
                    created_by=created_by,
                    score_lines=score_lines,
                )
                evaluations.append(evaluation)
                logger.info(f"班级评价进度: {idx + 1}/{len(classroom_ids)}")

            except Exception as e:
                logger.error(f"评价班级 {classroom_id} 失败: {e}")
                continue

        await db.commit()
        logger.info(f"批量评价完成: {len(evaluations)}/{len(classroom_ids)} 个班级")
        return evaluations
