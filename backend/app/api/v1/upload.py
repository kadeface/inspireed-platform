"""
通用文件上传 API
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.services.upload import upload_service
from app.utils.resource_url import filename_to_url

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = frozenset({
    "mp4", "webm", "ogg", "mov", "avi", "mkv",
    "jpg", "jpeg", "png", "gif", "webp", "svg",
    "pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx",
    "txt", "md", "zip", "rar",
})


class UploadResponse(BaseModel):
    """文件上传响应"""
    file_url: str
    file_size: int
    filename: str


@router.post("/", response_model=UploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> UploadResponse:
    """上传文件（通用接口）"""
    if not file.filename:
        raise HTTPException(400, "文件名不能为空")

    file_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if file_ext and file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"不支持的文件类型: .{file_ext}。"
            f"支持的类型: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        raise HTTPException(400, f"文件大小超过限制 ({max_mb}MB)")

    try:
        upload_result = await upload_service.upload_file(file)
        file_url = filename_to_url(upload_result["file_url"], request)

        return UploadResponse(
            file_url=file_url,
            file_size=upload_result["file_size"],
            filename=file.filename or "unknown",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("File upload failed for user %s", current_user.id)
        raise HTTPException(500, "文件上传失败")

