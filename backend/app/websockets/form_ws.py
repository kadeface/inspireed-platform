"""
Form WebSocket Handler - 互动表单实时通信
"""

import json
import logging
from typing import Optional, Dict, Any

from fastapi import WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user_from_token
from app.models.user import User, UserRole
from app.models.form_cell import FormCell, FormResponse
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)


class FormWebSocketHandler:
    """表单WebSocket处理器"""

    def __init__(self):
        self.active_form_rooms: Dict[int, Dict[str, Any]] = {}
        # 每个form_cell_id对应一个房间，存储房间状态

    async def handle_connection(
        self,
        websocket: WebSocket,
        form_cell_id: int,
        token: str,
        db: AsyncSession
    ):
        """
        处理WebSocket连接

        Args:
            websocket: WebSocket连接
            form_cell_id: 表单ID
            token: JWT token
            db: 数据库会话
        """
        # 验证用户身份
        try:
            current_user = await get_current_user_from_token(token, db)
        except Exception as e:
            logger.warning(f"Form WS authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # 验证表单是否存在
        result = await db.execute(
            select(FormCell).where(FormCell.id == form_cell_id)
        )
        form_cell = result.scalar_one_or_none()
        if not form_cell:
            await websocket.close(code=1008, reason="Form not found")
            return

        # 确定用户角色和通道范围
        user_role = current_user.role
        scope = "form"  # 使用form作为scope

        # 接受连接
        await websocket.accept()

        # 注册到连接管理器
        await manager.connect_v2(
            websocket=websocket,
            scope=scope,
            channel_id=form_cell_id,
            user_id=current_user.id,
            role=user_role
        )

        # 初始化房间状态（如果不存在）
        if form_cell_id not in self.active_form_rooms:
            self.active_form_rooms[form_cell_id] = {
                "is_active": False,
                "participants": set(),
                "response_count": 0
            }

        # 添加参与者
        self.active_form_rooms[form_cell_id]["participants"].add(current_user.id)

        role_name = "教师" if user_role == UserRole.TEACHER else "学生"
        logger.info(
            f"Form WebSocket: {role_name} {current_user.id} connected to form {form_cell_id}"
        )

        # 发送欢迎消息
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "form_cell_id": form_cell_id,
            "user_id": current_user.id,
            "role": user_role.value,
            "is_active": self.active_form_rooms[form_cell_id]["is_active"]
        }))

        # 发送当前统计（如果表单已激活）
        if self.active_form_rooms[form_cell_id]["is_active"]:
            await self._send_current_results(websocket, form_cell_id, db)

        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)

                await self._handle_message(
                    message=message,
                    websocket=websocket,
                    form_cell_id=form_cell_id,
                    current_user=current_user,
                    db=db
                )

        except WebSocketDisconnect:
            logger.info(f"Form WebSocket: User {current_user.id} disconnected from form {form_cell_id}")

        except Exception as e:
            logger.error(f"Form WebSocket error for user {current_user.id}: {e}")

        finally:
            # 清理连接
            await manager.disconnect_v2(
                scope=scope,
                channel_id=form_cell_id,
                user_id=current_user.id,
                role=user_role
            )

            # 从房间移除参与者
            if form_cell_id in self.active_form_rooms:
                self.active_form_rooms[form_cell_id]["participants"].discard(current_user.id)

    async def _handle_message(
        self,
        message: Dict[str, Any],
        websocket: WebSocket,
        form_cell_id: int,
        current_user: User,
        db: AsyncSession
    ):
        """
        处理接收到的消息

        Args:
            message: 消息内容
            websocket: WebSocket连接
            form_cell_id: 表单ID
            current_user: 当前用户
            db: 数据库会话
        """
        message_type = message.get("type")

        if message_type == "form_start":
            # 教师开始投票
            if current_user.role != UserRole.TEACHER:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "detail": "只有教师可以开始投票"
                }))
                return

            await self._handle_form_start(form_cell_id, db)

        elif message_type == "form_stop":
            # 教师停止投票
            if current_user.role != UserRole.TEACHER:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "detail": "只有教师可以停止投票"
                }))
                return

            await self._handle_form_stop(form_cell_id, db)

        elif message_type == "form_submit":
            # 学生提交答案
            if current_user.role != UserRole.STUDENT:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "detail": "只有学生可以提交答案"
                }))
                return

            await self._handle_form_submit(
                message=message,
                form_cell_id=form_cell_id,
                current_user=current_user,
                db=db
            )

        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def _handle_form_start(self, form_cell_id: int, db: AsyncSession):
        """处理开始投票"""
        if form_cell_id not in self.active_form_rooms:
            self.active_form_rooms[form_cell_id] = {
                "is_active": False,
                "participants": set(),
                "response_count": 0
            }

        self.active_form_rooms[form_cell_id]["is_active"] = True

        # 广播开始消息给所有用户
        await manager.broadcast(
            event={
                "type": "form_started",
                "form_cell_id": form_cell_id
            },
            scope="form",
            channel_id=form_cell_id
        )

        logger.info(f"Form {form_cell_id} started")

    async def _handle_form_stop(self, form_cell_id: int, db: AsyncSession):
        """处理停止投票"""
        if form_cell_id in self.active_form_rooms:
            self.active_form_rooms[form_cell_id]["is_active"] = False

        # 广播停止消息给所有用户
        await manager.broadcast(
            event={
                "type": "form_stopped",
                "form_cell_id": form_cell_id
            },
            scope="form",
            channel_id=form_cell_id
        )

        logger.info(f"Form {form_cell_id} stopped")

    async def _handle_form_submit(
        self,
        message: Dict[str, Any],
        form_cell_id: int,
        current_user: User,
        db: AsyncSession
    ):
        """处理学生提交答案"""
        # 检查表单是否激活
        if form_cell_id not in self.active_form_rooms or \
           not self.active_form_rooms[form_cell_id]["is_active"]:
            await manager.send_to_student(
                event={
                    "type": "error",
                    "detail": "投票尚未开始或已结束"
                },
                scope="form",
                channel_id=form_cell_id,
                student_ids=[current_user.id]
            )
            return

        answers = message.get("answers")
        session_id = message.get("session_id")

        if not answers:
            await manager.send_to_student(
                event={
                    "type": "error",
                    "detail": "答案不能为空"
                },
                scope="form",
                channel_id=form_cell_id,
                student_ids=[current_user.id]
            )
            return

        # 创建答案记录
        try:
            form_response = FormResponse(
                form_cell_id=form_cell_id,
                user_id=current_user.id,
                answers=answers,
                session_id=session_id
            )
            db.add(form_response)
            await db.commit()

            # 更新房间计数
            if form_cell_id in self.active_form_rooms:
                self.active_form_rooms[form_cell_id]["response_count"] += 1

            # 发送确认消息给学生
            await manager.send_to_student(
                event={
                    "type": "submit_success",
                    "form_cell_id": form_cell_id
                },
                scope="form",
                channel_id=form_cell_id,
                student_ids=[current_user.id]
            )

            # 广播新答案通知给教师
            await manager.send_to_teacher(
                event={
                    "type": "new_response",
                    "form_cell_id": form_cell_id,
                    "user_id": current_user.id
                },
                scope="form",
                channel_id=form_cell_id
            )

            # 广播更新后的结果给所有人
            await self._broadcast_results_update(form_cell_id, db)

            logger.info(f"User {current_user.id} submitted response for form {form_cell_id}")

        except Exception as e:
            logger.error(f"Error saving form response: {e}")
            await manager.send_to_student(
                event={
                    "type": "error",
                    "detail": "提交答案失败"
                },
                scope="form",
                channel_id=form_cell_id,
                student_ids=[current_user.id]
            )

    async def _send_current_results(
        self,
        websocket: WebSocket,
        form_cell_id: int,
        db: AsyncSession
    ):
        """发送当前结果统计"""
        try:
            # 获取表单响应数
            from sqlalchemy import func, text as sql_text

            count_result = await db.execute(
                select(func.count(FormResponse.id))
                .where(FormResponse.form_cell_id == form_cell_id)
            )
            total_responses = count_result.scalar() or 0

            # 发送当前统计
            await websocket.send_text(json.dumps({
                "type": "results_update",
                "form_cell_id": form_cell_id,
                "total_responses": total_responses
            }))

        except Exception as e:
            logger.error(f"Error sending current results: {e}")

    async def _broadcast_results_update(self, form_cell_id: int, db: AsyncSession):
        """广播结果更新"""
        try:
            from sqlalchemy import func

            # 获取表单响应数
            count_result = await db.execute(
                select(func.count(FormResponse.id))
                .where(FormResponse.form_cell_id == form_cell_id)
            )
            total_responses = count_result.scalar() or 0

            # 广播结果更新
            await manager.broadcast(
                event={
                    "type": "results_update",
                    "form_cell_id": form_cell_id,
                    "total_responses": total_responses
                },
                scope="form",
                channel_id=form_cell_id
            )

        except Exception as e:
            logger.error(f"Error broadcasting results update: {e}")


# 全局单例
form_ws_handler = FormWebSocketHandler()
