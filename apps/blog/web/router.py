from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from apps.packages.content.markdown import render_markdown
from apps.packages.content.rss import build_rss
from apps.packages.db import get_session
from apps.packages.security import get_current_user_optional
from apps.packages.services import BlogService, CommentService

router = APIRouter(tags=["blog-web"])


def _client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


@router.get("/", response_class=HTMLResponse, name="blog.home")
async def home(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    service = BlogService(session)
    all_posts = await service.get_posts(limit=8)
    categories = await service.get_categories_with_count()
    tags = await service.get_tags_with_count()

    featured_post = all_posts[0] if all_posts else None
    recent_posts = all_posts[1:5]
    if not recent_posts:
        recent_posts = all_posts[:4]

    catalog = request.app.state.catalog
    return catalog.render(
        "pages/BlogHome.jinja",
        request=request,
        user=user,
        featured_post=featured_post,
        recent_posts=recent_posts,
        categories=categories[:8],
        tags=tags[:12],
    )


@router.get("/posts", response_class=HTMLResponse)
async def posts(
    request: Request,
    category: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    q = q or request.query_params.get("search")
    service = BlogService(session)
    posts_list = await service.get_posts(category=category, tag=tag, search=q, limit=50)
    categories = await service.get_categories_with_count()

    catalog = request.app.state.catalog
    if request.headers.get("HX-Request"):
        return catalog.render(
            "blog/PostList.jinja",
            posts=posts_list,
            categories=[c["category"] for c in categories],
            current_category=category or "",
        )

    return catalog.render(
        "pages/BlogList.jinja",
        request=request,
        user=user,
        posts=posts_list,
        categories=[c["category"] for c in categories],
        current_category=category or "",
        current_tag=tag or "",
    )


@router.get("/posts/{slug}", response_class=HTMLResponse)
async def post_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    service = BlogService(session)
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    await service.increment_views(post)
    comments = await CommentService(session).list_comments(slug)

    catalog = request.app.state.catalog
    return catalog.render(
        "pages/BlogDetail.jinja",
        request=request,
        user=user,
        post=post,
        content=post.content_html or render_markdown(post.content_md),
        comments=comments,
    )


@router.get("/tags/{slug}", response_class=HTMLResponse)
async def tag_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    return await posts(request=request, tag=slug, session=session, user=user)


@router.get("/categories/{slug}", response_class=HTMLResponse)
async def category_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    return await posts(request=request, category=slug, session=session, user=user)


@router.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    return await posts(request=request, q=q, session=session, user=user)


@router.get("/feed.xml")
async def feed_xml(session: AsyncSession = Depends(get_session)) -> Response:
    posts = await BlogService(session).get_posts(limit=20)
    items = [
        {
            "title": p.title,
            "link": f"https://blog.fabiosouza.com/posts/{p.slug}",
            "description": p.description,
        }
        for p in posts
    ]
    xml = build_rss(
        title="Blog by Fabio Souza",
        link="https://blog.fabiosouza.com",
        description="Posts and articles",
        items=items,
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/partials/posts/list", response_class=HTMLResponse)
async def partial_posts_list(
    request: Request,
    category: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    q = q or request.query_params.get("search")
    service = BlogService(session)
    posts_list = await service.get_posts(category=category, tag=tag, search=q, limit=50)
    categories = await service.get_categories_with_count()
    catalog = request.app.state.catalog
    return catalog.render(
        "blog/PostList.jinja",
        posts=posts_list,
        categories=[c["category"] for c in categories],
        current_category=category or "",
    )


@router.get("/partials/posts/search", response_class=HTMLResponse)
async def partial_posts_search(
    request: Request,
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    return await partial_posts_list(request=request, q=q, session=session)


@router.get("/partials/comments", response_class=HTMLResponse)
async def partial_comments(
    request: Request,
    post_slug: str,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    comments = await CommentService(session).list_comments(post_slug)
    catalog = request.app.state.catalog
    return catalog.render("blog/Comments.jinja", comments=comments, post_slug=post_slug, user=user)


@router.post("/partials/comments/new", response_class=HTMLResponse)
async def partial_comments_new(
    request: Request,
    post_slug: str,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_optional),
):
    form = await request.form()
    content = str(form.get("content") or "").strip()
    guest_name = str(form.get("guest_name") or "").strip() or None
    guest_email = str(form.get("guest_email") or "").strip() or None

    if not user and not guest_name:
        comments = await CommentService(session).list_comments(post_slug)
        catalog = request.app.state.catalog
        return HTMLResponse(
            catalog.render(
                "blog/Comments.jinja",
                comments=comments,
                post_slug=post_slug,
                user=user,
            ),
            status_code=400,
        )

    await CommentService(session).create_comment(
        post_slug=post_slug,
        content=content,
        user=user,
        guest_name=guest_name,
        guest_email=guest_email,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )

    return await partial_comments(request=request, post_slug=post_slug, session=session, user=user)


@router.post("/partials/reactions", response_class=HTMLResponse)
async def partial_reactions(
    request: Request,
    post_slug: str,
    reaction_type: str = "like",
    session: AsyncSession = Depends(get_session),
):
    service = BlogService(session)
    post = await service.get_post_by_slug(post_slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    await service.add_reaction(post.id, reaction_type)
    counts = await service.get_reactions_count(post.id)
    catalog = request.app.state.catalog
    return catalog.render("blog/Reactions.jinja", post_slug=post_slug, counts=counts)
