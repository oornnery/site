import logging
import math

from app.core.i18n import get_translations
from app.models.project import Project
from app.infrastructure.markdown import get_project_by_slug, load_all_projects
from app.services.seo import seo_for_page, seo_for_project
from app.models.contexts import (
    PageRenderData,
    ProjectDetailPageContext,
    ProjectsListPageContext,
)

logger = logging.getLogger(__name__)

_MAX_QUERY_LENGTH = 200
_MAX_TAG_LENGTH = 100


class ProjectsPageService:
    def build_list_page(
        self,
        *,
        q: str = "",
        tag: str = "",
        featured: bool | None = None,
        page: int = 1,
        page_size: int = 10,
        lang: str | None = None,
    ) -> PageRenderData:
        t = get_translations(lang)
        q = q[:_MAX_QUERY_LENGTH]
        tag = tag[:_MAX_TAG_LENGTH]

        all_projects = load_all_projects(lang)
        all_tags = tuple(sorted({t_tag for p in all_projects for t_tag in p.tags}))

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
                p
                for p in filtered
                if any(t_tag.lower() == tag_lower for t_tag in p.tags)
            )
        if featured is not None:
            filtered = tuple(p for p in filtered if p.featured == featured)

        total = len(filtered)
        total_pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        paginated = filtered[start : start + page_size]

        seo = seo_for_page(
            title=t.pages.projects.seo_title,
            description=t.pages.projects.seo_description,
            path="/projects",
            lang=lang or "",
        )
        logger.debug(
            f"Projects list use-case built with project_count={len(paginated)}"
            f" (q={q!r} tag={tag!r} featured={featured} page={page}/{total_pages})"
        )
        return PageRenderData(
            template="pages/projects/list.jinja",
            context=ProjectsListPageContext(
                seo=seo,
                projects=paginated,
                all_tags=all_tags,
                q=q,
                selected_tag=tag,
                page=page,
                total_pages=total_pages,
            ),
        )

    def get_project(self, slug: str, lang: str | None = None) -> Project | None:
        return get_project_by_slug(slug, lang)

    def build_detail_page(self, project: Project) -> PageRenderData:
        seo = seo_for_project(project)
        return PageRenderData(
            template="pages/projects/detail.jinja",
            context=ProjectDetailPageContext(
                seo=seo,
                project=project,
            ),
        )
