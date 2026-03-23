from pydantic import BaseModel, ConfigDict

from app.models.project import Project
from app.models.seo import SEOMeta


class ProjectsListPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    projects: tuple[Project, ...]
    all_tags: tuple[str, ...] = ()
    q: str = ""
    selected_tag: str = ""
    page: int = 1
    total_pages: int = 1
    current_path: str = "/projects"


class ProjectDetailPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    project: Project
    current_path: str = "/projects"
