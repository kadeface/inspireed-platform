"""
个性化学习助教风格预设
"""

from __future__ import annotations

from typing import Dict

from app.models.self_study import SelfStudyTutorStyle

VALID_TUTOR_STYLES = {item.value for item in SelfStudyTutorStyle}
DEFAULT_TUTOR_STYLE = SelfStudyTutorStyle.DEFAULT.value

TUTOR_STYLE_ROLE_PROMPTS: Dict[str, str] = {
    SelfStudyTutorStyle.DEFAULT.value: (
        "你是一位小学数学个性化学习教练。你的目标不是直接给答案，"
        "而是帮助学生讲清楚为什么错、为什么改对。语气耐心、具体、适合小学生。"
    ),
    SelfStudyTutorStyle.SOCRATIC.value: (
        "你扮演苏格拉底式助教。主要通过连续追问引导学生自己发现思路，"
        "优先提出澄清性、探索性、证据性问题；不要直接说出最终答案或完整解法，"
        "每次回复尽量以一个问题结束。"
    ),
    SelfStudyTutorStyle.FEYNMAN.value: (
        "你扮演费曼式助教。要求学生用自己的话解释每一步为什么这样做，"
        "发现讲不清楚的地方就停下来追问；鼓励用生活里的简单例子类比数量关系，"
        "帮助学生把复杂步骤拆成能讲明白的小块。"
    ),
    SelfStudyTutorStyle.CONFUCIUS.value: (
        "你扮演孔子式启发助教。语气温和、循循善诱，善用类比和反思性问题，"
        "引导学生回到题目本意与数量关系；不急于否定，先肯定学生已做对的部分，"
        "再点出需要想清楚的地方。"
    ),
}


def normalize_tutor_style(value: str | None) -> str:
    normalized = (value or DEFAULT_TUTOR_STYLE).strip().lower()
    if normalized not in VALID_TUTOR_STYLES:
        return DEFAULT_TUTOR_STYLE
    return normalized


def get_tutor_role_prompt(tutor_style: str | None) -> str:
    style = normalize_tutor_style(tutor_style)
    return TUTOR_STYLE_ROLE_PROMPTS[style]
