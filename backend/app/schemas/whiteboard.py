"""白板与课堂分组 Schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from typing import Literal

from pydantic import BaseModel, Field


class SessionGroupMemberOut(BaseModel):
    user_id: int
    group_index: int
    display_name: Optional[str] = None


class SessionGroupsResponse(BaseModel):
    session_id: int
    groups: List[Dict[str, Any]]
    members: List[SessionGroupMemberOut]


class SetupGroupsRequest(BaseModel):
    group_count: int = Field(..., ge=1, le=12)
    random_assign: bool = True


class PatchMemberGroupRequest(BaseModel):
    group_index: int = Field(..., ge=1, le=12)


class WhiteboardStateResponse(BaseModel):
    session_id: int
    cell_id: int
    document: Dict[str, Any]
    version: int
    updated_at: Optional[datetime] = None


class WhiteboardModeRequest(BaseModel):
    mode: Literal["setup", "collaborate", "locked"]


class WhiteboardOpMessage(BaseModel):
    cell_id: int
    op: Dict[str, Any]
