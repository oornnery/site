import logging
import re
import threading
from pathlib import Path
from typing import Any

import mistune
import nh3
import yaml
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from pydantic import ValidationError

from app.core.config import PROJECT_ROOT, settings
from app.infrastructure.gist import (
    _extract_gist_id,
    _extract_gist_markdown,
    _fetch_gist_comments,
    _fetch_gist_payload,
    _gist_comments_url,
)
from app.models.about import AboutContent, AboutFrontmatter
from app.models.blog import BlogPost, BlogPostFrontmatter
from app.models.project import Project, ProjectFrontmatter

CONTENT_DIR = PROJECT_ROOT / "content"
PROJECTS_DIR = CONTENT_DIR / "projects"
BLOG_DIR = CONTENT_DIR / "blog"
logger = logging.getLogger(__name__)


def _content_dir_for_lang(lang: str) -> Path:
    """Return the language-specific content directory, falling back to legacy paths."""
    lang_dir = CONTENT_DIR / lang
    if lang_dir.exists():
        return lang_dir
    return CONTENT_DIR


def _parse_frontmatter(filepath: Path) -> tuple[dict[str, Any], str]:
    if not filepath.exists():
        return {}, ""

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError:
        logger.exception(f"Failed to read markdown file: {filepath}")
        return {}, ""

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            _, fm, body = parts
            try:
                meta = yaml.safe_load(fm) or {}
            except yaml.YAMLError:
                logger.exception(f"Invalid YAML frontmatter in file: {filepath}")
                meta = {}
            return meta, body.strip()
    return {}, text.strip()


_mistune_renderer = mistune.create_markdown(
    plugins=[
        "mistune.plugins.table.table",
        "mistune.plugins.formatting.strikethrough",
    ],
)


def _render_md(content: str) -> str:
    if not content:
        return ""
    result = _mistune_renderer(content)
    return str(result)


_NH3_ALLOWED_TAGS = {
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}

_NH3_ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {"href", "title", "target"},
    "div": {"class"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "ol": {"start"},
    "span": {"class"},
    "table": {"class"},
    "code": {"class"},
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align", "scope"},
}

_NH3_URL_SCHEMES = {"http", "https", "mailto"}


def _sanitize_html(html: str) -> str:
    return nh3.clean(
        html,
        tags=_NH3_ALLOWED_TAGS,
        attributes=_NH3_ALLOWED_ATTRS,
        url_schemes=_NH3_URL_SCHEMES,
        link_rel="noopener noreferrer",
        strip_comments=True,
    )


def _extract_description(markdown_body: str) -> str:
    lines = [line.strip() for line in markdown_body.splitlines() if line.strip()]
    for line in lines:
        if line.startswith(("#", "-", "*", ">")):
            continue
        compact = re.sub(r"\s+", " ", line).strip()
        if compact:
            return compact[:157].rstrip() + "..." if len(compact) > 160 else compact
    return "Post content."


def render_sanitized_markdown(content: str) -> str:
    if not content.strip():
        return ""
    return _sanitize_html(_render_md(content))


def _build_content_cache() -> TTLCache:
    ttl = settings.markdown_cache_ttl
    if ttl <= 0:
        ttl = 60 * 60 * 24 * 365
    return TTLCache(maxsize=64, ttl=ttl)


_content_cache: TTLCache = _build_content_cache()
_cache_lock = threading.Lock()


@cached(
    cache=_content_cache,
    key=lambda lang=None: hashkey("about", lang or settings.default_language),
    lock=_cache_lock,
)
def load_about(lang: str | None = None) -> AboutContent:
    resolved_lang = lang or settings.default_language
    base = _content_dir_for_lang(resolved_lang)
    about_path = base / "about.md"
    if not about_path.exists():
        about_path = CONTENT_DIR / "about.md"
    meta, body = _parse_frontmatter(about_path)
    frontmatter = AboutFrontmatter.model_validate(meta)
    body_markdown = body or "Content coming soon."

    hero_markdown, _, about_markdown = body_markdown.partition("## About")
    hero_markdown = hero_markdown.strip()
    about_markdown = about_markdown.strip()

    hero_html = render_sanitized_markdown(hero_markdown)
    logger.info(f"About content loaded from {about_path} (lang={resolved_lang}).")
    return AboutContent(
        frontmatter=frontmatter,
        body_markdown=body_markdown,
        body_html=render_sanitized_markdown(body_markdown),
        hero_markdown=hero_markdown,
        hero_html=hero_html,
        about_markdown=about_markdown,
        about_html=render_sanitized_markdown(about_markdown),
        work_experience=frontmatter.work_experience,
        education=frontmatter.education,
        certificates=frontmatter.certificates,
        skill_groups=frontmatter.skill_groups,
    )


