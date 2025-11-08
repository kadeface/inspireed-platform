"""
通用数据验证与规范化工具
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - 仅用于类型检查
    from app.models.user import UserRole
else:
    UserRole = None  # type: ignore[assignment]


def normalize_user_role(value: Any, *, allow_none: bool = False) -> Optional["UserRole"]:
    """
    将外部传入的角色值统一转换为 UserRole 枚举。

    - 支持直接传入 UserRole
    - 支持大小写不敏感的字符串（会自动转为小写）
    - 当 allow_none=True 时允许 None 或空字符串
    """

    if value is None:
        if allow_none:
            return None
        raise ValueError("用户角色不能为空")

    from app.models.user import UserRole as _UserRole

    if isinstance(value, _UserRole):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if not normalized:
            if allow_none:
                return None
            raise ValueError("用户角色不能为空")
        try:
            return _UserRole(normalized)
        except ValueError as exc:  # pragma: no cover - 简单映射，无需覆盖
            raise ValueError(f"不支持的用户角色: {value}") from exc

    raise TypeError(f"用户角色类型错误: {type(value).__name__}, 需为字符串或 UserRole")
