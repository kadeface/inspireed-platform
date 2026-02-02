"""
SessionStateMachine 单元测试

测试会话状态机的所有功能：
- 状态转换验证
- 非法状态转换拒绝
- 状态查询方法
- 重置功能
"""

import pytest
from app.services.session_state_machine import (
    SessionStatus,
    SessionStateMachine,
    InvalidStateTransitionError,
)


class TestSessionStateMachine:
    """测试 SessionStateMachine 类"""

    def test_initial_state(self):
        """测试初始状态应该是 PREPARING"""
        machine = SessionStateMachine()
        assert machine.status == SessionStatus.PREPARING
        assert machine.is_preparing()
        assert not machine.is_teaching()
        assert not machine.is_ended()

    def test_custom_initial_state(self):
        """测试自定义初始状态"""
        machine = SessionStateMachine(initial_status=SessionStatus.TEACHING)
        assert machine.status == SessionStatus.TEACHING
        assert not machine.is_preparing()
        assert machine.is_teaching()
        assert not machine.is_ended()

    def test_preparing_to_teaching(self):
        """测试 PREPARING → TEACHING 转换"""
        machine = SessionStateMachine()
        assert machine.can_transition_to(SessionStatus.TEACHING)

        machine.transition_to(SessionStatus.TEACHING)
        assert machine.status == SessionStatus.TEACHING
        assert machine.is_teaching()

    def test_preparing_to_ended(self):
        """测试 PREPARING → ENDED 转换"""
        machine = SessionStateMachine()
        assert machine.can_transition_to(SessionStatus.ENDED)

        machine.transition_to(SessionStatus.ENDED)
        assert machine.status == SessionStatus.ENDED
        assert machine.is_ended()

    def test_teaching_to_ended(self):
        """测试 TEACHING → ENDED 转换"""
        machine = SessionStateMachine(initial_status=SessionStatus.TEACHING)
        assert machine.can_transition_to(SessionStatus.ENDED)

        machine.transition_to(SessionStatus.ENDED)
        assert machine.status == SessionStatus.ENDED
        assert machine.is_ended()

    def test_invalid_teaching_to_preparing(self):
        """测试非法转换：TEACHING → PREPARING"""
        machine = SessionStateMachine(initial_status=SessionStatus.TEACHING)
        assert not machine.can_transition_to(SessionStatus.PREPARING)

        with pytest.raises(InvalidStateTransitionError) as exc_info:
            machine.transition_to(SessionStatus.PREPARING)

        assert exc_info.value.current_status == SessionStatus.TEACHING
        assert exc_info.value.new_status == SessionStatus.PREPARING

    def test_invalid_ended_to_preparing(self):
        """测试非法转换：ENDED → PREPARING"""
        machine = SessionStateMachine(initial_status=SessionStatus.ENDED)
        assert not machine.can_transition_to(SessionStatus.PREPARING)

        with pytest.raises(InvalidStateTransitionError):
            machine.transition_to(SessionStatus.PREPARING)

    def test_invalid_ended_to_teaching(self):
        """测试非法转换：ENDED → TEACHING"""
        machine = SessionStateMachine(initial_status=SessionStatus.ENDED)
        assert not machine.can_transition_to(SessionStatus.TEACHING)

        with pytest.raises(InvalidStateTransitionError):
            machine.transition_to(SessionStatus.TEACHING)

    def test_invalid_preparing_to_preparing(self):
        """测试非法转换：PREPARING → PREPARING（自己转换到自己）"""
        machine = SessionStateMachine()
        # 状态机不允许转换到当前状态
        assert not machine.can_transition_to(SessionStatus.PREPARING)

    def test_reset_from_preparing(self):
        """测试从 PREPARING 状态重置"""
        machine = SessionStateMachine()
        assert machine.is_preparing()

        machine.reset()
        assert machine.is_preparing()

    def test_reset_from_teaching(self):
        """测试从 TEACHING 状态重置"""
        machine = SessionStateMachine(initial_status=SessionStatus.TEACHING)
        assert machine.is_teaching()

        machine.reset()
        assert machine.is_preparing()

    def test_reset_from_ended(self):
        """测试从 ENDED 状态重置"""
        machine = SessionStateMachine(initial_status=SessionStatus.ENDED)
        assert machine.is_ended()

        machine.reset()
        assert machine.is_preparing()

    def test_reset_with_custom_state(self):
        """测试重置到自定义状态"""
        machine = SessionStateMachine()
        machine.reset(initial_status=SessionStatus.ENDED)

        assert machine.is_ended()

    def test_complete_workflow(self):
        """测试完整的工作流程：PREPARING → TEACHING → ENDED"""
        machine = SessionStateMachine()

        # 初始状态
        assert machine.is_preparing()

        # 开始上课
        machine.transition_to(SessionStatus.TEACHING)
        assert machine.is_teaching()

        # 结束课程
        machine.transition_to(SessionStatus.ENDED)
        assert machine.is_ended()

        # 尝试继续转换应该失败
        assert not machine.can_transition_to(SessionStatus.TEACHING)

    def test_cancelled_workflow(self):
        """测试取消课程流程：PREPARING → ENDED"""
        machine = SessionStateMachine()

        # 初始状态
        assert machine.is_preparing()

        # 取消课程（直接结束）
        machine.transition_to(SessionStatus.ENDED)
        assert machine.is_ended()

    def test_repr(self):
        """测试 __repr__ 方法"""
        machine = SessionStateMachine()
        repr_str = repr(machine)

        assert "SessionStateMachine" in repr_str
        assert "PREPARING" in repr_str
