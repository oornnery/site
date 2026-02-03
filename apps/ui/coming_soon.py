from __future__ import annotations

from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.status import HTTP_200_OK


def render_coming_soon_html(
    request: Request,
    *,
    brand: str,
    title: str = "Page under construction",
    message: str | None = None,
    home_href: str = "/",
    home_label: str = "Back to home",
) -> HTMLResponse:
    catalog = request.app.state.catalog
    html = catalog.render(
        "@ui/pages/coming-soon.jinja",
        globals={"request": request},
        title=title,
        brand=brand,
        message=message,
        home_href=home_href,
        home_label=home_label,
    )
    return HTMLResponse(html, status_code=HTTP_200_OK)
