"""
管理员 AI 配置接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models import User
from app.schemas.ai_settings import AISettingsResponse, AISettingsUpdateRequest
from app.services.ai_settings import ai_settings_service

router = APIRouter()


@router.get("", response_model=AISettingsResponse)
@router.get("/", response_model=AISettingsResponse)
async def get_ai_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> AISettingsResponse:
    del current_user
    config = await ai_settings_service.get_runtime_config(db)
    return AISettingsResponse(**ai_settings_service.serialize(config))


@router.put("", response_model=AISettingsResponse)
@router.put("/", response_model=AISettingsResponse)
async def update_ai_settings(
    payload: AISettingsUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> AISettingsResponse:
    config = await ai_settings_service.update_runtime_config(
        db,
        current_user,
        payload=payload.model_dump(),
    )
    return AISettingsResponse(**ai_settings_service.serialize(config))
