from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from apps.ui.catalog import UI_STATIC_DIR, build_catalog
from apps.ui.not_found import not_found_response
from .api.router import router as api_router
from .web.router import router as web_router

APP_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = APP_DIR / "components"
STATIC_DIR = APP_DIR / "static"


def create_app() -> FastAPI:
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app = FastAPI(title="blog", debug=debug)

    # Static: app + ui compartilhado
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    if UI_STATIC_DIR.exists():
        app.mount("/static/ui", StaticFiles(directory=str(UI_STATIC_DIR)), name="static-ui")

    # JX catalog no app.state
    app.state.catalog = build_catalog(
        app_components_dir=COMPONENTS_DIR,
        debug=debug,
        site_name="oornnery",
    )

    # Middlewares
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Routers
    app.include_router(api_router)
    app.include_router(web_router)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, _exc: Exception):
        return not_found_response(
            request,
            brand="portfolio.oornnery.com.br",
            title="Portfolio - Page not found",
            home_href=str(request.url_for("portfolio.home")),
        )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.portfolio.app:app", host="localhost", port=8000, reload=True)
