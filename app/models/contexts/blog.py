from pydantic import BaseModel, ConfigDict

from app.models.blog import BlogPost, BlogTag
from app.models.seo import SEOMeta


class BlogHomePageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    featured_posts: tuple[BlogPost, ...]
    recent_posts: tuple[BlogPost, ...]
    tags: tuple[BlogTag, ...]
    current_path: str = "/blog"


class BlogPostsPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    posts: tuple[BlogPost, ...]
    q: str = ""
    page: int = 1
    total_pages: int = 1
    current_path: str = "/blog"


class BlogPostDetailPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    post: BlogPost
    previous_post: BlogPost | None = None
    next_post: BlogPost | None = None
    read_time_minutes: int = 1
    current_path: str = "/blog"


class BlogTagsPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    tags: tuple[BlogTag, ...]
    posts: tuple[BlogPost, ...]
    selected_tag: str = ""
    page: int = 1
    total_pages: int = 1
    current_path: str = "/blog"
