import logging

from app.models.models import Project
from app.infrastructure.markdown import get_project_by_slug, load_all_projects
from app.services.seo import seo_for_page, seo_for_project
from app.services.types import (
    PageRenderData,
    ProjectDetailPageContext,
    ProjectsListPageContext,
)

logger = logging.getLogger(__name__)


class ProjectsPageService:
    def build_list_page(
        self, *, q: str = "", tag: str = "", featured: bool | None = None
    ) -> PageRenderData:
        all_projects = load_all_projects()
        all_tags = tuple(sorted({t for p in all_projects for t in p.tags}))

        filtered = all_projects
        if q:
            q_lower = q.lower()
            filtered = tuple(
                p
                for p in filtered
                if q_lower in p.title.lower() or q_lower in p.description.lower()
            )
        if tag:
            tag_lower = tag.lower()
            filtered = tuple(
                p for p in filtered if any(t.lower() == tag_lower for t in p.tags)
            )
        if featured is not None:
            filtered = tuple(p for p in filtered if p.featured == featured)

        seo = seo_for_page(
            title="Projects",
            description="My projects and selected work.",
            path="/projects",
        )
        logger.debug(
            f"Projects list use-case built with project_count={len(filtered)}"
            f" (q={q!r} tag={tag!r} featured={featured})"
        )
        return PageRenderData(
            template="pages/projects/list.jinja",
            context=ProjectsListPageContext(
                seo=seo,
                projects=filtered,
                all_tags=all_tags,
                q=q,
                selected_tag=tag,
            ),
        )

    def get_project(self, slug: str) -> Project | None:
        return get_project_by_slug(slug)

    def build_detail_page(self, project: Project) -> PageRenderData:
        seo = seo_for_project(project)
        return PageRenderData(
            template="pages/projects/detail.jinja",
            context=ProjectDetailPageContext(
                seo=seo,
                project=project,
            ),
        )
