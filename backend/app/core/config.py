"""
应用配置管理
"""

import json
import logging
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

logger = logging.getLogger(__name__)


def parse_cors(v: Any) -> List[str]:
    """解析 CORS origins"""
    if isinstance(v, str):
        if not v or v.strip() == "":
            return []
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return v
    return []


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # 基础配置
    PROJECT_NAME: str = "InspireEd"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # API 文档开关 — 生产环境应设为 False
    DOCS_ENABLED: bool = True

    # 安全配置
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day (production-safe default)

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def ensure_secret_key(cls, v: Optional[str]) -> str:
        if not v or v == "your-secret-key-change-in-production":
            generated = secrets.token_urlsafe(64)
            logger.warning(
                "SECRET_KEY not set or using placeholder — "
                "auto-generated a random key. Set SECRET_KEY in .env for production."
            )
            return generated
        return v

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[List[str], BeforeValidator(parse_cors)] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    ALLOW_LAN_ACCESS: bool = True

    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "inspireed"
    POSTGRES_PORT: int = 5432

    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        user = values.get("POSTGRES_USER") or ""
        password = values.get("POSTGRES_PASSWORD") or ""
        host = values.get("POSTGRES_SERVER") or "localhost"
        port = values.get("POSTGRES_PORT") or 5432
        database = values.get("POSTGRES_DB") or ""
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "inspireed"
    MINIO_SECURE: bool = False

    # Kafka配置
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_LESSON_LOGS_TOPIC: str = "lesson_logs"
    KAFKA_QA_LOGS_TOPIC: str = "qa_logs"

    # JupyterHub配置
    JUPYTERHUB_URL: str = "http://localhost:8000"
    JUPYTERHUB_API_TOKEN: str = ""

    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7

    # 邮件配置（可选）
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # 超级管理员
    FIRST_SUPERUSER: str = "admin@inspireed.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    # 文件上传配置
    UPLOAD_DIR: str = "storage"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB


settings = Settings()
