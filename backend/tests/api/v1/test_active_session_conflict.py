"""创建课堂遇到未结束会话时，错误体要带上会话 id，而不是只靠中文文案。"""

from app.services.active_session_conflict import active_session_conflict_detail


def test_conflict_detail_includes_session_id():
    detail = active_session_conflict_detail(42)

    assert detail["code"] == "active_session_exists"
    assert detail["existing_session_id"] == 42
    assert "42" in detail["message"]
    assert "已有活跃的课堂会话" in detail["message"]
