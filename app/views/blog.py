import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, Response

from app.core.deps import get_blog_page_service
from app.core.rendering import get_lang, is_htmx, render_fragment, render_page
from app.services import BlogPageService
from app.models.contexts import BlogPostsPageContext, BlogTagsPageContext

router = APIRouter(prefix="/blog", tags=["blog"])
logger = logging.getLogger(__name__)

BlogPageServiceDep = Annotated[BlogPageService, Depends(get_blog_page_service)]


@router.get("", response_class=HTMLResponse)
async def blog_home(
    request: Request,
    page_service: BlogPageServiceDep,
) -> HTMLResponse:
    lang = get_lang(request)
    page = page_service.build_home_page(lang=lang)
    logger.debug("Blog home page rendered.")
    return render_page(page, lang=lang)


@router.get("/posts", response_class=HTMLResponse)
async def blog_posts(
    request: Request,
    page_service: BlogPageServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    q: Annotated[str, Query(max_length=200)] = "",
) -> HTMLResponse:
    lang = get_lang(request)
    page_data = page_service.build_posts_page(q=q, page=page, lang=lang)
    logger.debug("Blog posts page rendered.")
    if is_htmx(request):
        ctx = page_data.context
        if not isinstance(ctx, BlogPostsPageContext):
            raise TypeError(f"Expected BlogPostsPageContext, got {type(ctx).__name__}")
        return render_fragment(
            "@features/blog/posts-fragment.jinja",
            lang=lang,
            posts=ctx.posts,
            q=ctx.q,
            page=ctx.page,
            total_pages=ctx.total_pages,
        )
    return render_page(page_data, lang=lang)


@router.get("/posts/{slug}", response_class=HTMLResponse)
async def blog_post_detail(
    request: Request,
    slug: Annotated[str, Path()],
    page_service: BlogPageServiceDep,
) -> HTMLResponse:
    lang = get_lang(request)
    post = page_service.get_post(slug, lang=lang)
    if post is None:
        logger.info(f"Blog post detail not found for slug={slug}.")
        raise HTTPException(status_code=404, detail="Blog post not found")
    page = page_service.build_post_page(post, lang=lang)
    logger.debug(f"Blog post detail page rendered for slug={slug}.")
    return render_page(page, lang=lang)


@router.get("/tags", response_class=HTMLResponse)
async def blog_tags(
    request: Request,
    page_service: BlogPageServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
) -> HTMLResponse:
    lang = get_lang(request)
    page_data = page_service.build_tags_page(page=page, lang=lang)
    logger.debug("Blog tags page rendered.")
    if is_htmx(request):
        ctx = page_data.context
        if not isinstance(ctx, BlogTagsPageContext):
            raise TypeError(f"Expected BlogTagsPageContext, got {type(ctx).__name__}")
        return render_fragment(
            "@features/blog/tags-fragment.jinja",
            lang=lang,
            tags=ctx.tags,
            posts=ctx.posts,
            selected_tag=ctx.selected_tag,
            page=ctx.page,
            total_pages=ctx.total_pages,
        )
    return render_page(page_data, lang=lang)


@router.get("/tags/{tag}", response_class=HTMLResponse)
async def blog_tag_detail(
    tag: Annotated[str, Path()],
    request: Request,
    page_service: BlogPageServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
) -> HTMLResponse:
    lang = get_lang(request)
    page_data = page_service.build_tags_page(tag=tag, page=page, lang=lang)
    logger.debug(f"Blog tag page rendered for tag={tag}.")
    if is_htmx(request):
        ctx = page_data.context
        if not isinstance(ctx, BlogTagsPageContext):
            raise TypeError(f"Expected BlogTagsPageContext, got {type(ctx).__name__}")
        return render_fragment(
            "@features/blog/tags-fragment.jinja",
            lang=lang,
            tags=ctx.tags,
            posts=ctx.posts,
            selected_tag=ctx.selected_tag,
            page=ctx.page,
            total_pages=ctx.total_pages,
        )
    return render_page(page_data, lang=lang)


@router.get("/feed.xml")
async def blog_feed(
    request: Request,
    page_service: BlogPageServiceDep,
) -> Response:
    lang = get_lang(request)
    feed = page_service.build_rss_feed(lang=lang)
    logger.debug("Blog RSS feed rendered.")
    return Response(
        content=feed,
        media_type="application/rss+xml",
        headers={"Cache-Control": "public, max-age=900"},
    )
