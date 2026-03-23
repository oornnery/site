from pydantic import BaseModel, ConfigDict

from app.models.blog import BlogPost
from app.models.project import Project
from app.models.seo import SEOMeta


class HomePageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    featured: tuple[Project, ...]
    latest_posts: tuple[BlogPost, ...]
    csrf_token: str
    current_path: str = "/"
