# WebSocket 实时同步设计方案

> **文档版本：** v1.0  
> **创建日期：** 2025-01-17  
> **状态：** 设计阶段 🎨  
> **优先级：** ⭐⭐⭐⭐⭐ 高优先级

## 概述

本文档详细说明将现有的**轮询（Polling）机制**升级为 **WebSocket 实时推送机制**的完整方案，以实现课堂同步场景下的0延迟、低负载实时通信。

### 当前问题

**现有架构（轮询机制）：**

```
教师端切换内容
  ↓
后端更新数据库（session.settings.display_cell_orders）
  ↓
❌ 没有主动推送给学生端
  ↓
学生端每1秒轮询一次 (GET /sessions/{id})
  ↓
检测到变化，更新UI
```

**存在的问题：**

1. ⏱️ **延迟问题**：最多有1秒延迟（轮询间隔）
2. 🔥 **服务器负载高**：30个学生 × 1次/秒 = 30 QPS（空负载）
3. 💸 **资源浪费**：即使没有变化，也会频繁请求
4. 📶 **扩展性差**：学生越多，服务器压力越大
5. 🔋 **电量消耗**：移动设备频繁请求，耗电量高

### 目标架构（WebSocket）

```
教师端切换内容
  ↓
后端更新数据库（session.settings.display_cell_orders）
  ↓
✅ WebSocket 服务器广播消息给所有在线学生
  ↓
学生端立即接收，实时更新UI（0延迟）
```

**预期收益：**

- ✅ **0延迟**：教师切换，学生立即看到
- ✅ **低负载**：只在有变化时推送，无空负载
- ✅ **节省资源**：服务器资源占用减少 90%+
- ✅ **更好扩展性**：支持数百学生同时在线
- ✅ **省电**：移动设备电量消耗减少
- ✅ **更符合实时教学场景**

---

## 技术选型

### 后端：FastAPI + WebSocket

**选择理由：**

- FastAPI 原生支持 WebSocket
- 与现有 ASGI 架构无缝集成
- 性能优异（基于 Starlette）
- 代码简洁，易于维护

**依赖库：**

```python
# 已在项目中
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
```

### 前端：原生 WebSocket API

**选择理由：**

- 浏览器原生支持，无需额外依赖
- 轻量、性能好
- Vue 3 响应式系统完美配合

**不使用第三方库的原因：**

- `socket.io-client`：过于庞大，功能冗余
- 原生 API 已足够满足需求

---

## 架构设计

### 1. WebSocket 连接管理

#### 1.1 连接建立

**连接 URL：**

```
ws://api-domain/api/v1/classroom-sessions/sessions/{session_id}/ws?token={jwt_token}
```

**认证方式：**

- **方案1（推荐）：** Query Parameter 传递 JWT Token
  - 优点：简单、兼容性好
  - 缺点：Token 暴露在 URL 中（使用 HTTPS/WSS 可避免）

- **方案2：** 首次连接后通过消息发送认证
  - 优点：Token 不在 URL 中
  - 缺点：实现复杂，需要处理认证状态

**本方案使用 Query Parameter（方案1）**

#### 1.2 连接生命周期

```typescript
1. 学生打开课程页面
   ↓
2. 调用 findAndJoinSession()
   ↓
3. 加入会话成功（POST /sessions/{id}/join）
   ↓
4. 建立 WebSocket 连接 (connectWebSocket)
   ↓
5. 连接成功，发送 "join" 消息
   ↓
6. 开始监听服务器消息
   ↓
7. 接收实时更新（教师切换内容等）
   ↓
8. 页面关闭/离开课程
   ↓
9. 断开 WebSocket 连接
   ↓
10. 调用 leaveSession()
```

### 2. 消息协议设计

#### 2.1 消息格式（JSON）

**基础结构：**

```typescript
interface WebSocketMessage {
  type: string          // 消息类型
  timestamp: string     // ISO 8601 时间戳
  data: any            // 消息数据（根据type不同而变化）
}
```

#### 2.2 客户端 → 服务器消息

**1. 加入会话（join）**

```json
{
  "type": "join",
  "timestamp": "2025-01-17T10:30:00Z",
  "data": {
    "session_id": 123,
    "student_id": 456
  }
}
```

**2. 心跳（ping）**

```json
{
  "type": "ping",
  "timestamp": "2025-01-17T10:30:15Z",
  "data": {}
}
```

**3. 更新进度（update_progress）**

```json
{
  "type": "update_progress",
  "timestamp": "2025-01-17T10:30:30Z",
  "data": {
    "current_cell_id": 10,
    "completed_cells": [1, 2, 3, 5],
    "progress_percentage": 45.5
  }
}
```

#### 2.3 服务器 → 客户端消息

**1. 连接成功（connected）**

```json
{
  "type": "connected",
  "timestamp": "2025-01-17T10:30:00Z",
  "data": {
    "session_id": 123,
    "current_state": {
      "status": "active",
      "display_cell_orders": [0, 2, 5],
      "current_cell_id": 10
    }
  }
}
```

**2. 内容切换（cell_changed）⭐ 核心消息**

```json
{
  "type": "cell_changed",
  "timestamp": "2025-01-17T10:30:45Z",
  "data": {
    "action": "navigate",
    "display_cell_orders": [0, 2, 5, 8],
    "current_cell_id": 15,
    "changed_by": {
      "user_id": 100,
      "user_name": "张老师"
    }
  }
}
```