@cached(
    cache=_content_cache,
    key=lambda lang=None: hashkey("all_projects", lang or settings.default_language),
    lock=_cache_lock,
)
def load_all_projects(lang: str | None = None) -> tuple[Project, ...]:
    resolved_lang = lang or settings.default_language
    base = _content_dir_for_lang(resolved_lang)
    projects_dir = base / "projects"
    if not projects_dir.exists():
        projects_dir = CONTENT_DIR / "projects"
    if not projects_dir.exists():
        logger.info(
            f"Projects directory {projects_dir} not found. Returning empty project list."
        )
        return ()

    projects: list[Project] = []
    for md_file in projects_dir.glob("*.md"):
        meta, body = _parse_frontmatter(md_file)
        try:
            frontmatter = ProjectFrontmatter.model_validate(meta)
        except ValidationError:
            logger.exception(f"Invalid project frontmatter in file: {md_file}")
            continue

        resolved_title = frontmatter.title or md_file.stem.replace("-", " ").title()
        resolved_slug = frontmatter.slug or md_file.stem
        projects.append(
            Project(
                slug=resolved_slug,
                title=resolved_title,
                description=frontmatter.description,
                content_html=_sanitize_html(_render_md(body)),
                thumbnail=frontmatter.thumbnail,
                tags=tuple(frontmatter.tags),
                tech_stack=tuple(frontmatter.tech_stack),
                github_url=frontmatter.github_url or None,
                live_url=frontmatter.live_url or None,
                date=frontmatter.published_date,
                featured=frontmatter.featured,
            )
        )

    sorted_projects = sorted(
        projects,
        key=lambda p: (p.date is not None, p.date, p.slug),
        reverse=True,
    )
    logger.info(
        f"Loaded {len(sorted_projects)} project(s) from {projects_dir} (lang={resolved_lang})."
    )
    return tuple(sorted_projects)


def get_project_by_slug(slug: str, lang: str | None = None) -> Project | None:
    project = next(
        (project for project in load_all_projects(lang) if project.slug == slug), None
    )
    if project is None:
        logger.info(f"Project not found for slug={slug}.")
    return project


@cached(
    cache=_content_cache,
    key=lambda lang=None: hashkey("all_blog_posts", lang or settings.default_language),
    lock=_cache_lock,
)
def load_all_blog_posts(lang: str | None = None) -> tuple[BlogPost, ...]:
    resolved_lang = lang or settings.default_language
    base = _content_dir_for_lang(resolved_lang)
    blog_dir = base / "blog"
    if not blog_dir.exists():
        blog_dir = CONTENT_DIR / "blog"
    if not blog_dir.exists():
        logger.info(f"Blog directory {blog_dir} not found. Returning empty post list.")
        return ()

    posts: list[BlogPost] = []
    for md_file in sorted(blog_dir.glob("*.md"), reverse=True):
        meta, body = _parse_frontmatter(md_file)
        try:
            frontmatter = BlogPostFrontmatter.model_validate(meta)
        except ValidationError:
            logger.exception(f"Invalid blog post frontmatter in file: {md_file}")
            continue

        if frontmatter.draft and not settings.debug:
            logger.info(f"Skipping draft blog post in file: {md_file}")
            continue

        resolved_title = frontmatter.title or md_file.stem.replace("-", " ").title()
        resolved_slug = frontmatter.slug or md_file.stem
        gist_url = frontmatter.gist_url.strip()
        gist_id = _extract_gist_id(gist_url)
        if gist_url and not gist_id:
            logger.warning(
                f"Invalid gist_url for blog post slug={resolved_slug}: gist_url={gist_url}"
            )

        body_markdown = body.strip()
        if not body_markdown and gist_id:
            gist_payload = _fetch_gist_payload(gist_id)
            if gist_payload is not None:
                body_markdown = _extract_gist_markdown(
                    gist_payload, frontmatter.gist_file
                )
        if not body_markdown:
            body_markdown = "Content coming soon."

        resolved_description = (
            frontmatter.description.strip()
            if frontmatter.description.strip()
            else _extract_description(body_markdown)
        )
        comments = _fetch_gist_comments(gist_id) if gist_id else ()
        resolved_discussion_url = frontmatter.discussion_url.strip()
        if gist_url:
            resolved_discussion_url = _gist_comments_url(gist_url)

        posts.append(
            BlogPost(
                slug=resolved_slug,
                title=resolved_title,
                description=resolved_description,
                content_html=_sanitize_html(_render_md(body_markdown)),
                tags=tuple(frontmatter.tags),
                author=frontmatter.author.strip(),
                discussion_url=resolved_discussion_url,
                gist_url=gist_url,
                gist_id=gist_id,
                comments=comments,
                date=frontmatter.published_date,
                featured=frontmatter.featured,
            )
        )

    sorted_posts = sorted(
        posts,
        key=lambda post: (post.date is not None, post.date, post.slug),
        reverse=True,
    )
    logger.info(
        f"Loaded {len(sorted_posts)} blog post(s) from {blog_dir} (lang={resolved_lang})."
    )
    return tuple(sorted_posts)


def get_blog_post_by_slug(slug: str, lang: str | None = None) -> BlogPost | None:
    post = next((post for post in load_all_blog_posts(lang) if post.slug == slug), None)
    if post is None:
        logger.info(f"Blog post not found for slug={slug}.")
    return post
