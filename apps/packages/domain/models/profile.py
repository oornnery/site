from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    name: str = Field(default="Fabio Souza")
    location: str = Field(default="São Paulo, Brazil")
    short_bio: str = Field(default="Full-stack Developer")
    email: str = Field(default="contact@example.com")
    phone: str | None = None

    website: str | None = None
    github: str | None = None
    linkedin: str | None = None
    twitter: str | None = None

    social_links: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    about_summary: str = Field(default="")
    about_markdown: str = Field(default="")

    work_experience: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    education: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    certificates: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    updated_at: datetime = Field(default_factory=utc_now)