**3. 会话状态变化（session_status_changed）**

```json
{
  "type": "session_status_changed",
  "timestamp": "2025-01-17T11:00:00Z",
  "data": {
    "status": "ended",
    "reason": "teacher_ended"
  }
}
```

**4. 活动开始（activity_started）**

```json
{
  "type": "activity_started",
  "timestamp": "2025-01-17T10:35:00Z",
  "data": {
    "activity_id": 20,
    "cell_id": 15,
    "duration_minutes": 10,
    "instructions": "请完成以下问题..."
  }
}
```

**5. 活动结束（activity_ended）**

```json
{
  "type": "activity_ended",
  "timestamp": "2025-01-17T10:45:00Z",
  "data": {
    "activity_id": 20,
    "show_results": true
  }
}
```

**6. 统计数据更新（statistics_updated）**

```json
{
  "type": "statistics_updated",
  "timestamp": "2025-01-17T10:30:50Z",
  "data": {
    "total_students": 30,
    "active_students": 28,
    "average_progress": 52.5
  }
}
```

**7. 心跳响应（pong）**

```json
{
  "type": "pong",
  "timestamp": "2025-01-17T10:30:15Z",
  "data": {}
}
```

**8. 错误消息（error）**

```json
{
  "type": "error",
  "timestamp": "2025-01-17T10:30:20Z",
  "data": {
    "code": "INVALID_SESSION",
    "message": "会话不存在或已结束",
    "details": {}
  }
}
```

### 3. 连接管理器（后端）

#### 3.1 ConnectionManager 类

**职责：**

- 管理所有 WebSocket 连接
- 按会话（session_id）分组存储连接
- 提供广播、单播、组播功能
- 处理连接异常和重连

**核心方法：**

```python
class ConnectionManager:
    def __init__(self):
        # 存储结构：{session_id: {student_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: int, student_id: int):
        """接受并注册新连接"""
        
    async def disconnect(self, session_id: int, student_id: int):
        """移除连接"""
        
    async def send_personal_message(self, message: dict, session_id: int, student_id: int):
        """发送消息给特定学生"""
        
    async def broadcast_to_session(self, message: dict, session_id: int, exclude_student_id: int = None):
        """广播消息给会话内所有学生"""
        
    async def send_to_teacher(self, message: dict, session_id: int):
        """发送消息给教师端"""
        
    def get_session_connections_count(self, session_id: int) -> int:
        """获取会话的在线人数"""
```

#### 3.2 数据结构

```python
from typing import Dict, Set
from fastapi import WebSocket

# 连接存储结构
active_connections: Dict[int, Dict[int, WebSocket]] = {
    # session_id: {student_id: websocket}
    123: {
        456: <WebSocket>,
        457: <WebSocket>,
        458: <WebSocket>,
    },
    124: {
        459: <WebSocket>,
    }
}
```

---

## 后端实现

### 1. WebSocket 端点

**文件：** `backend/app/api/v1/classroom_sessions.py`

```python
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime

# 全局连接管理器
manager = ConnectionManager()

@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: str,  # JWT token from query parameter
    db: AsyncSession = Depends(deps.get_db),
):
    """
    WebSocket 连接端点
    
    连接URL: ws://api/v1/classroom-sessions/sessions/{session_id}/ws?token={jwt}
    """
    
    # 1. 验证Token并获取用户信息
    try:
        current_user = await deps.get_current_user_from_token(token, db)
        if not current_user:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Auth failed: {str(e)}")
        return
    
    # 2. 验证用户角色（只允许学生连接，教师端使用HTTP API）
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.STUDENT:
        await websocket.close(code=1008, reason="Only students can connect via WebSocket")
        return
    
    # 3. 验证会话存在性和权限
    session = await db.get(ClassSession, session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # 验证学生属于该班级
    classroom_id = cast(int, session.classroom_id)
    student_classroom_id = cast(Optional[int], current_user.classroom_id)
    if student_classroom_id != classroom_id:
        await websocket.close(code=1008, reason="Access denied")
        return
    
    # 4. 接受连接
    await websocket.accept()
    student_id = cast(int, current_user.id)
    
    # 5. 注册连接
    await manager.connect(websocket, session_id, student_id)
    
    # 6. 发送初始状态（当前会话状态）
    await send_initial_state(websocket, session, db)
    
    # 7. 更新学生在线状态（数据库）
    await update_student_online_status(db, session_id, student_id, is_online=True)
    
    try:
        # 8. 监听客户端消息
        while True:
            # 接收文本消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            await handle_client_message(
                message=message,
                session_id=session_id,
                student_id=student_id,
                websocket=websocket,
                db=db,
            )
    
    except WebSocketDisconnect:
        # 客户端主动断开
        print(f"🔌 学生 {student_id} 断开连接（会话 {session_id}）")
    
    except Exception as e:
        # 异常断开
        print(f"❌ WebSocket异常: {str(e)}")
    
    finally:
        # 9. 清理：移除连接、更新状态
        await manager.disconnect(session_id, student_id)
        await update_student_online_status(db, session_id, student_id, is_online=False)
        print(f"✅ 学生 {student_id} 连接已清理（会话 {session_id}）")


async def send_initial_state(websocket: WebSocket, session: ClassSession, db: AsyncSession):
    """发送初始状态给新连接的客户端"""
    
    message = {
        "type": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "session_id": session.id,
            "current_state": {
                "status": session.status,
                "display_cell_orders": (session.settings or {}).get("display_cell_orders", []),
                "current_cell_id": session.current_cell_id,
                "current_activity_id": session.current_activity_id,
            }
        }
    }
    
    await websocket.send_text(json.dumps(message))


async def handle_client_message(
    message: dict,
    session_id: int,
    student_id: int,
    websocket: WebSocket,
    db: AsyncSession,
):
    """处理客户端发送的消息"""
    
    message_type = message.get("type")
    
    if message_type == "ping":
        # 心跳响应
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }))
    
    elif message_type == "update_progress":
        # 更新学生进度
        data = message.get("data", {})
        await update_student_progress(
            db=db,
            session_id=session_id,
            student_id=student_id,
            current_cell_id=data.get("current_cell_id"),
            completed_cells=data.get("completed_cells", []),
            progress_percentage=data.get("progress_percentage", 0),
        )
    
    else:
        # 未知消息类型
        print(f"⚠️ 未知消息类型: {message_type}")


async def update_student_online_status(
    db: AsyncSession,
    session_id: int,
    student_id: int,
    is_online: bool,
):
    """更新学生在线状态"""
    
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.student_id == student_id,
            )
        )
    )
    participation = result.scalar_one_or_none()
    
    if participation:
        participation.is_active = is_online
        participation.last_active_at = datetime.utcnow()
        if not is_online:
            participation.left_at = datetime.utcnow()
        await db.commit()


async def update_student_progress(
    db: AsyncSession,
    session_id: int,
    student_id: int,
    current_cell_id: Optional[int],
    completed_cells: List[int],
    progress_percentage: float,
):
    """更新学生学习进度"""
    
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session_id,
                StudentSessionParticipation.student_id == student_id,
            )
        )
    )
    participation = result.scalar_one_or_none()
    
    if participation:
        if current_cell_id:
            participation.current_cell_id = current_cell_id
        participation.completed_cells = completed_cells
        participation.progress_percentage = progress_percentage
        participation.last_active_at = datetime.utcnow()
        await db.commit()
```

