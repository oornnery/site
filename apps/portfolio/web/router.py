from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from apps.packages.content.markdown import render_markdown
from apps.packages.db import get_session
from apps.packages.domain.models import Settings
from apps.packages.security import get_current_user_optional
from apps.packages.services import BlogService, ContactMessageService, ProfileService, ProjectService

router = APIRouter(tags=["portfolio-web"])


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def generate_resume_html(profile, about_html: str) -> str:
    return f"""
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>{profile.name} - Resume</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: #111; margin: 24px; }}
    h1 {{ margin-bottom: 0; }}
    .muted {{ color: #555; margin-top: 4px; }}
    h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 20px; }}
    .tag {{ display: inline-block; background: #f3f4f6; padding: 2px 8px; border-radius: 10px; margin-right: 6px; }}
  </style>
</head>
<body>
  <h1>{profile.name}</h1>
  <p class=\"muted\">{profile.short_bio}</p>
  <p class=\"muted\">{profile.location} | {profile.email}</p>

  <h2>About</h2>
  <div>{about_html}</div>

  <h2>Skills</h2>
  <p>{''.join([f'<span class="tag">{s}</span>' for s in (profile.skills or [])])}</p>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, name="portfolio.home")
async def home(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    settings_result = await session.execute(select(Settings).where(Settings.id == 1))
    db_settings = settings_result.scalar_one_or_none()
    settings_view = (
        db_settings.model_dump()
        if db_settings
        else {
            "projects_enabled": True,
            "blog_enabled": False,
            "home_background_url": None,
        }
    )
    settings_view["blog_enabled"] = False

    profile = await ProfileService(session).get_main_profile()
    projects_limit = int((db_settings.home_projects_count if db_settings else 4) or 4)
    posts_limit = int((db_settings.home_posts_count if db_settings else 4) or 4)
    featured_only = bool(db_settings.home_projects_featured_only) if db_settings else False
    projects = await ProjectService(session).get_featured_projects(limit=projects_limit)
    if not featured_only and len(projects) < projects_limit:
        all_projects = await ProjectService(session).get_projects(limit=max(24, projects_limit * 3))
        existing_ids = {project.id for project in projects}
        for project in all_projects:
            if project.id in existing_ids:
                continue
            projects.append(project)
            existing_ids.add(project.id)
            if len(projects) >= projects_limit:
                break
    posts = await BlogService(session).get_posts(limit=posts_limit)

    catalog = request.app.state.catalog
    return catalog.render(
        "pages/Home.jinja",
        request=request,
        user=user,
        profile=profile,
        projects=projects,
        posts=posts,
        settings=settings_view,
    )


@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    profile = await ProfileService(session).get_main_profile()
    about_html = render_markdown(profile.about_markdown if profile else "")

    catalog = request.app.state.catalog
    return catalog.render(
        "pages/About.jinja",
        request=request,
        user=user,
        profile=profile,
        about_html=about_html,
    )


@router.get("/projects", response_class=HTMLResponse)
async def projects_list(
    request: Request,
    search: str | None = None,
    category: str | None = None,
    tech: str | None = None,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    projects = await ProjectService(session).get_projects(
        category=category,
        search=search,
        tech=tech,
    )

    catalog = request.app.state.catalog
    if request.headers.get("HX-Request"):
        return catalog.render("partials/ProjectGrid.jinja", projects=projects)

    return catalog.render(
        "pages/Projects.jinja",
        request=request,
        user=user,
        projects=projects,
        current_tech=tech or "",
        current_search=search or "",
    )


@router.get("/partials/projects/grid", response_class=HTMLResponse)
async def projects_grid_partial(
    request: Request,
    search: str | None = None,
    category: str | None = None,
    tech: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    projects = await ProjectService(session).get_projects(
        category=category,
        search=search,
        tech=tech,
    )
    catalog = request.app.state.catalog
    return catalog.render("partials/ProjectGrid.jinja", projects=projects)


@router.get("/projects/{slug}", response_class=HTMLResponse)
async def project_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    project = await ProjectService(session).get_project_by_slug(slug)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    catalog = request.app.state.catalog
    return catalog.render(
        "pages/ProjectDetail.jinja",
        request=request,
        user=user,
        project=project,
        content=project.content_html or render_markdown(project.content_md),
    )


@router.get("/resume", response_class=HTMLResponse)
async def resume(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    return await about(request=request, session=session, user=user)


@router.get("/resume.pdf")
async def resume_pdf(session: AsyncSession = Depends(get_session)):
    profile = await ProfileService(session).get_main_profile()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    about_html = render_markdown(profile.about_markdown)
    html_content = generate_resume_html(profile, about_html)

    try:
        from weasyprint import HTML

        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        filename = f"{profile.name.replace(' ', '_')}_Resume.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF generation requires WeasyPrint installed",
        ) from exc


@router.get("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    profile = await ProfileService(session).get_main_profile()
    catalog = request.app.state.catalog
    return catalog.render("pages/Contact.jinja", request=request, user=user, profile=profile)


@router.post("/partials/contact/form", response_class=HTMLResponse)
async def contact_form_submit(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    form = await request.form()
    name = str(form.get("name") or "").strip()
    email = str(form.get("email") or "").strip()
    message = str(form.get("message") or "").strip()

    errors: dict[str, str] = {}
    if len(name) < 2:
        errors["name"] = "Name must have at least 2 characters"
    if "@" not in email:
        errors["email"] = "Valid email is required"
    if len(message) < 10:
        errors["message"] = "Message must have at least 10 characters"

    catalog = request.app.state.catalog
    if errors:
        return HTMLResponse(
            catalog.render(
                "partials/ContactForm.jinja",
                form_data={"name": name, "email": email, "message": message},
                errors=errors,
            ),
            status_code=400,
        )

    ip_address = _get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    await ContactMessageService(session).create_message(
        name=name,
        email=email,
        message=message,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    toast = catalog.render("partials/Toast.jinja", message="Message sent successfully!", tone="success")
    form_html = catalog.render("partials/ContactForm.jinja", success_message="Thanks! I will get back to you soon.")
    return HTMLResponse(form_html + toast)
