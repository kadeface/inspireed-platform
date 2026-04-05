"""
FastAPI 主应用
"""

import logging
import os
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router

logger = logging.getLogger(__name__)

CORS_ORIGIN_PATTERN = re.compile(
    r"^https?://((localhost|127\.0\.0\.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?|.*\.cloudstudio\.club|.*\.coding\.net)$"
)


def _is_origin_allowed(origin: str) -> bool:
    if settings.ALLOW_LAN_ACCESS and CORS_ORIGIN_PATTERN.match(origin):
        return True
    return origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]


def _add_cors_headers(
    response, origin: str, *,
    methods: str = "GET, HEAD, OPTIONS",
    headers: str = "Range, Content-Type, Accept",
    expose: str = "Content-Range, Content-Length, Accept-Ranges",
) -> None:
    if _is_origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = methods
        response.headers["Access-Control-Allow-Headers"] = headers
        response.headers["Access-Control-Expose-Headers"] = expose


def fix_redirect_response(response, origin: str, request: Request) -> None:
    """修复 307 重定向响应：添加 CORS 头并修复 Location URL"""
    if not origin or not CORS_ORIGIN_PATTERN.match(origin):
        return

    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    if not origin.startswith("https://"):
        return

    location = response.headers.get("Location")
    if not location:
        return

    if location.startswith("http://"):
        response.headers["Location"] = location.replace("http://", "https://")
    elif location.startswith("/"):
        host = request.headers.get("host") or request.headers.get("x-forwarded-host")
        if host:
            response.headers["Location"] = f"https://{host}{location}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception:
        logger.exception("Failed to initialize database")
        logger.warning("Application will continue, but database operations may fail")

    yield

    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception:
        logger.exception("Error closing database")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DOCS_ENABLED else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DOCS_ENABLED else None,
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

cors_config: dict = {
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "max_age": 3600,
}

if settings.ALLOW_LAN_ACCESS or (
    settings.BACKEND_CORS_ORIGINS and "*" in [str(o) for o in settings.BACKEND_CORS_ORIGINS]
):
    cors_config["allow_origin_regex"] = CORS_ORIGIN_PATTERN.pattern
    logger.info("CORS configured with LAN access enabled (pattern: %s)", CORS_ORIGIN_PATTERN.pattern)
else:
    cors_config["allow_origins"] = [
        str(origin) for origin in settings.BACKEND_CORS_ORIGINS
    ]
    logger.info("CORS configured with specific origins: %s", cors_config["allow_origins"])

app.add_middleware(CORSMiddleware, **cors_config)

@app.middleware("http")
async def redirect_cors_middleware(request: Request, call_next):
    """为 307 重定向响应添加 CORS 头并修复 Location URL"""
    origin = request.headers.get("origin")

    response = await call_next(request)

    if response.status_code == 307 and origin:
        fix_redirect_response(response, origin, request)

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler — never leaks internal details to the client."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

    origin = request.headers.get("origin")
    if origin:
        _add_cors_headers(response, origin, methods="*", headers="*")

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


# 安全占位：互动 HTML 可能引用 share-modal.js，若脚本内对不存在的 DOM 调用 addEventListener 会报错，统一返回带空值检查的占位脚本
SHARE_MODAL_JS_STUB = b"""(function(){
  function safeAdd(el, ev, fn) { if (el && typeof el.addEventListener === 'function') el.addEventListener(ev, fn); }
  var byId = function(id) { return document.getElementById ? document.getElementById(id) : null; };
  safeAdd(byId('share-btn'), 'click', function(){});
  safeAdd(byId('shareBtn'), 'click', function(){});
  safeAdd(byId('open-share-modal'), 'click', function(){});
  safeAdd(document.querySelector('.share-modal-trigger'), 'click', function(){});
})();
"""


# 配置静态文件服务 - 使用自定义路由确保CORS头被正确添加（支持 GET/HEAD，视频会发 HEAD 探路）
@app.api_route("/uploads/resources/{file_path:path}", methods=["GET", "HEAD"])
async def serve_static_file(file_path: str, request: Request):
    """
    提供静态文件服务，支持视频流（Range请求）和CORS
    支持图片、视频、音频等多媒体文件
    """
    # 请求 share-modal.js 时统一返回安全占位脚本，避免互动页无对应 DOM 时 addEventListener 报错
    if file_path.strip().rstrip("/") == "share-modal.js":
        return Response(
            content=SHARE_MODAL_JS_STUB,
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"},
        )

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
        match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            
            # 读取指定范围的文件内容
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
    
    if origin and _is_origin_allowed(origin):
        _add_cors_headers(response, origin)
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"

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

    if origin and _is_origin_allowed(origin):
        _add_cors_headers(
            response, origin,
            headers="Range, Content-Type, Accept, Authorization",
        )
        response.headers["Access-Control-Max-Age"] = "3600"
    else:
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
