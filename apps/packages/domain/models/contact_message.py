from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class ContactMessage(SQLModel, table=True):
    __tablename__ = "contact_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254, index=True)
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=10, max_length=5000)

    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)

    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=500)
