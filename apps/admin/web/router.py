from __future__ import annotations

import asyncio
import json
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from apps.packages.db import get_session
from apps.packages.db.session import async_session_factory
from apps.packages.domain.models import AuditLog, Comment, PageView, Post, Project, Settings, User
from apps.packages.security import clear_auth_cookie, get_current_user_optional, set_auth_cookie
from apps.packages.services import (
    AnalyticsService,
    AuthService,
    BlogService,
    CommentService,
    ContactMessageService,
    ProfileService,
    ProjectService,
)

router = APIRouter(tags=["admin-web"])

UPLOADS_ROOT_DIR = Path(__file__).resolve().parents[3] / "apps" / "packages" / "static" / "uploads"
SOCIAL_UPLOAD_DIR = UPLOADS_ROOT_DIR / "social"
FILES_UPLOAD_DIR = UPLOADS_ROOT_DIR / "files"
SOCIAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FILES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _save_social_icon(upload) -> str | None:
    if not upload or not getattr(upload, "filename", None):
        return None
    suffix = Path(upload.filename).suffix.lower()
    allowed = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
    ext = suffix if suffix in allowed else ""
    filename = f"{uuid4().hex}{ext}"
    target = SOCIAL_UPLOAD_DIR / filename
    content = await upload.read()
    if not content:
        return None
    target.write_bytes(content)
    return f"/static/uploads/social/{filename}"


async def _save_uploaded_file(upload, *, folder: Path, web_prefix: str) -> tuple[str, int] | None:
    if not upload or not getattr(upload, "filename", None):
        return None
    content = await upload.read()
    if not content:
        return None

    suffix = Path(upload.filename).suffix.lower()
    safe_ext = suffix if suffix and len(suffix) <= 10 else ""
    filename = f"{uuid4().hex}{safe_ext}"
    target = folder / filename
    target.write_bytes(content)
    return f"{web_prefix}/{filename}", len(content)


def _as_bool(raw) -> bool:
    if isinstance(raw, bool):
        return raw
    if raw is None:
        return False
    return str(raw).lower() in {"true", "on", "1", "yes"}


def _parse_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _as_int(raw, *, default: int, min_value: int, max_value: int) -> int:
    try:
        value = int(str(raw))
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, value))


def _clean_optional_url(raw) -> str | None:
    value = str(raw or "").strip()
    if not value:
        return None
    if value.lower() in {"none", "null"}:
        return None
    return value


def _clean_optional_text(raw) -> str | None:
    value = str(raw or "").strip()
    if not value:
        return None
    if value.lower() in {"none", "null"}:
        return None
    return value


def _clean_optional_icon_url(raw) -> str | None:
    value = _clean_optional_text(raw)
    if not value:
        return None
    lower = value.lower()
    if lower.startswith(("http://", "https://", "/static/", "/uploads/", "data:image/")):
        return value
    return None


def _infer_social_icon(*, title: str, url: str) -> str:
    hint = f"{title} {url}".lower()
    if "github" in hint:
        return "github"
    if "linkedin" in hint:
        return "linkedin"
    if "twitter" in hint or "x.com" in hint or hint.strip() == "x":
        return "twitter"
    if "mailto:" in hint or "email" in hint or "@" in url:
        return "email"
    if "tel:" in hint or "phone" in hint:
        return "phone"
    return "globe"


def _toast_redirect(url: str, message: str, tone: str = "success") -> RedirectResponse:
    sep = "&" if "?" in url else "?"
    toast_url = f"{url}{sep}toast={quote(message)}&tone={quote(tone)}"
    return RedirectResponse(url=toast_url, status_code=303)


def _redirect_login() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)


def _is_admin(user) -> bool:
    return bool(user and user.is_admin)


def _human_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


async def _build_overview(session: AsyncSession, days: int) -> tuple[dict, dict]:
    summary = await AnalyticsService(session).pageviews_summary(days=days)
    total_visitors = sum(summary["by_app"].values())
    overview = {
        "total_visitors": total_visitors,
        "new_visitors": total_visitors,
        "unique_visitors": total_visitors,
        "total_pageviews": summary["total_pageviews"],
        "total_events": summary["total_pageviews"],
        "active_sessions": 0,
        "period_days": days,
    }
    return overview, summary


