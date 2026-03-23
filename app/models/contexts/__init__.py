from typing import TypeAlias

from app.models.contexts.about import AboutPageContext
from app.models.contexts.base import (
    ContactFormResult,
    ContactSubmissionResult,
    PageRenderData,
)
from app.models.contexts.blog import (
    BlogHomePageContext,
    BlogPostDetailPageContext,
    BlogPostsPageContext,
    BlogTagsPageContext,
)
from app.models.contexts.contact import ContactPageContext
from app.models.contexts.home import HomePageContext
from app.models.contexts.projects import (
    ProjectDetailPageContext,
    ProjectsListPageContext,
)

PageContext: TypeAlias = (
    HomePageContext
    | AboutPageContext
    | ProjectsListPageContext
    | ProjectDetailPageContext
    | ContactPageContext
    | BlogHomePageContext
    | BlogPostsPageContext
    | BlogPostDetailPageContext
    | BlogTagsPageContext
)

__all__ = [
    "AboutPageContext",
    "BlogHomePageContext",
    "BlogPostDetailPageContext",
    "BlogPostsPageContext",
    "BlogTagsPageContext",
    "ContactFormResult",
    "ContactPageContext",
    "ContactSubmissionResult",
    "HomePageContext",
    "PageContext",
    "PageRenderData",
    "ProjectDetailPageContext",
    "ProjectsListPageContext",
]
