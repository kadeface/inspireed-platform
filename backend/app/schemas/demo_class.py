from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DemoClassStatusResponse(BaseModel):
    school_ready: bool
    classroom_ready: bool
    school_id: Optional[int] = None
    classroom_id: Optional[int] = None
    school_name: str = "DEMO School"
    classroom_name: str = "Demo Class"
    target_accounts: int = 60
    ready_accounts: int = 0
    missing_usernames: List[str] = Field(default_factory=list)
    account_rule: str = "st01–st60 / password 123456"


class DemoClassProvisionResponse(BaseModel):
    school_id: int
    classroom_id: int
    created_users: int
    skipped_users: int
    created_memberships: int
    conflicts: List[str] = Field(default_factory=list)
    message: str


class DemoClassResetPasswordsResponse(BaseModel):
    reset_count: int
    message: str
