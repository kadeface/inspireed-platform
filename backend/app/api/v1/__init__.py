"""
API v1 路由包
"""

from typing import cast

from fastapi import APIRouter

from app.api.v1 import (
    activities,
    admin_dashboard,
    admin_organization,
    admin_users,
    auth,
    cells,
    chapters,
    classroom_sessions,
    course_export,
    curriculum,
    favorites,
    learning_paths,
    lessons,
    library_assets,
    public_curriculum,
    questions,
    researcher_curriculum,
    resources,
    reviews,
    subject_groups,
    student_ai_assistant,
    teacher_ai_assistant,
    upload,
    users,
)

api_router = APIRouter()

public_curriculum_router = cast(
    APIRouter, getattr(public_curriculum, "router", None)
)
if public_curriculum_router is None:
    raise RuntimeError("public_curriculum router is not defined")

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(curriculum.router, prefix="/curriculum", tags=["课程体系"])
api_router.include_router(
    public_curriculum_router, prefix="/public/curriculum", tags=["公开-课程体系"]
)
api_router.include_router(chapters.router, prefix="/chapters", tags=["章节"])
api_router.include_router(resources.router, prefix="/resources", tags=["资源"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["教案"])
api_router.include_router(cells.router, prefix="/cells", tags=["单元"])
api_router.include_router(activities.router, prefix="/activities", tags=["教学活动"])
api_router.include_router(classroom_sessions.router, prefix="/classroom-sessions", tags=["课堂会话"])
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
api_router.include_router(
    teacher_ai_assistant.router,
    prefix="/teacher/assistant",
    tags=["教师-智能助手"],
)
api_router.include_router(
    student_ai_assistant.router,
    prefix="/student/assistant",
    tags=["学生-智能助手"],
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

# 文件上传路由
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])

# 资源库路由
api_router.include_router(library_assets.router, prefix="/library/assets", tags=["资源库"])
