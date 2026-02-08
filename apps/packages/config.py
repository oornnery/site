from __future__ import annotations

import secrets
import warnings

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Fabio Souza Site"
    ENV: str = "development"

    DATABASE_URL: str = "sqlite+aiosqlite:///./site.db"
    SEED_DB_ON_STARTUP: bool = True

    SECRET_KEY: str = ""

    PUBLIC_PORTFOLIO_URL: str = "http://localhost:8000"
    PUBLIC_BLOG_URL: str = "http://localhost:8001"
    PUBLIC_ADMIN_URL: str = "http://localhost:8002"

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    ALLOW_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8002",
    ]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

    RATE_LIMIT_PER_MINUTE: int = 60
    FORCE_HTTPS: bool = False
    REALTIME_ENABLED: bool = True

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if not value or value == "your-secret-key-here":
            generated = secrets.token_urlsafe(32)
            warnings.warn(
                "SECRET_KEY not set. Using generated key for development.",
                UserWarning,
                stacklevel=2,
            )
            return generated
        return value

    @field_validator("ALLOWED_HOSTS", mode="after")
    @classmethod
    def validate_allowed_hosts(cls, values: list[str]) -> list[str]:
        return [h for h in values if h != "*"]

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV.lower() == "development"

    @property
    def services(self) -> list[dict[str, str]]:
        return [
            {"id": "portfolio", "name": "Portfolio", "url": self.PUBLIC_PORTFOLIO_URL},
            {"id": "blog", "name": "Blog", "url": self.PUBLIC_BLOG_URL},
            {"id": "admin", "name": "Admin", "url": self.PUBLIC_ADMIN_URL},
        ]


settings = Settings()
