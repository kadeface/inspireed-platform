"""
WebSocket 连接管理器
"""

from typing import Dict, Optional, List
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    """管理所有 WebSocket 连接"""
    
    def __init__(self):
        # 存储结构：{session_id: {student_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: int, student_id: int):
        """接受并注册新连接"""
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        
        # 如果学生已有连接，先断开旧连接（处理重复连接）
        if student_id in self.active_connections[session_id]:
            old_ws = self.active_connections[session_id][student_id]
            try:
                await old_ws.close()
            except:
                pass
        
        # 注册新连接
        self.active_connections[session_id][student_id] = websocket
        
        print(f"✅ 学生 {student_id} 连接到会话 {session_id}")
        print(f"📊 会话 {session_id} 当前在线: {len(self.active_connections[session_id])} 人")
    
    async def disconnect(self, session_id: int, student_id: int):
        """移除连接"""
        
        if session_id in self.active_connections:
            if student_id in self.active_connections[session_id]:
                del self.active_connections[session_id][student_id]
                print(f"🔌 学生 {student_id} 断开连接（会话 {session_id}）")
            
            # 如果会话没有连接了，删除会话记录
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                print(f"🗑️ 会话 {session_id} 已无在线学生，清理记录")
    
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
        
        if session_id not in self.active_connections:
            return
        
        # 添加时间戳
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        message_text = json.dumps(message)
        
        # 记录要删除的连接（发送失败的）
        disconnected_students = []
        
        for student_id, websocket in self.active_connections[session_id].items():
            # 跳过排除的学生
            if exclude_student_id and student_id == exclude_student_id:
                continue
            
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                print(f"❌ 广播失败（学生 {student_id}）: {str(e)}")
                disconnected_students.append(student_id)
        
        # 清理断开的连接
        for student_id in disconnected_students:
            await self.disconnect(session_id, student_id)
        
        print(f"📢 广播消息到会话 {session_id}（{len(self.active_connections[session_id])} 人）")
    
    def get_session_connections_count(self, session_id: int) -> int:
        """获取会话的在线人数"""
        
        if session_id in self.active_connections:
            return len(self.active_connections[session_id])
        return 0
    
    def get_all_session_ids(self) -> List[int]:
        """获取所有有在线学生的会话ID"""
        
        return list(self.active_connections.keys())


# 全局单例
manager = ConnectionManager()

