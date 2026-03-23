from dataclasses import dataclass
from datetime import date as DateType

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    description: str
    content_html: str
    thumbnail: str = ""
    tags: tuple[str, ...] = ()
    tech_stack: tuple[str, ...] = ()
    github_url: str | None = None
    live_url: str | None = None
    date: DateType | None = None
    featured: bool = False


class ProjectFrontmatter(BaseModel):
    title: str = ""
    slug: str = ""
    description: str = ""
    thumbnail: str = ""
    tags: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    github_url: str = ""
    live_url: str = ""
    published_date: DateType | None = Field(default=None, alias="date")
    featured: bool = False

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
