from __future__ import annotations

from functools import lru_cache
from typing import Annotated
from urllib.parse import quote

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DB_CHARSET = "utf8mb4"


class Settings(BaseSettings):
    """应用配置，全部通过环境变量或 .env 文件注入。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- MySQL ----
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "temperature"

    # ---- 缓存 ----
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # ---- 雪花 ID ----
    snowflake_worker_id: int = 1

    # ---- 鉴权 ----
    jwt_secret_key: str = Field(min_length=16)
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 7

    # ---- 邮箱验证码 ----
    email_code_expire_seconds: int = 300
    email_code_resend_seconds: int = 60
    email_code_max_attempts: int = 5

    # ---- 登录失败锁定 ----
    login_max_failures: int = 5
    login_lock_seconds: int = 900

    # ---- SMTP ----
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_ssl: bool = True
    smtp_from_email: str = ""

    # ---- 服务 ----
    api_prefix: str = "/api"
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def access_token_expire_seconds(self) -> int:
        return self.access_token_expire_minutes * 60

    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.refresh_token_expire_days * 86400

    @property
    def database_url(self) -> str:
        """异步 MySQL 连接串（由上面的分项配置拼装）。"""
        return (
            f"mysql+asyncmy://{quote(self.mysql_user, safe='')}:"
            f"{quote(self.mysql_password, safe='')}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset={DB_CHARSET}"
        )

    @property
    def redis_url(self) -> str:
        """Redis 连接串（由上面的分项配置拼装）。"""
        auth = f":{quote(self.redis_password, safe='')}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
