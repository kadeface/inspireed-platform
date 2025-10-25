"""
Cell单元API路由
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, Cell, Lesson, CellType
from app.schemas.cell import (
    CellCreate, CellUpdate, CellResponse, CellListResponse,
    CodeExecutionRequest, CodeExecutionResponse,
    CellExecutionRequest, CellExecutionResponse,
    QAQuestionRequest, QAAnswerResponse, QACellUpdate,
    ChartDataRequest, SimConfigRequest,
    ContestSubmissionRequest, ContestSubmissionResponse
)
from app.api.deps import get_current_active_user
from app.services.ai_qa import ai_qa_service

router = APIRouter()


# ==================== 辅助函数 ====================

async def get_cell_or_404(
    cell_id: int,
    db: AsyncSession,
    current_user: User
) -> Cell:
    """获取Cell或返回404"""
    # 构建查询，包含关联的Lesson信息
    query = select(Cell).options(
        selectinload(Cell.lesson)
    ).where(Cell.id == cell_id)
    
    result = await db.execute(query)
    cell = result.scalar_one_or_none()
    
    if not cell:
        raise HTTPException(status_code=404, detail="Cell不存在")
    
    # 检查权限：学生只能访问已发布的课程
    if current_user.role == "student" and cell.lesson.status != "published":
        raise HTTPException(status_code=403, detail="无权限访问此Cell")
    
    # 检查权限：教师只能访问自己创建的课程
    if current_user.role in ["teacher", "researcher"] and cell.lesson.creator_id != current_user.id:
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
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get('question', ''),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5
    )
    
    return {
        "suggestions": suggestions,
        "cell_id": cell_id
    }


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    question = cell.content.get('question', '')
    answer = cell.content.get('answer', '')
    
    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")
    
    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)
    
    return {
        "cell_id": cell_id,
        "evaluation": evaluation,
        "question": question,
        "answer": answer
    }


async def get_lesson_or_404(
    lesson_id: int,
    db: AsyncSession,
    current_user: User
) -> Lesson:
    """获取Lesson或返回404"""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 检查权限
    if current_user.role == "student" and lesson.status != "published":
        raise HTTPException(status_code=403, detail="无权限访问此教案")
    
    if current_user.role in ["teacher", "researcher"] and lesson.creator_id != current_user.id:
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
    cell = Cell(
        **cell_in.model_dump(exclude={'lesson_id'}),
        lesson_id=cell_in.lesson_id
    )
    
    db.add(cell)
    await db.commit()
    await db.refresh(cell)
    
    return cell


@router.get("/{cell_id}/qa/suggestions")
async def get_qa_suggestions(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取QA Cell的相关问题建议"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get('question', ''),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5
    )
    
    return {
        "suggestions": suggestions,
        "cell_id": cell_id
    }


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    question = cell.content.get('question', '')
    answer = cell.content.get('answer', '')
    
    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")
    
    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)
    
    return {
        "cell_id": cell_id,
        "evaluation": evaluation,
        "question": question,
        "answer": answer
    }


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
    
    return cell


@router.get("/{cell_id}/qa/suggestions")
async def get_qa_suggestions(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取QA Cell的相关问题建议"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get('question', ''),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5
    )
    
    return {
        "suggestions": suggestions,
        "cell_id": cell_id
    }


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    question = cell.content.get('question', '')
    answer = cell.content.get('answer', '')
    
    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")
    
    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)
    
    return {
        "cell_id": cell_id,
        "evaluation": evaluation,
        "question": question,
        "answer": answer
    }


@router.get("/{cell_id}", response_model=CellResponse)
async def get_cell(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取单个Cell"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    return cell


@router.get("/{cell_id}/qa/suggestions")
async def get_qa_suggestions(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取QA Cell的相关问题建议"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get('question', ''),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5
    )
    
    return {
        "suggestions": suggestions,
        "cell_id": cell_id
    }


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    question = cell.content.get('question', '')
    answer = cell.content.get('answer', '')
    
    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")
    
    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)
    
    return {
        "cell_id": cell_id,
        "evaluation": evaluation,
        "question": question,
        "answer": answer
    }


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


@router.get("/{cell_id}/qa/suggestions")
async def get_qa_suggestions(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取QA Cell的相关问题建议"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get('question', ''),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5
    )
    
    return {
        "suggestions": suggestions,
        "cell_id": cell_id
    }


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    question = cell.content.get('question', '')
    answer = cell.content.get('answer', '')
    
    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")
    
    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)
    
    return {
        "cell_id": cell_id,
        "evaluation": evaluation,
        "question": question,
        "answer": answer
    }


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


@router.post("/{cell_id}/duplicate", response_model=CellResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_cell(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """复制Cell"""
    original_cell = await get_cell_or_404(cell_id, db, current_user)
    
    # 创建新Cell
    new_cell = Cell(
        lesson_id=original_cell.lesson_id,
        cell_type=original_cell.cell_type,
        title=f"{original_cell.title} (副本)" if original_cell.title else None,
        content=original_cell.content.copy(),
        config=original_cell.config.copy() if original_cell.config else {},
        order=original_cell.order + 1,
        editable=original_cell.editable
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
        if cell.cell_type == CellType.CODE:
            # 代码执行逻辑
            code = cell.content.get('code', '')
            language = cell.content.get('language', 'python')
            
            # 这里应该调用实际的代码执行服务
            # 暂时返回模拟结果
            output = f"执行 {language} 代码:\n{code}\n\n执行完成"
            error = None
            
        elif cell.cell_type == CellType.SIM:
            # 仿真执行逻辑
            sim_type = cell.content.get('type', 'threejs')
            config = cell.content.get('config', {})
            
            output = f"启动 {sim_type} 仿真\n配置: {config}"
            error = None
            
        elif cell.cell_type == CellType.CHART:
            # 图表渲染逻辑
            chart_type = cell.content.get('chartType', 'bar')
            data = cell.content.get('data', {})
            
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
            result={"status": "completed"}
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return CellExecutionResponse(
            success=False,
            output=None,
            error=str(e),
            execution_time=execution_time,
            result={"status": "failed"}
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
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不支持问答")
    
    import time
    start_time = time.time()
    
    try:
        if question_request.ask_ai:
            # 调用AI问答服务
            ai_response = await ai_qa_service.ask_question(
                question=question_request.question,
                context=f"Cell ID: {cell_id}",
                lesson_title=cell.lesson.title if cell.lesson else None,
                cell_content=cell.content
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
        cell.content.update({
            'question': question_request.question,
            'answer': answer,
            'isAIAnswer': is_ai_answer
        })
        await db.commit()
        
        return QAAnswerResponse(
            answer=answer,
            is_ai_answer=is_ai_answer,
            confidence=confidence,
            response_time=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        raise HTTPException(
            status_code=500, 
            detail=f"问答处理失败: {str(e)}"
        )


@router.put("/{cell_id}/qa", response_model=CellResponse)
async def update_qa_cell(
    cell_id: int,
    qa_update: QACellUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新QA Cell内容"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 更新QA内容
    update_data = qa_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            # 处理字段名映射
            if field == 'is_ai_answer':
                cell.content['isAIAnswer'] = value
            else:
                cell.content[field] = value
    
    await db.commit()
    await db.refresh(cell)
    
    return cell


@router.get("/{cell_id}/qa/suggestions")
async def get_qa_suggestions(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取QA Cell的相关问题建议"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    # 获取相关问题建议
    suggestions = await ai_qa_service.get_related_questions(
        question=cell.content.get('question', ''),
        lesson_title=cell.lesson.title if cell.lesson else None,
        limit=5
    )
    
    return {
        "suggestions": suggestions,
        "cell_id": cell_id
    }


@router.post("/{cell_id}/qa/evaluate")
async def evaluate_qa_answer(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """评估QA Cell的回答质量"""
    cell = await get_cell_or_404(cell_id, db, current_user)
    
    if cell.cell_type != CellType.QA:
        raise HTTPException(status_code=400, detail="此Cell类型不是QA类型")
    
    question = cell.content.get('question', '')
    answer = cell.content.get('answer', '')
    
    if not question or not answer:
        raise HTTPException(status_code=400, detail="问题或回答为空")
    
    # 评估回答质量
    evaluation = await ai_qa_service.evaluate_answer_quality(question, answer)
    
    return {
        "cell_id": cell_id,
        "evaluation": evaluation,
        "question": question,
        "answer": answer
    }

