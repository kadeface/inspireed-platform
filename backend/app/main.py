"""
FastAPI 主应用
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
    # 匹配 localhost 和常见的局域网IP段
    cors_config[
        "allow_origin_regex"
    ] = r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?"
else:
    # 只允许配置的源
    cors_config["allow_origins"] = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

app.add_middleware(CORSMiddleware, **cors_config)

# 配置静态文件服务
app.mount(
    "/uploads/resources", StaticFiles(directory="storage/resources"), name="uploads_resources"
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
