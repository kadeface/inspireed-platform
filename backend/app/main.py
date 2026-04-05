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
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router

logger = logging.getLogger(__name__)

LAN_ORIGIN_PATTERN = re.compile(
    r"^https?://(localhost|127\.0\.0\.1"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})"
    r"(:\d+)?$"
)


def _is_origin_allowed(origin: str) -> bool:
    if settings.ALLOW_LAN_ACCESS:
        return bool(LAN_ORIGIN_PATTERN.match(origin))
    return origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]


def _add_cors_headers(response: JSONResponse, origin: str, methods: str = "GET, OPTIONS") -> None:
    if _is_origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = methods
        response.headers["Access-Control-Allow-Headers"] = "*"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    await init_db()
    logger.info("Database initialized")

    yield

    await close_db()
    logger.info("Database connection closed")


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
}

if settings.ALLOW_LAN_ACCESS:
    cors_config["allow_origin_regex"] = LAN_ORIGIN_PATTERN.pattern
    logger.info("CORS configured with LAN access enabled")
else:
    cors_config["allow_origins"] = [
        str(origin) for origin in settings.BACKEND_CORS_ORIGINS
    ]
    logger.info("CORS configured with specific origins: %s", cors_config["allow_origins"])

app.add_middleware(CORSMiddleware, **cors_config)


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
        _add_cors_headers(response, origin)

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


STORAGE_ROOT = os.path.abspath("storage/resources")


@app.get("/uploads/resources/{file_path:path}")
async def serve_static_file(file_path: str, request: Request):
    """提供静态文件服务，确保CORS头被正确添加"""
    file_full_path = os.path.join("storage/resources", file_path)

    if not os.path.abspath(file_full_path).startswith(STORAGE_ROOT):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access denied"},
        )

    if not os.path.exists(file_full_path) or not os.path.isfile(file_full_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "File not found"},
        )

    response = FileResponse(file_full_path)

    origin = request.headers.get("origin")
    if origin:
        _add_cors_headers(response, origin)

    return response


@app.options("/uploads/resources/{file_path:path}")
async def options_static_file(request: Request):
    """处理OPTIONS预检请求"""
    response = JSONResponse(content={})

    origin = request.headers.get("origin")
    if origin:
        _add_cors_headers(response, origin)

    return response


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
