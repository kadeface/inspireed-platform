"""数据收集提交的展示名与体积限制。"""

from app.services.interactive_collect import payload_is_too_large, student_label_from_payload


def test_label_prefers_name_fields():
    assert student_label_from_payload({"姓名": " 张三 ", "完成": True}) == "张三"
    assert student_label_from_payload({"name": "Ann"}) == "Ann"
    assert student_label_from_payload({"完成": True}) == "未署名"


def test_payload_size_limit():
    assert payload_is_too_large({"note": "ok"}) is False
    assert payload_is_too_large({"blob": "x" * 20_000}) is True
