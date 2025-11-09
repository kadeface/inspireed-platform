"""
问答系统API路由
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.database import get_db
from app.models import User, Question, Answer, Lesson, Cell, QuestionStatus, AskType, AnswererType
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListItem,
    QuestionListResponse,
    AnswerCreate,
    AnswerUpdate,
    AnswerResponse,
    VoteCreate,
    RatingCreate,
    UserBrief,
    LessonBrief,
    CellBrief,
    QuestionStats,
)

router = APIRouter()


# ==================== 辅助函数 ====================


async def get_question_or_404(
    question_id: int, db: AsyncSession, load_relations: bool = False
) -> Question:
    """获取问题或返回404"""
    query = select(Question)

    if load_relations:
        query = query.options(
            selectinload(Question.student),
            selectinload(Question.lesson),
            selectinload(Question.cell),
            selectinload(Question.answers).selectinload(Answer.answerer),
        )

    result = await db.execute(query.where(Question.id == question_id))
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(status_code=404, detail="问题不存在")

    return question


def build_question_list_item(question: Question, answer_count: int = 0) -> dict:
    """构建问题列表项"""
    has_ai_answer = False
    has_teacher_answer = False

    if hasattr(question, "answers") and question.answers:
        for answer in question.answers:
            if answer.answerer_type == AnswererType.AI:
                has_ai_answer = True
            elif answer.answerer_type == AnswererType.TEACHER:
                has_teacher_answer = True

    return {
        **question.__dict__,
        "student": UserBrief.model_validate(question.student),
        "lesson": LessonBrief.model_validate(question.lesson),
        "cell": CellBrief.model_validate(question.cell) if question.cell else None,
        "answer_count": (
            answer_count or len(question.answers) if hasattr(question, "answers") else 0
        ),
        "has_ai_answer": has_ai_answer,
        "has_teacher_answer": has_teacher_answer,
    }


# ==================== 学生端API ====================


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建问题（学生）

    - 学生在学习课程时提问
    - 可以向教师提问、向AI提问，或同时向两者提问
    - 如果选择AI提问，会立即生成AI回答
    """
    # 验证课程存在
    lesson = await db.get(Lesson, question_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 如果指定了cell_id，验证cell存在
    if question_in.cell_id:
        cell = await db.get(Cell, question_in.cell_id)
        if cell is None or cast(Optional[int], cell.lesson_id) != question_in.lesson_id:
            raise HTTPException(status_code=404, detail="Cell不存在或不属于该课程")

    # 创建问题
    question = Question(
        **question_in.model_dump(), student_id=current_user.id, status=QuestionStatus.PENDING
    )

    db.add(question)
    await db.commit()
    await db.refresh(question)

    # 如果需要AI回答，创建AI回答（这里暂时使用简单的模拟）
    ai_answer = None
    if question_in.ask_type in [AskType.AI, AskType.BOTH]:
        # TODO: 集成真正的AI服务
        # 目前使用模拟回答
        ai_answer = Answer(
            question_id=question.id,
            answerer_type=AnswererType.AI,
            content=[
                {
                    "id": "ai-1",
                    "cell_type": "text",
                    "title": "AI回答",
                    "content": {
                        "text": f"<p>关于您的问题「{question.title}」，我来帮您解答：</p><p>{question.content}</p><p>这是一个AI生成的临时回答。完整的AI功能正在开发中。</p>"
                    },
                }
            ],
            ai_model="mock-ai",
            ai_prompt_tokens=100,
            ai_completion_tokens=200,
        )
        db.add(ai_answer)

        # 更新问题状态为已回答
        setattr(question, "status", QuestionStatus.ANSWERED)

        await db.commit()
        await db.refresh(ai_answer)

    # 重新加载问题以包含关联数据
    question = await get_question_or_404(cast(int, question.id), db, load_relations=True)

    return question


@router.get("/my", response_model=QuestionListResponse)
async def get_my_questions(
    lesson_id: Optional[int] = Query(None, description="按课程筛选"),
    status: Optional[QuestionStatus] = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取我的问题列表（学生）
    """
    # 构建查询
    query = select(Question).where(Question.student_id == current_user.id)

    if lesson_id:
        query = query.where(Question.lesson_id == lesson_id)

    if status:
        query = query.where(Question.status == status)

    # 加载关联数据
    query = query.options(
        selectinload(Question.student),
        selectinload(Question.lesson),
        selectinload(Question.cell),
        selectinload(Question.answers),
    )

    # 总数
    count_query = (
        select(func.count()).select_from(Question).where(Question.student_id == current_user.id)
    )
    if lesson_id:
        count_query = count_query.where(Question.lesson_id == lesson_id)
    if status:
        count_query = count_query.where(Question.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.order_by(Question.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    questions = result.scalars().all()

    # 构建响应
    items = [QuestionListItem(**build_question_list_item(q)) for q in questions]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": total is not None and page * page_size < total,
    }


@router.get("/lesson/{lesson_id}", response_model=QuestionListResponse)
async def get_lesson_questions(
    lesson_id: int,
    sort: str = Query("recent", regex="^(recent|popular|upvotes)$", description="排序方式"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取课程的所有公开问答

    - 其他学生可以查看公开的问题和回答
    - 支持按最新、最热、点赞数排序
    """
    # 验证课程存在
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 构建查询（只显示公开的问题）
    query = select(Question).where(
        and_(Question.lesson_id == lesson_id, Question.is_public == True)
    )

    # 加载关联数据
    query = query.options(
        selectinload(Question.student),
        selectinload(Question.lesson),
        selectinload(Question.cell),
        selectinload(Question.answers),
    )

    # 排序
    if sort == "popular":
        query = query.order_by(Question.views.desc(), Question.upvotes.desc())
    elif sort == "upvotes":
        query = query.order_by(Question.upvotes.desc())
    else:  # recent
        query = query.order_by(Question.created_at.desc())

    # 总数
    count_query = (
        select(func.count())
        .select_from(Question)
        .where(and_(Question.lesson_id == lesson_id, Question.is_public == True))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    questions = result.scalars().all()

    # 构建响应
    items = [QuestionListItem(**build_question_list_item(q)) for q in questions]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": total is not None and page * page_size < total,
    }


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question_detail(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取问题详情（包含所有回答）

    - 自动增加查看次数
    - 返回所有回答（AI回答和教师回答）
    """
    question = await get_question_or_404(question_id, db, load_relations=True)

    # 权限检查：只有提问者和教师可以查看私有问题
    is_public = cast(Optional[bool], question.is_public) or False
    student_id = cast(Optional[int], question.student_id)
    if (
        not is_public
        and student_id != current_user.id
        and current_user.role.value != "teacher"
    ):
        raise HTTPException(status_code=403, detail="无权查看该问题")

    # 增加查看次数
    current_views = cast(Optional[int], question.views) or 0
    setattr(question, "views", current_views + 1)
    await db.commit()

    return question


@router.put("/{question_id}/resolve", response_model=QuestionResponse)
async def resolve_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    标记问题为已解决（学生）
    """
    question = await get_question_or_404(question_id, db)

    # 只有提问者可以标记为已解决
    student_id = cast(Optional[int], question.student_id)
    if student_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有提问者可以标记问题为已解决")

    setattr(question, "status", QuestionStatus.RESOLVED)
    await db.commit()

    # 重新加载
    question = await get_question_or_404(question_id, db, load_relations=True)
    return question


# ==================== 教师端API ====================


@router.get("/teacher/pending", response_model=QuestionListResponse)
async def get_teacher_pending_questions(
    lesson_id: Optional[int] = Query(None, description="按课程筛选"),
    sort: str = Query("created_at", regex="^(created_at|upvotes)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_teacher),
) -> Any:
    """
    获取待回答的问题列表（教师）

    - 显示所有向教师提问且未回答的问题
    - 可以按课程筛选
    """
    # 构建查询：待回答或只有AI回答的问题
    query = select(Question).where(
        or_(Question.ask_type == AskType.TEACHER, Question.ask_type == AskType.BOTH)
    )

    if lesson_id:
        query = query.where(Question.lesson_id == lesson_id)

    # 加载关联数据
    query = query.options(
        selectinload(Question.student),
        selectinload(Question.lesson),
        selectinload(Question.cell),
        selectinload(Question.answers),
    )

    # 排序
    if sort == "upvotes":
        query = query.order_by(Question.upvotes.desc())
    else:
        query = query.order_by(Question.created_at.desc())

    # 总数
    count_query = (
        select(func.count())
        .select_from(Question)
        .where(or_(Question.ask_type == AskType.TEACHER, Question.ask_type == AskType.BOTH))
    )
    if lesson_id:
        count_query = count_query.where(Question.lesson_id == lesson_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    questions = result.scalars().all()

    # 过滤出还没有教师回答的问题
    pending_questions = []
    for q in questions:
        has_teacher_answer = any(a.answerer_type == AnswererType.TEACHER for a in q.answers)
        if not has_teacher_answer:
            pending_questions.append(q)

    # 构建响应
    items = [QuestionListItem(**build_question_list_item(q)) for q in pending_questions]

    return {
        "items": items,
        "total": len(pending_questions),
        "page": page,
        "page_size": page_size,
        "has_more": False,
    }


@router.get("/teacher/stats", response_model=QuestionStats)
async def get_teacher_question_stats(
    lesson_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_teacher),
) -> Any:
    """
    获取问题统计（教师）
    """
    base_query = select(func.count()).select_from(Question)

    if lesson_id:
        base_query = base_query.where(Question.lesson_id == lesson_id)

    # 总数
    total_result = await db.execute(base_query)
    total = total_result.scalar()

    # 按状态统计
    stats = {"total": total}
    for status_value in QuestionStatus:
        status_query = base_query.where(Question.status == status_value)
        result = await db.execute(status_query)
        stats[status_value.value] = result.scalar()

    return stats


@router.put("/{question_id}/pin", response_model=QuestionResponse)
async def pin_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_teacher),
) -> Any:
    """
    置顶/取消置顶问题（教师）

    - 用于标记优质问答
    """
    question = await get_question_or_404(question_id, db)

    setattr(question, "is_pinned", not cast(bool, question.is_pinned))
    await db.commit()

    question = await get_question_or_404(question_id, db, load_relations=True)
    return question


# ==================== Answer相关API ====================


@router.post("/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    answer_in: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_teacher),
) -> Any:
    """
    教师回答问题

    - 使用Cell模块方式回答
    - 可以包含文本、代码、图表等多种Cell类型
    """
    # 验证问题存在
    question = await get_question_or_404(answer_in.question_id, db)

    # 创建回答
    answer = Answer(
        **answer_in.model_dump(), answerer_type=AnswererType.TEACHER, answerer_id=current_user.id
    )

    db.add(answer)

    # 更新问题状态
    if cast(str, question.status) == QuestionStatus.PENDING:
        setattr(question, "status", QuestionStatus.ANSWERED)

    await db.commit()
    await db.refresh(answer)

    # 加载回答者信息
    result = await db.execute(
        select(Answer).options(selectinload(Answer.answerer)).where(Answer.id == answer.id)
    )
    answer = result.scalar_one()

    return answer


@router.put("/answers/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    answer_id: int,
    answer_in: AnswerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.require_teacher),
) -> Any:
    """
    更新回答（教师）
    """
    answer = await db.get(Answer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="回答不存在")

    # 权限检查
    answerer_id = cast(Optional[int], answer.answerer_id)
    if answerer_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该回答")

    # 更新
    update_data = answer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(answer, field, value)

    await db.commit()
    await db.refresh(answer)

    # 加载回答者信息
    result = await db.execute(
        select(Answer).options(selectinload(Answer.answerer)).where(Answer.id == answer.id)
    )
    answer = result.scalar_one()

    return answer


@router.post("/answers/{answer_id}/rate", response_model=AnswerResponse)
async def rate_answer(
    answer_id: int,
    rating_in: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    对回答评分（学生）
    """
    answer = await db.get(Answer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="回答不存在")

    # 获取问题，确保是提问者
    question = await get_question_or_404(cast(int, answer.question_id), db)
    student_id = cast(Optional[int], question.student_id)
    if student_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有提问者可以评分")

    setattr(answer, "rating", rating_in.rating)
    await db.commit()
    await db.refresh(answer)

    # 加载回答者信息
    result = await db.execute(
        select(Answer).options(selectinload(Answer.answerer)).where(Answer.id == answer.id)
    )
    answer = result.scalar_one()

    return answer
