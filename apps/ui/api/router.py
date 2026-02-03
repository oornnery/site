from __future__ import annotations

import inspect
from datetime import datetime, timezone
from html import escape
from typing import Any, Awaitable, Callable, Mapping

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.status import HTTP_404_NOT_FOUND

HealthzCallable = Callable[[], Mapping[str, Any] | Awaitable[Mapping[str, Any]]]


def render_health_log_item(payload: Mapping[str, Any]) -> str:
    status = escape(str(payload.get("status", "OK")))
    code = payload.get("code")
    timestamp = payload.get("datetime")

    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()
    timestamp = escape(str(timestamp))

    code_text = "" if code is None else escape(str(code))
    status_class = "ui-log-status"
    if code is not None:
        try:
            code_int = int(code)
        except (TypeError, ValueError):
            code_int = None
        if code_int is not None and code_int >= 500:
            status_class = "ui-log-status ui-log-status--error"

    return (
        '<li class="ui-log-item">'
        f'<span class="{status_class}">{status}</span>'
        f'<span class="ui-log-code">{code_text}</span>'
        f'<span class="ui-log-time">{timestamp}</span>'
        "</li>"
    )


def register_not_found_handler(
    app: FastAPI,
    *,
    title: str,
    brand: str,
    message: str,
    home_route_name: str,
    home_label: str = "Back to home",
) -> None:
    async def not_found_handler(request: Request, _exc: Exception) -> Response:
        accept = request.headers.get("accept", "")
        if request.url.path.startswith("/api") or "application/json" in accept:
            return JSONResponse({"detail": "Not Found"}, status_code=HTTP_404_NOT_FOUND)

        catalog = request.app.state.catalog
        html = catalog.render(
            "@ui/pages/error.jinja",
            globals={"request": request},
            title=title,
            brand=brand,
            message=message,
            home_href=str(request.url_for(home_route_name)),
            home_label=home_label,
        )
        return HTMLResponse(html, status_code=HTTP_404_NOT_FOUND)

    app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_handler)


def build_health_router(
    *,
    api_healthz: HealthzCallable,
    title: str,
    brand: str,
) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz", response_class=HTMLResponse, name="healthz.page")
    async def health_page(request: Request) -> HTMLResponse:
        catalog = request.app.state.catalog
        html = catalog.render(
            "@ui/pages/healthz.jinja",
            globals={"request": request},
            title=title,
            brand=brand,
            logs_url="/healthz/logs",
        )
        return HTMLResponse(html)

    @router.get("/healthz/logs", response_class=HTMLResponse, include_in_schema=False)
    async def health_logs(_request: Request) -> HTMLResponse:
        payload = api_healthz()
        if inspect.isawaitable(payload):
            payload = await payload
        return HTMLResponse(render_health_log_item(payload))

    return router
