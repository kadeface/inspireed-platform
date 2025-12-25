"""
Formative assessment aggregation services.
"""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any, Dict, List, Optional

import sqlalchemy as sa
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import (
    ActivitySubmission,
    ActivitySubmissionStatus,
    FlowchartSnapshot,
    FormativeAssessment,
)
from app.models.question import Question, QuestionStatus


def _calc_accuracy(submissions: List[ActivitySubmission]) -> Optional[float]:
    correct_items = 0
    total_items = 0

    for submission in submissions:
        responses = submission.responses or {}
        for item in responses.values():
            if not isinstance(item, dict):
                continue
            if "is_correct" in item:
                total_items += 1
                if item.get("is_correct"):
                    correct_items += 1
            elif "score" in item and submission.max_score:
                total_items += 1
                score = item.get("score")
                max_score = item.get("max_score") or item.get("full_score")
                if isinstance(score, (int, float)) and score is not None:
                    if max_score:
                        if score >= max_score:
                            correct_items += 1
                    else:
                        # assume partial credit counts proportionally
                        correct_items += min(max(score, 0), 1)

    if total_items == 0:
        return None
    return round(correct_items / total_items, 4)


def _calc_average_time(submissions: List[ActivitySubmission]) -> Optional[float]:
    times = [s.time_spent for s in submissions if s.time_spent]
    if not times:
        return None
    return round(mean(times), 2)


