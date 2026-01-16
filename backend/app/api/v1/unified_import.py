"""
Unified Import API Endpoint

Provides a single endpoint for all Excel-based imports.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models import User
from app.schemas.import_schemas import (
    ImportStrategyType,
    ImportResult,
    SchoolImportResult,
    TeacherImportResult,
    SchoolImportResponse,
    SchoolImportError,
)
from app.services.import_orchestrator import ImportOrchestrator

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import", tags=["import"])


@router.post("", response_model=ImportResult)
async def unified_import(
    strategy_type: ImportStrategyType = Query(..., description="Import strategy type"),
    file: UploadFile = File(..., description="Excel file"),
    update_existing: bool = Query(False, description="Update existing records"),
    auto_create: bool = Query(True, description="Auto-create related entities (regions, teachers, etc.)"),
    exam_id: Optional[int] = Query(None, description="Exam ID (for student imports)"),
    school_id: Optional[int] = Query(None, description="School ID (for classroom imports)"),
    region_id: Optional[int] = Query(None, description="Region ID (for classroom imports)"),
    is_school_admin: bool = Query(False, description="School admin mode (for classroom imports)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """
    Unified import endpoint for Excel-based imports

    Supports:
    - **school**: Import schools with region auto-creation
    - **classroom**: Import classrooms (dual-mode: district or school admin)
    - **student**: Import student exam mappings (requires exam_id)
    - **teacher**: Import teacher assignments (with teacher/semester auto-creation)

    **Parameters:**
    - **strategy_type**: Import type (school, classroom, student, teacher)
    - **file**: Excel file (.xlsx or .xls)
    - **update_existing**: Update existing records instead of skipping them
    - **auto_create**: Auto-create related entities (regions, teachers, semesters)
    - **exam_id**: Required for student imports
    - **school_id**: Required for classroom imports in school admin mode
    - **region_id**: Optional region ID for classroom imports
    - **is_school_admin**: Enable school admin mode for classroom imports

    **Returns:**
    Import result with statistics and error details
    """

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="必须上传文件")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        raise HTTPException(
            status_code=400,
            detail=f"只支持Excel文件格式 (.xlsx, .xls)，当前文件格式: {file_ext}"
        )

    # Build context
    context = {
        "update_existing": update_existing,
        "auto_create": auto_create,
        "auto_create_region": auto_create,
        "auto_create_teachers": auto_create,
        "auto_create_semesters": auto_create,
        "exam_id": exam_id,
        "school_id": school_id,
        "region_id": region_id,
        "is_school_admin": is_school_admin,
    }

    # Save to temp file
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="上传的文件为空")
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)

        logger.info(
            f"Processing {strategy_type} import: {file.filename} "
            f"({len(content)} bytes)"
        )

        # Execute import
        orchestrator = ImportOrchestrator()
        result = await orchestrator.execute_import(
            db=db,
            strategy_type=strategy_type.value,
            file_path=temp_file_path,
            context=context
        )

        # Return appropriate response type based on strategy
        if strategy_type == ImportStrategyType.SCHOOL:
            return SchoolImportResult(**result)
        elif strategy_type == ImportStrategyType.TEACHER:
            return TeacherImportResult(**result)
        else:
            return ImportResult(**result)

    except HTTPException:
        raise
    except ValueError as e:
        # Invalid strategy type
        logger.error(f"Invalid strategy: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Import failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

    finally:
        # Clean up temp file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")


@router.get("/strategies")
async def list_strategies():
    """List available import strategies

    Returns information about supported import types and their requirements.
    """
    return {
        "strategies": [
            {
                "type": "school",
                "name": "学校导入",
                "description": "导入学校信息，支持自动创建区域",
                "required_context": [],
                "optional_context": ["auto_create_region"],
            },
            {
                "type": "classroom",
                "name": "班级导入",
                "description": "导入班级信息，支持县区端和学校端两种模式",
                "required_context": [],
                "optional_context": ["school_id", "region_id", "is_school_admin", "update_existing"],
            },
            {
                "type": "student",
                "name": "学生导入",
                "description": "导入学生考试映射，将学生与考号关联",
                "required_context": ["exam_id"],
                "optional_context": [],
            },
            {
                "type": "teacher",
                "name": "教师导入",
                "description": "导入教师教学任务，支持自动创建教师和学期",
                "required_context": [],
                "optional_context": ["auto_create_teachers", "auto_create_semesters", "update_existing"],
            },
        ]
    }
