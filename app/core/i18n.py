from __future__ import annotations

import logging
import threading
from typing import Any

import yaml
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from pydantic import BaseModel, Field

from app.core.config import PROJECT_ROOT, settings

logger = logging.getLogger(__name__)

I18N_DIR = PROJECT_ROOT / "content" / "i18n"


class NavLink(BaseModel):
    href: str
    label: str


class Palette(BaseModel):
    id: str
    label: str


class HomePageStrings(BaseModel):
    seo_title: str = "Home"
    seo_description: str = ""


class AboutPageStrings(BaseModel):
    seo_title: str = "About"
    seo_description_fallback: str = "About me"


class ProjectsPageStrings(BaseModel):
    title: str = "Projects"
    subtitle: str = ""
    seo_title: str = "Projects"
    seo_description: str = ""
    featured_label: str = "★ Featured"
    live_demo: str = "Live Demo"
    source_code: str = "Source Code"
    no_projects_found: str = "No projects found."


class BlogPageStrings(BaseModel):
    title: str = "Blog"
    subtitle: str = ""
    seo_title: str = "Blog"
    seo_description: str = ""
    posts_seo_title: str = "Blog Posts"
    posts_seo_description: str = ""
    tags_title: str = "Blog Tags"
    tags_description: str = ""
    tag_title_template: str = "Tag: {tag}"
    tag_description_template: str = "Posts tagged with {tag}."
    rss_description: str = ""
    featured_posts_heading: str = "Featured Posts"
    latest_posts_heading: str = "Latest Posts"
    tags_heading: str = "Tags"
    all_posts_title: str = "All Posts"
    all_posts_subtitle: str = "Every published article."
    posts_breadcrumb: str = "Posts"
    tags_breadcrumb: str = "Tags"
    browse_by_topic: str = "Browse posts by topic."
    search_placeholder: str = "Search posts by title, description, or tag..."
    min_read: str = "min read"
    featured_label: str = "Featured"
    continue_reading: str = "Continue Reading"
    view_all_posts_arrow: str = "View all posts →"
    previous_post: str = "← Previous"
    next_post: str = "Next →"
    all_tags_label: str = "All"
    no_posts_for_tag: str = "No posts found for this tag."
    no_posts_for_query: str = 'No posts found for "{q}".'
    no_posts_yet: str = "No posts published yet."


class ContactPageStrings(BaseModel):
    title: str = "Contact"
    subtitle: str = ""
    seo_title: str = "Contact"
    seo_description: str = ""
    form_heading: str = ""
    connect_heading: str = ""


class PageStrings(BaseModel):
    home: HomePageStrings = Field(default_factory=HomePageStrings)
    about: AboutPageStrings = Field(default_factory=AboutPageStrings)
    projects: ProjectsPageStrings = Field(default_factory=ProjectsPageStrings)
    blog: BlogPageStrings = Field(default_factory=BlogPageStrings)
    contact: ContactPageStrings = Field(default_factory=ContactPageStrings)


class ContactFormStrings(BaseModel):
    name_label: str = "Name"
    name_placeholder: str = ""
    email_label: str = "Email"
    email_placeholder: str = ""
    message_label: str = "Message"
    message_placeholder: str = ""
    submit_label: str = "Send Message"
    subject_default: str = "Contact form submission"


class FormStrings(BaseModel):
    contact: ContactFormStrings = Field(default_factory=ContactFormStrings)


class EmptyStates(BaseModel):
    projects: str = "No projects yet."
    blog_posts: str = "No blog posts yet."
    featured_posts: str = "No featured posts yet."
    recent_posts: str = "No recent posts yet."
    tags: str = "No tags available."
    search_results: str = "No results found."


class CtaStrings(BaseModel):
    view_resume: str = ""
    view_all_projects: str = ""
    view_all_posts: str = ""
    view_all_tags: str = ""


class ErrorStrings(BaseModel):
    csrf_invalid: str = "Invalid or expired security token. Please reload the page."
    form_invalid: str = "Please check the form and try again."
    content_type_unsupported: str = "Unsupported content type."
    notification_failed: str = (
        "Your message could not be delivered right now. Please try again later."
    )
    unexpected_state: str = "Unexpected contact submission state."
    not_found: str = "Page not found."
    rate_limited: str = "Too many requests. Please try again later."


class MessageStrings(BaseModel):
    contact_success: str = "Message sent successfully. Thank you for reaching out."


class CommonStrings(BaseModel):
    home: str = "Home"
    rss: str = "RSS"
    language_name: str = "English"
    scroll: str = "Scroll"
    on_this_page: str = "On this page"
    view: str = "View"


class ResumeStrings(BaseModel):
    title: str = "Resume"
    contact: str = "Contact"
    view_projects: str = "View Projects"
    work_experience: str = "Work Experience"
    education: str = "Education"
    certificates: str = "Certificates"
    skills: str = "Skills"
    about: str = "About"


