"""
质量监测报告 API

支持 Excel 导入、列表、详情
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_active_user
from app.models import User, MonitoringReport, MonitoringReportSchool, UserRole
from app.schemas.evaluation import (
    MonitoringReportResponse,
    MonitoringReportDetailResponse,
    MonitoringReportSchoolResponse,
)
from app.services.monitoring_report_import_service import (
    parse_and_import,
    MonitoringReportImportError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/import", response_model=MonitoringReportResponse, status_code=status.HTTP_201_CREATED)
async def import_monitoring_report(
    file: UploadFile = File(...),
    report_type: str = Form(..., description="primary=小学, junior_high=初中"),
    name: str = Form(..., description="报告名称"),
    academic_year: str = Form(..., description="学年，如 2025-2026"),
    semester_type: str = Form(..., description="up=上学期, down=下学期"),
    region_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """上传 Excel 并导入质量监测报告"""
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
        UserRole.RESEARCHER,
    ):
        raise HTTPException(status_code=403, detail="无权限导入")

    if report_type not in ("primary", "junior_high"):
        raise HTTPException(status_code=400, detail="report_type 需为 primary 或 junior_high")

    if semester_type not in ("up", "down"):
        raise HTTPException(status_code=400, detail="semester_type 需为 up 或 down")

    fn = file.filename or "upload"
    suffix = Path(fn).suffix or ".xlsx"
    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        report = await parse_and_import(
            db=db,
            file_path=tmp_path,
            report_type=report_type,
            name=name,
            academic_year=academic_year,
            semester_type=semester_type,
            region_id=region_id,
            created_by=current_user.id,
        )
        return report
    except MonitoringReportImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("导入质量监测报告失败")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/", response_model=list[MonitoringReportResponse])
async def list_monitoring_reports(
    academic_year: Optional[str] = Query(None, description="学年"),
    semester_type: Optional[str] = Query(None, description="up/down"),
    report_type: Optional[str] = Query(None, description="primary/junior_high"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取质量监测报告列表，支持按学年、学期、类型筛选"""
    conditions = []
    if academic_year:
        conditions.append(MonitoringReport.academic_year == academic_year)
    if semester_type:
        conditions.append(MonitoringReport.semester_type == semester_type)
    if report_type:
        conditions.append(MonitoringReport.report_type == report_type)

    q = select(MonitoringReport)
    if conditions:
        q = q.where(and_(*conditions))
    q = q.order_by(desc(MonitoringReport.created_at)).offset(skip).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/{report_id}", response_model=MonitoringReportDetailResponse)
async def get_monitoring_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取质量监测报告详情（含学校明细）"""
    result = await db.execute(
        select(MonitoringReport)
        .options(selectinload(MonitoringReport.school_rows))
        .where(MonitoringReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    school_rows = sorted(report.school_rows, key=lambda x: (x.display_order, x.id))
    data = MonitoringReportResponse.model_validate(report).model_dump()
    data["school_rows"] = [MonitoringReportSchoolResponse.model_validate(r) for r in school_rows]
    return MonitoringReportDetailResponse(**data)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitoring_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除质量监测报告"""
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.RESEARCHER,
    ):
        raise HTTPException(status_code=403, detail="无权限删除")

    result = await db.execute(select(MonitoringReport).where(MonitoringReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    await db.delete(report)
    await db.commit()
