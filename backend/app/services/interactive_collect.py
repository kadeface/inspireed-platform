"""交互课件数据收集：从提交内容里取出展示名，并限制体积。"""

from __future__ import annotations

import json
from typing import Optional

MAX_PAYLOAD_CHARS = 16_000
_LABEL_KEYS = ("姓名", "name", "student_name", "学生")


def student_label_from_payload(payload: dict) -> str:
    for key in _LABEL_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:100]
    return "未署名"


def payload_is_too_large(payload: Optional[dict]) -> bool:
    if not payload:
        return False
    encoded = json.dumps(payload, ensure_ascii=False, default=str)
    return len(encoded) > MAX_PAYLOAD_CHARS
