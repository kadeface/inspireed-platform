"""
SessionStateMachine - 课堂会话状态机

实现简化后的3状态状态机：
- PREPARING (准备中)
- TEACHING (上课中)
- ENDED (已结束)

状态转换规则：
- PREPARING → TEACHING (教师开始上课)
- PREPARING → ENDED (取消课程)
- TEACHING → ENDED (教师结束课程)
- ENDED (终态，不能转换)
"""

from enum import Enum
from typing import Dict, List, Optional


class SessionStatus(str, Enum):
    """会话状态枚举"""
    PREPARING = "PREPARING"  # 准备中
    TEACHING = "TEACHING"    # 上课中
    ENDED = "ENDED"          # 已结束


class InvalidStateTransitionError(Exception):
    """非法状态转换异常"""
    def __init__(self, current_status: SessionStatus, new_status: SessionStatus):
        self.current_status = current_status
        self.new_status = new_status
        message = f"Cannot transition from {current_status.value} to {new_status.value}"
        super().__init__(message)


class SessionStateMachine:
    """
    会话状态机

    管理课堂会话的状态转换，确保只有合法的状态转换才能被执行。
    """

    # 定义合法的状态转换
    TRANSITIONS: Dict[SessionStatus, List[SessionStatus]] = {
        SessionStatus.PREPARING: [SessionStatus.TEACHING, SessionStatus.ENDED],
        SessionStatus.TEACHING: [SessionStatus.ENDED],
        SessionStatus.ENDED: [],  # 终态，不能转换
    }

    def __init__(self, initial_status: SessionStatus = SessionStatus.PREPARING):
        """
        初始化状态机

        Args:
            initial_status: 初始状态，默认为 PREPARING
        """
        self._status = initial_status

    @property
    def status(self) -> SessionStatus:
        """获取当前状态"""
        return self._status

    def can_transition_to(self, new_status: SessionStatus) -> bool:
        """
        检查是否可以转换到新状态

        Args:
            new_status: 目标状态

        Returns:
            bool: 如果可以转换返回 True，否则返回 False
        """
        allowed_transitions = self.TRANSITIONS.get(self._status, [])
        return new_status in allowed_transitions

    def transition_to(self, new_status: SessionStatus) -> bool:
        """
        执行状态转换

        Args:
            new_status: 目标状态

        Returns:
            bool: 转换成功返回 True

        Raises:
            InvalidStateTransitionError: 如果状态转换不合法
        """
        if not self.can_transition_to(new_status):
            raise InvalidStateTransitionError(self._status, new_status)

        self._status = new_status
        return True

    def is_preparing(self) -> bool:
        """是否处于准备中状态"""
        return self._status == SessionStatus.PREPARING

    def is_teaching(self) -> bool:
        """是否处于上课中状态"""
        return self._status == SessionStatus.TEACHING

    def is_ended(self) -> bool:
        """是否处于已结束状态"""
        return self._status == SessionStatus.ENDED

    def reset(self, initial_status: SessionStatus = SessionStatus.PREPARING) -> None:
        """
        重置状态机

        Args:
            initial_status: 重置后的初始状态，默认为 PREPARING
        """
        self._status = initial_status

    def __repr__(self) -> str:
        return f"SessionStateMachine(status={self._status.value})"
