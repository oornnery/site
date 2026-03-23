import logging
from typing import Callable

from app.core.i18n import get_translations
from app.core.security import generate_csrf_token
from app.infrastructure.markdown import load_all_blog_posts, load_all_projects
from app.services.seo import seo_for_page
from app.models.contexts import HomePageContext, PageRenderData

logger = logging.getLogger(__name__)

_FEATURED_LIMIT = 3
_LATEST_POSTS_LIMIT = 3


class HomePageService:
    def __init__(
        self, csrf_token_factory: Callable[..., str] = generate_csrf_token
    ) -> None:
        self._csrf_token_factory = csrf_token_factory

    def build_page(
        self, *, user_agent: str = "", lang: str | None = None
    ) -> PageRenderData:
        t = get_translations(lang)
        all_projects = list(load_all_projects(lang))
        all_posts = list(load_all_blog_posts(lang))
        featured_projects = [project for project in all_projects if project.featured]
        non_featured_projects = [
            project for project in all_projects if not project.featured
        ]
        featured = (featured_projects + non_featured_projects)[:_FEATURED_LIMIT]
        latest_posts = all_posts[:_LATEST_POSTS_LIMIT]
        csrf_token = self._csrf_token_factory(user_agent=user_agent)
        seo = seo_for_page(
            title=t.pages.home.seo_title,
            description=t.pages.home.seo_description,
            path="/",
            lang=lang or "",
        )
        logger.debug(
            "Home use-case built with featured_count=%s total_projects=%s latest_posts=%s",
            len(featured),
            len(all_projects),
            len(latest_posts),
        )
        return PageRenderData(
            template="pages/home.jinja",
            context=HomePageContext(
                seo=seo,
                featured=tuple(featured),
                latest_posts=tuple(latest_posts),
                csrf_token=csrf_token,
            ),
        )
