"""
课程导出导入 API
"""

from typing import Any, List, Optional, Dict, Set, cast
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import json
import io
import os
import re
import zipfile
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime

from app.core.database import get_db
from app.models import Subject, Grade, Course, Chapter, Lesson, Resource, User, UserRole
from app.models.lesson import LessonStatus
from app.api.deps import get_current_user, get_current_admin, get_current_researcher

router = APIRouter()


def require_admin_or_researcher(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员或研究员权限"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESEARCHER]:
        raise HTTPException(status_code=403, detail="需要管理员或研究员权限")
    return current_user


def require_teacher_or_admin_or_researcher(current_user: User = Depends(get_current_user)) -> User:
    """要求教师、管理员或研究员权限"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN, UserRole.RESEARCHER]:
        raise HTTPException(status_code=403, detail="需要教师、管理员或研究员权限")
    return current_user


def extract_file_urls_from_content(content: Any) -> Set[str]:
    """从教案内容中提取所有文件URL"""
    file_urls = set()
    
    if not content:
        return file_urls
    
    # 确保content是列表
    if not isinstance(content, list):
        return file_urls
    
    for cell in content:
        if not isinstance(cell, dict):
            continue
            
        cell_type = cell.get("type", "")
        cell_content = cell.get("content", {})
        
        # TextCell: 从HTML中提取图片和文件URL
        if cell_type == "text" and isinstance(cell_content, dict):
            html = cell_content.get("html", "")
            if html:
                # 提取img标签的src
                img_pattern = r'<img[^>]+src\s*=\s*["\']([^"\']+)["\']'
                for match in re.finditer(img_pattern, html, re.IGNORECASE):
                    url = match.group(1)
                    if url and not url.startswith(("data:", "blob:")):
                        # 如果是完整URL（包含http://或https://），提取路径部分
                        if url.startswith(("http://", "https://")):
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(url)
                                if parsed.path:
                                    url = parsed.path
                                else:
                                    continue  # 如果没有路径部分，跳过
                            except:
                                continue  # 解析失败，跳过
                        # 只添加相对路径URL（以/uploads/开头的）
                        if url.startswith("/uploads/"):
                            file_urls.add(url)
                
                # 提取文件附件的URL
                file_pattern = r'data-(?:pdf|file)-url\s*=\s*["\']([^"\']+)["\']'
                for match in re.finditer(file_pattern, html, re.IGNORECASE):
                    url = match.group(1)
                    if url:
                        # 如果是完整URL（包含http://或https://），提取路径部分
                        if url.startswith(("http://", "https://")):
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(url)
                                if parsed.path:
                                    url = parsed.path
                                else:
                                    continue  # 如果没有路径部分，跳过
                            except:
                                continue  # 解析失败，跳过
                        # 只添加相对路径URL（以/uploads/开头的）
                        if url.startswith("/uploads/"):
                            file_urls.add(url)
        
        # VideoCell: 提取视频URL
        elif cell_type == "video" and isinstance(cell_content, dict):
            video_url = cell_content.get("videoUrl") or cell_content.get("video_url")
            if video_url:
                # 提取相对路径部分（如果是完整URL，提取路径）
                if video_url.startswith(("http://", "https://")):
                    # 提取路径部分
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(video_url)
                        if parsed.path:
                            video_url = parsed.path
                    except:
                        pass
                # 如果不是blob URL，添加
                if video_url and not video_url.startswith("blob:"):
                    file_urls.add(video_url)
        
        # ReferenceMaterialCell: 提取资源URL
        elif cell_type == "reference_material" and isinstance(cell_content, dict):
            preview_url = cell_content.get("preview_url")
            download_url = cell_content.get("download_url")
            for url in [preview_url, download_url]:
                if url:
                    # 提取相对路径部分（如果是完整URL，提取路径）
                    if url.startswith(("http://", "https://")):
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            if parsed.path:
                                url = parsed.path
                        except:
                            pass
                    # 添加相对路径URL
                    if url and not url.startswith(("http://", "https://", "blob:")):
                        file_urls.add(url)
        
        # InteractiveCell: 可能包含HTML文件或资源URL
        elif cell_type == "interactive" and isinstance(cell_content, dict):
            html_url = cell_content.get("html_url") or cell_content.get("htmlUrl")
            if html_url:
                # 如果是完整URL，提取路径部分
                if html_url.startswith(("http://", "https://")):
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(html_url)
                        if parsed.path and parsed.path.startswith("/uploads/"):
                            html_url = parsed.path
                        else:
                            html_url = None  # 不是我们的资源URL
                    except:
                        html_url = None  # 解析失败
                # 添加相对路径URL
                if html_url and not html_url.startswith(("blob:", "data:")) and html_url.startswith("/uploads/"):
                    file_urls.add(html_url)
        
        # 通用：检查content中是否有其他URL字段
        if isinstance(cell_content, dict):
            # 查找所有可能的URL字段
            url_fields = ["url", "src", "href", "file_url", "fileUrl", "image_url", "imageUrl", 
                         "thumbnail_url", "thumbnailUrl", "background_url", "backgroundUrl"]
            for field in url_fields:
                url_value = cell_content.get(field)
                if url_value and isinstance(url_value, str):
                    # 提取相对路径部分
                    if url_value.startswith(("http://", "https://")):
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(url_value)
                            if parsed.path:
                                url_value = parsed.path
                        except:
                            pass
                    if url_value and not url_value.startswith(("http://", "https://", "blob:", "data:")):
                        file_urls.add(url_value)
    
    return file_urls


def url_to_file_path(url: str) -> Optional[str]:
    """
    将URL转换为实际文件路径
    
    支持多种URL格式：
    1. 相对路径: /uploads/resources/filename.jpg
    2. 完整URL (域名): http://example.com/uploads/resources/filename.jpg
    3. 完整URL (IP地址): http://192.168.1.100:8000/uploads/resources/filename.jpg
    4. 完整URL (localhost): http://localhost:8000/uploads/resources/filename.jpg
    5. 纯文件名: filename.jpg
    
    最佳实践：数据库中应存储相对路径，这样可以：
    - 避免IP地址变更导致的问题
    - 便于跨环境迁移
    - 前端可以根据当前服务器地址动态构建完整URL
    """
    if not url:
        return None
    
    # 使用配置中的上传目录
    from app.core.config import settings
    base_upload_dir = settings.UPLOAD_DIR  # 通常是 "storage"
    resources_dir = os.path.join(base_upload_dir, "resources")
    
    # 提取文件名（无论URL格式如何）
    filename = None
    url_path = url.strip()
    
    # 方法1: 如果是完整URL（包含协议），提取路径部分
    if "://" in url_path:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url_path)
            # 提取路径部分（如 /uploads/resources/file.jpg）
            url_path = parsed.path if parsed.path else ""
            # 也可以从完整URL中直接提取文件名
            filename = os.path.basename(parsed.path)
        except Exception as e:
            print(f"警告: 解析URL失败 {url}: {str(e)}")
            # 降级处理：手动提取
            if "/" in url_path:
                # 尝试提取路径部分
                parts = url_path.split("://", 1)
                if len(parts) > 1:
                    # 去掉协议和域名/IP部分
                    path_part = parts[1].split("/", 3)  # 分割：['', 'domain:port', 'uploads', 'resources/...']
                    if len(path_part) >= 4:
                        url_path = "/" + "/".join(path_part[2:])  # 保留 /uploads/resources/...
                    elif len(path_part) >= 3:
                        url_path = "/" + path_part[2]
    
    # 方法2: 如果路径以 /uploads/resources/ 开头，提取文件名
    if not filename and url_path.startswith("/uploads/resources/"):
        filename = url_path.replace("/uploads/resources/", "").strip()
        # 移除可能的查询参数或锚点
        if "?" in filename:
            filename = filename.split("?")[0]
        if "#" in filename:
            filename = filename.split("#")[0]
    
    # 方法3: 如果路径包含 /resources/ 或 /uploads/，提取文件名
    elif not filename and ("/resources/" in url_path or "/uploads/" in url_path):
        filename = url_path.split("/")[-1].strip()
        # 移除可能的查询参数或锚点
        if "?" in filename:
            filename = filename.split("?")[0]
        if "#" in filename:
            filename = filename.split("#")[0]
    
    # 方法4: 如果路径中没有斜杠，可能就是文件名
    elif not filename and "/" not in url_path and "." in url_path:
        filename = url_path
        # 移除可能的查询参数或锚点
        if "?" in filename:
            filename = filename.split("?")[0]
        if "#" in filename:
            filename = filename.split("#")[0]
    
    # 如果仍然没有提取到文件名，尝试直接从URL末尾提取
    if not filename:
        # 尝试提取最后一个路径段作为文件名
        parts = url_path.strip("/").split("/")
        if parts:
            potential_filename = parts[-1]
            if "." in potential_filename:  # 包含扩展名，可能是文件名
                filename = potential_filename
                # 移除可能的查询参数或锚点
                if "?" in filename:
                    filename = filename.split("?")[0]
                if "#" in filename:
                    filename = filename.split("#")[0]
    
    if not filename:
        print(f"警告: 无法从URL提取文件名: {url}")
        return None
    
    # 尝试多个可能的存储路径
    possible_paths = [
        os.path.join(resources_dir, filename),
        os.path.join("storage", "resources", filename),
        os.path.join("backend", "storage", "resources", filename),
        os.path.join(os.getcwd(), "storage", "resources", filename),
        os.path.join(os.getcwd(), "backend", "storage", "resources", filename),
        os.path.abspath(os.path.join(resources_dir, filename)),
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
    
    # 如果都没找到，记录调试信息
    print(f"调试: 无法找到文件 - 原始URL: {url}, 提取的文件名: {filename}, 尝试的路径: {possible_paths}")
    return None


async def _process_zip_import(zip_content: bytes, current_user: User) -> tuple[Dict, Dict[str, str]]:
    """
    处理ZIP文件导入
    返回: (导入数据字典, URL映射字典)
    """
    from app.services.upload import upload_service
    from fastapi import UploadFile
    
    url_mapping = {}
    import_data = None
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 解压ZIP文件
        zip_path = os.path.join(temp_dir, "import.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_content)
        
        try:
            zip_file = zipfile.ZipFile(zip_path, 'r')
        except zipfile.BadZipFile as e:
            raise HTTPException(400, f"ZIP文件格式错误或已损坏: {str(e)}")
        except Exception as e:
            raise HTTPException(400, f"无法打开ZIP文件: {str(e)}")
        
        with zip_file:
            # 读取JSON数据
            try:
                file_list = zip_file.namelist()
            except Exception as e:
                raise HTTPException(400, f"无法读取ZIP文件列表: {str(e)}")
            
            if file_list is None:
                raise HTTPException(400, "ZIP文件损坏或格式不正确")
            
            if "data.json" not in file_list:
                available_files = ", ".join(file_list[:10])  # 显示前10个文件名
                if len(file_list) > 10:
                    available_files += f" ... (共 {len(file_list)} 个文件)"
                raise HTTPException(400, f"ZIP文件中缺少data.json。可用文件: {available_files}")
            
            json_content = zip_file.read("data.json")
            
            # 根据导出函数的实现，data.json 使用 UTF-8 编码
            # 优先尝试 UTF-8，如果失败再尝试其他编码
            import_data = None
            last_decode_error = None
            last_json_error = None
            
            # 优先使用 UTF-8（导出时使用的编码）
            try:
                decoded_content = json_content.decode('utf-8')
                import_data = json.loads(decoded_content)
            except UnicodeDecodeError as e:
                last_decode_error = f"UTF-8解码失败: {str(e)}"
                # 如果 UTF-8 失败，尝试其他编码
                encodings = ['utf-8-sig', 'gbk', 'gb2312', 'gb18030']
                for encoding in encodings:
                    try:
                        decoded_content = json_content.decode(encoding)
                        try:
                            import_data = json.loads(decoded_content)
                            break  # 成功解析，跳出循环
                        except json.JSONDecodeError as e:
                            last_json_error = f"编码 {encoding}: JSON解析失败 - {str(e)}"
                            continue
                    except UnicodeDecodeError as e:
                        continue  # 尝试下一个编码
            except json.JSONDecodeError as e:
                last_json_error = f"UTF-8编码JSON解析失败: {str(e)}"
                # 显示错误位置附近的内容
                try:
                    decoded_content = json_content.decode('utf-8', errors='replace')
                    if hasattr(e, 'pos') and e.pos is not None:
                        start = max(0, e.pos - 100)
                        end = min(len(decoded_content), e.pos + 100)
                        context = decoded_content[start:end].replace('\n', '\\n').replace('\r', '\\r')
                        last_json_error += f" (位置 {e.pos} 附近: ...{context}...)"
                except:
                    pass
            
            if import_data is None:
                error_msg = "无法解析ZIP文件中的data.json。"
                if last_json_error:
                    error_msg += f" {last_json_error}"
                elif last_decode_error:
                    error_msg += f" {last_decode_error}"
                else:
                    error_msg += " 请确保文件是有效的JSON格式。"
                raise HTTPException(400, error_msg)
            
            # 处理资源文件
            resources_dir = os.path.join(temp_dir, "resources")
            os.makedirs(resources_dir, exist_ok=True)
            
            # 提取所有资源文件
            for file_info in zip_file.filelist:
                if file_info.filename.startswith("resources/") and not file_info.is_dir():
                    # 提取文件
                    zip_file.extract(file_info.filename, temp_dir)
                    file_path = os.path.join(temp_dir, file_info.filename)
                    
                    # 上传文件到服务器
                    original_filename = os.path.basename(file_info.filename)
                    
                    # 读取文件内容
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    
                    # 创建UploadFile对象（使用BytesIO）
                    from io import BytesIO
                    file_stream = BytesIO(file_content)
                    upload_file = UploadFile(
                        filename=original_filename,
                        file=file_stream
                    )
                    
                    # 上传文件
                    try:
                        upload_result = await upload_service.upload_file(upload_file)
                        
                        # 检查上传结果
                        if not upload_result or "file_url" not in upload_result:
                            print(f"警告: 文件 {original_filename} 上传失败或返回格式不正确")
                            continue
                        
                            # 记录URL映射 - 记录多种可能的URL格式
                        old_url = f"/uploads/resources/{original_filename}"
                        new_url = upload_result["file_url"]
                        
                        # 映射各种可能的URL格式（包括完整路径和文件名）
                        url_mapping[old_url] = new_url
                        url_mapping[original_filename] = new_url
                        url_mapping[f"resources/{original_filename}"] = new_url
                        url_mapping[f"/resources/{original_filename}"] = new_url
                        # 处理可能包含服务器地址的完整URL
                        # 提取URL路径部分进行匹配（忽略服务器地址）
                        if "/" in new_url:
                            new_url_path = "/" + "/".join(new_url.split("/")[3:])  # 移除协议和域名部分
                            if new_url_path != old_url:
                                url_mapping[new_url_path] = new_url
                        
                    except Exception as e:
                        print(f"警告: 上传文件 {original_filename} 时出错: {str(e)}")
                        continue
        
        # 确保 import_data 不为 None
        if import_data is None:
            raise HTTPException(400, "ZIP文件处理失败：无法解析data.json")
    
    return import_data, url_mapping


def _update_urls_in_data(data: Dict, url_mapping: Dict[str, str]) -> Dict:
    """
    更新数据中的URL引用
    """
    if data is None:
        raise ValueError("data 不能为 None")
    if url_mapping is None:
        url_mapping = {}
    
    import copy
    data = copy.deepcopy(data)
    
    def update_urls_in_content(content: Any) -> Any:
        """递归更新内容中的URL"""
        if isinstance(content, dict):
            # 更新字典中的URL字段
            for key, value in content.items():
                if key in ["file_url", "thumbnail_url", "cover_image_url", "videoUrl", "video_url", 
                          "preview_url", "download_url"] and isinstance(value, str):
                    # 尝试匹配URL - 改进匹配逻辑
                    updated = False
                    for old_url, new_url in url_mapping.items():
                        # 提取文件名用于匹配
                        old_filename = old_url.split("/")[-1] if "/" in old_url else old_url
                        value_filename = value.split("/")[-1] if "/" in value else value
                        
                        # 完整URL匹配
                        if old_url == value or value == old_url:
                            content[key] = new_url
                            updated = True
                            break
                        # 文件名匹配
                        elif old_filename and value_filename and old_filename == value_filename:
                            content[key] = new_url
                            updated = True
                            break
                        # 部分匹配（旧URL包含在新URL中，或相反）
                        elif old_url in value or value in old_url:
                            # 提取完整路径部分进行更精确匹配
                            if "/" in old_url and "/" in value:
                                old_path = old_url.split("/")[-1]  # 只取文件名部分
                                if old_path in value:
                                    content[key] = new_url
                                    updated = True
                                    break
                    # 如果还没有更新，尝试通过文件名匹配
                    if not updated and value:
                        value_filename = value.split("/")[-1] if "/" in value else value
                        for old_url, new_url in url_mapping.items():
                            old_filename = old_url.split("/")[-1] if "/" in old_url else old_url
                            if old_filename == value_filename:
                                content[key] = new_url
                                break
                elif key == "html" and isinstance(value, str):
                    # 更新HTML中的URL
                    html = value
                    for old_url, new_url in url_mapping.items():
                        # 替换各种可能的URL格式
                        html = html.replace(old_url, new_url)
                        filename = old_url.split("/")[-1]
                        if filename in html:
                            html = html.replace(f"/uploads/resources/{filename}", new_url)
                            html = html.replace(f'"/uploads/resources/{filename}"', f'"{new_url}"')
                            html = html.replace(f"'/uploads/resources/{filename}'", f"'{new_url}'")
                    content[key] = html
                else:
                    content[key] = update_urls_in_content(value)
            return content
        elif isinstance(content, list):
            return [update_urls_in_content(item) for item in content]
        else:
            return content
    
    # 更新教案内容
    for lesson in data.get("lessons", []):
        lesson["content"] = update_urls_in_content(lesson.get("content", []))
        if "cover_image_url" in lesson and lesson["cover_image_url"]:
            cover_image_url = lesson["cover_image_url"]
            if isinstance(cover_image_url, str):
                for old_url, new_url in url_mapping.items():
                    if old_url in cover_image_url:
                        lesson["cover_image_url"] = new_url
                        break
    
    # 更新资源URL
    for resource in data.get("resources", []):
        for key in ["file_url", "thumbnail_url"]:
            if key in resource and resource[key]:
                resource_url = resource[key]
                if isinstance(resource_url, str):
                    for old_url, new_url in url_mapping.items():
                        if old_url in resource_url:
                            resource[key] = new_url
                            break
    
    return data


def collect_all_files(export_data: Dict, lesson_data_list: List[Dict], resource_data_list: List[Dict]) -> Dict[str, str]:
    """
    收集所有需要导出的文件
    返回: {文件在ZIP中的路径: 实际文件路径}
    """
    files_map = {}
    
    # 从教案内容中提取文件
    for lesson_data in lesson_data_list:
        try:
            content = lesson_data.get("content", [])
            if content is None:
                content = []
            file_urls = extract_file_urls_from_content(content)
            
            # 封面图
            cover_image_url = lesson_data.get("cover_image_url")
            if cover_image_url:
                file_urls.add(cover_image_url)
            
            # 转换URL为文件路径
            for url in file_urls:
                if url:
                    file_path = url_to_file_path(url)
                    if file_path and os.path.exists(file_path):
                        # 在ZIP中使用相对路径
                        zip_path = f"resources/{os.path.basename(file_path)}"
                        # 如果已经有同名文件但路径不同，使用文件名+部分哈希避免冲突
                        if zip_path in files_map and files_map[zip_path] != file_path:
                            # 文件名冲突，添加路径信息
                            filename_base = os.path.splitext(os.path.basename(file_path))[0]
                            filename_ext = os.path.splitext(os.path.basename(file_path))[1]
                            path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
                            zip_path = f"resources/{filename_base}_{path_hash}{filename_ext}"
                        files_map[zip_path] = file_path
                        print(f"调试: 成功添加文件到导出列表 - URL: {url}, 路径: {file_path}, ZIP路径: {zip_path}")
                    else:
                        # 记录无法找到的文件（用于调试）
                        print(f"警告: 无法找到文件对应的路径 - URL: {url}, 提取到的路径: {file_path}")
            print(f"调试: 从教案 '{lesson_data.get('title', '未知')}' 中提取了 {len(file_urls)} 个文件URL")
        except Exception as e:
            # 如果处理某个教案时出错，记录错误但继续处理其他教案
            import traceback
            print(f"警告: 处理教案文件时出错: {str(e)}\n{traceback.format_exc()}")
            continue
    
    # 从资源数据中提取文件
    for resource_data in resource_data_list:
        file_url = resource_data.get("file_url")
        thumbnail_url = resource_data.get("thumbnail_url")
        
        for url in [file_url, thumbnail_url]:
            if url:
                file_path = url_to_file_path(url)
                if file_path and os.path.exists(file_path):
                    zip_path = f"resources/{os.path.basename(file_path)}"
                    # 如果已经有同名文件但路径不同，使用文件名+部分哈希避免冲突
                    if zip_path in files_map and files_map[zip_path] != file_path:
                        # 文件名冲突，添加路径信息
                        filename_base = os.path.splitext(os.path.basename(file_path))[0]
                        filename_ext = os.path.splitext(os.path.basename(file_path))[1]
                        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
                        zip_path = f"resources/{filename_base}_{path_hash}{filename_ext}"
                    files_map[zip_path] = file_path
                    print(f"调试: 成功添加资源文件到导出列表 - URL: {url}, 路径: {file_path}, ZIP路径: {zip_path}")
                else:
                    # 记录无法找到的文件（用于调试）
                    print(f"警告: 无法找到资源文件对应的路径 - URL: {url}, 提取到的路径: {file_path}")
    
    print(f"调试: 总共收集到 {len(files_map)} 个文件需要导出")
    return files_map


@router.get("/export-template")
async def get_export_template():
    """获取课程导出模板"""

    template_data = {
        "version": "1.0",
        "export_time": datetime.utcnow().isoformat(),
        "description": "课程导出模板 - 包含完整的课程体系数据",
        "data": {
            "subjects": [
                {
                    "name": "数学",
                    "code": "math",
                    "description": "数学学科",
                    "is_active": True,
                    "display_order": 1,
                }
            ],
            "grades": [{"name": "一年级", "level": 1, "is_active": True}],
            "courses": [
                {
                    "subject_code": "math",
                    "grade_level": 1,
                    "name": "一年级数学",
                    "code": "grade1-math",
                    "description": "一年级数学课程",
                    "is_active": True,
                    "display_order": 1,
                }
            ],
            "chapters": [
                {
                    "course_code": "grade1-math",
                    "name": "第一章：数的认识",
                    "code": "chapter-1",
                    "description": "学习数的基本概念",
                    "display_order": 1,
                    "parent_code": None,
                    "is_active": True,
                }
            ],
            "lessons": [
                {
                    "course_code": "grade1-math",
                    "chapter_code": "chapter-1",
                    "title": "数的认识教案",
                    "description": "学习1-10的数字",
                    "status": "published",
                    "content": [],
                    "tags": ["基础", "数字"],
                    "difficulty_level": "beginner",
                    "estimated_duration": 40,
                }
            ],
            "resources": [
                {
                    "chapter_code": "chapter-1",
                    "title": "数字卡片",
                    "description": "1-10的数字卡片",
                    "resource_type": "pdf",
                    "file_url": "https://example.com/numbers.pdf",
                    "is_official": True,
                    "is_downloadable": True,
                    "display_order": 1,
                }
            ],
        },
    }

    # 转换为JSON字符串
    json_str = json.dumps(template_data, ensure_ascii=False, indent=2)

    # 创建字节流
    output = io.BytesIO()
    output.write(json_str.encode("utf-8"))
    output.seek(0)

    # 返回文件下载
    import urllib.parse

    filename = urllib.parse.quote("课程导出模板.json")
    return StreamingResponse(
        output,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/courses/{course_id}/export")
async def export_course(
    course_id: int,
    include_lessons: bool = True,
    include_resources: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_researcher),
):
    """导出单个课程的完整数据"""

    # 获取课程及其关联数据
    course_result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.subject),
            selectinload(Course.grade),
            selectinload(Course.chapters).selectinload(Chapter.resources),
            selectinload(Course.lessons),
        )
        .where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(404, "课程不存在")

    # 构建导出数据
    export_data = {
        "version": "1.0",
        "export_time": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "description": f"课程导出：{course.name}",
        "data": {
            "subjects": [
                {
                    "name": course.subject.name,
                    "code": course.subject.code,
                    "description": course.subject.description,
                    "is_active": course.subject.is_active,
                    "display_order": course.subject.display_order,
                }
            ],
            "grades": [
                {
                    "name": course.grade.name,
                    "level": course.grade.level,
                    "is_active": course.grade.is_active,
                }
            ],
            "courses": [
                {
                    "subject_code": course.subject.code,
                    "grade_level": course.grade.level,
                    "name": course.name,
                    "code": course.code,
                    "description": course.description,
                    "is_active": course.is_active,
                    "display_order": course.display_order,
                }
            ],
            "chapters": [],
            "lessons": [],
            "resources": [],
        },
    }

    # 处理章节数据
    chapter_code_map = {}
    for chapter in course.chapters:
        chapter_data = {
            "course_code": course.code,
            "name": chapter.name,
            "code": chapter.code,
            "description": chapter.description,
            "display_order": chapter.display_order,
            "parent_code": None,
            "is_active": chapter.is_active,
        }

        # 处理父章节关系
        if chapter.parent_id:
            # 查找父章节的code
            parent_chapter = next(
                (c for c in course.chapters if c.id == chapter.parent_id), None
            )
            if parent_chapter:
                chapter_data["parent_code"] = parent_chapter.code

        export_data["data"]["chapters"].append(chapter_data)
        chapter_code_map[chapter.id] = chapter.code

        # 处理资源数据
        if include_resources:
            for resource in chapter.resources:
                resource_data = {
                    "chapter_code": chapter.code,
                    "title": resource.title,
                    "description": resource.description,
                    "resource_type": resource.resource_type,
                    "file_url": resource.file_url,
                    "file_size": resource.file_size,
                    "page_count": resource.page_count,
                    "thumbnail_url": resource.thumbnail_url,
                    "is_official": resource.is_official,
                    "is_downloadable": resource.is_downloadable,
                    "is_active": resource.is_active,
                    "display_order": resource.display_order,
                }
                export_data["data"]["resources"].append(resource_data)

    # 处理教案数据
    if include_lessons:
        for lesson in course.lessons:
            lesson_data = {
                "course_code": course.code,
                "chapter_code": (
                    chapter_code_map.get(lesson.chapter_id)
                    if lesson.chapter_id
                    else None
                ),
                "title": lesson.title,
                "description": lesson.description,
                "status": lesson.status.value,
                "content": lesson.content,
                "tags": lesson.tags,
                "cover_image_url": lesson.cover_image_url,
                "difficulty_level": (
                    lesson.difficulty_level.value if lesson.difficulty_level else None
                ),
                "estimated_duration": lesson.estimated_duration,
                "reference_notes": lesson.reference_notes,
            }
            export_data["data"]["lessons"].append(lesson_data)

    # 收集所有需要导出的文件
    lesson_data_list = export_data["data"].get("lessons", [])
    resource_data_list = export_data["data"].get("resources", [])
    files_map = collect_all_files(export_data, lesson_data_list, resource_data_list)
    
    # 创建ZIP文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
        zip_file.writestr("data.json", json_str.encode("utf-8"))
        
        # 添加所有资源文件
        for zip_path, file_path in files_map.items():
            try:
                zip_file.write(file_path, zip_path)
            except Exception as e:
                # 如果文件不存在或无法读取，记录错误但继续
                print(f"警告: 无法添加文件 {file_path}: {str(e)}")
        
        # 创建文件清单
        manifest = {
            "version": "1.0",
            "export_time": datetime.utcnow().isoformat(),
            "files": list(files_map.keys()),
            "file_count": len(files_map)
        }
        zip_file.writestr("manifest.json", json.dumps(manifest, indent=2).encode("utf-8"))
    
    zip_buffer.seek(0)
    
    # 返回ZIP文件下载
    import urllib.parse
    filename = urllib.parse.quote(f"{course.name}_导出.zip")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/export-all")
async def export_all_courses(
    include_lessons: bool = True,
    include_resources: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_researcher),
):
    """导出所有课程的完整数据"""

    # 获取所有课程及其关联数据
    courses_result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.subject),
            selectinload(Course.grade),
            selectinload(Course.chapters).selectinload(Chapter.resources),
            selectinload(Course.lessons),
        )
        .where(Course.is_active == True)
        .order_by(Course.subject_id, Course.grade_id)
    )
    courses = courses_result.scalars().all()

    if not courses:
        raise HTTPException(404, "没有找到任何课程")

    # 构建导出数据
    export_data = {
        "version": "1.0",
        "export_time": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "description": "完整课程体系导出",
        "data": {
            "subjects": [],
            "grades": [],
            "courses": [],
            "chapters": [],
            "lessons": [],
            "resources": [],
        },
    }

    # 收集所有学科和年级
    subjects_dict = {}
    grades_dict = {}

    for course in courses:
        # 收集学科
        if course.subject.id not in subjects_dict:
            subjects_dict[course.subject.id] = {
                "name": course.subject.name,
                "code": course.subject.code,
                "description": course.subject.description,
                "is_active": course.subject.is_active,
                "display_order": course.subject.display_order,
            }

        # 收集年级
        if course.grade.id not in grades_dict:
            grades_dict[course.grade.id] = {
                "name": course.grade.name,
                "level": course.grade.level,
                "is_active": course.grade.is_active,
            }

        # 添加课程数据
        course_data = {
            "subject_code": course.subject.code,
            "grade_level": course.grade.level,
            "name": course.name,
            "code": course.code,
            "description": course.description,
            "is_active": course.is_active,
            "display_order": course.display_order,
        }
        export_data["data"]["courses"].append(course_data)

        # 处理章节数据
        chapter_code_map = {}
        for chapter in course.chapters:
            chapter_data = {
                "course_code": course.code,
                "name": chapter.name,
                "code": chapter.code,
                "description": chapter.description,
                "display_order": chapter.display_order,
                "parent_code": None,
                "is_active": chapter.is_active,
            }

            # 处理父章节关系
            if chapter.parent_id:
                parent_chapter = next(
                    (c for c in course.chapters if c.id == chapter.parent_id), None
                )
                if parent_chapter:
                    chapter_data["parent_code"] = parent_chapter.code

            export_data["data"]["chapters"].append(chapter_data)
            chapter_code_map[chapter.id] = chapter.code

            # 处理资源数据
            if include_resources:
                for resource in chapter.resources:
                    resource_data = {
                        "chapter_code": chapter.code,
                        "title": resource.title,
                        "description": resource.description,
                        "resource_type": resource.resource_type,
                        "file_url": resource.file_url,
                        "file_size": resource.file_size,
                        "page_count": resource.page_count,
                        "thumbnail_url": resource.thumbnail_url,
                        "is_official": resource.is_official,
                        "is_downloadable": resource.is_downloadable,
                        "is_active": resource.is_active,
                        "display_order": resource.display_order,
                    }
                    export_data["data"]["resources"].append(resource_data)

        # 处理教案数据
        if include_lessons:
            for lesson in course.lessons:
                lesson_data = {
                    "course_code": course.code,
                    "chapter_code": (
                        chapter_code_map.get(lesson.chapter_id)
                        if lesson.chapter_id
                        else None
                    ),
                    "title": lesson.title,
                    "description": lesson.description,
                    "status": lesson.status.value,
                    "content": lesson.content,
                    "tags": lesson.tags,
                    "cover_image_url": lesson.cover_image_url,
                    "difficulty_level": (
                        lesson.difficulty_level.value
                        if lesson.difficulty_level
                        else None
                    ),
                    "estimated_duration": lesson.estimated_duration,
                    "reference_notes": lesson.reference_notes,
                }
                export_data["data"]["lessons"].append(lesson_data)

    # 添加学科和年级数据
    export_data["data"]["subjects"] = list(subjects_dict.values())
    export_data["data"]["grades"] = list(grades_dict.values())

    # 收集所有需要导出的文件
    lesson_data_list = export_data["data"].get("lessons", [])
    resource_data_list = export_data["data"].get("resources", [])
    files_map = collect_all_files(export_data, lesson_data_list, resource_data_list)
    
    # 创建ZIP文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 添加JSON数据
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
        zip_file.writestr("data.json", json_str.encode("utf-8"))
        
        # 添加所有资源文件
        for zip_path, file_path in files_map.items():
            try:
                zip_file.write(file_path, zip_path)
            except Exception as e:
                # 如果文件不存在或无法读取，记录错误但继续
                print(f"警告: 无法添加文件 {file_path}: {str(e)}")
        
        # 创建文件清单
        manifest = {
            "version": "1.0",
            "export_time": datetime.utcnow().isoformat(),
            "files": list(files_map.keys()),
            "file_count": len(files_map)
        }
        zip_file.writestr("manifest.json", json.dumps(manifest, indent=2).encode("utf-8"))
    
    zip_buffer.seek(0)
    
    # 返回ZIP文件下载
    import urllib.parse
    filename = urllib.parse.quote(
        f"完整课程体系导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    )
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.post("/import")
async def import_courses(
    file: UploadFile = File(...),
    overwrite_existing: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_researcher),
):
    """导入课程数据（支持ZIP和JSON格式）"""

    # 验证文件类型
    if not file.filename:
        raise HTTPException(400, "文件名不能为空")
    
    # 先读取文件内容以检测实际格式
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(400, "上传的文件为空")
    
    # 通过文件头（魔数）检测实际文件格式
    # ZIP 文件签名: PK\x03\x04 或 PK\x05\x06 (空ZIP) 或 PK\x07\x08
    is_zip_by_content = (
        len(content) >= 4 and 
        content[:2] == b'PK' and 
        content[2:4] in [b'\x03\x04', b'\x05\x06', b'\x07\x08', b'\x50\x4b']
    )
    
    # JSON 文件通常以 { 或 [ 开头（去除BOM后）
    is_json_by_content = False
    if len(content) > 0:
        # 尝试检测 UTF-8 BOM
        if content.startswith(b'\xef\xbb\xbf'):
            content_start = content[3:].lstrip()
        else:
            content_start = content.lstrip()
        
        # 检查是否以 JSON 字符开头
        try:
            first_char = content_start[0:1]
            is_json_by_content = first_char in [b'{', b'[']
        except (IndexError, TypeError):
            pass
    
    # 根据扩展名和实际内容判断文件类型
    is_zip_by_ext = file.filename.lower().endswith(".zip")
    is_json_by_ext = file.filename.lower().endswith(".json")
    
    # 如果扩展名和实际内容不匹配，给出警告并使用实际内容类型
    if is_zip_by_ext and not is_zip_by_content and is_json_by_content:
        # 扩展名是 .zip 但内容是 JSON
        is_zip = False
        is_json = True
    elif is_json_by_ext and not is_json_by_content and is_zip_by_content:
        # 扩展名是 .json 但内容是 ZIP（这是当前的情况）
        is_zip = True
        is_json = False
    else:
        # 使用扩展名判断，但优先使用实际内容
        if is_zip_by_content:
            is_zip = True
            is_json = False
        elif is_json_by_content:
            is_zip = False
            is_json = True
        else:
            # 使用扩展名
            is_zip = is_zip_by_ext
            is_json = is_json_by_ext
    
    if not (is_zip or is_json):
        raise HTTPException(400, "文件必须是ZIP或JSON格式。检测到文件扩展名: " + file.filename)

    try:

        # URL映射：旧URL -> 新URL（用于更新导入后的文件引用）
        url_mapping = {}
        
        # 如果是ZIP文件，解压并处理文件
        if is_zip:
            import_data, url_mapping = await _process_zip_import(content, current_user)
        else:
            # JSON文件，尝试多种编码格式解析
            # 注意：latin-1 可以解码任何字节，但可能产生乱码，所以放在最后
            import_data = None
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'latin-1']
            last_decode_error = None
            last_json_error = None
            successful_decodings = []  # 记录成功解码但JSON解析失败的编码
            decoded_preview = None  # 记录解码后的内容预览
            
            for encoding in encodings:
                try:
                    decoded_content = content.decode(encoding)
                    # 检查解码后的内容是否看起来像JSON（以 { 或 [ 开头）
                    stripped_content = decoded_content.strip()
                    
                    # 对于 latin-1，额外检查是否包含乱码字符（如果包含大量非ASCII且不是中文，可能是乱码）
                    if encoding == 'latin-1':
                        # 检查是否包含中文字符或常见的JSON字符
                        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in decoded_content[:500])
                        has_json_chars = '{' in decoded_content[:100] or '[' in decoded_content[:100]
                        # 如果既没有中文也没有JSON字符，可能是乱码
                        if not has_chinese and not has_json_chars:
                            continue
                    
                    if not (stripped_content.startswith('{') or stripped_content.startswith('[')):
                        # 解码成功但内容不像JSON，记录并继续
                        successful_decodings.append(encoding)
                        if not decoded_preview:
                            decoded_preview = decoded_content[:200]  # 保存前200个字符用于调试
                        continue
                    
                    try:
                        import_data = json.loads(decoded_content)
                        break  # 成功解析，跳出循环
                    except json.JSONDecodeError as e:
                        last_json_error = f"编码 {encoding}: JSON解析失败 - {str(e)}"
                        if hasattr(e, 'pos') and e.pos is not None:
                            # 显示错误位置附近的内容
                            start = max(0, e.pos - 50)
                            end = min(len(decoded_content), e.pos + 50)
                            context = decoded_content[start:end].replace('\n', '\\n').replace('\r', '\\r')
                            last_json_error += f" (位置 {e.pos} 附近: ...{context}...)"
                        successful_decodings.append(encoding)
                        if not decoded_preview:
                            decoded_preview = decoded_content[:200]  # 保存前200个字符用于调试
                        continue
                except UnicodeDecodeError as e:
                    last_decode_error = f"编码 {encoding}: 解码失败 - {str(e)}"
                    continue  # 尝试下一个编码
            
            if import_data is None:
                # 构建详细的错误信息
                error_msg = "无法解析JSON文件。"
                
                if successful_decodings:
                    # 过滤掉 latin-1，因为它可能产生乱码
                    valid_encodings = [e for e in successful_decodings if e != 'latin-1']
                    if valid_encodings:
                        error_msg += f" 文件可以解码为: {', '.join(valid_encodings)}，但JSON格式无效。"
                    elif 'latin-1' in successful_decodings:
                        error_msg += " 文件可能使用了非标准编码，解码后内容可能不正确。"
                    
                    if last_json_error:
                        error_msg += f" {last_json_error}"
                    
                    # 显示解码后的内容预览（如果有）
                    if decoded_preview:
                        preview = decoded_preview.replace('\n', '\\n').replace('\r', '\\r')
                        if len(preview) > 100:
                            preview = preview[:100] + "..."
                        error_msg += f" 文件开头内容: {preview}"
                elif last_decode_error:
                    error_msg += f" 无法解码文件内容。最后尝试: {last_decode_error}"
                else:
                    error_msg += " 请确保文件是有效的JSON格式且使用UTF-8或GBK编码。"
                
                raise HTTPException(400, error_msg)

        # 验证数据格式
        if import_data is None:
            raise HTTPException(400, "导入数据为空，请检查文件格式")
        
        if not isinstance(import_data, dict):
            raise HTTPException(400, f"无效的导入文件格式：期望字典类型，实际为 {type(import_data).__name__}")
        
        # 确保 import_data 是字典类型后再检查 "data" 字段
        if not isinstance(import_data, dict) or "data" not in import_data:
            raise HTTPException(400, "无效的导入文件格式：缺少 'data' 字段")

        data = import_data.get("data")
        
        # 验证 data 字段
        if data is None:
            raise HTTPException(400, "无效的导入文件格式：'data' 字段为空")
        
        if not isinstance(data, dict):
            raise HTTPException(400, f"无效的导入文件格式：'data' 字段必须是字典类型，实际为 {type(data).__name__}")
        
        # 更新URL引用（如果有文件映射）
        if url_mapping:
            data = _update_urls_in_data(data, url_mapping)

        # 导入结果统计
        import_result = {
            "subjects": {"created": 0, "skipped": 0},
            "grades": {"created": 0, "skipped": 0},
            "courses": {"created": 0, "skipped": 0},
            "chapters": {"created": 0, "skipped": 0},
            "lessons": {"created": 0, "skipped": 0},
            "resources": {"created": 0, "skipped": 0},
            "errors": [],
            "warnings": [],
        }

        # 创建映射字典
        subject_code_map = {}
        grade_level_map = {}
        course_code_map = {}
        chapter_code_map = {}

        # 1. 导入学科
        # 注意：学科是共享的基础数据，即使overwrite_existing=True也不应该更新现有学科
        # 避免因为导入某个课程而污染系统中其他课程使用的学科数据
        subjects = data.get("subjects") or []
        for subject_data in subjects:
            try:
                # 检查是否已存在
                existing = await db.execute(
                    select(Subject).where(Subject.code == subject_data["code"])
                )
                existing_subject = existing.scalar_one_or_none()

                subject_id_value = None

                if existing_subject:
                    # 学科已存在，直接使用现有学科，不更新（避免污染共享数据）
                    import_result["subjects"]["skipped"] += 1
                    subject_id_value = existing_subject.id
                else:
                    # 创建新学科
                    subject = Subject(**subject_data)
                    db.add(subject)
                    await db.commit()
                    await db.refresh(subject)
                    import_result["subjects"]["created"] += 1
                    subject_id_value = subject.id

                if subject_id_value is not None:
                    subject_code_map[subject_data["code"]] = subject_id_value

            except Exception as e:
                import_result["errors"].append(
                    f"导入学科失败 {subject_data.get('name', '')}: {str(e)}"
                )

        # 2. 导入年级
        # 注意：年级是共享的基础数据，即使overwrite_existing=True也不应该更新现有年级
        # 避免因为导入某个课程而污染系统中其他课程使用的年级数据
        grades = data.get("grades") or []
        for grade_data in grades:
            try:
                # 验证必需字段
                if "level" not in grade_data:
                    import_result["errors"].append(
                        f"导入年级失败 {grade_data.get('name', '未知')}: 缺少必需字段 'level'"
                    )
                    continue
                
                # 确保 level 是整数类型
                try:
                    grade_level = int(grade_data["level"])
                except (ValueError, TypeError):
                    import_result["errors"].append(
                        f"导入年级失败 {grade_data.get('name', '未知')}: 'level' 必须是整数，当前值为 {grade_data['level']}"
                    )
                    continue
                
                # 检查是否已存在
                existing = await db.execute(
                    select(Grade).where(Grade.level == grade_level)
                )
                existing_grade = existing.scalar_one_or_none()

                grade_id_value = None

                if existing_grade:
                    # 年级已存在，直接使用现有年级，不更新（避免污染共享数据）
                    import_result["grades"]["skipped"] += 1
                    grade_id_value = existing_grade.id
                else:
                    # 创建新年级，确保使用转换后的整数 level
                    grade_data_copy = grade_data.copy()
                    grade_data_copy["level"] = grade_level
                    grade = Grade(**grade_data_copy)
                    db.add(grade)
                    await db.commit()
                    await db.refresh(grade)
                    import_result["grades"]["created"] += 1
                    grade_id_value = grade.id

                if grade_id_value is not None:
                    grade_level_map[grade_level] = grade_id_value

            except Exception as e:
                import_result["errors"].append(
                    f"导入年级失败 {grade_data.get('name', '未知')}: {str(e)}"
                )

        # 3. 导入课程
        courses = data.get("courses") or []
        for course_data in courses:
            try:
                # 验证必需字段
                if "subject_code" not in course_data:
                    import_result["errors"].append(
                        f"导入课程失败 {course_data.get('name', '未知')}: 缺少必需字段 'subject_code'"
                    )
                    continue
                
                if "grade_level" not in course_data:
                    import_result["errors"].append(
                        f"导入课程失败 {course_data.get('name', '未知')}: 缺少必需字段 'grade_level'"
                    )
                    continue
                
                # 确保 grade_level 是整数类型，以便正确匹配
                try:
                    course_grade_level = int(course_data["grade_level"])
                except (ValueError, TypeError):
                    import_result["errors"].append(
                        f"导入课程失败 {course_data.get('name', '未知')}: 'grade_level' 必须是整数，当前值为 {course_data['grade_level']}"
                    )
                    continue
                
                # 获取学科和年级ID
                subject_id = subject_code_map.get(course_data["subject_code"])
                grade_id = grade_level_map.get(course_grade_level)

                if not subject_id:
                    import_result["warnings"].append(
                        f"导入课程失败 {course_data.get('name', '未知')}: 学科代码 '{course_data['subject_code']}' 不存在（请确保在导入文件中包含该学科）"
                    )
                    continue
                
                if not grade_id:
                    import_result["errors"].append(
                        f"导入课程失败 {course_data.get('name', '未知')}: 年级级别 {course_grade_level} 不存在（请确保在导入文件中包含该年级，且 level 值为 {course_grade_level}）"
                    )
                    continue

                # 验证 course_code 字段
                if "code" not in course_data or not course_data["code"]:
                    import_result["errors"].append(
                        f"导入课程失败 {course_data.get('name', '未知')}: 缺少必需字段 'code'（课程代码）"
                    )
                    continue

                course_code = course_data["code"]

                # 优先使用 course_code 来检查课程是否已存在
                # 这样可以区分同一学科和年级的不同课程（如"智慧农业"和"信息科技"）
                existing = await db.execute(
                    select(Course).where(Course.code == course_code)
                )
                existing_course = existing.scalar_one_or_none()

                course_id_value = None

                if existing_course:
                    # 如果找到相同 code 的课程，检查学科和年级是否匹配
                    if existing_course.subject_id != subject_id or existing_course.grade_id != grade_id:
                        import_result["errors"].append(
                            f"导入课程失败 {course_data.get('name', '未知')}: 课程代码 '{course_code}' 已存在，但属于不同的学科或年级（现有：学科ID={existing_course.subject_id}, 年级ID={existing_course.grade_id}；导入：学科ID={subject_id}, 年级ID={grade_id}）"
                        )
                        continue

                    if overwrite_existing:
                        # 更新现有课程
                        for key, value in course_data.items():
                            if key not in ["subject_code", "grade_level", "code"]:
                                setattr(existing_course, key, value)
                        await db.commit()
                        import_result["courses"]["skipped"] += 1
                    else:
                        import_result["courses"]["skipped"] += 1
                    course_id_value = existing_course.id
                else:
                    # 检查是否已有相同学科和年级的课程（但 code 不同）
                    # 如果存在，给出警告但允许创建（因为可能是不同的课程）
                    duplicate_check = await db.execute(
                        select(Course).where(
                            Course.subject_id == subject_id,
                            Course.grade_id == grade_id,
                            Course.name == course_data.get("name", "")
                        )
                    )
                    duplicate_course = duplicate_check.scalar_one_or_none()
                    
                    if duplicate_course:
                        # 如果名称也相同，则认为是重复课程
                        import_result["errors"].append(
                            f"导入课程失败 {course_data.get('name', '未知')}: 已存在相同名称、学科和年级的课程（代码：{duplicate_course.code}）。如需更新，请使用相同的课程代码或启用覆盖选项。"
                        )
                        continue

                    # 创建新课程
                    course = Course(
                        subject_id=subject_id,
                        grade_id=grade_id,
                        name=course_data["name"],
                        code=course_code,
                        description=course_data.get("description"),
                        is_active=course_data.get("is_active", True),
                        display_order=course_data.get("display_order", 0),
                        created_by=current_user.id,
                    )
                    db.add(course)
                    await db.commit()
                    await db.refresh(course)
                    import_result["courses"]["created"] += 1
                    course_id_value = course.id

                if course_id_value is not None:
                    course_code_map[course_code] = course_id_value

            except Exception as e:
                import_result["errors"].append(
                    f"导入课程失败 {course_data.get('name', '')}: {str(e)}"
                )

        # 4. 导入章节
        chapters = data.get("chapters") or []
        for chapter_data in chapters:
            try:
                # 获取课程ID
                course_id = course_code_map.get(chapter_data["course_code"])
                if not course_id:
                    import_result["errors"].append(
                        f"章节 {chapter_data.get('name', '')} 的课程不存在"
                    )
                    continue

                # 处理父章节关系
                parent_id = None
                if chapter_data.get("parent_code"):
                    parent_id = chapter_code_map.get(chapter_data["parent_code"])
                    if not parent_id:
                        import_result["errors"].append(
                            f"章节 {chapter_data.get('name', '')} 的父章节不存在"
                        )
                        continue

                # 检查是否已存在
                existing = await db.execute(
                    select(Chapter).where(
                        Chapter.course_id == course_id,
                        Chapter.code == chapter_data["code"],
                    )
                )
                existing_chapter = existing.scalar_one_or_none()

                chapter_id_value = None

                if existing_chapter:
                    if overwrite_existing:
                        # 更新现有章节
                        for key, value in chapter_data.items():
                            if key not in ["course_code", "parent_code"]:
                                setattr(existing_chapter, key, value)
                        setattr(existing_chapter, "parent_id", parent_id)
                        await db.commit()
                        import_result["chapters"]["skipped"] += 1
                    else:
                        import_result["chapters"]["skipped"] += 1
                    chapter_id_value = existing_chapter.id
                else:
                    # 创建新章节
                    chapter = Chapter(
                        course_id=course_id,
                        parent_id=parent_id,
                        name=chapter_data["name"],
                        code=chapter_data["code"],
                        description=chapter_data.get("description"),
                        display_order=chapter_data.get("display_order", 0),
                        is_active=chapter_data.get("is_active", True),
                    )
                    db.add(chapter)
                    await db.commit()
                    await db.refresh(chapter)
                    import_result["chapters"]["created"] += 1
                    chapter_id_value = chapter.id

                if chapter_id_value is not None:
                    chapter_code_map[chapter_data["code"]] = chapter_id_value

            except Exception as e:
                import_result["errors"].append(
                    f"导入章节失败 {chapter_data.get('name', '')}: {str(e)}"
                )

        # 辅助函数：获取或创建默认的"未分类"课程
        default_course_id_cache = None
        async def get_or_create_default_course(db: AsyncSession, current_user: User) -> int:
            """获取或创建默认的未分类课程，用于归类没有课程归属的教案"""
            nonlocal default_course_id_cache
            if default_course_id_cache is not None:
                return default_course_id_cache
            
            # 1. 获取或创建"未分类"学科
            default_subject_code = "uncategorized"
            subject_result = await db.execute(
                select(Subject).where(Subject.code == default_subject_code)
            )
            default_subject = subject_result.scalar_one_or_none()
            
            if not default_subject:
                default_subject = Subject(
                    name="未分类",
                    code=default_subject_code,
                    description="用于归类没有课程归属的教学案例",
                    is_active=True,
                    display_order=9999,  # 放在最后
                )
                db.add(default_subject)
                await db.commit()
                await db.refresh(default_subject)
            
            # 2. 获取或创建"未分类"年级（level=99，超出正常范围1-12）
            # 先尝试通过level查找
            default_grade_level = 99
            grade_result = await db.execute(
                select(Grade).where(Grade.level == default_grade_level)
            )
            default_grade = grade_result.scalar_one_or_none()
            
            # 如果通过level找不到，尝试通过名称查找（可能之前创建过level=0的）
            if not default_grade:
                grade_result_by_name = await db.execute(
                    select(Grade).where(Grade.name == "未分类")
                )
                default_grade = grade_result_by_name.scalar_one_or_none()
                
                # 如果找到了但level不是99，更新level为99
                if default_grade:
                    current_level = cast(int, default_grade.level)
                    if current_level != default_grade_level:
                        setattr(default_grade, 'level', default_grade_level)
                        await db.commit()
                        await db.refresh(default_grade)
            
            # 如果仍然不存在，创建新的
            if not default_grade:
                default_grade = Grade(
                    name="未分类",
                    level=default_grade_level,
                    is_active=True,
                )
                db.add(default_grade)
                await db.commit()
                await db.refresh(default_grade)
            
            # 3. 获取或创建"未分类"课程
            default_course_code = "uncategorized-course"
            course_result = await db.execute(
                select(Course).where(Course.code == default_course_code)
            )
            default_course = course_result.scalar_one_or_none()
            
            if not default_course:
                default_course = Course(
                    subject_id=default_subject.id,
                    grade_id=default_grade.id,
                    name="未分类课程",
                    code=default_course_code,
                    description="用于归类没有课程归属的教学案例",
                    is_active=True,
                    display_order=9999,
                    created_by=current_user.id,
                )
                db.add(default_course)
                await db.commit()
                await db.refresh(default_course)
            
            default_course_id_cache = cast(int, default_course.id)
            return cast(int, default_course.id)

        # 5. 导入教案
        lessons = data.get("lessons") or []
        for lesson_data in lessons:
            try:
                # 获取课程ID
                course_code = lesson_data.get("course_code")
                course_id = course_code_map.get(course_code) if course_code else None
                
                # 如果找不到课程，使用默认的"未分类"课程
                if not course_id:
                    course_id = await get_or_create_default_course(db, current_user)
                    # 记录提示信息（作为警告而不是错误）
                    lesson_title = lesson_data.get('title', '未知')
                    import_result["warnings"].append(
                        f"提示：教案 '{lesson_title}' 的课程代码 '{course_code}' 不存在，已自动归类到'未分类课程'"
                    )

                # 获取章节ID
                chapter_id = None
                if lesson_data.get("chapter_code"):
                    chapter_id = chapter_code_map.get(lesson_data["chapter_code"])
                    if not chapter_id:
                        import_result["errors"].append(
                            f"教案 {lesson_data.get('title', '')} 的章节不存在"
                        )
                        continue

                # 检查是否已存在
                existing = await db.execute(
                    select(Lesson).where(
                        Lesson.course_id == course_id,
                        Lesson.title == lesson_data["title"],
                    )
                )
                existing_lesson = existing.scalar_one_or_none()

                if existing_lesson:
                    if overwrite_existing:
                        # 更新现有教案
                        for key, value in lesson_data.items():
                            if key not in ["course_code", "chapter_code"]:
                                setattr(existing_lesson, key, value)
                        setattr(existing_lesson, "chapter_id", chapter_id)
                        await db.commit()
                        import_result["lessons"]["skipped"] += 1
                    else:
                        import_result["lessons"]["skipped"] += 1
                else:
                    # 创建新教案
                    # 导入的教案默认设置为PUBLISHED状态，实现共享功能
                    # 因为教师导出教案就表示愿意与他人分享
                    imported_status = lesson_data.get("status", "draft")
                    # 如果导出时是已发布状态，保持已发布；如果是草稿，也设为已发布（共享）
                    if imported_status and imported_status in ["published", "draft"]:
                        final_status = LessonStatus.PUBLISHED
                    elif imported_status:
                        try:
                            final_status = LessonStatus(imported_status)
                        except (ValueError, TypeError):
                            final_status = LessonStatus.PUBLISHED
                    else:
                        final_status = LessonStatus.PUBLISHED
                    
                    lesson = Lesson(
                        course_id=course_id,
                        chapter_id=chapter_id,
                        title=lesson_data["title"],
                        description=lesson_data.get("description"),
                        status=final_status,
                        content=lesson_data.get("content", []),
                        tags=lesson_data.get("tags", []),
                        cover_image_url=lesson_data.get("cover_image_url"),
                        difficulty_level=lesson_data.get("difficulty_level"),
                        estimated_duration=lesson_data.get("estimated_duration"),
                        reference_notes=lesson_data.get("reference_notes"),
                        creator_id=current_user.id,
                    )
                    # 如果是已发布状态，设置发布时间
                    if final_status == LessonStatus.PUBLISHED:
                        setattr(lesson, "published_at", datetime.utcnow())
                    db.add(lesson)
                    await db.commit()
                    await db.refresh(lesson)
                    import_result["lessons"]["created"] += 1

            except Exception as e:
                import_result["errors"].append(
                    f"导入教案失败 {lesson_data.get('title', '')}: {str(e)}"
                )

        # 6. 导入资源
        resources = data.get("resources") or []
        for resource_data in resources:
            try:
                # 获取章节ID
                chapter_id = chapter_code_map.get(resource_data["chapter_code"])
                if not chapter_id:
                    import_result["errors"].append(
                        f"资源 {resource_data.get('title', '')} 的章节不存在"
                    )
                    continue

                # 检查是否已存在
                existing = await db.execute(
                    select(Resource).where(
                        Resource.chapter_id == chapter_id,
                        Resource.title == resource_data["title"],
                    )
                )
                existing_resource = existing.scalar_one_or_none()

                if existing_resource:
                    if overwrite_existing:
                        # 更新现有资源
                        for key, value in resource_data.items():
                            if key != "chapter_code":
                                setattr(existing_resource, key, value)
                        await db.commit()
                        import_result["resources"]["skipped"] += 1
                    else:
                        import_result["resources"]["skipped"] += 1
                else:
                    # 创建新资源
                    resource = Resource(
                        chapter_id=chapter_id,
                        title=resource_data["title"],
                        description=resource_data.get("description"),
                        resource_type=resource_data["resource_type"],
                        file_url=resource_data.get("file_url"),
                        file_size=resource_data.get("file_size"),
                        page_count=resource_data.get("page_count"),
                        thumbnail_url=resource_data.get("thumbnail_url"),
                        is_official=resource_data.get("is_official", False),
                        is_downloadable=resource_data.get("is_downloadable", True),
                        is_active=resource_data.get("is_active", True),
                        display_order=resource_data.get("display_order", 0),
                        created_by=current_user.id,
                    )
                    db.add(resource)
                    await db.commit()
                    await db.refresh(resource)
                    import_result["resources"]["created"] += 1

            except Exception as e:
                import_result["errors"].append(
                    f"导入资源失败 {resource_data.get('title', '')}: {str(e)}"
                )

        return {
            "message": "导入完成",
            "result": import_result,
            "summary": {
                "total_created": sum(
                    import_result[key]["created"]
                    for key in [
                        "subjects",
                        "grades",
                        "courses",
                        "chapters",
                        "lessons",
                        "resources",
                    ]
                ),
                "total_skipped": sum(
                    import_result[key]["skipped"]
                    for key in [
                        "subjects",
                        "grades",
                        "courses",
                        "chapters",
                        "lessons",
                        "resources",
                    ]
                ),
                "total_errors": len(import_result["errors"]),
                "total_warnings": len(import_result.get("warnings", [])),
            },
        }

    except HTTPException:
        # 重新抛出 HTTPException，保持原始错误信息
        raise
    except Exception as e:
        # 记录详细错误信息用于调试
        import traceback
        error_trace = traceback.format_exc()
        print(f"导入失败 - 详细错误信息:\n{error_trace}")
        raise HTTPException(400, f"导入失败: {str(e)}")


@router.get("/lessons/{lesson_id}/export")
async def export_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin_or_researcher),
):
    """导出单个教案（教师、管理员或研究员）"""
    try:
        # 获取教案及其关联数据
        lesson_result = await db.execute(
            select(Lesson)
            .options(
                selectinload(Lesson.course).selectinload(Course.subject),
                selectinload(Lesson.course).selectinload(Course.grade),
                selectinload(Lesson.chapter),
                selectinload(Lesson.creator),
            )
            .where(Lesson.id == lesson_id)
        )
        lesson = lesson_result.scalar_one_or_none()
        
        if not lesson:
            raise HTTPException(404, "教案不存在")
        
        # 权限检查：教师只能导出自己创建的教案
        role_value = cast(str, getattr(current_user.role, "value", current_user.role))
        try:
            user_role = UserRole(role_value)
        except ValueError:
            raise HTTPException(status_code=403, detail="当前用户角色无效")
        
        if user_role == UserRole.TEACHER:
            creator_id = getattr(lesson, 'creator_id', None)
            current_user_id = getattr(current_user, 'id', None)
            if creator_id is not None and current_user_id is not None and creator_id != current_user_id:
                raise HTTPException(403, "只能导出自己创建的教案")
        
        # 获取课程信息
        course = lesson.course
        if not course:
            raise HTTPException(404, "教案关联的课程不存在")
        
        # 构建导出数据
        export_data = {
            "version": "1.0",
            "export_time": datetime.utcnow().isoformat(),
            "exported_by": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
            },
            "data": {
                "lessons": [],
                "courses": [],
                "chapters": [],
            }
        }
        
        # 添加课程信息
        course_data = {
            "code": course.code,
            "name": course.name,
            "description": course.description,
            "subject_code": course.subject.code if course.subject else None,
            "grade_level": course.grade.level if course.grade else None,
        }
        export_data["data"]["courses"].append(course_data)
        
        # 添加章节信息（如果教案关联了章节）
        if lesson.chapter:
            chapter_data = {
                "code": lesson.chapter.code,
                "name": lesson.chapter.name,
                "description": lesson.chapter.description,
                "course_code": course.code,
                "order": lesson.chapter.order,
            }
            export_data["data"]["chapters"].append(chapter_data)
        
        # 添加教案数据
        lesson_data = {
            "course_code": course.code,
            "chapter_code": lesson.chapter.code if lesson.chapter else None,
            "title": lesson.title,
            "description": lesson.description,
            "status": lesson.status.value,
            "content": lesson.content if lesson.content is not None else [],
            "tags": lesson.tags or [],
            "cover_image_url": lesson.cover_image_url,
            "difficulty_level": lesson.difficulty_level.value if lesson.difficulty_level is not None else None,
            "estimated_duration": lesson.estimated_duration,
            "reference_notes": lesson.reference_notes,
        }
        export_data["data"]["lessons"].append(lesson_data)
        
        # 收集所有需要导出的文件
        lesson_data_list = export_data["data"].get("lessons", [])
        try:
            files_map = collect_all_files(export_data, lesson_data_list, [])
        except Exception as e:
            # 如果收集文件失败，记录错误但继续（使用空文件映射）
            print(f"警告: 收集文件时出错: {str(e)}")
            files_map = {}
        
        # 创建ZIP文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 添加JSON数据
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            zip_file.writestr("data.json", json_str.encode("utf-8"))
            
            # 添加所有资源文件
            for zip_path, file_path in files_map.items():
                try:
                    if os.path.exists(file_path):
                        zip_file.write(file_path, zip_path)
                    else:
                        print(f"警告: 文件不存在 {file_path}")
                except Exception as e:
                    # 如果文件不存在或无法读取，记录错误但继续
                    print(f"警告: 无法添加文件 {file_path}: {str(e)}")
            
            # 创建文件清单
            manifest = {
                "version": "1.0",
                "export_time": datetime.utcnow().isoformat(),
                "files": list(files_map.keys()),
                "file_count": len(files_map)
            }
            zip_file.writestr("manifest.json", json.dumps(manifest, indent=2).encode("utf-8"))
        
        zip_buffer.seek(0)
        
        # 返回ZIP文件下载
        import urllib.parse
        filename = urllib.parse.quote(f"{lesson.title}_导出.zip")
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
        )
    except HTTPException:
        # 重新抛出 HTTPException，保持原始错误信息
        raise
    except Exception as e:
        # 记录详细错误信息用于调试
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"导出教案失败 - 详细错误信息:\n{error_trace}"
        print(error_msg)
        # 在开发环境中返回更详细的错误信息
        import sys
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            # 调试模式：返回完整错误信息
            raise HTTPException(500, f"导出教案失败: {str(e)}\n\n{error_trace}")
        else:
            # 生产模式：只返回简要错误信息
            raise HTTPException(500, f"导出教案失败: {str(e)}")
