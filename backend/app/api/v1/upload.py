"""
通用文件上传 API
用于上传视频、图片等文件到服务器
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from typing import Optional
from pydantic import BaseModel

from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.upload import upload_service
from app.utils.resource_url import filename_to_url

router = APIRouter()


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
    """
    上传文件（通用接口）
    
    支持的文件类型：
    - 视频：mp4, webm, ogg, mov, avi
    - 图片：jpg, jpeg, png, gif, webp
    - 文档：pdf, doc, docx, ppt, pptx
    - 其他：根据需求扩展
    
    返回文件的完整 URL，前端可直接使用
    """
    if not file.filename:
        raise HTTPException(400, "文件名不能为空")
    
    # 验证文件类型（可选，根据需求调整）
    allowed_extensions = {
        # 视频
        'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv',
        # 图片
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
        # 文档
        'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
        # 其他
        'txt', 'md', 'zip', 'rar'
    }
    
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext and file_ext not in allowed_extensions:
        raise HTTPException(
            400, 
            f"不支持的文件类型: .{file_ext}。支持的类型: {', '.join(sorted(allowed_extensions))}"
        )
    
    # 验证文件大小（可选，例如限制为 500MB）
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    # 注意：这里只能检查 Content-Length，实际文件大小需要在上传时检查
    
    try:
        # 使用 upload_service 上传文件（返回文件名）
        upload_result = await upload_service.upload_file(file)
        
        # 将文件名转换为完整URL返回给前端
        file_url = filename_to_url(upload_result["file_url"], request)
        
        return UploadResponse(
            file_url=file_url,  # 返回完整URL
            file_size=upload_result["file_size"],
            filename=file.filename or "unknown"
        )
    except Exception as e:
        raise HTTPException(500, f"文件上传失败: {str(e)}")

