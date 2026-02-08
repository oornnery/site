from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class PageView(SQLModel, table=True):
    __tablename__ = "pageviews"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    app: str = Field(index=True, max_length=20)
    path: str = Field(max_length=2048)
    referrer: str | None = Field(default=None, max_length=2048)
    ua: str | None = Field(default=None, max_length=512)
    ip_hash: str | None = Field(default=None, max_length=128)
    created_at: datetime = Field(default_factory=utc_now)
