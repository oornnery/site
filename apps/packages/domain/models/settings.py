from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from apps.packages.domain.models.common import utc_now


class Settings(SQLModel, table=True):
    __tablename__ = "settings"

    id: int = Field(default=1, primary_key=True)

    projects_enabled: bool = True
    blog_enabled: bool = True

    github_repo_owner: str | None = None
    github_repo_name: str | None = None
    github_posts_path: str = "posts"
    github_token: str | None = None
    github_enabled: bool = False

    home_background_url: str | None = None
    home_projects_count: int = 4
    home_posts_count: int = 4
    home_projects_featured_only: bool = False

    site_name: str = "Fabio Souza"
    site_description: str | None = None

    updated_at: datetime = Field(default_factory=utc_now)
