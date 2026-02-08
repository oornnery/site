from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.packages.db import get_session
from apps.packages.security import get_current_user_optional
from apps.packages.services import BlogService, CommentService

router = APIRouter(prefix="/api", tags=["blog-api"])


@router.get("/posts")
async def list_posts(
    category: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session),
):
    offset = max(0, (page - 1) * per_page)
    posts = await BlogService(session).get_posts(
        category=category,
        tag=tag,
        search=q,
        limit=per_page,
        offset=offset,
    )
    return posts


@router.get("/posts/{slug}")
async def get_post(slug: str, session: AsyncSession = Depends(get_session)):
    service = BlogService(session)
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await service.increment_views(post)
    return post


@router.get("/tags")
async def list_tags(session: AsyncSession = Depends(get_session)):
    return await BlogService(session).get_tags_with_count()


@router.get("/categories")
async def list_categories(session: AsyncSession = Depends(get_session)):
    return await BlogService(session).get_categories_with_count()


@router.post("/posts/{slug}/reactions")
async def add_reaction(slug: str, payload: dict, session: AsyncSession = Depends(get_session)):
    service = BlogService(session)
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    reaction_type = str(payload.get("type") or "like")
    reaction = await service.add_reaction(post.id, reaction_type)
    return reaction


@router.get("/comments/{post_slug}")
async def get_comments(post_slug: str, session: AsyncSession = Depends(get_session)):
    return await CommentService(session).list_comments(post_slug)


@router.post("/comments/{post_slug}")
async def create_comment(
    post_slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    payload: dict
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)

    content = str(payload.get("content") or "").strip()
    guest_name = str(payload.get("guest_name") or "").strip() or None
    guest_email = str(payload.get("guest_email") or "").strip() or None

    if not user and not guest_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest name is required for anonymous comments",
        )
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content required")

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")

    comment = await CommentService(session).create_comment(
        post_slug=post_slug,
        content=content,
        user=user,
        guest_name=guest_name,
        guest_email=guest_email,
        ip_address=ip,
        user_agent=ua,
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return comment
