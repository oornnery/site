from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse

from app.core.dependencies import render_template
from app.services import PageRenderData


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


def render_page(page: PageRenderData, *, status_code: int = 200) -> HTMLResponse:
    context = page.context.model_dump()
    html = render_template(page.template, **context)
    return HTMLResponse(content=html, status_code=status_code)


def render_fragment(
    template: str, *, status_code: int = 200, **context: Any
) -> HTMLResponse:
    html = render_template(template, **context)
    return HTMLResponse(content=html, status_code=status_code)