### 2. ConnectionManager 实现

**文件：** `backend/app/services/websocket_manager.py`（新建）

```python
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
```

### 3. 修改导航API（广播变化）

**文件：** `backend/app/api/v1/classroom_sessions.py`

在 `navigate_to_cell` 方法中，保存数据后，广播消息：

```python
@router.post("/sessions/{session_id}/navigate", response_model=ClassSessionResponse)
async def navigate_to_cell(
    session_id: int,
    data: NavigateToCellRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """切换当前显示的Cell（使用 display_cell_orders 数组）"""
    
    # ... 现有逻辑：验证权限、更新数据库 ...
    
    # 保存 display_cell_orders 到 settings
    new_settings = dict(session.settings) if session.settings else {}
    new_settings["display_cell_orders"] = data.display_cell_orders
    setattr(session, "settings", new_settings)
    
    # 更新 current_cell_id
    if len(data.display_cell_orders) > 0:
        result = await db.execute(
            select(Cell).where(
                and_(
                    Cell.lesson_id == session.lesson_id,
                    Cell.order == data.display_cell_orders[0],
                )
            )
        )
        first_cell = result.scalar_one_or_none()
        session.current_cell_id = first_cell.id if first_cell else None
    else:
        session.current_cell_id = None
    
    await db.commit()
    await db.refresh(session)
    
    # ✅ 新增：通过 WebSocket 广播变化
    from app.services.websocket_manager import manager
    
    await manager.broadcast_to_session(
        message={
            "type": "cell_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "action": "navigate",
                "display_cell_orders": data.display_cell_orders,
                "current_cell_id": session.current_cell_id,
                "changed_by": {
                    "user_id": current_user.id,
                    "user_name": current_user.full_name or current_user.username,
                }
            }
        },
        session_id=session_id,
    )
    
    print(f"📢 已广播内容切换（会话 {session_id}）")
    
    return session
```

### 4. Token 认证辅助函数

**文件：** `backend/app/api/deps.py`

```python
from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User


async def get_current_user_from_token(
    token: str,
    db: AsyncSession,
) -> Optional[User]:
    """从 JWT Token 获取当前用户（用于 WebSocket 认证）"""
    
    try:
        # 解码 Token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        
        # 查询用户
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    except JWTError:
        return None
```

---

## 前端实现

### 1. WebSocket Service

**文件：** `frontend/src/services/websocket.ts`（新建）

