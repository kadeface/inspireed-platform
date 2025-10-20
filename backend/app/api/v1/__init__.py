"""
API v1 路由包
"""
from fastapi import APIRouter

from app.api.v1 import auth, lessons, cells, qa, users, curriculum, chapters, resources

api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(curriculum.router, prefix="/curriculum", tags=["课程体系"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["章节"])
api_router.include_router(resources.router, prefix="/resources", tags=["资源"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["教案"])
api_router.include_router(cells.router, prefix="/cells", tags=["单元"])
api_router.include_router(qa.router, prefix="/qa", tags=["问答"])

