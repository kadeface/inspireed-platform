"""
FastAPI 主应用
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print("✅ Database initialized")

    yield

    # 关闭时清理资源
    await close_db()
    print("👋 Database connection closed")


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
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# 如果启用局域网访问，使用正则表达式匹配所有局域网IP
if settings.ALLOW_LAN_ACCESS:
    # 匹配 localhost 和常见的局域网IP段（包括 192.168.x.x）
    # 注意：正则表达式需要匹配端口号
    cors_config[
        "allow_origin_regex"
    ] = r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?"
    print(f"✅ CORS configured with LAN access enabled (regex: {cors_config['allow_origin_regex']})")
else:
    # 只允许配置的源
    cors_config["allow_origins"] = [
        str(origin) for origin in settings.BACKEND_CORS_ORIGINS
    ]
    print(f"✅ CORS configured with specific origins: {cors_config['allow_origins']}")

app.add_middleware(CORSMiddleware, **cors_config)


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
        import re
        if settings.ALLOW_LAN_ACCESS:
            pattern = r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?"
            if re.match(pattern, origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
        elif origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


# 配置静态文件服务
app.mount(
    "/uploads/resources",
    StaticFiles(directory="storage/resources"),
    name="uploads_resources",
)

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
