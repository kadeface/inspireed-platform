"""
AI 运行配置 Schema
"""

from pydantic import BaseModel, Field

# 与环境变量 AI_MAX_TOKENS 上限保持一致，避免默认值校验失败导致 500
AI_CHANNEL_MAX_TOKENS_LIMIT = 100_000


class AIChannelSettings(BaseModel):
    base_url: str = Field(..., min_length=1, max_length=500)
    model: str = Field(..., min_length=1, max_length=200)
    max_tokens: int = Field(..., ge=1, le=AI_CHANNEL_MAX_TOKENS_LIMIT)
    temperature: float = Field(..., ge=0.0, le=2.0)


class AISettingsResponse(BaseModel):
    text: AIChannelSettings
    self_study_vision: AIChannelSettings
    api_key_configured: bool
    api_key_source: str


class AISettingsUpdateRequest(BaseModel):
    text: AIChannelSettings
    self_study_vision: AIChannelSettings
