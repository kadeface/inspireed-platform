from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.demo_class import (
    DemoClassProvisionResponse,
    DemoClassResetPasswordsResponse,
    DemoClassStatusResponse,
)
from app.services.demo_class import DemoClassService

router = APIRouter()
service = DemoClassService()


@router.get("/status", response_model=DemoClassStatusResponse)
async def demo_class_status(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    data = await service.get_status(db)
    return DemoClassStatusResponse(**data)


@router.post("/provision", response_model=DemoClassProvisionResponse)
async def demo_class_provision(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        data = await service.provision(db)
        await db.commit()
        return DemoClassProvisionResponse(**data)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-passwords", response_model=DemoClassResetPasswordsResponse)
async def demo_class_reset_passwords(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        data = await service.reset_passwords(db)
        await db.commit()
        return DemoClassResetPasswordsResponse(**data)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
