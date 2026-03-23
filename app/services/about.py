import logging

from app.core.i18n import get_translations
from app.infrastructure.markdown import load_about
from app.services.seo import seo_for_page
from app.models.contexts import AboutPageContext, PageRenderData

logger = logging.getLogger(__name__)


class AboutPageService:
    def build_page(self, lang: str | None = None) -> PageRenderData:
        t = get_translations(lang)
        about_content = load_about(lang)
        frontmatter = about_content.frontmatter
        seo = seo_for_page(
            title=t.pages.about.seo_title,
            description=frontmatter.description
            or t.pages.about.seo_description_fallback,
            path="/about",
            lang=lang or "",
        )
        logger.debug(
            f"About use-case built with html_length={len(about_content.body_html)}"
        )
        return PageRenderData(
            template="pages/about.jinja",
            context=AboutPageContext(
                seo=seo,
                meta=frontmatter,
                hero_html=about_content.hero_html,
                about_html=about_content.about_html,
                work_experience=tuple(about_content.work_experience),
                education=tuple(about_content.education),
                certificates=tuple(about_content.certificates),
                skill_groups=tuple(about_content.skill_groups),
            ),
        )
