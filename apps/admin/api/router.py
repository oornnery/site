from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from apps.packages.config import settings
from apps.packages.db import get_session
from apps.packages.domain.models import AuditLog
from apps.packages.security import (
    CurrentAdminUser,
    clear_auth_cookie,
    get_current_user_optional,
    set_auth_cookie,
)
from apps.packages.services import AnalyticsService, AuthService, BlogService, ProjectService

router = APIRouter(prefix="/api", tags=["admin-api"])
UPLOADS_ROOT_DIR = Path(__file__).resolve().parents[3] / "apps" / "packages" / "static" / "uploads"
FILES_UPLOAD_DIR = UPLOADS_ROOT_DIR / "files"
FILES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _audit(
    session: AsyncSession,
    *,
    actor_id: UUID | None,
    action: str,
    entity: str,
    entity_id: str | None,
    payload: dict,
) -> None:
    log = AuditLog(
        actor_user_id=actor_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        payload_json=payload,
    )
    session.add(log)
    await session.commit()


async def _save_upload(file: UploadFile) -> tuple[str, int]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty upload")
    suffix = Path(file.filename or "").suffix.lower()
    if len(suffix) > 10:
        suffix = ""
    filename = f"{uuid4().hex}{suffix}"
    target = FILES_UPLOAD_DIR / filename
    target.write_bytes(content)
    return f"/static/uploads/files/{filename}", len(content)


@router.post("/auth/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    user = await service.authenticate_user(email, password)
    if not user:
        return JSONResponse({"detail": "Invalid credentials"}, status_code=401)

    token = service.create_token_for_user(user)
    response = JSONResponse({"ok": True, "user": {"id": str(user.id), "email": user.email, "name": user.name}})
    set_auth_cookie(response, token)

    user.last_login = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()

    return response


@router.post("/auth/logout")
async def logout():
    response = JSONResponse({"ok": True})
    clear_auth_cookie(response)
    return response


@router.get("/auth/me")
async def me(user=Depends(get_current_user_optional)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "is_admin": user.is_admin,
    }


@router.get("/auth/github/start")
async def github_start(session: AsyncSession = Depends(get_session)):
    # MVP dev flow: if OAuth is not configured, sign in as seeded admin in development.
    if settings.is_development and (not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET):
        service = AuthService(session)
        user = await service.get_user_by_email("admin@example.com")
        if not user:
            raise HTTPException(status_code=404, detail="Admin seed user not found")
        token = service.create_token_for_user(user)
        response = RedirectResponse(url="/admin", status_code=302)
        set_auth_cookie(response, token)
        return response

    raise HTTPException(status_code=501, detail="GitHub OAuth production flow not configured in this MVP")


@router.get("/auth/github/callback")
async def github_callback(session: AsyncSession = Depends(get_session)):
    return await github_start(session=session)


@router.post("/posts")
async def create_post(
    payload: dict,
    admin: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
):
    service = BlogService(session)
    post = await service.create_post(payload)
    await _audit(
        session,
        actor_id=admin.id,
        action="create",
        entity="post",
        entity_id=str(post.id),
        payload={"title": post.title, "slug": post.slug},
    )
    return post


@router.put("/posts/{post_id}")
@router.patch("/posts/{post_id}")
async def update_post(
    post_id: UUID,
    payload: dict,
    admin: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
):
    service = BlogService(session)
    post = await service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    updated = await service.update_post(post, payload)
    await _audit(
        session,
        actor_id=admin.id,
        action="update",
        entity="post",
        entity_id=str(updated.id),
        payload={"title": updated.title, "slug": updated.slug},
    )
    return updated


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: UUID,
    admin: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
):
    service = BlogService(session)
    post = await service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    await service.delete_post(post)
    await _audit(
        session,
        actor_id=admin.id,
        action="delete",
        entity="post",
        entity_id=str(post_id),
        payload={"slug": post.slug},
    )
    return {"ok": True}


@router.post("/projects")
async def create_project(
    payload: dict,
    admin: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
):
    service = ProjectService(session)
    project = await service.create_project(payload)
    await _audit(
        session,
        actor_id=admin.id,
        action="create",
        entity="project",
        entity_id=str(project.id),
        payload={"title": project.title, "slug": project.slug},
    )
    return project


@router.put("/projects/{project_id}")
@router.patch("/projects/{project_id}")
async def update_project(
    project_id: UUID,
    payload: dict,
    admin: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
):
    service = ProjectService(session)
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    updated = await service.update_project(project, payload)
    await _audit(
        session,
        actor_id=admin.id,
        action="update",
        entity="project",
        entity_id=str(updated.id),
        payload={"title": updated.title, "slug": updated.slug},
    )
    return updated


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    admin: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
):
    service = ProjectService(session)
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    await service.delete_project(project)
    await _audit(
        session,
        actor_id=admin.id,
        action="delete",
        entity="project",
        entity_id=str(project_id),
        payload={"slug": project.slug},
    )
    return {"ok": True}


@router.get("/analytics/pageviews")
async def analytics_pageviews(
    admin: CurrentAdminUser,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    _ = admin
    return await AnalyticsService(session).pageviews_summary(days=days)


@router.get("/audit")
async def audit_list(
    admin: CurrentAdminUser,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    _ = admin
    result = await session.execute(select(AuditLog).order_by(col(AuditLog.created_at).desc()).limit(limit))
    logs = result.scalars().all()
    return logs


@router.post("/files/upload")
async def files_upload(
    admin: CurrentAdminUser,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    file_url, file_size = await _save_upload(file)
    await _audit(
        session,
        actor_id=admin.id,
        action="upload",
        entity="file",
        entity_id=file_url,
        payload={"url": file_url, "size": file_size, "filename": file.filename},
    )
    return {"ok": True, "url": file_url, "size": file_size, "filename": file.filename}
