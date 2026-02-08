from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now
from apps.packages.web.sanitize import sanitize_html


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", index=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", index=True)

    content: str = Field(min_length=1, max_length=2000)
    guest_name: str | None = Field(default=None, max_length=50)
    guest_email: str | None = Field(default=None, max_length=254)

    parent_id: uuid.UUID | None = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    is_deleted: bool = Field(default=False)
    is_flagged: bool = Field(default=False)

    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=500)

    @classmethod
    def build_content(cls, value: str) -> str:
        return sanitize_html(value.strip())
