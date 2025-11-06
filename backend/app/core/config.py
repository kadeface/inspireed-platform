"""
应用配置管理
"""
import json
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors(v: Any) -> List[str]:
    """解析 CORS origins"""
    if isinstance(v, str):
        # 处理空字符串
        if not v or v.strip() == "":
            return []
        # 尝试作为 JSON 解析
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        # 否则按逗号分隔
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
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS - 允许局域网访问
    # 在生产环境中，应该设置具体的域名而不是使用通配符
    # 可以通过环境变量 BACKEND_CORS_ORIGINS 覆盖
    # 支持格式：逗号分隔 或 JSON数组
    # 例如：BACKEND_CORS_ORIGINS=http://localhost:5173,http://192.168.1.100:5173
    # 或：BACKEND_CORS_ORIGINS=["http://localhost:5173","http://192.168.1.100:5173"]
    BACKEND_CORS_ORIGINS: Annotated[List[str], BeforeValidator(parse_cors)] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        # 支持常见的局域网IP段 (192.168.x.x)
        # 如需添加更多IP，请通过环境变量配置
    ]
    
    # 是否允许局域网访问（开发模式）
    # 生产环境应设置为 False
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
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )
    
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
    JUPYTERHUB_API_TOKEN: str = "your-jupyterhub-token"
    
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
    
    # 文件上传配置 (MVP)
    UPLOAD_DIR: str = "storage"  # 上传文件存储目录
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB


settings = Settings()

