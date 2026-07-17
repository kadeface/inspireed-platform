"""
Office文档转换服务
将Office文档转换为PDF以便在浏览器中预览

Document preview (Word/PPT/Excel): install LibreOffice (`libreoffice` or `soffice`
on PATH). Without it, Office preview fails; users can still download originals.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import io
import aiofiles
from typing import Optional, Dict, Any
from pathlib import Path
import subprocess
import tempfile

from docx import Document
from pptx import Presentation
import PyPDF2
from PIL import Image
import fitz  # PyMuPDF

from app.core.config import settings
from app.utils.resource_url import url_to_filename

OFFICE_EXTENSIONS = frozenset({"doc", "docx", "ppt", "pptx", "xls", "xlsx"})
DIRECT_PREVIEW_EXTENSIONS = frozenset({
    "pdf", "jpg", "jpeg", "png", "gif", "webp", "svg", "md", "markdown", "txt",
})


def _resources_root() -> Path:
    return Path(settings.UPLOAD_DIR).resolve() / "resources"


def resolve_resource_path(file_ref: str) -> Path | None:
    if not file_ref:
        return None
    if file_ref.startswith(("http://", "https://", "ftp://")):
        return None
    name = url_to_filename(file_ref)
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        return None
    root = _resources_root()
    candidate = (root / name).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


def converted_pdf_path(source: Path) -> Path:
    return source.with_name(f"{source.stem}_converted.pdf")


def delete_converted_pdf(file_ref: str) -> None:
    source = resolve_resource_path(file_ref)
    if source is None:
        return
    pdf_path = converted_pdf_path(source)
    if pdf_path.is_file():
        pdf_path.unlink()


class OfficeConverterService:
    """Office文档转换服务"""

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self._lo_binary: str | None = None
        self._lo_unavailable: bool = False
        self._convert_locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, path: str) -> asyncio.Lock:
        key = str(Path(path).resolve())
        if key not in self._convert_locks:
            self._convert_locks[key] = asyncio.Lock()
        return self._convert_locks[key]

    async def convert_to_pdf(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """
        将Office文档转换为PDF

        Args:
            file_path: 源文件路径
            output_path: 输出PDF路径

        Returns:
            转换结果信息
        """
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".doc":
                return await self._convert_doc_to_pdf(file_path, output_path)
            elif file_ext == ".docx":
                return await self._convert_docx_to_pdf(file_path, output_path)
            elif file_ext in [".ppt", ".pptx"]:
                return await self._convert_ppt_to_pdf(file_path, output_path)
            elif file_ext in [".xls", ".xlsx"]:
                return await self._convert_excel_to_pdf(file_path, output_path)
            else:
                raise ValueError(f"不支持的文档格式: {file_ext}")

        except Exception as e:
            return {"success": False, "error": str(e), "pdf_url": None}

    async def _convert_doc_to_pdf(
        self, doc_path: str, pdf_path: str
    ) -> Dict[str, Any]:
        """将DOC转换为PDF（仅LibreOffice）"""
        try:
            if await self._has_libreoffice():
                return await self._convert_with_libreoffice(doc_path, pdf_path)
            return {
                "success": False,
                "error": "DOC转换需要LibreOffice",
                "pdf_url": None,
            }
        except Exception as e:
            return {"success": False, "error": f"DOC转换失败: {str(e)}", "pdf_url": None}

    async def _convert_docx_to_pdf(
        self, docx_path: str, pdf_path: str
    ) -> Dict[str, Any]:
        """将DOCX转换为PDF（仅 LibreOffice；避免无 LO 时同步内容提取卡死事件循环）"""
        try:
            if await self._has_libreoffice():
                return await self._convert_with_libreoffice(docx_path, pdf_path)
            return {
                "success": False,
                "error": "预览需要安装 LibreOffice（libreoffice/soffice 在 PATH 中）",
                "pdf_url": None,
            }
        except Exception as e:
            return {"success": False, "error": f"DOCX转换失败: {str(e)}", "pdf_url": None}

    async def _convert_ppt_to_pdf(self, ppt_path: str, pdf_path: str) -> Dict[str, Any]:
        """将PPT/PPTX转换为PDF（仅 LibreOffice）"""
        try:
            if await self._has_libreoffice():
                return await self._convert_with_libreoffice(ppt_path, pdf_path)
            return {
                "success": False,
                "error": "预览需要安装 LibreOffice（libreoffice/soffice 在 PATH 中）",
                "pdf_url": None,
            }
        except Exception as e:
            return {"success": False, "error": f"PPT转换失败: {str(e)}", "pdf_url": None}

    async def _convert_excel_to_pdf(
        self, excel_path: str, pdf_path: str
    ) -> Dict[str, Any]:
        """将XLS/XLSX转换为PDF（仅LibreOffice）"""
        try:
            if await self._has_libreoffice():
                return await self._convert_with_libreoffice(excel_path, pdf_path)
            return {
                "success": False,
                "error": "Excel转换需要LibreOffice",
                "pdf_url": None,
            }
        except Exception as e:
            return {"success": False, "error": f"Excel转换失败: {str(e)}", "pdf_url": None}

    async def _has_libreoffice(self) -> bool:
        """检查是否安装了LibreOffice（失败结果会缓存，避免反复探测拖慢请求）"""
        if self._lo_binary:
            return True
        if getattr(self, "_lo_unavailable", False):
            return False

        import shutil

        for binary in ("libreoffice", "soffice"):
            if not shutil.which(binary):
                continue
            try:
                result = await asyncio.to_thread(
                    subprocess.run,
                    [binary, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    self._lo_binary = binary
                    return True
            except Exception:
                continue

        self._lo_unavailable = True
        return False

    async def _convert_with_libreoffice(
        self, input_path: str, output_path: str
    ) -> Dict[str, Any]:
        """使用LibreOffice转换文档"""
        try:
            output_dir = os.path.dirname(output_path) or "."
            os.makedirs(output_dir, exist_ok=True)
            lo_binary = getattr(self, "_lo_binary", None) or "soffice"

            # 独立 UserInstallation，避免并发 soffice 抢同一 profile 导致空成功
            profile_key = hashlib.md5(os.path.abspath(input_path).encode()).hexdigest()[:12]
            profile_dir = os.path.join(self.temp_dir, f"lo_profile_{profile_key}")
            os.makedirs(profile_dir, exist_ok=True)
            profile_uri = Path(profile_dir).resolve().as_uri()

            cmd = [
                lo_binary,
                "--headless",
                f"-env:UserInstallation={profile_uri}",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                input_path,
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=90,
            )

            input_name = Path(input_path).stem
            generated_pdf = os.path.join(output_dir, f"{input_name}.pdf")

            if result.returncode == 0:
                if os.path.exists(generated_pdf) and os.path.abspath(generated_pdf) != os.path.abspath(
                    output_path
                ):
                    os.replace(generated_pdf, output_path)

                if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
                    return {
                        "success": True,
                        "error": None,
                        "pdf_url": output_path,
                        "method": "libreoffice",
                    }

                detail = (result.stderr or result.stdout or "").strip()
                return {
                    "success": False,
                    "error": f"LibreOffice 未生成 PDF 文件{(': ' + detail) if detail else ''}",
                    "pdf_url": None,
                }

            return {
                "success": False,
                "error": f"LibreOffice转换失败: {result.stderr or result.stdout}",
                "pdf_url": None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"LibreOffice转换异常: {str(e)}",
                "pdf_url": None,
            }

    async def _convert_docx_content_to_pdf(
        self, docx_path: str, pdf_path: str
    ) -> Dict[str, Any]:
        """从DOCX提取内容并生成简化PDF"""
        try:
            # 读取DOCX文档
            doc = Document(docx_path)

            # 创建PDF文档
            pdf_doc = fitz.open()

            # 提取段落内容
            y_position = 50
            page_margin = 50
            line_height = 20
            max_width = 500

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # 检查是否需要新页面
                    if y_position > 750:  # 页面底部
                        pdf_doc.new_page()
                        y_position = 50

                    # 处理文本格式
                    text = paragraph.text.strip()

                    # 检查是否是标题（通过样式判断）
                    is_heading = False
                    if paragraph.style.name.startswith("Heading"):
                        is_heading = True
                        font_size = 16
                        font_color = (0, 0, 0)  # 黑色
                    else:
                        font_size = 12
                        font_color = (0, 0, 0)  # 黑色

                    # 添加文本到PDF
                    try:
                        pdf_doc[-1].insert_text(
                            (page_margin, y_position),
                            text,
                            fontsize=font_size,
                            color=font_color,
                        )
                        y_position += line_height + (10 if is_heading else 0)
                    except Exception as text_error:
                        print(f"Error inserting text: {text_error}")
                        # 如果插入失败，尝试简单的文本插入
                        try:
                            pdf_doc[-1].insert_text(
                                (page_margin, y_position), text, fontsize=12
                            )
                            y_position += line_height
                        except:
                            continue

            # 如果没有内容，添加提示信息
            if len(pdf_doc) == 0 or not any(
                page.get_text().strip() for page in pdf_doc
            ):
                page = pdf_doc.new_page()
                page.insert_text((50, 100), "文档内容提取中...", fontsize=14)
                page.insert_text((50, 130), "请使用其他预览方式查看完整内容", fontsize=12)

            # 保存PDF
            pdf_doc.save(pdf_path)
            pdf_doc.close()

            return {
                "success": True,
                "error": None,
                "pdf_url": pdf_path,
                "method": "content_extraction",
            }

        except Exception as e:
            return {"success": False, "error": f"内容提取转换失败: {str(e)}", "pdf_url": None}

    async def _convert_ppt_content_to_pdf(
        self, ppt_path: str, pdf_path: str
    ) -> Dict[str, Any]:
        """从PPT/PPTX提取内容并生成简化PDF"""
        try:
            # 读取PPT文档
            prs = Presentation(ppt_path)

            # 创建PDF文档
            pdf_doc = fitz.open()

            for slide_num, slide in enumerate(prs.slides):
                page = pdf_doc.new_page()

                # 添加幻灯片标题
                page.insert_text(
                    (50, 50), f"幻灯片 {slide_num + 1}", fontsize=16, color=(0, 0, 0)
                )

                # 提取文本框内容
                y_pos = 100
                content_found = False

                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        content_found = True
                        text = shape.text.strip()

                        # 检查文本长度，如果太长则分行
                        if len(text) > 80:
                            # 简单的文本换行
                            words = text.split()
                            lines = []
                            current_line = ""

                            for word in words:
                                if len(current_line + " " + word) <= 80:
                                    current_line += " " + word if current_line else word
                                else:
                                    if current_line:
                                        lines.append(current_line)
                                    current_line = word

                            if current_line:
                                lines.append(current_line)

                            for line in lines:
                                if y_pos > 750:  # 页面底部，创建新页面
                                    page = pdf_doc.new_page()
                                    page.insert_text(
                                        (50, 50),
                                        f"幻灯片 {slide_num + 1} (续)",
                                        fontsize=14,
                                        color=(0, 0, 0),
                                    )
                                    y_pos = 100

                                page.insert_text(
                                    (50, y_pos), line, fontsize=12, color=(0, 0, 0)
                                )
                                y_pos += 25
                        else:
                            if y_pos > 750:  # 页面底部
                                page = pdf_doc.new_page()
                                page.insert_text(
                                    (50, 50),
                                    f"幻灯片 {slide_num + 1} (续)",
                                    fontsize=14,
                                    color=(0, 0, 0),
                                )
                                y_pos = 100

                            page.insert_text(
                                (50, y_pos), text, fontsize=12, color=(0, 0, 0)
                            )
                            y_pos += 25

                # 如果没有找到文本内容，添加提示
                if not content_found:
                    page.insert_text(
                        (50, 100), "此幻灯片无文本内容", fontsize=12, color=(100, 100, 100)
                    )
                    page.insert_text(
                        (50, 130), "可能包含图片或其他媒体内容", fontsize=10, color=(100, 100, 100)
                    )

            # 如果没有幻灯片，添加提示信息
            if len(pdf_doc) == 0:
                page = pdf_doc.new_page()
                page.insert_text((50, 100), "演示文稿内容提取中...", fontsize=14)
                page.insert_text((50, 130), "请使用其他预览方式查看完整内容", fontsize=12)

            # 保存PDF
            pdf_doc.save(pdf_path)
            pdf_doc.close()

            return {
                "success": True,
                "error": None,
                "pdf_url": pdf_path,
                "method": "content_extraction",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"PPT内容提取转换失败: {str(e)}",
                "pdf_url": None,
            }

    async def get_converted_pdf_url(self, original_file_url: str) -> Optional[str]:
        """
        获取Office文档的转换PDF URL

        Args:
            original_file_url: 原始文件URL或文件名

        Returns:
            转换后的PDF URL，如果转换失败则返回None
        """
        try:
            source = resolve_resource_path(original_file_url)
            if source is None:
                return None

            pdf_path = converted_pdf_path(source)
            if pdf_path.is_file() and pdf_path.stat().st_size > 0:
                return f"/uploads/resources/{pdf_path.name}"

            async with self._lock_for(str(source)):
                # 另一请求可能已转换完成
                if pdf_path.is_file() and pdf_path.stat().st_size > 0:
                    return f"/uploads/resources/{pdf_path.name}"

                result = await self.convert_to_pdf(str(source), str(pdf_path))

                if result["success"] and pdf_path.is_file() and pdf_path.stat().st_size > 0:
                    print(f"Office文档转换成功，使用方法: {result.get('method', 'unknown')}")
                    return f"/uploads/resources/{pdf_path.name}"

                print(f"Office文档转换失败: {result.get('error') or '输出文件不存在'}")
                return None

        except Exception as e:
            print(f"获取转换PDF URL失败: {str(e)}")
            return None


# 单例实例
office_converter_service = OfficeConverterService()
