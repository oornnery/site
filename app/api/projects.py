import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_projects_page_service
from app.core.rendering import is_htmx, render_fragment, render_page
from app.services import ProjectsPageService
from app.services.types import ProjectsListPageContext

router = APIRouter(prefix="/projects", tags=["projects"])
logger = logging.getLogger(__name__)

ProjectsPageServiceDep = Annotated[
    ProjectsPageService, Depends(get_projects_page_service)
]


@router.get("", response_class=HTMLResponse)
async def projects_list(
    request: Request,
    page_service: ProjectsPageServiceDep,
    q: Annotated[str, Query()] = "",
    tag: Annotated[str, Query()] = "",
    page: Annotated[int, Query(ge=1)] = 1,
) -> HTMLResponse:
    page_data = page_service.build_list_page(q=q, tag=tag, page=page)
    logger.debug("Projects list page rendered.")
    if is_htmx(request):
        ctx = page_data.context
        if not isinstance(ctx, ProjectsListPageContext):
            raise TypeError(
                f"Expected ProjectsListPageContext, got {type(ctx).__name__}"
            )
        return render_fragment(
            "@features/projects/projects-list-fragment.jinja",
            projects=ctx.projects,
        )
    return render_page(page_data)


@router.get("/{slug}", response_class=HTMLResponse)
async def project_detail(
    slug: Annotated[str, Path()],
    page_service: ProjectsPageServiceDep,
) -> HTMLResponse:
    project = page_service.get_project(slug)
    if project is None:
        logger.info(f"Project detail not found for slug={slug}.")
        raise HTTPException(status_code=404, detail="Project not found")
    page = page_service.build_detail_page(project)
    logger.debug(f"Project detail page rendered for slug={slug}.")
    return render_page(page)