```typescript
/**
 * WebSocket 服务
 */

export interface WebSocketMessage {
  type: string
  timestamp: string
  data: any
}

export type WebSocketEventCallback = (message: WebSocketMessage) => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private url: string = ''
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 3000 // 3秒
  private heartbeatInterval: number = 30000 // 30秒
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private isManualClose: boolean = false
  
  // 事件监听器
  private eventListeners: Map<string, Set<WebSocketEventCallback>> = new Map()
  
  /**
   * 连接 WebSocket
   */
  connect(sessionId: number, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // 构建 WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const wsBase = apiBase.replace('http://', '').replace('https://', '')
      
      this.url = `${wsProtocol}//${wsBase}/api/v1/classroom-sessions/sessions/${sessionId}/ws?token=${token}`
      
      console.log('🔌 连接 WebSocket:', this.url.replace(token, '***'))
      
      try {
        this.ws = new WebSocket(this.url)
        this.isManualClose = false
        
        // 连接成功
        this.ws.onopen = () => {
          console.log('✅ WebSocket 连接成功')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }
        
        // 接收消息
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('❌ 解析消息失败:', error)
          }
        }
        
        // 连接关闭
        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket 连接关闭:', event.code, event.reason)
          this.stopHeartbeat()
          
          // 如果不是手动关闭，尝试重连
          if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect(sessionId, token)
          }
        }
        
        // 连接错误
        this.ws.onerror = (error) => {
          console.error('❌ WebSocket 错误:', error)
          reject(error)
        }
        
      } catch (error) {
        console.error('❌ WebSocket 连接失败:', error)
        reject(error)
      }
    })
  }
  
  /**
   * 断开连接
   */
  disconnect() {
    this.isManualClose = true
    this.stopHeartbeat()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    console.log('🔌 WebSocket 已断开')
  }
  
  /**
   * 发送消息
   */
  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('⚠️ WebSocket 未连接，无法发送消息')
    }
  }
  
  /**
   * 监听特定类型的消息
   */
  on(messageType: string, callback: WebSocketEventCallback) {
    if (!this.eventListeners.has(messageType)) {
      this.eventListeners.set(messageType, new Set())
    }
    this.eventListeners.get(messageType)!.add(callback)
  }
  
  /**
   * 移除事件监听
   */
  off(messageType: string, callback: WebSocketEventCallback) {
    if (this.eventListeners.has(messageType)) {
      this.eventListeners.get(messageType)!.delete(callback)
    }
  }
  
  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage) {
    console.log('📨 收到消息:', message.type, message.data)
    
    // 触发对应类型的监听器
    if (this.eventListeners.has(message.type)) {
      const callbacks = this.eventListeners.get(message.type)!
      callbacks.forEach(callback => {
        try {
          callback(message)
        } catch (error) {
          console.error('❌ 消息处理回调错误:', error)
        }
      })
    }
    
    // 触发通用监听器（'*'）
    if (this.eventListeners.has('*')) {
      const callbacks = this.eventListeners.get('*')!
      callbacks.forEach(callback => {
        try {
          callback(message)
        } catch (error) {
          console.error('❌ 通用消息处理回调错误:', error)
        }
      })
    }
  }
  
  /**
   * 重连
   */
  private reconnect(sessionId: number, token: string) {
    this.reconnectAttempts++
    console.log(`🔄 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
    
    setTimeout(() => {
      this.connect(sessionId, token).catch(error => {
        console.error('❌ 重连失败:', error)
      })
    }, this.reconnectDelay)
  }
  
  /**
   * 开始心跳
   */
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({
        type: 'ping',
        timestamp: new Date().toISOString(),
        data: {},
      })
    }, this.heartbeatInterval)
  }
  
  /**
   * 停止心跳
   */
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
  
  /**
   * 获取连接状态
   */
  get isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// 单例
export const websocketService = new WebSocketService()
```

### 2. 修改 useClassroomSession Composable

**文件：** `frontend/src/composables/useClassroomSession.ts`

```typescript
import { ref, computed, onUnmounted } from 'vue'
import classroomSessionService from '../services/classroomSession'
import { websocketService, type WebSocketMessage } from '../services/websocket'
import { getAuthToken } from '../utils/auth' // 假设有获取 Token 的函数
import type { ClassSession, StudentParticipation } from '../types/classroomSession'

export function useClassroomSession(lessonId: number) {
  const session = ref<ClassSession | null>(null)
  const participation = ref<StudentParticipation | null>(null)
  const currentCellId = ref<number | null>(null)
  
  const isInClassroomMode = computed(() => {
    return session.value?.status === 'active'
  })
  
  /**
   * 查找并加入会话（使用 WebSocket）
   */
  async function findAndJoinSession() {
    try {
      // 1. 获取该教案的所有活跃会话
      const sessions = await classroomSessionService.listSessions(lessonId, 'active')
      
      if (sessions.length > 0) {
        const activeSession = sessions[0]
        
        // 确保 settings 被正确设置
        if (!activeSession.settings) {
          activeSession.settings = {}
        }
        
        session.value = activeSession
        
        // 处理字段映射
        const cellId = (activeSession as any).current_cell_id ?? activeSession.currentCellId ?? null
        currentCellId.value = cellId
        
        console.log('🎓 找到活跃会话:', {
          sessionId: activeSession.id,
          status: activeSession.status,
          currentCellId: cellId,
          settings: activeSession.settings,
        })
        
        // 2. 尝试加入会话
        try {
          participation.value = await classroomSessionService.joinSession(activeSession.id)
          console.log('✅ 成功加入会话:', participation.value)
        } catch (error: any) {
          if (error.response?.status === 403) {
            console.log('ℹ️ 已经加入过会话，继续使用')
          } else {
            console.error('❌ 加入会话失败:', error)
            throw error
          }
        }
        
        // 3. 建立 WebSocket 连接
        await connectWebSocket(activeSession.id)
        
        return activeSession
      } else {
        console.log('ℹ️ 未找到活跃会话')
      }
      
      return null
    } catch (error) {
      console.error('❌ 查找会话失败:', error)
      return null
    }
  }
  
  /**
   * 连接 WebSocket
   */
  async function connectWebSocket(sessionId: number) {
    try {
      // 获取认证 Token
      const token = getAuthToken()
      if (!token) {
        console.error('❌ 未找到认证 Token')
        return
      }
      
      // 连接 WebSocket
      await websocketService.connect(sessionId, token)
      
      // 监听消息
      setupWebSocketListeners()
      
      console.log('✅ WebSocket 连接已建立')
    } catch (error) {
      console.error('❌ WebSocket 连接失败:', error)
      console.log('✅ WebSocket 连接已建立')
    } catch (error) {
      console.error('❌ WebSocket 连接失败:', error)
      // 降级到轮询模式（保留兼容性）
      startPolling()
    }
  }
  
  /**
   * 设置 WebSocket 消息监听器
   */
  function setupWebSocketListeners() {
    // 1. 监听连接成功消息
    websocketService.on('connected', (message: WebSocketMessage) => {
      console.log('🎉 WebSocket 已连接，接收初始状态:', message.data)
      
      // 更新会话状态
      if (message.data.current_state && session.value) {
        session.value.status = message.data.current_state.status
        session.value.settings = {
          ...session.value.settings,
          display_cell_orders: message.data.current_state.display_cell_orders,
        }
        currentCellId.value = message.data.current_state.current_cell_id
      }
    })
    
    // 2. 监听内容切换消息（核心）
    websocketService.on('cell_changed', (message: WebSocketMessage) => {
      console.log('🔄 收到内容切换消息:', message.data)
      
      if (session.value) {
        // 更新 display_cell_orders
        if (message.data.display_cell_orders !== undefined) {
          session.value.settings = {
            ...session.value.settings,
            display_cell_orders: message.data.display_cell_orders,
          }
        }
        
        // 更新 current_cell_id
        if (message.data.current_cell_id !== undefined) {
          currentCellId.value = message.data.current_cell_id
        }
        
        console.log('✅ 内容已同步:', {
          displayCellOrders: session.value.settings?.display_cell_orders,
          currentCellId: currentCellId.value,
        })
      }
    })
    
    // 3. 监听会话状态变化
    websocketService.on('session_status_changed', (message: WebSocketMessage) => {
      console.log('📊 会话状态变化:', message.data)
      
      if (session.value) {
        session.value.status = message.data.status
        
        // 如果会话结束，断开连接
        if (message.data.status === 'ended') {
          console.log('⏹️ 会话已结束')
          disconnectWebSocket()
        }
      }
    })
    
    // 4. 监听活动开始
    websocketService.on('activity_started', (message: WebSocketMessage) => {
      console.log('🎯 活动开始:', message.data)
      // TODO: 触发活动界面显示
    })
    
    // 5. 监听活动结束
    websocketService.on('activity_ended', (message: WebSocketMessage) => {
      console.log('✅ 活动结束:', message.data)
      // TODO: 显示活动结果
    })
    
    // 6. 监听错误消息
    websocketService.on('error', (message: WebSocketMessage) => {
      console.error('❌ 服务器错误:', message.data)
      // TODO: 显示错误提示
    })
  }
  
  /**
   * 断开 WebSocket 连接
   */
  function disconnectWebSocket() {
    websocketService.disconnect()
  }
  
  /**
   * 离开会话
   */
  async function leaveSession() {
    // 断开 WebSocket
    disconnectWebSocket()
    
    if (session.value) {
      try {
        await classroomSessionService.leaveSession(session.value.id)
      } catch (error) {
        console.error('❌ 离开会话失败:', error)
      }
    }
    
    session.value = null
    participation.value = null
  }
  
  /**
   * 更新进度（通过 WebSocket）
   */
  async function updateProgress(completedCellIds: number[], currentCellId?: number) {
    if (!participation.value || !session.value) return
    
    // 计算进度百分比
    const totalCells = /* 获取总Cell数 */ 10 // TODO: 从 lesson.content.length 获取
    const progressPercentage = (completedCellIds.length / totalCells) * 100
    
    // 通过 WebSocket 发送进度更新
    websocketService.send({
      type: 'update_progress',
      timestamp: new Date().toISOString(),
      data: {
        current_cell_id: currentCellId || currentCellId.value,
        completed_cells: completedCellIds,
        progress_percentage: progressPercentage,
      },
    })
  }
  
  /**
   * 是否应该限制显示
   * 课堂模式下默认严格同步，只显示教师指定的Cell
   */
  const shouldSyncDisplay = computed(() => {
    if (!isInClassroomMode.value) {
      return false
    }
    const syncMode = session.value?.settings?.sync_mode
    return syncMode === 'strict' || syncMode === undefined || syncMode === null
  })
  
  /**
   * 是否有可显示的内容
   */
  const hasDisplayableContent = computed(() => {
    if (!isInClassroomMode.value) {
      return true
    }
    
    const settings = session.value?.settings
    const displayCellOrders = settings?.display_cell_orders || []
    
    return Array.isArray(displayCellOrders) && displayCellOrders.length > 0
  })
  
  // 清理函数
  onUnmounted(() => {
    disconnectWebSocket()
    leaveSession()
  })
  
  return {
    session,
    participation,
    currentCellId,
    isInClassroomMode,
    shouldSyncDisplay,
    hasDisplayableContent,
    findAndJoinSession,
    leaveSession,
    updateProgress,
  }
}

// ========== 轮询模式（降级方案，保留兼容性）==========

let pollingInterval: ReturnType<typeof setInterval> | null = null
const POLLING_INTERVAL = 5000 // 降级时使用5秒轮询（减少负载）

function startPolling() {
  if (pollingInterval) return
  
  console.log('⚠️ 降级到轮询模式（WebSocket 不可用）')
  pollingInterval = setInterval(() => {
    // 轮询逻辑（与现有实现相同）
    refreshSession()
  }, POLLING_INTERVAL)
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

async function refreshSession() {
  // ... 现有轮询逻辑 ...
}
```

### 3. 修改学生端页面

**文件：** `frontend/src/pages/Student/LessonView.vue`

```vue
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useClassroomSession } from '@/composables/useClassroomSession'
import lessonService from '@/services/lesson'
import type { Lesson } from '@/types/lesson'

const route = useRoute()
const lessonId = Number(route.params.id)

const lesson = ref<Lesson | null>(null)

// 使用课堂会话 Composable
const {
  session,
  isInClassroomMode,
  shouldSyncDisplay,
  hasDisplayableContent,
  findAndJoinSession,
} = useClassroomSession(lessonId)

/**
 * 过滤显示的Cells（使用 WebSocket 实时更新的数据）
 */
const filteredCells = computed(() => {
  if (!lesson.value?.content) return []
  
  // 非课堂模式：显示所有Cell
  if (!isInClassroomMode.value) {
    return lesson.value.content
  }
  
  // 课堂模式：严格同步，只显示教师指定的Cell
  if (shouldSyncDisplay.value) {
    const settings = session.value?.settings
    const displayOrders = settings?.display_cell_orders || []
    
    if (Array.isArray(displayOrders) && displayOrders.length > 0) {
      // 根据 display_cell_orders 过滤
      return lesson.value.content.filter((cell, index) => {
        const cellOrder = cell.order !== undefined ? cell.order : index
        return displayOrders.includes(cellOrder)
      })
    }
    
    // 如果没有选中任何模块，返回空数组
    return []
  }
  
  // 非严格同步模式：显示所有Cell
  return lesson.value.content
})

/**
 * 加载课程内容
 */
async function loadLesson() {
  try {
    const data = await lessonService.getLesson(lessonId)
    lesson.value = data
    
    // 加载完成后，尝试查找并加入会话
    await findAndJoinSession()
  } catch (error) {
    console.error('❌ 加载课程失败:', error)
  }
}

onMounted(() => {
  loadLesson()
})

// 监听 filteredCells 变化（用于调试）
watch(filteredCells, (newCells) => {
  console.log('📋 显示的Cell数量:', newCells.length)
})
</script>

<template>
  <div class="lesson-view">
    <!-- 课堂模式指示器 -->
    <div v-if="isInClassroomMode" class="classroom-mode-banner">
      <span class="badge">课堂模式</span>
      <span class="status">正在同步教师内容</span>
    </div>
    
    <!-- 等待教师切换内容 -->
    <div v-if="isInClassroomMode && !hasDisplayableContent" class="waiting-state">
      <div class="icon">⏳</div>
      <h3>等待教师切换内容</h3>
      <p>教师正在准备课程内容，请稍候...</p>
    </div>
    
    <!-- 课程内容 -->
    <div v-else class="lesson-content">
      <h1>{{ lesson?.title }}</h1>
      
      <!-- Cell列表 -->
      <div v-for="(cell, index) in filteredCells" :key="cell.id || index" class="cell-item">
        <!-- 根据 cell.type 渲染不同组件 -->
        <component :is="getCellComponent(cell.type)" :cell="cell" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.classroom-mode-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.waiting-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  color: #666;
}

.waiting-state .icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}
</style>
```

### 4. 获取认证Token工具函数

**文件：** `frontend/src/utils/auth.ts`

```typescript
/**
 * 获取当前用户的 JWT Token
 */
export function getAuthToken(): string | null {
  // 从 localStorage 获取 Token
  const token = localStorage.getItem('auth_token')
  
  // 或者从 Pinia Store 获取
  // import { useAuthStore } from '@/stores/auth'
  // const authStore = useAuthStore()
  // return authStore.token
  
  return token
}

/**
 * 设置认证 Token
 */
export function setAuthToken(token: string) {
  localStorage.setItem('auth_token', token)
}

/**
 * 清除认证 Token
 */
export function clearAuthToken() {
  localStorage.removeItem('auth_token')
}
```

---

## 迁移策略

### Phase 1: 实现 WebSocket 基础设施（Week 1）

**目标：** 搭建 WebSocket 服务端和客户端基础

**任务：**

1. ✅ 实现 `ConnectionManager` 类
2. ✅ 实现 WebSocket 端点（`/sessions/{id}/ws`）
3. ✅ 实现前端 `WebSocketService`
4. ✅ 添加认证机制（Token 验证）
5. ✅ 单元测试

**验收标准：**

- 学生能够成功连接 WebSocket
- 能够发送和接收心跳消息
- 断线自动重连正常工作

### Phase 2: 实现核心功能（Week 2）

**目标：** 实现内容同步的核心功能

**任务：**

1. ✅ 修改 `navigate_to_cell` API，添加广播逻辑
2. ✅ 前端监听 `cell_changed` 消息
3. ✅ 更新 `useClassroomSession` Composable
4. ✅ 修改学生端页面（`LessonView.vue`）
5. ✅ 集成测试

**验收标准：**

- 教师切换内容，学生端立即（<100ms）更新
- 多个学生同时在线，都能收到更新
- 页面刷新后能够重新连接并获取最新状态

### Phase 3: 灰度发布（Week 3）

**目标：** 小范围验证，收集反馈

**策略：**

1. **特性开关（Feature Flag）**
   
   ```typescript
   // 前端配置
   const USE_WEBSOCKET = import.meta.env.VITE_USE_WEBSOCKET === 'true'
   
   if (USE_WEBSOCKET) {
     await connectWebSocket(sessionId)
   } else {
     startPolling()
   }
   ```

2. **灰度用户**
   - 选择 10-20 名测试学生
   - 在小班级（<15人）中测试
   - 收集性能数据和用户反馈

3. **监控指标**
   - WebSocket 连接成功率
   - 消息延迟（教师切换 → 学生接收）
   - 断线重连次数
   - 服务器资源占用

### Phase 4: 全面切换（Week 4）

**目标：** 全量上线 WebSocket

**任务：**

1. ✅ 所有用户启用 WebSocket
2. ✅ 移除轮询代码（保留降级逻辑）
3. ✅ 性能优化
4. ✅ 文档更新

**降级方案（保留）：**

```typescript
// 如果 WebSocket 连接失败，自动降级到轮询
try {
  await connectWebSocket(sessionId)
} catch (error) {
  console.warn('⚠️ WebSocket 不可用，降级到轮询模式')
  startPolling()
}
```

---

## 性能对比

### 对比测试场景

**测试条件：**
- 班级人数：30 名学生
- 测试时长：10 分钟
- 教师切换频率：每 30 秒切换一次内容

### 轮询模式（旧方案）

| 指标 | 数值 |
|------|------|
| **平均延迟** | 500ms（轮询间隔的一半） |
| **最大延迟** | 1000ms（轮询间隔） |
| **API请求数** | 30学生 × 600次 = 18,000 次 |
| **服务器QPS** | 30 QPS（持续） |
| **网络流量** | ~180 MB（假设每次响应 10KB） |
| **CPU占用** | 中等（频繁查询数据库） |

### WebSocket 模式（新方案）

| 指标 | 数值 |
|------|------|
| **平均延迟** | <50ms（实时推送） |
| **最大延迟** | <100ms（网络延迟） |
| **广播消息数** | 20 次（每30秒1次 × 10分钟） |
| **服务器推送数** | 20 × 30 = 600 次 |
| **网络流量** | ~1.2 MB（只在有变化时推送） |
| **CPU占用** | 低（事件驱动，无轮询） |

### 性能提升

✅ **延迟降低：** 500ms → 50ms（**10倍提升**）  
✅ **请求减少：** 18,000 → 600（**减少 97%**）  
✅ **流量节省：** 180MB → 1.2MB（**节省 99%**）  
✅ **服务器负载：** 30 QPS → ~0 QPS（**几乎为0**）

---

## 故障处理

### 1. WebSocket 连接失败

**原因：**
- 网络问题
- 服务器重启
- Token 过期
- 防火墙/代理阻止 WebSocket

**处理：**

```typescript
try {
  await websocketService.connect(sessionId, token)
} catch (error) {
  // 自动降级到轮询
  console.warn('⚠️ WebSocket 连接失败，降级到轮询模式')
  startPolling()
}
```

### 2. 连接中断

**原因：**
- 网络波动
- 移动设备切换网络（WiFi ↔ 4G）
- 服务器维护

**处理：**

- **自动重连**：最多尝试 5 次，间隔 3 秒
- **断点续传**：重连后获取最新状态
- **用户提示**：显示"正在重连..."

```typescript
private reconnect(sessionId: number, token: string) {
  this.reconnectAttempts++
  
  if (this.reconnectAttempts > this.maxReconnectAttempts) {
    console.error('❌ 重连失败，降级到轮询')
    startPolling()
    return
  }
  
  setTimeout(() => {
    this.connect(sessionId, token)
  }, this.reconnectDelay)
}
```

### 3. 心跳超时

**检测：**

- 服务器端：30秒内未收到 `ping`，主动断开连接
- 客户端：30秒内未收到 `pong`，认为连接断开

**处理：**

- 客户端自动重连
- 服务器清理僵尸连接

### 4. 消息丢失

**原因：**
- 网络丢包
- 服务器异常

**防范：**

- 连接成功后，服务器发送完整初始状态
- 客户端每次重连后，主动请求最新状态
- 关键操作（如活动提交）使用 HTTP API 确认

---

## 部署注意事项

### 1. Nginx 配置（WebSocket 支持）

**文件：** `nginx.conf`

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # HTTP API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket（关键配置）
    location /api/v1/classroom-sessions/sessions/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置（WebSocket 长连接）
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }
}
```

### 2. Uvicorn 配置

**启动命令：**

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --ws auto \
  --timeout-keep-alive 65
```

