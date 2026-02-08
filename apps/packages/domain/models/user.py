from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str = Field(max_length=100)
    avatar_url: str | None = None
    provider: str = Field(default="email")
    provider_id: str | None = None
    hashed_password: str | None = None
    role: str = Field(default="admin")
    is_admin: bool = Field(default=True)
    is_banned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    last_login: datetime = Field(default_factory=utc_now)
