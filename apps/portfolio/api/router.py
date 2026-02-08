from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.packages.db import get_session
from apps.packages.services import ContactMessageService, ProfileService, ProjectService

router = APIRouter(prefix="/api", tags=["portfolio-api"])


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=5000)
    subject: str | None = Field(default=None, max_length=200)


class ContactResponse(BaseModel):
    success: bool = True
    message: str
    timestamp: datetime


@router.get("/projects")
async def list_projects(
    category: str | None = None,
    featured: bool | None = None,
    search: str | None = None,
    tech: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    service = ProjectService(session)
    projects = await service.get_projects(
        category=category,
        featured=featured,
        search=search,
        tech=tech,
    )
    return projects


@router.get("/projects/{slug}")
async def get_project(slug: str, session: AsyncSession = Depends(get_session)):
    service = ProjectService(session)
    project = await service.get_project_by_slug(slug)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/profile")
async def get_profile(session: AsyncSession = Depends(get_session)):
    service = ProfileService(session)
    profile = await service.get_main_profile()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_contact_message(
    request: Request,
    payload: ContactRequest,
    session: AsyncSession = Depends(get_session),
):
    ip_address = request.headers.get("X-Forwarded-For", "")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    elif request.client:
        ip_address = request.client.host
    else:
        ip_address = None

    user_agent = request.headers.get("User-Agent")

    await ContactMessageService(session).create_message(
        name=payload.name,
        email=str(payload.email),
        subject=payload.subject,
        message=payload.message,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ContactResponse(
        success=True,
        message="Thank you for your message! I'll get back to you soon.",
        timestamp=datetime.now(timezone.utc),
    )