@router.get("/", name="admin.root")
async def root(user=Depends(get_current_user_optional)):
    return RedirectResponse(url="/admin" if _is_admin(user) else "/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None, user=Depends(get_current_user_optional)):
    if _is_admin(user):
        return RedirectResponse(url="/admin", status_code=302)
    catalog = request.app.state.catalog
    return catalog.render("pages/Login.jinja", request=request, user=user, error=error or "")


@router.post("/login")
async def login_submit(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    form = await request.form()
    email = str(form.get("email") or "").strip()
    password = str(form.get("password") or "").strip()

    service = AuthService(session)
    user = await service.authenticate_user(email, password)
    if not user:
        return RedirectResponse(url="/login?error=Email+ou+senha+incorretos", status_code=303)

    response = RedirectResponse(url="/admin", status_code=303)
    set_auth_cookie(response, service.create_token_for_user(user))

    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()

    return response


@router.get("/logout")
async def logout_page():
    response = RedirectResponse(url="/", status_code=302)
    clear_auth_cookie(response)
    return response


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)

    total_posts = (await session.execute(select(func.count(Post.id)))).scalar() or 0
    total_projects = (await session.execute(select(func.count(Project.id)))).scalar() or 0
    recent_pageviews = (
        await session.execute(select(func.count(PageView.id)).where(PageView.created_at >= last_7_days))
    ).scalar() or 0

    recent_visitors = (
        await session.execute(
            select(func.count(func.distinct(PageView.ip_hash))).where(PageView.created_at >= last_7_days)
        )
    ).scalar() or 0

    stats = {
        "total_posts": total_posts,
        "total_projects": total_projects,
        "recent_visitors": recent_visitors,
        "recent_pageviews": recent_pageviews,
    }

    catalog = request.app.state.catalog
    return catalog.render("admin/Dashboard.jinja", request=request, user=user, stats=stats)


@router.get("/admin/blog", response_class=HTMLResponse)
async def admin_blog_list(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    posts = await BlogService(session).get_posts(include_drafts=True, limit=300)
    catalog = request.app.state.catalog
    return catalog.render("admin/BlogList.jinja", request=request, user=user, posts=posts)


@router.get("/admin/blog/new", response_class=HTMLResponse)
async def admin_blog_new(request: Request, user=Depends(get_current_user_optional)):
    if not _is_admin(user):
        return _redirect_login()

    catalog = request.app.state.catalog
    return catalog.render("admin/BlogEdit.jinja", request=request, user=user, post=None, errors={})


@router.post("/admin/blog/new", response_class=HTMLResponse)
async def admin_blog_create(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    form = await request.form()
    payload = {
        "title": str(form.get("title") or "").strip(),
        "slug": str(form.get("slug") or "").strip(),
        "description": str(form.get("description") or "").strip(),
        "content_md": str(form.get("content") or "").strip(),
        "image": _clean_optional_url(form.get("image")),
        "category": str(form.get("category") or "").strip() or "general",
        "reading_time": int(form.get("reading_time") or 5),
        "tags": _parse_list(str(form.get("tags") or "")),
        "draft": _as_bool(form.get("draft")),
        "lang": str(form.get("lang") or "pt").strip(),
    }

    if not payload["title"] or not payload["slug"]:
        catalog = request.app.state.catalog
        return HTMLResponse(
            catalog.render(
                "admin/BlogEdit.jinja",
                request=request,
                user=user,
                post=None,
                errors={"title": "Title and slug are required"},
                form_data=payload,
                toast_message="Title and slug are required",
                toast_tone="error",
            ),
            status_code=400,
        )

    post = await BlogService(session).create_post(payload)
    session.add(AuditLog(actor_user_id=user.id, action="create", entity="post", entity_id=str(post.id), payload_json={"title": post.title, "slug": post.slug}))
    await session.commit()

    return _toast_redirect("/admin/blog", "Post created")


@router.get("/admin/blog/{post_id}", response_class=HTMLResponse)
async def admin_blog_edit(
    post_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    post = await BlogService(session).get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    catalog = request.app.state.catalog
    return catalog.render("admin/BlogEdit.jinja", request=request, user=user, post=post, errors={})


@router.post("/admin/blog/{post_id}", response_class=HTMLResponse)
async def admin_blog_update(
    post_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    service = BlogService(session)
    post = await service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    form = await request.form()
    payload = {
        "title": str(form.get("title") or "").strip(),
        "slug": str(form.get("slug") or "").strip(),
        "description": str(form.get("description") or "").strip(),
        "content_md": str(form.get("content") or "").strip(),
        "image": _clean_optional_url(form.get("image")),
        "category": str(form.get("category") or "").strip() or "general",
        "reading_time": int(form.get("reading_time") or 5),
        "tags": _parse_list(str(form.get("tags") or "")),
        "draft": _as_bool(form.get("draft")),
        "lang": str(form.get("lang") or "pt").strip(),
    }

    updated = await service.update_post(post, payload)
    session.add(AuditLog(actor_user_id=user.id, action="update", entity="post", entity_id=str(updated.id), payload_json={"title": updated.title, "slug": updated.slug}))
    await session.commit()

    return _toast_redirect("/admin/blog", "Post updated")


@router.post("/admin/blog/{post_id}/delete")
async def admin_blog_delete(
    post_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    service = BlogService(session)
    post = await service.get_post_by_id(post_id)
    if post:
        await service.delete_post(post)
        session.add(AuditLog(actor_user_id=user.id, action="delete", entity="post", entity_id=str(post_id), payload_json={"slug": post.slug}))
        await session.commit()

    return _toast_redirect("/admin/blog", "Post deleted")


@router.get("/admin/projects", response_class=HTMLResponse)
async def admin_projects_list(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    projects = await ProjectService(session).get_projects(limit=500)
    catalog = request.app.state.catalog
    return catalog.render("admin/ProjectsList.jinja", request=request, user=user, projects=projects)


@router.get("/admin/projects/new", response_class=HTMLResponse)
async def admin_project_new(request: Request, user=Depends(get_current_user_optional)):
    if not _is_admin(user):
        return _redirect_login()

    catalog = request.app.state.catalog
    return catalog.render("admin/ProjectEdit.jinja", request=request, user=user, project=None, errors={})


@router.post("/admin/projects/new", response_class=HTMLResponse)
async def admin_project_create(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    form = await request.form()
    payload = {
        "title": str(form.get("title") or "").strip(),
        "slug": str(form.get("slug") or "").strip(),
        "description": str(form.get("description") or "").strip(),
        "content_md": str(form.get("content") or "").strip(),
        "image": _clean_optional_url(form.get("image")),
        "category": str(form.get("category") or "").strip() or "other",
        "github_url": _clean_optional_url(form.get("github_url")),
        "demo_url": _clean_optional_url(form.get("demo_url")),
        "featured": _as_bool(form.get("featured")),
        "tech_stack": _parse_list(str(form.get("tech_stack") or "")),
    }

    project = await ProjectService(session).create_project(payload)
    session.add(AuditLog(actor_user_id=user.id, action="create", entity="project", entity_id=str(project.id), payload_json={"title": project.title, "slug": project.slug}))
    await session.commit()

    return _toast_redirect("/admin/projects", "Project created")


@router.get("/admin/projects/{project_id}", response_class=HTMLResponse)
async def admin_project_edit(
    project_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    project = await ProjectService(session).get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    catalog = request.app.state.catalog
    return catalog.render("admin/ProjectEdit.jinja", request=request, user=user, project=project, errors={})


@router.post("/admin/projects/{project_id}", response_class=HTMLResponse)
async def admin_project_update(
    project_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    service = ProjectService(session)
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    form = await request.form()
    payload = {
        "title": str(form.get("title") or "").strip(),
        "slug": str(form.get("slug") or "").strip(),
        "description": str(form.get("description") or "").strip(),
        "content_md": str(form.get("content") or "").strip(),
        "image": _clean_optional_url(form.get("image")),
        "category": str(form.get("category") or "").strip() or "other",
        "github_url": _clean_optional_url(form.get("github_url")),
        "demo_url": _clean_optional_url(form.get("demo_url")),
        "featured": _as_bool(form.get("featured")),
        "tech_stack": _parse_list(str(form.get("tech_stack") or "")),
    }

    updated = await service.update_project(project, payload)
    session.add(AuditLog(actor_user_id=user.id, action="update", entity="project", entity_id=str(updated.id), payload_json={"title": updated.title, "slug": updated.slug}))
    await session.commit()

    return _toast_redirect("/admin/projects", "Project updated")


@router.post("/admin/projects/{project_id}/delete")
async def admin_project_delete(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    service = ProjectService(session)
    project = await service.get_project_by_id(project_id)
    if project:
        await service.delete_project(project)
        session.add(AuditLog(actor_user_id=user.id, action="delete", entity="project", entity_id=str(project_id), payload_json={"slug": project.slug}))
        await session.commit()

    return _toast_redirect("/admin/projects", "Project deleted")


@router.get("/admin/profile", response_class=HTMLResponse)
async def admin_profile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    profile = await ProfileService(session).get_or_create_profile(user.id)
    catalog = request.app.state.catalog
    return catalog.render("admin/Profile.jinja", request=request, user=user, profile=profile)


@router.post("/admin/profile")
async def admin_profile_save(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    profile = await ProfileService(session).get_or_create_profile(user.id)
    form = await request.form()

    # Parse complex arrays from [] fields.
    def get_list(key: str) -> list[str]:
        return [str(v).strip() for v in form.getlist(key) if str(v).strip()]

    work_titles = form.getlist("work_title[]")
    work_companies = form.getlist("work_company[]")
    work_locations = form.getlist("work_location[]")
    work_start_dates = form.getlist("work_start_date[]")
    work_end_dates = form.getlist("work_end_date[]")
    work_descs = form.getlist("work_description[]")

    work_experience = []
    for idx, title in enumerate(work_titles):
        title = str(title).strip()
        if not title:
            continue
        work_experience.append(
            {
                "title": title,
                "company": str(work_companies[idx]).strip() if idx < len(work_companies) else "",
                "location": str(work_locations[idx]).strip() if idx < len(work_locations) else "",
                "start_date": str(work_start_dates[idx]).strip() if idx < len(work_start_dates) else "",
                "end_date": str(work_end_dates[idx]).strip() if idx < len(work_end_dates) else "",
                "description": str(work_descs[idx]).strip() if idx < len(work_descs) else "",
            }
        )

    edu_schools = form.getlist("edu_school[]")
    edu_degrees = form.getlist("edu_degree[]")
    edu_start_dates = form.getlist("edu_start_date[]")
    edu_end_dates = form.getlist("edu_end_date[]")

    education = []
    for idx, school in enumerate(edu_schools):
        school = str(school).strip()
        if not school:
            continue
        education.append(
            {
                "school": school,
                "degree": str(edu_degrees[idx]).strip() if idx < len(edu_degrees) else "",
                "start_date": str(edu_start_dates[idx]).strip() if idx < len(edu_start_dates) else "",
                "end_date": str(edu_end_dates[idx]).strip() if idx < len(edu_end_dates) else "",
            }
        )

    cert_names = form.getlist("cert_name[]")
    cert_issuers = form.getlist("cert_issuer[]")
    cert_dates = form.getlist("cert_date[]")
    cert_urls = form.getlist("cert_url[]")
    cert_ids = form.getlist("cert_credential_id[]")

    certificates = []
    for idx, name in enumerate(cert_names):
        name = str(name).strip()
        if not name:
            continue
        certificates.append(
            {
                "name": name,
                "issuer": str(cert_issuers[idx]).strip() if idx < len(cert_issuers) else "",
                "date": str(cert_dates[idx]).strip() if idx < len(cert_dates) else "",
                "url": str(cert_urls[idx]).strip() if idx < len(cert_urls) and str(cert_urls[idx]).strip() else None,
                "credential_id": str(cert_ids[idx]).strip() if idx < len(cert_ids) and str(cert_ids[idx]).strip() else None,
            }
        )

    social_titles = form.getlist("social_title[]")
    social_urls = form.getlist("social_url[]")
    social_icons = form.getlist("social_icon[]")
    social_icon_urls = form.getlist("social_icon_url[]")
    social_icon_uploads = form.getlist("social_icon_upload[]")

    social_links = []
    for idx, title in enumerate(social_titles):
        title = str(title).strip()
        url = _clean_optional_text(social_urls[idx] if idx < len(social_urls) else "") or ""
        raw_icon = str(social_icons[idx]).strip() if idx < len(social_icons) else ""
        icon = raw_icon.lower()
        icon = {
            "x": "twitter",
            "website": "globe",
            "web": "globe",
            "site": "globe",
            "mail": "email",
            "envelope": "email",
            "telephone": "phone",
        }.get(icon, icon)
        if icon not in {"github", "linkedin", "twitter", "email", "phone", "globe"}:
            icon = _infer_social_icon(title=title, url=url)
        icon_url = _clean_optional_icon_url(social_icon_urls[idx] if idx < len(social_icon_urls) else "")

        upload = social_icon_uploads[idx] if idx < len(social_icon_uploads) else None
        uploaded_url = await _save_social_icon(upload)
        if uploaded_url:
            icon_url = uploaded_url

        if not title and not url:
            continue

        social_links.append(
            {
                "title": title,
                "url": url,
                "icon": icon,
                "icon_url": icon_url or None,
            }
        )

    payload = {
        "name": str(form.get("name") or "").strip(),
        "location": str(form.get("location") or "").strip(),
        "short_bio": str(form.get("short_bio") or "").strip(),
        "email": str(form.get("email") or "").strip(),
        "phone": _clean_optional_text(form.get("phone")),
        "website": _clean_optional_url(form.get("website")),
        "about_summary": str(form.get("about_summary") or "").strip(),
        "about_markdown": str(form.get("about_markdown") or ""),
        "work_experience": work_experience,
        "education": education,
        "certificates": certificates,
        "skills": get_list("skills[]"),
        "social_links": social_links,
    }

    await ProfileService(session).update_profile(profile, payload)
    session.add(AuditLog(actor_user_id=user.id, action="update", entity="profile", entity_id=str(profile.id), payload_json={"name": payload["name"]}))
    await session.commit()

    return _toast_redirect("/admin/profile", "Profile saved")


@router.get("/admin/comments", response_class=HTMLResponse)
async def admin_comments(
    request: Request,
    show_deleted: bool = False,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    query = (
        select(Comment, Post)
        .join(Post, Comment.post_id == Post.id)
        .order_by(col(Comment.created_at).desc())
    )
    if not show_deleted:
        query = query.where(Comment.is_deleted == False)  # noqa: E712

    result = await session.execute(query)
    comments = []
    for comment, post in result.all():
        comments.append(
            {
                "id": str(comment.id),
                "content": comment.content,
                "created_at": comment.created_at,
                "is_deleted": comment.is_deleted,
                "is_flagged": comment.is_flagged,
                "is_guest": comment.user_id is None,
                "display_name": comment.guest_name or "Anonymous",
                "guest_email": comment.guest_email,
                "ip_address": comment.ip_address,
                "post_title": post.title,
                "post_slug": post.slug,
            }
        )

    catalog = request.app.state.catalog
    return catalog.render(
        "admin/CommentsList.jinja",
        request=request,
        user=user,
        comments=comments,
        show_deleted=show_deleted,
    )


@router.get("/admin/comments/{comment_id}", response_class=HTMLResponse)
async def admin_comment_detail(
    comment_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    query = (
        select(Comment, Post)
        .join(Post, Comment.post_id == Post.id)
        .where(Comment.id == comment_id)
    )
    result = await session.execute(query)
    row = result.first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    comment, post = row
    comment_data = {
        "id": str(comment.id),
        "content": comment.content,
        "created_at": comment.created_at,
        "is_deleted": comment.is_deleted,
        "is_flagged": comment.is_flagged,
        "is_guest": comment.user_id is None,
        "display_name": comment.guest_name or "Anonymous",
        "guest_email": comment.guest_email,
        "ip_address": comment.ip_address,
        "post_title": post.title,
        "post_slug": post.slug,
    }

    catalog = request.app.state.catalog
    return catalog.render("admin/CommentDetail.jinja", comment=comment_data)


@router.post("/admin/comments/{comment_id}/delete")
async def admin_comment_delete(
    comment_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    comment = await CommentService(session).get_comment_by_id(comment_id)
    if comment:
        await CommentService(session).delete_comment(comment)
        session.add(AuditLog(actor_user_id=user.id, action="delete", entity="comment", entity_id=str(comment_id), payload_json={}))
        await session.commit()

    return _toast_redirect("/admin/comments", "Comment deleted")


@router.post("/admin/comments/{comment_id}/restore")
async def admin_comment_restore(
    comment_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    comment = await CommentService(session).get_comment_by_id(comment_id)
    if comment:
        await CommentService(session).restore_comment(comment)
        session.add(AuditLog(actor_user_id=user.id, action="restore", entity="comment", entity_id=str(comment_id), payload_json={}))
        await session.commit()

    return _toast_redirect("/admin/comments?show_deleted=true", "Comment restored")


@router.get("/admin/messages", response_class=HTMLResponse)
async def admin_messages(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    messages = await ContactMessageService(session).list_messages(limit=500)
    catalog = request.app.state.catalog
    return catalog.render("admin/MessagesList.jinja", request=request, user=user, messages=messages)


@router.get("/admin/status", response_class=HTMLResponse)
async def admin_status(
    request: Request,
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()
    catalog = request.app.state.catalog
    return catalog.render("admin/Status.jinja", request=request, user=user)


@router.get("/admin/audit", response_class=HTMLResponse)
async def admin_audit(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    rows = await session.execute(select(AuditLog).order_by(col(AuditLog.created_at).desc()).limit(200))
    logs = list(rows.scalars().all())

    actor_ids = {log.actor_user_id for log in logs if log.actor_user_id}
    actor_map: dict[str, str] = {}
    if actor_ids:
        users_result = await session.execute(select(User).where(col(User.id).in_(actor_ids)))
        for actor in users_result.scalars().all():
            actor_map[str(actor.id)] = actor.name or actor.email or str(actor.id)

    rendered_logs = []
    for log in logs:
        payload = log.payload_json or {}
        payload_preview = json.dumps(payload, ensure_ascii=False)
        rendered_logs.append(
            {
                "created_at": (log.created_at.strftime("%d/%m/%Y %H:%M:%S") if log.created_at else "-"),
                "actor": actor_map.get(str(log.actor_user_id), "System"),
                "action": log.action,
                "entity": log.entity,
                "entity_id": log.entity_id,
                "payload_preview": payload_preview if payload_preview else "{}",
            }
        )

    catalog = request.app.state.catalog
    return catalog.render("admin/Audit.jinja", request=request, user=user, logs=rendered_logs)


@router.get("/admin/files", response_class=HTMLResponse)
async def admin_files(
    request: Request,
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    items = []
    for folder, folder_name in ((FILES_UPLOAD_DIR, "files"), (SOCIAL_UPLOAD_DIR, "social")):
        for file_path in sorted(folder.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
            if not file_path.is_file():
                continue
            stat = file_path.stat()
            rel_path = file_path.relative_to(UPLOADS_ROOT_DIR).as_posix()
            items.append(
                {
                    "name": file_path.name,
                    "folder": folder_name,
                    "size_human": _human_size(stat.st_size),
                    "updated_at": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
                    "url": f"/static/uploads/{rel_path}",
                    "path": rel_path,
                }
            )

    catalog = request.app.state.catalog
    return catalog.render("admin/Files.jinja", request=request, user=user, files=items)


@router.post("/admin/files")
async def admin_files_upload(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    form = await request.form()
    upload = form.get("file")
    saved = await _save_uploaded_file(upload, folder=FILES_UPLOAD_DIR, web_prefix="/static/uploads/files")
    if not saved:
        return _toast_redirect("/admin/files", "Select a valid file to upload", "error")

    file_url, size = saved
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="upload",
            entity="file",
            entity_id=file_url,
            payload_json={"url": file_url, "size": size},
        )
    )
    await session.commit()
    return _toast_redirect("/admin/files", "File uploaded")


@router.post("/admin/files/delete")
async def admin_files_delete(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    form = await request.form()
    rel_path = str(form.get("path") or "").strip().lstrip("/")
    if not rel_path:
        return _toast_redirect("/admin/files", "Invalid file path", "error")

    root = UPLOADS_ROOT_DIR.resolve()
    target = (UPLOADS_ROOT_DIR / rel_path).resolve()
    if root not in target.parents or not target.is_file():
        return _toast_redirect("/admin/files", "File not found", "error")

    target.unlink(missing_ok=True)
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="delete",
            entity="file",
            entity_id=rel_path,
            payload_json={"path": rel_path},
        )
    )
    await session.commit()
    return _toast_redirect("/admin/files", "File deleted")


@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    row = await session.execute(select(Settings).where(Settings.id == 1))
    app_settings = row.scalar_one_or_none()
    if not app_settings:
        app_settings = Settings(id=1)
        session.add(app_settings)
        await session.commit()
        await session.refresh(app_settings)

    catalog = request.app.state.catalog
    return catalog.render("admin/Settings.jinja", request=request, user=user, settings=app_settings, errors={})


@router.post("/admin/settings", response_class=HTMLResponse)
async def admin_settings_save(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    row = await session.execute(select(Settings).where(Settings.id == 1))
    app_settings = row.scalar_one_or_none()
    if not app_settings:
        app_settings = Settings(id=1)

    form = await request.form()
    app_settings.site_name = str(form.get("site_name") or "Fabio Souza").strip() or "Fabio Souza"
    app_settings.site_description = str(form.get("site_description") or "").strip() or None
    app_settings.projects_enabled = _as_bool(form.get("projects_enabled"))
    app_settings.blog_enabled = _as_bool(form.get("blog_enabled"))
    app_settings.home_background_url = str(form.get("home_background_url") or "").strip() or None
    app_settings.home_projects_count = _as_int(form.get("home_projects_count"), default=4, min_value=3, max_value=6)
    app_settings.home_posts_count = _as_int(form.get("home_posts_count"), default=4, min_value=3, max_value=6)
    app_settings.home_projects_featured_only = str(form.get("home_projects_mode") or "").strip() == "featured_only"
    app_settings.github_repo_owner = str(form.get("github_repo_owner") or "").strip() or None
    app_settings.github_repo_name = str(form.get("github_repo_name") or "").strip() or None
    app_settings.github_posts_path = str(form.get("github_posts_path") or "posts").strip() or "posts"
    app_settings.github_enabled = _as_bool(form.get("github_enabled"))

    token_value = str(form.get("github_token") or "").strip()
    if token_value and token_value != "***hidden***":
        app_settings.github_token = token_value

    app_settings.updated_at = datetime.now(timezone.utc)

    session.add(app_settings)
    session.add(AuditLog(actor_user_id=user.id, action="update", entity="settings", entity_id="1", payload_json={"site_name": app_settings.site_name}))
    await session.commit()

    return _toast_redirect("/admin/settings", "Settings saved")


@router.post("/admin/settings/sync-github")
async def admin_settings_sync_github(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="sync",
            entity="github_posts",
            entity_id=None,
            payload_json={},
        )
    )
    await session.commit()
    return _toast_redirect("/admin/settings", "Settings saved")


@router.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics(
    request: Request,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    overview, summary = await _build_overview(session, days)

    # Transform to template-compatible shapes.
    top_paths = [
        {"url": item["path"], "title": item["path"], "views": item["count"]}
        for item in summary["top_paths"]
    ]

    # by day for chart
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days - 1)
    rows = await session.execute(
        select(func.date(PageView.created_at), func.count(PageView.id))
        .where(PageView.created_at >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc))
        .group_by(func.date(PageView.created_at))
        .order_by(func.date(PageView.created_at))
    )
    by_day_map = {str(row[0]): row[1] for row in rows.all()}
    pageviews_by_day = []
    for i in range(days):
        day = start + timedelta(days=i)
        key = str(day)
        pageviews_by_day.append({"date": key, "views": int(by_day_map.get(key, 0))})

    recent_events = []
    recent_visitors = []

    catalog = request.app.state.catalog
    return catalog.render(
        "admin/Analytics.jinja",
        request=request,
        user=user,
        overview=overview,
        top_pages=top_paths,
        top_referrers=[],
        top_ips=[],
        device_stats={"desktop": 0, "mobile": 0, "tablet": 0},
        browser_stats=[],
        country_stats=[],
        recent_events=recent_events,
        recent_visitors=recent_visitors,
        pageviews_by_day=pageviews_by_day,
        selected_days=days,
    )


@router.get("/events/admin.analytics")
async def admin_analytics_events(
    request: Request,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    catalog = request.app.state.catalog

    async def event_stream():
        while True:
            if await request.is_disconnected():
                break

            overview, _ = await _build_overview(session, days)
            html = catalog.render("admin/AnalyticsCards.jinja", overview=overview)

            yield "event: metrics\n"
            for line in html.splitlines():
                yield f"data: {line}\n"
            yield "\n"

            await asyncio.sleep(10)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sse/audit/stream")
async def sse_audit_stream(
    request: Request,
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    async def event_stream():
        last_id = None
        while True:
            if await request.is_disconnected():
                break

            async with async_session_factory() as stream_session:
                latest_result = await stream_session.execute(
                    select(AuditLog).order_by(col(AuditLog.created_at).desc()).limit(1)
                )
                latest = latest_result.scalar_one_or_none()

            if latest and latest.id != last_id:
                payload = {
                    "id": str(latest.id),
                    "action": latest.action,
                    "entity": latest.entity,
                    "entity_id": latest.entity_id,
                    "created_at": latest.created_at.isoformat() if latest.created_at else None,
                }
                last_id = latest.id
                yield "event: audit\n"
                yield f"data: {json.dumps(payload)}\n\n"
            else:
                yield "event: heartbeat\n"
                yield "data: {}\n\n"

            await asyncio.sleep(5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sse/jobs/stream")
async def sse_jobs_stream(
    request: Request,
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()

    async def event_stream():
        while True:
            if await request.is_disconnected():
                break
            payload = {"status": "idle", "updated_at": datetime.now(timezone.utc).isoformat()}
            yield "event: jobs\n"
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(10)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/admin/partials/posts/table", response_class=HTMLResponse)
async def admin_partial_posts_table(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()
    posts = await BlogService(session).get_posts(include_drafts=True, limit=300)
    catalog = request.app.state.catalog
    return catalog.render("admin/BlogList.jinja", request=request, user=user, posts=posts)


@router.get("/admin/partials/projects/table", response_class=HTMLResponse)
async def admin_partial_projects_table(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    if not _is_admin(user):
        return _redirect_login()
    projects = await ProjectService(session).get_projects(limit=500)
    catalog = request.app.state.catalog
    return catalog.render("admin/ProjectsList.jinja", request=request, user=user, projects=projects)


@router.get("/admin/partials/toast", response_class=HTMLResponse)
async def admin_partial_toast(request: Request, message: str = "Done", tone: str = "success"):
    catalog = request.app.state.catalog
    return catalog.render("ui/Toast.jinja", message=message, variant=tone)


@router.post("/admin/partials/editor/preview", response_class=HTMLResponse)
async def admin_partial_editor_preview(request: Request):
    form = await request.form()
    content = str(form.get("content") or "")
    html = f"<div class='prose prose-invert max-w-none'>{content}</div>"
    return HTMLResponse(html)
