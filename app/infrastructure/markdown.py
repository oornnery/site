import logging
import re
import threading
from pathlib import Path
from typing import Any

import markdown
import nh3
import yaml
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from pydantic import ValidationError

from app.core.config import settings
from app.infrastructure.about_parser import _parse_about_body
from app.infrastructure.gist_service import (
    _extract_gist_id,
    _extract_gist_markdown,
    _fetch_gist_comments,
    _fetch_gist_payload,
    _gist_comments_url,
)
from app.models.models import BlogPost, Project
from app.models.schemas import (
    AboutContent,
    AboutFrontmatter,
    BlogPostFrontmatter,
    ProjectFrontmatter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = PROJECT_ROOT / "content"
PROJECTS_DIR = CONTENT_DIR / "projects"
BLOG_DIR = CONTENT_DIR / "blog"
logger = logging.getLogger(__name__)


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


def _render_md(content: str) -> str:
    if not content:
        return ""
    return markdown.markdown(
        content,
        extensions=["fenced_code", "codehilite", "tables", "toc", "attr_list"],
    )


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


# Keep the private name as an alias for backward compatibility
_render_sanitized_markdown = render_sanitized_markdown


def _build_content_cache() -> TTLCache:
    ttl = settings.markdown_cache_ttl
    if ttl <= 0:
        ttl = 60 * 60 * 24 * 365
    return TTLCache(maxsize=16, ttl=ttl)


_content_cache: TTLCache = _build_content_cache()
_cache_lock = threading.Lock()


@cached(cache=_content_cache, key=lambda: hashkey("about"), lock=_cache_lock)
def load_about() -> AboutContent:
    about_path = CONTENT_DIR / "about.md"
    meta, body = _parse_frontmatter(about_path)
    frontmatter = AboutFrontmatter.model_validate(meta)
    body_markdown = body or "Content coming soon."
    parsed_about = _parse_about_body(body_markdown)
    logger.info(f"About content loaded from {about_path}.")
    return AboutContent(
        frontmatter=frontmatter,
        body_markdown=body_markdown,
        body_html=parsed_about["hero_html"],
        hero_markdown=parsed_about["hero_markdown"],
        hero_html=parsed_about["hero_html"],
        about_markdown=parsed_about["about_markdown"],
        about_html=parsed_about["about_html"],
        work_experience=parsed_about["work_experience"],
        education=parsed_about["education"],
        certificates=parsed_about["certificates"],
        skill_groups=parsed_about["skill_groups"],
    )


@cached(cache=_content_cache, key=lambda: hashkey("all_projects"), lock=_cache_lock)
def load_all_projects() -> tuple[Project, ...]:
    if not PROJECTS_DIR.exists():
        logger.info(
            f"Projects directory {PROJECTS_DIR} not found. Returning empty project list."
        )
        return ()

    projects: list[Project] = []
    for md_file in PROJECTS_DIR.glob("*.md"):
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
    logger.info(f"Loaded {len(sorted_projects)} project(s) from {PROJECTS_DIR}.")
    return tuple(sorted_projects)


def get_project_by_slug(slug: str) -> Project | None:
    project = next(
        (project for project in load_all_projects() if project.slug == slug), None
    )
    if project is None:
        logger.info(f"Project not found for slug={slug}.")
    return project


@cached(cache=_content_cache, key=lambda: hashkey("all_blog_posts"), lock=_cache_lock)
def load_all_blog_posts() -> tuple[BlogPost, ...]:
    if not BLOG_DIR.exists():
        logger.info(f"Blog directory {BLOG_DIR} not found. Returning empty post list.")
        return ()

    posts: list[BlogPost] = []
    for md_file in sorted(BLOG_DIR.glob("*.md"), reverse=True):
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
    logger.info(f"Loaded {len(sorted_posts)} blog post(s) from {BLOG_DIR}.")
    return tuple(sorted_posts)


def get_blog_post_by_slug(slug: str) -> BlogPost | None:
    post = next((post for post in load_all_blog_posts() if post.slug == slug), None)
    if post is None:
        logger.info(f"Blog post not found for slug={slug}.")
    return post
