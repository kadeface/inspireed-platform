"""
Cell单元API路由
"""

from typing import Any, List, Optional, Union, cast
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, Cell, Lesson, CellType
from app.schemas.cell import (
    CellCreate,
    CellUpdate,
    CellResponse,
    CellListResponse,
    CodeExecutionRequest,
    CodeExecutionResponse,
    CellExecutionRequest,
    CellExecutionResponse,
    QAQuestionRequest,
    QAAnswerResponse,
    QACellUpdate,
    ChartDataRequest,
    SimConfigRequest,
    ContestSubmissionRequest,
    ContestSubmissionResponse,
)
from app.api.deps import get_current_active_user
from app.services.ai_qa import ai_qa_service

router = APIRouter()


# ==================== 辅助函数 ====================


async def get_cell_or_404(cell_id: int, db: AsyncSession, current_user: User) -> Cell:
    """获取Cell或返回404"""
    # 构建查询，包含关联的Lesson信息
    query = select(Cell).options(selectinload(Cell.lesson)).where(Cell.id == cell_id)

    result = await db.execute(query)
    cell = result.scalar_one_or_none()

    if not cell:
        raise HTTPException(status_code=404, detail="Cell不存在")

    user_role = cast(str, current_user.role)
    lesson_status = cast(Optional[str], getattr(cell.lesson, "status", None))
    lesson_creator_id = cast(Optional[int], getattr(cell.lesson, "creator_id", None))
    current_user_id = cast(int, current_user.id)

    # 检查权限：学生只能访问已发布的课程
    if user_role == "student" and lesson_status != "published":
        raise HTTPException(status_code=403, detail="无权限访问此Cell")

    # 检查权限：教师只能访问自己创建的课程
    if user_role in ["teacher", "researcher"] and lesson_creator_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权限访问此Cell")

    return cell


@router.get("/{cell_id}/qa/suggestions")
async def get_qa_suggestions(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取QA Cell的相关问题建议"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    cell_type = cast(Optional[CellType], getattr(cell, "cell_type", None))
    if cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")

    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get("question", ""),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5,
    )

    return {"suggestions": suggestions, "cell_id": cell_id}


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    cell_type = cast(Optional[CellType], getattr(cell, "cell_type", None))
    if cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")

    question = cell.content.get("question", "")
    answer = cell.content.get("answer", "")

    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")

    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)

    return {"cell_id": cell_id, "evaluation": evaluation, "question": question, "answer": answer}


async def get_lesson_or_404(lesson_id: int, db: AsyncSession, current_user: User) -> Lesson:
    """获取Lesson或返回404"""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    # 检查权限
    user_role = cast(str, current_user.role)
    lesson_status = cast(Optional[str], getattr(lesson, "status", None))
    lesson_creator_id = cast(Optional[int], getattr(lesson, "creator_id", None))
    current_user_id = cast(int, current_user.id)

    if user_role == "student" and lesson_status != "published":
        raise HTTPException(status_code=403, detail="无权限访问此教案")

    if user_role in ["teacher", "researcher"] and lesson_creator_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权限访问此教案")

    return lesson


# ==================== Cell CRUD API ====================


