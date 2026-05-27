"""
API v1 路由包
"""

from typing import cast

from fastapi import APIRouter

from app.api.v1 import (
    monitoring_reports,
    activities,
    admin_dashboard,
    admin_organization,
    admin_rooms,
    admin_users,
    analytics,
    auth,
    cells,
    chapters,
    classroom_assistant,
    classroom_sessions,
    mathlab_contest,
    whiteboard,
    course_export,
    courseware,
    curriculum,
    daily_performance,
    data_center,
    debug_shared_lessons,
    evaluations,
    exam_rooms,
    exam_subjects,
    exams,
    favorites,
    import_tasks,
    learning_paths,
    lessons,
    library_assets,
    project_cells,
    public_curriculum,
    questions,
    researcher_curriculum,
    review_channel,
    resources,
    reviews,
    scores,
    sections,
    semesters,
    student_projects,
    subject_groups,
    student_ai_assistant,
    teacher_ai_assistant,
    teacher_positions,
    teachers,
    total_scores,
    upload,
    users,
    unified_import as unified_import_module,
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
api_router.include_router(sections.router, prefix="", tags=["大环节"])
api_router.include_router(activities.router, prefix="/activities", tags=["教学活动"])
api_router.include_router(classroom_sessions.router, prefix="/classroom-sessions", tags=["课堂会话"])
api_router.include_router(mathlab_contest.router, prefix="/classroom-sessions", tags=["MathLab竞赛"])
api_router.include_router(whiteboard.router, prefix="/classroom-sessions", tags=["协作白板"])
api_router.include_router(classroom_assistant.router, prefix="/classroom-assistant", tags=["班级教学助手"])
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
    debug_shared_lessons.router, prefix="/subject-groups", tags=["学科教研组-调试"]
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
api_router.include_router(
    admin_rooms.router, prefix="/admin/organization/rooms", tags=["管理员-课室管理"]
)

# 课程导出导入路由
api_router.include_router(
    course_export.router, prefix="/course-export", tags=["课程导出导入"]
)

# 文件上传路由
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])

# 统一导入路由
api_router.include_router(unified_import_module.router, tags=["统一导入"])

# 资源库路由
api_router.include_router(library_assets.router, prefix="/library/assets", tags=["资源库"])

# 学生项目路由
api_router.include_router(
    student_projects.router, prefix="/student/projects", tags=["学生-项目"]
)
api_router.include_router(
    project_cells.router, prefix="/project-cells", tags=["项目-单元"]
)

# 评价系统路由
api_router.include_router(
    semesters.router, prefix="/semesters", tags=["评价-学期管理"]
)
api_router.include_router(
    exam_subjects.router, tags=["评价-考试科目配置"]
)
api_router.include_router(
    exams.router, prefix="/exams", tags=["评价-考试管理"]
)
api_router.include_router(
    exam_rooms.router, prefix="/exams/{exam_id}/rooms", tags=["评价-考场安排"]
)
api_router.include_router(
    scores.router, prefix="/scores", tags=["评价-成绩查询"]
)
api_router.include_router(
    daily_performance.router, prefix="/daily-performance", tags=["评价-日常表现成绩"]
)
api_router.include_router(
    total_scores.router, prefix="/total-scores", tags=["评价-高中总分"]
)
api_router.include_router(
    evaluations.router, prefix="/evaluations", tags=["评价-增值评价"]
)
api_router.include_router(
    monitoring_reports.router,
    prefix="/monitoring-reports",
    tags=["评价-质量监测报告"],
)
api_router.include_router(
    data_center.router, tags=["评价-数据中心"]
)
api_router.include_router(
    import_tasks.router, prefix="/import-tasks", tags=["评价-导入任务"]
)
api_router.include_router(
    teachers.router, tags=["教师-教学任务管理"]
)
api_router.include_router(
    teacher_positions.router, tags=["教师-职务类型管理"]
)
api_router.include_router(
    analytics.router, prefix="/admin", tags=["评价-增值分析"]
)
api_router.include_router(
    review_channel.router, tags=["作品评审通道"]
)
# 创AI课件交互数据
api_router.include_router(
    courseware.router, prefix="/courseware", tags=["创AI-课件交互"]
)
