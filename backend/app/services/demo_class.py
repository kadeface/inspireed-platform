from __future__ import annotations

DEMO_SCHOOL_CODE = "DEMO"
DEMO_SCHOOL_NAME = "DEMO School"
DEMO_CLASS_NAME = "Demo Class"
DEMO_CLASS_CODE = "DEMO"
DEMO_REGION_CODE = "DEMO"
DEMO_REGION_NAME = "Demo Region"
DEMO_GRADE_NAME = "高一"
DEMO_PASSWORD = "123456"
DEMO_ACCOUNT_COUNT = 60
DEMO_EMAIL_DOMAIN = "demo.inspireed.local"


def demo_username(n: int) -> str:
    return f"st{n:02d}"


def demo_display_name(n: int) -> str:
    return f"ST{n:02d}"


def demo_email(n: int) -> str:
    return f"{demo_username(n)}@{DEMO_EMAIL_DOMAIN}"


def all_demo_usernames() -> list[str]:
    return [demo_username(i) for i in range(1, DEMO_ACCOUNT_COUNT + 1)]


def is_demo_username(username: str) -> bool:
    if len(username) != 4 or not username.startswith("st"):
        return False
    try:
        n = int(username[2:])
    except ValueError:
        return False
    return 1 <= n <= DEMO_ACCOUNT_COUNT
