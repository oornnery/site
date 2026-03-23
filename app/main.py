import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.views.router import views_router
from app.core.config import settings, split_csv
from app.core.deps import (
    get_catalog,
    get_contact_page_service,
    limiter,
    render_template,
)
from app.core.i18n import get_translations
from app.core.language import LanguageMiddleware
from app.core.logger import configure_logging
from app.core.rendering import get_lang, is_htmx, render_fragment, render_page
from app.core.security import (
    RequestBodySizeLimitMiddleware,
    RequestTracingMiddleware,
    SecurityHeadersMiddleware,
)
from app.services.seo import seo_for_page

CONTACT_PATH = "/contact"

logger = logging.getLogger(__name__)


def rate_limit_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    return HTMLResponse("Rate limit exceeded.", status_code=429)


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    logger.info("Creating FastAPI application.")

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info("Mounted static files directory at /static.")
    else:
        logger.warning("Static directory not found; /static mount skipped.")

    app.state.limiter = limiter
    app.add_middleware(RequestTracingMiddleware)  # type: ignore[arg-type]
    app.add_middleware(RequestBodySizeLimitMiddleware)  # type: ignore[arg-type]
    app.add_middleware(SecurityHeadersMiddleware)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)  # type: ignore[arg-type]
    cors_origins = split_csv(settings.cors_allow_origins)
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,  # type: ignore[arg-type]
            allow_origins=cors_origins,
            allow_methods=split_csv(settings.cors_allow_methods) or ["GET"],
            allow_headers=split_csv(settings.cors_allow_headers),
            allow_credentials=settings.cors_allow_credentials,
        )
    app.add_middleware(
        TrustedHostMiddleware,  # type: ignore[arg-type]
        allowed_hosts=split_csv(settings.trusted_hosts) or ["localhost"],
    )
    app.add_middleware(LanguageMiddleware)  # type: ignore[arg-type]
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> Response:
        if request.method == "POST" and request.url.path == CONTACT_PATH:
            user_agent = request.headers.get("user-agent", "")
            lang = get_lang(request)
            t = get_translations(lang)
            page_service = get_contact_page_service()
            errors = {"form": t.errors.form_invalid}
            page = page_service.build_page(
                user_agent=user_agent,
                errors=errors,
                lang=lang,
            )
            if is_htmx(request):
                from app.models.contexts import ContactPageContext

                ctx = page.context
                assert isinstance(ctx, ContactPageContext)
                return render_fragment(
                    "@features/contact/fragment.jinja",
                    status_code=422,
                    lang=lang,
                    csrf_token=ctx.csrf_token,
                    success=ctx.success,
                    errors=ctx.errors,
                    form_data=ctx.form_data,
                )
            return render_page(page, status_code=422, lang=lang)
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    app.include_router(api_router)
    app.include_router(views_router)
    logger.info("Routers registered from app.api.router and app.views.router.")

    get_catalog()  # Fail fast if templates or content/about.md are misconfigured

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
        logger.info(f"Route not found for path={request.url.path}")
        lang = get_lang(request)
        t = get_translations(lang)
        seo = seo_for_page("404 - Not Found", t.errors.not_found)
        html = render_template(
            "pages/not-found.jinja", seo=seo, current_path="", t=t, current_lang=lang
        )
        return HTMLResponse(content=html, status_code=404)

    logger.info("FastAPI application created successfully.")
    return app


app = create_app()
