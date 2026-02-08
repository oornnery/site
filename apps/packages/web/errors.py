from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.status import HTTP_404_NOT_FOUND


def register_not_found_handler(
    app: FastAPI,
    *,
    title: str,
    home_route_name: str,
) -> None:
    async def handler(request: Request, _exc: Exception):
        accept = request.headers.get("accept", "")
        if request.url.path.startswith("/api") or "application/json" in accept:
            return JSONResponse({"detail": "Not Found"}, status_code=HTTP_404_NOT_FOUND)

        catalog = request.app.state.catalog
        html = catalog.render(
            "pages/Error.jinja",
            title=title,
            brand="Fabio Souza",
            home_href=str(request.url_for(home_route_name)),
            home_label="Back to home",
        )
        return HTMLResponse(html, status_code=HTTP_404_NOT_FOUND)

    app.add_exception_handler(HTTP_404_NOT_FOUND, handler)
