"""
文件上传服务
"""

import os
import aiofiles
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from typing import Optional
import PyPDF2
from PIL import Image
import io

from app.core.config import settings


class UploadService:
    """文件上传服务"""

    def __init__(self):
        # 确保上传目录存在
        self.upload_dir = settings.UPLOAD_DIR
        self.resources_dir = os.path.join(self.upload_dir, "resources")
        self.thumbnails_dir = os.path.join(self.upload_dir, "thumbnails")

        os.makedirs(self.resources_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)

    async def upload_pdf(self, file: UploadFile, generate_thumbnail: bool = True) -> dict:
        """
        上传 PDF 文件并提取元数据

        Args:
            file: 上传的文件对象
            generate_thumbnail: 是否生成缩略图

        Returns:
            {
                'file_url': str,
                'file_size': int,
                'page_count': int,
                'thumbnail_url': str (如果生成)
            }
        """
        # 验证文件类型
        if not file.content_type or file.content_type != "application/pdf":
            raise HTTPException(400, "Only PDF files are allowed")

        # 生成唯一文件名
        ext = file.filename.split(".")[-1] if file.filename else "pdf"
        filename = f"{uuid4()}.{ext}"
        filepath = os.path.join(self.resources_dir, filename)

        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 保存文件
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        # 提取 PDF 元数据
        try:
            pdf_meta = self._extract_pdf_metadata(io.BytesIO(content))
        except Exception as e:
            print(f"Failed to extract PDF metadata: {e}")
            pdf_meta = {"page_count": 0}

        # 生成缩略图（可选）
        thumbnail_url = None
        if generate_thumbnail:
            try:
                thumbnail_url = await self._generate_pdf_thumbnail(filepath, filename)
            except Exception as e:
                print(f"Failed to generate thumbnail: {e}")

        # 返回文件信息
        result = {
            "file_url": f"/uploads/resources/{filename}",
            "file_size": file_size,
            "page_count": pdf_meta.get("page_count", 0),
        }

        if thumbnail_url:
            result["thumbnail_url"] = thumbnail_url

        return result

    async def upload_file(self, file: UploadFile) -> dict:
        """
        上传通用文件

        Args:
            file: 上传的文件对象

        Returns:
            {
                'file_url': str,
                'file_size': int
            }
        """
        # 生成唯一文件名
        ext = file.filename.split(".")[-1] if file.filename else "bin"
        filename = f"{uuid4()}.{ext}"
        filepath = os.path.join(self.resources_dir, filename)

        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 保存文件
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        return {"file_url": f"/uploads/resources/{filename}", "file_size": file_size}

    def _extract_pdf_metadata(self, file_stream: io.BytesIO) -> dict:
        """提取 PDF 元数据"""
        try:
            reader = PyPDF2.PdfReader(file_stream)
            metadata = {
                "page_count": len(reader.pages),
            }

            # 尝试获取其他元数据
            if reader.metadata:
                metadata["title"] = reader.metadata.get("/Title", "")
                metadata["author"] = reader.metadata.get("/Author", "")

            return metadata
        except Exception as e:
            print(f"Error extracting PDF metadata: {e}")
            return {"page_count": 0}

    async def _generate_pdf_thumbnail(self, pdf_path: str, original_filename: str) -> Optional[str]:
        """
        生成 PDF 缩略图（第一页）

        注意：这个功能需要 pdf2image 和 poppler-utils
        如果环境不支持，可以跳过缩略图生成
        """
        try:
            import fitz  # PyMuPDF

            # 打开 PDF
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                return None

            # 获取第一页
            page = doc[0]

            # 渲染为图片（缩小尺寸）
            zoom = 0.3  # 缩放因子
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # 生成缩略图文件名
            thumb_filename = f"thumb_{os.path.splitext(original_filename)[0]}.png"
            thumb_path = os.path.join(self.thumbnails_dir, thumb_filename)

            # 保存缩略图
            pix.save(thumb_path)

            doc.close()

            return f"/uploads/thumbnails/{thumb_filename}"
        except ImportError:
            print("PyMuPDF (fitz) not installed, skipping thumbnail generation")
            return None
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None

    async def delete_file(self, file_url: str) -> bool:
        """删除文件"""
        try:
            # 从 URL 提取文件路径
            if file_url.startswith("/uploads/resources/"):
                filename = file_url.replace("/uploads/resources/", "")
                filepath = os.path.join(self.resources_dir, filename)

                if os.path.exists(filepath):
                    os.remove(filepath)
                    return True

            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# 单例实例
upload_service = UploadService()
