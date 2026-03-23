from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.deps import render_template
from app.core.i18n import get_translations
from app.services import PageRenderData


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


def get_lang(request: Request) -> str:
    """Extract language from request state (set by LanguageMiddleware)."""
    return getattr(request.state, "lang", None) or settings.default_language


def render_page(
    page: PageRenderData, *, status_code: int = 200, lang: str | None = None
) -> HTMLResponse:
    resolved_lang = lang or settings.default_language
    context = page.context.model_dump()
    t = get_translations(resolved_lang)
    context["t"] = t
    context["current_lang"] = resolved_lang
    html = render_template(page.template, **context)
    return HTMLResponse(content=html, status_code=status_code)


def render_fragment(
    template: str,
    *,
    status_code: int = 200,
    lang: str | None = None,
    **context: Any,
) -> HTMLResponse:
    resolved_lang = lang or settings.default_language
    t = get_translations(resolved_lang)
    context["t"] = t
    context["current_lang"] = resolved_lang
    html = render_template(template, **context)
    return HTMLResponse(content=html, status_code=status_code)
