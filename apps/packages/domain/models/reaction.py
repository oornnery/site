from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class Reaction(SQLModel, table=True):
    __tablename__ = "reactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", index=True)
    type: str = Field(max_length=20)
    count: int = Field(default=0)
    created_at: datetime = Field(default_factory=utc_now)
