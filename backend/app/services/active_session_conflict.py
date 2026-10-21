"""同一教案、同一班级已有未结束会话时的冲突说明。"""

from datetime import timedelta

ACTIVE_SESSION_EXISTS = "active_session_exists"

# 与学生端列表的可见窗口一致：上课 40 分钟，准备中 48 小时。
STUDENT_TEACHING_VISIBLE = timedelta(minutes=40)
STUDENT_PREPARING_VISIBLE = timedelta(hours=48)


def active_session_conflict_detail(session_id: int) -> dict:
    return {
        "code": ACTIVE_SESSION_EXISTS,
        "existing_session_id": session_id,
        "message": (
            f"该班级已有活跃的课堂会话（ID: {session_id}），"
            "请继续上一节或结束后再创建"
        ),
    }
