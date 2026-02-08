from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(index=True, unique=True, min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    content_md: str = Field(default="")
    content_html: str = Field(default="")
    image: str | None = None
    tech_stack: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    category: str = Field(default="other", max_length=50)
    github_url: str | None = None
    demo_url: str | None = None
    featured: bool = Field(default=False)
    github_stars: int = Field(default=0)
    github_forks: int = Field(default=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
