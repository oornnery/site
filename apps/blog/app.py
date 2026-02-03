from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from apps.ui.catalog import UI_STATIC_DIR, build_catalog
from apps.ui.api.router import register_not_found_handler
from .api.router import router as api_router
from .web.router import router as web_router

APP_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = APP_DIR / "components"
STATIC_DIR = APP_DIR / "static"


def create_app() -> FastAPI:
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app = FastAPI(title="blog", debug=debug)

    # Static: ui + app (mount ui first so /static/ui resolves correctly)
    if UI_STATIC_DIR.exists():
        app.mount("/static/ui", StaticFiles(directory=str(UI_STATIC_DIR)), name="static-ui")
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
    register_not_found_handler(
        app,
        title="Blog - Page not found",
        brand="Blog",
        message="Sorry, the page you are looking for does not exist.",
        home_route_name="blog.home",
    )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.blog.app:app", host="localhost", port=8000, reload=True)