**说明：**
- `--ws auto`：自动选择 WebSocket 实现（websockets 或 wsproto）
- `--timeout-keep-alive 65`：保持连接 65 秒（略大于心跳间隔 30 秒）

### 3. 防火墙配置

确保以下端口开放：

- **8000**：后端 API（包括 WebSocket）
- **80/443**：前端（Nginx）

### 4. SSL/TLS（生产环境必须）

WebSocket 在 HTTPS 网站上必须使用 WSS（WebSocket Secure）：

```typescript
// 前端自动检测协议
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
```

**Nginx SSL 配置：**

```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... WebSocket 配置 ...
}
```

### 5. 负载均衡（多实例部署）

**挑战：** WebSocket 是有状态连接，需要会话粘性（Sticky Session）

**解决方案 1：IP Hash（推荐）**

```nginx
upstream backend {
    ip_hash;  # 相同IP总是路由到相同后端
    server backend1:8000;
    server backend2:8000;
}
```

**解决方案 2：使用 Redis 作为消息中间件**

```python
# 使用 Redis Pub/Sub 广播消息到所有实例
import redis

redis_client = redis.Redis()

# 教师切换内容时
await redis_client.publish(
    f'session:{session_id}',
    json.dumps(message)
)

# 每个实例监听 Redis 频道
pubsub = redis_client.pubsub()
pubsub.subscribe(f'session:{session_id}')

for message in pubsub.listen():
    # 广播给本实例的连接
    await manager.broadcast_to_session(...)
```