class CommentsStrings(BaseModel):
    heading: str = "Comments"
    discussion_on: str = "Discussion for {title} lives on {source}."
    no_comments: str = "No comments yet. Start the discussion on {source}."
    not_available: str = "Comments are not available for this post yet."
    not_configured: str = "Comments via gist are not configured for this post yet."
    comment_on: str = "Comment on {source}"
    source_gist: str = "Gist"
    source_github: str = "GitHub"


class PaginationStrings(BaseModel):
    prev: str = "← Prev"
    next: str = "Next →"


class AriaStrings(BaseModel):
    open_main_menu: str = "Open main menu"
    select_palette: str = "Select color palette"
    select_language: str = "Select language"
    prev_featured: str = "Previous featured post"
    next_featured: str = "Next featured post"


class NotFoundPageStrings(BaseModel):
    label: str = "Error"
    code: str = "404"
    message: str = "The page you requested does not exist."
    action: str = "Return Home"


class MaintenancePageStrings(BaseModel):
    label: str = "Service Status"
    title: str = "Maintenance"
    retry: str = "Try Again"
    contact: str = "Contact"


class ErrorPageStrings(BaseModel):
    not_found: NotFoundPageStrings = Field(default_factory=NotFoundPageStrings)
    maintenance: MaintenancePageStrings = Field(default_factory=MaintenancePageStrings)


class Translations(BaseModel):
    nav: dict[str, Any] = Field(default_factory=dict)
    nav_links: list[NavLink] = Field(default_factory=list)
    palettes: list[Palette] = Field(default_factory=list)
    pages: PageStrings = Field(default_factory=PageStrings)
    form: FormStrings = Field(default_factory=FormStrings)
    empty_states: EmptyStates = Field(default_factory=EmptyStates)
    cta: CtaStrings = Field(default_factory=CtaStrings)
    errors: ErrorStrings = Field(default_factory=ErrorStrings)
    messages: MessageStrings = Field(default_factory=MessageStrings)
    common: CommonStrings = Field(default_factory=CommonStrings)
    resume: ResumeStrings = Field(default_factory=ResumeStrings)
    comments: CommentsStrings = Field(default_factory=CommentsStrings)
    pagination: PaginationStrings = Field(default_factory=PaginationStrings)
    aria: AriaStrings = Field(default_factory=AriaStrings)
    error_pages: ErrorPageStrings = Field(default_factory=ErrorPageStrings)

    @classmethod
    def from_yaml(cls, data: dict[str, Any]) -> Translations:
        nav_data = data.get("nav", {})
        return cls(
            nav=nav_data,
            nav_links=[NavLink(**link) for link in nav_data.get("links", [])],
            palettes=[Palette(**p) for p in data.get("palettes", [])],
            pages=PageStrings.model_validate(data.get("pages", {})),
            form=FormStrings.model_validate(data.get("form", {})),
            empty_states=EmptyStates.model_validate(data.get("empty_states", {})),
            cta=CtaStrings.model_validate(data.get("cta", {})),
            errors=ErrorStrings.model_validate(data.get("errors", {})),
            messages=MessageStrings.model_validate(data.get("messages", {})),
            common=CommonStrings.model_validate(data.get("common", {})),
            resume=ResumeStrings.model_validate(data.get("resume", {})),
            comments=CommentsStrings.model_validate(data.get("comments", {})),
            pagination=PaginationStrings.model_validate(data.get("pagination", {})),
            aria=AriaStrings.model_validate(data.get("aria", {})),
            error_pages=ErrorPageStrings.model_validate(data.get("error_pages", {})),
        )


def _build_i18n_cache() -> TTLCache:
    ttl = settings.markdown_cache_ttl
    if ttl <= 0:
        ttl = 60 * 60 * 24 * 365
    return TTLCache(maxsize=16, ttl=ttl)


_i18n_cache: TTLCache = _build_i18n_cache()
_i18n_lock = threading.Lock()


@cached(
    cache=_i18n_cache,
    key=lambda lang: hashkey("translations", lang),
    lock=_i18n_lock,
)
def load_translations(lang: str) -> Translations:
    yaml_path = I18N_DIR / f"{lang}.yaml"
    if not yaml_path.exists():
        logger.warning(f"Translation file not found: {yaml_path}")
        if lang != settings.default_language:
            return load_translations(settings.default_language)
        return Translations()

    try:
        text = yaml_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
    except (OSError, yaml.YAMLError):
        logger.exception(f"Failed to load translation file: {yaml_path}")
        if lang != settings.default_language:
            return load_translations(settings.default_language)
        return Translations()

    translations = Translations.from_yaml(data)
    logger.info(f"Translations loaded for lang={lang} from {yaml_path}.")
    return translations


def get_translations(lang: str | None = None) -> Translations:
    resolved_lang = lang or settings.default_language
    if resolved_lang not in settings.supported_languages:
        resolved_lang = settings.default_language
    return load_translations(resolved_lang)
