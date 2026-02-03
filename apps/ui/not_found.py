from __future__ import annotations

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.status import HTTP_404_NOT_FOUND


def render_not_found_html(
    request: Request,
    *,
    brand: str,
    title: str = "Page not found",
    message: str | None = None,
    home_href: str = "/",
    home_label: str = "Back to home",
) -> HTMLResponse:
    catalog = request.app.state.catalog
    html = catalog.render(
        "@ui/pages/404.jinja",
        globals={"request": request},
        title=title,
        brand=brand,
        message=message,
        home_href=home_href,
        home_label=home_label,
    )
    return HTMLResponse(html, status_code=HTTP_404_NOT_FOUND)


def not_found_response(
    request: Request,
    *,
    brand: str,
    title: str = "Page not found",
    message: str | None = None,
    home_href: str = "/",
    home_label: str = "Back to home",
) -> Response:
    accept = request.headers.get("accept", "")
    if request.url.path.startswith("/api") or "application/json" in accept:
        return JSONResponse({"detail": "Not Found"}, status_code=HTTP_404_NOT_FOUND)

    return render_not_found_html(
        request,
        brand=brand,
        title=title,
        message=message,
        home_href=home_href,
        home_label=home_label,
    )