---

## 监控和日志

### 1. 关键指标

**连接指标：**
- 当前在线连接数
- 连接成功率
- 平均连接时长
- 断线重连次数

**性能指标：**
- 消息延迟（P50, P95, P99）
- 消息丢失率
- 服务器资源占用（CPU、内存、网络）

**业务指标：**
- 课堂会话数量
- 平均学生在线数
- 内容切换频率

### 2. 日志格式

**连接日志：**

```
[2025-01-17 10:30:00] [INFO] WebSocket Connected: session=123, student=456, ip=192.168.1.100
[2025-01-17 10:35:00] [INFO] WebSocket Disconnected: session=123, student=456, duration=300s
```

**消息日志：**

```
[2025-01-17 10:32:15] [INFO] Message Sent: session=123, type=cell_changed, recipients=30
[2025-01-17 10:32:15] [DEBUG] Broadcast: session=123, display_cell_orders=[0,2,5]
```

**错误日志：**

```
[2025-01-17 10:33:00] [ERROR] WebSocket Send Failed: session=123, student=456, error="Connection closed"
[2025-01-17 10:33:00] [WARN] Auto Reconnect: student=456, attempt=1/5
```

### 3. Prometheus 指标（可选）

```python
from prometheus_client import Counter, Gauge, Histogram

# 连接数
websocket_connections = Gauge(
    'websocket_connections',
    'Current WebSocket connections',
    ['session_id']
)

# 消息数量
websocket_messages = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['type', 'direction']  # direction: sent/received
)

# 消息延迟
websocket_latency = Histogram(
    'websocket_message_latency_seconds',
    'WebSocket message latency'
)
```

