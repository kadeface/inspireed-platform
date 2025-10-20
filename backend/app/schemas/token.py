"""
Token Schemas
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token负载"""
    sub: Optional[int] = None

