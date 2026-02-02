"""
FastAPI 主应用
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.exceptions import RequestValidationError
import traceback
import os
import re
import mimetypes

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router

# CORS 源匹配正则表达式（与 CORS 配置保持一致）
# 支持：localhost、所有IP地址（包括公网和局域网）、Cloud Studio 域名
CORS_ORIGIN_PATTERN = re.compile(
    r"^https?://((localhost|127\.0\.0\.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?|.*\.cloudstudio\.club|.*\.coding\.net)$"
)


def fix_redirect_response(response, origin: str, request: Request) -> None:
    """
    修复 307 重定向响应：添加 CORS 头并修复 Location URL
    
    Args:
        response: FastAPI 响应对象
        origin: 请求的 Origin 头
        request: FastAPI 请求对象
    """
    if not origin or not CORS_ORIGIN_PATTERN.match(origin):
        return
    
    # 添加 CORS 头
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    # 修复 Location URL（HTTP -> HTTPS）
    if not origin.startswith("https://"):
        return
        
    location = response.headers.get("Location")
    if not location:
        return
    
    if location.startswith("http://"):
        # 绝对路径：直接替换
        response.headers["Location"] = location.replace("http://", "https://")
    elif location.startswith("/"):
        # 相对路径：构建完整 HTTPS URL
        host = request.headers.get("host") or request.headers.get("x-forwarded-host")
        if host:
            response.headers["Location"] = f"https://{host}{location}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    import asyncio
    import traceback
    
    # 启动时初始化数据库（带重试机制）
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        print(traceback.format_exc())
        # 不抛出异常，让应用继续启动，但会在首次数据库操作时失败
        # 这样可以避免健康检查失败
        print("⚠️ Application will continue, but database operations may fail")

    yield

    # 关闭时清理资源
    try:
        await close_db()
        print("👋 Database connection closed")
    except Exception as e:
        print(f"⚠️ Error closing database: {e}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# 配置CORS
cors_config = {
    "allow_credentials": True,
    "allow_methods": ["*"],  # 允许所有 HTTP 方法，包括 OPTIONS（预检请求）
    "allow_headers": ["*"],  # 允许所有请求头
    "expose_headers": ["*"],  # 暴露所有响应头
    "max_age": 3600,  # 预检请求缓存时间（秒）
}

# 如果启用局域网访问，使用正则表达式匹配所有局域网IP和 Cloud Studio 域名
# 或者如果 BACKEND_CORS_ORIGINS 包含 "*"，也使用正则表达式允许所有来源
if settings.ALLOW_LAN_ACCESS or (settings.BACKEND_CORS_ORIGINS and "*" in [str(o) for o in settings.BACKEND_CORS_ORIGINS]):
    # 匹配 localhost、常见的局域网IP段、以及 Cloud Studio 域名
    # Cloud Studio URL 格式：https://{id}--{port}.{region}.cloudstudio.club
    # 注意：Cloud Studio 的端口在域名内部（--8000），不在后面（:8000）
    cors_config["allow_origin_regex"] = CORS_ORIGIN_PATTERN.pattern
    print(f"✅ CORS configured with LAN access enabled")
    print(f"   ALLOW_LAN_ACCESS: {settings.ALLOW_LAN_ACCESS}")
    print(f"   BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
    print(f"   Regex pattern: {cors_config['allow_origin_regex']}")
    # 测试 Cloud Studio 域名匹配
    test_origin = "https://645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club"
    if CORS_ORIGIN_PATTERN.match(test_origin):
        print(f"   ✅ Test origin matched: {test_origin}")
    else:
        print(f"   ❌ Test origin NOT matched: {test_origin}")
else:
    # 只允许配置的源
    cors_config["allow_origins"] = [
        str(origin) for origin in settings.BACKEND_CORS_ORIGINS
    ]
    print(f"✅ CORS configured with specific origins: {cors_config['allow_origins']}")

app.add_middleware(CORSMiddleware, **cors_config)

# 添加请求日志中间件（用于调试 CORS）
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求，特别是 OPTIONS 预检请求和 CORS 相关请求"""
    origin = request.headers.get("origin")
    method = request.method
    url = str(request.url)
    
    # 记录所有带有 Origin 头的请求（CORS 请求）
    if origin:
        print(f"🌐 [CORS] 请求: {method} {url}")
        print(f"   Origin: {origin}")
        # 检查 origin 是否匹配正则表达式
        if CORS_ORIGIN_PATTERN.match(origin):
            print(f"   ✅ Origin 匹配正则表达式")
        else:
            print(f"   ❌ Origin 不匹配正则表达式！")
    
    # 如果是 OPTIONS 请求（预检请求），记录详细信息
    if method == "OPTIONS":
        print(f"🔍 [CORS] OPTIONS 预检请求:")
        print(f"   Origin: {origin}")
        print(f"   URL: {url}")
        print(f"   Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        
        # 为 307 重定向响应添加 CORS 头并修复 Location URL（FastAPI 的尾部斜杠重定向）
        if response.status_code == 307 and origin:
            fix_redirect_response(response, origin, request)
        
        # 记录响应头（特别是 CORS 相关头）
        if origin or method == "OPTIONS":
            cors_headers = {
                k: v for k, v in response.headers.items() 
                if k.lower().startswith('access-control-')
            }
            if cors_headers:
                print(f"   ✅ CORS 响应头: {cors_headers}")
            else:
                print(f"   ⚠️ 警告：响应没有 CORS 头！")
                print(f"   状态码: {response.status_code}")
        
        return response
    except Exception as e:
        print(f"❌ [CORS] 请求处理异常: {e}")
        print(f"   Origin: {origin}")
        print(f"   URL: {url}")
        raise


# 全局异常处理器 - 确保错误响应包含CORS头
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，确保错误响应包含CORS头"""
    print(f"❌ Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    # 获取请求的 Origin 头
    origin = request.headers.get("origin")
    print(f"🔍 Request origin: {origin}")
    
    # 返回JSON响应，CORSMiddleware会自动添加CORS头
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": type(exc).__name__,
        },
    )
    
    # 手动添加CORS头（确保即使异常也能返回CORS头）
    if origin:
        # 检查origin是否匹配允许的源
        if settings.ALLOW_LAN_ACCESS and CORS_ORIGIN_PATTERN.match(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        elif origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    # 安全处理body，避免FormData等不可序列化对象
    body_content = exc.body
    try:
        # 尝试序列化body，如果失败则转为字符串
        import json
        json.dumps(body_content)
    except (TypeError, ValueError):
        body_content = str(body_content) if body_content else None
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": body_content,
        },
    )


# 配置静态文件服务 - 使用自定义路由确保CORS头被正确添加（支持 GET/HEAD，视频会发 HEAD 探路）
@app.api_route("/uploads/resources/{file_path:path}", methods=["GET", "HEAD"])
async def serve_static_file(file_path: str, request: Request):
    """
    提供静态文件服务，支持视频流（Range请求）和CORS
    支持图片、视频、音频等多媒体文件
    """
    # 构建文件路径
    file_full_path = os.path.join("storage/resources", file_path)
    
    # 安全检查：确保文件路径在允许的目录内
    if not os.path.abspath(file_full_path).startswith(os.path.abspath("storage/resources")):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access denied"}
        )
    
    # 检查文件是否存在
    if not os.path.exists(file_full_path) or not os.path.isfile(file_full_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "File not found"}
        )
    
    # 获取请求的 Origin 头
    origin = request.headers.get("origin")
    
    # 获取文件大小
    file_size = os.path.getsize(file_full_path)
    
    # 检查是否是Range请求（视频流）
    range_header = request.headers.get("range")
    
    if range_header:
        # 解析Range头：bytes=start-end
        import re
        match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            
            # 读取指定范围的文件内容
            from fastapi.responses import StreamingResponse
            
            def iter_file():
                with open(file_full_path, "rb") as f:
                    f.seek(start)
                    remaining = end - start + 1
                    chunk_size = 8192
                    while remaining > 0:
                        chunk = f.read(min(chunk_size, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk
            
            # 检测MIME类型
            import mimetypes
            media_type = mimetypes.guess_type(file_full_path)[0] or "application/octet-stream"
            
            # 创建206 Partial Content响应
            response = StreamingResponse(
                iter_file(),
                status_code=206,
                media_type=media_type,
            )
            
            # 添加Range相关头
            response.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            response.headers["Content-Length"] = str(end - start + 1)
            response.headers["Accept-Ranges"] = "bytes"
        else:
            # Range格式错误，返回完整文件
            response = FileResponse(
                file_full_path,
                media_type=None,
            )
    else:
        # 常规请求，返回完整文件
        response = FileResponse(
            file_full_path,
            media_type=None,
        )
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Content-Length"] = str(file_size)
    
    # 添加CORS头（无论是否有Origin，都添加，确保跨域访问）
    if origin and (settings.ALLOW_LAN_ACCESS and CORS_ORIGIN_PATTERN.match(origin)):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Range, Content-Type, Accept"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
    elif origin and origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Range, Content-Type, Accept"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
    else:
        # 即使没有Origin或不匹配，也添加基本的CORS头（用于直接访问）
        # 这对于生产环境的视频播放很重要
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
    
    # 添加缓存控制（视频文件可以缓存）
    response.headers["Cache-Control"] = "public, max-age=31536000"

    # HEAD 请求只返回头信息，不返回 body（避免 405）
    if request.method == "HEAD":
        return Response(status_code=response.status_code, headers=dict(response.headers))

    return response


@app.options("/uploads/resources/{file_path:path}")
async def options_static_file(request: Request):
    """处理OPTIONS预检请求"""
    origin = request.headers.get("origin")
    
    response = JSONResponse(content={})
    
    if origin and (settings.ALLOW_LAN_ACCESS and CORS_ORIGIN_PATTERN.match(origin)):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Range, Content-Type, Accept, Authorization"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
        response.headers["Access-Control-Max-Age"] = "3600"
    elif origin and origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Range, Content-Type, Accept, Authorization"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
        response.headers["Access-Control-Max-Age"] = "3600"
    else:
        # 默认允许所有来源（用于静态资源访问）
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Range, Content-Type, Accept"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
    
    return response

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to InspireEd API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
