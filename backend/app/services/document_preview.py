from __future__ import annotations

from typing import Any, Optional

from app.services.office_converter import (
    DIRECT_PREVIEW_EXTENSIONS,
    OFFICE_EXTENSIONS,
    office_converter_service,
)
from app.utils.resource_url import url_to_filename


def _ext(file_ref: str) -> str:
    name = url_to_filename(file_ref) or ""
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def _public_url(file_ref: str) -> str:
    return f"/uploads/resources/{url_to_filename(file_ref)}"


async def build_preview_payload(
    *,
    file_ref: str,
    title: Optional[str] = None,
    file_size: Optional[int] = None,
    page_count: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    ext = _ext(file_ref)
    public = _public_url(file_ref)
    payload: dict[str, Any] = {
        "title": title,
        "file_url": public,
        "file_type": ext,
        "file_size": file_size,
        "page_count": page_count,
        "can_preview_directly": ext in DIRECT_PREVIEW_EXTENSIONS,
        "preview_url": public,
        "converted_to_pdf": False,
        "conversion_error": None,
    }
    if extra:
        payload.update(extra)

    if ext in OFFICE_EXTENSIONS:
        try:
            converted = await office_converter_service.get_converted_pdf_url(file_ref)
            if converted:
                payload["preview_url"] = converted
                payload["converted_to_pdf"] = True
            else:
                payload["conversion_error"] = "无法转换文档为PDF格式，请下载原文件查看"
        except Exception as e:
            payload["conversion_error"] = f"转换过程中出现错误: {e}"
    elif ext not in DIRECT_PREVIEW_EXTENSIONS:
        payload["conversion_error"] = (
            f"不支持在线预览的文件类型: .{ext}" if ext else "不支持在线预览"
        )

    return payload