@router.post("/", response_model=CellResponse, status_code=status.HTTP_201_CREATED)
async def create_cell(
    cell_in: CellCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建Cell"""
    # 验证Lesson存在且有权限
    lesson = await get_lesson_or_404(cell_in.lesson_id, db, current_user)

    # 创建Cell
    cell = Cell(**cell_in.model_dump(exclude={"lesson_id"}), lesson_id=cell_in.lesson_id)

    db.add(cell)
    await db.commit()
    await db.refresh(cell)

    return cell

@router.get("/lesson/{lesson_id}", response_model=List[CellResponse])
async def get_lesson_cells(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取指定教案的所有Cells"""
    # 验证Lesson存在且有权限
    lesson = await get_lesson_or_404(lesson_id, db, current_user)

    # 查询Cells，按order排序
    query = select(Cell).where(Cell.lesson_id == lesson_id).order_by(Cell.order, Cell.created_at)
    result = await db.execute(query)
    cells = result.scalars().all()

    return [CellResponse.model_validate(cell_obj) for cell_obj in cells]


@router.get("/{cell_id}", response_model=CellResponse)
async def get_cell(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取单个Cell"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    return cell

@router.put("/{cell_id}", response_model=CellResponse)
async def update_cell(
    cell_id: int,
    cell_update: CellUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新Cell"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    # 更新字段
    update_data = cell_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cell, field, value)

    await db.commit()
    await db.refresh(cell)

    return cell


@router.delete("/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cell(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """删除Cell"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    await db.delete(cell)
    await db.commit()


@router.post(
    "/{cell_id}/duplicate", response_model=CellResponse, status_code=status.HTTP_201_CREATED
)
async def duplicate_cell(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """复制Cell"""
    original_cell = await get_cell_or_404(cell_id, db, current_user)

    # 创建新Cell
    original_title = cast(Optional[str], getattr(original_cell, "title", None))
    original_content = cast(Optional[dict], getattr(original_cell, "content", None))
    original_config = cast(Optional[dict], getattr(original_cell, "config", None))
    original_order = cast(Optional[int], getattr(original_cell, "order", None))
    original_editable = cast(Optional[bool], getattr(original_cell, "editable", None))

    new_cell = Cell(
        lesson_id=cast(int, original_cell.lesson_id),
        cell_type=cast(CellType, original_cell.cell_type),
        title=f"{original_title} (副本)" if original_title else None,
        content=original_content.copy() if original_content else {},
        config=original_config.copy() if original_config else {},
        order=(original_order or 0) + 1,
        editable=bool(original_editable),
    )

    db.add(new_cell)
    await db.commit()
    await db.refresh(new_cell)

    return new_cell


# ==================== Cell执行API ====================


@router.post("/{cell_id}/execute", response_model=CellExecutionResponse)
async def execute_cell(
    cell_id: int,
    execution_request: CellExecutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """执行Cell"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    import time

    start_time = time.time()

    try:
        cell_type = cast(Optional[CellType], getattr(cell, "cell_type", None))
        cell_content = cast(dict, getattr(cell, "content", {}))

        if cell_type == CellType.CODE:
            # 代码执行逻辑
            code = cell_content.get("code", "")
            language = cell_content.get("language", "python")

            # 这里应该调用实际的代码执行服务
            # 暂时返回模拟结果
            output = f"执行 {language} 代码:\n{code}\n\n执行完成"
            error = None

        elif cell_type == CellType.SIM:
            # 仿真执行逻辑
            sim_type = cell_content.get("type", "threejs")
            config = cell_content.get("config", {})

            output = f"启动 {sim_type} 仿真\n配置: {config}"
            error = None

        elif cell_type == CellType.CHART:
            # 图表渲染逻辑
            chart_type = cell_content.get("chartType", "bar")
            data = cell_content.get("data", {})

            output = f"渲染 {chart_type} 图表\n数据: {data}"
            error = None

        else:
            output = f"Cell类型 {cell.cell_type} 暂不支持执行"
            error = None

        execution_time = (time.time() - start_time) * 1000

        return CellExecutionResponse(
            success=True,
            output=output,
            error=error,
            execution_time=execution_time,
            result={"status": "completed"},
        )

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return CellExecutionResponse(
            success=False,
            output=None,
            error=str(e),
            execution_time=execution_time,
            result={"status": "failed"},
        )


# ==================== QA Cell API ====================


@router.post("/{cell_id}/ask", response_model=QAAnswerResponse)
async def ask_question(
    cell_id: int,
    question_request: QAQuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """向Cell提问"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    cell_type = cast(Optional[CellType], getattr(cell, "cell_type", None))
    if cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不支持问答")

    import time

    start_time = time.time()

    try:
        if question_request.ask_ai:
            # 调用AI问答服务
            cell_content_dict = cast(Optional[dict], getattr(cell, "content", None))
            ai_response = await ai_qa_service.ask_question(
                question=question_request.question,
                context=f"Cell ID: {cell_id}",
                lesson_title=cell.lesson.title if cell.lesson else None,
                cell_content=cell_content_dict,
            )

            answer = ai_response.answer
            is_ai_answer = True
            confidence = ai_response.confidence
            response_time = ai_response.response_time
        else:
            # 教师问答逻辑
            answer = "此问题已提交给教师，请等待回复。"
            is_ai_answer = False
            confidence = None
            response_time = (time.time() - start_time) * 1000

        # 更新Cell内容
        cell.content.update(
            {"question": question_request.question, "answer": answer, "isAIAnswer": is_ai_answer}
        )
        await db.commit()

        return QAAnswerResponse(
            answer=answer,
            is_ai_answer=is_ai_answer,
            confidence=confidence,
            response_time=response_time,
        )

    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")


@router.put("/{cell_id}/qa", response_model=CellResponse)
async def update_qa_cell(
    cell_id: int,
    qa_update: QACellUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新QA Cell内容"""
    cell = await get_cell_or_404(cell_id, db, current_user)

    cell_type = cast(Optional[CellType], getattr(cell, "cell_type", None))
    if cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")

    # 更新QA内容
    update_data = qa_update.model_dump(exclude_unset=True)
    cell_content = cast(dict, getattr(cell, "content", {}))
    for field, value in update_data.items():
        if value is not None:
            # 处理字段名映射
            if field == "is_ai_answer":
                cell_content["isAIAnswer"] = value
            else:
                cell_content[field] = value

    setattr(cell, "content", cell_content)

    await db.commit()
    await db.refresh(cell)

    return cell


# ==================== 学习科学 API ====================


@router.get("/{cell_id}/dependencies")
async def get_cell_dependencies(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取Cell的依赖树
    返回当前Cell的所有前置依赖关系
    """
    cell = await get_cell_or_404(cell_id, db, current_user)

    # 获取当前lesson的所有cells
    query = select(Cell).where(Cell.lesson_id == cell.lesson_id).order_by(Cell.order)
    result = await db.execute(query)
    all_cells = result.scalars().all()

    # 构建Cell ID到Cell对象的映射
    cell_map = {str(c.id): c for c in all_cells}

    # 递归获取依赖树
    def get_dependencies_recursive(current_cell_id: str, visited=None):
        if visited is None:
            visited = set()

        if current_cell_id in visited:
            return []

        visited.add(current_cell_id)

        current_cell = cell_map.get(current_cell_id)
        if not current_cell:
            return []

        prereqs = current_cell.prerequisite_cells or []
        dependencies = []

        for prereq_id in prereqs:
            prereq_cell = cell_map.get(str(prereq_id))
            if prereq_cell:
                dep_info = {
                    "id": prereq_cell.id,
                    "title": prereq_cell.title,
                    "cognitive_level": prereq_cell.cognitive_level,
                    "order": prereq_cell.order,
                    "dependencies": get_dependencies_recursive(str(prereq_id), visited),
                }
                dependencies.append(dep_info)

        return dependencies

    dependencies = get_dependencies_recursive(str(cell.id))

    return {
        "cell_id": cell.id,
        "title": cell.title,
        "dependencies": dependencies,
        "total_prerequisites": len(dependencies),
    }


@router.get("/{cell_id}/unlock-status")
async def check_cell_unlock_status(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    检查Cell的解锁状态
    基于前置依赖关系判断当前Cell是否可以访问
    """
    cell = await get_cell_or_404(cell_id, db, current_user)

    # 如果没有前置依赖，则默认解锁
    raw_prereqs = cast(Optional[List[Any]], getattr(cell, "prerequisite_cells", None))
    prereqs_list = list(raw_prereqs or [])
    if not prereqs_list:
        return {"cell_id": cell.id, "is_locked": False, "reason": None, "missing_prerequisites": []}

    # TODO: 这里应该查询学生的学习进度数据
    # 暂时模拟：假设学生已完成部分cells
    # 在实际实现中，需要查询 student_cell_progress 表
    completed_cell_ids = []  # 应该从数据库查询

    # 检查所有前置依赖是否都已完成
    missing_prereqs: List[dict[str, Any]] = []
    completed_ids = {str(cid) for cid in completed_cell_ids}

    for prereq_id in prereqs_list:
        prereq_id_str = str(prereq_id)
        if prereq_id_str in completed_ids:
            continue

        # 获取前置Cell的信息
        prereq_id_value = cast(Union[int, str], prereq_id)
        prereq_id_int = int(prereq_id_value)
        prereq_query = select(Cell).where(Cell.id == prereq_id_int)
        prereq_result = await db.execute(prereq_query)
        prereq_cell = prereq_result.scalar_one_or_none()

        if prereq_cell:
            missing_prereqs.append(
                {
                    "id": prereq_cell.id,
                    "title": prereq_cell.title,
                    "cognitive_level": prereq_cell.cognitive_level,
                }
            )

    is_locked = len(missing_prereqs) > 0

    return {
        "cell_id": cell.id,
        "is_locked": is_locked,
        "reason": "需要完成前置单元" if is_locked else None,
        "missing_prerequisites": missing_prereqs,
        "total_prerequisites": len(prereqs_list),
        "completed_prerequisites": len(prereqs_list) - len(missing_prereqs),
    }
