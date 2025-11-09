"""
API v1 路由包
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    lessons,
    cells,
    questions,
    users,
    curriculum,
    chapters,
    resources,
    researcher_curriculum,
    admin_dashboard,
    admin_users,
    admin_organization,
    favorites,
    reviews,
    learning_paths,
    course_export,
    activities,
    subject_groups,
)

api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(curriculum.router, prefix="/curriculum", tags=["课程体系"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["章节"])
api_router.include_router(resources.router, prefix="/resources", tags=["资源"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["教案"])
api_router.include_router(cells.router, prefix="/cells", tags=["单元"])
api_router.include_router(activities.router, prefix="/activities", tags=["教学活动"])
api_router.include_router(questions.router, prefix="/questions", tags=["问答系统"])

# 学生端增强功能路由
api_router.include_router(favorites.router, prefix="/favorites", tags=["收藏"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["评分评论"])
api_router.include_router(
    learning_paths.router, prefix="/learning-paths", tags=["学习路径"]
)

# 教师协作功能路由
api_router.include_router(
    subject_groups.router, prefix="/subject-groups", tags=["学科教研组"]
)

# 角色专用路由
api_router.include_router(
    researcher_curriculum.router, prefix="/researcher/curriculum", tags=["教研员-课程体系"]
)
api_router.include_router(
    admin_dashboard.router, prefix="/admin/dashboard", tags=["管理员-数据看板"]
)
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["管理员-用户管理"])
api_router.include_router(
    admin_organization.router, prefix="/admin/organization", tags=["管理员-组织架构"]
)

# 课程导出导入路由
api_router.include_router(
    course_export.router, prefix="/course-export", tags=["课程导出导入"]
)