async def calculate_student_metrics(
    db: AsyncSession,
    lesson_id: int,
    student_id: int,
    phase: Optional[str] = None,
    session_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Aggregate formative assessment metrics for a student within a lesson.
    
    Args:
        db: Database session
        lesson_id: Lesson ID
        student_id: Student ID
        phase: Optional phase filter
        session_id: Optional session ID filter. If provided, only submissions from this session are included.
    """

    submission_conditions = [
        ActivitySubmission.lesson_id == lesson_id,
        ActivitySubmission.student_id == student_id,
    ]
    
    # Filter by session_id if provided
    if session_id is not None:
        submission_conditions.append(ActivitySubmission.session_id == session_id)
    
    submission_stmt = select(ActivitySubmission).where(and_(*submission_conditions))
    submission_result = await db.execute(submission_stmt)
    submissions = submission_result.scalars().all()

    total_submissions = len(submissions)
    submitted = [
        s
        for s in submissions
        if s.status
        in (ActivitySubmissionStatus.SUBMITTED, ActivitySubmissionStatus.GRADED)
    ]
    graded = [s for s in submissions if s.status == ActivitySubmissionStatus.GRADED]

    avg_score = None
    if graded:
        scores = [s.score for s in graded if s.score is not None]
        if scores:
            avg_score = round(mean(scores), 2)

    accuracy = _calc_accuracy(graded or submitted)
    avg_time = _calc_average_time(submitted)

    # Flowchart insight
    # If session_id is provided, filter by submissions from that session
    if session_id is not None:
        # Join with ActivitySubmission to filter by session_id
        flowchart_stmt = (
            select(FlowchartSnapshot)
            .join(ActivitySubmission, FlowchartSnapshot.submission_id == ActivitySubmission.id)
            .where(
                and_(
                    FlowchartSnapshot.lesson_id == lesson_id,
                    FlowchartSnapshot.student_id == student_id,
                    ActivitySubmission.session_id == session_id,
                )
            )
            .order_by(FlowchartSnapshot.updated_at.desc())
            .limit(1)
        )
    else:
        flowchart_stmt = (
            select(FlowchartSnapshot)
            .where(
                and_(
                    FlowchartSnapshot.lesson_id == lesson_id,
                    FlowchartSnapshot.student_id == student_id,
                )
            )
            .order_by(FlowchartSnapshot.updated_at.desc())
            .limit(1)
        )
    flowchart_result = await db.execute(flowchart_stmt)
    flowchart = flowchart_result.scalar_one_or_none()
    flowchart_metrics: Dict[str, Any] = {}
    if flowchart:
        flowchart_metrics = {
            "version": flowchart.version,
            "updated_at": flowchart.updated_at.isoformat(),
        }
        if flowchart.analysis:
            flowchart_metrics.update(flowchart.analysis)

    # Question & answer participation
    question_stmt = select(
        func.count(Question.id),
        func.sum(func.cast(Question.status == QuestionStatus.RESOLVED, sa.Integer)),
        func.sum(func.cast(Question.status == QuestionStatus.ANSWERED, sa.Integer)),
    ).where(
        and_(
            Question.lesson_id == lesson_id,
            Question.student_id == student_id,
        )
    )
    question_result = await db.execute(question_stmt)
    question_count, resolved_count, answered_count = question_result.one()

    metrics: Dict[str, Any] = {
        "phase": phase,
        "total_submissions": total_submissions,
        "submitted_count": len(submitted),
        "graded_count": len(graded),
        "average_score": avg_score,
        "accuracy": accuracy,
        "average_time_spent": avg_time,
        "flowchart": flowchart_metrics or None,
        "questions_asked": int(question_count or 0),
        "questions_resolved": int(resolved_count or 0),
        "questions_answered": int(answered_count or 0),
        "updated_at": datetime.utcnow().isoformat(),
    }

    return metrics


def _determine_risk_level(metrics: Dict[str, Any]) -> Optional[str]:
    accuracy = metrics.get("accuracy")
    average_score = metrics.get("average_score")

    if accuracy is None and average_score is None:
        return None

    if accuracy is not None and accuracy < 0.6:
        return "high"
    if average_score is not None and average_score < 60:
        return "high"

    if accuracy is not None and accuracy < 0.75:
        return "medium"
    if average_score is not None and average_score < 75:
        return "medium"

    return "low"


def _generate_recommendations(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    recommendations: List[Dict[str, Any]] = []

    accuracy = metrics.get("accuracy")
    average_time = metrics.get("average_time_spent")
    questions_resolved = metrics.get("questions_resolved", 0)
    questions_asked = metrics.get("questions_asked", 0)

    if accuracy is not None and accuracy < 0.6:
        recommendations.append(
            {
                "type": "focus_practice",
                "message": "加强针对性练习，关注错误率较高的知识点。",
            }
        )
    if average_time is not None and average_time > 600:
        recommendations.append(
            {
                "type": "time_management",
                "message": "作答耗时较长，可安排课中辅导或提供示例讲解。",
            }
        )
    if questions_asked and questions_resolved < questions_asked:
        recommendations.append(
            {
                "type": "qa_follow_up",
                "message": "存在未解决的问题，建议教师重点跟进并反馈。",
            }
        )

    return recommendations


async def upsert_formative_assessment(
    db: AsyncSession,
    lesson_id: int,
    student_id: int,
    metrics: Dict[str, Any],
    phase: Optional[str] = None,
    session_id: Optional[int] = None,
) -> FormativeAssessment:
    stmt = select(FormativeAssessment).where(
        and_(
            FormativeAssessment.lesson_id == lesson_id,
            FormativeAssessment.student_id == student_id,
            FormativeAssessment.phase == phase,
            FormativeAssessment.session_id == session_id,
        )
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    risk_level = _determine_risk_level(metrics)
    recommendations = _generate_recommendations(metrics)

    if record:
        record.metrics = metrics
        record.phase = phase
        record.session_id = session_id
        record.risk_level = risk_level
        record.recommendations = recommendations
        record.updated_at = datetime.utcnow()
    else:
        record = FormativeAssessment(
            lesson_id=lesson_id,
            student_id=student_id,
            phase=phase,
            session_id=session_id,
            metrics=metrics,
            risk_level=risk_level,
            recommendations=recommendations,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)

    return record


async def recompute_formative_assessment(
    db: AsyncSession,
    lesson_id: int,
    student_id: int,
    phase: Optional[str] = None,
    session_id: Optional[int] = None,
) -> FormativeAssessment:
    metrics = await calculate_student_metrics(
        db, lesson_id, student_id, phase=phase, session_id=session_id
    )
    return await upsert_formative_assessment(
        db, lesson_id, student_id, metrics=metrics, phase=phase, session_id=session_id
    )


