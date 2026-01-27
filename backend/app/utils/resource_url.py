"""
资源URL转换工具函数
将文件名转换为完整URL，或从URL中提取文件名
"""
from typing import Optional
from urllib.parse import urlparse
from fastapi import Request

from app.core.config import settings


def filename_to_url(filename: str, request: Optional[Request] = None) -> str:
    """
    将文件名转换为完整URL
    
    Args:
        filename: 文件名（如 "xxx.png"）、相对路径（如 "/uploads/resources/xxx.png"）
                  或完整URL（如 "http://host:port/uploads/resources/xxx.png"）
        request: FastAPI请求对象（可选，用于自动获取base_url）
    
    Returns:
        完整URL（如 "http://host:port/uploads/resources/xxx.png"）
        如果输入是完整URL且指向资源路径，会提取文件名后使用动态服务器地址重新构建
    
    示例:
        >>> filename_to_url("abc123.png", request)
        "http://localhost:8000/uploads/resources/abc123.png"
        
        >>> filename_to_url("/uploads/resources/abc123.png", request)
        "http://localhost:8000/uploads/resources/abc123.png"
        
        >>> filename_to_url("http://192.168.1.102:8000/uploads/resources/abc123.png", request)
        "http://localhost:8000/uploads/resources/abc123.png"  # 使用当前请求的服务器地址
    """
    if not filename:
        return filename
    
    # 如果已经是完整URL，检查是否是资源URL，如果是则提取文件名后重新构建（使用动态服务器地址）
    if filename.startswith(('http://', 'https://')):
        # 检查是否是资源URL（/uploads/resources/或/uploads/thumbnails/）
        if "/uploads/resources/" in filename or "/uploads/thumbnails/" in filename:
            # 提取文件名，然后使用动态服务器地址重新构建URL
            # 直接调用同文件中的url_to_filename函数
            filename = url_to_filename(filename)
        else:
            # 不是资源URL，保持原样（可能是外部链接）
            return filename
    
    # 向后兼容：如果包含路径前缀，提取文件名
    # 支持格式：/uploads/resources/xxx.png 或 uploads/resources/xxx.png
    if '/uploads/resources/' in filename:
        # 提取文件名部分
        filename = filename.split('/uploads/resources/')[-1]
    elif filename.startswith('/uploads/resources/'):
        filename = filename.replace('/uploads/resources/', '', 1)
    elif filename.startswith('uploads/resources/'):
        filename = filename.replace('uploads/resources/', '', 1)
    elif filename.startswith('/'):
        # 如果是以/开头的其他路径，也提取文件名
        filename = filename.split('/')[-1]
    
    # 获取base URL
    base_url = settings.RESOURCE_BASE_URL
    if not base_url and request:
        # 从请求中获取base URL
        base_url = str(request.base_url).rstrip('/')
    elif not base_url:
        # 如果没有配置且没有请求对象，使用默认值（开发环境）
        base_url = "http://localhost:8000"
    
    # 构建完整URL
    base_path = settings.RESOURCE_BASE_PATH.strip('/')
    return f"{base_url}/{base_path}/{filename}"


def url_to_filename(url: str) -> str:
    """
    从URL中提取文件名（向后兼容：支持完整URL和相对路径）
    
    Args:
        url: 完整URL（如 "http://host:port/uploads/resources/xxx.png"）
             或相对路径（如 "/uploads/resources/xxx.png"）
             或文件名（如 "xxx.png"）
    
    Returns:
        文件名（如 "xxx.png"）
    
    示例:
        >>> url_to_filename("http://localhost:8000/uploads/resources/abc123.png")
        "abc123.png"
        
        >>> url_to_filename("/uploads/resources/abc123.png")
        "abc123.png"
        
        >>> url_to_filename("abc123.png")
        "abc123.png"
    """
    if not url:
        return url
    
    # 如果已经是纯文件名（不包含路径分隔符和协议），直接返回
    if '/' not in url and not url.startswith(('http://', 'https://')):
        return url
    
    # 从完整URL或相对路径中提取路径部分
    if url.startswith(('http://', 'https://')):
        try:
            parsed = urlparse(url)
            path = parsed.path
        except Exception:
            # URL解析失败，尝试直接提取文件名
            path = url.split('/')[-1]
            return path if '.' in path else url
    else:
        path = url
    
    # 提取文件名（最后一个路径段）
    filename = path.split('/')[-1]
    
    # 如果提取失败（空字符串），返回原值
    return filename if filename else url


def normalize_filename(filename: str) -> str:
    """
    规范化文件名（移除路径前缀，只保留文件名）
    
    Args:
        filename: 文件名或路径
    
    Returns:
        规范化后的文件名
    
    示例:
        >>> normalize_filename("/uploads/resources/abc123.png")
        "abc123.png"
        
        >>> normalize_filename("uploads/resources/abc123.png")
        "abc123.png"
        
        >>> normalize_filename("abc123.png")
        "abc123.png"
    """
    return url_to_filename(filename)

