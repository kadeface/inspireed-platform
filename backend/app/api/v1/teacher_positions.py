"""
教师职务类型管理 API

提供教师职务类型的CRUD操作接口
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models import User
from app.schemas.teacher_position import (
    TeacherPositionTypeCreate,
    TeacherPositionTypeUpdate,
    TeacherPositionTypeResponse,
    TeacherPositionTypeListResponse,
)
from app.services.teacher_position_service import (
    TeacherPositionService,
    TeacherPositionServiceError,
)

router = APIRouter(prefix="/teacher-positions", tags=["teacher-positions"])


@router.post("/", response_model=TeacherPositionTypeResponse, status_code=201)
async def create_position_type(
    position_type_in: TeacherPositionTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建教师职务类型"""
    try:
        position_type = await TeacherPositionService.create_position_type(db, position_type_in)
        return position_type
    except TeacherPositionServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建职务类型失败: {str(e)}")


@router.get("/", response_model=TeacherPositionTypeListResponse)
async def list_position_types(
    category: Optional[str] = Query(None, description="职务分类筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    search: Optional[str] = Query(None, description="搜索关键词（名称、代码、描述）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取职务类型列表"""
    try:
        position_types = await TeacherPositionService.list_position_types(
            db=db,
            category=category,
            is_active=is_active,
            search=search,
        )
        return TeacherPositionTypeListResponse(
            position_types=[
                TeacherPositionTypeResponse.model_validate(pt) for pt in position_types
            ],
            total=len(position_types),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取职务类型列表失败: {str(e)}")


@router.get("/{position_type_id}", response_model=TeacherPositionTypeResponse)
async def get_position_type(
    position_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取单个职务类型"""
    position_type = await TeacherPositionService.get_position_type(db, position_type_id)
    if not position_type:
        raise HTTPException(status_code=404, detail=f"职务类型ID {position_type_id} 不存在")
    return position_type


@router.put("/{position_type_id}", response_model=TeacherPositionTypeResponse)
async def update_position_type(
    position_type_id: int,
    position_type_in: TeacherPositionTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新职务类型"""
    try:
        position_type = await TeacherPositionService.update_position_type(
            db, position_type_id, position_type_in
        )
        return position_type
    except TeacherPositionServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新职务类型失败: {str(e)}")


@router.delete("/{position_type_id}")
async def delete_position_type(
    position_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除职务类型"""
    try:
        deleted = await TeacherPositionService.delete_position_type(db, position_type_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"职务类型ID {position_type_id} 不存在")
        return {"message": "职务类型删除成功"}
    except TeacherPositionServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除职务类型失败: {str(e)}")
