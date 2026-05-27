"""白板 WebSocket 消息处理"""

import json
from datetime import datetime
from typing import Any, Optional

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.websocket_manager import manager as ws_manager
from app.services.whiteboard import (
    default_document,
    get_or_create_state,
    process_whiteboard_op,
)


async def _send(ws: WebSocket, event_type: str, data: dict) -> None:
    await ws.send_text(
        json.dumps(
            {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
            }
        )
    )


async def _broadcast(session_id: int, event_type: str, data: dict) -> None:
    msg = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }
    try:
        await ws_manager.broadcast_to_session(message=msg, session_id=session_id)
        await ws_manager.send_to_teacher(
            event=msg, scope="session", channel_id=session_id
        )
    except Exception:
        pass


async def handle_whiteboard_message(
    message: dict,
    *,
    session_id: int,
    user_id: int,
    is_teacher: bool,
    websocket: WebSocket,
    db: AsyncSession,
) -> bool:
    """处理白板相关 WS 消息，返回 True 表示已处理。"""
    message_type = message.get("type")
    if not message_type or not str(message_type).startswith("whiteboard."):
        return False

    data = message.get("data") or {}
    cell_id = data.get("cell_id")
    if cell_id is None:
        await _send(websocket, "whiteboard.error", {"detail": "缺少 cell_id"})
        return True

    cell_id = int(cell_id)

    if message_type == "whiteboard.subscribe":
        state = await get_or_create_state(db, session_id, cell_id)
        await _send(
            websocket,
            "whiteboard.sync",
            {
                "session_id": session_id,
                "cell_id": cell_id,
                "document": state.document or default_document(),
                "version": state.version,
            },
        )
        return True

    if message_type == "whiteboard.op":
        op = data.get("op")
        if not op:
            await _send(websocket, "whiteboard.error", {"detail": "缺少 op"})
            return True
        result, err = await process_whiteboard_op(
            db,
            session_id,
            cell_id,
            op,
            user_id=user_id,
            is_teacher=is_teacher,
        )
        if err:
            await _send(websocket, "whiteboard.error", {"detail": err, "cell_id": cell_id})
            return True
        payload = {"session_id": session_id, **result}
        await _broadcast(session_id, "whiteboard.op", payload)
        return True

    return False
