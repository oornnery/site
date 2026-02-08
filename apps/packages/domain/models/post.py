from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(index=True, unique=True, min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    content_md: str = Field(default="")
    content_html: str = Field(default="")
    image: str | None = None
    category: str = Field(default="general", max_length=50)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    draft: bool = Field(default=False)
    lang: str = Field(default="pt", max_length=5)
    reading_time: int = Field(default=0)
    views: int = Field(default=0)
    published_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