---

## 测试清单

### 功能测试

- [ ] 学生能够成功连接 WebSocket
- [ ] 教师切换内容，学生端实时更新（<100ms）
- [ ] 多个学生同时在线，都能收到更新
- [ ] 页面刷新后能够重新连接
- [ ] 学生离开页面，连接正常断开
- [ ] 会话结束时，所有连接自动断开

### 异常测试

- [ ] 网络断开后，自动重连
- [ ] 重连失败，降级到轮询
- [ ] Token 过期，连接被拒绝
- [ ] 服务器重启，客户端能够重连
- [ ] 心跳超时，连接自动清理

### 性能测试

- [ ] 30 个学生同时在线，消息延迟 <100ms
- [ ] 100 个学生同时在线，服务器资源占用正常
- [ ] 教师频繁切换（每秒1次），系统稳定
- [ ] 长时间运行（2小时），无内存泄漏

### 兼容性测试

- [ ] Chrome（最新版）
- [ ] Firefox（最新版）
- [ ] Safari（最新版）
- [ ] Edge（最新版）
- [ ] 移动端浏览器（iOS Safari、Android Chrome）

---

## 相关文件

### 新增文件

**后端：**
- `backend/app/services/websocket_manager.py` - WebSocket 连接管理器
- `backend/app/api/v1/classroom_sessions.py` - 添加 WebSocket 端点

