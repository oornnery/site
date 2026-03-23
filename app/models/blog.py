from dataclasses import dataclass
from datetime import date as DateType

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class BlogComment:
    author: str
    body: str
    created_at: str = ""
    profile_url: str = ""
    html_url: str = ""
    avatar_url: str = ""


@dataclass(frozen=True)
class BlogPost:
    slug: str
    title: str
    description: str
    content_html: str
    tags: tuple[str, ...] = ()
    author: str = ""
    discussion_url: str = ""
    gist_url: str = ""
    gist_id: str = ""
    comments: tuple[BlogComment, ...] = ()
    date: DateType | None = None
    featured: bool = False


@dataclass(frozen=True)
class BlogTag:
    name: str
    count: int


class BlogPostFrontmatter(BaseModel):
    title: str = ""
    slug: str = ""
    description: str = ""
    author: str = ""
    tags: list[str] = Field(default_factory=list)
    discussion_url: str = ""
    gist_url: str = ""
    gist_file: str = ""
    published_date: DateType | None = Field(default=None, alias="date")
    featured: bool = False
    draft: bool = False

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
