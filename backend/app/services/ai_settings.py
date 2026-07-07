"""
AI 配置服务
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import SystemSetting, User


AI_SETTINGS_KEY = "ai_runtime_settings"


@dataclass
class AIChannelRuntimeConfig:
    base_url: str
    model: str
    max_tokens: int
    temperature: float


@dataclass
class AIRuntimeConfig:
    text: AIChannelRuntimeConfig
    self_study_vision: AIChannelRuntimeConfig
    api_key_configured: bool
    api_key_source: str


def _build_channel_config(payload: dict[str, Any], defaults: AIChannelRuntimeConfig) -> AIChannelRuntimeConfig:
    return AIChannelRuntimeConfig(
        base_url=str(payload.get("base_url") or defaults.base_url),
        model=str(payload.get("model") or defaults.model),
        max_tokens=int(payload.get("max_tokens") or defaults.max_tokens),
        temperature=float(payload.get("temperature") if payload.get("temperature") is not None else defaults.temperature),
    )


class AISettingsService:
    def build_defaults(self) -> AIRuntimeConfig:
        base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1")
        default_model = getattr(settings, "DEFAULT_AI_MODEL", "gpt-3.5-turbo")
        max_tokens = int(getattr(settings, "AI_MAX_TOKENS", 20000))
        temperature = float(getattr(settings, "AI_TEMPERATURE", 0.7))

        text_defaults = AIChannelRuntimeConfig(
            base_url=base_url,
            model=default_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        vision_defaults = AIChannelRuntimeConfig(
            base_url=base_url,
            model=default_model,
            max_tokens=min(max_tokens, 2000),
            temperature=min(temperature, 0.7),
        )
        return AIRuntimeConfig(
            text=text_defaults,
            self_study_vision=vision_defaults,
            api_key_configured=bool(getattr(settings, "OPENAI_API_KEY", "")),
            api_key_source="env",
        )

    async def get_runtime_config(self, db: AsyncSession) -> AIRuntimeConfig:
        defaults = self.build_defaults()
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == AI_SETTINGS_KEY)
        )
        setting = result.scalar_one_or_none()
        if setting is None or not isinstance(setting.value_json, dict):
            return defaults

        payload = setting.value_json
        return AIRuntimeConfig(
            text=_build_channel_config(payload.get("text") or {}, defaults.text),
            self_study_vision=_build_channel_config(
                payload.get("self_study_vision") or {},
                defaults.self_study_vision,
            ),
            api_key_configured=defaults.api_key_configured,
            api_key_source=defaults.api_key_source,
        )

    async def update_runtime_config(
        self,
        db: AsyncSession,
        current_user: User,
        *,
        payload: dict[str, Any],
    ) -> AIRuntimeConfig:
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == AI_SETTINGS_KEY)
        )
        setting = result.scalar_one_or_none()
        if setting is None:
            setting = SystemSetting(
                key=AI_SETTINGS_KEY,
                description="AI runtime settings for assistant text channels and self-study vision channels.",
                value_json=payload,
                updated_by=current_user.id,
            )
            db.add(setting)
        else:
            setting.value_json = payload
            setting.updated_by = current_user.id

        await db.flush()
        return await self.get_runtime_config(db)

    def serialize(self, config: AIRuntimeConfig) -> dict[str, Any]:
        return {
            "text": {
                "base_url": config.text.base_url,
                "model": config.text.model,
                "max_tokens": config.text.max_tokens,
                "temperature": config.text.temperature,
            },
            "self_study_vision": {
                "base_url": config.self_study_vision.base_url,
                "model": config.self_study_vision.model,
                "max_tokens": config.self_study_vision.max_tokens,
                "temperature": config.self_study_vision.temperature,
            },
            "api_key_configured": config.api_key_configured,
            "api_key_source": config.api_key_source,
        }


ai_settings_service = AISettingsService()