**前端：**
- `frontend/src/services/websocket.ts` - WebSocket 客户端服务
- `frontend/src/utils/auth.ts` - 认证工具函数

### 修改文件

**后端：**
- `backend/app/api/v1/classroom_sessions.py` - `navigate_to_cell()` 添加广播
- `backend/app/api/deps.py` - 添加 Token 认证辅助函数

**前端：**
- `frontend/src/composables/useClassroomSession.ts` - 使用 WebSocket
- `frontend/src/pages/Student/LessonView.vue` - 使用实时更新的数据
- `frontend/src/services/classroomSession.ts` - （可选）保留 HTTP API 用于降级

### 配置文件

- `nginx.conf` - 添加 WebSocket 支持
- `.env` - 添加 `VITE_USE_WEBSOCKET=true`

---

## 总结

### 核心优势

✅ **实时性**：教师切换内容，学生立即看到（<100ms 延迟）  
✅ **低负载**：服务器请求减少 97%，资源占用降低 90%+  
✅ **可扩展**：支持数百学生同时在线  
✅ **省电**：移动设备电量消耗显著降低  
✅ **用户体验**：更流畅的实时互动体验

### 风险控制

✅ **降级方案**：WebSocket 不可用时，自动降级到轮询  
✅ **灰度发布**：小范围验证后再全量上线  
✅ **监控完善**：实时监控连接状态和性能指标  
✅ **向后兼容**：保留 HTTP API，确保现有功能不受影响

### 下一步

1. **Phase 1（Week 1）：** 实现基础设施
2. **Phase 2（Week 2）：** 实现核心功能
3. **Phase 3（Week 3）：** 灰度发布，收集反馈
4. **Phase 4（Week 4）：** 全面上线，移除轮询

---

**文档版本：** v1.0  
**最后更新：** 2025-01-17  
**状态：** ✅ 设计完成，待实      // 降级到轮询模