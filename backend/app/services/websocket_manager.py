"""
WebSocket 连接管理器
支持学生和教师的双角色连接管理
"""

from typing import Dict, Optional, List
from fastapi import WebSocket
from starlette.websockets import WebSocketState
import json
from datetime import datetime

from app.models.user import UserRole


class ConnectionManager:
    """管理所有 WebSocket 连接"""
    
    def __init__(self):
        # 学生连接：{channel_key: {user_id: WebSocket}}
        # channel_key 格式: "session:{session_id}" 或 "lesson:{lesson_id}"
        self.student_connections: Dict[str, Dict[int, WebSocket]] = {}
        
        # 教师连接：{channel_key: {user_id: WebSocket}}
        self.teacher_connections: Dict[str, Dict[int, WebSocket]] = {}
        
        # 旧版兼容：{session_id: {student_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    def _make_channel_key(self, scope: str, id: int) -> str:
        """生成通道键"""
        return f"{scope}:{id}"
    
    async def connect_v2(
        self,
        *,
        websocket: WebSocket,
        scope: str,
        channel_id: int,
        user_id: int,
        role: UserRole
    ):
        """
        新版连接方法（支持双角色和双通道）
        
        参数:
            websocket: WebSocket 连接
            scope: 通道范围（'session' 或 'lesson'）
            channel_id: 通道ID（session_id 或 lesson_id）
            user_id: 用户ID
            role: 用户角色（TEACHER 或 STUDENT）
        """
        channel_key = self._make_channel_key(scope, channel_id)
        store = self.teacher_connections if role == UserRole.TEACHER else self.student_connections
        
        if channel_key not in store:
            store[channel_key] = {}
        
        # 如果用户已有连接，先断开旧连接
        if user_id in store[channel_key]:
            old_ws = store[channel_key][user_id]
            if old_ws.client_state == WebSocketState.CONNECTED:
                try:
                    await old_ws.close()
                except:
                    pass
        
        # 注册新连接
        store[channel_key][user_id] = websocket
        
        role_name = "教师" if role == UserRole.TEACHER else "学生"
        print(f"✅ {role_name} {user_id} 连接到 {scope} {channel_id}")
        print(f"📊 {scope} {channel_id} 当前在线 {role_name}: {len(store[channel_key])} 人")
    
    async def connect(self, websocket: WebSocket, session_id: int, student_id: int):
        """旧版连接方法（兼容性保留）"""
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        
        # 如果学生已有连接，先断开旧连接（处理重复连接）
        if student_id in self.active_connections[session_id]:
            old_ws = self.active_connections[session_id][student_id]
            try:
                await old_ws.close()
            except Exception:
                pass
        
        # 注册新连接
        self.active_connections[session_id][student_id] = websocket
        
        # 同时注册到新版存储
        await self.connect_v2(
            websocket=websocket,
            scope="session",
            channel_id=session_id,
            user_id=student_id,
            role=UserRole.STUDENT
        )
        
        print(f"✅ 学生 {student_id} 连接到会话 {session_id}")
        print(f"📊 会话 {session_id} 当前在线: {len(self.active_connections[session_id])} 人")
    
    async def disconnect_v2(
        self,
        *,
        scope: str,
        channel_id: int,
        user_id: int,
        role: UserRole
    ):
        """
        新版断开连接方法
        
        参数:
            scope: 通道范围（'session' 或 'lesson'）
            channel_id: 通道ID
            user_id: 用户ID
            role: 用户角色
        """
        channel_key = self._make_channel_key(scope, channel_id)
        store = self.teacher_connections if role == UserRole.TEACHER else self.student_connections
        
        if channel_key in store:
            store[channel_key].pop(user_id, None)
            
            role_name = "教师" if role == UserRole.TEACHER else "学生"
            print(f"🔌 {role_name} {user_id} 断开连接（{scope} {channel_id}）")
            
            # 如果通道没有连接了，删除通道记录
            if not store[channel_key]:
                del store[channel_key]
                print(f"🗑️ {scope} {channel_id} 已无在线{role_name}，清理记录")
    
    async def disconnect(self, session_id: int, student_id: int):
        """旧版断开连接方法（兼容性保留）"""
        
        if session_id in self.active_connections:
            if student_id in self.active_connections[session_id]:
                del self.active_connections[session_id][student_id]
                print(f"🔌 学生 {student_id} 断开连接（会话 {session_id}）")
            
            # 如果会话没有连接了，删除会话记录
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                print(f"🗑️ 会话 {session_id} 已无在线学生，清理记录")
        
        # 同时从新版存储断开
        await self.disconnect_v2(
            scope="session",
            channel_id=session_id,
            user_id=student_id,
            role=UserRole.STUDENT
        )
    
    async def send_personal_message(
        self,
        message: dict,
        session_id: int,
        student_id: int,
    ):
        """发送消息给特定学生"""
        
        if session_id in self.active_connections:
            if student_id in self.active_connections[session_id]:
                websocket = self.active_connections[session_id][student_id]
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"❌ 发送消息失败（学生 {student_id}）: {str(e)}")
                    # 连接已断开，清理
                    await self.disconnect(session_id, student_id)
    
    async def broadcast_to_session(
        self,
        message: dict,
        session_id: int,
        exclude_student_id: Optional[int] = None,
    ):
        """广播消息给会话内所有学生"""

        channel_key = self._make_channel_key("session", session_id)

        # 如果旧版存储为空，尝试使用新版存储
        if session_id not in self.active_connections:
            # 检查新版存储
            if channel_key in self.student_connections and len(self.student_connections[channel_key]) > 0:
                # 使用新版存储广播
                message_text = json.dumps(message) if "timestamp" in message else json.dumps({**message, "timestamp": datetime.utcnow().isoformat()})
                sent_count = 0
                for user_id, websocket in self.student_connections[channel_key].items():
                    if exclude_student_id and user_id == exclude_student_id:
                        continue
                    try:
                        await websocket.send_text(message_text)
                        sent_count += 1
                    except Exception:
                        pass
                return
            
            # 如果新版存储也没有连接，记录警告
            if channel_key not in self.student_connections or len(self.student_connections.get(channel_key, {})) == 0:
                print(f"⚠️ [broadcast_to_session] 会话 {session_id} 无学生 WebSocket 连接")
                return

        # 添加时间戳
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()

        message_text = json.dumps(message)

        # 记录要删除的连接（发送失败的）
        disconnected_students = []
        sent_count = 0

        for student_id, websocket in self.active_connections[session_id].items():
            # 跳过排除的学生
            if exclude_student_id and student_id == exclude_student_id:
                continue

            try:
                await websocket.send_text(message_text)
                sent_count += 1
            except Exception as e:
                print(f"❌ 广播失败（学生 {student_id}）: {str(e)}")
                disconnected_students.append(student_id)

        # 清理断开的连接
        for student_id in disconnected_students:
            await self.disconnect(session_id, student_id)

        # 同步广播给访客连接（只读观摩）
        guest_key = f"guest:{session_id}"
        guest_conns = getattr(self, "_guest_connections", {}).get(guest_key, set())
        dead_guests = []
        for gws in guest_conns:
            try:
                await gws.send_text(message_text)
            except Exception:
                dead_guests.append(gws)
        for gws in dead_guests:
            guest_conns.discard(gws)

    def get_session_connections_count(self, session_id: int) -> int:
        """获取会话的在线人数"""
        
        if session_id in self.active_connections:
            return len(self.active_connections[session_id])
        return 0
    
    def get_all_session_ids(self) -> List[int]:
        """获取所有有在线学生的会话ID"""
        
        return list(self.active_connections.keys())
    
    def has_teacher_connection(self, scope: str, channel_id: int, exclude_user_id: Optional[int] = None) -> bool:
        """
        检查是否有教师连接到指定通道
        
        参数:
            scope: 通道范围（'session' 或 'lesson'）
            channel_id: 通道ID
            exclude_user_id: 排除的用户ID（用于检查除特定用户外是否还有其他教师）
        """
        channel_key = self._make_channel_key(scope, channel_id)
        if channel_key not in self.teacher_connections:
            return False
        
        teacher_connections = self.teacher_connections[channel_key]
        if exclude_user_id:
            # 检查是否有除指定用户外的其他教师
            return any(uid != exclude_user_id for uid in teacher_connections.keys())
        else:
            # 检查是否有任何教师
            return len(teacher_connections) > 0
    
    async def send_to_teacher(self, event: dict, scope: str, channel_id: int, teacher_ids: List[int] = []):
        """
        发送消息给教师
        
        参数:
            event: 事件消息
            scope: 通道范围
            channel_id: 通道ID
            teacher_ids: 教师ID列表（None表示广播给所有教师）
        """
        await self._send_to_role(
            event=event,
            scope=scope,
            channel_id=channel_id,
            user_ids=teacher_ids,
            role=UserRole.TEACHER
        )
    
    async def send_to_student(self, event: dict, scope: str, channel_id: int, student_ids: List[int] = []):
        """
        发送消息给学生
        
        参数:
            event: 事件消息
            scope: 通道范围
            channel_id: 通道ID
            student_ids: 学生ID列表（None表示广播给所有学生）
        """
        await self._send_to_role(
            event=event,
            scope=scope,
            channel_id=channel_id,
            user_ids=student_ids,
            role=UserRole.STUDENT
        )
    
    async def broadcast(self, event: dict, scope: str, channel_id: int):
        """
        广播消息给通道内所有用户（学生+教师）
        
        参数:
            event: 事件消息
            scope: 通道范围
            channel_id: 通道ID
        """
        await self.send_to_teacher(event, scope, channel_id, [])
        await self.send_to_student(event, scope, channel_id, [])
    
    async def _send_to_role(
        self,
        event: dict,
        scope: str,
        channel_id: int,
        user_ids: List[int],
        role: UserRole
    ):
        """
        内部方法：发送消息给指定角色的用户
        
        参数:
            event: 事件消息
            scope: 通道范围
            channel_id: 通道ID
            user_ids: 用户ID列表（None表示广播）
            role: 用户角色
        """
        channel_key = self._make_channel_key(scope, channel_id)
        store = self.teacher_connections if role == UserRole.TEACHER else self.student_connections
        
        if channel_key not in store:
            return
        
        recipients = store[channel_key]
        delivery_list = user_ids if user_ids else list(recipients.keys())
        
        message_text = json.dumps(event)
        disconnected_users = []
        
        for user_id in delivery_list:
            websocket = recipients.get(user_id)
            if not websocket:
                continue
            
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                print(f"❌ 发送消息失败（用户 {user_id}）: {str(e)}")
                disconnected_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected_users:
            await self.disconnect_v2(
                scope=scope,
                channel_id=channel_id,
                user_id=user_id,
                role=role
            )


# 全局单例
manager = ConnectionManager()

