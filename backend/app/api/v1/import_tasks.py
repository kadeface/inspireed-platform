"""
导入任务API

提供Excel成绩导入任务的创建、查询和管理功能
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse

from app.api.deps import get_db, get_current_active_user
from app.models import User, Exam, ImportTask, UserRole, ImportStatus
from app.schemas.evaluation import (
    ImportTaskCreate,
    ImportTaskResponse,
    ImportTaskWithProgressResponse,
)
from app.services.excel_import_service import ExcelImportService, ExcelImportError
from app.services.upload import UploadService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ImportTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_import_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks,
    task_name: str = Query(..., description="任务名称", max_length=200),
    exam_id: int = Query(..., description="考试ID"),
    file: UploadFile = File(..., description="Excel文件"),
    auto_process: bool = Query(True, description="是否自动处理"),
) -> Any:
    """
    创建新的导入任务

    上传Excel文件并创建导入任务

    权限说明：
    - 管理员、区县管理员、学校管理员可以创建导入任务

    Excel格式要求：
    - 必需列：考号、学籍号、科目、原始分
    - 可选列：姓名、缺考、作弊
    - 支持格式：.xlsx, .xls

    返回导入任务信息
    """
    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建导入任务"
        )

    # 验证考试是否存在
    exam_result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # 验证文件类型
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须上传文件"
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持Excel文件格式 (.xlsx, .xls)"
        )

    # 保存文件
    try:
        upload_service = UploadService()
        upload_result = await upload_service.upload_file(file)

        # 创建导入任务
        import_task = ImportTask(
            task_name=task_name,
            task_type="score_data",
            exam_id=exam_id,
            file_url=upload_result["file_url"],
            file_name=file.filename,
            file_size=upload_result["file_size"],
            status=ImportStatus.PENDING,
            progress=0,
            created_by=current_user.id,
        )
        db.add(import_task)
        await db.commit()
        await db.refresh(import_task)

        # 如果需要自动处理，添加后台任务
        if auto_process:
            background_tasks.add_task(process_import_task_background, import_task.id)

        return import_task

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/{task_id}", response_model=ImportTaskWithProgressResponse)
async def get_import_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    task_id: int,
) -> Any:
    """
    获取导入任务详情

    返回任务的详细信息和当前进度
    """
    # 查询任务
    result = await db.execute(
        select(ImportTask).where(ImportTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入任务不存在"
        )

    # 权限检查：创建者和管理员可以查看
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能查看自己创建的任务"
            )

    return task


@router.get("/", response_model=list[ImportTaskResponse])
async def list_import_tasks(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    exam_id: Optional[int] = Query(None, description="考试ID筛选"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
) -> Any:
    """
    获取导入任务列表

    权限说明：
    - 管理员：可查看所有任务
    - 其他用户：只能查看自己创建的任务
    """
    # 构建查询条件
    conditions = []

    # 根据角色限制数据访问
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        conditions.append(ImportTask.created_by == current_user.id)

    # 应用筛选条件
    if exam_id:
        conditions.append(ImportTask.exam_id == exam_id)

    if status_filter:
        try:
            status_enum = ImportStatus(status_filter)
            conditions.append(ImportTask.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {status_filter}"
            )

    # 执行查询
    if conditions:
        query = select(ImportTask).where(
            and_(*conditions)
        ).order_by(desc(ImportTask.created_at)).offset(skip).limit(limit)
    else:
        query = select(ImportTask).order_by(
            desc(ImportTask.created_at)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.post("/{task_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_import_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    task_id: int,
) -> Any:
    """
    取消导入任务

    只能取消待处理或处理中的任务

    权限说明：
    - 管理员：可以取消任何任务
    - 其他用户：只能取消自己创建的任务
    """
    # 查询任务
    result = await db.execute(
        select(ImportTask).where(ImportTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入任务不存在"
        )

    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能取消自己创建的任务"
            )

    # 检查任务状态
    if task.status in [ImportStatus.COMPLETED, ImportStatus.FAILED, ImportStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务已{task.status}，无法取消"
        )

    # 更新任务状态
    task.status = ImportStatus.CANCELLED
    task.completed_at = datetime.utcnow()
    await db.commit()

    return {
        "message": "任务已取消",
        "task_id": task_id
    }


@router.get("/{task_id}/errors", response_model=dict)
async def get_import_task_errors(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    task_id: int,
) -> Any:
    """
    获取导入任务的错误详情

    返回详细的错误信息列表
    """
    # 查询任务
    result = await db.execute(
        select(ImportTask).where(ImportTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入任务不存在"
        )

    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能查看自己创建的任务"
            )

    if not task.error_details:
        return {
            "task_id": task_id,
            "error_message": task.error_message,
            "errors": []
        }

    return {
        "task_id": task_id,
        "error_message": task.error_message,
        "errors": task.error_details.get("errors", [])
    }


@router.post("/{task_id}/retry", response_model=ImportTaskResponse)
async def retry_import_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks,
    task_id: int,
) -> Any:
    """
    重试失败的导入任务

    重置任务状态并重新处理

    权限说明：
    - 管理员：可以重试任何任务
    - 其他用户：只能重试自己创建的任务
    """
    # 查询任务
    result = await db.execute(
        select(ImportTask).where(ImportTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入任务不存在"
        )

    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能重试自己创建的任务"
            )

    # 检查任务状态
    if task.status != ImportStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能重试失败的任务"
        )

    # 重置任务状态
    task.status = ImportStatus.PENDING
    task.progress = 0
    task.processed_rows = 0
    task.failed_rows = 0
    task.error_message = None
    task.error_details = None
    task.started_at = None
    task.completed_at = None
    await db.commit()

    # 在后台异步处理
    background_tasks.add_task(process_import_task_background, task_id)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_import_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    task_id: int,
) -> None:
    """
    删除导入任务

    注意：删除任务不会删除已导入的成绩数据

    权限说明：
    - 管理员、区县管理员：可以删除任何任务
    - 其他管理员：只能删除自己创建的任务
    """
    # 查询任务
    result = await db.execute(
        select(ImportTask).where(ImportTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导入任务不存在"
        )

    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN]:
        if task.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己创建的任务"
            )

    # 删除上传的文件
    if task.file_url:
        try:
            from app.services.upload import UploadService
            upload_service = UploadService()
            file_path = os.path.join(upload_service.resources_dir, task.file_url)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"删除文件失败: {e}")

    # 删除任务
    await db.delete(task)
    await db.commit()


# ============================================================================
# 异步处理函数
# ============================================================================

async def process_import_task_background(task_id: int) -> None:
    """
    后台处理导入任务

    这个函数会在后台任务中执行，不阻塞主线程
    """
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            await ExcelImportService.process_import_task(db, task_id)
        except Exception as e:
            logger.error(f"处理导入任务 {task_id} 失败: {e}")
