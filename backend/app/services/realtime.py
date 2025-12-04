"""
实时通知服务
提供统一的 WebSocket 消息构建和目标解析
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Union, cast, Dict, Any, List
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.organization import Classroom
from app.models.classroom_session import ClassSession
from app.models.activity import ActivitySubmission
from app.models.user import User


@dataclass(frozen=True)
class Channel:
    """WebSocket 通道描述符"""
    scope: Literal["session", "lesson"]
    id: int


@dataclass
class RealtimeTarget:
    """实时通知目标描述符"""
    channel: Channel
    recipient_ids: list[int]

    @property
    def is_broadcast(self) -> bool:
        """是否为广播模式（所有人）"""
        return len(self.recipient_ids) == 0

    @classmethod
    def session(cls, session_id: int, teacher_ids: Optional[list[int]] = None):
        """创建课堂会话目标"""
        return cls(
            channel=Channel(scope="session", id=session_id),
            recipient_ids=teacher_ids or []
        )

    @classmethod
    def lesson(cls, lesson_id: int, teacher_ids: Optional[list[int]] = None):
        """创建课后教案目标"""
        return cls(
            channel=Channel(scope="lesson", id=lesson_id),
            recipient_ids=teacher_ids or []
        )


def build_event(
    *,
    type: str,
    channel: Channel,
    delivery_mode: Literal["cast", "unicast"],
    data: dict,
    ack_token: Optional[str] = None
) -> dict:
    """
    构建统一的 WebSocket 事件消息
    
    参数:
        type: 事件类型（如 'new_submission', 'submission_graded'）
        channel: 消息通道
        delivery_mode: 投递模式（cast=广播, unicast=单播）
        data: 事件数据
        ack_token: 可选的确认令牌
    
    返回:
        标准化的事件消息字典
    """
    return {
        "event_id": str(uuid4()),
        "version": 1,
        "type": type,
        "timestamp": datetime.utcnow().isoformat(),
        "channel": {
            "scope": channel.scope,
            "id": channel.id
        },
        "delivery_mode": delivery_mode,
        "data": data,
        "ack_token": ack_token,
    }


async def resolve_teacher_targets(
    db: AsyncSession,
    submission: ActivitySubmission
) -> Optional[RealtimeTarget]:
    """
    解析教师通知目标
    
    课堂模式：channel.scope = session，绑定 session_id
    课后模式：channel.scope = lesson，获取所有相关教师
    
    参数:
        db: 数据库会话
        submission: 活动提交
    
    返回:
        RealtimeTarget 或 None（如果无法确定目标）
    """
    # 课堂模式：有 session_id
    session_id = cast(int, submission.session_id) if submission.session_id is not None else None
    if session_id is not None:
        session = await db.get(ClassSession, session_id)
        teacher_id = cast(int, session.teacher_id) if session and session.teacher_id is not None else None
        if session is not None and teacher_id is not None:
            return RealtimeTarget.session(
                session_id=session_id,
                teacher_ids=[teacher_id]
            )
    
    # 课后模式：根据 lesson -> classroom -> teacher 映射
    lesson_id = cast(int, submission.lesson_id)
    teacher_ids = await fetch_teachers_by_lesson(db, lesson_id)
    if teacher_ids:
        return RealtimeTarget.lesson(
            lesson_id=lesson_id,
            teacher_ids=teacher_ids
        )
    
    return None


async def resolve_student_target(
    db: AsyncSession,
    submission: ActivitySubmission
) -> Optional[RealtimeTarget]:
    """
    解析学生通知目标
    
    课堂模式：channel.scope = session
    课后模式：channel.scope = lesson
    
    参数:
        db: 数据库会话
        submission: 活动提交
    
    返回:
        RealtimeTarget 或 None
    """
    student_id = cast(int, submission.student_id)
    session_id = cast(int, submission.session_id) if submission.session_id is not None else None
    lesson_id = cast(int, submission.lesson_id)
    
    # 课堂模式
    if session_id is not None:
        return RealtimeTarget.session(
            session_id=session_id,
            teacher_ids=[student_id]  # 复用 teacher_ids 字段存储学生ID
        )
    
    # 课后模式
    return RealtimeTarget.lesson(
        lesson_id=lesson_id,
        teacher_ids=[student_id]
    )


async def fetch_teachers_by_lesson(
    db: AsyncSession,
    lesson_id: int
) -> list[int]:
    """
    获取有权访问指定教案的所有教师ID
    
    目前直接从教案创建者获取教师ID
    未来可以扩展为通过 ClassSession 关联查询
    
    参数:
        db: 数据库会话
        lesson_id: 教案ID
    
    返回:
        教师ID列表
    """
    teacher_ids = []
    
    # 方案1: 通过 ClassSession 获取教师（推荐）
    try:
        result = await db.execute(
            select(ClassSession.teacher_id)
            .where(ClassSession.lesson_id == lesson_id)
            .distinct()
        )
        teacher_ids = [row[0] for row in result.all() if row[0] is not None]
    except Exception:
        pass  # 如果 ClassSession 表结构不匹配，忽略错误
    
    # 方案2: 从 Lesson 的创建者获取
    if not teacher_ids:
        lesson = await db.get(Lesson, lesson_id)
        if lesson and lesson.teacher_id:
            teacher_ids = [lesson.teacher_id]
    
    return teacher_ids


async def get_submission_statistics(
    db: AsyncSession,
    cell_id: Union[int, str],  # 支持数字 ID 或 UUID 字符串
    lesson_id: int,
    session_id: Optional[int] = None,
) -> dict:
    """
    获取提交统计信息
    
    课堂模式：统计参与该会话的学生
    课后模式：统计所有班级的学生
    
    参数:
        db: 数据库会话
        cell_id: Cell ID
        lesson_id: 教案ID
        session_id: 可选的会话ID（课堂模式）
    
    返回:
        统计信息字典
    """
    from sqlalchemy import func, select as sql_select
    from app.models.activity import ActivitySubmissionStatus
    from app.models.classroom_session import StudentSessionParticipation
    
    # 计算总学生数
    if session_id:
        # 课堂模式：统计参与该会话的学生数
        total_students_result = await db.execute(
            sql_select(func.count(StudentSessionParticipation.id))
            .where(StudentSessionParticipation.session_id == session_id)
        )
        total_students = int(total_students_result.scalar() or 0)
    else:
        # 课后模式：当前未实现完整的课后模式统计
        # TODO: 实现课后模式的学生统计逻辑
        # 可以考虑从 lesson 的 creator 的 classroom 统计，或者从提交记录推断
        total_students = 0
    
    # 统计各状态的提交数
    # 注意：需要对每个学生只统计优先级最高的提交
    from app.models.activity import ActivitySubmission
    
    # 如果 cell_id 是 UUID 字符串，需要先转换为数字 ID
    from app.models.cell import Cell
    from app.models.lesson import Lesson
    
    actual_cell_id: Union[int, str] = cell_id
    if isinstance(cell_id, str):
        # 先尝试直接转换为整数（可能是数字字符串）
        try:
            actual_cell_id = int(cell_id)
        except ValueError:
            # 是 UUID 格式，需要从 lesson.content 中查找对应的数据库 ID
            # 如果 lesson_id 为 None，无法进行 UUID 转换
            if lesson_id is None:
                # 无法转换 UUID，返回空统计
                return {
                    "cell_id": cell_id,  # 保持原始格式
                    "lesson_id": lesson_id,
                    "total_students": total_students,
                    "submitted_count": 0,  # 已提交包括已评分
                    "draft_count": 0,
                    "not_started_count": max(0, total_students),
                    "average_score": None,
                    "average_time_spent": 0,
                    "item_statistics": {},  # 添加空字典而不是 None
                }
            
            lesson = await db.get(Lesson, lesson_id)
            if lesson is not None and lesson.content is not None:
                lesson_content = cast(Optional[List[Dict[str, Any]]], lesson.content)
                if lesson_content:
                    for cell_data in lesson_content:
                        cell_uuid = cell_data.get("id")
                        if str(cell_uuid) == cell_id:
                            # 找到了匹配的 UUID，通过 order 查找数据库 ID
                            cell_order = cell_data.get("order")
                            cell_type = cell_data.get("type") or cell_data.get("cell_type")
                            if cell_order is not None:
                                cell_result = await db.execute(
                                    sql_select(Cell)
                                    .where(Cell.lesson_id == lesson_id)
                                    .where(Cell.order == cell_order)
                                )
                                matched_cell = cell_result.scalar_one_or_none()
                                if matched_cell:
                                    actual_cell_id = cast(int, matched_cell.id)
                                    break
    
    # 确保 actual_cell_id 是整数类型，否则无法查询数据库
    if not isinstance(actual_cell_id, int):
        # 如果仍然无法转换为整数，返回空统计
        # 这通常发生在 UUID 无法在 lesson.content 中找到匹配的情况
        return {
            "cell_id": cell_id,  # 保持原始格式
            "lesson_id": lesson_id,
            "total_students": total_students,
            "submitted_count": 0,  # 已提交包括已评分
            "draft_count": 0,
            "not_started_count": max(0, total_students),
            "average_score": None,
            "average_time_spent": 0,
            "item_statistics": {},  # 添加空字典而不是 None
        }
    
    # 查询所有提交，按优先级排序
    query = (
        sql_select(ActivitySubmission)
        .where(ActivitySubmission.cell_id == actual_cell_id)
        .where(ActivitySubmission.lesson_id == lesson_id)
        .order_by(ActivitySubmission.updated_at.desc())
    )
    
    if session_id:
        query = query.where(ActivitySubmission.session_id == session_id)
    
    submissions_result = await db.execute(query)
    all_submissions = submissions_result.scalars().all()
    
    # 对每个学生，只保留优先级最高的提交
    status_priority = {
        ActivitySubmissionStatus.DRAFT: 1,
        ActivitySubmissionStatus.RETURNED: 2,
        ActivitySubmissionStatus.SUBMITTED: 3,
        ActivitySubmissionStatus.GRADED: 4,
    }
    
    student_best_submission = {}  # student_id -> submission
    for submission in all_submissions:
        student_id = submission.student_id
        if student_id not in student_best_submission:
            student_best_submission[student_id] = submission
        else:
            # 使用 cast 进行类型转换
            current_status = cast(ActivitySubmissionStatus, submission.status)
            existing_status = cast(ActivitySubmissionStatus, student_best_submission[student_id].status)
            
            current_priority = status_priority.get(current_status, 0)
            existing_priority = status_priority.get(existing_status, 0)
            
            # 如果当前记录优先级更高，或优先级相同但更新时间更晚
            if current_priority > existing_priority or (
                current_priority == existing_priority and 
                submission.updated_at > student_best_submission[student_id].updated_at
            ):
                student_best_submission[student_id] = submission
    
    # 统计各状态的数量
    status_dict: dict[str, int] = {}
    for submission in student_best_submission.values():
        status = cast(ActivitySubmissionStatus, submission.status)
        status_value = status.value
        status_dict[status_value] = status_dict.get(status_value, 0) + 1
    
    # 计算平均分和平均用时（基于已筛选的最佳提交）
    submitted_or_graded = [
        s for s in student_best_submission.values()
        if s.status in [ActivitySubmissionStatus.SUBMITTED, ActivitySubmissionStatus.GRADED]
    ]
    
    avg_score = None
    avg_time = None
    
    if submitted_or_graded:
        scores = [s.score for s in submitted_or_graded if s.score is not None]
        times = [s.time_spent for s in submitted_or_graded if s.time_spent is not None]
        
        if scores:
            avg_score = sum(scores) / len(scores)
        if times:
            avg_time = sum(times) / len(times)
    
    # 计算已处理的提交数（已提交+已评分+已退回）
    submitted_count = status_dict.get("submitted", 0)
    graded_count = status_dict.get("graded", 0)
    returned_count = status_dict.get("returned", 0)
    draft_count = status_dict.get("draft", 0)
    
    processed_count = submitted_count + graded_count + returned_count
    not_started_count = max(0, total_students - processed_count - draft_count)
    
    # 计算题目级统计（item_statistics）
    item_aggregates: Dict[str, Dict[str, Any]] = {}
    for submission in student_best_submission.values():
        responses = submission.responses or {}
        for item_id, item_value in responses.items():
            # 处理不同的答案格式：
            # 1. 如果 item_value 是字符串（直接是选项ID），如 "opt1"
            # 2. 如果 item_value 是对象，如 { "answer": "opt1" } 或 { "answer": ["opt1", "opt2"] }
            # 3. 如果 item_value 是数组（多选题），如 ["opt1", "opt2"]
            
            aggregate = item_aggregates.setdefault(
                item_id,
                {
                    "attempts": 0,
                    "correct_count": 0,
                    "scores": [],
                    "options": {},
                    "knowledge": {},
                    "times": [],
                },
            )
            aggregate["attempts"] += 1
            
            # 提取答案
            answer = None
            if isinstance(item_value, dict):
                # 对象格式：{ "answer": "opt1", "correct": true, ... }
                if item_value.get("is_correct") or item_value.get("correct"):
                    aggregate["correct_count"] += 1
                
                score = item_value.get("score")
                if isinstance(score, (int, float)):
                    aggregate["scores"].append(float(score))
                
                time_spent = item_value.get("time_spent")
                if isinstance(time_spent, (int, float)):
                    aggregate["times"].append(float(time_spent))
                
                answer = item_value.get("answer") or item_value.get("value") or item_value.get("text")
            elif isinstance(item_value, (str, int, float)):
                # 直接是选项ID字符串或数字，如 "opt1" 或 "1"
                answer = item_value
            elif isinstance(item_value, list):
                # 数组格式（多选题），如 ["opt1", "opt2"]
                answer = item_value
            
            # 统计选项分布
            if isinstance(answer, list):
                # 多选题：答案是数组
                for option in answer:
                    key = str(option)
                    aggregate["options"][key] = aggregate["options"].get(key, 0) + 1
            elif answer is not None:
                # 单选题：答案是单个值
                key = str(answer)
                aggregate["options"][key] = aggregate["options"].get(key, 0) + 1
            
            # 处理知识标签（仅在 item_value 是字典时）
            if isinstance(item_value, dict):
                knowledge_tags = item_value.get("knowledge_tags") or item_value.get("tags")
                if isinstance(knowledge_tags, list):
                    for tag in knowledge_tags:
                        tag_key = str(tag)
                        aggregate["knowledge"][tag_key] = aggregate["knowledge"].get(tag_key, 0) + 1
    
    # 汇总题目级统计
    item_statistics: Dict[str, Dict[str, Any]] = {}
    for item_id, aggregate in item_aggregates.items():
        item_stat = {
            "attempts": aggregate["attempts"],
            "correct_count": aggregate["correct_count"],
            "accuracy": aggregate["correct_count"] / aggregate["attempts"] if aggregate["attempts"] > 0 else 0.0,
        }
        
        if aggregate["scores"]:
            item_stat["avg_score"] = sum(aggregate["scores"]) / len(aggregate["scores"])
            item_stat["min_score"] = min(aggregate["scores"])
            item_stat["max_score"] = max(aggregate["scores"])
        
        if aggregate["options"]:
            item_stat["option_distribution"] = aggregate["options"]
        
        if aggregate["times"]:
            item_stat["avg_time"] = sum(aggregate["times"]) / len(aggregate["times"])
        
        if aggregate["knowledge"]:
            item_stat["knowledge_distribution"] = aggregate["knowledge"]
        
        item_statistics[item_id] = item_stat
    
    # 返回时使用原始的 cell_id（可能是 UUID 字符串）
    return {
        "cell_id": cell_id,  # 保持原始格式（UUID 或数字 ID）
        "lesson_id": lesson_id,
        "total_students": total_students,
        "submitted_count": submitted_count + graded_count,  # 已提交包括已评分
        "draft_count": draft_count,
        "not_started_count": not_started_count,
        "average_score": float(avg_score) if avg_score is not None else None,
        "average_time_spent": int(avg_time) if avg_time is not None else 0,
        "item_statistics": item_statistics,  # 总是返回字典（可能为空），而不是 None
    }

